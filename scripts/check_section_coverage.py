#!/usr/bin/env python3
"""Count entries for all _SECTION canonical keys."""

import re

with open('custom_components/stiebel_eltron_http/mapping.py', encoding='utf-8') as f:
    lines = f.readlines()

sections = {}
current_key = None
count = 0

for line in lines:
    # Check for section canonical key
    if 'CanonicalKey.' in line and '_SECTION' in line and ': [' in line:
        match = re.search(r'CanonicalKey\.(\w+_SECTION):', line)
        if match:
            current_key = match.group(1)
            count = 0
    # Count entries
    elif current_key and '"' in line and line.strip().startswith('"'):
        count += 1
    # End of section
    elif current_key and '],' in line:
        sections[current_key] = count
        current_key = None
        count = 0

print("Section canonical keys with their entry counts:\n")
for key in sorted(sections.keys()):
    status = "✅" if sections[key] >= 12 else "⚠️ "
    print(f"{status} {key}: {sections[key]} entries")

print(f"\n\nSections with < 12 entries:")
for key in sorted(sections.keys()):
    if sections[key] < 12:
        print(f"  {key}: {sections[key]}/12")
