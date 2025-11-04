import importlib.util
import sys
import types
from pathlib import Path

import pytest


TESTDATA_DIR = Path(__file__).resolve().parent.parent / "scripts" / "testdata"


def _load_module_from_path(module_name: str, path: Path):
    """Load a module by filesystem path under the given module_name.

    This avoids importing the package __init__ which depends on Home Assistant.
    """
    if module_name in sys.modules:
        return sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    # Ensure package context is set so relative imports in the module work.
    parent = module_name.rpartition(".")[0]
    module.__package__ = parent
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# Inject a minimal homeassistant.const so scraper can import ATTR_SW_VERSION
if "homeassistant.const" not in sys.modules:
    ha_mod = types.ModuleType("homeassistant")
    ha_const = types.ModuleType("homeassistant.const")
    ha_const.ATTR_SW_VERSION = "sw_version"
    sys.modules["homeassistant"] = ha_mod
    sys.modules["homeassistant.const"] = ha_const


@pytest.fixture(scope="module")
def scraper_client():
    root = Path(__file__).resolve().parent.parent / "custom_components" / "stiebel_eltron_http"
    const_mod = _load_module_from_path(
        "custom_components.stiebel_eltron_http.const", root / "const.py"
    )
    scraper_mod = _load_module_from_path(
        "custom_components.stiebel_eltron_http.scraper", root / "scraper.py"
    )
    # Instantiate a client instance for calling instance methods (parsing helpers).
    client = scraper_mod.StiebelEltronScrapingClient(host="local.test", session=None)
    return client


def _all_localized_files():
    # find files like s_1_1_de.html, s_1_1_en.html, s_1_1_fr.html, s_1_1_nl.html, s_1_1_it.html, s_1_1_sv.html, s_1_1_es.html, s_1_1_pl.html
    files = (
        list(TESTDATA_DIR.glob("*_de.html")) 
        + list(TESTDATA_DIR.glob("*_en.html"))
        + list(TESTDATA_DIR.glob("*_fr.html"))
        + list(TESTDATA_DIR.glob("*_nl.html"))
        + list(TESTDATA_DIR.glob("*_it.html"))
        + list(TESTDATA_DIR.glob("*_sv.html"))
        + list(TESTDATA_DIR.glob("*_es.html"))
        + list(TESTDATA_DIR.glob("*_pl.html"))
    )
    return sorted(files)


@pytest.mark.parametrize("file_path", _all_localized_files())
def test_auto_detect_language(scraper_client, file_path: Path):
    html = file_path.read_text(encoding="utf-8")
    # Derive expected language from the ISG language-switch element which is
    # the sole source of truth we rely on for language detection.
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    expected = None
    lang_elem = soup.select_one(".eingestelle_sprache a")
    if lang_elem and lang_elem.string:
        link_text = lang_elem.string.strip().lower()
        if "english" in link_text:
            expected = "en"
        elif "deutsch" in link_text or "german" in link_text:
            expected = "de"
        elif "français" in link_text or "francais" in link_text or "french" in link_text:
            expected = "fr"
        elif "nederlands" in link_text or "dutch" in link_text:
            expected = "nl"
        elif "italiano" in link_text or "italian" in link_text:
            expected = "it"
        elif "svenska" in link_text or "swedish" in link_text:
            expected = "sv"
        elif "español" in link_text or "espanol" in link_text or "spanish" in link_text:
            expected = "es"
        elif "polski" in link_text or "polish" in link_text:
            expected = "pl"

    if expected is None:
        # fallback to filename suffix if the element is missing
        if file_path.name.endswith("_de.html"):
            expected = "de"
        elif file_path.name.endswith("_en.html"):
            expected = "en"
        elif file_path.name.endswith("_fr.html"):
            expected = "fr"
        elif file_path.name.endswith("_nl.html"):
            expected = "nl"
        elif file_path.name.endswith("_it.html"):
            expected = "it"
        elif file_path.name.endswith("_sv.html"):
            expected = "sv"
        elif file_path.name.endswith("_es.html"):
            expected = "es"
        elif file_path.name.endswith("_pl.html"):
            expected = "pl"
    detected = scraper_client._auto_detect_language(html)
    assert detected == expected, f"{file_path.name} detected as {detected}, expected {expected}"


