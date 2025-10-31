import os, sys
sys.path.insert(0, os.getcwd())
from bs4 import BeautifulSoup
from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient, _matches_alias
from custom_components.stiebel_eltron_http.mapping import CanonicalKey, get_aliases
from custom_components.stiebel_eltron_http.const import DHW_TEMPERATURE_KEY

path = os.path.join("scripts", "testdata", "s_1_0_de.html")
with open(path, "r", encoding="utf-8") as fh:
    html = fh.read()

soup = BeautifulSoup(html, "html.parser")
all_tables = soup.find_all("table")
client = StiebelEltronScrapingClient("dummy", None)

for idx, t in enumerate(all_tables, start=1):
    rows = t.find_all("tr")
    headers = rows[0].find_all(["th"]) if rows else []
    section = headers[0].get_text(strip=True) if headers else ""
    if _matches_alias(section, get_aliases(CanonicalKey.DHW_SECTION)):
        print("Found DHW table at index", idx, "header", section)
        val = client._extract_temperature(t, CanonicalKey.ACTUAL_TEMPERATURE)
        print("_extract_temperature returned:", val)
        break
else:
    print("No DHW table found")
