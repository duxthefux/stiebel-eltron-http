"""Remove variant entries from mapping.py, keeping only real fields from test data.

Strategy:
1. Extract all field names from test HTML files
2. For each CanonicalKey in HEADER_ALIASES:
   - Keep only entries that match actual test data fields
   - Preserve the order and language comments
   - Remove true variants (not in test data)
3. Ensure each CanonicalKey has exactly 12 entries (one per language) or fewer for device-specific fields
"""

from pathlib import Path
from bs4 import BeautifulSoup
import re
from collections import defaultdict

LANGUAGES = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]

def extract_test_fields():
    """Extract all field names from test HTML files."""
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
    
    # Create reverse lookup: field -> list of languages
    field_to_langs = defaultdict(list)
    for lang, fields in fields_by_lang.items():
        for field in fields:
            field_to_langs[field].append(lang)
    
    return fields_by_lang, field_to_langs

def clean_mapping_file():
    """Remove variants from mapping.py."""
    print("Extracting fields from test HTML files...")
    fields_by_lang, field_to_langs = extract_test_fields()
    
    for lang in LANGUAGES:
        print(f"  {lang}: {len(fields_by_lang[lang])} fields")
    
    all_test_fields = set()
    for fields in fields_by_lang.values():
        all_test_fields.update(fields)
    print(f"\nTotal unique fields in test data: {len(all_test_fields)}")
    
    mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
    lines = mapping_file.read_text(encoding='utf-8').split('\n')
    
    new_lines = []
    in_header_aliases = False
    in_canonical_key = False
    current_key_name = None
    current_entries = []
    brace_depth = 0
    
    for i, line in enumerate(lines):
        # Track when we enter HEADER_ALIASES
        if 'HEADER_ALIASES: dict[CanonicalKey, list[str]] = {' in line:
            in_header_aliases = True
            new_lines.append(line)
            continue
        
        # Track brace depth
        if in_header_aliases:
            brace_depth += line.count('{') - line.count('}')
            if brace_depth == 0 and '}' in line:
                in_header_aliases = False
                new_lines.append(line)
                continue
        
        if not in_header_aliases:
            new_lines.append(line)
            continue
        
        # Check if this is a CanonicalKey line
        if 'CanonicalKey.' in line and ': [' in line:
            # Save previous key if any
            if in_canonical_key and current_entries:
                new_lines.extend(current_entries)
                new_lines.append('    ],')
            
            in_canonical_key = True
            current_key_name = line.strip()
            current_entries = [line]
            continue
        
        # Check if this is the end of a canonical key
        if in_canonical_key and line.strip() == '],':
            # Process entries for current key
            if current_entries:
                new_lines.extend(current_entries)
                new_lines.append(line)
            current_entries = []
            in_canonical_key = False
            continue
        
        # Process entry lines within a canonical key
        if in_canonical_key:
            # Check if this line is a field entry
            match = re.match(r'^\s+"(.+?)",\s*#\s*(.+)$', line)
            if match:
                field_text = match.group(1)
                comment = match.group(2)
                
                # Keep if field is in test data (not marked as variant)
                if 'variant' not in comment:
                    current_entries.append(line)
                elif field_text in all_test_fields:
                    # This is marked as variant but IS in test data - keep it but fix comment
                    langs = field_to_langs.get(field_text, [])
                    if langs:
                        lang_comment = ', '.join(langs)
                        indent = line[:len(line) - len(line.lstrip())]
                        new_line = f'{indent}"{field_text}",  # {lang_comment}'
                        current_entries.append(new_line)
                        print(f"  Fixed: {field_text} -> # {lang_comment}")
                # else: skip variant entries not in test data
            else:
                # Not a field entry, keep as-is
                current_entries.append(line)
    
    # Write back
    mapping_file.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"\n✅ Cleaned mapping.py - removed variant entries not in test data")

if __name__ == "__main__":
    clean_mapping_file()
