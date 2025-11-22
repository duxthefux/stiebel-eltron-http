#!/usr/bin/env python3
"""Extract HK1/CC1 temperature fields from all languages with better search."""

from bs4 import BeautifulSoup
from pathlib import Path

test_dir = Path('scripts/testdata')
languages = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

def find_hk1_actual(soup):
    """Find actual temperature HK1/CC1 field."""
    for row in soup.find_all('tr'):
        key_td = row.find('td', class_='key')
        if not key_td:
            continue
        
        key_text = key_td.get_text(strip=True)
        upper = key_text.upper()
        
        # Look for: (ACTUAL|IST|REELLE) + (HK|CC) + 1 + TEMP
        if ('HK' in upper or 'CC' in upper) and '1' in key_text:
            if any(word in upper for word in ['ACTUAL', 'IST', 'REELLE', 'AKTUELL', 'ATTUALE', 'SKUTEČNÁ', 'TÉNYLEGES', 'TODELLINEN']):
                if 'TEMP' in upper:
                    return key_text
    return None

def find_hk1_target(soup):
    """Find target/set temperature HK1/CC1 field."""
    for row in soup.find_all('tr'):
        key_td = row.find('td', class_='key')
        if not key_td:
            continue
        
        key_text = key_td.get_text(strip=True)
        upper = key_text.upper()
        
        # Look for: (TARGET|SET|SOLL|CONSIGNE) + (HK|CC) + 1 + TEMP
        if ('HK' in upper or 'CC' in upper) and '1' in key_text:
            if any(word in upper for word in ['TARGET', 'SET', 'SOLL', 'CONSIGNE', 'INGESTELD', 'IMPOSTATA', 'MÅLVÄRDE', 'ESTABLECIDA', 'ZADANÁ', 'BEÁLLÍTOTT', 'ASETETTU']):
                if 'TEMP' in upper:
                    return key_text
    return None

print("ACTUAL_TEMPERATURE_HK1:")
for lang in languages:
    test_file = test_dir / f's_1_0_{lang}.html'
    if not test_file.exists():
        print(f"  {lang}: FILE NOT FOUND")
        continue
    
    soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
    field = find_hk1_actual(soup)
    
    if field:
        print(f"  {lang}: '{field}'")
    else:
        print(f"  {lang}: NOT FOUND")

print("\nTARGET_TEMPERATURE_HK1:")
for lang in languages:
    test_file = test_dir / f's_1_0_{lang}.html'
    if not test_file.exists():
        print(f"  {lang}: FILE NOT FOUND")
        continue
    
    soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
    field = find_hk1_target(soup)
    
    if field:
        print(f"  {lang}: '{field}'")
    else:
        print(f"  {lang}: NOT FOUND")
