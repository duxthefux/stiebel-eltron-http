""""English (en) translations.

Combines entity names from translations/{lang_code}.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "AMOUNT OF HEAT",
    ],
    CanonicalKey.DHW_SECTION: [
        "DHW",
        "Warmwasser",
    ],
    CanonicalKey.EFFICIENCY_SECTION: [
        "EFFICIENCY",
    ],
    CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION: [
        "EXTERNAL HEAT SOURCE",
    ],
    CanonicalKey.HEATING_SECTION: [
        "HEATING",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.NHZ_DHW_SUM: [
        "NHZ DHW TOTAL",
    ],
    CanonicalKey.NHZ_HEATING_SUM: [
        "NHZ HEATING TOTAL",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "POWER CONSUMPTION",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "PROCESS DATA",
    ],
    CanonicalKey.VD_DHW_DAY: [
        "DHW 1–24 h",  # Note: en-dash (–) not hyphen (-)
        "VD DHW TODAY",
    ],
    CanonicalKey.VD_DHW_TOTAL: [
        "DHW 1–12 M",
        "VD DHW TOTAL",
    ],
    CanonicalKey.VD_HEATING_DAY: [
        "HEATING 1–24 h",
        "VD HEATING TODAY",
    ],
    CanonicalKey.VD_HEATING_TOTAL: [
        "HEATING 1–12 M",
        "VD HEATING TOTAL",
    ],
    CanonicalKey.ACTUAL_TEMPERATURE_HK_1: [
        "ACTUAL TEMPERATURE HK 1",
    ],
    CanonicalKey.SET_TEMPERATURE_HK_1: [
        "SET TEMPERATURE HK 1",
    ],
    CanonicalKey.ACTUAL_TEMPERATURE_HK_2: [
        "ACTUAL TEMPERATURE HK 2",
    ],
    CanonicalKey.SET_TEMPERATURE_HK_2: [
        "SET TEMPERATURE HK 2",
    ],
    CanonicalKey.ACTUAL_BUFFER_TEMPERATURE: [
        "ACTUAL BUFFER TEMPERATURE",
    ],
    CanonicalKey.SET_BUFFER_TEMPERATURE: [
        "SET BUFFER TEMPERATURE",
    ],
    CanonicalKey.DUAL_MODE_TEMP_HZG: [
        "DUAL MODE TEMP HZG",
    ],
    CanonicalKey.DUAL_MODE_TEMP_WW: [
        "DUAL MODE TEMP WW",
    ],
    CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE: [
        "ACTUAL TEMPERATURE",
    ],
    CanonicalKey.EXTERNAL_SET_TEMPERATURE: [
        "SET TEMPERATURE",
    ],
    CanonicalKey.RUNTIME_VD_HEATING: [
        "VD HEATING",
    ],
    CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE: [
        "ACTUAL TEMPERATURE",
    ],
    CanonicalKey.EXTERNAL_SET_TEMPERATURE: [
        "SET TEMPERATURE",
    ],
    CanonicalKey.RUNTIME_VD_DHW: [
        "VD DHW",
    ],
    CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE: [
        "ACTUAL TEMPERATURE",
    ],
    CanonicalKey.EXTERNAL_SET_TEMPERATURE: [
        "SET TEMPERATURE",
    ],
    CanonicalKey.RUNTIME_VD_DEFROST: [
        "VD DEFROST",
    ],
    CanonicalKey.DEFROST_TIME: [
        "DEFROST TIME",
    ],
    CanonicalKey.DEFROST_STARTS: [
        "DEFROST STARTS",
    ],
    CanonicalKey.COMPRESSOR_STARTS: [
        "COMPRESSOR",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('en', PARSING_TRANSLATIONS)
