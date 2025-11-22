#!/usr/bin/env python3
"""
Extract ALL missing translations from s_1_1 (runtime) and s_2_7 (diagnostic) pages.
Uses position-based extraction for reliability.
"""

import sys
import bs4
from pathlib import Path
from collections import defaultdict

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

# Section keywords
RUNTIME_KEYWORDS = ['LAUFZEIT', 'RUNTIME', 'DURÉE', 'DUREE', 'LOOPTIJD', 'TEMPO', 
                    'DRIFTTID', 'TIEMPO', 'CZAS', 'DOBA', 'ÜZEM', 'UZEM',
                    'KÄYTTÖ', 'KAYTTO', 'DRIFT', 'DURATA', 'FUNZ', 'MÛKÖDÉSI', 'MUKODESI',
                    'KÄYNTIAIKA', 'KAYNN']

STARTS_KEYWORDS = ['STARTS', 'DÉMARR', 'DEMARR', 'INSCHAK', 'AVVIAM', 'AVVII', 'STARTER',
                   'ARRANQ', 'URUCHOM', 'START', 'INDÍTÁ', 'INDITA', 'KÄYNN', 'KAYNN']

def find_section_table(soup, keywords):
    """Find a table with a header matching any of the keywords."""
    tables = soup.find_all('table')
    for table in tables:
        th = table.find('th')
        if th:
            header_text = th.get_text().upper()
            if any(kw.upper() in header_text for kw in keywords):
                return table
    return None

def get_field_by_index(table, index):
    """Get the field name at a specific index in the table."""
    if not table:
        return None
    rows = table.find_all('tr')
    field_index = 0
    for row in rows:
        key_cell = row.find('td', class_='key')
        if key_cell:
            if field_index == index:
                return key_cell.get_text(strip=True)
            field_index += 1
    return None

results = defaultdict(dict)

# ===== Extract from s_1_1 (Runtime counters and starts) =====
print("Extracting from s_1_1 pages (Runtime counters & starts)...")
print("=" * 70)

runtime_positions = {
    0: 'RUNTIME_COMPRESSOR_HEATING',
    1: 'RUNTIME_COMPRESSOR_DHW',
    2: 'RUNTIME_COMPRESSOR_DEFROST',
    3: 'RUNTIME_SUPPLEMENTARY_HEATER_1',
    4: 'RUNTIME_SUPPLEMENTARY_HEATER_2',
    5: 'RUNTIME_SUPPLEMENTARY_HEATER_TOTAL',
    6: 'DEFROST_TIME',
    7: 'DEFROST_STARTS',
}

starts_positions = {
    0: 'COMPRESSOR_STARTS',
}

for lang in LANGUAGES:
    html_file = Path(f'scripts/testdata/s_1_1_{lang}.html')
    if not html_file.exists():
        print(f"⚠️  Missing: s_1_1_{lang}.html")
        continue
    
    text = html_file.read_text(encoding='utf-8')
    soup = bs4.BeautifulSoup(text, 'html.parser')
    
    # Extract from RUNTIME section
    runtime_table = find_section_table(soup, RUNTIME_KEYWORDS)
    if runtime_table:
        for index, canonical_key in runtime_positions.items():
            field_name = get_field_by_index(runtime_table, index)
            if field_name:
                results[canonical_key][lang] = field_name
    else:
        print(f"  ⚠️  {lang}: RUNTIME section not found")
    
    # Extract from STARTS section
    starts_table = find_section_table(soup, STARTS_KEYWORDS)
    if starts_table:
        for index, canonical_key in starts_positions.items():
            field_name = get_field_by_index(starts_table, index)
            if field_name:
                results[canonical_key][lang] = field_name
    else:
        print(f"  ⚠️  {lang}: STARTS section not found")

# Print results
print("\n" + "=" * 70)
print("EXTRACTION RESULTS - s_1_1 Fields")
print("=" * 70)

for canonical_key in sorted(results.keys()):
    translations = results[canonical_key]
    missing_count = 12 - len(translations)
    
    print(f"\n{canonical_key}: {len(translations)}/12 languages found")
    if missing_count > 0:
        missing_langs = [lang for lang in LANGUAGES if lang not in translations]
        print(f"  ❌ MISSING: {', '.join(missing_langs)}")
    
    for lang in LANGUAGES:
        if lang in translations:
            print(f"  {lang}: \"{translations[lang]}\"")
    
    # Format for HEADER_ALIASES
    if translations:
        print(f"\n  # For HEADER_ALIASES:")
        print(f"  CanonicalKey.{canonical_key}: [")
        for lang in LANGUAGES:
            if lang in translations:
                print(f"      \"{translations[lang]}\",  # {lang}")
        print(f"  ],")

print("\n" + "=" * 70)
print(f"Extraction complete. Found {len(results)} fields.")
print(f"\nTotal translations: {sum(len(t) for t in results.values())}")
expected = len(results) * 12
print(f"Expected: {expected}")
print(f"Missing: {expected - sum(len(t) for t in results.values())}")
