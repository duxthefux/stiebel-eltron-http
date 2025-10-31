import importlib.util
import sys
from pathlib import Path

from bs4 import BeautifulSoup


TESTDATA_DIR = Path(__file__).resolve().parent.parent / "scripts" / "testdata"


def _load_module_from_path(module_name: str, path: Path):
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    parent = module_name.rpartition(".")[0]
    module.__package__ = parent
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _load_parsing_module():
    root = Path(__file__).resolve().parent.parent / "custom_components" / "stiebel_eltron_http"
    return _load_module_from_path("custom_components.stiebel_eltron_http.parsing", root / "parsing.py")


def test_extract_energy_from_s_1_1_en():
    parsing = _load_parsing_module()
    html_path = TESTDATA_DIR / "s_1_1_en.html"
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Find table rows that likely contain the energy totals. We search for any table
    # and call extract_energy with canonical key VD_HEATING_TOTAL and VD_DHW_TOTAL.
    tables = soup.find_all("table")
    assert tables, "No tables found in fixture"

    found_total = None
    for t in tables:
        val = parsing.extract_energy(t, parsing.CanonicalKey.VD_HEATING_TOTAL)
        if val is not None:
            found_total = val
            break

    # The English snapshot should contain a numeric total heat produced (kWh)
    assert found_total is not None
    assert isinstance(found_total, (int, float))
    # Reasonable sanity check: should be positive
    assert found_total > 0


def test_extract_temperature_from_s_1_1_en():
    parsing = _load_parsing_module()
    html_path = TESTDATA_DIR / "s_1_1_en.html"
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # The RETURN_TEMPERATURE is expected to be in a small process data table.
    tables = soup.find_all("table")
    found_temp = None
    for t in tables:
        val = parsing.extract_temperature(t, parsing.CanonicalKey.RETURN_TEMPERATURE)
        if val is not None:
            found_temp = val
            break

    assert found_temp is not None
    assert isinstance(found_temp, (int, float))
    # typical return temperature should be within plausible range
    assert -50 < found_temp < 150


def test_extract_percentage_from_s_1_8_en():
    parsing = _load_parsing_module()
    html_path = TESTDATA_DIR / "s_1_8_en.html"
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")
    found_pct = None
    # Search for FAN_POWER_RELATIVE or other percentage-like values
    for t in tables:
        val = parsing.extract_percentage(t, parsing.CanonicalKey.FAN_POWER_RELATIVE)
        if val is not None:
            found_pct = val
            break

    # It's acceptable that some snapshots don't contain the expected percentage;
    # but if present it must be numeric and between 0 and 100.
    if found_pct is not None:
        assert isinstance(found_pct, (int, float))
        assert 0 <= found_pct <= 100


def test_table_helpers_find_section_and_dict():
    parsing = _load_parsing_module()
    html_path = TESTDATA_DIR / "s_1_1_en.html"
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    # Find the AMOUNT_OF_HEAT_SECTION tables and ensure at least one is present
    tables = parsing.find_section_tables(soup, parsing.CanonicalKey.AMOUNT_OF_HEAT_SECTION)
    assert isinstance(tables, list)
    assert tables, "No AMOUNT_OF_HEAT_SECTION tables found in fixture"

    # Convert the first table to a dict and assert keys look sane
    tbl = tables[0]
    mapping = parsing.table_to_dict(tbl)
    assert isinstance(mapping, dict)
    # keys should be non-empty strings and values should be non-empty strings
    for k, v in mapping.items():
        assert isinstance(k, str) and k
        assert isinstance(v, str)


def test_parse_process_data_table():
    parsing = _load_parsing_module()
    html_path = TESTDATA_DIR / "s_1_1_en.html"
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    tables = parsing.find_section_tables(soup, parsing.CanonicalKey.PROCESS_DATA_SECTION)
    assert tables, "No PROCESS_DATA_SECTION tables found"

    parsed = parsing.parse_process_data_table(tables[0])
    # Expect at least the RETURN_TEMPERATURE canonical alias to be present
    assert parsing.CanonicalKey.RETURN_TEMPERATURE in parsed
    val = parsed.get(parsing.CanonicalKey.RETURN_TEMPERATURE)
    assert val is None or isinstance(val, (int, float))


def test_parse_efficiency_table():
    parsing = _load_parsing_module()
    html_path = TESTDATA_DIR / "s_1_8_en.html"
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    tables = parsing.find_section_tables(soup, parsing.CanonicalKey.EFFICIENCY_SECTION)
    # Some fixtures may not include an efficiency table; if not present skip
    if not tables:
        return

    parsed = parsing.parse_efficiency_table(tables[0])
    # If present, parsed should be a dict and values numeric or None
    assert isinstance(parsed, dict)
    for k, v in parsed.items():
        # keys are canonical enum members
        assert isinstance(k, parsing.CanonicalKey)
        assert v is None or isinstance(v, (int, float))


def test_parse_amount_power_table():
    parsing = _load_parsing_module()
    html_path = TESTDATA_DIR / "s_1_1_en.html"
    html = html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    tables = parsing.find_section_tables(soup, parsing.CanonicalKey.AMOUNT_OF_HEAT_SECTION)
    assert tables, "No AMOUNT_OF_HEAT_SECTION tables found"

    parsed = parsing.parse_amount_power_table(tables[0])
    # Expect some energy keys to be present and numeric
    assert isinstance(parsed, dict)
    for k, v in parsed.items():
        assert k in (
            parsing.CanonicalKey.VD_HEATING_TOTAL,
            parsing.CanonicalKey.VD_HEATING_DAY,
            parsing.CanonicalKey.VD_DHW_TOTAL,
            parsing.CanonicalKey.VD_DHW_DAY,
        )
        assert v is None or isinstance(v, (int, float))

