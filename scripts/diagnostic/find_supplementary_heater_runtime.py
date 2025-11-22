#!/usr/bin/env python3
"""Find RUNTIME_SUPPLEMENTARY_HEATER_TOTAL field in all languages."""

from bs4 import BeautifulSoup
from pathlib import Path

test_dir = Path('scripts/testdata')
languages = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

print("RUNTIME_SUPPLEMENTARY_HEATER_TOTAL:")
for lang in languages:
    test_file = test_dir / f's_1_1_{lang}.html'
    if not test_file.exists():
        print(f"  {lang}: FILE NOT FOUND")
        continue
    
    soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
    
    # Look for "NHZ" or supplementary heater runtime
    found = False
    for row in soup.find_all('tr'):
        key_td = row.find('td', class_='key')
        if not key_td:
            continue
        
        key_text = key_td.get_text(strip=True)
        
        # Look for NHZ, supplementary, additional heater patterns
        if any(x in key_text.upper() for x in ['NHZ 1/2', 'SUPPLEMENTARY', 'ADDITIONAL', 'ADDIZIONALE', 'TILLÄGG', 'ADICIONAL', 'DODATKOW', 'PŘÍDAV', 'KIEGÉSZÍTŐ', 'LISÄ', 'EKSTRA']):
            if any(x in key_text.upper() for x in ['BETRIEBSSTUNDEN', 'RUNTIME', 'OPERATING', 'HOURS', 'ORE', 'TIMER', 'HODINY', 'ÓRA', 'TUNTI']):
                print(f"  {lang}: '{key_text}'")
                found = True
                break
    
    if not found:
        # Try simpler search - just look for the runtime section with heater text
        for row in soup.find_all('tr'):
            key_td = row.find('td', class_='key')
            if not key_td:
                continue
            key_text = key_td.get_text(strip=True)
            if 'NHZ' in key_text or 'ZWE' in key_text:
                print(f"  {lang}: '{key_text}'")
                break
