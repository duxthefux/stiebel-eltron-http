""""Polish (pl) translations.

Combines entity names from translations/{lang_code}.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "ILOSC CIEPLA",
    ],
    CanonicalKey.DHW_SECTION: [
        "CIEPLA WODA UZYTKOWA",
    ],
    CanonicalKey.EFFICIENCY_SECTION: [
        "EFEKTYWNOŚĆ",
    ],
    CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION: [
        "ZEWN. WYTWORNICA CIEPLA",
    ],
    CanonicalKey.HEATING_SECTION: [
        "OGRZEWANIE",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.NHZ_DHW_SUM: [
        "NHZ CWU SUMA",
    ],
    CanonicalKey.NHZ_HEATING_SUM: [
        "NHZ OGRZ SUMA",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "POBOR MOCY",
        "ZUŻYCIE ENERGII ELEKTRYCZNEJ",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "DANE PROCESU",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('pl', PARSING_TRANSLATIONS)
