#!/usr/bin/env python3
"""Check table headers in s_1_0 HTML files."""

from pathlib import Path
from bs4 import BeautifulSoup

for lang in ['de', 'fr', 'fi']:
    print(f"\n{'='*80}")
    print(f"=== {lang.upper()} ===")
    print('='*80)
    
    html_path = Path(f'scripts/testdata/s_1_0_{lang}.html')
    html = BeautifulSoup(html_path.read_text(encoding='utf-8'), 'html.parser')
    
    tables = html.find_all('table')
    print(f"Found {len(tables)} tables\n")
    
    for i, table in enumerate(tables):
        print(f"--- TABLE {i} ---")
        all_rows = table.find_all('tr')
        if all_rows:
            first_row = all_rows[0]
            all_headers = first_row.find_all(['th'])
            curr_headers = [header.get_text(strip=True) for header in all_headers]
            section_title = curr_headers[0] if curr_headers else ""
            
            print(f"Section title: '{section_title}'")
            
            # Show first few data rows
            for row_idx, row in enumerate(all_rows[1:4], start=1):
                tds = row.find_all('td')
                if len(tds) >= 2:
                    print(f"  Row {row_idx}: {tds[0].get_text(strip=True)[:40]}")
        print()
