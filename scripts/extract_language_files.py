"""Extract language-specific translations from mapping.py into separate files."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from custom_components.stiebel_eltron_http.mapping import HEADER_ALIASES, CanonicalKey

# Read the mapping.py file to extract comments
mapping_file = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "mapping.py"
mapping_content = mapping_file.read_text(encoding="utf-8")

# Language codes in order
LANG_CODES = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]

# Store translations by language
translations_by_lang = {lang: {} for lang in LANG_CODES}

# Parse HEADER_ALIASES and extract by looking at comments in original file
for canonical_key, aliases in HEADER_ALIASES.items():
    # Find this canonical key in the file
    search_str = f'CanonicalKey.{canonical_key}:'
    if search_str in mapping_content:
        # Find the section
        start_idx = mapping_content.find(search_str)
        # Find the closing bracket
        bracket_count = 0
        in_list = False
        current_idx = start_idx
        
        while current_idx < len(mapping_content):
            char = mapping_content[current_idx]
            if char == '[':
                in_list = True
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0 and in_list:
                    # Found the end
                    section = mapping_content[start_idx:current_idx+1]
                    break
            current_idx += 1
        else:
            section = ""
        
        if section:
            # Extract each line with comment
            lines = section.split('\n')
            alias_idx = 0
            for line in lines:
                # Look for string with comment
                if '"' in line and '#' in line:
                    # Extract the string
                    str_start = line.find('"')
                    str_end = line.find('"', str_start + 1)
                    if str_start >= 0 and str_end > str_start:
                        alias_text = line[str_start+1:str_end]
                        
                        # Extract comment
                        comment_start = line.find('#', str_end)
                        if comment_start >= 0:
                            comment = line[comment_start+1:].strip()
                            
                            # Check if it's a language code or TODO
                            if comment in LANG_CODES:
                                if alias_text in aliases:
                                    translations_by_lang[comment][str(canonical_key)] = alias_text
                            elif comment.startswith('TODO') and alias_text in aliases:
                                # Extract lang code from before TODO
                                parts = line[str_end:comment_start].strip().split()
                                # Try to find lang in the comment or nearby
                                for lang in LANG_CODES:
                                    if f'# {lang}' in line[:comment_start]:
                                        translations_by_lang[lang][str(canonical_key)] = (alias_text, comment)
                                        break

# Write out language files
output_dir = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "i18n"

for lang_code in LANG_CODES:
    translations = translations_by_lang[lang_code]
    print(f"{lang_code}: {len(translations)} translations")
    
    # Build the file content
    content_lines = [
        f'"""Translation mappings for {lang_code.upper()} ({"German" if lang_code == "de" else "English" if lang_code == "en" else "French" if lang_code == "fr" else "Dutch" if lang_code == "nl" else "Italian" if lang_code == "it" else "Swedish" if lang_code == "sv" else "Spanish" if lang_code == "es" else "Polish" if lang_code == "pl" else "Czech" if lang_code == "cs" else "Hungarian" if lang_code == "hu" else "Finnish" if lang_code == "fi" else "Danish"})."""',
        '',
        'from .canonical_keys import CanonicalKey',
        '',
        '',
        f'TRANSLATIONS_{lang_code.upper()} = {{',
    ]
    
    for canonical_key_str, alias in sorted(translations.items()):
        if isinstance(alias, tuple):
            alias_text, comment = alias
            content_lines.append(f'    CanonicalKey.{canonical_key_str}: "{alias_text}",  # {comment}')
        else:
            content_lines.append(f'    CanonicalKey.{canonical_key_str}: "{alias_text}",')
    
    content_lines.append('}')
    content_lines.append('')
    
    output_file = output_dir / f"{lang_code}.py"
    output_file.write_text('\n'.join(content_lines), encoding='utf-8')
    print(f"  Wrote {output_file}")

print("\nDone!")
