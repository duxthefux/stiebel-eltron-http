#!/usr/bin/env python3
"""Analyze all testdata pages to see what canonical keys are extracted."""

import sys
import os
from pathlib import Path
from collections import defaultdict
import importlib.util
import types

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Add current directory to path
sys.path.insert(0, os.getcwd())

# Create lightweight package modules to avoid Home Assistant dependencies
sys.modules.setdefault("custom_components", types.ModuleType("custom_components"))
sys.modules.setdefault(
    "custom_components.stiebel_eltron_http",
    types.ModuleType("custom_components.stiebel_eltron_http"),
)

# Load const.py
PACKAGE_DIR = Path("custom_components")
HEATPUMP_DIR = PACKAGE_DIR / "stiebel_eltron_http"

const_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.const", str(HEATPUMP_DIR / "const.py")
)
const_mod = importlib.util.module_from_spec(const_spec)
const_spec.loader.exec_module(const_mod)
sys.modules["custom_components.stiebel_eltron_http.const"] = const_mod

# Load mapping.py
mapping_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.mapping", str(HEATPUMP_DIR / "mapping.py")
)
mapping_mod = importlib.util.module_from_spec(mapping_spec)
mapping_spec.loader.exec_module(mapping_mod)
sys.modules["custom_components.stiebel_eltron_http.mapping"] = mapping_mod

# Load dedupe.py
dedupe_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.dedupe", str(HEATPUMP_DIR / "dedupe.py")
)
dedupe_mod = importlib.util.module_from_spec(dedupe_spec)
dedupe_spec.loader.exec_module(dedupe_mod)
sys.modules["custom_components.stiebel_eltron_http.dedupe"] = dedupe_mod

# Load parsing.py
parsing_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.parsing", str(HEATPUMP_DIR / "parsing.py")
)
parsing_mod = importlib.util.module_from_spec(parsing_spec)
parsing_spec.loader.exec_module(parsing_mod)
sys.modules["custom_components.stiebel_eltron_http.parsing"] = parsing_mod

# Load scraper.py
scraper_spec = importlib.util.spec_from_file_location(
    "custom_components.stiebel_eltron_http.scraper", str(HEATPUMP_DIR / "scraper.py")
)
scraper_mod = importlib.util.module_from_spec(scraper_spec)
scraper_spec.loader.exec_module(scraper_mod)
sys.modules["custom_components.stiebel_eltron_http.scraper"] = scraper_mod

StiebelEltronScrapingClient = scraper_mod.StiebelEltronScrapingClient

LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']
PAGE_TYPES = ['s_0_0', 's_1_0', 's_1_1', 's_1_8', 's_2_7', 's_5_0']

def main():
    testdata_dir = Path("scripts/testdata")
    
    # Track which keys appear on which pages
    page_keys = defaultdict(set)
    key_languages = defaultdict(lambda: defaultdict(set))  # key -> page -> languages
    
    client = StiebelEltronScrapingClient("dummy", None)
    
    extractors = [
        ("info_system", client._extract_info_system),
        ("info_heatpump", client._extract_info_heatpump),
        ("diagnosis_system", client._extract_diagnosis_system),
        ("profile_network", client._extract_profile_network),
    ]
    
    for page_type in PAGE_TYPES:
        for lang in LANGUAGES:
            html_file = testdata_dir / f'{page_type}_{lang}.html'
            if not html_file.exists():
                continue
            
            html_content = html_file.read_text(encoding='utf-8')
            
            # Run all extractors
            for name, func in extractors:
                result = func(html_content)
                if not result:
                    continue
                
                for key in result.keys():
                    page_keys[page_type].add(key)
                    key_languages[key][page_type].add(lang)
    
    print("=" * 80)
    print("CANONICAL KEYS EXTRACTED BY PAGE TYPE")
    print("=" * 80)
    print()
    
    for page_type in sorted(PAGE_TYPES):
        keys = sorted(page_keys[page_type])
        print(f"{page_type}: {len(keys)} unique keys")
        for key in keys:
            lang_count = len(key_languages[key][page_type])
            status = "✅" if lang_count == 12 else f"⚠️ {lang_count}/12"
            print(f"  {status} {key}")
        print()
    
    print("=" * 80)
    print("KEYS WITH INCOMPLETE LANGUAGE COVERAGE")
    print("=" * 80)
    print()
    
    incomplete = []
    for key in sorted(key_languages.keys()):
        for page_type in PAGE_TYPES:
            if page_type in key_languages[key]:
                lang_count = len(key_languages[key][page_type])
                if lang_count < 12:
                    missing_langs = set(LANGUAGES) - key_languages[key][page_type]
                    incomplete.append((key, page_type, lang_count, sorted(missing_langs)))
    
    if incomplete:
        for key, page, count, missing in sorted(incomplete):
            print(f"{key} on {page}: {count}/12 languages")
            print(f"  Missing: {', '.join(missing)}")
    else:
        print("✅ All keys have complete 12-language coverage!")
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    total_keys = len(key_languages)
    complete_keys = sum(1 for k in key_languages if all(len(langs) == 12 for langs in key_languages[k].values()))
    print(f"Total unique keys across all pages: {total_keys}")
    print(f"Keys with complete 12-language coverage: {complete_keys}/{total_keys}")

if __name__ == '__main__':
    main()
