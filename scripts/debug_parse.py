from pathlib import Path
import importlib.util, sys
import types

ROOT = Path(__file__).resolve().parent.parent / "custom_components" / "stiebel_eltron_http"
TESTDATA = Path(__file__).resolve().parent / "testdata"


def load_module_from_path(name, path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

const = load_module_from_path("custom_components.stiebel_eltron_http.const", ROOT / "const.py")
# Provide minimal shims for runtime-only dependencies so we can import the scraper
# module in this standalone script without installing aiohttp or Home Assistant.
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

scraper = load_module_from_path("custom_components.stiebel_eltron_http.scraper", ROOT / "scraper.py")

client = scraper.StiebelEltronScrapingClient(host="local.test", session=None)

for fname in ["s_1_1_en.html", "s_1_1_de.html"]:
    p = TESTDATA / fname
    print('\n===', fname, '===')
    html = p.read_text(encoding='utf-8')
    data = client._extract_info_system(html)
    for k in sorted(data.keys()):
        print(f"{k}: {data[k]!r}")

print('\nLoaded HEADER_ALIASES keys:')
for k, v in scraper.HEADER_ALIASES.items():
    if k.startswith('INVERTER') or 'POWER' in k or 'FAN' in k or 'COMPRESSOR' in k:
        print(k, '->', v)
