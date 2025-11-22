"""Simple, safe removal of variant entries from mapping.py."""

from pathlib import Path
import re

mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
content = mapping_file.read_text(encoding='utf-8')
lines = content.split('\n')

new_lines = []
variants_removed = 0

for line in lines:
    # Check if this line is a field entry marked as variant
    if re.match(r'^\s+".*?",\s*#\s*variant\s*$', line):
        variants_removed += 1
        # Skip this line
        continue
    else:
        new_lines.append(line)

# Write back
new_content = '\n'.join(new_lines)
mapping_file.write_text(new_content, encoding='utf-8')

print(f"✅ Removed {variants_removed} variant entries")
print(f"   File has {len(new_lines)} lines (was {len(lines)})")
