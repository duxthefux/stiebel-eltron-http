#!/usr/bin/env python3
"""Add language comments to all HEADER_ALIASES entries."""

from pathlib import Path
import re

# Language order in the aliases
LANGUAGES = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

mapping_path = Path('custom_components/stiebel_eltron_http/mapping.py')
content = mapping_path.read_text(encoding='utf-8')

# Find all HEADER_ALIASES entries
# Pattern: match lines with quoted strings inside HEADER_ALIASES dictionary
lines = content.split('\n')
output_lines = []
inside_header_aliases = False
inside_canonical_key = False
lang_index = 0
indent_level = 0

for i, line in enumerate(lines):
    # Detect start of HEADER_ALIASES
    if 'HEADER_ALIASES: dict[CanonicalKey, list[str]] = {' in line:
        inside_header_aliases = True
        output_lines.append(line)
        continue
    
    # Detect end of HEADER_ALIASES (look for closing brace at indent 0)
    if inside_header_aliases and line.strip() == '}' and not inside_canonical_key:
        inside_header_aliases = False
        output_lines.append(line)
        continue
    
    if not inside_header_aliases:
        output_lines.append(line)
        continue
    
    # Detect start of a CanonicalKey entry
    if 'CanonicalKey.' in line and ': [' in line:
        inside_canonical_key = True
        lang_index = 0
        output_lines.append(line)
        continue
    
    # Detect end of a CanonicalKey entry
    if inside_canonical_key and line.strip() == '],':
        inside_canonical_key = False
        output_lines.append(line)
        continue
    
    # Process string entries inside CanonicalKey
    if inside_canonical_key and line.strip().startswith('"'):
        # Check if line already has a comment
        if '#' in line:
            # Already has comment, keep as is
            output_lines.append(line)
            lang_index += 1
        else:
            # Add language comment
            if lang_index < len(LANGUAGES):
                # Remove trailing comma if present, add comment, add comma back
                stripped = line.rstrip()
                if stripped.endswith(','):
                    new_line = stripped[:-1] + f',  # {LANGUAGES[lang_index]}'
                else:
                    new_line = stripped + f'  # {LANGUAGES[lang_index]}'
                output_lines.append(new_line)
                lang_index += 1
            else:
                # More entries than languages - just keep as is
                output_lines.append(line)
    else:
        output_lines.append(line)

# Write back
output_content = '\n'.join(output_lines)
mapping_path.write_text(output_content, encoding='utf-8')
print(f"Added language comments to HEADER_ALIASES in {mapping_path}")
