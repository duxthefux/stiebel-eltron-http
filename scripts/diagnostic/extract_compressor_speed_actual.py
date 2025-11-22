#!/usr/bin/env python3
"""Extract actual compressor speed field from all languages."""

from bs4 import BeautifulSoup
from pathlib import Path

test_dir = Path('scripts/testdata')
languages = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

print("COMPRESSOR_SPEED_ACTUAL:")
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
        
        # Look for compressor speed actual patterns
        upper = key_text.upper()
        if any(p in upper for p in ['DREHZAHL', 'SPEED', 'VITESSE', 'TOERENTAL', 'GIRI', 'VARVTAL', 'VEL.', 'OBROTY', 'OTACKY', 'FORDSZ', 'KÄYNTINOP', 'OMDREJ']):
            if any(p in upper for p in ['IST', 'ACTUAL', 'REELLE', 'ACTUEEL', 'EFF', 'AKT', 'REAL', 'RZECZ', 'SKUT', 'TÉNYL', 'TOD', 'FAK']):
                if any(p in upper for p in ['VERDICHT', 'COMPRESS', 'COMP']):
                    print(f"  {lang}: '{key_text}'")
                    found = True
                    break
    
    if not found:
        print(f"  {lang}: NOT FOUND")
