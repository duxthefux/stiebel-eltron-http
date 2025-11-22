""""Hungarian (hu) translations.

Combines entity names from translations/{lang_code}.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "HÕMENNYISÉG",
    ],
    CanonicalKey.DHW_SECTION: [
        "MELEGVÍZ",
    ],
    CanonicalKey.EFFICIENCY_SECTION: [
        "HATÉKONYSÁG",
    ],
    CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION: [
        "KÜLSÕ HÕGENERÁTOR",
    ],
    CanonicalKey.HEATING_SECTION: [
        "FÛTÉS",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.NHZ_DHW_SUM: [
        "NHZ MELEGVÍZ ÖSSZEG",
    ],
    CanonicalKey.NHZ_HEATING_SUM: [
        "NHZ FÛTÉS ÖSSZEG",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "TELJESÍTMÉNYFELVETEL",
        "ENERGIAFOGYASZTÁS",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "FOLYAMATADATOK",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('hu', PARSING_TRANSLATIONS)
