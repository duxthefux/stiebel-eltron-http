"""Small pure parsing helpers extracted for unit testing.

Only conversion helpers are included here (temperatures, percentages,
energy and generic numeric parsing). These are pure functions with no
Home Assistant dependencies so we can add focused unit tests.
"""
from __future__ import annotations

import re
import bs4

from .mapping import HEADER_ALIASES, CanonicalKey, to_canonical_key, get_aliases


def _convert_temperature(value: str) -> float | None:
    """Convert a Stiebel Eltron ISG temperature format (23,3°C) to a float."""
    if isinstance(value, str):
        value = value.replace(",", ".").replace("°C", "").strip()
    try:
        return float(value)
    except ValueError:
        return None


def _convert_percentage(value: str) -> float | None:
    """Convert a Stiebel Eltron ISG percentage format (53,3%) to a float."""
    if isinstance(value, str):
        value = value.replace(",", ".").replace("%", "").strip()
    try:
        return float(value)
    except ValueError:
        return None


def _convert_energy(value: str) -> float | None:
    """Convert a Stiebel Eltron ISG energy format (24,249MWh) to a float in kWh."""
    if not isinstance(value, str):
        return None

    low = value.lower()
    is_kwh = "kwh" in low
    is_mwh = "mwh" in low
    if not (is_kwh or is_mwh):
        return None

    # remove unit text case-insensitively and normalize decimal comma
    clean_value = value.replace(",", ".")
    clean_value = re.sub(r"(?i)mwh", "", clean_value)
    clean_value = re.sub(r"(?i)kwh", "", clean_value).strip()
    try:
        result = float(clean_value)
        if is_mwh:
            result *= 1000  # Convert MWh to kWh

    except ValueError:
        return None
    else:
        return result


def _convert_numeric(value: str) -> float | None:
    """Convert a numeric string with units (e.g., '5,22bar', '31,9l/min', '1,2kW') to float.

    Strips non-numeric characters except comma, dot, minus and then converts.
    """
    if not isinstance(value, str):
        return None
    # keep digits, comma, dot, minus and exponent markers just in case
    cleaned = re.sub(r"[^0-9,\.\-eE]", "", value)
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _normalize_text(value: str) -> str:
    """Normalize a header/label string for robust comparisons.

    Lowercase, collapse whitespace and strip surrounding whitespace so
    comparisons are case-insensitive and tolerant to minor spacing differences.
    """
    if not isinstance(value, str):
        return ""
    # collapse multiple whitespace into single spaces, strip and lowercase
    return re.sub(r"\s+", " ", value).strip().lower()


def _matches_alias(header_text: str, candidates: list[str]) -> bool:
    """Return True if header_text matches any candidate alias.

    Matching rules (best-effort):
    - Normalize both header_text and candidate
    - Consider equal, candidate substring of header_text or header_text substring of candidate
      (this covers cases like "ISTTEMPERATUR HK 1" matching alias "ISTTEMPERATUR HK")
    """
    nh = _normalize_text(header_text)
    if not nh:
        return False
    for c in candidates:
        nc = _normalize_text(c)
        if not nc:
            continue
        if nh == nc or nc in nh or nh in nc:
            return True
    return False


def _find_best_alias(header_text: str, aliases: dict[CanonicalKey, list[str]] | None = None) -> CanonicalKey | None:
    """Find the best-matching canonical alias for header_text using provided aliases.

    When multiple alias candidates match (due to substring overlaps) prefer the
    most specific candidate (longest normalized length). Returns the canonical
    alias key (as present in aliases) or None if no candidate matched.
    """
    # default to module-level alias map when none provided
    if aliases is None:
        aliases = HEADER_ALIASES

    nh = _normalize_text(header_text)
    if not nh:
        return None
    best = None
    best_len = -1
    for canonical, candidates in aliases.items():
        for c in candidates:
            nc = _normalize_text(c)
            if not nc:
                continue
            # Only match when candidate equals header or candidate is a substring
            # of the header (candidate shorter than header). Do NOT match when
            # the header is a substring of the candidate to avoid assigning the
            # wrong, longer candidate to a shorter header (e.g. "INVERTER POWER"
            # vs "INVERTER POWER CONSUMPTION").
            if nh == nc or nc in nh:
                l = len(nc)
                if l > best_len:
                    best_len = l
                    best = canonical
    return best


def extract_energy(table: bs4.element.Tag, expected_header: CanonicalKey | str) -> float | None:
    """Extract an energy value from a two-column table given the expected header.

    expected_header may be a canonical key (like "VD_HEATING_TOTAL") or an
    explicit string. When a canonical key is used, the function consults
    HEADER_ALIASES. This is a pure function operating on a BeautifulSoup
    table Tag and uses the conversion helpers in this module.
    """
    table_rows = table.find_all("tr")
    for curr_table_row in table_rows:
        elems = curr_table_row.find_all(["td", "th"])  # type: ignore  # noqa: PGH003

        if not elems:
            continue
        texts = [elem.get_text(strip=True) for elem in elems]

        if len(texts) < 2:  # noqa: PLR2004
            continue

        matches: list[str] = get_aliases(expected_header)

        if _matches_alias(texts[0], matches):
            return _convert_energy(texts[1])

    return None


