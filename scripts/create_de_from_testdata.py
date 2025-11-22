"""Generate de.py with only German translations that appear in testdata.

This ensures we only include German translations that are actually used.
"""

import re
from pathlib import Path

# Read actual German field names from testdata
extracted_fields_file = Path(__file__).parent.parent / "extracted_german_fields.txt"
with open(extracted_fields_file, 'r', encoding='utf-8') as f:
    testdata_german_fields = {line.strip() for line in f if line.strip()}

print(f"Loaded {len(testdata_german_fields)} German field names from testdata")
print()

# Read mapping.py
mapping_file = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "mapping.py"
with open(mapping_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract HEADER_ALIASES dictionary
match = re.search(r'HEADER_ALIASES:.*?= \{(.*?)\n\}', content, re.DOTALL)
if not match:
    print("Could not find HEADER_ALIASES")
    exit(1)

aliases_text = match.group(1)

# Parse entries and filter for German translations that appear in testdata
german_translations = {}
total_found = 0
total_in_testdata = 0

# Find each CanonicalKey entry
entries = re.finditer(r'CanonicalKey\.(\w+):\s*\[(.*?)\]', aliases_text, re.DOTALL)

for entry in entries:
    key_name = entry.group(1)
    values_text = entry.group(2)
    
    # Extract quoted strings
    values = re.findall(r'"([^"]+)"', values_text)
    
    # Filter for values that appear in testdata
    testdata_values = []
    for value in values:
        if value in testdata_german_fields:
            testdata_values.append(value)
            total_in_testdata += 1
    
    if testdata_values:
        german_translations[key_name] = testdata_values
        total_found += len(testdata_values)

print(f"Found {len(german_translations)} keys with {total_found} German translations in testdata")
print()

# Generate de.py
output_file = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "i18n" / "de.py"

lines = [
    '"""German (de) translations.',
    '',
    'Extracted from mapping.py HEADER_ALIASES.',
    'Only includes strings that appear in German test data files.',
    '"""',
    '',
    'from .canonical_keys import CanonicalKey',
    '',
    '',
    'TRANSLATIONS: dict[CanonicalKey, list[str]] = {',
]

# Sort keys for consistent output
for key_name in sorted(german_translations.keys()):
    values = german_translations[key_name]
    lines.append(f'    CanonicalKey.{key_name}: [')
    for value in values:
        # Escape quotes and backslashes in the value
        escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
        lines.append(f'        "{escaped_value}",')
    lines.append('    ],')

lines.append('}')

output_content = '\n'.join(lines) + '\n'

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(output_content)

print(f"✓ Created {output_file}")
print(f"  Keys: {len(german_translations)}")
print(f"  Translations: {total_found}")
