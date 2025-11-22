#!/usr/bin/env python3
"""Find the missing field names in test data."""

from bs4 import BeautifulSoup
from pathlib import Path

# Missing keys we need to find
missing_keys = [
    "actual_temperature_hk1",
    "target_temperature_hk1",
    "runtime_supplementary_heater_1",
    "runtime_supplementary_heater_2",
]

# Search patterns for each key
search_patterns = {
    "actual_temperature_hk1": ["HK1", "RAUM", "IST", "ACTUAL", "ROOM"],
    "target_temperature_hk1": ["HK1", "SOLL", "TARGET", "SETPOINT"],
    "runtime_supplementary_heater_1": ["ZUSATZ", "SUPPLEMENTARY", "ZWE1", "HEATER 1", "STUFE 1"],
    "runtime_supplementary_heater_2": ["ZUSATZ", "SUPPLEMENTARY", "ZWE2", "HEATER 2", "STUFE 2"],
}

test_dir = Path('scripts/testdata')

print("Searching for missing fields in all test files...\n")

for page in ['s_1_0', 's_1_1']:
    print(f"\n{'='*80}")
    print(f"PAGE: {page}")
    print('='*80)
    
    for lang in ['de', 'en', 'fr']:
        test_file = test_dir / f'{page}_{lang}.html'
        if not test_file.exists():
            continue
            
        soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
        rows = soup.find_all('tr')
        
        print(f"\n{lang.upper()}:")
        
        for key in missing_keys:
            patterns = search_patterns[key]
            found = False
            
            for row in rows:
                key_td = row.find('td', class_='key')
                value_td = row.find('td', class_='value')
                
                if not key_td or not value_td:
                    continue
                
                row_text = row.get_text()
                key_text = key_td.get_text(strip=True)
                value_text = value_td.get_text(strip=True)
                
                # Check if any pattern matches
                if any(pattern in row_text.upper() for pattern in patterns):
                    print(f"  {key}: '{key_text}' = {value_text}")
                    found = True
            
            if not found:
                print(f"  {key}: NOT FOUND")
