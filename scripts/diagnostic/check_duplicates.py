#!/usr/bin/env python3
"""Find duplicate entries in HEADER_ALIASES."""

from pathlib import Path
import re

content = Path('custom_components/stiebel_eltron_http/mapping.py').read_text(encoding='utf-8')

# Find all HEADER_ALIASES entries
pattern = r'(CanonicalKey\.\w+): \[(.*?)\],'
matches = re.findall(pattern, content, re.DOTALL)

print("Checking for duplicate entries in HEADER_ALIASES...\n")

duplicates_found = False
for key_name, entries in matches:
    # Extract all string values
    values = re.findall(r'"([^"]+)"', entries)
    
    if len(values) != len(set(values)):
        duplicates_found = True
        print(f"\n{key_name}:")
        print(f"  Total entries: {len(values)}")
        print(f"  Unique entries: {len(set(values))}")
        
        # Show which values are duplicated
        from collections import Counter
        counts = Counter(values)
        for val, count in counts.items():
            if count > 1:
                print(f"  '{val}' appears {count} times")

if not duplicates_found:
    print("✅ No duplicates found! All canonical keys have unique field names per language.")