def extract_temperature(table: bs4.element.Tag, expected_header: CanonicalKey | str) -> float | None:
    """Extract a temperature value from a two-column table given the expected header."""
    table_rows = table.find_all("tr")
    for curr_table_row in table_rows:
        elems = curr_table_row.find_all(["td", "th"])  # type: ignore  # noqa: PGH003

        if not elems:
            continue
        texts = [elem.get_text(strip=True) for elem in elems]

        if len(texts) < 2:
            continue

        matches: list[str] = get_aliases(expected_header)

        if _matches_alias(texts[0], matches):
            return _convert_temperature(texts[1])

    return None


def extract_percentage(table: bs4.element.Tag, expected_header: CanonicalKey | str) -> float | None:
    """Extract a percentage value from a two-column table given the expected header."""
    table_rows = table.find_all("tr")
    for curr_table_row in table_rows:
        elems = curr_table_row.find_all(["td", "th"])  # type: ignore  # noqa: PGH003

        if not elems:
            continue
        texts = [elem.get_text(strip=True) for elem in elems]

        if len(texts) < 2:
            continue

        matches: list[str] = get_aliases(expected_header)

        if _matches_alias(texts[0], matches):
            return _convert_percentage(texts[1])

    return None


def find_section_tables(soup: bs4.BeautifulSoup, section_key: CanonicalKey | str) -> list[bs4.element.Tag]:
    """Return a list of tables whose first header cell matches section_key aliases.

    section_key may be a canonical key present in HEADER_ALIASES or an explicit
    header string. Matching is delegated to _matches_alias.
    """
    tables: list[bs4.element.Tag] = []
    all_tables = soup.find_all("table")
    for curr_table in all_tables:
        # Try to read the first header text for the table (if present)
        rows = curr_table.find_all("tr")
        if not rows:
            continue
        first_row = rows[0]
        headers = first_row.find_all(["th"])  # type: ignore  # noqa: PGH003
        section_title = headers[0].get_text(strip=True) if headers else ""

        matches: list[str] = []
        matches = get_aliases(section_key)

        if _matches_alias(section_title, matches):
            tables.append(curr_table)

    return tables


def find_first_section_table(soup: bs4.BeautifulSoup, section_key: CanonicalKey | str) -> bs4.element.Tag | None:
    """Return the first matching table for section_key or None if not found."""
    tables = find_section_tables(soup, section_key)
    return tables[0] if tables else None


def table_to_dict(table: bs4.element.Tag) -> dict[str, str]:
    """Convert a two-column HTML table into a dict mapping first-col -> second-col text.

    Only rows with at least two cells are considered. Text values are stripped.
    """
    out: dict[str, str] = {}
    rows = table.find_all("tr")
    for r in rows:
        elems = r.find_all(["td", "th"])  # type: ignore  # noqa: PGH003
        if not elems or len(elems) < 2:
            continue
        key = elems[0].get_text(strip=True)
        val = elems[1].get_text(strip=True)
        out[key] = val
    return out


def parse_process_data_table(table: bs4.element.Tag) -> dict[CanonicalKey, float | None]:
    """Parse a process-data style two-column table and return canonical -> value.

    The function resolves the best-matching canonical alias for each first-column
    label and converts the second-column using the appropriate conversion helper
    (temperature, percentage, numeric). Returns a mapping from canonical alias
    (strings like 'RETURN_TEMPERATURE') to numeric values (or None when parsing
    fails). This function is intentionally pure and does not import project
    constants so the caller (scraper) can map canonical aliases to const keys.
    """
    out: dict[CanonicalKey, float | None] = {}

    temp_keys = {
        CanonicalKey.RETURN_TEMPERATURE,
        CanonicalKey.SUPPLY_TEMPERATURE,
        CanonicalKey.FROST_PROTECTION_TEMPERATURE,
        CanonicalKey.OUTSIDE_TEMPERATURE,
        CanonicalKey.COMPRESSOR_INLET_TEMPERATURE,
        CanonicalKey.HOT_GAS_TEMPERATURE,
        CanonicalKey.CONDENSER_TEMPERATURE,
        CanonicalKey.OIL_SUMP_TEMPERATURE,
        CanonicalKey.EVAPORATOR_INLET_TEMPERATURE,
        CanonicalKey.EVAPORATOR_OUTLET_TEMPERATURE,
    }

    percentage_keys = {
        CanonicalKey.FAN_POWER_RELATIVE,
    }

    numeric_keys = {
        CanonicalKey.LOW_PRESSURE,
        CanonicalKey.HIGH_PRESSURE,
        CanonicalKey.WATER_FLOW,
        CanonicalKey.INVERTER_CURRENT,
        CanonicalKey.INVERTER_VOLTAGE,
        CanonicalKey.COMPRESSOR_SPEED_ACTUAL,
        CanonicalKey.COMPRESSOR_SPEED_TARGET,
        CanonicalKey.INVERTER_POWER,
        CanonicalKey.INVERTER_POWER_INPUT,
    }

    rows = table.find_all("tr")
    for r in rows:
        elems = r.find_all(["td", "th"])  # type: ignore  # noqa: PGH003
        if not elems:
            continue
        texts = [e.get_text(strip=True) for e in elems]
        if len(texts) < 2:
            continue
        key_text = texts[0]
        val_text = texts[1]

        matched = _find_best_alias(key_text)
        if matched is None:
            continue

        if matched in temp_keys:
            out[matched] = _convert_temperature(val_text)
        elif matched in percentage_keys:
            out[matched] = _convert_percentage(val_text)
        elif matched in numeric_keys:
            out[matched] = _convert_numeric(val_text)
        # else: unknown matched alias; ignore

    return out


