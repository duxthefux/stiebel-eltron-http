from pathlib import Path
import sys

from tests.test_scraper_localization import _load_module_from_path, TESTDATA_DIR


def test_efficiency_values_parsed():
    # Load const and scraper modules same way other tests do
    root = Path(__file__).resolve().parent.parent / "custom_components" / "stiebel_eltron_http"
    const_mod = sys.modules.get("custom_components.stiebel_eltron_http.const")
    if const_mod is None:
        const_mod = _load_module_from_path("custom_components.stiebel_eltron_http.const", root / "const.py")
    scraper_mod = sys.modules.get("custom_components.stiebel_eltron_http.scraper")
    if scraper_mod is None:
        scraper_mod = _load_module_from_path("custom_components.stiebel_eltron_http.scraper", root / "scraper.py")

    client = scraper_mod.StiebelEltronScrapingClient(host="local.test", session=None)
    html_path = TESTDATA_DIR / "s_1_8_de.html"
    html = html_path.read_text(encoding="utf-8")
    data = client._extract_info_energy(html)

    # Expected values from the EFFIZIENZ table in the fixture (updated from test data)
    expected = {
        const_mod.EFFICIENCY_HEATING_TODAY_KEY: 7.01,  # Updated from test data
        const_mod.EFFICIENCY_HEATING_1_12M_KEY: 6.37,  # Updated from test data
        const_mod.EFFICIENCY_HEATING_13_24M_KEY: 0.0,
        const_mod.EFFICIENCY_DHW_TODAY_KEY: 4.09,  # Updated from test data
        const_mod.EFFICIENCY_DHW_1_12M_KEY: 4.46,  # Updated from test data
        const_mod.EFFICIENCY_DHW_13_24M_KEY: 0.0,
    }

    for k, v in expected.items():
        assert k in data, f"Missing efficiency key {k}"
        assert data[k] is not None, f"Value for {k} is None"
        assert isinstance(data[k], (int, float)), f"Value for {k} not numeric: {data[k]!r}"
        # allow small rounding differences
        assert round(float(data[k]), 2) == round(float(v), 2), f"Unexpected value for {k}: {data[k]!r} vs {v!r}"
