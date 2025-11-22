#!/usr/bin/env python3
"""Debug French section matching."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from bs4 import BeautifulSoup

from custom_components.stiebel_eltron_http.mapping import CanonicalKey, get_aliases
from custom_components.stiebel_eltron_http import parsing

html_content = Path('scripts/testdata/s_1_0_fr.html').read_text(encoding='utf-8')
soup = BeautifulSoup(html_content, 'html.parser')

all_tables = soup.find_all('table')
print(f"Found {len(all_tables)} tables\n")

for table_index, curr_table in enumerate(all_tables):
    all_rows = curr_table.find_all('tr')
    all_headers = all_rows[0].find_all(['th'])
    
    curr_headers = [header.get_text(strip=True) for header in all_headers]
    section_title = curr_headers[0] if curr_headers else ""
    
    print(f"=== TABLE {table_index} ===")
    print(f"Section title: '{section_title}'")
    
    # Check if it matches ELECTRIC_REHEATING_SECTION
    aliases = get_aliases(CanonicalKey.ELECTRIC_REHEATING_SECTION)
    print(f"ELECTRIC_REHEATING_SECTION aliases: {aliases}")
    
    matches = parsing._matches_alias(section_title, aliases)
    print(f"Matches ELECTRIC_REHEATING_SECTION: {matches}")
    
    # Show some data rows
    for row in all_rows[1:4]:
        tds = row.find_all('td')
        if len(tds) >= 2:
            print(f"  {tds[0].get_text(strip=True)}")
    
    print()
