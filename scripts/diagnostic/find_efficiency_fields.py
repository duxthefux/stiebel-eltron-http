#!/usr/bin/env python3
"""Find efficiency fields in test data."""

from bs4 import BeautifulSoup
from pathlib import Path

test_dir = Path('scripts/testdata')

# Look for efficiency fields in s_1_8 page
for lang in ['de', 'en']:
    for page in ['s_1_8']:
        test_file = test_dir / f'{page}_{lang}.html'
        if not test_file.exists():
            print(f"{page}_{lang}: FILE NOT FOUND")
            continue
        
        print(f"\n{page}_{lang}.html:")
        soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
        
        # Find all keys
        for row in soup.find_all('tr'):
            key_td = row.find('td', class_='key')
            value_td = row.find('td', class_='value')
            
            if not key_td or not value_td:
                continue
            
            key_text = key_td.get_text(strip=True)
            value_text = value_td.get_text(strip=True)
            
            # Look for anything with months or efficiency-related
            if any(x in key_text.upper() for x in ['MONTH', 'MONAT', 'COP', 'JAZ', 'EFFICIENCY']):
                print(f"  {key_text}: {value_text}")
