"""Check for overlapping aliases in mapping.py"""
import re
from pathlib import Path
from collections import defaultdict

# Read the mapping.py file
mapping_file = Path(__file__).parent.parent.parent / "custom_components" / "stiebel_eltron_http" / "mapping.py"
content = mapping_file.read_text(encoding='utf-8')

# Extract HEADER_ALIASES dictionary
# Find the dictionary definition
match = re.search(r'HEADER_ALIASES:\s*dict\[CanonicalKey,\s*list\[str\]\]\s*=\s*{(.*?)\n}', content, re.DOTALL)
if not match:
    print("Could not find HEADER_ALIASES in mapping.py")
    exit(1)

dict_content = match.group(1)

# Parse the aliases - look for patterns like: KEY_NAME: [...],
pattern = r'(\w+):\s*\[(.*?)\],'
matches = re.findall(pattern, dict_content, re.DOTALL)

# Build alias -> keys mapping
alias_to_keys = defaultdict(list)
total_aliases = 0

for canonical_key, aliases_str in matches:
    # Extract individual aliases (strings in quotes)
    # Use a more precise pattern that handles escaped quotes
    alias_pattern = r'"([^"\\]*(?:\\.[^"\\]*)*)"|\'([^\'\\]*(?:\\.[^\'\\]*)*)\''
    alias_matches = re.findall(alias_pattern, aliases_str)
    
    # Extract non-empty matches (one of the two groups will match)
    aliases = [match[0] or match[1] for match in alias_matches]
    
    for alias in aliases:
        if alias:  # Skip empty strings
            normalized = alias.lower().strip()
            alias_to_keys[normalized].append(canonical_key)
            total_aliases += 1

# Find overlaps
overlaps = {alias: keys for alias, keys in alias_to_keys.items() if len(keys) > 1}

if overlaps:
    print(f'⚠️  Found {len(overlaps)} overlapping aliases:')
    print('='*80)
    for alias, keys in sorted(overlaps.items()):
        print(f'Alias: "{alias}"')
        for key in keys:
            print(f'  - {key}')
        print()
else:
    print('✓ No overlapping aliases found!')
    print(f'Total unique aliases: {len(alias_to_keys)}')
    print(f'Total aliases (including duplicates): {total_aliases}')
    print(f'Total canonical keys: {len(matches)}')

if overlaps:
    print(f'⚠️  Found {len(overlaps)} overlapping aliases:')
    print('='*80)
    for alias, keys in sorted(overlaps.items()):
        print(f'Alias: "{alias}"')
        for key in keys:
            print(f'  - {key}')
        print()
else:
    print('✓ No overlapping aliases found!')
    print(f'Total unique aliases: {len(alias_to_keys)}')
    print(f'Total aliases (including duplicates): {total_aliases}')
    print(f'Total canonical keys: {len(matches)}')
