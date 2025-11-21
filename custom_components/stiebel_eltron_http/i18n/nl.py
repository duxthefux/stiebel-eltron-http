""""Dutch (nl) translations.

Combines entity names from translations/{lang_code}.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "WARMTEHOEVEELHEID",
    ],
    CanonicalKey.DHW_SECTION: [
        "WARM WATER",
    ],
    CanonicalKey.HEATING_SECTION: [
        "VERWARMING",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.NHZ_DHW_SUM: [
        "NHZ WARM WATER TOTAAL",
    ],
    CanonicalKey.NHZ_HEATING_SUM: [
        "NHZ VERWARMEN TOTAAL",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "STROOMVERBRUIK",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "PROCESGEGEVENS",
    ],
    CanonicalKey.ROOM_TEMPERATURE_SECTION: [
        "KAMERTEMP.",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('nl', PARSING_TRANSLATIONS)
