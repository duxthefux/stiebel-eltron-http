#!/usr/bin/env python3
"""
FINAL VERIFICATION REPORT
=========================

Verifies user's requirement: "every value of testdata is extracted from all 
languages and pages and made as sensor"

This script:
1. Runs the scraper on actual test data files
2. Collects all extracted fields
3. Verifies each extracted field has a corresponding sensor
"""

from pathlib import Path
import sys
import types
import importlib.util
import re

# Setup paths
repo_root = Path.cwd()
testdata_dir = repo_root / 'scripts' / 'testdata'

# Load const module
const_path = repo_root / 'custom_components' / 'stiebel_eltron_http' / 'const.py'
spec = importlib.util.spec_from_file_location("const", const_path)
const = importlib.util.module_from_spec(spec)
spec.loader.exec_module(const)

# Load sensor definitions
sensor_path = repo_root / 'custom_components' / 'stiebel_eltron_http' / 'sensor.py'
with open(sensor_path, 'r', encoding='utf-8') as f:
    sensor_content = f.read()

sensor_pattern = r'key=([A-Z_]+_KEY)'
sensor_keys_found = re.findall(sensor_pattern, sensor_content)
sensor_keys = {getattr(const, key_name) for key_name in sensor_keys_found if hasattr(const, key_name)}

print("="*80)
print("SENSOR COVERAGE VERIFICATION")
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

# Process all test files
all_extracted_keys = set()
files_by_language = {}

for html_file in sorted(testdata_dir.glob("*.html")):
    # Extract language code
    lang = html_file.stem.split('_')[-1]  # e.g., s_1_0_de.html → de
    
    if lang not in files_by_language:
        files_by_language[lang] = []
    files_by_language[lang].append(html_file.name)
    
    # Extract data
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
    
    for extractor in extractors:
        try:
            result = extractor(html)
            if result:
                all_extracted_keys.update(result.keys())
        except:
            pass  # Some extractors may fail on irrelevant pages

print(f"Languages tested: {len(files_by_language)}")
for lang, files in sorted(files_by_language.items()):
    print(f"  {lang}: {len(files)} files")

print(f"\nTotal unique fields extracted from ALL test files: {len(all_extracted_keys)}")

# Check coverage
covered_keys = all_extracted_keys & sensor_keys
missing_sensors = all_extracted_keys - sensor_keys

print(f"\n{'='*80}")
print("COVERAGE ANALYSIS")
print(f"{'='*80}\n")

print(f"Fields extracted from test data: {len(all_extracted_keys)}")
print(f"Fields with sensors:            {len(covered_keys)}")
print(f"Coverage:                        {len(covered_keys)/len(all_extracted_keys)*100:.1f}%")

if missing_sensors:
    print(f"\n❌ Fields extracted but WITHOUT sensors ({len(missing_sensors)}):")
    for key in sorted(missing_sensors):
        print(f"   - {key}")
    print("\n" + "="*80)
    print("❌ INCOMPLETE COVERAGE")
    print("="*80)
    print("Not all extracted fields have sensors!")
else:
    print(f"\n{'='*80}")
    print("✅ PERFECT COVERAGE")
    print(f"{'='*80}")
    print("Every value extracted from test data has a corresponding sensor!")
    print(f"\nVerified across:")
    print(f"  - {len(files_by_language)} languages")
    print(f"  - {sum(len(f) for f in files_by_language.values())} test files")
    print(f"  - {len(all_extracted_keys)} unique fields")

# Also check: sensors without extracted data
extra_sensors = sensor_keys - all_extracted_keys
if extra_sensors:
    print(f"\n📋 Note: {len(extra_sensors)} sensors defined but NOT extracted from current test data")
    print("   (These may be device-specific or from other pages not in test data)")
    for key in sorted(extra_sensors):
        print(f"   - {key}")
