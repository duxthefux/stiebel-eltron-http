import os
import sys
sys.path.insert(0, os.getcwd())

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient
from custom_components.stiebel_eltron_http.const import DHW_TEMPERATURE_KEY

TESTDATA_DIR = os.path.join(os.path.dirname(__file__), "testdata")

for fname in ["s_1_0_en.html", "s_1_0_de.html"]:
    path = os.path.join(TESTDATA_DIR, fname)
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    client = StiebelEltronScrapingClient("dummy", None)
    res = client._extract_info_system(text)
    print(f"File: {fname}")
    print("Full result:", res)
    print(f"DHW key ('{DHW_TEMPERATURE_KEY}') value: {res.get(DHW_TEMPERATURE_KEY)!r}")
    print("Type:", type(res.get(DHW_TEMPERATURE_KEY)))
    print("-")
