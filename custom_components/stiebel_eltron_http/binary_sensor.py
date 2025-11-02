"""Binary sensor platform for Stiebel Eltron ISG (portal connectivity)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)

from custom_components.stiebel_eltron_http.const import LOGGER

from .const import START_PORTAL_OK, START_SYSTEM_OK
from .entity import StiebelEltronHttpEntity

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


class StiebelEltronHttpPortalBinarySensor(StiebelEltronHttpEntity, BinarySensorEntity):
    """Binary sensor exposing portal connectivity (based on icon)."""

    def __init__(self, coordinator: "StiebelEltronHttpDataUpdateCoordinator", entity_description: BinarySensorEntityDescription) -> None:
        # reuse the same device info wiring from StiebelEltronHttpEntity
        super().__init__(coordinator, entity_description)  # type: ignore[arg-type]

    def _handle_coordinator_update(self) -> None:
        LOGGER.debug("Coordinator update received for binary sensor: %s", self.entity_description.key)
        # coordinator stores boolean under the key
        val = self.coordinator.data.get(self.entity_description.key)
        self._attr_is_on = bool(val)
        return super()._handle_coordinator_update()
