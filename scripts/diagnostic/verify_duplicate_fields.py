#!/usr/bin/env python3
"""Verify if fields with duplicates are actually the same across languages."""

from bs4 import BeautifulSoup
from pathlib import Path

test_dir = Path('scripts/testdata')
languages = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

# Fields to check
fields_to_check = {
    'HP-ID': 's_2_7',
    'HP-TYPE': 's_2_7',
    'PARAMETERSET': 's_2_7',
}

for field_pattern, page in fields_to_check.items():
    print(f"\n{field_pattern}:")
    for lang in languages:
        test_file = test_dir / f'{page}_{lang}.html'
        if not test_file.exists():
            continue
        
        soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
        
        for row in soup.find_all('tr'):
            key_td = row.find('td', class_='key')
            if not key_td:
                continue
            
            key_text = key_td.get_text(strip=True)
            
            if field_pattern.replace('-', ' ').replace('-', '') in key_text.upper().replace('-', ' ').replace('-', ''):
                print(f"  {lang}: '{key_text}'")
                break
