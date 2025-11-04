"""Stiebel Eltron ISG scraping client."""

from __future__ import annotations

import re
import socket
from typing import Any

import aiohttp
import async_timeout
import bs4
from homeassistant.const import ATTR_SW_VERSION

from .const import (
    DIAGNOSIS_SYSTEM_PATH,
    EXPECTED_HTML_TITLE,
    HTTP_CONNECTION_TIMEOUT,
    INFO_HEATPUMP_PATH,
    INFO_SYSTEM_PATH,
    LOGGER,
    MAC_ADDRESS_KEY,
    START_BETRIEBSART,
    START_PORTAL_OK,
    START_SYSTEM_OK,
    OUTSIDE_TEMPERATURE_KEY,
    PROFILE_NETWORK_PATH,
    ROOM_HUMIDITY_KEY,
    ROOM_TEMPERATURE_KEY,
    DHW_TEMPERATURE_KEY,
    TOTAL_HEAT_PRODUCED_KEY,
    HEAT_PRODUCED_TODAY_KEY,
    TOTAL_DHW_PRODUCED_KEY,
    DHW_PRODUCED_TODAY_KEY,
    TOTAL_HEATING_CONSUMED_KEY,
    HEATING_CONSUMED_TODAY_KEY,
    TOTAL_DHW_CONSUMED_KEY,
    DHW_CONSUMED_TODAY_KEY,
    RETURN_TEMPERATURE_KEY,
    SUPPLY_TEMPERATURE_KEY,
    FROST_PROTECTION_TEMPERATURE_KEY,
    COMPRESSOR_INLET_TEMPERATURE_KEY,
    HOT_GAS_TEMPERATURE_KEY,
    CONDENSER_TEMPERATURE_KEY,
    OIL_SUMP_TEMPERATURE_KEY,
    LOW_PRESSURE_KEY,
    HIGH_PRESSURE_KEY,
    WATER_FLOW_KEY,
    INVERTER_CURRENT_KEY,
    INVERTER_VOLTAGE_KEY,
    COMPRESSOR_SPEED_ACTUAL_KEY,
    COMPRESSOR_SPEED_TARGET_KEY,
    FAN_POWER_RELATIVE_KEY,
    EVAPORATOR_INLET_TEMPERATURE_KEY,
    EVAPORATOR_OUTLET_TEMPERATURE_KEY,
    INVERTER_POWER_INPUT_KEY,
    INVERTER_POWER_KEY,
    EFFICIENCY_HEATING_TODAY_KEY,
    EFFICIENCY_HEATING_1_12M_KEY,
    EFFICIENCY_HEATING_13_24M_KEY,
    EFFICIENCY_DHW_TODAY_KEY,
    EFFICIENCY_DHW_1_12M_KEY,
    EFFICIENCY_DHW_13_24M_KEY,
    DEFAULT_LANGUAGE,
    DEFAULT_FETCH_ENERGY,
)

from . import parsing
from .mapping import CANONICAL_TO_CONST, ENERGY_CONSUMED_MAP, CanonicalKey, to_canonical_key, get_aliases

# Reference the centralized alias map (now in parsing.py).
HEADER_ALIASES = parsing.HEADER_ALIASES


class StiebelEltronScrapingClientError(Exception):
    """Exception to indicate a general scraping error."""

    def __init__(self, message: str) -> None:
        """Initialize with an explanation message."""
        super().__init__(message)


class StiebelEltronScrapingClientCommunicationError(
    StiebelEltronScrapingClientError,
):
    """Exception to indicate a communication error."""


