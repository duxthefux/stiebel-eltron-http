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
    CanonicalKey.START_BETRIEBSART: [
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

