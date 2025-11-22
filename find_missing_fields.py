#!/usr/bin/env python3
"""Find all fields in English testdata that might not be extracted."""

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


def find_missing_fields():
    """Find all fields in testdata that are not being extracted."""
    testdata_dir = Path("scripts/testdata")
    
    # Load modules
    root = Path("custom_components/stiebel_eltron_http")
    const_mod = _load_module_from_path("custom_components.stiebel_eltron_http.const", root / "const.py")
    scraper_mod = _load_module_from_path("custom_components.stiebel_eltron_http.scraper", root / "scraper.py")
    
    # Create scraper instance
    client = scraper_mod.StiebelEltronScrapingClient(host="local.test", session=None, language='en')
    
    print("\n" + "="*70)
    print("FINDING MISSING FIELDS IN ENGLISH TESTDATA")
    print("="*70)
    
    # Check each page type
    pages = [
        ("s_0_0_en.html", "_extract_start_page", "START PAGE"),
        ("s_1_0_en.html", "_extract_info_system", "INFO > SYSTEM"),
        ("s_1_1_en.html", "_extract_info_heatpump", "INFO > HEAT PUMP"),
        ("s_1_8_en.html", "_extract_info_energy", "INFO > ENERGY"),
        ("s_2_7_en.html", "_extract_diagnosis_system", "DIAGNOSIS > SYSTEM"),
        ("s_5_0_en.html", "_extract_profile_network", "PROFILE > NETWORK"),
    ]
    
    all_missing = []
    
    for filename, method_name, page_name in pages:
        html_path = testdata_dir / filename
        if not html_path.exists():
            continue
        
        html = html_path.read_text(encoding='utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        
        # Get extracted values
        method = getattr(client, method_name, None)
        extracted_data = method(html) if method else {}
        extracted_values = set()
        
        # Collect all extracted values (case-insensitive)
        for value in extracted_data.values():
            if isinstance(value, str):
                extracted_values.add(value.lower())
            elif isinstance(value, (int, float)):
                extracted_values.add(str(value))
        
        # Find all fields in HTML
        all_fields = []
        
        # Check all table rows
        rows = soup.find_all('tr')
        for row in rows:
            key_cell = row.find('td', class_='key')
            value_cell = row.find('td', class_='value')
            
            if key_cell and value_cell:
                key = key_cell.get_text(strip=True)
                value = value_cell.get_text(strip=True)
                
                # Skip empty or placeholder values
                if value and value not in ['---', 'n/a', 'N/A', '']:
                    all_fields.append((key, value))
        
        # Also check for fields in tables without the key/value class structure
        tables = soup.find_all('table')
        for table in tables:
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    # Check if this looks like a key-value pair
                    key_text = cells[0].get_text(strip=True)
                    value_text = cells[1].get_text(strip=True)
                    
                    # Skip if already found or if it's a header
                    if value_text and value_text not in ['---', 'n/a', 'N/A', '']:
                        # Check if value matches any extracted value
                        is_extracted = False
                        for extracted_val in extracted_data.values():
                            if isinstance(extracted_val, str):
                                if extracted_val.lower() in value_text.lower() or value_text.lower() in extracted_val.lower():
                                    is_extracted = True
                                    break
                            elif isinstance(extracted_val, (int, float)):
                                # Check if number appears in value
                                if str(extracted_val) in value_text or value_text.replace(',', '.').replace('°C', '').replace('%', '').replace('kWh', '').replace('MWh', '').strip() == str(extracted_val):
                                    is_extracted = True
                                    break
                        
                        if not is_extracted and (key_text, value_text) not in all_fields:
                            all_fields.append((key_text, value_text))
        
        # Find potentially missing fields
        missing = []
        for key, value in all_fields:
            # Check if this value appears in extracted data
            is_extracted = False
            
            for extracted_val in extracted_data.values():
                if isinstance(extracted_val, str):
                    # String comparison (case-insensitive)
                    if extracted_val.lower() in value.lower() or value.lower() in extracted_val.lower():
                        is_extracted = True
                        break
                elif isinstance(extracted_val, (int, float)):
                    # Numeric comparison - check if number appears in value
                    clean_value = value.replace(',', '.').replace('°C', '').replace('%', '').replace('kWh', '').replace('MWh', '').replace('bar', '').replace('l/min', '').replace('V', '').replace('A', '').strip()
                    try:
                        if abs(float(clean_value) - extracted_val) < 0.01:
                            is_extracted = True
                            break
                    except (ValueError, TypeError):
                        pass
            
            if not is_extracted:
                missing.append((key, value))
        
        if missing:
            print(f"\n{page_name} ({filename})")
            print("-" * 70)
            print(f"Extracted: {len(extracted_data)} values")
            print(f"Found in HTML: {len(all_fields)} fields")
            print(f"Potentially missing: {len(missing)} fields\n")
            
            for key, value in missing:
                print(f"  {key:45s} = {value}")
                all_missing.append((page_name, key, value))
    
    print("\n" + "="*70)
    print(f"SUMMARY: {len(all_missing)} potentially missing fields across all pages")
    print("="*70)
    
    return all_missing


if __name__ == "__main__":
    missing = find_missing_fields()
