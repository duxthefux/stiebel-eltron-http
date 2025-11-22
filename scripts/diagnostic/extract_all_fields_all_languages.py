#!/usr/bin/env python3
"""Extract ALL field names from ALL test files to verify correct language mapping."""

from bs4 import BeautifulSoup
from pathlib import Path
import json

test_dir = Path('scripts/testdata')
languages = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

# Fields to extract from each page
fields_by_page = {
    's_1_0': [
        'COMPRESSOR_SPEED_ACTUAL',
        'COMPRESSOR_SPEED_TARGET',
    ],
    's_1_1': [
        'COMPRESSOR_SPEED_ACTUAL',
        'COMPRESSOR_SPEED_TARGET',
        'RUNTIME_COMPRESSOR_HEATING',
        'RUNTIME_COMPRESSOR_DHW',
        'RUNTIME_COMPRESSOR_DEFROST',
    ],
}

# Extract all keys from each language
all_data = {}
for lang in languages:
    all_data[lang] = {}
    for page in ['s_1_0', 's_1_1', 's_2_7']:
        test_file = test_dir / f'{page}_{lang}.html'
        if not test_file.exists():
            continue
        
        soup = BeautifulSoup(test_file.read_text(encoding='utf-8'), 'html.parser')
        keys = []
        for row in soup.find_all('tr'):
            key_td = row.find('td', class_='key')
            if key_td:
                keys.append(key_td.get_text(strip=True))
        
        all_data[lang][page] = keys

# Print all keys from each page for comparison
for page in ['s_1_1']:
    print(f"\n{'='*80}")
    print(f"PAGE: {page}")
    print('='*80)
    
    # Get max number of keys
    max_keys = max(len(all_data[lang].get(page, [])) for lang in languages)
    
    # Print keys side by side
    for i in range(min(50, max_keys)):  # First 50 keys
        print(f"\nRow {i}:")
        for lang in languages:
            keys = all_data[lang].get(page, [])
            if i < len(keys):
                print(f"  {lang}: {keys[i]}")
            else:
                print(f"  {lang}: (no data)")
