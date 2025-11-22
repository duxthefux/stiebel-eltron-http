#!/usr/bin/env python3
"""Extract supplementary heater 1 and 2 runtime fields from all languages."""

from bs4 import BeautifulSoup
from pathlib import Path

test_dir = Path('scripts/testdata')
languages = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

print("RUNTIME_SUPPLEMENTARY_HEATER_1 (NHZ 1 / Heater 1):")
for lang in languages:
    test_file = test_dir / f's_1_1_{lang}.html'
    if not test_file.exists():
        print(f"  {lang}: FILE NOT FOUND")
        continue
    
    soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
    
    found = False
    for row in soup.find_all('tr'):
        key_td = row.find('td', class_='key')
        if not key_td:
            continue
        
        key_text = key_td.get_text(strip=True)
        
        # Look for heater 1 patterns (not containing "2" or "/" or "SUMME"/"TOTAL"/"SUM")
        if any(p in key_text.upper() for p in ['NHZ 1', 'HEATER 1', 'CHAUFF. APPOINT 1', 'BIJVERWARMER 1', 
                                                  'RISCALD. INTEGR. 1', 'TILLSKOTTSVÄRME 1', 'CALEFACCIÓN ADIC. 1',
                                                  'OGRZEW. DODATKOWE 1', 'PŘÍDAVNÉ TOPENÍ 1', 'KIEGÉSZÍTŐ FŰTÉS 1',
                                                  'LISÄLÄMM. 1', 'TILSKUDSVARME 1']):
            if '2' not in key_text and '/' not in key_text and not any(x in key_text.upper() for x in ['SUMME', 'TOTAL', 'SUM']):
                print(f"  {lang}: '{key_text}'")
                found = True
                break
    
    if not found:
        print(f"  {lang}: NOT FOUND")

print("\nRUNTIME_SUPPLEMENTARY_HEATER_2 (NHZ 2 / Heater 2):")
for lang in languages:
    test_file = test_dir / f's_1_1_{lang}.html'
    if not test_file.exists():
        print(f"  {lang}: FILE NOT FOUND")
        continue
    
    soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
    
    found = False
    for row in soup.find_all('tr'):
        key_td = row.find('td', class_='key')
        if not key_td:
            continue
        
        key_text = key_td.get_text(strip=True)
        
        # Look for heater 2 patterns (containing "2" but not "/" or "SUMME"/"TOTAL"/"SUM")
        if '2' in key_text and '/' not in key_text:
            if any(p in key_text.upper() for p in ['NHZ', 'HEATER', 'CHAUFF', 'BIJVERWARMER', 'RISCALD', 
                                                     'TILLSKOTT', 'CALEFAC', 'OGRZEW', 'PŘÍDAV', 'KIEGÉSZÍT',
                                                     'LISÄLÄMM', 'TILSKUD']):
                if not any(x in key_text.upper() for x in ['SUMME', 'TOTAL', 'SUM']):
                    print(f"  {lang}: '{key_text}'")
                    found = True
                    break
    
    if not found:
        print(f"  {lang}: NOT FOUND")
