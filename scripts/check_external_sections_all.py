#!/usr/bin/env python3
"""Extract external heat generator section from all s_1_0 test files."""

from pathlib import Path
from bs4 import BeautifulSoup

TESTDATA_DIR = Path("testdata")
LANGUAGES = ["cs", "da", "de", "en", "es", "fi", "fr", "hu", "it", "nl", "pl", "sv"]

# External section keywords in different languages
EXTERNAL_KEYWORDS = [
    "EXTERN", "EXTERNAL", "EXTERNO", "ESTERNO", "EXTÉRIEUR", 
    "EXTERNÉ", "ULKOINEN", "KÜLSŐ", "ZEWNĘTRZNY"
]

def extract_external_section(lang: str):
    """Extract external heat generator section for a language."""
    file_path = TESTDATA_DIR / f"s_1_0_{lang}.html"
    
    if not file_path.exists():
        return None
    
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    # Find all section headers
    headers = soup.find_all('th', class_='round-top')
    
    for header in headers:
        header_text = header.get_text(strip=True)
        
        # Check if this is the external heat generator section
        if any(keyword in header_text.upper() for keyword in EXTERNAL_KEYWORDS):
            print(f"\n{lang.upper()}: Section header = '{header_text}'")
            
            # Find the table containing this header
            table = header.find_parent('table')
            if table:
                # Extract all key-value pairs
                rows = table.find_all('tr')[1:]  # Skip header row
                
                for row in rows[:4]:  # First 4 fields
                    key_cell = row.find('td', class_='key')
                    value_cell = row.find('td', class_='value')
                    
                    if key_cell and value_cell:
                        key = key_cell.get_text(strip=True)
                        value = value_cell.get_text(strip=True)
                        print(f"  {key}: {value}")
            
            return True
    
    return False

print("Checking WÄRMEERZEUGER EXTERN / EXTERNAL HEAT GENERATOR section in all languages:")
print("=" * 80)

for lang in LANGUAGES:
    result = extract_external_section(lang)
    if not result:
        print(f"\n{lang.upper()}: NOT FOUND")

print("\n" + "=" * 80)
print("These are the fields we should extract:")
print("  1. ISTTEMPERATUR / ACTUAL TEMPERATURE -> external_actual_temperature")
print("  2. SOLLTEMPERATUR / SET TEMPERATURE -> external_set_temperature")
print("  3. BIVALENZTEMPERATUR HZG -> dual_mode_temp_hzg")
print("  4. BIVALENZTEMPERATUR WW / UNTERE EINSATZGRENZE -> dual_mode_temp_ww or lower_limit")
