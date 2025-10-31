import os, sys
sys.path.insert(0, os.getcwd())
import importlib.util
import types

# create lightweight package modules
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

SCRAPER_PATH = os.path.join(os.getcwd(), "custom_components", "stiebel_eltron_http", "scraper.py")
spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.scraper", SCRAPER_PATH
)
scraper_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_mod)  # type: ignore
sys.modules["custom_components.stiebel_eltron_http.scraper"] = scraper_mod

from custom_components.stiebel_eltron_http.scraper import HEADER_ALIASES, _matches_alias, _normalize_text
from bs4 import BeautifulSoup

path = os.path.join("scripts", "testdata", "s_1_8_en.html")
with open(path, 'r', encoding='utf-8') as fh:
    html = fh.read()

soup = BeautifulSoup(html, 'html.parser')
tables = soup.find_all('table')
for t in tables:
    rows = t.find_all('tr')
    hdrs = rows[0].find_all(['th']) if rows else []
    section = hdrs[0].get_text(strip=True) if hdrs else ''
    if _matches_alias(section, HEADER_ALIASES.get('AMOUNT_OF_HEAT_SECTION', [])):
        for r in rows:
            elems = r.find_all(['td','th'])
            if not elems: continue
            texts = [e.get_text(strip=True) for e in elems]
            if len(texts) < 2: continue
            key_text = texts[0]
            print('\nRow key:', key_text)
            print(' normalized key:', repr(_normalize_text(key_text)))
            for cand in HEADER_ALIASES.get('VD_HEATING_DAY', []):
                print('  cand:', cand, ' normalized:', repr(_normalize_text(cand)))
                print('   match?', _matches_alias(key_text, [cand]))

