#!/usr/bin/env python3
"""Apply manual translations to mapping.py file."""

from pathlib import Path
from manual_translations import MANUAL_TRANSLATIONS

# Read the current mapping.py
mapping_file = Path('custom_components/stiebel_eltron_http/mapping.py')
content = mapping_file.read_text(encoding='utf-8')

# For each field, find and replace its HEADER_ALIASES entry
replacements_made = 0

for field_name in sorted(MANUAL_TRANSLATIONS.keys()):
    translations = MANUAL_TRANSLATIONS[field_name]
    
    # Build the new entry
    new_entry_lines = [f"    CanonicalKey.{field_name}: ["]
    for lang in ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']:
        if lang in translations:
            new_entry_lines.append(f'        "{translations[lang]}",')
    new_entry_lines.append("    ],")
    new_entry = '\n'.join(new_entry_lines)
    
    # Find the existing entry pattern
    # Look for "CanonicalKey.FIELD_NAME: [" followed by lines until we hit "],\n"
    import re
    pattern = rf'    CanonicalKey\.{field_name}: \[.*?\],\n'
    
    match = re.search(pattern, content, re.DOTALL)
    if match:
        old_entry = match.group(0)
        content = content.replace(old_entry, new_entry + '\n', 1)
        replacements_made += 1
        print(f"✓ Replaced {field_name}")
    else:
        print(f"✗ Could not find {field_name} - may need manual addition")

# Write back
mapping_file.write_text(content, encoding='utf-8')
print(f"\nCompleted: {replacements_made} replacements made")
print(f"Updated: {mapping_file}")
