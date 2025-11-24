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
    # DHW section uses plain field names without "MELEGVÍZ" prefix
    CanonicalKey.ACTUAL_TEMPERATURE: [
        "TÉNYLEGES HÕMÉRSÉKLET",  # DHW section field (unprefixed)
    ],
    CanonicalKey.SET_TEMPERATURE: [
        "NÉVL. HŐMÉRS.",  # DHW section field (unprefixed)
    ],
    # External section - same field names but in different section
    CanonicalKey.EXTERNAL_ACTUAL_TEMPERATURE: [
        "TÉNYLEGES HÕMÉRSÉKLET",
    ],
    CanonicalKey.EXTERNAL_SET_TEMPERATURE: [
        "NÉVL. HŐMÉRS.",
    ],
    # Process data section - unprefixed field names as they appear in HTML
    CanonicalKey.RETURN_TEMPERATURE: [
        "VISSZATÉRÕ HÕMÉRSÉKLET",
    ],
    CanonicalKey.SUPPLY_TEMPERATURE: [
        "ELÕREMENÕ HÕMÉRSÉKLET",
    ],
    CanonicalKey.COMPRESSOR_INLET_TEMPERATURE: [
        "KOMPRESSZOR BEMENŐ HŐMÉRSÉKLETE",
    ],
    CanonicalKey.HOT_GAS_TEMPERATURE: [
        "FORRÓGÁZ-HÕMÉRSÉKLET",
    ],
    CanonicalKey.CONDENSER_TEMPERATURE: [
        "KONDENZÁTOR-HÕMÉRSÉKLET",
    ],
    CanonicalKey.OIL_SUMP_TEMPERATURE: [
        "OLAJTEKNÕ-HÕMÉRSÉKLET",
    ],
    CanonicalKey.LOW_PRESSURE: [
        "NYOMÁS ALACSONY NYOMÁS",
    ],
    CanonicalKey.HIGH_PRESSURE: [
        "NYOMÁS NAGYNYOMÁS",
    ],
    CanonicalKey.WATER_FLOW: [
        "WP TÉRFOGATÁRAM",
    ],
    CanonicalKey.INVERTER_CURRENT: [
        "INVERTER ÁRAMERÕSSÉG",
    ],
    CanonicalKey.INVERTER_POWER: [
        "INVERTER POWER",
    ],
}

# Load from JSON and merge with parsing translations
TRANSLATIONS: dict[CanonicalKey, list[str]] = load_translations_from_json('hu', PARSING_TRANSLATIONS)
