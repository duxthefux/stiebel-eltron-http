#!/usr/bin/env python3
"""Extract s_1_8 field names from all languages."""

from pathlib import Path
from bs4 import BeautifulSoup

LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

# Get German fields as reference
print("="*80)
print("GERMAN (reference) - s_1_8 fields:")
print("="*80)

html = BeautifulSoup(Path('scripts/testdata/s_1_8_de.html').read_text(encoding='utf-8'), 'html.parser')
de_fields = {}
for table in html.find_all('table'):
    for row in table.find_all('tr'):
        tds = row.find_all('td')
        if len(tds) >= 2:
            fname = tds[0].get_text(strip=True)
            fval = tds[1].get_text(strip=True)
            de_fields[fname] = fval

for fname, fval in sorted(de_fields.items()):
    print(f"  {fname}: {fval}")

# Check a few key languages
for lang in ['nl', 'es', 'fr', 'sv', 'pl', 'cs', 'hu', 'fi']:
    print(f"\n{'='*80}")
    print(f"{lang.upper()} - s_1_8 fields:")
    print('='*80)
    
    html = BeautifulSoup(Path(f'scripts/testdata/s_1_8_{lang}.html').read_text(encoding='utf-8'), 'html.parser')
    fields = {}
    for table in html.find_all('table'):
        for row in table.find_all('tr'):
            tds = row.find_all('td')
            if len(tds) >= 2:
                fname = tds[0].get_text(strip=True)
                fval = tds[1].get_text(strip=True)
                fields[fname] = fval
    
    for fname, fval in sorted(fields.items()):
        print(f"  {fname}: {fval}")