def parse_efficiency_table(table: bs4.element.Tag) -> dict[CanonicalKey, float | None]:
    """Parse an efficiency (COP-like) table and return a mapping of detected keys.

    The table may contain rows labelled for heating or DHW and sometimes rows
    for the '13-24' month range which are not present in the canonical alias
    map. This function returns a dict using the following keys when present:
      - 'VD_HEATING_DAY', 'VD_HEATING_TOTAL', 'VD_DHW_DAY', 'VD_DHW_TOTAL'
      - 'HEATING_13_24' and 'DHW_13_24' for detected 13-24 rows

    Values are converted to float where possible using _convert_numeric.
    """
    out: dict[CanonicalKey, float | None] = {}

    rows = table.find_all("tr")
    for r in rows:
        elems = r.find_all(["td", "th"])  # type: ignore  # noqa: PGH003
        if not elems:
            continue
        texts = [e.get_text(strip=True) for e in elems]
        if len(texts) < 2:
            continue
        key_text = texts[0]
        val_text = texts[1]

        # Normalize key text for substring checks
        nkey = _normalize_text(key_text)
        # Detect '13-24' rows explicitly
        if "13-24" in nkey or "13–24" in nkey or "13 24" in nkey:
            # Decide whether it's DHW/warm or heating by presence of 'warm'/'dhw'
            if "warm" in nkey or "dhw" in nkey:
                out[CanonicalKey.DHW_13_24] = _convert_numeric(val_text)
            else:
                out[CanonicalKey.HEATING_13_24] = _convert_numeric(val_text)
            continue

        # Otherwise attempt canonical alias matching
        matched = _find_best_alias(key_text)
        if matched in (CanonicalKey.VD_HEATING_DAY, CanonicalKey.VD_HEATING_SUM, CanonicalKey.NHZ_HEATING_SUM):
            # map several possible heating canonical labels to today's heating
            out[CanonicalKey.VD_HEATING_DAY] = _convert_numeric(val_text)
        elif matched == CanonicalKey.VD_HEATING_TOTAL:
            out[CanonicalKey.VD_HEATING_TOTAL] = _convert_numeric(val_text)
        elif matched in (CanonicalKey.VD_DHW_DAY, CanonicalKey.NHZ_DHW_SUM):
            out[CanonicalKey.VD_DHW_DAY] = _convert_numeric(val_text)
        elif matched == CanonicalKey.VD_DHW_TOTAL:
            out[CanonicalKey.VD_DHW_TOTAL] = _convert_numeric(val_text)

    return out


def parse_amount_power_table(table: bs4.element.Tag) -> dict[CanonicalKey, float | None]:
    """Parse an AMOUNT_OF_HEAT / POWER_CONSUMPTION style table.

    Returns a mapping of canonical aliases to numeric values for the common
    energy rows:
      - 'VD_HEATING_TOTAL', 'VD_HEATING_DAY', 'VD_DHW_TOTAL', 'VD_DHW_DAY'

    Uses _matches_alias/HEADER_ALIASES to resolve localized labels and
    _convert_energy to normalize units (kWh/MWh).
    """
    out: dict[CanonicalKey, float | None] = {}
    rows = table.find_all("tr")
    for r in rows:
        elems = r.find_all(["td", "th"])  # type: ignore  # noqa: PGH003
        if not elems:
            continue
        texts = [e.get_text(strip=True) for e in elems]
        if len(texts) < 2:
            continue
        key_text = texts[0]
        val_text = texts[1]

        # Try to match against the known canonical energy labels
        for canonical in (
            CanonicalKey.VD_HEATING_TOTAL,
            CanonicalKey.VD_HEATING_DAY,
            CanonicalKey.VD_DHW_TOTAL,
            CanonicalKey.VD_DHW_DAY,
        ):
            candidates = get_aliases(canonical)
            if _matches_alias(key_text, candidates):
                out[canonical] = _convert_energy(val_text)
                break

    return out


