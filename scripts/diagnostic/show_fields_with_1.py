#!/usr/bin/env python3
"""Show all fields containing '1' from each language."""

from bs4 import BeautifulSoup
from pathlib import Path

test_dir = Path('scripts/testdata')

for lang in ['nl', 'it', 'sv', 'es', 'cs', 'hu', 'fi', 'da']:
    print(f'\n{lang.upper()}:')
    test_file = test_dir / f's_1_0_{lang}.html'
    if not test_file.exists():
        print('  FILE NOT FOUND')
        continue
    
    soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
    keys = [row.find('td', class_='key').get_text(strip=True) 
            for row in soup.find_all('tr') 
            if row.find('td', class_='key')]
    
    for k in keys:
        if '1' in k:
            print(f'  {k}')
