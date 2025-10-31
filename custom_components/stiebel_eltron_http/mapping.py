"""Central canonical alias -> integration const mapping.

This module centralizes the translation between parsing canonical aliases
and the integration constant names used in the scraper (e.g.,
TOTAL_HEAT_PRODUCED_KEY).

We expose a `CanonicalKey` StrEnum so the code can use a typed symbol
instead of raw strings for canonical keys.
"""

from enum import StrEnum

from .const import (
    TOTAL_HEAT_PRODUCED_KEY,
    HEAT_PRODUCED_TODAY_KEY,
    TOTAL_DHW_PRODUCED_KEY,
    DHW_PRODUCED_TODAY_KEY,
    TOTAL_HEATING_CONSUMED_KEY,
    HEATING_CONSUMED_TODAY_KEY,
    TOTAL_DHW_CONSUMED_KEY,
    DHW_CONSUMED_TODAY_KEY,
    RETURN_TEMPERATURE_KEY,
    SUPPLY_TEMPERATURE_KEY,
    FROST_PROTECTION_TEMPERATURE_KEY,
    OUTSIDE_TEMPERATURE_KEY,
    COMPRESSOR_INLET_TEMPERATURE_KEY,
    HOT_GAS_TEMPERATURE_KEY,
    CONDENSER_TEMPERATURE_KEY,
    OIL_SUMP_TEMPERATURE_KEY,
    LOW_PRESSURE_KEY,
    HIGH_PRESSURE_KEY,
    WATER_FLOW_KEY,
    INVERTER_CURRENT_KEY,
    INVERTER_VOLTAGE_KEY,
    COMPRESSOR_SPEED_ACTUAL_KEY,
    COMPRESSOR_SPEED_TARGET_KEY,
    FAN_POWER_RELATIVE_KEY,
    EVAPORATOR_INLET_TEMPERATURE_KEY,
    EVAPORATOR_OUTLET_TEMPERATURE_KEY,
    INVERTER_POWER_INPUT_KEY,
    INVERTER_POWER_KEY,
    EFFICIENCY_HEATING_TODAY_KEY,
    EFFICIENCY_HEATING_1_12M_KEY,
    EFFICIENCY_HEATING_13_24M_KEY,
    EFFICIENCY_DHW_TODAY_KEY,
    EFFICIENCY_DHW_1_12M_KEY,
    EFFICIENCY_DHW_13_24M_KEY,
)


class CanonicalKey(StrEnum):
    # Sections
    ROOM_TEMPERATURE_SECTION = "ROOM_TEMPERATURE_SECTION"
    HEATING_SECTION = "HEATING_SECTION"
    PROCESS_DATA_SECTION = "PROCESS_DATA_SECTION"
    DHW_SECTION = "DHW_SECTION"
    AMOUNT_OF_HEAT_SECTION = "AMOUNT_OF_HEAT_SECTION"
    POWER_CONSUMPTION_SECTION = "POWER_CONSUMPTION_SECTION"
    EFFICIENCY_SECTION = "EFFICIENCY_SECTION"
    ISG_SECTION = "ISG_SECTION"

    # Energy/item labels
    VD_HEATING_TOTAL = "VD_HEATING_TOTAL"
    VD_HEATING_DAY = "VD_HEATING_DAY"
    VD_DHW_TOTAL = "VD_DHW_TOTAL"
    VD_DHW_DAY = "VD_DHW_DAY"
    VD_HEATING_SUM = "VD_HEATING_SUM"
    NHZ_HEATING_SUM = "NHZ_HEATING_SUM"
    NHZ_DHW_SUM = "NHZ_DHW_SUM"

    # Temperature / humidity
    ACTUAL_TEMPERATURE_1 = "ACTUAL_TEMPERATURE_1"
    RELATIVE_HUMIDITY_1 = "RELATIVE_HUMIDITY_1"
    OUTSIDE_TEMPERATURE = "OUTSIDE_TEMPERATURE"
    ACTUAL_TEMPERATURE = "ACTUAL_TEMPERATURE"

    # Process data
    RETURN_TEMPERATURE = "RETURN_TEMPERATURE"
    SUPPLY_TEMPERATURE = "SUPPLY_TEMPERATURE"
    FROST_PROTECTION_TEMPERATURE = "FROST_PROTECTION_TEMPERATURE"
    COMPRESSOR_INLET_TEMPERATURE = "COMPRESSOR_INLET_TEMPERATURE"
    HOT_GAS_TEMPERATURE = "HOT_GAS_TEMPERATURE"
    CONDENSER_TEMPERATURE = "CONDENSER_TEMPERATURE"
    OIL_SUMP_TEMPERATURE = "OIL_SUMP_TEMPERATURE"
    LOW_PRESSURE = "LOW_PRESSURE"
    HIGH_PRESSURE = "HIGH_PRESSURE"
    WATER_FLOW = "WATER_FLOW"
    INVERTER_CURRENT = "INVERTER_CURRENT"
    INVERTER_VOLTAGE = "INVERTER_VOLTAGE"
    COMPRESSOR_SPEED_ACTUAL = "COMPRESSOR_SPEED_ACTUAL"
    COMPRESSOR_SPEED_TARGET = "COMPRESSOR_SPEED_TARGET"
    FAN_POWER_RELATIVE = "FAN_POWER_RELATIVE"
    EVAPORATOR_INLET_TEMPERATURE = "EVAPORATOR_INLET_TEMPERATURE"
    EVAPORATOR_OUTLET_TEMPERATURE = "EVAPORATOR_OUTLET_TEMPERATURE"
    INVERTER_POWER_INPUT = "INVERTER_POWER_INPUT"
    INVERTER_POWER = "INVERTER_POWER"

    # Efficiency keys
    HEATING_13_24 = "HEATING_13_24"
    DHW_13_24 = "DHW_13_24"


