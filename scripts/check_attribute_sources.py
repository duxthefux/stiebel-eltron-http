"""Check which extractor (_extract_info_system, _extract_info_heatpump, _extract_diagnosis_system,
_extract_profile_network) returns which keys for each test HTML file.

Run from the repository root with: python scripts/check_attribute_sources.py
"""
import glob
import os
import sys
from pprint import pprint

# Ensure repository root is on sys.path so we can import the package modules
sys.path.insert(0, os.getcwd())

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient

TESTDATA_DIR = os.path.join(os.path.dirname(__file__), "testdata")

client = StiebelEltronScrapingClient("dummy", None)

all_files = sorted(glob.glob(os.path.join(TESTDATA_DIR, "*.html")))

# Collect mapping: file -> {extractor: keys}
report = {}
# Also collect key -> set of (file, extractor)
key_map = {}

for f in all_files:
    name = os.path.basename(f)
    with open(f, "r", encoding="utf-8") as fh:
        text = fh.read()

    sys_res = client._extract_info_system(text)
    hp_res = client._extract_info_heatpump(text)
    diag_res = client._extract_diagnosis_system(text)
    prof_res = client._extract_profile_network(text)

    entry = {
        "info_system": sorted(sys_res.keys()),
        "info_heatpump": sorted(hp_res.keys()),
        "diagnosis_system": sorted(diag_res.keys()),
        "profile_network": sorted(prof_res.keys()),
    }
    report[name] = entry

    for extractor, keys in entry.items():
        for k in keys:
            key_map.setdefault(k, set()).add((name, extractor))

# Print per-file report (compact)
print("Per-file extractor -> keys summary:\n")
for fname, data in report.items():
    print(f"File: {fname}")
    for extractor, keys in data.items():
        print(f"  {extractor}: {len(keys)} keys")
    print()

print("Detailed file mappings (key lists):\n")
for fname, data in report.items():
    print(f"File: {fname}")
    for extractor, keys in data.items():
        if keys:
            print(f"  {extractor}: {keys}")
    print()

print("Aggregate key -> (file, extractor) mappings:\n")
for k in sorted(key_map.keys()):
    print(f"{k}: {sorted(key_map[k])}")

# Exit with a helpful count
print(f"\nChecked {len(all_files)} files; found {len(key_map)} distinct keys extracted by any extractor.")
