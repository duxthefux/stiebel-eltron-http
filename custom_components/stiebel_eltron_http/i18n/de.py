"""German (de) translations.

Combines entity names from translations/de.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "WÄRMEMENGE",
    ],
    CanonicalKey.EFFICIENCY_SECTION: [
        "EFFIZIENZ",
    ],
    CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION: [
        "WÄRMEERZEUGER EXTERN",
    ],
    # DHW temperature: HTML shows plain "ISTTEMPERATUR", but UI should show "WARMWASSER ISTTEMPERATUR"
    # This parsing entry allows finding the field in HTML, while de.json provides the descriptive UI name
    CanonicalKey.ACTUAL_TEMPERATURE: [
        "ISTTEMPERATUR",
    ],
    CanonicalKey.SET_TEMPERATURE: [
        "SOLLTEMPERATUR",
    ],
    # Note: ISTTEMPERATUR and SOLLTEMPERATUR are generic field names that appear
    # in multiple sections (WARMWASSER, HEIZUNG, WÄRMEERZEUGER EXTERN). The parser
    # uses section-aware context filtering with EXTERNAL_HEAT_SOURCE_SECTION context
    # to match these only in the external heat source section.
    CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE: [
        "ISTTEMPERATUR",
    ],
    CanonicalKey.EXTERNAL_SET_TEMPERATURE: [
        "SOLLTEMPERATUR",
    ],
    CanonicalKey.DUAL_MODE_TEMP_HZG: [
        "BIVALENZTEMPERATUR HZG",
    ],
    CanonicalKey.DUAL_MODE_TEMP_WW: [
        "BIVALENZTEMPERATUR WW",
    ],
    CanonicalKey.LOWER_LIMIT_HZG: [
        "UNTERE EINSATZGRENZE HZG",
    ],
    CanonicalKey.LOWER_LIMIT_WW: [
        "UNTERE EINSATZGRENZE WW",
    ],
    CanonicalKey.HEATING_SECTION: [
        "HEIZUNG",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "STROMVERBRAUCH",
        "LEISTUNGSAUFNAHME",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "PROZESSDATEN",
    ],
    CanonicalKey.START_OPERATION_MODE: [
        "BETRIEBSART",
    ],
    CanonicalKey.INVERTER_POWER: [
        "INVERTER AUFNAHMELEISTUNG",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.VD_DHW_DAY: [
        "WARMWASSER 1-24 h",
        "VD WARMWASSER TAG",
    ],
    CanonicalKey.VD_DHW_TOTAL: [
        "WARMWASSER 1-12 M",
        "VD WARMWASSER SUMME",
    ],
    CanonicalKey.VD_HEATING_DAY: [
        "HEIZEN 1-24 h",
        "VD HEIZEN TAG",
    ],
    CanonicalKey.VD_HEATING_TOTAL: [
        "HEIZEN 1-12 M",
        "VD HEIZEN SUMME",
    ],
    CanonicalKey.VD_HEATING_SUM: [
        "VD HEIZUNG SUMME",
    ],
    CanonicalKey.WATER_FLOW: [
        "WP WASSERVOLUMENSTROM",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('de', PARSING_TRANSLATIONS)