# Localized header/section aliases used for scraping. Keys are canonical
# identifiers represented by `CanonicalKey` and the values are lists of
# possible header strings that may appear in the ISG HTML in different
# localizations. Keep this map in sync with the parser and the scraper.
HEADER_ALIASES: dict[CanonicalKey, list[str]] = {
    # Sections on the "Info > System" page
    CanonicalKey.ROOM_TEMPERATURE_SECTION: ["ROOM TEMPERATURE", "RAUMTEMPERATUR", "RAUM TEMPERATUR"],
    CanonicalKey.HEATING_SECTION: ["HEATING", "HEIZUNG"],
    CanonicalKey.PROCESS_DATA_SECTION: ["PROCESS DATA", "PROZESSDATEN", "PROZESS DATEN", "PROZESS-DATEN"],
    CanonicalKey.DHW_SECTION: ["DHW", "Warmwasser", "WW", "TRINKWASSER", "DHW (Warmwasser)"],

    # Sections on the "Info > Heat Pump" page
    CanonicalKey.AMOUNT_OF_HEAT_SECTION: ["AMOUNT OF HEAT", "MENGE DER WÄRME", "WÄRMEMENGE", "MENGE"],
    # 'Leistungsaufnahme' and 'Verbrauch' are other German labels seen in some ISG variants
    CanonicalKey.POWER_CONSUMPTION_SECTION: [
        "POWER CONSUMPTION",
        "STROMVERBRAUCH",
        "ENERGIEVERBRAUCH",
        "LEISTUNGSAUFNAHME",
        "VERBRAUCH",
        "VERBRAUCH HEIZUNG",
    ],

    # Efficiency / COP table shown on some ENERGY pages
    CanonicalKey.EFFICIENCY_SECTION: ["EFFICIENCY", "EFFIZIENZ"],

    # Diagnosis
    CanonicalKey.ISG_SECTION: ["ISG"],

    # Energy/item labels that appear as first column values inside tables
    CanonicalKey.VD_HEATING_TOTAL: [
        "VD HEATING TOTAL",
        "VD HEIZUNG GESAMT",
        "VD HEATING TOTAL",
        "VD HEIZEN SUMME",
        "VD HEIZEN SUMME",
        # Some snapshots use short labels like 'HEATING 1-12 M' or 'HEATING 1–12 M'
        "HEATING 1-12 M",
        "HEATING 1–12 M",
        "HEIZEN 1-12 M",
        "HEIZEN 1–12 M",
    ],
    CanonicalKey.VD_HEATING_DAY: [
        "VD HEATING DAY",
        "VD HEIZUNG TAG",
        "VD HEATING DAY",
        "VD HEIZEN TAG",
        # daily labels
        "HEATING 1-24 h",
        "HEATING 1–24 h",
        "HEIZEN 1-24 h",
        "HEIZEN 1–24 h",
    ],
    CanonicalKey.VD_DHW_TOTAL: [
        "VD DHW TOTAL",
        "VD WW GESAMT",
        "VD DHW TOTAL",
        "VD WARMWASSER SUMME",
        "DHW 1-12 M",
        "DHW 1–12 M",
        "WARMWASSER 1-12 M",
        "WARMWASSER 1–12 M",
    ],
    CanonicalKey.VD_DHW_DAY: [
        "VD DHW DAY",
        "VD WW TAG",
        "VD DHW DAY",
        "VD WARMWASSER TAG",
        "DHW 1-24 h",
        "DHW 1–24 h",
        "WARMWASSER 1-24 h",
        "WARMWASSER 1–24 h",
    ],
    # Additional energy labels that appear on some German ISG pages
    CanonicalKey.VD_HEATING_SUM: ["VD HEATING SUM", "VD HEIZEN SUMME", "VD HEIZUNG SUMME"],
    CanonicalKey.NHZ_HEATING_SUM: ["NHZ HEIZEN SUMME", "NHZ HEIZUNG SUMME"],
    CanonicalKey.NHZ_DHW_SUM: ["NHZ WARMWASSER SUMME"],
    # Temperature / humidity / label mappings (canonical -> localized variants)
    CanonicalKey.ACTUAL_TEMPERATURE_1: ["ACTUAL TEMPERATURE 1", "ISTTEMPERATUR HK 1", "ISTTEMPERATUR 1", "ISTTEMPERATUR"],
    CanonicalKey.RELATIVE_HUMIDITY_1: ["RELATIVE HUMIDITY 1", "RAUMFEUCHTE 1", "RAUMFEUCHTE", "RELATIVE HUMIDITY"],
    CanonicalKey.OUTSIDE_TEMPERATURE: ["OUTSIDE TEMPERATURE", "AUSSENTEMPERATUR", "AUSSENTEMPERATUR"],
    CanonicalKey.ACTUAL_TEMPERATURE: ["ACTUAL TEMPERATURE", "ISTTEMPERATUR"],

    # Process data labels (both German and English aliases)
    CanonicalKey.RETURN_TEMPERATURE: [
        "RÜCKLAUFTEMPERATUR",
        "RUECKLAUFTEMPERATUR",
        "RETURN TEMPERATURE",
    ],
    CanonicalKey.SUPPLY_TEMPERATURE: [
        "VORLAUFTEMPERATUR",
        "VORLAUFTEMPERATUR",
        "SUPPLY TEMPERATURE",
        "FLOW TEMPERATURE",
    ],
    # English pages may abbreviate the label (e.g. "FROST PROTECTION TEMP").
    CanonicalKey.FROST_PROTECTION_TEMPERATURE: [
        "FROSTSCHUTZTEMPERATUR",
        "FROST PROTECTION TEMPERATURE",
        "FROST PROTECTION TEMP",
    ],
    CanonicalKey.OUTSIDE_TEMPERATURE: ["AUSSENTEMPERATUR", "OUTSIDE TEMPERATURE", "AMBIENT TEMPERATURE"],
    CanonicalKey.COMPRESSOR_INLET_TEMPERATURE: [
        "VERDICHTEREINTRITTSTEMPERATUR",
        "COMPRESSOR INLET TEMPERATURE",
    ],
    CanonicalKey.HOT_GAS_TEMPERATURE: ["HEISSGASTEMPERATUR", "HOT GAS TEMPERATURE"],
    CanonicalKey.CONDENSER_TEMPERATURE: [
        "VERFLÜSSIGERTEMPERATUR",
        "VERFLUESSIGERTEMPERATUR",
        "CONDENSER TEMPERATURE",
    ],
    CanonicalKey.OIL_SUMP_TEMPERATURE: ["ÖLSUMPFTEMPERATUR", "OELSUMPFTEMPERATUR", "OIL SUMP TEMPERATURE"],
    CanonicalKey.LOW_PRESSURE: ["DRUCK NIEDERDRUCK", "NIEDERDRUCK", "LOW PRESSURE"],
    CanonicalKey.HIGH_PRESSURE: ["DRUCK HOCHDRUCK", "HOCHDRUCK", "HIGH PRESSURE"],
    CanonicalKey.WATER_FLOW: ["WP WASSERVOLUMENSTROM", "WASSERVOLUMENSTROM", "WATER FLOW", "WATER VOLUME FLOW"],
    CanonicalKey.INVERTER_CURRENT: ["STROM INVERTER", "INVERTER CURRENT"],
    CanonicalKey.INVERTER_VOLTAGE: ["SPANNUNG INVERTER", "SPANNUNG", "INVERTER VOLTAGE", "VOLTAGE"],
    CanonicalKey.COMPRESSOR_SPEED_ACTUAL: [
        "ISTDREHZAHL VERDICHTER",
        "ISTDREHZAHL",
        "COMPRESSOR SPEED ACTUAL",
        "ACTUAL COMPRESSOR SPEED",
    ],
    CanonicalKey.COMPRESSOR_SPEED_TARGET: [
        "SOLLDREHZAHL VERDICHTER",
        "SOLLDREHZAHL",
        "COMPRESSOR SPEED TARGET",
        "TARGET COMPRESSOR SPEED",
        # English pages may use 'SET COMPRESSOR SPEED'
        "SET COMPRESSOR SPEED",
    ],
    CanonicalKey.FAN_POWER_RELATIVE: [
        "LÜFTERLEISTUNG RELATIV",
        "LUFTERLEISTUNG RELATIV",
        "FAN POWER RELATIVE",
        "FAN POWER (%)",
        "FAN POWER",
        # English snapshot uses 'RELATIVE FAN SPEED'
        "RELATIVE FAN SPEED",
    ],
    CanonicalKey.EVAPORATOR_INLET_TEMPERATURE: ["VERDAMPFEREINTRITTSTEMPERATUR", "EVAPORATOR INLET TEMPERATURE"],
    CanonicalKey.EVAPORATOR_OUTLET_TEMPERATURE: ["VERDAMPFERAUSTRITTSTEMPERATUR", "EVAPORATOR OUTLET TEMPERATURE"],
    CanonicalKey.INVERTER_POWER_INPUT: [
        # labels that indicate inverter power consumption / uptake
        "AUFNAHMELEISTUNG INVERTER",
        "INVERTER POWER CONSUMPTION",
        "INVERTER POWER INPUT",
        "INVERTER INPUT POWER",
    ],
    # Distinct alias for the displayed inverter power value (may be rounded/different)
    CanonicalKey.INVERTER_POWER: [
        "INVERTER POWER",
        "INVERTER AUFNAHMELEISTUNG",
    ],
}

