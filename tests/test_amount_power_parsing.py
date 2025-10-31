from pathlib import Path
import sys

from tests.test_scraper_localization import _load_module_from_path, TESTDATA_DIR


def _load_modules():
    root = Path(__file__).resolve().parent.parent / "custom_components" / "stiebel_eltron_http"
    const_mod = sys.modules.get("custom_components.stiebel_eltron_http.const")
    if const_mod is None:
        const_mod = _load_module_from_path("custom_components.stiebel_eltron_http.const", root / "const.py")
    scraper_mod = sys.modules.get("custom_components.stiebel_eltron_http.scraper")
    if scraper_mod is None:
        scraper_mod = _load_module_from_path("custom_components.stiebel_eltron_http.scraper", root / "scraper.py")
    return const_mod, scraper_mod


def _assert_expected_values(data: dict, expected: dict):
    for k, v in expected.items():
        assert k in data, f"Missing key {k}"
        assert data[k] is not None, f"Value for {k} is None"
        assert isinstance(data[k], (int, float)), f"Value for {k} not numeric: {data[k]!r}"
        # allow small rounding differences
        assert round(float(data[k]), 3) == round(float(v), 3), f"Unexpected value for {k}: {data[k]!r} vs {v!r}"


def test_amount_and_power_parsing_de():
    const_mod, scraper_mod = _load_modules()
    client = scraper_mod.StiebelEltronScrapingClient(host="local.test", session=None)
    html_path = TESTDATA_DIR / "s_1_8_de.html"
    html = html_path.read_text(encoding="utf-8")
    data = client._extract_info_energy(html)

    expected = {
        # AMOUNT OF HEAT (values normalized to kWh by the scraper)
        const_mod.TOTAL_HEAT_PRODUCED_KEY: 2951.0,  # 2,951MWh -> 2951 kWh
        const_mod.HEAT_PRODUCED_TODAY_KEY: 132.03,  # 132,030kWh -> 132.03 kWh
        const_mod.TOTAL_DHW_PRODUCED_KEY: 2556.0,  # 2,556MWh -> 2556 kWh
        const_mod.DHW_PRODUCED_TODAY_KEY: 26.728,  # 26,728kWh -> 26.728 kWh

        # POWER CONSUMPTION (also normalized to kWh)
        const_mod.TOTAL_HEATING_CONSUMED_KEY: 458.0,  # 0,458MWh -> 458 kWh
        const_mod.HEATING_CONSUMED_TODAY_KEY: 24.383,  # 24,383kWh -> 24.383 kWh
        const_mod.TOTAL_DHW_CONSUMED_KEY: 572.0,  # 0,572MWh -> 572 kWh
        const_mod.DHW_CONSUMED_TODAY_KEY: 6.762,  # 6,762kWh -> 6.762 kWh
    }

    _assert_expected_values(data, expected)


def test_amount_and_power_parsing_en():
    const_mod, scraper_mod = _load_modules()
    client = scraper_mod.StiebelEltronScrapingClient(host="local.test", session=None)
    html_path = TESTDATA_DIR / "s_1_8_en.html"
    html = html_path.read_text(encoding="utf-8")
    data = client._extract_info_energy(html)

    expected = {
        const_mod.TOTAL_HEAT_PRODUCED_KEY: 2951.0,
        const_mod.HEAT_PRODUCED_TODAY_KEY: 132.03,
        const_mod.TOTAL_DHW_PRODUCED_KEY: 2556.0,
        const_mod.DHW_PRODUCED_TODAY_KEY: 26.728,
        const_mod.TOTAL_HEATING_CONSUMED_KEY: 458.0,
        const_mod.HEATING_CONSUMED_TODAY_KEY: 24.383,
        const_mod.TOTAL_DHW_CONSUMED_KEY: 572.0,
        const_mod.DHW_CONSUMED_TODAY_KEY: 6.762,
    }

    _assert_expected_values(data, expected)
