""""Czech (cs) translations.

Combines entity names from translations/{lang_code}.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "MNOZSTVI TEPLA",
    ],
    CanonicalKey.DHW_SECTION: [
        "TEPLA VODA",
    ],
    CanonicalKey.EFFICIENCY_SECTION: [
        "ÚČINNOST",
    ],
    CanonicalKey.HEATING_SECTION: [
        "TOPENI",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.NHZ_DHW_SUM: [
        "NHZ TEPLA VODA SOUCET",
    ],
    CanonicalKey.NHZ_HEATING_SUM: [
        "NHZ TOPENI SOUCET",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "PRIKON",
        "SPOTŘEBA PROUDU",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "PROCESNI DATA",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('cs', PARSING_TRANSLATIONS)
