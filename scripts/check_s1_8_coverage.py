#!/usr/bin/env python3
"""Check what s_1_8 fields exist in all languages."""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from bs4 import BeautifulSoup
from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient

LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

print("="*80)
print("CHECKING s_1_8 FIELD AVAILABILITY")
print("="*80)

# First, check what German extracts (our baseline)
client = StiebelEltronScrapingClient("dummy", "dummy", "dummy")
html_path = Path('scripts/testdata/s_1_8_de.html')
html_content = html_path.read_text(encoding='utf-8')
result_de = client._extract_info_energy(html_content)

print(f"\nGerman (de) extracted {len(result_de)} fields:")
for key in sorted(result_de.keys()):
    print(f"  - {key}: {result_de[key]}")

# Now check each language
print(f"\n{'='*80}")
print("CHECKING EACH LANGUAGE")
print('='*80)

for lang in LANGUAGES:
    html_path = Path(f'scripts/testdata/s_1_8_{lang}.html')
    html_content = html_path.read_text(encoding='utf-8')
    result = client._extract_info_energy(html_content)
    
    missing = set(result_de.keys()) - set(result.keys())
    
    if missing:
        print(f"\n{lang.upper()}: {len(result)}/{len(result_de)} fields")
        print(f"  Missing: {', '.join(sorted(missing))}")
    else:
        print(f"{lang.upper()}: ✅ All {len(result_de)} fields")
