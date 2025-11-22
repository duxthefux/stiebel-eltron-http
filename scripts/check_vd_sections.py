#!/usr/bin/env python3
"""Check which section contains VD fields."""

from pathlib import Path
from bs4 import BeautifulSoup

for lang in ['nl', 'fi', 'da']:
    print(f"\n{'='*80}")
    print(f"{lang.upper()}")
    print('='*80)
    
    html_path = Path(f'scripts/testdata/s_1_1_{lang}.html')
    html = BeautifulSoup(html_path.read_text(encoding='utf-8'), 'html.parser')
    
    tables = html.find_all('table')
    for i, table in enumerate(tables):
        # Get section header
        all_rows = table.find_all('tr')
        if all_rows:
            all_headers = all_rows[0].find_all(['th'])
            curr_headers = [header.get_text(strip=True) for header in all_headers]
            section_title = curr_headers[0] if curr_headers else ""
            
            # Check if this table has VD fields
            has_vd = False
            for row in all_rows[1:]:
                tds = row.find_all('td')
                if len(tds) >= 2:
                    field_name = tds[0].get_text(strip=True)
                    if 'VD' in field_name or ('VERWARMEN' in field_name and 'DAG' in field_name):
                        has_vd = True
                        print(f"\nTable {i}: Section '{section_title}'")
                        print(f"  Found: {field_name}")
                        break
