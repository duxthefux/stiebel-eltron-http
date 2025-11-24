""""Swedish (sv) translations.

Combines entity names from translations/{lang_code}.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "VÄRMEMÄNGD",
    ],
    CanonicalKey.DHW_SECTION: [
        "VARMVATTEN",
    ],
    CanonicalKey.EFFICIENCY_SECTION: [
        "VERKNINGSGRAD",
    ],
    CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION: [
        "VÄRMEGENERATOR EXTERN",
    ],
    CanonicalKey.HEATING_SECTION: [
        "UPPVÄRMNING",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.NHZ_DHW_SUM: [
        "NHZ VARMVATTEN SUMMA",
    ],
    CanonicalKey.NHZ_HEATING_SUM: [
        "NHZ VÄRME SUMMA",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "EFFEKTFÖRBRUKNING",
        "STRÖMFÖRBRUKNING",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "PROCESSDATA",
    ],
    # DHW section uses plain field names without prefix
    CanonicalKey.ACTUAL_TEMPERATURE: [
        "AKT TEMPERATUR",  # DHW section field (unprefixed)
    ],
    CanonicalKey.SET_TEMPERATURE: [
        "BÖRTEMPERATUR",  # DHW section field (unprefixed)
    ],
    # External section - same field names but in different section
    CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE: [
        "AKT TEMPERATUR",
    ],
    CanonicalKey.EXTERNAL_SET_TEMPERATURE: [
        "BÖRTEMPERATUR",
    ],
    CanonicalKey.INVERTER_POWER: [
        "INVERTER POWER",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('sv', PARSING_TRANSLATIONS)
