"""Check which CanonicalKeys are missing from the rebuilt mapping."""

from pathlib import Path
import re

# Get all CanonicalKeys from const.py
const_file = Path("custom_components/stiebel_eltron_http/const.py")
const_content = const_file.read_text(encoding='utf-8')

const_keys = set()
for line in const_content.split('\n'):
    if '_KEY =' in line:
        match = re.match(r'^(\w+)_KEY\s*=', line)
        if match:
            # Convert SOME_FIELD_KEY to SOME_FIELD
            const_keys.add(match.group(1))

print(f"Found {len(const_keys)} constants in const.py")

# Get all CanonicalKeys from mapping.py HEADER_ALIASES
mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
mapping_content = mapping_file.read_text(encoding='utf-8')

mapped_keys = set()
for line in mapping_content.split('\n'):
    if 'CanonicalKey.' in line and ': [' in line:
        match = re.search(r'CanonicalKey\.(\w+)', line)
        if match:
            mapped_keys.add(match.group(1))

print(f"Found {len(mapped_keys)} CanonicalKeys in HEADER_ALIASES")

# Find missing
missing = const_keys - mapped_keys
print(f"\n⚠️  {len(missing)} keys in const.py but NOT in HEADER_ALIASES:")
for key in sorted(missing):
    print(f"  - {key}")

# Find extra (in mapping but not in const)
extra = mapped_keys - const_keys
if extra:
    print(f"\nℹ️  {len(extra)} keys in HEADER_ALIASES but NOT in const.py:")
    for key in sorted(extra):
        print(f"  - {key}")
