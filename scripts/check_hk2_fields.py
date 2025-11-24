#!/usr/bin/env python3
"""Check HK 2 fields in testdata."""

from pathlib import Path
from bs4 import BeautifulSoup

html_path = Path('scripts/testdata/s_1_0_en.html')
html = html_path.read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')

print("\n=== HK 2 (Heating Circuit 2) Fields in s_1_0_en.html ===\n")

rows = soup.find_all('tr')
for row in rows:
    key_cell = row.find('td', class_='key')
    value_cell = row.find('td', class_='value')
    
    if key_cell and value_cell and 'HK 2' in key_cell.get_text():
        key = key_cell.get_text(strip=True)
        value = value_cell.get_text(strip=True)
        print(f"{key:40s} = {value}")

# Check all languages
print("\n=== HK 2 Fields Across All Languages ===\n")
testdata_dir = Path('scripts/testdata')

for html_file in sorted(testdata_dir.glob('s_1_0_*.html')):
    lang = html_file.stem.split('_')[-1]
    html = html_file.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    hk2_fields = []
    rows = soup.find_all('tr')
    for row in rows:
        key_cell = row.find('td', class_='key')
        if key_cell and 'HK 2' in key_cell.get_text():
            hk2_fields.append(key_cell.get_text(strip=True))
    
    if hk2_fields:
        print(f"\n{lang.upper()}:")
        for field in hk2_fields:
            print(f"  - {field}")
