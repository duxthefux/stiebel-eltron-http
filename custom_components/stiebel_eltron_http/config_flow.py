"""Config flow for the Stiebel Eltron ISG without Modbus integration."""

from __future__ import annotations

from typing import TYPE_CHECKING
import re
import asyncio
from urllib.parse import urlsplit

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_DEVICE_ID, CONF_HOST, CONF_NAME

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult

from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.service_info.ssdp import (
    ATTR_UPNP_FRIENDLY_NAME,
    ATTR_UPNP_PRESENTATION_URL,
    ATTR_UPNP_SERIAL,
    SsdpServiceInfo,
)
from slugify import slugify

from .const import (
    DOMAIN,
    LOGGER,
    MAC_ADDRESS_KEY,
        CONF_LANGUAGE,
        SUPPORTED_LANGUAGES,
        DEFAULT_LANGUAGE,
        AUTO_LANGUAGE,
        CONF_FETCH_ENERGY,
        DEFAULT_FETCH_ENERGY,
        CONF_UPDATE_INTERVAL,
        DEFAULT_UPDATE_INTERVAL_MINUTES,
)
from .scraper import (
    StiebelEltronScrapingClient,
    StiebelEltronScrapingClientAuthenticationError,
    StiebelEltronScrapingClientCommunicationError,
    StiebelEltronScrapingClientError,
)


class StiebelEltronIsgHttpFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Stiebel Eltron ISG without Modbus."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}

        if user_input is not None:
            _default_host = user_input[CONF_HOST]
            # language choice may be explicit ("en"/"de") or "auto"
            chosen_lang = user_input.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
            self.config = {
                CONF_HOST: user_input[CONF_HOST],
                CONF_LANGUAGE: chosen_lang,
                CONF_FETCH_ENERGY: user_input.get(CONF_FETCH_ENERGY, DEFAULT_FETCH_ENERGY),
                CONF_UPDATE_INTERVAL: int(user_input.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES)),
            }

            try:
                # try to connect and verify that it looks like a Stiebel Eltron ISG
                # If the user selected AUTO_LANGUAGE, run detection and persist
                if chosen_lang == AUTO_LANGUAGE:
                    detected_lang = await self._test_connect(host=self.config[CONF_HOST])
                    # persist detected language so subsequent client calls use it
                    self.config[CONF_LANGUAGE] = detected_lang
                else:
                    # validate connectivity without overriding the user's choice
                    await self._test_connect(host=self.config[CONF_HOST])

                # retrieve the MAC address from the device and normalize it
                mac = await self._get_mac_address(host=self.config[CONF_HOST])
                # normalize to hex-only lowercase (stable unique id)
                norm_mac = re.sub(r"[^0-9a-fA-F]", "", mac).lower() if mac else mac
                self.config[CONF_DEVICE_ID] = norm_mac

                LOGGER.debug("Discovered device with config: %s", self.config)

                # set a unique ID based on the MAC address
                await self._format_and_set_unique_id(self.config[CONF_DEVICE_ID])

                # The user-visible 'fetch energy' flag is a runtime option and
                # should be stored in the config entry's `options` so it can be
                # changed via the UI later. Create the entry with the core data
                # (host/language/device id) and schedule a short background
                # task that will attach the options to the newly-created entry
                # once Home Assistant has created it in the registry.
                fetch_value = self.config.get(CONF_FETCH_ENERGY, DEFAULT_FETCH_ENERGY)
                update_interval_value = int(self.config.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES))

                # Build data to persist (omit the runtime option from entry.data)
                data_to_persist = {
                    CONF_HOST: self.config[CONF_HOST],
                    CONF_LANGUAGE: self.config[CONF_LANGUAGE],
                    CONF_DEVICE_ID: self.config[CONF_DEVICE_ID],
                }

                # Schedule a background task that will find the newly created
                # entry by the unique_id (slugified MAC) and update its options.
                # Use normalized MAC (hex only, lowercase) as unique id so it is
                # stable across formatting variations (colons, dashes, upper/lower).
                unique_id = self.config[CONF_DEVICE_ID]
                new_options = {CONF_FETCH_ENERGY: fetch_value, CONF_UPDATE_INTERVAL: update_interval_value}
                # fire-and-forget; best-effort update
                self.hass.async_create_task(
                    self._persist_options_for_new_entry(unique_id, new_options)
                )

                return self.async_create_entry(title=self.config[CONF_HOST], data=data_to_persist)

            except StiebelEltronScrapingClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except StiebelEltronScrapingClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except StiebelEltronScrapingClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"

        _default_host = self.config[CONF_HOST] if hasattr(self, "config") else ""
        _default_lang = self.config[CONF_LANGUAGE] if hasattr(self, "config") else AUTO_LANGUAGE
        _default_fetch = (
            self.config[CONF_FETCH_ENERGY]
            if hasattr(self, "config")
            else DEFAULT_FETCH_ENERGY
        )
        _default_update = (
            int(self.config[CONF_UPDATE_INTERVAL]) if hasattr(self, "config") and CONF_UPDATE_INTERVAL in self.config else DEFAULT_UPDATE_INTERVAL_MINUTES
        )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=_default_host): str,
                    vol.Optional(CONF_LANGUAGE, default=_default_lang): vol.In(
                        SUPPORTED_LANGUAGES
                    ),
                    vol.Optional(CONF_FETCH_ENERGY, default=_default_fetch): bool,
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=_default_update,
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                },
            ),
            errors=_errors,
        )

    async def async_step_ssdp(
        self, discovery_info: SsdpServiceInfo
    ) -> ConfigFlowResult:
        """Prepare configuration for a SSDP discovered device."""
        LOGGER.info("Discovered SSDP device with UPnP info: %s", discovery_info.upnp)
        url = urlsplit(discovery_info.upnp[ATTR_UPNP_PRESENTATION_URL])
        mac_address = format_mac(discovery_info.upnp[ATTR_UPNP_SERIAL])
        LOGGER.debug("Found MAC address from UPnP: %s", mac_address)

        self.config = {
            CONF_HOST: url.hostname,
        }

        self._async_abort_entries_match({CONF_HOST: self.config[CONF_HOST]})

        # set a unique ID based on the MAC address
        await self._format_and_set_unique_id(mac_address)

        self.context["title_placeholders"] = {
            CONF_NAME: discovery_info.upnp[ATTR_UPNP_FRIENDLY_NAME],
            CONF_HOST: self.config[CONF_HOST],
        }

        return await self.async_step_user()

    async def _format_and_set_unique_id(self, mac_address: str) -> None:
        """Format the MAC address and use it for unique ID."""
        # Normalize MAC to hex only lowercase (stable and portable)
        _unique_id = re.sub(r"[^0-9a-fA-F]", "", mac_address).lower()
        LOGGER.debug("Formatting MAC address %s into unique ID %s", mac_address, _unique_id)
        await self.async_set_unique_id(_unique_id)
        self._abort_if_unique_id_configured(updates=self.config)

    async def _test_connect(self, host: str) -> None:
        """Validate connection to ISG."""
        client = StiebelEltronScrapingClient(
            host=host,
            session=async_create_clientsession(self.hass),
            language=self.config.get(CONF_LANGUAGE, DEFAULT_LANGUAGE) if hasattr(self, "config") else DEFAULT_LANGUAGE,
        )
        await client.async_test_connect()
        return client._language

    async def _get_mac_address(self, host: str) -> str:
        """Retrieve the MAC address from the ISG."""
        client = StiebelEltronScrapingClient(
            host=host,
            session=async_create_clientsession(self.hass),
            language=self.config.get(CONF_LANGUAGE, DEFAULT_LANGUAGE) if hasattr(self, "config") else DEFAULT_LANGUAGE,
        )
        mac_address_result = await client.async_get_mac_address()

        if not mac_address_result:
            msg = "Could not retrieve MAC address"
            raise StiebelEltronScrapingClientError(msg)

        mac_address = mac_address_result.get(MAC_ADDRESS_KEY)
        LOGGER.debug("Found MAC address from ISG: %s", mac_address)

        return mac_address

    async def _persist_options_for_new_entry(self, unique_id: str, options: dict) -> None:
        """Find the new config entry by unique_id and persist options onto it.

        Home Assistant creates the entry after this flow returns; to attach
        options at setup-time we poll the registry briefly and then update the
        freshly-created entry. This is best-effort and non-blocking.
        """
        # Wait a short while for the entry to be registered and then update it.
        for _ in range(30):
            for entry in self.hass.config_entries.async_entries(DOMAIN):
                if entry.unique_id == unique_id:
                    self.hass.config_entries.async_update_entry(entry, options=options)
                    LOGGER.debug("Persisted options %s for new entry %s", options, unique_id)
                    return
            await asyncio.sleep(0.1)

        LOGGER.warning("Could not persist options for new entry %s: entry not found", unique_id)


