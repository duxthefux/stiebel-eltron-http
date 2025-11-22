#!/usr/bin/env python3
"""List all fields in English testdata files."""

from pathlib import Path
from bs4 import BeautifulSoup


def list_all_fields():
    """List all fields with values in each English testdata file."""
    testdata_dir = Path("scripts/testdata")
    
    files = [
        "s_0_0_en.html",
        "s_1_0_en.html",
        "s_1_1_en.html",
        "s_1_8_en.html",
        "s_2_7_en.html",
        "s_5_0_en.html",
    ]
    
    for filename in files:
        html_path = testdata_dir / filename
        if not html_path.exists():
            continue
        
        html = html_path.read_text(encoding='utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        
        print(f"\n{'='*70}")
        print(f"{filename}")
        print(f"{'='*70}\n")
        
        rows = soup.find_all('tr')
        for row in rows:
            key_cell = row.find('td', class_='key')
            value_cell = row.find('td', class_='value')
            
            if key_cell and value_cell:
                key = key_cell.get_text(strip=True)
                value = value_cell.get_text(strip=True)
                
                if value and value not in ['---', '']:
                    print(f"{key:50s} = {value}")


if __name__ == "__main__":
    list_all_fields()
