"""Fix language comments in mapping.py by matching actual field names from test HTML files.

This script:
1. Extracts all field names from all test HTML files (12 languages × 3 pages)
2. For each CanonicalKey in HEADER_ALIASES:
   - For each string in the alias list:
     - Finds which language(s) contain that exact string
     - Adds/corrects the language comment
3. Handles cases where:
   - One string appears in multiple languages (add all, e.g., "# de, en, fr")
   - String not found in test data (mark as "# variant")
"""

from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import re

# Language order
LANGUAGES = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]

# Page patterns
PAGES = ["s_1_0", "s_1_1", "s_2_7"]  # Start, Info>Heatpump, Profile>Network


def extract_all_fields():
    """Extract all field names from all test HTML files.
    
    Returns:
        dict: {language: {field_name: page_where_found}}
    """
    testdata_dir = Path("scripts/testdata")
    fields_by_lang = defaultdict(dict)
    
    for lang in LANGUAGES:
        for page in PAGES:
            file_path = testdata_dir / f"{page}_{lang}.html"
            if not file_path.exists():
                continue
                
            soup = BeautifulSoup(file_path.read_text(encoding='utf-8'), 'html.parser')
            rows = soup.find_all('tr')
            
            for row in rows:
                key_cell = row.find('td', class_='key')
                if key_cell:
                    field_name = key_cell.get_text(strip=True)
                    if field_name and field_name not in fields_by_lang[lang]:
                        fields_by_lang[lang][field_name] = page
    
    return fields_by_lang


def find_languages_for_field(field_text, fields_by_lang):
    """Find which language(s) contain the exact field text.
    
    Args:
        field_text: The field name to search for
        fields_by_lang: Dictionary of {language: {field_name: page}}
    
    Returns:
        list: Language codes that contain this field (e.g., ['de', 'en'])
    """
    matching_langs = []
    for lang in LANGUAGES:
        if field_text in fields_by_lang[lang]:
            matching_langs.append(lang)
    return matching_langs


def fix_mapping_file():
    """Read mapping.py, fix all language comments, write back."""
    print("Extracting fields from test HTML files...")
    fields_by_lang = extract_all_fields()
    
    # Print stats
    for lang in LANGUAGES:
        print(f"  {lang}: {len(fields_by_lang[lang])} unique fields")
    
    mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
    content = mapping_file.read_text(encoding='utf-8')
    
    # Find HEADER_ALIASES section
    aliases_start = content.find("HEADER_ALIASES: dict[CanonicalKey, list[str]] = {")
    if aliases_start == -1:
        print("ERROR: Could not find HEADER_ALIASES in mapping.py")
        return
    
    # Find the closing brace for HEADER_ALIASES
    # This is tricky - need to match braces
    brace_count = 0
    aliases_end = aliases_start
    in_aliases = False
    for i in range(aliases_start, len(content)):
        if content[i] == '{':
            brace_count += 1
            in_aliases = True
        elif content[i] == '}':
            brace_count -= 1
            if in_aliases and brace_count == 0:
                aliases_end = i + 1
                break
    
    if aliases_end == aliases_start:
        print("ERROR: Could not find end of HEADER_ALIASES")
        return
    
    aliases_section = content[aliases_start:aliases_end]
    
    # Process each entry in HEADER_ALIASES
    # Pattern: "some text",  # old comment
    # Replace with: "some text",  # correct comment
    
    def replace_comment(match):
        """Replace the comment for a field entry."""
        indent = match.group(1)
        quote = match.group(2)
        field_text = match.group(3)
        
        # Find which language(s) have this field
        langs = find_languages_for_field(field_text, fields_by_lang)
        
        if langs:
            comment = ", ".join(langs)
        else:
            # Not found in test data - mark as variant
            comment = "variant"
        
        return f'{indent}{quote}{field_text}{quote},  # {comment}'
    
    # Pattern to match: whitespace + quote + text + quote + comma + optional comment
    pattern = r'^(\s+)(["\'`])(.*?)\2,\s*(?:#.*)?$'
    
    lines = aliases_section.split('\n')
    new_lines = []
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            new_line = replace_comment(match)
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    
    new_aliases_section = '\n'.join(new_lines)
    
    # Replace in content
    new_content = content[:aliases_start] + new_aliases_section + content[aliases_end:]
    
    # Write back
    mapping_file.write_text(new_content, encoding='utf-8')
    print(f"\nUpdated {mapping_file}")
    print("All language comments have been corrected based on actual test data.")


if __name__ == "__main__":
    fix_mapping_file()
