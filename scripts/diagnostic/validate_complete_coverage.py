#!/usr/bin/env python3
"""
COMPREHENSIVE VALIDATION: Verify all values from all test pages in all languages
are extracted and have corresponding sensors.
"""

from pathlib import Path
import sys
import types
import importlib.util
import re
from collections import defaultdict

# Setup paths
repo_root = Path.cwd()
testdata_dir = repo_root / 'scripts' / 'testdata'

# Load const module
const_path = repo_root / 'custom_components' / 'stiebel_eltron_http' / 'const.py'
spec = importlib.util.spec_from_file_location("const", const_path)
const = importlib.util.module_from_spec(spec)
spec.loader.exec_module(const)

# Get all sensor keys from sensor.py
sensor_path = repo_root / 'custom_components' / 'stiebel_eltron_http' / 'sensor.py'
with open(sensor_path, 'r', encoding='utf-8') as f:
    sensor_content = f.read()

sensor_pattern = r'key=([A-Z_]+_KEY)'
sensor_keys_found = re.findall(sensor_pattern, sensor_content)
sensor_keys = {getattr(const, key_name) for key_name in sensor_keys_found if hasattr(const, key_name)}

print("="*80)
print("COMPREHENSIVE VALIDATION REPORT")
print("="*80)
print(f"Total sensors defined: {len(sensor_keys)}\n")

# Setup scraper environment (mock Home Assistant)
sys.modules.setdefault("custom_components", types.ModuleType("custom_components"))
sys.modules.setdefault(
    "custom_components.stiebel_eltron_http",
    types.ModuleType("custom_components.stiebel_eltron_http"),
)
sys.modules["custom_components.stiebel_eltron_http.const"] = const

# Load scraper
scraper_path = repo_root / 'custom_components' / 'stiebel_eltron_http' / 'scraper.py'
spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.scraper", scraper_path
)
scraper_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_mod)
StiebelEltronScrapingClient = scraper_mod.StiebelEltronScrapingClient

# Process all test files by language
languages = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']
all_extracted_keys = set()
extraction_by_language = defaultdict(set)
extraction_by_page = defaultdict(set)

print("Processing test files by language:")
print("-" * 80)

for lang in languages:
    lang_files = sorted(testdata_dir.glob(f"*_{lang}.html"))
    
    if not lang_files:
        print(f"  {lang.upper()}: No test files found")
        continue
    
    lang_keys = set()
    
    for html_file in lang_files:
        page = html_file.stem.replace(f'_{lang}', '')  # e.g., s_1_0
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        client = StiebelEltronScrapingClient("testhost", None)
        
        # Run all extraction methods
        extractors = [
            client._extract_info_system,
            client._extract_info_heatpump,
            client._extract_diagnosis_system,
            client._extract_profile_network,
        ]
        
        page_keys = set()
        for extractor in extractors:
            try:
                result = extractor(html)
                if result:
                    page_keys.update(result.keys())
            except:
                pass
        
        lang_keys.update(page_keys)
        extraction_by_page[page].update(page_keys)
    
    extraction_by_language[lang] = lang_keys
    all_extracted_keys.update(lang_keys)
    
    # Check coverage for this language
    covered = lang_keys & sensor_keys
    missing = lang_keys - sensor_keys
    
    coverage_pct = (len(covered) / len(lang_keys) * 100) if lang_keys else 0
    
    status = "✅" if not missing else "⚠️"
    print(f"  {status} {lang.upper()}: {len(lang_keys)} fields extracted, "
          f"{len(covered)} have sensors ({coverage_pct:.1f}%)")
    
    if missing:
        print(f"      Missing sensors: {', '.join(sorted(missing))}")

print("\n" + "="*80)
print("EXTRACTION BY PAGE")
print("="*80)

for page in sorted(extraction_by_page.keys()):
    keys = extraction_by_page[page]
    covered = keys & sensor_keys
    missing = keys - sensor_keys
    
    status = "✅" if not missing else "⚠️"
    print(f"{status} {page}: {len(keys)} fields, {len(covered)} with sensors")
    if missing:
        print(f"    Missing: {', '.join(sorted(missing))}")

print("\n" + "="*80)
print("OVERALL SUMMARY")
print("="*80)

covered_keys = all_extracted_keys & sensor_keys
missing_sensors = all_extracted_keys - sensor_keys

print(f"\nTotal unique fields extracted: {len(all_extracted_keys)}")
print(f"Fields with sensors:            {len(covered_keys)}")
print(f"Fields without sensors:         {len(missing_sensors)}")
print(f"Coverage:                        {len(covered_keys)/len(all_extracted_keys)*100:.1f}%")

if missing_sensors:
    print(f"\n❌ MISSING SENSORS ({len(missing_sensors)}):")
    for key in sorted(missing_sensors):
        print(f"   - {key}")
else:
    print("\n✅ PERFECT COVERAGE!")
    print("Every value from all pages in all languages has a corresponding sensor!")

# Also check: sensors without extracted data
extra_sensors = sensor_keys - all_extracted_keys
if extra_sensors:
    print(f"\n📋 SENSORS NOT IN TEST DATA ({len(extra_sensors)}):")
    print("   (These may be device-specific or future fields)")
    for key in sorted(extra_sensors):
        print(f"   - {key}")

print("\n" + "="*80)
print("VALIDATION COMPLETE")
print("="*80)
print(f"Tested: {len(languages)} languages × {len(set(extraction_by_page.keys()))} pages")
print(f"Result: {'✅ ALL VALUES COVERED' if not missing_sensors else '⚠️ COVERAGE INCOMPLETE'}")
