#!/usr/bin/env python3
"""Check s_1_8_en.html table details."""

from pathlib import Path
from bs4 import BeautifulSoup

html_path = Path('scripts/testdata/s_1_8_en.html')
html = html_path.read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')

tables = soup.find_all('table')
print(f"\nFound {len(tables)} tables in s_1_8_en.html\n")

for idx, table in enumerate(tables, start=1):
    rows = table.find_all('tr')
    if not rows:
        print(f"Table {idx}: No rows")
        continue
    
    headers = rows[0].find_all(['th'])
    header_texts = [h.get_text(strip=True) for h in headers]
    
    print(f"Table {idx}: {header_texts[0] if header_texts else 'No header'}")
    print(f"  Headers: {header_texts}")
    print(f"  Rows: {len(rows)}")
    
    # Show first few data rows
    for row_idx, row in enumerate(rows[:5], start=1):
        cells = row.find_all(['td', 'th'])
        cell_texts = [c.get_text(strip=True) for c in cells]
        print(f"    Row {row_idx}: {cell_texts}")
    
    print()
