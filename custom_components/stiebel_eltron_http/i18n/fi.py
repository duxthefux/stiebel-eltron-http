""""Finnish (fi) translations.

Combines entity names from translations/{lang_code}.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "LÄMPÖMÄÄRÄ",
    ],
    CanonicalKey.DHW_SECTION: [
        "LÄMMINVESI",
    ],
    CanonicalKey.EFFICIENCY_SECTION: [
        "TEHOKKUUS",
    ],
    CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION: [
        "LÄMMÖNTUOTTAJA ULK",
    ],
    CanonicalKey.HEATING_SECTION: [
        "LÄMMITYS",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.NHZ_DHW_SUM: [
        "NHZ LV SUMMA",
    ],
    CanonicalKey.NHZ_HEATING_SUM: [
        "NHZ LÄMM SUMMA",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "VIRRANKULUTUS",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "PROSESSITIEDOT",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('fi', PARSING_TRANSLATIONS)
