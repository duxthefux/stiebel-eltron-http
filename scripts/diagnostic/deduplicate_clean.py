"""
Clean deduplication using simple line-by-line processing.
Preserves exact structure, just filters entries.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

# Language order
LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

def extract_fields_from_html(file_path: Path) -> set[str]:
    """Extract all field names from an HTML file."""
    html = file_path.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    fields = set()
    for row in soup.find_all('tr'):
        key_cell = row.find('td', class_='key')
        if key_cell:
            field = key_cell.get_text(strip=True)
            if field:
                fields.add(field)
    return fields

def build_field_to_languages() -> dict[str, list[str]]:
    """Build mapping of field text to list of languages it appears in."""
    testdata_dir = Path('scripts/testdata')
    field_to_langs = {}
    
    for lang in LANGUAGES:
        lang_fields = set()
        # Check all 3 pages for this language
        for page in ['s_1_0', 's_1_1', 's_2_7']:
            html_file = testdata_dir / f'{page}_{lang}.html'
            if html_file.exists():
                lang_fields.update(extract_fields_from_html(html_file))
        
        # Add this language to each field
        for field in lang_fields:
            if field not in field_to_langs:
                field_to_langs[field] = []
            field_to_langs[field].append(lang)
    
    return field_to_langs

def main():
    print("Building field->languages mapping from test data...")
    field_to_langs = build_field_to_languages()
    print(f"Found {len(field_to_langs)} unique fields across all languages")
    
    # Read original mapping.py
    mapping_file = Path('custom_components/stiebel_eltron_http/mapping.py')
    content = mapping_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Find where HEADER_ALIASES starts and ends
    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if 'HEADER_ALIASES: dict[CanonicalKey, list[str]] = {' in line:
            start_idx = i
        elif start_idx is not None and line.strip() == '}':
            end_idx = i
            break
    
    if start_idx is None or end_idx is None:
        print("ERROR: Could not find HEADER_ALIASES bounds")
        return
    
    print(f"HEADER_ALIASES: lines {start_idx + 1} to {end_idx + 1}")
    
    # Keep everything before HEADER_ALIASES
    result = lines[:start_idx + 1]
    
    # Process HEADER_ALIASES line by line
    current_key = None
    seen_languages = set()
    brace_depth = 0
    
    key_pattern = re.compile(r'^\s*CanonicalKey\.([A-Z_]+):\s*\[\s*$')
    entry_pattern = re.compile(r'^\s*"([^"]+)",?\s*(?:#.*)?$')
    
    entries_kept = 0
    entries_removed = 0
    keys_processed = 0
    
    # Track which keys have ANY entries in test data
    keys_in_testdata = set()
    for field in field_to_langs:
        for entry_str in field_to_langs[field]:
            keys_in_testdata.add(field)
    
    # First pass: identify which CanonicalKeys have at least one entry in test data
    canonical_keys_in_testdata = set()
    i = start_idx + 1
    while i < end_idx:
        line = lines[i]
        key_match = key_pattern.match(line)
        if key_match:
            temp_key = key_match.group(1)
            # Check next lines for any entry that's in test data
            j = i + 1
            while j < end_idx and not key_pattern.match(lines[j]) and lines[j].strip() not in ('],', ']', '}'):
                entry_match = entry_pattern.match(lines[j])
                if entry_match:
                    field_text = entry_match.group(1)
                    if field_text in field_to_langs:
                        canonical_keys_in_testdata.add(temp_key)
                        break
                j += 1
        i += 1
    
    print(f"Found {len(canonical_keys_in_testdata)} keys with entries in test data")
    
    # Now process
    for i in range(start_idx + 1, end_idx + 1):
        line = lines[i]
        
        # Check for new CanonicalKey
        key_match = key_pattern.match(line)
        if key_match:
            if current_key:
                keys_processed += 1
            current_key = key_match.group(1)
            seen_languages = set()
            result.append(line)
            continue
        
        # Check if it's an entry
        entry_match = entry_pattern.match(line)
        if entry_match and current_key:
            field_text = entry_match.group(1)
            existing_comment = entry_match.group(2) if len(entry_match.groups()) > 1 else None
            
            # If this key has NO entries in test data, preserve entries but ensure they have comments
            if current_key not in canonical_keys_in_testdata:
                # If already has a comment, keep as-is
                if existing_comment:
                    result.append(line)
                else:
                    # Add a generic comment indicating it's not in test data
                    result.append(f'        "{field_text}",  # variant')
                entries_kept += 1
                continue
            
            # Find which languages this field belongs to
            langs_for_field = field_to_langs.get(field_text, [])
            
            # Keep if it covers new languages
            new_langs = [l for l in langs_for_field if l not in seen_languages]
            
            if new_langs:
                # Keep this entry and add language comment
                if len(langs_for_field) == len(LANGUAGES):
                    comment = "  # all"
                else:
                    comment = f"  # {', '.join(langs_for_field)}"
                
                # Write entry with comment
                result.append(f'        "{field_text}",{comment}')
                seen_languages.update(new_langs)
                entries_kept += 1
            else:
                # Duplicate - skip
                entries_removed += 1
            continue
        
        # Check for closing bracket
        if line.strip() in ('],', ']'):
            if current_key:
                keys_processed += 1
                current_key = None
                seen_languages = set()
            result.append(line)
            continue
        
        # Any other line (comments, blank lines, etc.)
        result.append(line)
    
    # Add everything after HEADER_ALIASES
    result.extend(lines[end_idx + 1:])
    
    # Write output
    output = '\n'.join(result)
    mapping_file.write_text(output, encoding='utf-8')
    
    print(f"\nDone!")
    print(f"Keys processed: {keys_processed}")
    print(f"Entries kept: {entries_kept}")
    print(f"Entries removed: {entries_removed}")
    print(f"Total lines: {len(result)} (was {len(lines)})")

if __name__ == '__main__':
    main()