@pytest.mark.parametrize("file_path", TESTDATA_DIR.glob("s_1_1_*.html"))
def test_info_heatpump_energy_parsing(scraper_client, file_path: Path):
    html = file_path.read_text(encoding="utf-8")
    data = scraper_client._extract_info_heatpump(html)
    # Expect at least the total heat produced key to be present (may be None if not parsed)
    from custom_components.stiebel_eltron_http.const import TOTAL_HEAT_PRODUCED_KEY

    assert TOTAL_HEAT_PRODUCED_KEY in data
    val = data[TOTAL_HEAT_PRODUCED_KEY]
    # if present, should be numeric (kWh)
    if val is not None:
        assert isinstance(val, (int, float))


@pytest.mark.parametrize("file_path", TESTDATA_DIR.glob("s_1_1_de.html"))
def test_return_temperature_parsing(scraper_client, file_path: Path):
    """Ensure the RETURN_TEMPERATURE_KEY is parsed from the process data table.

    The ISG German pages use labels like 'RÜCKLAUFTEMPERATUR' or 'RUECKLAUFTEMPERATUR'.
    We assert the scraper returns a numeric value when present.
    """
    html = file_path.read_text(encoding="utf-8")
    # Process values live on the Heat Pump page (s=1,1)
    data = scraper_client._extract_info_heatpump(html)
    from custom_components.stiebel_eltron_http.const import RETURN_TEMPERATURE_KEY

    assert RETURN_TEMPERATURE_KEY in data
    val = data[RETURN_TEMPERATURE_KEY]
    if val is not None:
        assert isinstance(val, (int, float))


@pytest.mark.parametrize("file_path", [
    TESTDATA_DIR / "s_1_1_de.html",
    TESTDATA_DIR / "s_1_1_en.html",
    TESTDATA_DIR / "s_1_1_fr.html",
    TESTDATA_DIR / "s_1_1_nl.html",
    TESTDATA_DIR / "s_1_1_it.html",
    TESTDATA_DIR / "s_1_1_sv.html",
    TESTDATA_DIR / "s_1_1_es.html",
    TESTDATA_DIR / "s_1_1_pl.html",
])
def test_all_process_values_parsing(scraper_client, file_path: Path):
    """Ensure the scraper extracts/processes all numeric process values on the heat-pump page.

    The test runs against German, English, French, Dutch, Italian, Swedish, Spanish, and Polish snapshots and asserts that for a
    canonical set of process metric keys the scraper returns numeric values when
    present. It also checks that at least a few metrics are parsed from the page.
    """
    from custom_components.stiebel_eltron_http.const import (
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
    )

    process_keys = [
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
    ]

    html = file_path.read_text(encoding="utf-8")
    # Process values live on the Heat Pump page (s=1,1)
    data = scraper_client._extract_info_heatpump(html)

    parsed_count = 0
    for k in process_keys:
        if k in data:
            parsed_count += 1
            v = data[k]
            if v is not None:
                assert isinstance(v, (int, float)), f"{k} parsed but not numeric: {v!r}"

    # Expect at least a few process metrics to be parsed from the page.
    # German snapshots usually contain many process labels; English snapshots
    # may contain fewer depending on firmware/localization. Allow a smaller
    # minimum for English pages.
    min_expected = 3 if file_path.name.endswith("_de.html") else 1
    assert parsed_count >= min_expected, (
        f"Too few process metrics parsed from {file_path.name}: {parsed_count} (expected >= {min_expected})"
    )


@pytest.mark.parametrize("file_path", TESTDATA_DIR.glob("s_2_7_*.html"))
def test_diagnosis_version_parsing(scraper_client, file_path: Path):
    html = file_path.read_text(encoding="utf-8")
    data = scraper_client._extract_diagnosis_system(html)
    # The scraper uses ATTR_SW_VERSION key (injected above as 'sw_version')
    assert "sw_version" in data
    ver = data["sw_version"]
    assert isinstance(ver, str) and ver.count(".") >= 2


