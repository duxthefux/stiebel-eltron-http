"""Deduplicate mapping entries - keep only ONE entry per language that exists in test data."""

from pathlib import Path
from bs4 import BeautifulSoup
import re
from collections import defaultdict

LANGUAGES = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]

# Extract all fields by language from test data
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
    
    return fields_by_lang

# Create reverse lookup
def create_field_to_lang_map(fields_by_lang):
    field_to_langs = defaultdict(list)
    for lang, fields in fields_by_lang.items():
        for field in fields:
            field_to_langs[field].append(lang)
    return field_to_langs

print("Extracting test data fields...")
fields_by_lang = extract_test_fields()
field_to_langs = create_field_to_lang_map(fields_by_lang)

for lang in LANGUAGES:
    print(f"  {lang}: {len(fields_by_lang[lang])} fields")

print(f"\nTotal unique fields: {len(field_to_langs)}")

# Parse mapping.py
mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
lines = mapping_file.read_text(encoding='utf-8').split('\n')

new_lines = []
in_header_aliases = False
in_canonical_key = False
current_key_line = None
seen_langs_for_key = set()
kept_entries = []
duplicates_removed = 0

for line in lines:
    # Track when we enter HEADER_ALIASES
    if 'HEADER_ALIASES: dict[CanonicalKey, list[str]] = {' in line:
        in_header_aliases = True
        new_lines.append(line)
        continue
    
    # Track when we exit
    if in_header_aliases and line.strip() == '}':
        # Flush last key
        if in_canonical_key and kept_entries:
            new_lines.extend(kept_entries)
            new_lines.append('    ],')
        in_header_aliases = False
        new_lines.append(line)
        continue
    
    if not in_header_aliases:
        new_lines.append(line)
        continue
    
    # New CanonicalKey
    if 'CanonicalKey.' in line and ': [' in line:
        # Save previous key
        if in_canonical_key and kept_entries:
            new_lines.extend(kept_entries)
            new_lines.append('    ],')
        
        in_canonical_key = True
        current_key_line = line
        seen_langs_for_key = set()
        kept_entries = [line]
        continue
    
    # End of current key
    if in_canonical_key and line.strip() == '],':
        # Don't add yet - will be added when we process next key or exit
        continue
    
    # Process entry line
    if in_canonical_key:
        match = re.match(r'^\s+"(.+?)"', line)
        if match:
            field_text = match.group(1)
            
            # Find which language(s) this field belongs to
            langs_for_field = field_to_langs.get(field_text, [])
            
            if langs_for_field:
                # Check if we've already seen this language for this key
                new_langs = [lang for lang in langs_for_field if lang not in seen_langs_for_key]
                
                if new_langs:
                    # Keep this entry
                    kept_entries.append(line)
                    seen_langs_for_key.update(new_langs)
                else:
                    # Duplicate for language we already have
                    duplicates_removed += 1
            else:
                # Field not in test data - it's a true variant, skip it
                duplicates_removed += 1
        else:
            # Not a field entry (comment, etc.)
            kept_entries.append(line)

# Write back
new_content = '\n'.join(new_lines)
mapping_file.write_text(new_content, encoding='utf-8')

print(f"\n✅ Removed {duplicates_removed} duplicate/variant entries")
print(f"   Kept only ONE entry per language per CanonicalKey")
print(f"   File has {len(new_lines)} lines (was {len(lines)})")
