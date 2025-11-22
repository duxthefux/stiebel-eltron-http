""""Danish (da) translations.

Combines entity names from translations/{lang_code}.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "VARMEMÆNGDE",
    ],
    CanonicalKey.DHW_SECTION: [
        "VARMT VAND",
    ],
    CanonicalKey.EFFICIENCY_SECTION: [
        "EFFEKTIVITET",
    ],
    CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION: [
        "VARMEGENERATOR EKSTERN",
    ],
    CanonicalKey.HEATING_SECTION: [
        "VARME",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.NHZ_DHW_SUM: [
        "NHZ VARMTVAND SUM",
    ],
    CanonicalKey.NHZ_HEATING_SUM: [
        "NHZ VARME SUM",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "STRØMFORBRUG",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "PROCESDATA",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('da', PARSING_TRANSLATIONS)
