#!/usr/bin/env python3
"""Check actual field names in test data."""

from bs4 import BeautifulSoup
from pathlib import Path

TESTDATA_DIR = Path(__file__).parent / "testdata"

langs = ['cs', 'da', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'sv']

for lang in langs:
    print(f"\n{lang.upper()}:")
    
    # Check s_1_8 efficiency section
    s_1_8 = TESTDATA_DIR / f"s_1_8_{lang}.html"
    if s_1_8.exists():
        soup = BeautifulSoup(s_1_8.open(encoding='utf-8'), 'html.parser')
        tables = soup.find_all('table', class_='info')
        print(f"  s_1_8: {len(tables)} sections")
        
        # Get efficiency section (usually last table)
        if tables:
            efficiency_table = tables[-1]
            print(f"    Section: {efficiency_table.find('th').get_text(strip=True)}")
            keys = efficiency_table.find_all('td', class_='key')
            for key in keys[:2]:  # First 2 fields
                print(f"      {key.get_text(strip=True)}")
    
    # Check s_1_0 for dual mode
    s_1_0 = TESTDATA_DIR / f"s_1_0_{lang}.html"
    if s_1_0.exists():
        soup = BeautifulSoup(s_1_0.open(encoding='utf-8'), 'html.parser')
        tables = soup.find_all('table', class_='info')
        
        # Look for external section
        for table in tables:
            section_name = table.find('th').get_text(strip=True)
            if 'EXTERN' in section_name.upper() or 'EXTERIEUR' in section_name.upper():
                print(f"  s_1_0 external section: {section_name}")
                keys = table.find_all('td', class_='key')
                for key in keys:
                    text = key.get_text(strip=True)
                    if 'BIVAL' in text.upper():
                        print(f"      {text}")
                break
