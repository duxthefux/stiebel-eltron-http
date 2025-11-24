#!/usr/bin/env python3
"""Check Hungarian s_1_1 field names."""

from pathlib import Path
from bs4 import BeautifulSoup

html_file = Path('scripts/testdata/s_1_1_hu.html')
html = html_file.read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')

tables = soup.find_all('table', class_='info')
print(f'Found {len(tables)} sections in s_1_1_hu.html\n')

for table_idx, table in enumerate(tables[:2]):  # First 2 sections
    header = table.find('th', class_='round-top')
    section_name = header.get_text(strip=True) if header else '(no header)'
    print(f"Section {table_idx}: {section_name}")
    
    rows = table.find_all('tr')
    field_count = 0
    for row in rows:
        key_cell = row.find('td', class_='key')
        if key_cell:
            field_name = key_cell.get_text(strip=True)
            print(f"  [{field_count}] {field_name}")
            field_count += 1
            if field_count >= 12:  # Limit output
                print(f"  ... ({field_count} total fields)")
                break
    print()
