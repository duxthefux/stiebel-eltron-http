import glob
import os
import sys

sys.path.insert(0, os.getcwd())

import pytest
import importlib.util

# Import the scraper module directly by path to avoid importing the package
# top-level `custom_components.__init__` which pulls in Home Assistant runtime
# symbols that may not be available in the test environment.
PACKAGE_DIR = os.path.join(os.getcwd(), "custom_components")
HEATPUMP_DIR = os.path.join(PACKAGE_DIR, "stiebel_eltron_http")

# Create lightweight package modules to allow relative imports inside the
# package modules (const.py, scraper.py) without executing the package
# __init__.py which depends on Home Assistant runtime components.
import types

sys.modules.setdefault("custom_components", types.ModuleType("custom_components"))
sys.modules.setdefault(
    "custom_components.stiebel_eltron_http",
    types.ModuleType("custom_components.stiebel_eltron_http"),
)

# Load const.py first as package module so scraper's relative imports work.
CONST_PATH = os.path.join(HEATPUMP_DIR, "const.py")
const_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.const", CONST_PATH
)
const_mod = importlib.util.module_from_spec(const_spec)
const_spec.loader.exec_module(const_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.const"] = const_mod

SCRAPER_PATH = os.path.join(HEATPUMP_DIR, "scraper.py")
spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.scraper", SCRAPER_PATH
)
scraper_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.scraper"] = scraper_mod
StiebelEltronScrapingClient = scraper_mod.StiebelEltronScrapingClient


TESTDATA_DIR = os.path.join(os.getcwd(), "scripts", "testdata")


def _all_html_files():
    return sorted(glob.glob(os.path.join(TESTDATA_DIR, "*.html")))


@pytest.mark.parametrize("html_file", _all_html_files())
def test_extracted_values_not_none(html_file):
    """For each test HTML, run each extractor and assert any returned value is not None.

    Empty extractor results are allowed (no attributes on that page). But if an
    extractor returns a key, its value must be non-None.
    """
    with open(html_file, "r", encoding="utf-8") as fh:
        text = fh.read()

    client = StiebelEltronScrapingClient("dummy", None)

    extractors = [
        ("info_system", client._extract_info_system),
        ("info_heatpump", client._extract_info_heatpump),
        ("diagnosis_system", client._extract_diagnosis_system),
        ("profile_network", client._extract_profile_network),
    ]

    for name, func in extractors:
        result = func(text)
        if not result:
            # No attributes found by this extractor for this page — that's fine.
            continue
        for key, val in result.items():
            assert val is not None, (
                f"File {os.path.basename(html_file)}: extractor {name} returned None for key {key}"
            )