async def async_get_options_flow(config_entry):
    """Return the options flow handler for this integration."""
    return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for stiebel_eltron_http."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict | None = None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            # Persist the options in entry.options (do not overwrite entry.data).
            new_options = dict(self.config_entry.options or {})
            if CONF_FETCH_ENERGY in user_input:
                new_options[CONF_FETCH_ENERGY] = user_input[CONF_FETCH_ENERGY]
            if CONF_UPDATE_INTERVAL in user_input:
                new_options[CONF_UPDATE_INTERVAL] = int(user_input[CONF_UPDATE_INTERVAL])
            if CONF_LANGUAGE in user_input:
                new_options[CONF_LANGUAGE] = user_input[CONF_LANGUAGE]

            # update the config entry options
            self.hass.config_entries.async_update_entry(self.config_entry, options=new_options)

            return self.async_create_entry(title="", data={})
        # show form with current defaults
        # Prefer values from options when showing the options form
        current_fetch = self.config_entry.options.get(
            CONF_FETCH_ENERGY,
            self.config_entry.data.get(CONF_FETCH_ENERGY, DEFAULT_FETCH_ENERGY),
        )
        current_lang = self.config_entry.options.get(
            CONF_LANGUAGE, self.config_entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
        )
        current_update = int(
            self.config_entry.options.get(
                CONF_UPDATE_INTERVAL,
                self.config_entry.data.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES),
            )
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_FETCH_ENERGY, default=current_fetch): bool,
                    vol.Optional(CONF_LANGUAGE, default=current_lang): vol.In(
                        SUPPORTED_LANGUAGES
                    ),
                    vol.Optional(
                        CONF_UPDATE_INTERVAL, default=current_update
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=1440)),
                }
            ),
            errors=errors,
        )


    
