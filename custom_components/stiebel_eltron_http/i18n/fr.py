""""French (fr) translations.

Combines entity names from translations/{lang_code}.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "QUANTITE DE CHALEUR",
    ],
    CanonicalKey.DHW_SECTION: [
        "EAU CHAUDE SANITAIRE",
    ],
    CanonicalKey.EFFICIENCY_SECTION: [
        "EFFICACITÉ",
    ],
    CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION: [
        "GENERATEUR CHAL. EXTERNE",
    ],
    CanonicalKey.HEATING_SECTION: [
        "CHAUFFAGE",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.NHZ_DHW_SUM: [
        "EL. CH. EAU N. TOTAL",
    ],
    CanonicalKey.NHZ_HEATING_SUM: [
        "ELEM. CH. NUIT TOTAL",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "PUISSANCE ABSORBEE",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "DONNEES PROCESS",
    ],
    CanonicalKey.ROOM_TEMPERATURE_SECTION: [
        "TEMP. AMBIANTE",
    ],
    # DHW section uses plain field names without prefix
    CanonicalKey.ACTUAL_TEMPERATURE: [
        "TEMPERATURE REELLE",  # DHW section field (unprefixed)
    ],
    CanonicalKey.SET_TEMPERATURE: [
        "TEMPÉRATURE DE CONSIGNE",  # DHW section field (unprefixed)
    ],
    # External section - same field names but in different section
    CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE: [
        "TEMPERATURE REELLE",
    ],
    CanonicalKey.EXTERNAL_SET_TEMPERATURE: [
        "TEMPÉRATURE DE CONSIGNE",
    ],
    CanonicalKey.INVERTER_POWER: [
        "PUISS INVERTER",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('fr', PARSING_TRANSLATIONS)
