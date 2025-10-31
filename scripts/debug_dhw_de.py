import os, sys
sys.path.insert(0, os.getcwd())
from bs4 import BeautifulSoup
from custom_components.stiebel_eltron_http.scraper import _matches_alias, HEADER_ALIASES
from custom_components.stiebel_eltron_http.mapping import CanonicalKey

path = os.path.join("scripts", "testdata", "s_1_0_de.html")
with open(path, "r", encoding="utf-8") as fh:
    html = fh.read()

soup = BeautifulSoup(html, "html.parser")
all_tables = soup.find_all("table")
print(f"Found {len(all_tables)} tables")
for idx, t in enumerate(all_tables, start=1):
    rows = t.find_all("tr")
    headers = rows[0].find_all(["th"]) if rows else []
    section = headers[0].get_text(strip=True) if headers else ""
    print(f"Table {idx} header: '{section}'")
    # Check if this is DHW section
    dhw_section_aliases = HEADER_ALIASES.get(CanonicalKey.DHW_SECTION, [])
    print("DHW_SECTION aliases:", dhw_section_aliases)
    print("_matches_alias(section, DHW_SECTION_aliases)", _matches_alias(section, dhw_section_aliases))
    for r in rows:
        elems = r.find_all(["td","th"])
        if not elems:
            continue
        texts = [e.get_text(strip=True) for e in elems]
        if len(texts) < 2:
            continue
        key_text = texts[0]
        val_text = texts[1]
        print(f"  row key: '{key_text}' val: '{val_text}'")
    # Check matching against ACTUAL_TEMPERATURE
    act_aliases = HEADER_ALIASES.get(CanonicalKey.ACTUAL_TEMPERATURE, [])
    print("    ACTUAL_TEMPERATURE aliases:", act_aliases)
    print("    _matches_alias(key_text, ACTUAL_TEMPERATURE_aliases)", _matches_alias(key_text, act_aliases))
    print('---')
