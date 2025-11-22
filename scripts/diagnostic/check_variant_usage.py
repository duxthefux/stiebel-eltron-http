"""Check if any 'variant' entries in mapping.py are actually used by test data."""

from pathlib import Path
from bs4 import BeautifulSoup
import re
from collections import defaultdict

# Extract all variants from mapping.py
mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
content = mapping_file.read_text(encoding='utf-8')

# Find all variant entries
variant_pattern = r'"(.+?)",\s*#\s*variant'
variants = re.findall(variant_pattern, content)
print(f"Total variant entries: {len(variants)}")
print(f"Unique variant strings: {len(set(variants))}")

# Extract all fields from all test HTML files
testdata_dir = Path("scripts/testdata")
all_test_fields = set()

for html_file in testdata_dir.glob("*.html"):
    soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), 'html.parser')
    rows = soup.find_all('tr')
    for row in rows:
        key_cell = row.find('td', class_='key')
        if key_cell:
            field_name = key_cell.get_text(strip=True)
            if field_name:
                all_test_fields.add(field_name)

print(f"\nTotal unique fields in test data: {len(all_test_fields)}")

# Check which variants actually appear in test data
variants_in_test = []
variants_not_in_test = []

for variant in set(variants):
    if variant in all_test_fields:
        variants_in_test.append(variant)
    else:
        variants_not_in_test.append(variant)

print(f"\nVariants that ARE in test data: {len(variants_in_test)}")
if variants_in_test:
    print("These should be properly tagged with their language!")
    for v in sorted(variants_in_test)[:10]:
        print(f"  - {v}")
    if len(variants_in_test) > 10:
        print(f"  ... and {len(variants_in_test) - 10} more")

print(f"\nVariants that are NOT in test data: {len(variants_not_in_test)}")
print("These are truly alternative phrasings not in current test set")

# Check if removing variants would break anything
print(f"\n{'='*60}")
print("RECOMMENDATION:")
print(f"{'='*60}")

if variants_in_test:
    print(f"⚠️  {len(variants_in_test)} variants ARE in test data - script missed them!")
    print("   These need proper language tags.")
else:
    print("✅ No variants appear in test data - they're all truly alternatives")

print(f"\nYou have {len(variants_not_in_test)} alternative phrasings.")
print("These could be:")
print("  1. From older/newer firmware versions")
print("  2. Different hardware models")
print("  3. Regional variations within same language")
print("  4. Typos/errors in original mapping")
print("\nIf you want to clean up the mapping:")
print("  - KEEP variants if they're known to exist on real devices")
print("  - REMOVE variants if they were just guesses/typos")
