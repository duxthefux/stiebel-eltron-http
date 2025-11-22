#!/usr/bin/env python3
"""Check actual field names in HTML files for missing languages."""

import bs4
from pathlib import Path

def find_section_table(soup, keywords):
    """Find a table with a header matching any of the keywords."""
    tables = soup.find_all('table')
    for table in tables:
        th = table.find('th')
        if th:
            header_text = th.get_text().upper()
            if any(kw in header_text for kw in keywords):
                return table
    return None

# Check what fields exist in languages we're missing
HEATING_KEYWORDS = ['HEIZUNG', 'HEATING', 'CHAUFFAGE', 'VERWARMING', 'RISCALDAMENTO', 
                    'UPPVÄRMNING', 'CALEFACCIÓN', 'OGRZEWANIE', 'TOPENI', 'FŰTÉS', 
                    'LÄMMITYS', 'OPVARMNING']

DHW_KEYWORDS = ['WARMWASSER', 'HOT WATER', 'EAU CHAUDE', 'WARMWATER', 'ACQUA CALDA',
                'VARMVATTEN', 'AGUA CALIENTE', 'CIEPŁA WODA', 'TEPLA VODA', 'MELEGVÍZ',
                'LÄMMIN VESI', 'VARMT VAND']

# First check Hungarian structure
lang = 'hu'
html_file = Path(f'scripts/testdata/s_1_0_{lang}.html')
text = html_file.read_text(encoding='utf-8')
soup = bs4.BeautifulSoup(text, 'html.parser')
tables = soup.find_all('table')

print(f"\n{'='*70}")
print(f"HU SECTION HEADERS:")
print('='*70)
for table in tables:
    th = table.find('th')
    if th:
        header = th.get_text(strip=True)
        print(f"\n{header}:")
        rows = table.find_all('tr')
        for i, row in enumerate(rows):
            key_cell = row.find('td', class_='key')
            if key_cell:
                key_text = key_cell.get_text(strip=True)
                print(f"  {i:2d}. {key_text}")
