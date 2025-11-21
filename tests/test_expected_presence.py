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

# Load i18n package components in the correct order
I18N_PATH = os.path.join(os.getcwd(), "custom_components", "stiebel_eltron_http", "i18n")

# 1. Load canonical_keys.py first (needed by all language files)
canonical_keys_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.i18n.canonical_keys", 
    os.path.join(I18N_PATH, "canonical_keys.py")
)
canonical_keys_mod = importlib.util.module_from_spec(canonical_keys_spec)
canonical_keys_spec.loader.exec_module(canonical_keys_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.i18n.canonical_keys"] = canonical_keys_mod

# 1b. Create a minimal i18n package module (needed for json_loader imports)
i18n_package_mod = types.ModuleType("custom_components.stiebel_eltron_http.i18n")
i18n_package_mod.__path__ = [I18N_PATH]  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.i18n"] = i18n_package_mod

# 1c. Load mapping.py early (needed by json_loader)
MAPPING_PATH = os.path.join(os.getcwd(), "custom_components", "stiebel_eltron_http", "mapping.py")
mapping_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.mapping", MAPPING_PATH
)
mapping_mod = importlib.util.module_from_spec(mapping_spec)
mapping_spec.loader.exec_module(mapping_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.mapping"] = mapping_mod

# 1d. Load json_loader.py (needed by language files)
json_loader_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.i18n.json_loader",
    os.path.join(I18N_PATH, "json_loader.py")
)
json_loader_mod = importlib.util.module_from_spec(json_loader_spec)
json_loader_spec.loader.exec_module(json_loader_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.i18n.json_loader"] = json_loader_mod

# 2. Load all language modules
for lang in ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]:
    lang_spec = importlib.util.spec_from_file_location(
        f"custom_components.stiebel_eltron_http.i18n.{lang}", 
        os.path.join(I18N_PATH, f"{lang}.py")
    )
    lang_mod = importlib.util.module_from_spec(lang_spec)
    lang_spec.loader.exec_module(lang_mod)  # type: ignore
    sys.modules[f"custom_components.stiebel_eltron_http.i18n.{lang}"] = lang_mod

# 3. Now load the i18n __init__.py properly
i18n_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.i18n", os.path.join(I18N_PATH, "__init__.py")
)
i18n_mod = importlib.util.module_from_spec(i18n_spec)
i18n_spec.loader.exec_module(i18n_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.i18n"] = i18n_mod

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