# A small whitelist of canonical aliases that are intentionally not mapped to
# integration constants because they are parsing/display-only labels (e.g.
# section-only names or short display keys). Tests and tooling can import
# this to avoid duplicating the same whitelist in test code.
ALLOWED_UNMAPPED_CANONICALS: set[CanonicalKey] = {
    CanonicalKey.ACTUAL_TEMPERATURE_1,
    CanonicalKey.RELATIVE_HUMIDITY_1,
    CanonicalKey.ACTUAL_TEMPERATURE,
    CanonicalKey.VD_HEATING_SUM,
    CanonicalKey.NHZ_HEATING_SUM,
    CanonicalKey.NHZ_DHW_SUM,
}


# Canonical alias -> const key mapping
CANONICAL_TO_CONST: dict[CanonicalKey, str] = {
    # Process data
    CanonicalKey.RETURN_TEMPERATURE: RETURN_TEMPERATURE_KEY,
    CanonicalKey.SUPPLY_TEMPERATURE: SUPPLY_TEMPERATURE_KEY,
    CanonicalKey.FROST_PROTECTION_TEMPERATURE: FROST_PROTECTION_TEMPERATURE_KEY,
    CanonicalKey.OUTSIDE_TEMPERATURE: OUTSIDE_TEMPERATURE_KEY,
    CanonicalKey.COMPRESSOR_INLET_TEMPERATURE: COMPRESSOR_INLET_TEMPERATURE_KEY,
    CanonicalKey.HOT_GAS_TEMPERATURE: HOT_GAS_TEMPERATURE_KEY,
    CanonicalKey.CONDENSER_TEMPERATURE: CONDENSER_TEMPERATURE_KEY,
    CanonicalKey.OIL_SUMP_TEMPERATURE: OIL_SUMP_TEMPERATURE_KEY,
    CanonicalKey.LOW_PRESSURE: LOW_PRESSURE_KEY,
    CanonicalKey.HIGH_PRESSURE: HIGH_PRESSURE_KEY,
    CanonicalKey.WATER_FLOW: WATER_FLOW_KEY,
    CanonicalKey.INVERTER_CURRENT: INVERTER_CURRENT_KEY,
    CanonicalKey.INVERTER_VOLTAGE: INVERTER_VOLTAGE_KEY,
    CanonicalKey.COMPRESSOR_SPEED_ACTUAL: COMPRESSOR_SPEED_ACTUAL_KEY,
    CanonicalKey.COMPRESSOR_SPEED_TARGET: COMPRESSOR_SPEED_TARGET_KEY,
    CanonicalKey.FAN_POWER_RELATIVE: FAN_POWER_RELATIVE_KEY,
    CanonicalKey.EVAPORATOR_INLET_TEMPERATURE: EVAPORATOR_INLET_TEMPERATURE_KEY,
    CanonicalKey.EVAPORATOR_OUTLET_TEMPERATURE: EVAPORATOR_OUTLET_TEMPERATURE_KEY,
    CanonicalKey.INVERTER_POWER: INVERTER_POWER_KEY,
    CanonicalKey.INVERTER_POWER_INPUT: INVERTER_POWER_INPUT_KEY,

    # Efficiency helper keys
    CanonicalKey.HEATING_13_24: EFFICIENCY_HEATING_13_24M_KEY,
    CanonicalKey.DHW_13_24: EFFICIENCY_DHW_13_24M_KEY,
    CanonicalKey.VD_HEATING_DAY: EFFICIENCY_HEATING_TODAY_KEY,
    CanonicalKey.VD_HEATING_TOTAL: EFFICIENCY_HEATING_1_12M_KEY,
    CanonicalKey.VD_DHW_DAY: EFFICIENCY_DHW_TODAY_KEY,
    CanonicalKey.VD_DHW_TOTAL: EFFICIENCY_DHW_1_12M_KEY,

    # Amount/power helper keys
    CanonicalKey.VD_HEATING_TOTAL: TOTAL_HEAT_PRODUCED_KEY,
    CanonicalKey.VD_HEATING_DAY: HEAT_PRODUCED_TODAY_KEY,
    CanonicalKey.VD_DHW_TOTAL: TOTAL_DHW_PRODUCED_KEY,
    CanonicalKey.VD_DHW_DAY: DHW_PRODUCED_TODAY_KEY,
}

