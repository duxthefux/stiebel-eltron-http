import os, sys
sys.path.insert(0, os.getcwd())

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient, _matches_alias
from custom_components.stiebel_eltron_http.mapping import CanonicalKey, get_aliases
from bs4 import BeautifulSoup

for fname in ["s_1_8_en.html", "s_1_8_de.html"]:
    path = os.path.join("scripts", "testdata", fname)
    with open(path, "r", encoding="utf-8") as fh:
        html = fh.read()
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    print(f"\nFile: {fname} - found {len(tables)} tables")
    for i, t in enumerate(tables, start=1):
        rows = t.find_all("tr")
        hdrs = rows[0].find_all(["th"]) if rows else []
        section = hdrs[0].get_text(strip=True) if hdrs else ""
        print(f"Table {i} header: '{section}'")
        if _matches_alias(section, get_aliases(CanonicalKey.AMOUNT_OF_HEAT_SECTION)):
            print("  -> AMOUNT_OF_HEAT_SECTION matched")
            # print rows
            for r in rows:
                elems = r.find_all(["td", "th"])
                if not elems: continue
                texts = [e.get_text(strip=True) for e in elems]
                if len(texts) >= 2:
                    print("   row:", texts[0], "->", texts[1])
            client = StiebelEltronScrapingClient("dummy", None)
            total = client._extract_energy(t, CanonicalKey.VD_HEATING_TOTAL)
            day = client._extract_energy(t, CanonicalKey.VD_HEATING_DAY)
            dhw_total = client._extract_energy(t, CanonicalKey.VD_DHW_TOTAL)
            dhw_day = client._extract_energy(t, CanonicalKey.VD_DHW_DAY)
            print("  extracted total:", total)
            print("  extracted day:", day)
            print("  extracted dhw_total:", dhw_total)
            print("  extracted dhw_day:", dhw_day)
