"""Constants for stiebel_eltron_http."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "stiebel_eltron_http"
HTTP_CONNECTION_TIMEOUT = 30  # seconds
EXPECTED_HTML_TITLE = "STIEBEL ELTRON Reglersteuerung"

# Configuration keys
CONF_LANGUAGE = "language"
# Special value meaning: auto-detect language during config
AUTO_LANGUAGE = "auto"
# Supported languages for scraping/lookup (include 'auto' for auto-detect)
# Languages: auto, English, German, French, Dutch, Italian, Swedish, Spanish, Polish, Czech, Hungarian, Finnish, Danish
SUPPORTED_LANGUAGES = (AUTO_LANGUAGE, "en", "de", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da")
# Default language
DEFAULT_LANGUAGE = "en"

# Optional config to control whether the integration should also fetch the
# Energy page (`/?s=1,8`) which some devices expose. Default True.
CONF_FETCH_ENERGY = "fetch_energy"
DEFAULT_FETCH_ENERGY = True

# How often to refresh data (in minutes). Can be configured via options.
CONF_UPDATE_INTERVAL = "update_interval_minutes"
DEFAULT_UPDATE_INTERVAL_MINUTES = 1

INFO_SYSTEM_PATH = "/?s=1,0"
INFO_HEATPUMP_PATH = "/?s=1,1"
INFO_ENERGY_PATH = "/?s=1,8"
DIAGNOSIS_SYSTEM_PATH = "/?s=2,7"
PROFILE_NETWORK_PATH = "/?s=5,0"

# Sensor keys
ROOM_TEMPERATURE_KEY = "room_temperature"
ROOM_HUMIDITY_KEY = "room_relative_humidity"
DHW_TEMPERATURE_KEY = "dhw_temperature"
OUTSIDE_TEMPERATURE_KEY = "outside_temperature"
TOTAL_HEAT_PRODUCED_KEY = "total_heat_produced"
HEAT_PRODUCED_TODAY_KEY = "heat_produced_today"
TOTAL_DHW_PRODUCED_KEY = "total_dhw_produced"
DHW_PRODUCED_TODAY_KEY = "dhw_produced_today"
TOTAL_HEATING_CONSUMED_KEY = "total_heating_consumed"
HEATING_CONSUMED_TODAY_KEY = "heating_consumed_today"
TOTAL_DHW_CONSUMED_KEY = "total_dhw_consumed"
DHW_CONSUMED_TODAY_KEY = "dhw_consumed_today"

# Efficiency / COP metrics (from the EFFIZIENZ / EFFICIENCY table)
EFFICIENCY_HEATING_TODAY_KEY = "efficiency_heating_today"
EFFICIENCY_HEATING_1_12M_KEY = "efficiency_heating_1_12m"
EFFICIENCY_HEATING_13_24M_KEY = "efficiency_heating_13_24m"
EFFICIENCY_DHW_TODAY_KEY = "efficiency_dhw_today"
EFFICIENCY_DHW_1_12M_KEY = "efficiency_dhw_1_12m"
EFFICIENCY_DHW_13_24M_KEY = "efficiency_dhw_13_24m"

# Additional process metrics from the ISG "PROZESSDATEN" / heat pump pages
RETURN_TEMPERATURE_KEY = "return_temperature"
SUPPLY_TEMPERATURE_KEY = "supply_temperature"
FROST_PROTECTION_TEMPERATURE_KEY = "frost_protection_temperature"
OUTSIDE_TEMPERATURE_KEY = OUTSIDE_TEMPERATURE_KEY  # alias (already defined)
COMPRESSOR_INLET_TEMPERATURE_KEY = "compressor_inlet_temperature"
HOT_GAS_TEMPERATURE_KEY = "hot_gas_temperature"
CONDENSER_TEMPERATURE_KEY = "condenser_temperature"
OIL_SUMP_TEMPERATURE_KEY = "oil_sump_temperature"
LOW_PRESSURE_KEY = "low_pressure"
HIGH_PRESSURE_KEY = "high_pressure"
WATER_FLOW_KEY = "water_flow"
INVERTER_CURRENT_KEY = "inverter_current"
INVERTER_VOLTAGE_KEY = "inverter_voltage"
COMPRESSOR_SPEED_ACTUAL_KEY = "compressor_speed_actual"
COMPRESSOR_SPEED_TARGET_KEY = "compressor_speed_target"
FAN_POWER_RELATIVE_KEY = "fan_power_relative"
EVAPORATOR_INLET_TEMPERATURE_KEY = "evaporator_inlet_temperature"
EVAPORATOR_OUTLET_TEMPERATURE_KEY = "evaporator_outlet_temperature"
INVERTER_POWER_INPUT_KEY = "inverter_power_input"
INVERTER_POWER_KEY = "inverter_power"

# Heating circuit 1 (HK 1)
ACTUAL_TEMPERATURE_HK_1_KEY = "actual_temperature_hk_1"
SET_TEMPERATURE_HK_1_KEY = "set_temperature_hk_1"

# Heating circuit 2 (HK 2)
ACTUAL_TEMPERATURE_HK_2_KEY = "actual_temperature_hk_2"
SET_TEMPERATURE_HK_2_KEY = "set_temperature_hk_2"

# Buffer temperatures
ACTUAL_BUFFER_TEMPERATURE_KEY = "actual_buffer_temperature"
SET_BUFFER_TEMPERATURE_KEY = "set_buffer_temperature"

# External heat source temperatures
EXTERNAL_ACTUAL_TEMPERATURE_KEY = "external_actual_temperature"
EXTERNAL_SET_TEMPERATURE_KEY = "external_set_temperature"

# Dual mode temperatures
DUAL_MODE_TEMP_HZG_KEY = "dual_mode_temp_hzg"
DUAL_MODE_TEMP_WW_KEY = "dual_mode_temp_ww"

# Application limits
LOWER_LIMIT_HZG_KEY = "lower_limit_hzg"
LOWER_LIMIT_WW_KEY = "lower_limit_ww"

# Runtime hours and counters
RUNTIME_VD_HEATING_KEY = "runtime_vd_heating"
RUNTIME_VD_DHW_KEY = "runtime_vd_dhw"
RUNTIME_VD_DEFROST_KEY = "runtime_vd_defrost"
DEFROST_TIME_KEY = "defrost_time"
DEFROST_STARTS_KEY = "defrost_starts"
COMPRESSOR_STARTS_KEY = "compressor_starts"


# Other keys
MAC_ADDRESS_KEY = "mac_address"

# Start page (s=0) sensors
START_OPERATION_MODE_KEY = "start_operation_mode"
START_PORTAL_OK = "start_portal_ok"
START_SYSTEM_OK = "start_system_ok"
