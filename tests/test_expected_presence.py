import os
import sys
import importlib.util
import types

sys.path.insert(0, os.getcwd())

# Load minimal package modules and const/scraper to avoid importing HA runtime
sys.modules.setdefault("custom_components", types.ModuleType("custom_components"))
sys.modules.setdefault(
    "custom_components.stiebel_eltron_http",
    types.ModuleType("custom_components.stiebel_eltron_http"),
)

CONST_PATH = os.path.join(os.getcwd(), "custom_components", "stiebel_eltron_http", "const.py")
const_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.const", CONST_PATH
)
const_mod = importlib.util.module_from_spec(const_spec)
const_spec.loader.exec_module(const_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.const"] = const_mod

# Load mapping.py as it's needed by parsing.py
MAPPING_PATH = os.path.join(os.getcwd(), "custom_components", "stiebel_eltron_http", "mapping.py")
mapping_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.mapping", MAPPING_PATH
)
mapping_mod = importlib.util.module_from_spec(mapping_spec)
mapping_spec.loader.exec_module(mapping_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.mapping"] = mapping_mod

# Load parsing.py as it's imported by scraper.py
PARSING_PATH = os.path.join(os.getcwd(), "custom_components", "stiebel_eltron_http", "parsing.py")
parsing_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.parsing", PARSING_PATH
)
parsing_mod = importlib.util.module_from_spec(parsing_spec)
parsing_spec.loader.exec_module(parsing_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.parsing"] = parsing_mod

SCRAPER_PATH = os.path.join(os.getcwd(), "custom_components", "stiebel_eltron_http", "scraper.py")
spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.scraper", SCRAPER_PATH
)
scraper_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.scraper"] = scraper_mod

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from custom_components.stiebel_eltron_http.const import (
    DHW_TEMPERATURE_KEY,
    OUTSIDE_TEMPERATURE_KEY,
    TOTAL_HEAT_PRODUCED_KEY,
    TOTAL_DHW_PRODUCED_KEY,
)


BASE = os.path.join(os.getcwd(), "scripts", "testdata")


def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def test_s_1_0_contains_dhw_and_outside():
    text_en = _load(os.path.join(BASE, "s_1_0_en.html"))
    text_de = _load(os.path.join(BASE, "s_1_0_de.html"))
    client = StiebelEltronScrapingClient("dummy", None)

    res_en = client._extract_info_system(text_en)
    res_de = client._extract_info_system(text_de)

    assert DHW_TEMPERATURE_KEY in res_en and res_en[DHW_TEMPERATURE_KEY] is not None
    assert OUTSIDE_TEMPERATURE_KEY in res_en and res_en[OUTSIDE_TEMPERATURE_KEY] is not None

    assert DHW_TEMPERATURE_KEY in res_de and res_de[DHW_TEMPERATURE_KEY] is not None
    assert OUTSIDE_TEMPERATURE_KEY in res_de and res_de[OUTSIDE_TEMPERATURE_KEY] is not None


def test_s_1_1_contains_totals_and_return_temp():
    text_en = _load(os.path.join(BASE, "s_1_1_en.html"))
    text_de = _load(os.path.join(BASE, "s_1_1_de.html"))
    client = StiebelEltronScrapingClient("dummy", None)

    res_en = client._extract_info_heatpump(text_en)
    res_de = client._extract_info_heatpump(text_de)

    assert TOTAL_HEAT_PRODUCED_KEY in res_en and res_en[TOTAL_HEAT_PRODUCED_KEY] is not None
    assert TOTAL_DHW_PRODUCED_KEY in res_en and res_en[TOTAL_DHW_PRODUCED_KEY] is not None

    assert TOTAL_HEAT_PRODUCED_KEY in res_de and res_de[TOTAL_HEAT_PRODUCED_KEY] is not None
    assert TOTAL_DHW_PRODUCED_KEY in res_de and res_de[TOTAL_DHW_PRODUCED_KEY] is not None


def test_s_1_8_contains_totals():
    text_en = _load(os.path.join(BASE, "s_1_8_en.html"))
    text_de = _load(os.path.join(BASE, "s_1_8_de.html"))
    client = StiebelEltronScrapingClient("dummy", None)

    res_en = client._extract_info_heatpump(text_en)
    res_de = client._extract_info_heatpump(text_de)

    assert TOTAL_HEAT_PRODUCED_KEY in res_en and res_en[TOTAL_HEAT_PRODUCED_KEY] is not None
    assert TOTAL_DHW_PRODUCED_KEY in res_en and res_en[TOTAL_DHW_PRODUCED_KEY] is not None

    assert TOTAL_HEAT_PRODUCED_KEY in res_de and res_de[TOTAL_HEAT_PRODUCED_KEY] is not None
    assert TOTAL_DHW_PRODUCED_KEY in res_de and res_de[TOTAL_DHW_PRODUCED_KEY] is not None


def test_s_2_7_contains_sw_version():
    # diagnosis_system extractor should provide sw_version for s_2_7 snapshots
    text_en = _load(os.path.join(BASE, "s_2_7_en.html"))
    text_de = _load(os.path.join(BASE, "s_2_7_de.html"))
    client = StiebelEltronScrapingClient("dummy", None)

    res_en = client._extract_diagnosis_system(text_en)
    res_de = client._extract_diagnosis_system(text_de)

    assert "sw_version" in res_en and res_en["sw_version"] is not None
    assert "sw_version" in res_de and res_de["sw_version"] is not None
