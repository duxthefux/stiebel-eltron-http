"""Deduplicate each CanonicalKey to have EXACTLY 12 entries (one per language) from test data.

For each CanonicalKey:
1. Extract the field name from each of the 12 languages' test files  
2. Keep only ONE entry per language (the one that actually exists in test data)
3. Add language comment

Since all pages have same structure, fields at same position should be same concept.
"""

from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import re

LANGUAGES = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]
PAGES = ["s_1_0", "s_1_1", "s_2_7"]

def extract_test_fields_by_lang():
    """Extract all fields from test data, organized by language."""
    testdata_dir = Path("scripts/testdata")
    fields_by_lang = defaultdict(set)
    
    for lang in LANGUAGES:
        for page in PAGES:
            file_path = testdata_dir / f"{page}_{lang}.html"
            if file_path.exists():
                soup = BeautifulSoup(file_path.read_text(encoding='utf-8'), 'html.parser')
                for row in soup.find_all('tr'):
                    key_cell = row.find('td', class_='key')
                    if key_cell:
                        field_name = key_cell.get_text(strip=True)
                        if field_name:
                            fields_by_lang[lang].add(field_name)
    
    # Create reverse lookup: field -> list of languages it appears in
    field_to_langs = defaultdict(list)
    for lang, fields in fields_by_lang.items():
        for field in fields:
            field_to_langs[field].append(lang)
    
    return fields_by_lang, field_to_langs

print("Extracting fields from test data...")
fields_by_lang, field_to_langs = extract_test_fields_by_lang()

for lang in LANGUAGES:
    print(f"  {lang}: {len(fields_by_lang[lang])} fields")

print(f"\nTotal unique fields in test data: {len(field_to_langs)}")

# Now process mapping.py
mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
lines = mapping_file.read_text(encoding='utf-8').split('\n')

new_lines = []
in_header_aliases = False
current_key_name = None
seen_langs_in_key = set()
pending_entries = []
stats = {"kept": 0, "removed": 0, "keys_processed": 0}

for i, line in enumerate(lines):
    # Detect HEADER_ALIASES section
    if 'HEADER_ALIASES: dict[CanonicalKey, list[str]] = {' in line:
        in_header_aliases = True
        new_lines.append(line)
        continue
    
    # Detect end of HEADER_ALIASES
    if in_header_aliases and line.strip() == '}':
        # Flush last key
        if current_key_name and pending_entries:
            new_lines.extend(pending_entries)
            new_lines.append('    ],')
        in_header_aliases = False
        new_lines.append(line)
        continue
    
    if not in_header_aliases:
        new_lines.append(line)
        continue
    
    # Detect new CanonicalKey
    if 'CanonicalKey.' in line and ': [' in line:
        # Flush previous key
        if current_key_name and pending_entries:
            new_lines.extend(pending_entries)
            new_lines.append('    ],')
        
        stats["keys_processed"] += 1
        current_key_name = line.strip()
        seen_langs_in_key = set()
        pending_entries = [line]
        continue
    
    # Detect end of list for current key
    if current_key_name and line.strip() == '],':
        # Don't add yet, will be added when we flush
        continue
    
    # Process entry line
    if current_key_name:
        match = re.match(r'^\s+"(.+?)"', line)
        if match:
            field_text = match.group(1)
            
            # Find which language(s) have this field
            langs_for_field = field_to_langs.get(field_text, [])
            
            if langs_for_field:
                # This field exists in test data
                # Check if we already have an entry for any of these languages
                new_langs = [lang for lang in langs_for_field if lang not in seen_langs_in_key]
                
                if new_langs:
                    # Keep this entry, add language comment
                    indent = line[:len(line) - len(line.lstrip())]
                    lang_comment = ", ".join(new_langs)
                    new_line = f'{indent}"{field_text}",  # {lang_comment}'
                    pending_entries.append(new_line)
                    seen_langs_in_key.update(new_langs)
                    stats["kept"] += 1
                else:
                    # Duplicate for language we already have
                    stats["removed"] += 1
            else:
                # Field not in test data - skip it
                stats["removed"] += 1
        else:
            # Not a field entry (comment, blank line, etc.)
            pending_entries.append(line)

# Write back
new_content = '\n'.join(new_lines)
mapping_file.write_text(new_content, encoding='utf-8')

print(f"\n✅ Deduplication complete!")
print(f"   Keys processed: {stats['keys_processed']}")
print(f"   Entries kept: {stats['kept']}")
print(f"   Entries removed: {stats['removed']}")
print(f"   Output has {len(new_lines)} lines (was {len(lines)})")
