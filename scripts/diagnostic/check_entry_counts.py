"""Check for keys with >12 entries or entries without comments."""

import re
from pathlib import Path

mapping_file = Path('custom_components/stiebel_eltron_http/mapping.py')
lines = mapping_file.read_text(encoding='utf-8').split('\n')

# Find HEADER_ALIASES
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if 'HEADER_ALIASES: dict[CanonicalKey, list[str]] = {' in line:
        start_idx = i
    elif start_idx is not None and line.strip() == '}':
        end_idx = i
        break

if not start_idx:
    print("Could not find HEADER_ALIASES")
    exit(1)

print(f"HEADER_ALIASES: lines {start_idx + 1} to {end_idx + 1}\n")

# Parse keys and entries
key_pattern = re.compile(r'^\s*CanonicalKey\.([A-Z_]+):\s*\[\s*$')
entry_pattern = re.compile(r'^\s*"([^"]+)",?\s*(?:#\s*(.+))?$')

current_key = None
entry_counts = {}
entries_without_comments = {}

for i in range(start_idx + 1, end_idx):
    line = lines[i]
    
    key_match = key_pattern.match(line)
    if key_match:
        current_key = key_match.group(1)
        entry_counts[current_key] = 0
        entries_without_comments[current_key] = []
        continue
    
    entry_match = entry_pattern.match(line)
    if entry_match and current_key:
        entry_counts[current_key] += 1
        comment = entry_match.group(2)
        if not comment:
            field_text = entry_match.group(1)
            entries_without_comments[current_key].append((i + 1, field_text))

# Report issues
print("=" * 80)
print("KEYS WITH MORE THAN 12 ENTRIES:")
print("=" * 80)
keys_gt_12 = {k: c for k, c in entry_counts.items() if c > 12}
if keys_gt_12:
    for key, count in sorted(keys_gt_12.items(), key=lambda x: -x[1]):
        print(f"  {key}: {count} entries ({count - 12} extra)")
else:
    print("  None found!")

print("\n" + "=" * 80)
print("KEYS WITH ENTRIES WITHOUT LANGUAGE COMMENTS:")
print("=" * 80)
keys_without_comments = {k: v for k, v in entries_without_comments.items() if v}
if keys_without_comments:
    for key, entries in sorted(keys_without_comments.items()):
        print(f"\n  {key}: {len(entries)} entries without comments")
        for line_num, field_text in entries[:5]:  # Show first 5
            print(f"    Line {line_num}: \"{field_text}\"")
        if len(entries) > 5:
            print(f"    ... and {len(entries) - 5} more")
else:
    print("  None found!")

print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"Total keys: {len(entry_counts)}")
print(f"Keys with exactly 12 entries: {sum(1 for c in entry_counts.values() if c == 12)}")
print(f"Keys with <12 entries: {sum(1 for c in entry_counts.values() if c < 12)}")
print(f"Keys with >12 entries: {len(keys_gt_12)}")
print(f"Keys with entries missing comments: {len(keys_without_comments)}")
