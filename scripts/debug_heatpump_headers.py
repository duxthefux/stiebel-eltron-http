from pathlib import Path
import importlib.util, sys, types

ROOT = Path(__file__).resolve().parent.parent / "custom_components" / "stiebel_eltron_http"
TESTDATA_DIR = Path(__file__).resolve().parent / "testdata"
FILES = ["s_1_1_en.html", "s_1_1_de.html"]


def load_module_from_path(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

# shims
if "aiohttp" not in sys.modules:
    sys.modules["aiohttp"] = types.ModuleType("aiohttp")
if "async_timeout" not in sys.modules:
    sys.modules["async_timeout"] = types.ModuleType("async_timeout")
if "homeassistant.const" not in sys.modules:
    ha = types.ModuleType("homeassistant")
    ha_const = types.ModuleType("homeassistant.const")
    ha_const.ATTR_SW_VERSION = "sw_version"
    sys.modules["homeassistant"] = ha
    sys.modules["homeassistant.const"] = ha_const

const = load_module_from_path("custom_components.stiebel_eltron_http.const", ROOT / "const.py")
scraper = load_module_from_path("custom_components.stiebel_eltron_http.scraper", ROOT / "scraper.py")

from bs4 import BeautifulSoup

for fname in FILES:
    TESTDATA = TESTDATA_DIR / fname
    html = TESTDATA.read_text(encoding='utf-8')
    print('---- File:', TESTDATA)
    soup = BeautifulSoup(html, 'html.parser')
    all_tables = soup.find_all('table')
    print('Found', len(all_tables), 'tables')
    for i, t in enumerate(all_tables, 1):
        headers = t.find_all('th')
        header_texts = [h.get_text(strip=True) for h in headers]
        print(f'\nTable {i} headers: {header_texts}')
        section_title = header_texts[0] if header_texts else ''
        matches = {}
        for key in ['PROCESS_DATA_SECTION', 'AMOUNT_OF_HEAT_SECTION', 'POWER_CONSUMPTION_SECTION']:
            aliases = scraper.HEADER_ALIASES.get(key, [])
            matches[key] = scraper._matches_alias(section_title, aliases)
        print('Matches:', matches)

    print('\n--- Run scraper _extract_info_heatpump result keys:')
    client = scraper.StiebelEltronScrapingClient(host='local', session=None)
    data = client._extract_info_heatpump(html)
    print(sorted(data.items()))
