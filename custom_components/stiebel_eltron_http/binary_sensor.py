"""Binary sensor platform for Stiebel Eltron ISG (portal connectivity)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.const import ATTR_SW_VERSION, CONF_HOST
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.stiebel_eltron_http.const import LOGGER, MAC_ADDRESS_KEY

from .const import START_PORTAL_OK, START_SYSTEM_OK

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import StiebelEltronHttpDataUpdateCoordinator
    from .data import StiebelEltronHttpConfigEntry


ENTITY_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key=START_PORTAL_OK,
        name="Portal connected",
        translation_key=START_PORTAL_OK,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
    BinarySensorEntityDescription(
        key=START_SYSTEM_OK,
        name="System OK",
        translation_key=START_SYSTEM_OK,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: StiebelEltronHttpConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary sensor platform."""
    data = entry.runtime_data.coordinator.data or {}

    to_create = []
    for desc in ENTITY_DESCRIPTIONS:
        key = desc.key
        if key in data and data.get(key) is not None:
            to_create.append(
                StiebelEltronHttpPortalBinarySensor(entry.runtime_data.coordinator, desc)
            )

    if to_create:
        async_add_entities(to_create)


class StiebelEltronHttpPortalBinarySensor(
    CoordinatorEntity["StiebelEltronHttpDataUpdateCoordinator"], BinarySensorEntity
):
    """Binary sensor exposing portal connectivity (based on icon)."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: "StiebelEltronHttpDataUpdateCoordinator",
        entity_description: BinarySensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = (
            coordinator.config_entry.entry_id + "_" + entity_description.key
        )
        LOGGER.debug("Setting binary sensor unique_id to %s", self._attr_unique_id)

        self._attr_device_info = DeviceInfo(
            configuration_url=f"http://{coordinator.config_entry.data[CONF_HOST]}",
            connections={
                (CONNECTION_NETWORK_MAC, coordinator.device_data[MAC_ADDRESS_KEY])
            },
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            manufacturer="Stiebel Eltron",
            model="Internet Service Gateway (ISG)",
            name="Stiebel Eltron ISG",
            sw_version=coordinator.device_data.get(ATTR_SW_VERSION, "-"),
        )

    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        LOGGER.debug(
            "Coordinator update received for binary sensor: %s",
            self.entity_description.key,
        )
        # coordinator stores boolean under the key
        val = self.coordinator.data.get(self.entity_description.key)
        self._attr_is_on = bool(val)
        return super()._handle_coordinator_update()
