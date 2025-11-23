"""Sensor platform for Stiebel Eltron ISG without Modbus."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfTemperature

from custom_components.stiebel_eltron_http.const import LOGGER

from .const import (
    OUTSIDE_TEMPERATURE_KEY,
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
    ACTUAL_TEMPERATURE_HK_1_KEY,
    SET_TEMPERATURE_HK_1_KEY,
    ACTUAL_TEMPERATURE_HK_2_KEY,
    SET_TEMPERATURE_HK_2_KEY,
    ACTUAL_BUFFER_TEMPERATURE_KEY,
    SET_BUFFER_TEMPERATURE_KEY,
    EXTERNAL_ACTUAL_TEMPERATURE_KEY,
    EXTERNAL_SET_TEMPERATURE_KEY,
    DUAL_MODE_TEMP_HZG_KEY,
    DUAL_MODE_TEMP_WW_KEY,
    LOWER_LIMIT_HZG_KEY,
    LOWER_LIMIT_WW_KEY,
    START_OPERATION_MODE_KEY,
)
from .entity import StiebelEltronHttpEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import StiebelEltronHttpDataUpdateCoordinator
    from .data import StiebelEltronHttpConfigEntry


ENTITY_DESCRIPTIONS = (
    SensorEntityDescription(
        key=ROOM_TEMPERATURE_KEY,
        name="Room temperature",
        translation_key=ROOM_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=DHW_TEMPERATURE_KEY,
        name="Hot water temperature",
        translation_key=DHW_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ROOM_HUMIDITY_KEY,
        name="Room relative humidity",
        translation_key=ROOM_HUMIDITY_KEY,
        icon="mdi:water-percent",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=OUTSIDE_TEMPERATURE_KEY,
        name="Outside temperature",
        translation_key=OUTSIDE_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=TOTAL_HEAT_PRODUCED_KEY,
        name="Total heating energy produced",
        translation_key=TOTAL_HEAT_PRODUCED_KEY,
        icon="mdi:radiator",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=HEAT_PRODUCED_TODAY_KEY,
        name="Heating energy produced today",
        translation_key=HEAT_PRODUCED_TODAY_KEY,
        icon="mdi:radiator",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    SensorEntityDescription(
        key=TOTAL_DHW_PRODUCED_KEY,
        name="Total hot water energy produced",
        translation_key=TOTAL_DHW_PRODUCED_KEY,
        icon="mdi:water-boiler",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=DHW_PRODUCED_TODAY_KEY,
        name="Hot water energy produced today",
        translation_key=DHW_PRODUCED_TODAY_KEY,
        icon="mdi:water-boiler",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    SensorEntityDescription(
        key=TOTAL_HEATING_CONSUMED_KEY,
        name="Total heating energy consumed",
        translation_key=TOTAL_HEATING_CONSUMED_KEY,
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=HEATING_CONSUMED_TODAY_KEY,
        name="Heating energy consumed today",
        translation_key=HEATING_CONSUMED_TODAY_KEY,
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),

    SensorEntityDescription(
        key=TOTAL_DHW_CONSUMED_KEY,
        name="Total hot water energy consumed",
        translation_key=TOTAL_DHW_CONSUMED_KEY,
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    SensorEntityDescription(
        key=DHW_CONSUMED_TODAY_KEY,
        name="Hot water energy consumed today",
        translation_key=DHW_CONSUMED_TODAY_KEY,
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    # ---- Additional process sensors ----
    SensorEntityDescription(
        key=RETURN_TEMPERATURE_KEY,
        name="Return temperature",
        translation_key=RETURN_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=SUPPLY_TEMPERATURE_KEY,
        name="Supply (flow) temperature",
        translation_key=SUPPLY_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=FROST_PROTECTION_TEMPERATURE_KEY,
        name="Frost protection temperature",
        translation_key=FROST_PROTECTION_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=COMPRESSOR_INLET_TEMPERATURE_KEY,
        name="Compressor inlet temperature",
        translation_key=COMPRESSOR_INLET_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=HOT_GAS_TEMPERATURE_KEY,
        name="Hot gas temperature",
        translation_key=HOT_GAS_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=CONDENSER_TEMPERATURE_KEY,
        name="Condenser temperature",
        translation_key=CONDENSER_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=OIL_SUMP_TEMPERATURE_KEY,
        name="Oil sump temperature",
        translation_key=OIL_SUMP_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=LOW_PRESSURE_KEY,
        name="Low pressure",
        translation_key=LOW_PRESSURE_KEY,
        icon="mdi:gauge",
        native_unit_of_measurement="bar",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=HIGH_PRESSURE_KEY,
        name="High pressure",
        translation_key=HIGH_PRESSURE_KEY,
        icon="mdi:gauge",
        native_unit_of_measurement="bar",
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=WATER_FLOW_KEY,
        name="Water flow",
        translation_key=WATER_FLOW_KEY,
        icon="mdi:water",
        native_unit_of_measurement="l/min",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=INVERTER_CURRENT_KEY,
        name="Inverter current",
        translation_key=INVERTER_CURRENT_KEY,
        icon="mdi:current-ac",
        native_unit_of_measurement="A",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=INVERTER_VOLTAGE_KEY,
        name="Inverter voltage",
        translation_key=INVERTER_VOLTAGE_KEY,
        icon="mdi:flash",
        native_unit_of_measurement="V",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=COMPRESSOR_SPEED_ACTUAL_KEY,
        name="Compressor actual speed",
        translation_key=COMPRESSOR_SPEED_ACTUAL_KEY,
        icon="mdi:speedometer",
        native_unit_of_measurement="Hz",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=COMPRESSOR_SPEED_TARGET_KEY,
        name="Compressor target speed",
        translation_key=COMPRESSOR_SPEED_TARGET_KEY,
        icon="mdi:speedometer",
        native_unit_of_measurement="Hz",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=FAN_POWER_RELATIVE_KEY,
        name="Fan power relative",
        translation_key=FAN_POWER_RELATIVE_KEY,
        icon="mdi:fan",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY if False else None,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=EVAPORATOR_INLET_TEMPERATURE_KEY,
        name="Evaporator inlet temperature",
        translation_key=EVAPORATOR_INLET_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=EVAPORATOR_OUTLET_TEMPERATURE_KEY,
        name="Evaporator outlet temperature",
        translation_key=EVAPORATOR_OUTLET_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=INVERTER_POWER_INPUT_KEY,
        name="Inverter input power",
        translation_key=INVERTER_POWER_INPUT_KEY,
        icon="mdi:power-plug",
        native_unit_of_measurement="kW",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=INVERTER_POWER_KEY,
        name="Inverter power",
        translation_key=INVERTER_POWER_KEY,
        icon="mdi:power-plug",
        native_unit_of_measurement="kW",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # ---- Efficiency / COP-like metrics ----
    SensorEntityDescription(
        key=EFFICIENCY_HEATING_TODAY_KEY,
        name="Heating efficiency (today)",
        translation_key=EFFICIENCY_HEATING_TODAY_KEY,
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=EFFICIENCY_HEATING_1_12M_KEY,
        name="Heating efficiency (1-12 months)",
        translation_key=EFFICIENCY_HEATING_1_12M_KEY,
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=EFFICIENCY_HEATING_13_24M_KEY,
        name="Heating efficiency (13-24 months)",
        translation_key=EFFICIENCY_HEATING_13_24M_KEY,
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=EFFICIENCY_DHW_TODAY_KEY,
        name="DHW efficiency (today)",
        translation_key=EFFICIENCY_DHW_TODAY_KEY,
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=EFFICIENCY_DHW_1_12M_KEY,
        name="DHW efficiency (1-12 months)",
        translation_key=EFFICIENCY_DHW_1_12M_KEY,
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=EFFICIENCY_DHW_13_24M_KEY,
        name="DHW efficiency (13-24 months)",
        translation_key=EFFICIENCY_DHW_13_24M_KEY,
        icon="mdi:gauge",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # ---- Start page overview fields (s=0) ----
    SensorEntityDescription(
        key=START_OPERATION_MODE_KEY,
        name="Operation mode",
        translation_key=START_OPERATION_MODE_KEY,
        icon="mdi:cog-outline",
    ),
    # ---- External heat source temperatures ----
    SensorEntityDescription(
        key=EXTERNAL_ACTUAL_TEMPERATURE_KEY,
        name="External heat source actual temperature",
        translation_key=EXTERNAL_ACTUAL_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=EXTERNAL_SET_TEMPERATURE_KEY,
        name="External heat source set temperature",
        translation_key=EXTERNAL_SET_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # ---- Heating circuit 1 (HK 1) ----
    SensorEntityDescription(
        key=ACTUAL_TEMPERATURE_HK_1_KEY,
        name="HK 1 actual temperature",
        translation_key=ACTUAL_TEMPERATURE_HK_1_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=SET_TEMPERATURE_HK_1_KEY,
        name="HK 1 set temperature",
        translation_key=SET_TEMPERATURE_HK_1_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # ---- Heating circuit 2 (HK 2) ----
    SensorEntityDescription(
        key=ACTUAL_TEMPERATURE_HK_2_KEY,
        name="HK 2 actual temperature",
        translation_key=ACTUAL_TEMPERATURE_HK_2_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=SET_TEMPERATURE_HK_2_KEY,
        name="HK 2 set temperature",
        translation_key=SET_TEMPERATURE_HK_2_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # ---- Buffer temperatures ----
    SensorEntityDescription(
        key=ACTUAL_BUFFER_TEMPERATURE_KEY,
        name="Buffer actual temperature",
        translation_key=ACTUAL_BUFFER_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=SET_BUFFER_TEMPERATURE_KEY,
        name="Buffer set temperature",
        translation_key=SET_BUFFER_TEMPERATURE_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    # ---- Dual mode and application limits ----
    SensorEntityDescription(
        key=DUAL_MODE_TEMP_HZG_KEY,
        name="Dual mode temperature heating",
        translation_key=DUAL_MODE_TEMP_HZG_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=DUAL_MODE_TEMP_WW_KEY,
        name="Dual mode temperature DHW",
        translation_key=DUAL_MODE_TEMP_WW_KEY,
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=LOWER_LIMIT_HZG_KEY,
        name="Lower application limit heating",
        translation_key=LOWER_LIMIT_HZG_KEY,
        icon="mdi:thermometer-chevron-down",
    ),
    SensorEntityDescription(
        key=LOWER_LIMIT_WW_KEY,
        name="Lower application limit DHW",
        translation_key=LOWER_LIMIT_WW_KEY,
        icon="mdi:thermometer-chevron-down",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: StiebelEltronHttpConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    # Only create room temperature / room humidity sensors when the coordinator
    # already has values for them. Coordinator is refreshed before setup, so
    # its `data` should be available here. This avoids creating empty sensors
    # on systems that don't expose room sensors.
    data = entry.runtime_data.coordinator.data or {}

    to_create = []
    # Track which keys we've created to avoid duplicates and to support
    # dynamic creation later when missing optional sensors appear.
    created_keys = set()
    for entity_description in ENTITY_DESCRIPTIONS:
        key = entity_description.key
        # Make room temperature, room humidity and efficiency sensors optional when missing
        optional_keys = {
            ROOM_TEMPERATURE_KEY,
            ROOM_HUMIDITY_KEY,
            EFFICIENCY_HEATING_TODAY_KEY,
            EFFICIENCY_HEATING_1_12M_KEY,
            EFFICIENCY_HEATING_13_24M_KEY,
            EFFICIENCY_DHW_TODAY_KEY,
            EFFICIENCY_DHW_1_12M_KEY,
            EFFICIENCY_DHW_13_24M_KEY,
            # Start page overview fields (s=0) are optional; create when available
            START_OPERATION_MODE_KEY,
            # Heating circuit sensors (HK 1, HK 2) are optional
            ACTUAL_TEMPERATURE_HK_1_KEY,
            SET_TEMPERATURE_HK_1_KEY,
            ACTUAL_TEMPERATURE_HK_2_KEY,
            SET_TEMPERATURE_HK_2_KEY,
            # Buffer sensors are optional
            ACTUAL_BUFFER_TEMPERATURE_KEY,
            SET_BUFFER_TEMPERATURE_KEY,
            # External heat source sensors are optional
            EXTERNAL_ACTUAL_TEMPERATURE_KEY,
            EXTERNAL_SET_TEMPERATURE_KEY,
        }
        if key in optional_keys:
            if key not in data or data.get(key) is None:
                LOGGER.debug("Skipping creation of optional sensor %s because no data available", key)
                continue
        to_create.append(
            StiebelEltronHttpSensor(
                coordinator=entry.runtime_data.coordinator,
                entity_description=entity_description,
            )
        )
        created_keys.add(key)

    if to_create:
        async_add_entities(to_create)

    # Dynamic creation: if optional sensors were skipped above, listen for
    # coordinator updates and create entities when the keys first appear with
    # a non-None value.
    optional_keys_missing = optional_keys - created_keys
    if optional_keys_missing:
        coordinator = entry.runtime_data.coordinator

        def _on_coordinator_update() -> None:
            # This callback runs in the event loop. Check coordinator.data for
            # newly-available keys and create entities for them.
            try:
                data_now = coordinator.data or {}
                new_keys = [k for k in list(optional_keys_missing) if (k in data_now and data_now.get(k) is not None)]
                if not new_keys:
                    return

                # Build entity objects for the new keys
                entities_to_add = []
                for ed in ENTITY_DESCRIPTIONS:
                    if ed.key in new_keys:
                        entities_to_add.append(
                            StiebelEltronHttpSensor(coordinator=coordinator, entity_description=ed)
                        )
                        # mark as created to avoid re-adding
                        created_keys.add(ed.key)
                        optional_keys_missing.discard(ed.key)

                if entities_to_add:
                    # schedule adding entities on the event loop
                    hass.async_create_task(async_add_entities(entities_to_add))

                # If we've created all optional entities, remove the listener
                if not optional_keys_missing:
                    try:
                        unsub()
                    except Exception:
                        LOGGER.debug("Failed to unsubscribe optional-sensor listener cleanly")
            except Exception:
                LOGGER.exception("Error while handling coordinator update for dynamic sensor creation")

        # register listener and keep unsubscribe function
        try:
            unsub = coordinator.async_add_listener(_on_coordinator_update)
        except Exception:
            LOGGER.exception("Failed to register dynamic sensor creation listener")


class StiebelEltronHttpSensor(StiebelEltronHttpEntity, SensorEntity):
    """Stiebel Eltron HTTP Sensor class."""

    def __init__(
        self,
        coordinator: StiebelEltronHttpDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description)

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        LOGGER.debug("Coordinator update received: %s", self.coordinator.data)

        new_value = self.coordinator.data.get(self.entity_description.key)
        LOGGER.debug(
            "Sensor %s updated with new value: %s",
            self.entity_description.key,
            new_value,
        )
        # update the sensor state based on the coordinator data
        self._attr_native_value = new_value

        return super()._handle_coordinator_update()
