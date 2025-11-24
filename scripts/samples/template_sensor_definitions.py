#!/usr/bin/env python3
"""Template for adding sensor entity definitions.

This file shows the code structure needed in sensor.py when adding new sensors.
Copy the relevant sections and customize for your specific sensors.

Usage:
    1. Review the examples below
    2. Copy to your sensor.py file
    3. Replace placeholders marked with ### USER: comments
    4. Choose appropriate device_class and state_class for each sensor
"""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfVolumeFlowRate,
    PERCENTAGE,
)

# ### USER: Import your new sensor keys from const.py
from .const import (
    NEW_SENSOR_1_KEY,
    NEW_SENSOR_2_KEY,
    NEW_SENSOR_3_KEY,
    # ... add all new keys
)


# =============================================================================
# Add sensor descriptions to the SENSORS tuple
# =============================================================================

SENSORS: tuple[SensorEntityDescription, ...] = (
    # ... existing sensors ...
    
    # ### USER: Add your new sensor definitions here
    
    # Example 1: Temperature sensor
    SensorEntityDescription(
        key=NEW_SENSOR_1_KEY,  # ### USER: Use your sensor key
        name="New Temperature Sensor",  # ### USER: Default English name
        translation_key=NEW_SENSOR_1_KEY,  # Same as key
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    
    # Example 2: Energy sensor (cumulative)
    SensorEntityDescription(
        key=NEW_SENSOR_2_KEY,
        name="Total Energy",
        translation_key=NEW_SENSOR_2_KEY,
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,  # For cumulative values
    ),
    
    # Example 3: Power sensor
    SensorEntityDescription(
        key=NEW_SENSOR_3_KEY,
        name="Current Power",
        translation_key=NEW_SENSOR_3_KEY,
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    
    # Example 4: Pressure sensor
    SensorEntityDescription(
        key="pressure_sensor",
        name="System Pressure",
        translation_key="pressure_sensor",
        device_class=SensorDeviceClass.PRESSURE,
        native_unit_of_measurement=UnitOfPressure.BAR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    
    # Example 5: Flow rate sensor
    SensorEntityDescription(
        key="flow_sensor",
        name="Flow Rate",
        translation_key="flow_sensor",
        device_class=SensorDeviceClass.VOLUME_FLOW_RATE,
        native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    
    # Example 6: Percentage/efficiency sensor
    SensorEntityDescription(
        key="efficiency_sensor",
        name="System Efficiency",
        translation_key="efficiency_sensor",
        device_class=None,  # No specific device class for percentages
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    
    # Example 7: Status/mode sensor (no unit)
    SensorEntityDescription(
        key="status_sensor",
        name="Operating Mode",
        translation_key="status_sensor",
        device_class=None,
        native_unit_of_measurement=None,
        state_class=None,  # No state class for text status
    ),
)


# =============================================================================
# COMMON DEVICE CLASSES AND UNITS
# =============================================================================

"""
### USER: Choose appropriate combinations for your sensors:

Temperature sensors:
    device_class=SensorDeviceClass.TEMPERATURE
    native_unit_of_measurement=UnitOfTemperature.CELSIUS
    state_class=SensorStateClass.MEASUREMENT

Energy sensors (cumulative total):
    device_class=SensorDeviceClass.ENERGY
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR (or MEGA_WATT_HOUR)
    state_class=SensorStateClass.TOTAL_INCREASING

Power sensors (instantaneous):
    device_class=SensorDeviceClass.POWER
    native_unit_of_measurement=UnitOfPower.KILO_WATT
    state_class=SensorStateClass.MEASUREMENT

Pressure sensors:
    device_class=SensorDeviceClass.PRESSURE
    native_unit_of_measurement=UnitOfPressure.BAR
    state_class=SensorStateClass.MEASUREMENT

Flow rate sensors:
    device_class=SensorDeviceClass.VOLUME_FLOW_RATE
    native_unit_of_measurement=UnitOfVolumeFlowRate.LITERS_PER_MINUTE
    state_class=SensorStateClass.MEASUREMENT

Duration sensors:
    device_class=SensorDeviceClass.DURATION
    native_unit_of_measurement=UnitOfTime.HOURS (or MINUTES)
    state_class=SensorStateClass.TOTAL_INCREASING (for runtime counters)

Frequency sensors:
    device_class=SensorDeviceClass.FREQUENCY
    native_unit_of_measurement=UnitOfFrequency.HERTZ
    state_class=SensorStateClass.MEASUREMENT

Percentage/Efficiency (no standard device class):
    device_class=None
    native_unit_of_measurement=PERCENTAGE
    state_class=SensorStateClass.MEASUREMENT

Text status/mode:
    device_class=None
    native_unit_of_measurement=None
    state_class=None
"""


# =============================================================================
# STATE CLASS GUIDELINES
# =============================================================================

"""
### USER: Choose state class based on sensor behavior:

SensorStateClass.MEASUREMENT
- Use for sensors that report instantaneous values
- Value can go up or down
- Examples: temperature, pressure, power, flow rate

SensorStateClass.TOTAL_INCREASING  
- Use for cumulative counters that only increase
- Examples: total energy, runtime hours, cycle counts
- Home Assistant can calculate rates from these

SensorStateClass.TOTAL
- Use for counters that can both increase and decrease
- Less common for heat pumps
- Example: net energy (can be negative)

None (no state class)
- Use for text status, modes, or other non-numeric data
- Examples: operating mode, error messages
"""