# Mapping for energy consumption keys (POWER_CONSUMPTION_SECTION) -> consts
ENERGY_CONSUMED_MAP: dict[CanonicalKey, str] = {
    CanonicalKey.VD_HEATING_TOTAL: TOTAL_HEATING_CONSUMED_KEY,
    CanonicalKey.VD_HEATING_DAY: HEATING_CONSUMED_TODAY_KEY,
    CanonicalKey.VD_DHW_TOTAL: TOTAL_DHW_CONSUMED_KEY,
    CanonicalKey.VD_DHW_DAY: DHW_CONSUMED_TODAY_KEY,
}


def to_canonical_key(value: str | CanonicalKey) -> CanonicalKey | None:
    """Convert a string or CanonicalKey-like value to a CanonicalKey member.

    Returns the CanonicalKey if conversion succeeds, otherwise None.
    This centralizes string->enum conversion and keeps callers simple.
    """
    if isinstance(value, CanonicalKey):
        return value
    if not isinstance(value, str):
        return None
    try:
        return CanonicalKey(value)
    except Exception:
        return None


def get_aliases(value: str | CanonicalKey) -> list[str]:
    """Return the alias candidate list for a canonical name or string.

    - If given a CanonicalKey, return HEADER_ALIASES[CanonicalKey] or [].
    - If given a str that matches a CanonicalKey name, return that key's
      aliases list. Otherwise return a single-item list with the original
      string so callers can still perform literal matching.
    """
    if isinstance(value, CanonicalKey):
        return HEADER_ALIASES.get(value, [])
    if not isinstance(value, str):
        return []
    ck = to_canonical_key(value)
    if ck is None:
        return [value]
    return HEADER_ALIASES.get(ck, [value])
