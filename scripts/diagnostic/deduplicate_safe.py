"""Deduplicate mapping entries safely - keep only ONE entry per language from test data.

For fields that appear in multiple languages with the same text (like "NHZ 1"),
keep ONE instance but list ALL languages it belongs to.
"""

from pathlib import Path
from bs4 import BeautifulSoup
import ast
from collections import defaultdict

LANGUAGES = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]

# Extract test fields
def extract_test_fields():
    testdata_dir = Path("scripts/testdata")
    fields_by_lang = defaultdict(set)
    
    for lang in LANGUAGES:
        for page in ["s_1_0", "s_1_1", "s_2_7"]:
            file_path = testdata_dir / f"{page}_{lang}.html"
            if file_path.exists():
                soup = BeautifulSoup(file_path.read_text(encoding='utf-8'), 'html.parser')
                for row in soup.find_all('tr'):
                    key_cell = row.find('td', class_='key')
                    if key_cell:
                        field_name = key_cell.get_text(strip=True)
                        if field_name:
                            fields_by_lang[lang].add(field_name)
    
    # Create reverse map: field -> list of languages
    field_to_langs = defaultdict(list)
    for lang, fields in fields_by_lang.items():
        for field in fields:
            field_to_langs[field].append(lang)
    
    return fields_by_lang, field_to_langs

print("Extracting test data...")
fields_by_lang, field_to_langs = extract_test_fields()

for lang in LANGUAGES:
    print(f"  {lang}: {len(fields_by_lang[lang])} fields")

# Read mapping.py and manually deduplicate
mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
content = mapping_file.read_text(encoding='utf-8')

# Split into lines for manual processing
lines = content.split('\n')
output_lines = []

in_header_aliases = False
current_canonical_key = None
seen_fields_per_key = {}  # canonical_key -> set of field texts seen
current_block_lines = []
entries_removed = 0
entries_kept = 0

i = 0
while i < len(lines):
    line = lines[i]
    
    # Detect start of HEADER_ALIASES
    if 'HEADER_ALIASES: dict[CanonicalKey, list[str]] = {' in line:
        in_header_aliases = True
        output_lines.append(line)
        i += 1
        continue
    
    # Detect end of HEADER_ALIASES
    if in_header_aliases and line.strip() == '}':
        in_header_aliases = False
        output_lines.append(line)
        i += 1
        continue
    
    # Outside HEADER_ALIASES, just copy
    if not in_header_aliases:
        output_lines.append(line)
        i += 1
        continue
    
    # Inside HEADER_ALIASES - detect CanonicalKey lines
    if 'CanonicalKey.' in line and ': [' in line:
        # Extract key name
        import re
        match = re.search(r'CanonicalKey\.(\w+)', line)
        if match:
            current_canonical_key = match.group(1)
            seen_fields_per_key[current_canonical_key] = set()
            output_lines.append(line)
            i += 1
            
            # Now process entries until we hit '],
            while i < len(lines):
                entry_line = lines[i]
                
                # Check if it's the closing bracket
                if entry_line.strip() == '],':
                    output_lines.append(entry_line)
                    i += 1
                    break
                
                # Check if it's a field entry
                entry_match = re.match(r'^(\s+)"(.+?)"', entry_line)
                if entry_match:
                    indent = entry_match.group(1)
                    field_text = entry_match.group(2)
                    
                    # Check if we've already seen this exact field for this key
                    if field_text in seen_fields_per_key[current_canonical_key]:
                        entries_removed += 1
                        i += 1
                        continue
                    
                    # Check if this field exists in test data
                    if field_text in field_to_langs:
                        # Keep it
                        output_lines.append(entry_line)
                        seen_fields_per_key[current_canonical_key].add(field_text)
                        entries_kept += 1
                    else:
                        # Not in test data - remove it
                        entries_removed += 1
                    
                    i += 1
                else:
                    # Not a field entry, keep as-is
                    output_lines.append(entry_line)
                    i += 1
        else:
            output_lines.append(line)
            i += 1
    else:
        output_lines.append(line)
        i += 1

# Write back
new_content = '\n'.join(output_lines)
mapping_file.write_text(new_content, encoding='utf-8')

print(f"\n✅ Deduplication complete!")
print(f"   Entries kept: {entries_kept}")
print(f"   Entries removed: {entries_removed}")
print(f"   Output has {len(output_lines)} lines (was {len(lines)})")
