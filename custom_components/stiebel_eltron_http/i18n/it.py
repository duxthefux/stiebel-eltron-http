""""Italian (it) translations.

Combines entity names from translations/{lang_code}.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "QUANTITÀ CALORE",
    ],
    CanonicalKey.DHW_SECTION: [
        "ACQUA CALDA",
    ],
    CanonicalKey.EFFICIENCY_SECTION: [
        "EFFICIENZA",
    ],
    CanonicalKey.HEATING_SECTION: [
        "RISCALDAMENTO",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.NHZ_DHW_SUM: [
        "NHZ AC SOMMA",
    ],
    CanonicalKey.NHZ_HEATING_SUM: [
        "NHZ RISC SOMMA",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "POTENZA ASSORBITA",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "DATI PROCESSO",
    ],
    CanonicalKey.ROOM_TEMPERATURE_SECTION: [
        "TMP. DELL'' AMB.'",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('it', PARSING_TRANSLATIONS)
