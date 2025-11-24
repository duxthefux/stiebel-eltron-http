#!/usr/bin/env python3
"""Complete extraction report for English testdata."""

import importlib.util
import sys
from pathlib import Path


def _load_module_from_path(module_name: str, path: Path):
    if module_name in sys.modules:
        return sys.modules[module_name]
    
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    parent = module_name.rpartition(".")[0]
    module.__package__ = parent
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def check_all_english():
    """Check all English testdata files using the actual scraper."""
    testdata_dir = Path("scripts/testdata")
    
    # Load modules
    root = Path("custom_components/stiebel_eltron_http")
    const_mod = _load_module_from_path("custom_components.stiebel_eltron_http.const", root / "const.py")
    scraper_mod = _load_module_from_path("custom_components.stiebel_eltron_http.scraper", root / "scraper.py")
    
    # Create scraper instance
    client = scraper_mod.StiebelEltronScrapingClient(host="local.test", session=None, language='en')
    
    print("\n" + "="*70)
    print("ENGLISH TESTDATA EXTRACTION REPORT")
    print("="*70)
    
    all_keys = set()
    file_results = {}
    
    # Check each page type
    pages = [
        ("s_0_0_en.html", "_extract_start_page", "START PAGE"),
        ("s_1_0_en.html", "_extract_info_system", "INFO > SYSTEM"),
        ("s_1_1_en.html", "_extract_info_heatpump", "INFO > HEAT PUMP"),
        ("s_1_8_en.html", "_extract_info_energy", "INFO > ENERGY"),
        ("s_2_7_en.html", "_extract_diagnosis_system", "DIAGNOSIS > SYSTEM"),
        ("s_5_0_en.html", "_extract_profile_network", "PROFILE > NETWORK"),
    ]
    
    for filename, method_name, page_name in pages:
        html_path = testdata_dir / filename
        if not html_path.exists():
            print(f"\n{page_name}: FILE NOT FOUND")
            continue
        
        html = html_path.read_text(encoding='utf-8')
        method = getattr(client, method_name, None)
        
        if not method:
            print(f"\n{page_name}: METHOD {method_name} NOT FOUND")
            continue
        
        try:
            data = method(html)
            file_results[filename] = data
            all_keys.update(data.keys())
            
            print(f"\n{page_name} ({filename})")
            print("-" * 70)
            if data:
                print(f"Extracted {len(data)} values:\n")
                for key, value in sorted(data.items()):
                    print(f"  {key:45s} = {value}")
            else:
                print("  No values extracted")
                
        except Exception as e:
            print(f"\n{page_name}: ERROR - {e}")
    
    print("\n" + "="*70)
    print(f"SUMMARY: {len(all_keys)} unique keys extracted across all English files")
    print("="*70)
    
    print("\nAll extracted keys:")
    for key in sorted(all_keys):
        print(f"  - {key}")
    
    print("\n" + "="*70)
    print("COVERAGE BY FILE:")
    print("="*70)
    for filename, data in file_results.items():
        print(f"  {filename:20s} : {len(data):2d} values")
    
    total_values = sum(len(data) for data in file_results.values())
    print(f"\n  TOTAL: {total_values} values extracted")
    print("="*70)


if __name__ == "__main__":
    check_all_english()
