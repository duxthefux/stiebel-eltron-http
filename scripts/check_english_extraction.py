#!/usr/bin/env python3
"""Check what values are extracted from English testdata files."""

import importlib.util
import sys
from pathlib import Path
from bs4 import BeautifulSoup


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


def check_extraction():
    """Check English testdata extraction."""
    testdata_dir = Path("scripts/testdata")
    english_files = sorted(testdata_dir.glob("*_en.html"))
    
    # Load the parsing module
    root = Path("custom_components/stiebel_eltron_http")
    parsing = _load_module_from_path("custom_components.stiebel_eltron_http.parsing", root / "parsing.py")
    
    print(f"\n=== Checking {len(english_files)} English testdata files ===\n")
    
    all_extracted_keys = set()
    file_results = {}
    
    for file_path in english_files:
        print(f"\n{'='*60}")
        print(f"File: {file_path.name}")
        print(f"{'='*60}")
        
        html_content = file_path.read_text(encoding='utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all("table")
        print(f"\nFound {len(tables)} tables")
        
        file_data = {}
        
        for idx, table in enumerate(tables, start=1):
            rows = table.find_all("tr")
            if not rows:
                continue
                
            headers = rows[0].find_all(["th"])
            header_texts = [h.get_text(strip=True) for h in headers]
            section_title = header_texts[0] if header_texts else ""
            
            print(f"\n  Table {idx}: '{section_title}'")
            
            # Try different parsing methods
            try:
                data = parsing.parse_process_data_table(table)
                if data:
                    print(f"    parse_process_data_table: {len(data)} values")
                    for k, v in data.items():
                        key_str = str(k)
                        file_data[key_str] = v
                        all_extracted_keys.add(key_str)
            except Exception:
                pass
            
            try:
                data = parsing.parse_efficiency_table(table)
                if data:
                    print(f"    parse_efficiency_table: {len(data)} values")
                    for k, v in data.items():
                        key_str = str(k)
                        file_data[key_str] = v
                        all_extracted_keys.add(key_str)
            except Exception:
                pass
                
            try:
                data = parsing.parse_amount_power_table(table)
                if data:
                    print(f"    parse_amount_power_table: {len(data)} values")
                    for k, v in data.items():
                        key_str = str(k)
                        file_data[key_str] = v
                        all_extracted_keys.add(key_str)
            except Exception:
                pass
        
        file_results[file_path.name] = file_data
        print(f"\n  Total extracted from {file_path.name}: {len(file_data)} values")
    
    print("\n" + "="*60)
    print(f"Summary: {len(all_extracted_keys)} unique keys extracted across all English files")
    print("="*60)
    
    # Show detailed breakdown
    for filename, data in sorted(file_results.items()):
        if data:
            print(f"\n{filename} ({len(data)} values):")
            for key, value in sorted(data.items()):
                print(f"  {key:45s} = {value}")
    
    print("\n" + "="*60)
    print("All unique extracted keys:")
    print("="*60)
    for key in sorted(all_extracted_keys):
        print(f"  - {key}")

if __name__ == "__main__":
    check_extraction()
