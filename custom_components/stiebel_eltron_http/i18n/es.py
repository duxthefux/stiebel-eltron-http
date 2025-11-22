""""Spanish (es) translations.

Combines entity names from translations/{lang_code}.json with parsing-specific strings.
This ensures both user-facing entity names and ISG web interface field names are recognized.
"""

from .canonical_keys import CanonicalKey
from .json_loader import load_translations_from_json


# Parsing-specific translations for HTML scraping
# Section headings and field variations needed for parsing but not mapped to sensors
PARSING_TRANSLATIONS: dict[CanonicalKey, list[str]] = {
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: [
        "CAUDAL CALORÍFICO",
    ],
    CanonicalKey.DHW_SECTION: [
        "AGUA CALIENTE",
    ],
    CanonicalKey.EXTERNAL_HEAT_SOURCE_SECTION: [
        "GENERADOR CALOR EXTERNO",
    ],
    CanonicalKey.HEATING_SECTION: [
        "CALEFACCIÓN",
    ],
    CanonicalKey.ISG_SECTION: [
        "ISG",
    ],
    CanonicalKey.NHZ_DHW_SUM: [
        "CAL. AUX. ACS TOTAL",
    ],
    CanonicalKey.NHZ_HEATING_SUM: [
        "CALEF. AUX. TOTAL",
    ],
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "CONSUMO ELÉCTRICO",
    ],
    CanonicalKey.PROCESS_DATA_SECTION: [
        "DATOS DE PROCESO",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('es', PARSING_TRANSLATIONS)
