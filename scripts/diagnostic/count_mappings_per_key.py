"""Find CanonicalKeys that have more or fewer than 12 entries."""

from pathlib import Path
import re

mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
content = mapping_file.read_text(encoding='utf-8')

# Find all CanonicalKey entries
in_header_aliases = False
current_key = None
entry_count = 0
results = {}

for line in content.split('\n'):
    if 'HEADER_ALIASES: dict[CanonicalKey, list[str]] = {' in line:
        in_header_aliases = True
        continue
    
    if in_header_aliases and line.strip() == '}':
        if current_key:
            results[current_key] = entry_count
        break
    
    if not in_header_aliases:
        continue
    
    # New CanonicalKey
    if 'CanonicalKey.' in line and ': [' in line:
        if current_key:
            results[current_key] = entry_count
        match = re.search(r'CanonicalKey\.(\w+)', line)
        if match:
            current_key = match.group(1)
            entry_count = 0
        continue
    
    # Count entries (lines with quotes)
    if current_key and re.match(r'^\s+".*"', line):
        entry_count += 1

# Analyze results
print(f"Total CanonicalKeys: {len(results)}\n")

exact_12 = []
more_than_12 = []
less_than_12 = []

for key, count in sorted(results.items()):
    if count == 12:
        exact_12.append((key, count))
    elif count > 12:
        more_than_12.append((key, count))
    else:
        less_than_12.append((key, count))

print(f"✅ Keys with exactly 12 entries: {len(exact_12)}")
print(f"⚠️  Keys with MORE than 12 entries: {len(more_than_12)}")
print(f"ℹ️  Keys with LESS than 12 entries: {len(less_than_12)}\n")

if more_than_12:
    print("Keys with MORE than 12 entries:")
    print("=" * 60)
    for key, count in more_than_12:
        print(f"  {key}: {count} entries (excess: {count - 12})")

if less_than_12:
    print(f"\nKeys with LESS than 12 entries (may be device-specific):")
    print("=" * 60)
    for key, count in less_than_12:
        print(f"  {key}: {count} entries")
