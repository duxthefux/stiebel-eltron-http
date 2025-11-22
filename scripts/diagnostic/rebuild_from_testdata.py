"""Rebuild HEADER_ALIASES from test data - extract fields in exact order from each language.

Since all pages have the same structure across languages, we:
1. Extract field names from each language's test files
2. Match them by position (row number)
3. Build mapping with exactly 12 entries per CanonicalKey
"""

from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import re

LANGUAGES = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]
PAGES = ["s_1_0", "s_1_1", "s_2_7"]

def extract_fields_by_position():
    """Extract fields maintaining their row position across all languages."""
    testdata_dir = Path("scripts/testdata")
    
    # Structure: page -> row_index -> lang -> field_name
    fields_by_page_and_row = defaultdict(lambda: defaultdict(dict))
    
    for page in PAGES:
        for lang in LANGUAGES:
            file_path = testdata_dir / f"{page}_{lang}.html"
            if not file_path.exists():
                print(f"⚠️  Missing: {file_path}")
                continue
            
            soup = BeautifulSoup(file_path.read_text(encoding='utf-8'), 'html.parser')
            rows = soup.find_all('tr')
            
            row_index = 0
            for row in rows:
                key_cell = row.find('td', class_='key')
                if key_cell:
                    field_name = key_cell.get_text(strip=True)
                    if field_name:
                        fields_by_page_and_row[page][row_index][lang] = field_name
                        row_index += 1
    
    return fields_by_page_and_row

def group_by_canonical_key(fields_by_page_and_row):
    """Group fields by their canonical key based on the German (de) field name."""
    # First, read current mapping to get CanonicalKey -> de field mappings
    mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
    content = mapping_file.read_text(encoding='utf-8')
    
    # Extract existing mappings to know which CanonicalKey each German field belongs to
    de_to_canonical = {}
    current_key = None
    
    for line in content.split('\n'):
        if 'CanonicalKey.' in line and ': [' in line:
            match = re.search(r'CanonicalKey\.(\w+)', line)
            if match:
                current_key = match.group(1)
        elif current_key and re.match(r'^\s+"(.+?)"', line):
            match = re.match(r'^\s+"(.+?)"', line)
            if match:
                field_text = match.group(1)
                # Assume first entry is German (or use heuristics)
                if field_text not in de_to_canonical:
                    de_to_canonical[field_text] = current_key
    
    # Now build canonical_key -> list of 12 language entries
    canonical_mappings = defaultdict(lambda: [None] * 12)
    
    for page in PAGES:
        for row_index, lang_fields in fields_by_page_and_row[page].items():
            # Get the German field name to determine CanonicalKey
            de_field = lang_fields.get('de')
            if not de_field:
                continue
            
            # Find which CanonicalKey this belongs to
            canonical_key = de_to_canonical.get(de_field)
            if not canonical_key:
                # Unknown field - skip or create new
                continue
            
            # Add all language versions
            for lang_idx, lang in enumerate(LANGUAGES):
                field_name = lang_fields.get(lang)
                if field_name and canonical_mappings[canonical_key][lang_idx] is None:
                    canonical_mappings[canonical_key][lang_idx] = field_name
    
    return canonical_mappings

print("Extracting fields from test data...")
fields_by_page_and_row = extract_fields_by_position()

print("Grouping by CanonicalKey...")
canonical_mappings = group_by_canonical_key(fields_by_page_and_row)

# Show summary
print(f"\nFound {len(canonical_mappings)} CanonicalKeys with mappings:")
for key, entries in sorted(canonical_mappings.items()):
    non_none = sum(1 for e in entries if e is not None)
    print(f"  {key}: {non_none}/12 languages")

# Now rebuild the HEADER_ALIASES section in mapping.py
print("\nRebuilding HEADER_ALIASES section...")

mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
content = mapping_file.read_text(encoding='utf-8')
lines = content.split('\n')

# Find HEADER_ALIASES section
start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if 'HEADER_ALIASES: dict[CanonicalKey, list[str]] = {' in line:
        start_idx = i
    elif start_idx is not None and line.strip() == '}':
        end_idx = i
        break

if start_idx is None or end_idx is None:
    print("❌ Could not find HEADER_ALIASES section!")
    exit(1)

# Build new HEADER_ALIASES section
new_section = [lines[start_idx]]

for canonical_key in sorted(canonical_mappings.keys()):
    entries = canonical_mappings[canonical_key]
    new_section.append(f"    CanonicalKey.{canonical_key}: [")
    
    for lang_idx, lang in enumerate(LANGUAGES):
        field_name = entries[lang_idx]
        if field_name:
            new_section.append(f'        "{field_name}",  # {lang}')
    
    new_section.append("    ],")

new_section.append("}")

# Replace old section with new
new_lines = lines[:start_idx] + new_section + lines[end_idx + 1:]

# Write back
new_content = '\n'.join(new_lines)
mapping_file.write_text(new_content, encoding='utf-8')

print(f"\n✅ Rebuilt HEADER_ALIASES!")
print(f"   Output has {len(new_lines)} lines (was {len(lines)})")
print(f"   Each CanonicalKey has entries from test data with language comments")
