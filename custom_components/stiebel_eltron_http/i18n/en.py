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
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('en', PARSING_TRANSLATIONS)
