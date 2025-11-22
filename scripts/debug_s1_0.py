#!/usr/bin/env python3
"""Check s_1_0 field extraction in detail."""

import sys
import os
from pathlib import Path
import importlib.util
import types

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Create lightweight package modules
sys.modules.setdefault("custom_components", types.ModuleType("custom_components"))
sys.modules.setdefault(
    "custom_components.stiebel_eltron_http",
    types.ModuleType("custom_components.stiebel_eltron_http"),
)

# Load modules
PACKAGE_DIR = Path("custom_components")
HEATPUMP_DIR = PACKAGE_DIR / "stiebel_eltron_http"

const_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.const", str(HEATPUMP_DIR / "const.py")
)
const_mod = importlib.util.module_from_spec(const_spec)
const_spec.loader.exec_module(const_mod)
sys.modules["custom_components.stiebel_eltron_http.const"] = const_mod

mapping_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.mapping", str(HEATPUMP_DIR / "mapping.py")
)
mapping_mod = importlib.util.module_from_spec(mapping_spec)
mapping_spec.loader.exec_module(mapping_mod)
sys.modules["custom_components.stiebel_eltron_http.mapping"] = mapping_mod

dedupe_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.dedupe", str(HEATPUMP_DIR / "dedupe.py")
)
dedupe_mod = importlib.util.module_from_spec(dedupe_spec)
dedupe_spec.loader.exec_module(dedupe_mod)
sys.modules["custom_components.stiebel_eltron_http.dedupe"] = dedupe_mod

parsing_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.parsing", str(HEATPUMP_DIR / "parsing.py")
)
parsing_mod = importlib.util.module_from_spec(parsing_spec)
parsing_spec.loader.exec_module(parsing_mod)
sys.modules["custom_components.stiebel_eltron_http.parsing"] = parsing_mod

scraper_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.scraper", str(HEATPUMP_DIR / "scraper.py")
)
scraper_mod = importlib.util.module_from_spec(scraper_spec)
scraper_spec.loader.exec_module(scraper_mod)
sys.modules["custom_components.stiebel_eltron_http.scraper"] = scraper_mod

StiebelEltronScrapingClient = scraper_mod.StiebelEltronScrapingClient

LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

# s_1_0 fields that are showing as incomplete
fields_to_check = [
    'actual_temperature_hk1',
    'bivalence_temperature_dhw',
    'bivalence_temperature_heating',
    'buffer_actual_temperature',
    'target_temperature_hk1',
]

def main():
    testdata_dir = Path("scripts/testdata")
    client = StiebelEltronScrapingClient("dummy", None)
    
    print("=" * 80)
    print("CHECKING s_1_0 FIELD EXTRACTION BY LANGUAGE")
    print("=" * 80)
    print()
    
    for field in fields_to_check:
        print(f"\n{field}:")
        print("-" * 60)
        
        for lang in LANGUAGES:
            html_file = testdata_dir / f's_1_0_{lang}.html'
            if not html_file.exists():
                print(f"  {lang}: FILE NOT FOUND")
                continue
            
            html_content = html_file.read_text(encoding='utf-8')
            result = client._extract_info_system(html_content)
            
            if field in result:
                print(f"  {lang}: ✅ {result[field]}")
            else:
                print(f"  {lang}: ❌ NOT FOUND")
                # Try to see what fields ARE extracted
                print(f"       Extracted fields: {list(result.keys())}")

if __name__ == '__main__':
    main()
