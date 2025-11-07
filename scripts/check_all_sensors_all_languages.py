#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify all expected sensors are extracted with non-None values from all testdata files for all languages."""

import sys
import os
from pathlib import Path
from collections import defaultdict

# Set UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.test_scraper_localization import _load_module_from_path

def _load_modules():
    root = Path(__file__).resolve().parent.parent / "custom_components" / "stiebel_eltron_http"
    const_mod = sys.modules.get("custom_components.stiebel_eltron_http.const")
    if const_mod is None:
        const_mod = _load_module_from_path("custom_components.stiebel_eltron_http.const", root / "const.py")
    
    mapping_mod = sys.modules.get("custom_components.stiebel_eltron_http.mapping")
    if mapping_mod is None:
        mapping_mod = _load_module_from_path("custom_components.stiebel_eltron_http.mapping", root / "mapping.py")
    
    parsing_mod = sys.modules.get("custom_components.stiebel_eltron_http.parsing")
    if parsing_mod is None:
        parsing_mod = _load_module_from_path("custom_components.stiebel_eltron_http.parsing", root / "parsing.py")
    
    scraper_mod = sys.modules.get("custom_components.stiebel_eltron_http.scraper")
    if scraper_mod is None:
        scraper_mod = _load_module_from_path("custom_components.stiebel_eltron_http.scraper", root / "scraper.py")
    
    return const_mod, scraper_mod

const_mod, scraper_mod = _load_modules()

TESTDATA_DIR = Path(__file__).parent / "testdata"

# Languages to check
LANGUAGES = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]

# Page types and their corresponding extractors
EXTRACTORS = {
    "s_0_0": ("start_page", lambda client, html: client._extract_start_page(html)),
    "s_1_0": ("info_system", lambda client, html: client._extract_info_system(html)),
    "s_1_1": ("info_heatpump", lambda client, html: client._extract_info_heatpump(html)),
    "s_1_8": ("info_energy", lambda client, html: client._extract_info_energy(html)),
    "s_2_7": ("diagnosis_system", lambda client, html: client._extract_diagnosis_system(html)),
    "s_5_0": ("profile_network", lambda client, html: client._extract_profile_network(html)),
}

def check_file(page_type: str, lang: str, extractor_func) -> dict:
    """Check what sensors are extracted from a file."""
    file_path = TESTDATA_DIR / f"{page_type}_{lang}.html"
    
    if not file_path.exists():
        return {"status": "MISSING_FILE", "data": {}}
    
    html = file_path.read_text(encoding="utf-8")
    client = scraper_mod.StiebelEltronScrapingClient(host="test", session=None)
    
    try:
        data = extractor_func(client, html)
    except Exception as e:
        return {"status": "ERROR", "data": {}, "error": str(e)}
    
    # Check for None values
    none_values = []
    for key, val in data.items():
        if val is None:
            none_values.append(key)
    
    if none_values:
        return {"status": "NONE_VALUES", "data": data, "none_keys": none_values}
    
    return {"status": "OK", "data": data}

# Collect all data for each page type across languages
print("=" * 120)
print("COMPREHENSIVE SENSOR CHECK - ALL LANGUAGES AND PAGE TYPES")
print("=" * 120)

all_ok = True
issues = []
page_keys = defaultdict(lambda: defaultdict(set))
total_sensors = 0

for page_type, (name, extractor) in EXTRACTORS.items():
    print(f"\n{page_type} ({name}):")
    print("-" * 120)
    
    for lang in LANGUAGES:
        result = check_file(page_type, lang, extractor)
        
        if result["status"] == "OK":
            sensor_count = len(result["data"])
            total_sensors += sensor_count
            print(f"  {lang}: OK - {sensor_count:2d} sensors extracted successfully")
            
            # Collect keys for this page type
            for key in result["data"].keys():
                page_keys[page_type][key].add(lang)
                
        elif result["status"] == "MISSING_FILE":
            print(f"  {lang}: WARN - File not found")
            issues.append(f"{page_type}_{lang}: File not found")
            all_ok = False
            
        elif result["status"] == "NONE_VALUES":
            sensor_count = len(result["data"])
            none_count = len(result["none_keys"])
            print(f"  {lang}: FAIL - {sensor_count} sensors but {none_count} are None: {', '.join(result['none_keys'])}")
            for key in result["none_keys"]:
                issues.append(f"{page_type}_{lang}: {key} is None")
            all_ok = False
            
            # Still collect non-None keys
            for key, val in result["data"].items():
                if val is not None:
                    page_keys[page_type][key].add(lang)
                    
        elif result["status"] == "ERROR":
            print(f"  {lang}: ERROR - {result['error']}")
            issues.append(f"{page_type}_{lang}: {result['error']}")
            all_ok = False
        else:
            print(f"  {lang}: UNKNOWN - {result['status']}")
            all_ok = False

# Summary: Show sensor coverage statistics
print("\n" + "=" * 120)
print("SENSOR COVERAGE SUMMARY")
print("=" * 120)

for page_type in sorted(EXTRACTORS.keys()):
    if page_type not in page_keys or not page_keys[page_type]:
        continue
        
    print(f"\n{page_type}:")
    all_sensors = sorted(page_keys[page_type].keys())
    
    # Count how many sensors have full coverage vs partial
    full_coverage = 0
    partial_coverage = 0
    
    for sensor in all_sensors:
        langs_with_sensor = page_keys[page_type][sensor]
        missing_langs = set(LANGUAGES) - langs_with_sensor
        
        if not missing_langs:
            full_coverage += 1
        else:
            partial_coverage += 1
            print(f"  WARN: {sensor}: Missing in {len(missing_langs)} lang(s): {', '.join(sorted(missing_langs))}")
            for lang in sorted(missing_langs):
                issues.append(f"{page_type}_{lang}: Missing sensor {sensor}")
    
    print(f"  Summary: {full_coverage} sensors with full coverage, {partial_coverage} with partial coverage")

# Final summary
print("\n" + "=" * 120)
print("FINAL SUMMARY")
print("=" * 120)
print(f"Total sensors extracted: {total_sensors}")
print(f"Total issues found: {len(issues)}")

if all_ok and not issues:
    print("\n*** SUCCESS: All sensors extracted with valid (non-None) values across all languages! ***")
    sys.exit(0)
else:
    print(f"\n*** ISSUES FOUND: {len(issues)} problems detected ***")
    if issues:
        print("\nTop 30 issues:")
        for issue in sorted(set(issues))[:30]:
            print(f"  - {issue}")
        if len(issues) > 30:
            print(f"  ... and {len(set(issues)) - 30} more unique issues")
    sys.exit(1)