@pytest.mark.parametrize("file_path,expected_map", [
    (
        TESTDATA_DIR / "s_1_1_en.html",
        {
            # English snapshot expected numeric values
            "RETURN_TEMPERATURE_KEY": 42.6,
            "SUPPLY_TEMPERATURE_KEY": 44.7,
            "FROST_PROTECTION_TEMPERATURE_KEY": 47.2,
            "OUTSIDE_TEMPERATURE_KEY": 11.0,
            "COMPRESSOR_INLET_TEMPERATURE_KEY": 13.6,
            "HOT_GAS_TEMPERATURE_KEY": 63.8,
            "CONDENSER_TEMPERATURE_KEY": 42.7,
            "OIL_SUMP_TEMPERATURE_KEY": 60.4,
            "LOW_PRESSURE_KEY": 5.56,
            "HIGH_PRESSURE_KEY": 15.25,
            "WATER_FLOW_KEY": 32.3,
            "INVERTER_CURRENT_KEY": 1.5,
            "INVERTER_VOLTAGE_KEY": 226.5,
            "COMPRESSOR_SPEED_ACTUAL_KEY": 21,
            "COMPRESSOR_SPEED_TARGET_KEY": 21,
            "FAN_POWER_RELATIVE_KEY": 40,
            "EVAPORATOR_INLET_TEMPERATURE_KEY": 9.0,
            "EVAPORATOR_OUTLET_TEMPERATURE_KEY": 10.0,
            "INVERTER_POWER_INPUT_KEY": 0.83,
            "INVERTER_POWER_KEY": 0.8,
        },
    ),
    (
        TESTDATA_DIR / "s_1_1_de.html",
        {
            # German snapshot expected numeric values
            "RETURN_TEMPERATURE_KEY": 42.5,
            "SUPPLY_TEMPERATURE_KEY": 44.7,
            "FROST_PROTECTION_TEMPERATURE_KEY": 47.2,
            "OUTSIDE_TEMPERATURE_KEY": 11.0,
            "COMPRESSOR_INLET_TEMPERATURE_KEY": 13.6,
            "HOT_GAS_TEMPERATURE_KEY": 64.1,
            "CONDENSER_TEMPERATURE_KEY": 42.7,
            "OIL_SUMP_TEMPERATURE_KEY": 60.7,
            "LOW_PRESSURE_KEY": 5.55,
            "HIGH_PRESSURE_KEY": 15.22,
            "WATER_FLOW_KEY": 32.2,
            "INVERTER_CURRENT_KEY": 1.5,
            "INVERTER_VOLTAGE_KEY": 225.8,
            "COMPRESSOR_SPEED_ACTUAL_KEY": 20,
            "COMPRESSOR_SPEED_TARGET_KEY": 21,
            "FAN_POWER_RELATIVE_KEY": 40,
            "EVAPORATOR_INLET_TEMPERATURE_KEY": 9.0,
            "EVAPORATOR_OUTLET_TEMPERATURE_KEY": 10.0,
            "INVERTER_POWER_INPUT_KEY": 0.87,
            "INVERTER_POWER_KEY": 0.8,
        },
    ),
])
def test_expected_process_values(scraper_client, file_path: Path, expected_map: dict):
    """Assert exact numeric conversions for a set of canonical keys on localized snapshots.

    Uses a small relative tolerance for floats to accommodate minor parsing/rounding differences.
    """
    # import canonical constant names to translate keys
    # Avoid importing package __init__ (which depends on Home Assistant). Prefer
    # the module already loaded by the fixture or load it directly from file.
    import sys
    const_mod = sys.modules.get("custom_components.stiebel_eltron_http.const")
    if const_mod is None:
        root = Path(__file__).resolve().parent.parent / "custom_components" / "stiebel_eltron_http"
        const_mod = _load_module_from_path("custom_components.stiebel_eltron_http.const", root / "const.py")
    html = file_path.read_text(encoding="utf-8")
    # Process values live on the Heat Pump page (s=1,1)
    data = scraper_client._extract_info_heatpump(html)

    for const_name, expected in expected_map.items():
        # Map the constant name to the actual key value in const module
        assert hasattr(const_mod, const_name), f"Const {const_name} not found in const.py"
        key = getattr(const_mod, const_name)
        assert key in data, f"Expected key {key} missing from parsed data of {file_path.name}"
        val = data[key]
        # Allow None only if expected is None (not applicable here)
        assert val is not None, f"Value for {key} is None in {file_path.name}"
        # Compare numeric with tolerant approx for floats
        if isinstance(expected, (int,)):
            assert val == expected, f"{key} expected {expected!r} got {val!r} in {file_path.name}"
        else:
            # use pytest.approx for float comparisons
            assert val == pytest.approx(expected, rel=1e-3), f"{key} expected {expected!r} got {val!r} in {file_path.name}"
