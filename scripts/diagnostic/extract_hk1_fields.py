#!/usr/bin/env python3
"""Extract HK1 temperature fields from all languages."""

from bs4 import BeautifulSoup
from pathlib import Path

test_dir = Path('scripts/testdata')
languages = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

print("ACTUAL_TEMPERATURE_HK1:")
for lang in languages:
    test_file = test_dir / f's_1_0_{lang}.html'
    if not test_file.exists():
        print(f"  {lang}: FILE NOT FOUND")
        continue
    
    soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
    
    # Find the field - look for "ACTUAL" and "HK" together
    found = False
    for row in soup.find_all('tr'):
        key_td = row.find('td', class_='key')
        if not key_td:
            continue
        
        key_text = key_td.get_text(strip=True)
        
        # Look for actual/ist + HK1 pattern
        if 'HK' in key_text.upper() and ('ACTUAL' in key_text.upper() or 'IST' in key_text.upper()):
            if 'TEMPERATURE' in key_text.upper() or 'TEMPERATUR' in key_text.upper() or 'TEMPÉRATURE' in key_text.upper():
                print(f"  {lang}: '{key_text}'")
                found = True
                break
    
    if not found:
        print(f"  {lang}: NOT FOUND")

print("\nTARGET_TEMPERATURE_HK1:")
for lang in languages:
    test_file = test_dir / f's_1_0_{lang}.html'
    if not test_file.exists():
        print(f"  {lang}: FILE NOT FOUND")
        continue
    
    soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
    
    # Find the field - look for "SET/TARGET/SOLL" and "HK" together
    found = False
    for row in soup.find_all('tr'):
        key_td = row.find('td', class_='key')
        if not key_td:
            continue
        
        key_text = key_td.get_text(strip=True)
        
        # Look for target/soll/set + HK1 pattern
        if 'HK' in key_text.upper() and ('TARGET' in key_text.upper() or 'SOLL' in key_text.upper() or 'SET ' in key_text.upper() or 'SETPOINT' in key_text.upper() or 'CONSIGNE' in key_text.upper()):
            if 'TEMPERATURE' in key_text.upper() or 'TEMPERATUR' in key_text.upper() or 'TEMPÉRATURE' in key_text.upper():
                print(f"  {lang}: '{key_text}'")
                found = True
                break
    
    if not found:
        print(f"  {lang}: NOT FOUND")
