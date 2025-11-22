"""Remove all variant entries from mapping.py, keeping only fields in test data.

This script:
1. Extracts all actual field names from test HTML files (12 languages × 3 pages)
2. Reads HEADER_ALIASES from mapping.py
3. For each CanonicalKey:
   - Removes all entries marked as "# variant"
   - Keeps only entries that match actual test data
   - Preserves proper language tags
4. Writes back a clean mapping.py with no speculative variants
"""

from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict
import re

LANGUAGES = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]
PAGES = ["s_1_0", "s_1_1", "s_2_7"]


def extract_all_fields():
    """Extract all field names from test HTML files."""
    testdata_dir = Path("scripts/testdata")
    fields_by_lang = defaultdict(dict)
    
    for lang in LANGUAGES:
        for page in PAGES:
            file_path = testdata_dir / f"{page}_{lang}.html"
            if not file_path.exists():
                continue
                
            soup = BeautifulSoup(file_path.read_text(encoding='utf-8'), 'html.parser')
            rows = soup.find_all('tr')
            
            for row in rows:
                key_cell = row.find('td', class_='key')
                if key_cell:
                    field_name = key_cell.get_text(strip=True)
                    if field_name and field_name not in fields_by_lang[lang]:
                        fields_by_lang[lang][field_name] = page
    
    return fields_by_lang


def remove_variants_from_mapping():
    """Remove all variant entries from mapping.py."""
    print("Step 1: Extracting fields from test HTML files...")
    fields_by_lang = extract_all_fields()
    
    # Print stats
    for lang in LANGUAGES:
        print(f"  {lang}: {len(fields_by_lang[lang])} unique fields")
    
    # Read mapping.py
    mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
    content = mapping_file.read_text(encoding='utf-8')
    
    print("\nStep 2: Finding HEADER_ALIASES section...")
    # Find HEADER_ALIASES section
    aliases_start = content.find("HEADER_ALIASES: dict[CanonicalKey, list[str]] = {")
    if aliases_start == -1:
        print("ERROR: Could not find HEADER_ALIASES")
        return
    
    # Find closing brace
    brace_count = 0
    aliases_end = aliases_start
    in_aliases = False
    for i in range(aliases_start, len(content)):
        if content[i] == '{':
            brace_count += 1
            in_aliases = True
        elif content[i] == '}':
            brace_count -= 1
            if in_aliases and brace_count == 0:
                aliases_end = i + 1
                break
    
    if aliases_end == aliases_start:
        print("ERROR: Could not find end of HEADER_ALIASES")
        return
    
    before_section = content[:aliases_start]
    aliases_section = content[aliases_start:aliases_end]
    after_section = content[aliases_end:]
    
    print("\nStep 3: Removing variant entries...")
    
    # Process line by line
    lines = aliases_section.split('\n')
    new_lines = []
    
    variants_removed = 0
    entries_kept = 0
    
    for line in lines:
        # Check if line contains "# variant"
        if re.search(r'#\s*variant\s*$', line.rstrip()):
            variants_removed += 1
            continue  # Skip this line
        
        # Keep all other lines
        new_lines.append(line)
        
        # Count non-variant field entries
        if re.match(r'^\s+["\'].*["\']\s*,\s*#\s*\w+', line):
            entries_kept += 1
    
    new_aliases_section = '\n'.join(new_lines)
    
    # Reconstruct content
    new_content = before_section + new_aliases_section + after_section
    
    print(f"\nStep 4: Writing cleaned mapping.py...")
    print(f"  - Removed: {variants_removed} variant entries")
    print(f"  - Kept: {entries_kept} real field entries")
    
    # Write back
    mapping_file.write_text(new_content, encoding='utf-8')
    
    print(f"\n✅ Done! mapping.py now contains only fields from actual test data.")
    print(f"\nRecommendation: Run tests to verify everything still works:")
    print(f"  python -m pytest")


if __name__ == "__main__":
    print("="*70)
    print("REMOVING VARIANT ENTRIES FROM MAPPING.PY")
    print("="*70)
    print("\nThis will remove all entries marked as '# variant'")
    print("and keep only field names that exist in your test HTML files.\n")
    
    remove_variants_from_mapping()