class StiebelEltronScrapingClientAuthenticationError(
    StiebelEltronScrapingClientError,
):
    """Exception to indicate an authentication error."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """Verify that the response is valid."""
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise StiebelEltronScrapingClientAuthenticationError(
            msg,
        )
    response.raise_for_status()


def _convert_temperature(value: str) -> float | None:
    """Delegate temperature conversion to parsing module."""
    return parsing._convert_temperature(value)


def _convert_percentage(value: str) -> float | None:
    """Delegate percentage conversion to parsing module."""
    return parsing._convert_percentage(value)


def _convert_energy(value: str) -> float | None:
    """Delegate energy conversion to parsing module."""
    return parsing._convert_energy(value)


def _convert_numeric(value: str) -> float | None:
    """Delegate numeric conversion to parsing module."""
    return parsing._convert_numeric(value)


def _normalize_text(value: str) -> str:
    """Delegate normalization to parsing module."""
    return parsing._normalize_text(value)


def _matches_alias(header_text: str, candidates: list[str]) -> bool:
    """Delegate alias matching to parsing module."""
    return parsing._matches_alias(header_text, candidates)


def _find_best_alias(header_text: str) -> CanonicalKey | None:
    """Find the best-matching canonical alias for header_text.

    When multiple alias candidates match (due to substring overlaps) prefer the
    most specific candidate (longest normalized length). Returns the canonical
    alias key (as present in HEADER_ALIASES) or None if no candidate matched.
    """
    """Delegate best-alias resolution to parsing module while using the
    local HEADER_ALIASES mapping. Keeps the scraper's internal API stable.
    """
    return parsing._find_best_alias(header_text, parsing.HEADER_ALIASES)


class StiebelEltronScrapingClient:
    """Scrape data from the Stiebel Eltron ISG web portal."""

    def __init__(
        self,
        host: str,
        session: aiohttp.ClientSession,
        language: str = DEFAULT_LANGUAGE,
        fetch_energy: bool = DEFAULT_FETCH_ENERGY,
    ) -> None:
        """Stiebel Eltron scraping client.

        language: controls which localized header aliases are tried when parsing.
        """
        self._host = host
        self._session = session
        self._language = language or DEFAULT_LANGUAGE
        # Whether to attempt fetching the Energy page /?s=1,8 during full fetch
        self._fetch_energy = bool(fetch_energy)

    async def async_test_connect(self) -> Any:
        """Test that we can connect."""
        url = f"http://{self._host}/"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            self._check_title(response)
            # Attempt to auto-detect page language and store it on the client.
            try:
                detected = self._auto_detect_language(response)
                self._language = detected
                LOGGER.debug("Auto-detected ISG language: %s", self._language)
            except Exception:  # keep detection best-effort
                LOGGER.debug("Language auto-detection failed; keeping default: %s", self._language)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return response

    def _auto_detect_language(self, response: str) -> str:
        """Try to detect the ISG page language from the language-switch element.

        This is a simple heuristic that searches for the language indicator in
        the UI. Returns a language code from SUPPORTED_LANGUAGES (defaults to  
        'en' when unsure).
        """
        # Only use the language-switch element on the page to detect language.
        # Some hosts use meta tags influenced by the local machine which are
        # unreliable for determining the ISG UI language. The ISG pages often
        # include a language switch like:
        # Example language switch element used by ISG pages:
        # <div class="eingestelle_sprache"><strong><a href="?s=5,3">ENGLISH</a></strong></div>
        # The scraper interprets the visible link text as the current UI
        # language. Therefore:
        #   - 'ENGLISH' -> 'en' (UI is English)
        #   - 'DEUTSCH' or 'GERMAN' -> 'de' (UI is German)
        #   - 'FRANÇAIS' or 'FRANCAIS' -> 'fr' (UI is French)
        #   - 'NEDERLANDS' or 'DUTCH' -> 'nl' (UI is Dutch)
        if not isinstance(response, str):
            return DEFAULT_LANGUAGE

        try:
            soup = bs4.BeautifulSoup(response, "html.parser")
            lang_elem = soup.select_one(".eingestelle_sprache a")
            if lang_elem and lang_elem.string:
                link_text = lang_elem.string.strip().lower()
                # Interpret the visible link text as the current UI language.
                if "english" in link_text:
                    return "en"
                if "deutsch" in link_text or "german" in link_text:
                    return "de"
                if "français" in link_text or "francais" in link_text or "french" in link_text:
                    return "fr"
                if "nederlands" in link_text or "dutch" in link_text:
                    return "nl"
                if "italiano" in link_text or "italian" in link_text:
                    return "it"
                if "svenska" in link_text or "swedish" in link_text:
                    return "sv"
                if "español" in link_text or "espanol" in link_text or "spanish" in link_text:
                    return "es"
        except Exception:
            # Best-effort; fall back to default language
            pass

        return DEFAULT_LANGUAGE

    async def async_get_device_info(self) -> Any:
        """Retrieve device info from the ISG device."""
        result = {}

        result.update(await self.async_get_mac_address())
        result.update(await self.async_get_versions())

        return result

    async def async_get_mac_address(self) -> Any:
        """Retrieve the MAC address from the ISG device."""
        return await self.async_scrape_profile_network()

    async def async_get_versions(self) -> Any:
        """Retrieve the hardware and software versions from the ISG device."""
        return await self.async_scrape_diagnosis_system()

    async def async_fetch_all(self) -> Any:
        """Scrape all available data from the ISG web portal."""
        result = {}

        # Also attempt to fetch the START page which contains overview info
        # such as Betriebsart, Systemstatus and Portalstatus.
        try:
            start_page = await self.async_scrape_start()
            result.update(start_page)
        except Exception:
            LOGGER.debug("Start page (s=0) not available or failed to parse")

        info_system_result = await self.async_scrape_info_system()
        result.update(info_system_result)

        info_system_heatpump = await self.async_scrape_info_heatpump()
        result.update(info_system_heatpump)

        # Optionally attempt to fetch the Energy / Energiebilanz page which some
        # devices expose at /?s=1,8. This can be controlled via the client
        # `fetch_energy` flag (stored in self._fetch_energy). When enabled we
        # reuse the heatpump extractor to parse totals, consumption and
        # efficiency tables that appear on s=1,8 pages.
        if self._fetch_energy:
            try:
                info_system_energy = await self.async_scrape_info_energy()
                result.update(info_system_energy)
            except Exception:
                # Keep best-effort: do not make the whole fetch fail if /?s=1,8
                # is missing or not accessible on this device.
                LOGGER.debug("Info Energy page (s=1,8) not available or failed to parse")
        else:
            LOGGER.debug("Skipping Energy page (s=1,8) because fetch_energy is disabled for this client")

        info_system_diagnosis = await self.async_scrape_diagnosis_system()
        result.update(info_system_diagnosis)

        LOGGER.debug("Scraped data: %s", result)
        return result

    async def async_scrape_info_system(self) -> Any:
        """Scrape data from the Info / System page."""
        url = f"http://{self._host}{INFO_SYSTEM_PATH}"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            result = self._extract_info_system(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    async def async_scrape_info_heatpump(self) -> Any:
        """Scrape data from the Info / Heat Pump page."""
        url = f"http://{self._host}{INFO_HEATPUMP_PATH}"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            result = self._extract_info_heatpump(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    async def async_scrape_info_energy(self) -> Any:
        """Scrape data from the Info / Energy (Energiebilanz) page (s=1,8).

        The 'Energy' page contains the same tables (amount of heat / power
        consumption) as some heat-pump screenshots. Reuse the heatpump extractor
        logic so we parse totals and consumption values consistently.
        """
        from .const import INFO_ENERGY_PATH

        url = f"http://{self._host}{INFO_ENERGY_PATH}"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            # Reuse the heatpump page extractor: it knows how to extract AMOUNT
            # OF HEAT and POWER CONSUMPTION tables which appear on s=1,8 pages.
            result = self._extract_info_energy(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    async def async_scrape_diagnosis_system(self) -> Any:
        """Scrape data from the Diagnosis / System page."""
        url = f"http://{self._host}{DIAGNOSIS_SYSTEM_PATH}"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            result = self._extract_diagnosis_system(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    async def async_scrape_profile_network(self) -> Any:
        """Scrape data from the Profile / Network page."""
        url = f"http://{self._host}{PROFILE_NETWORK_PATH}"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            result = self._extract_profile_network(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    async def async_scrape_start(self) -> Any:
        """Scrape data from the Start page (s=0)."""
        url = f"http://{self._host}/?s=0"

        try:
            response = await self._api_wrapper(
                method="GET",
                url=url,
            )
            result = self._extract_start_page(response)

        except aiohttp.ClientResponseError as exception:
            msg = f"Failed to connect to {self._host} - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
        else:
            return result

    def _extract_start_page(self, response: str) -> dict:
        """Extract Betriebsart from s=0 page.

        Returns a dict with key START_BETRIEBSART when available.
        """
        soup = bs4.BeautifulSoup(response, "html.parser")
        result: dict[str, object] = {}

        # Normalize helper
        def _text(el: bs4.element.Tag | None) -> str:
            return el.get_text(strip=True) if el else ""

        # Find blocks that include h3 headings and associated '.values' or
        # '.value' elements which commonly contain the displayed value.
        # Precompute alias lists for start-page fields to use centralized mapping
        betr_aliases = get_aliases(CanonicalKey.START_BETRIEBSART)

        for block in soup.find_all(class_=True):
            # We only care about blocks containing h3 headings
            h3 = block.find("h3")
            if not h3:
                continue
            heading = _normalize_text(_text(h3))

            # Betriebsart (operation mode) — use centralized alias matching
            if _matches_alias(heading, betr_aliases):
                # try to find an input with the displayed value first
                input_val = block.find("input", attrs={"value": True})
                if input_val and input_val.has_attr("value"):
                    result[START_BETRIEBSART] = input_val.get("value")
                    continue
                # fallback: any element with class 'value' or 'values'
                val_elem = block.find(class_="value") or block.find(class_="values")
                if val_elem:
                    # if it contains an input, use that value
                    iv = val_elem.find("input", attrs={"value": True})
                    if iv and iv.has_attr("value"):
                        result[START_BETRIEBSART] = iv.get("value")
                    else:
                        result[START_BETRIEBSART] = _text(val_elem)

        # As a final fallback, try to search for these headings anywhere in the page
        # if not found by block scan above.
        if START_BETRIEBSART not in result:
            # Fallback: find any header tag whose text matches the canonical aliases
            h = soup.find(
                lambda tag: tag.name in ("h3", "h2", "h1")
                and _matches_alias(_normalize_text(tag.get_text()), betr_aliases)
            )
            if h:
                # look for a following input with value
                nxt = h.find_next(lambda t: t.name == "input" and t.has_attr("value"))
                if nxt and nxt.has_attr("value"):
                    result[START_BETRIEBSART] = nxt.get("value")

        # Portal ok indicator: some pages include a small image indicating
        # portal connectivity (e.g. <img src="pics/icon_status_ok.gif"/>).
        # Can be: pics/icon_status_ok.gif, pics/icon_status_error.gif, pics/icon_status_warning.gif
        # Expose this as a boolean key START_PORTAL_OK when icon is OK.
        try:
            # Portal ok indicator
            portal_box = soup.find(id="box_start_status_portal")
            if portal_box:
                img = portal_box.find("img")
                if img and img.has_attr("src"):
                    src = (img.get("src") or "").strip()
                    # True only if the OK icon is present (not error or warning)
                    result[START_PORTAL_OK] = src == "pics/icon_status_ok.gif"

            # System ok indicator (similar approach)
            system_box = soup.find(id="box_start_status_system")
            if system_box:
                img = system_box.find("img")
                if img and img.has_attr("src"):
                    src = (img.get("src") or "").strip()
                    # True only if the OK icon is present (not error or warning)
                    result[START_SYSTEM_OK] = src == "pics/icon_status_ok.gif"
        except Exception:
            # Keep best-effort parsing—do not fail the whole extraction on errors.
            LOGGER.debug("Failed to parse start-page ok indicators", exc_info=True)

        LOGGER.debug("Extracted data from Start page: %s", result)
        return result

    def _check_title(self, response: str) -> None:
        """Check if the title matches the expected."""
        soup = bs4.BeautifulSoup(response, "html.parser")
        title = soup.title.string if soup.title and soup.title.string else None
        LOGGER.debug(
            "Potential ISG replied with an HTML doc containing title: %s", title
        )
        if not title or EXPECTED_HTML_TITLE not in title:
            raise StiebelEltronScrapingClientError(title or "No title found")

    def _extract_energy(
        self, table: bs4.element.Tag, expected_header: CanonicalKey | str
    ) -> float | None:
        # Delegate to parsing helper which handles alias lookup and conversion.
        return parsing.extract_energy(table, expected_header)

    def _extract_version(self, table: bs4.element.Tag) -> float | str:
        major_version, minor_version, revision = None, None, None

        # Accept both English and German labels for version rows.
        major_aliases = ["Major version", "Hauptversionsnummer", "Hauptversionsnr", "Hauptversion"]
        minor_aliases = ["Minor version", "Nebenversionsnummer", "Nebenversionsnr", "Nebenversion"]
        revision_aliases = ["Revision", "Revisionsnummer", "Revisionsnr"]

        table_rows = table.find_all("tr")
        for curr_table_row in table_rows:
            elems = curr_table_row.find_all(["td", "th"])  # type: ignore  # noqa: PGH003

            if not elems:
                continue
            texts = [elem.get_text(strip=True) for elem in elems]

            if len(texts) < 2:  # noqa: PLR2004
                continue

            key = texts[0]
            val = texts[1]

            if _matches_alias(key, major_aliases):
                major_version = val
            elif _matches_alias(key, minor_aliases):
                minor_version = val
            elif _matches_alias(key, revision_aliases):
                revision = val

        return f"{major_version}.{minor_version}.{revision}"

    def _extract_temperature(
        self, table: bs4.element.Tag, expected_header: CanonicalKey | str
    ) -> float | None:
        """Delegate temperature extraction to parsing module."""
        return parsing.extract_temperature(table, expected_header)

    def _extract_percentage(
        self, table: bs4.element.Tag, expected_header: CanonicalKey | str
    ) -> float | None:
        """Delegate percentage extraction to parsing module."""
        return parsing.extract_percentage(table, expected_header)

    def _extract_info_system(self, response: str) -> dict:
        """Extract the interesting values from the Info > System page."""
        soup = bs4.BeautifulSoup(response, "html.parser")
        result: dict[str, object] = {}

        # find all tables
        all_tables = soup.find_all("table")

        LOGGER.debug("Info > Heat Pump page: found %d tables", len(all_tables))

        for table_index, curr_table in enumerate(all_tables, start=1):
            all_rows = curr_table.find_all("tr")  # type: ignore  # noqa: PGH003
            all_headers = all_rows[0].find_all(["th"])  # type: ignore  # noqa: PGH003

            curr_headers = [header.get_text(strip=True) for header in all_headers]
            section_title = curr_headers[0] if curr_headers else ""

            # Snapshot keys before processing this table so we can log what it adds
            before_keys = set(result.keys())

            # Helper to check whether the current section title matches any alias
            def _section_matches(key: CanonicalKey | str) -> bool:
                # key may be a string canonical name or a CanonicalKey member.
                aliases = get_aliases(key)
                return _matches_alias(section_title, aliases)

            if _section_matches(CanonicalKey.ROOM_TEMPERATURE_SECTION):
                # Use canonical alias keys (underscored) so alias lookup works for
                # localized pages (e.g., German labels). Passing the canonical
                # key into the extractor will make it consult HEADER_ALIASES.
                result[ROOM_TEMPERATURE_KEY] = self._extract_temperature(
                    curr_table,  # type: ignore  # noqa: PGH003
                    CanonicalKey.ACTUAL_TEMPERATURE_1,
                )
                result[ROOM_HUMIDITY_KEY] = self._extract_percentage(
                    curr_table,  # type: ignore  # noqa: PGH003
                    CanonicalKey.RELATIVE_HUMIDITY_1,
                )
            # PROCESS_DATA_SECTION moved to the Heat Pump page: see _extract_info_heatpump
            elif _section_matches(CanonicalKey.HEATING_SECTION):
                # Prefer canonical key so alias matching picks up localized labels
                result[OUTSIDE_TEMPERATURE_KEY] = self._extract_temperature(
                    curr_table,  # type: ignore  # noqa: PGH003
                    CanonicalKey.OUTSIDE_TEMPERATURE,
                )
            elif _section_matches(CanonicalKey.DHW_SECTION):
                result[DHW_TEMPERATURE_KEY] = self._extract_temperature(
                    curr_table,  # type: ignore  # noqa: PGH003
                    CanonicalKey.ACTUAL_TEMPERATURE,
                )

        # return the scraped data
        LOGGER.debug("Extracted data from Info > System page: %s", result)
        return result

    def _extract_info_heatpump(self, response: str) -> dict:
        """Extract the interesting values from the Info > Heat Pump page."""
        soup = bs4.BeautifulSoup(response, "html.parser")
        result: dict[str, object] = {}

        # find all tables
        all_tables = soup.find_all("table")

        for table_index, curr_table in enumerate(all_tables, start=1):
            all_rows = curr_table.find_all("tr")  # type: ignore  # noqa: PGH003
            all_headers = all_rows[0].find_all(["th"])  # type: ignore  # noqa: PGH003

            curr_headers = [header.get_text(strip=True) for header in all_headers]
            section_title = curr_headers[0] if curr_headers else ""

            # Snapshot keys before processing this table so we can log what it adds
            before_keys = set(result.keys())

            def _section_matches(key: CanonicalKey | str) -> bool:
                # key may be a string canonical name or a CanonicalKey member.
                aliases = get_aliases(key)
                return _matches_alias(section_title, aliases)

            if _section_matches(CanonicalKey.AMOUNT_OF_HEAT_SECTION):
                # Delegate energy/amount parsing to parsing helper and map returned
                # canonical keys to integration constants using the centralized map.
                energy_map = parsing.parse_amount_power_table(curr_table)
                for canonical, val in energy_map.items():
                    const_key = CANONICAL_TO_CONST.get(canonical)
                    if const_key is not None:
                        result[const_key] = val
            elif _section_matches(CanonicalKey.PROCESS_DATA_SECTION):
                LOGGER.debug(
                    "Info > Heat Pump: processing table %d titled '%s' as PROCESS_DATA_SECTION",
                    table_index,
                    section_title,
                )
                # Many process-level metrics appear in this table (temperatures,
                # pressures, flows, inverter stats). Delegate row parsing to the
                # pure parsing helper which returns a mapping from canonical
                # alias -> numeric value. The scraper remains responsible for
                # mapping canonical aliases to integration const keys.
                parsed = parsing.parse_process_data_table(curr_table)
                for matched, val in parsed.items():
                    const_key = CANONICAL_TO_CONST.get(matched)
                    if const_key is not None:
                        result[const_key] = val
            elif _section_matches(CanonicalKey.POWER_CONSUMPTION_SECTION):
                # Reuse the same parse helper for energy-like tables and map to
                # consumed keys via ENERGY_CONSUMED_MAP.
                energy_map = parsing.parse_amount_power_table(curr_table)
                for canonical, val in energy_map.items():
                    const_key = ENERGY_CONSUMED_MAP.get(canonical)
                    if const_key is not None:
                        result[const_key] = val

            elif _section_matches(CanonicalKey.EFFICIENCY_SECTION):
                LOGGER.debug("Found EFFICIENCY_SECTION in table %d ('%s')", table_index, section_title)
                # Delegate parsing of the COP-like efficiency table to a pure helper
                # that returns a small mapping of detected keys to numeric values.
                eff_parsed = parsing.parse_efficiency_table(curr_table)
                # Map helper keys to integration constants
                if CanonicalKey.HEATING_13_24 in eff_parsed:
                    result[EFFICIENCY_HEATING_13_24M_KEY] = eff_parsed.get(CanonicalKey.HEATING_13_24)
                if CanonicalKey.DHW_13_24 in eff_parsed:
                    result[EFFICIENCY_DHW_13_24M_KEY] = eff_parsed.get(CanonicalKey.DHW_13_24)
                if CanonicalKey.VD_HEATING_DAY in eff_parsed:
                    result[EFFICIENCY_HEATING_TODAY_KEY] = eff_parsed.get(CanonicalKey.VD_HEATING_DAY)
                if CanonicalKey.VD_HEATING_TOTAL in eff_parsed:
                    result[EFFICIENCY_HEATING_1_12M_KEY] = eff_parsed.get(CanonicalKey.VD_HEATING_TOTAL)
                if CanonicalKey.VD_DHW_DAY in eff_parsed:
                    result[EFFICIENCY_DHW_TODAY_KEY] = eff_parsed.get(CanonicalKey.VD_DHW_DAY)
                if CanonicalKey.VD_DHW_TOTAL in eff_parsed:
                    result[EFFICIENCY_DHW_1_12M_KEY] = eff_parsed.get(CanonicalKey.VD_DHW_TOTAL)

            # log what keys this table added (if any) to help debug missing fields
            after_keys = set(result.keys())
            added = after_keys - before_keys
            if added:
                # show a small snippet of added keys/values
                added_snapshot = {k: result.get(k) for k in sorted(added)}
                LOGGER.debug(
                    "Info > Heat Pump: table %d ('%s') added keys: %s",
                    table_index,
                    section_title,
                    added_snapshot,
                )

        # return the scraped data
        LOGGER.debug("Extracted data from Info > Heat Pump page: %s", result)
        return result

    def _extract_info_energy(self, response: str) -> dict:
        """Extract values from the Info > Energy page (s=1,8).

        The energy page shares table structures with the heat pump page (amount
        of heat / power consumption). This wrapper reuses the same parsing
        logic but adds a short debug entry point to make it obvious when the
        energy page was parsed.
        """
        LOGGER.debug("Info > Energy page: parsing s=1,8 content")
        # Reuse heatpump parsing which already understands AMOUNT_OF_HEAT
        # and POWER_CONSUMPTION sections.
        result = self._extract_info_heatpump(response)
        LOGGER.debug("Extracted data from Info > Energy page: %s", result)
        return result

    def _extract_diagnosis_system(self, response: str) -> dict:
        """Extract the interesting values from the Diagnosis > System page."""
        soup = bs4.BeautifulSoup(response, "html.parser")
        result = {}

        # find all tables
        all_tables = soup.find_all("table")

        for curr_table in all_tables:
            all_rows = curr_table.find_all("tr")  # type: ignore  # noqa: PGH003
            all_headers = all_rows[0].find_all(["th"])  # type: ignore  # noqa: PGH003

            curr_headers = [header.get_text(strip=True) for header in all_headers]
            # Use normalized matching here too (some pages may localize this)
            if _normalize_text(curr_headers[0]) == _normalize_text("ISG"):
                result[ATTR_SW_VERSION] = self._extract_version(
                    curr_table,  # type: ignore  # noqa: PGH003
                )

        # return the scraped data
        LOGGER.debug("Extracted data from Diagnosis > System page: %s", result)
        return result

    def _extract_profile_network(self, response: str) -> dict:
        """Extract the interesting values from the Profile > Network page."""
        soup = bs4.BeautifulSoup(response, "html.parser")
        result = {}

        full_text = soup.get_text()

        # First, try to find a labeled MAC field (pages often show a heading
        # like "MAC-address" with the value in a nearby element). This is more
        # reliable than blind regex scanning when the page contains multiple
        # MAC-like strings.
        def _normalize_mac(raw: str) -> str:
            # remove any separators and lowercase
            hex_only = re.sub(r"[^0-9A-Fa-f]", "", raw).lower()
            if len(hex_only) != 12:
                return ""
            # format as colon-separated lower-case pairs
            return ":".join(hex_only[i : i + 2] for i in range(0, 12, 2))

        # Search for obvious labeled fields (e.g. <h3>MAC-address</h3>) and
        # try to read a nearby element with class 'values'. Prefer these when
        # present.
        for heading in soup.find_all("h3"):
            htext = _normalize_text(heading.get_text())
            if "mac" in htext:
                # Look up to the calibration block and search for a '.values' div
                calib = heading.find_parent()
                # climb until we find the calibration wrapper or run out
                for _ in range(3):
                    if calib is None:
                        break
                    # common wrapper class seen in fixtures
                    raw_classes = calib.get("class")
                    classes: list[str] = []
                    if raw_classes:
                        if isinstance(raw_classes, (list, tuple)):
                            classes = [str(c) for c in raw_classes]
                        else:
                            classes = [str(raw_classes)]
                    if any(c.startswith("calibration") for c in classes):
                        val_div = calib.find(class_="values")
                        if val_div:
                            nm = _normalize_mac(val_div.get_text(strip=True))
                            if nm:
                                result[MAC_ADDRESS_KEY] = nm
                                # Provide a small context snippet and the heading text
                                snippet = full_text[:200].replace("\n", " ")
                                LOGGER.debug("Found MAC in labeled field: %s (heading=%s)", nm, htext)
                                LOGGER.debug(
                                    "MAC candidates found on Profile > Network page (source_snippet=%s): %s",
                                    snippet,
                                    [nm],
                                )
                                return result
                            # otherwise continue searching
                        break
                    calib = calib.find_parent()

        # Look for common MAC address formats:
        #  - colon or hyphen separated pairs: XX:XX:XX:XX:XX:XX or XX-XX-..
        #  - contiguous 12 hex digits: XXXXXXXXXXXX
        mac_regex = re.compile(r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b|\b[0-9A-Fa-f]{12}\b")
        raw_candidates = re.findall(mac_regex, full_text)

        # Normalize and deduplicate while preserving order
        seen: set[str] = set()
        candidates: list[str] = []
        for r in raw_candidates:
            nm = _normalize_mac(r)
            if not nm:
                continue
            if nm in seen:
                continue
            seen.add(nm)
            candidates.append(nm)

        if candidates:
            # Prefer the first candidate found on the page; log all for debugging
            LOGGER.debug("MAC candidates found on Profile > Network page: %s", candidates)
            result[MAC_ADDRESS_KEY] = candidates[0]
        else:
            LOGGER.error("No MAC address found on Profile > Network page")

        # return the scraped data
        LOGGER.debug("Extracted data from Profile > Network page: %s", result)
        return result

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            headers = {"User-Agent": "StiebelEltronScrapingClient/1.0"}

            async with async_timeout.timeout(HTTP_CONNECTION_TIMEOUT):
                # Prepare a safe (truncated) representation of the payload for logging
                safe_data = None
                if data is not None:
                    try:
                        safe_data = str(data)
                        if len(safe_data) > 1000:
                            safe_data = safe_data[:1000] + "...(truncated)"
                    except Exception:
                        safe_data = "<unable to serialize payload>"

                # Log the request details at debug level. Be careful: payload may contain
                # sensitive information in some setups; we truncate large payloads above.
                LOGGER.debug(
                    "HTTP request: method=%s url=%s headers=%s payload=%s",
                    method,
                    url,
                    headers,
                    safe_data,
                )

                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)

                # Read full response text, then log a truncated snippet for debugging.
                text = await response.text()
                safe_text = text if isinstance(text, str) else str(text)
                if len(safe_text) > 1000:
                    safe_text = safe_text[:1000] + "...(truncated)"

                msg_template = (
                    "HTTP response: method=%s url=%s status=%s response_snippet=%s"
                )
                LOGGER.debug(msg_template, method, url, response.status, safe_text)

                return text

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise StiebelEltronScrapingClientCommunicationError(
                msg,
            ) from exception

        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise StiebelEltronScrapingClientCommunicationError(
                msg,
            ) from exception

        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise StiebelEltronScrapingClientError(
                msg,
            ) from exception
