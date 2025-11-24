#!/usr/bin/env python3
"""Extract external heat source section fields from all test data."""

from pathlib import Path
import re

TESTDATA_DIR = Path("testdata")
LANGUAGES = ["cs", "da", "de", "en", "es", "fi", "fr", "hu", "it", "nl", "pl", "sv"]

def extract_external_fields(lang: str):
    """Extract fields from external heat source section."""
    file_path = TESTDATA_DIR / f"s_1_0_{lang}.html"
    
    if not file_path.exists():
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find external section - match the header and get the content up to </table>
    # The structure is: <th>SECTION NAME</th></tr> <tr...><td class="key">FIELD</td>...
    patterns = [
        (r'(EXTERN|EXTERNAL|EKSTERN|ESTERNO|EXTÉRIEUR|EXTERNI|ZEWN|ULKOINEN|KÜLSŐ)[^<]*</th>', 'external'),
    ]
    
    section_start = None
    for pattern, name in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            section_start = match.end()
            break
    
    if not section_start:
        return []
    
    # Find the next </table> tag after the section start
    table_end = content.find('</table>', section_start)
    if table_end == -1:
        return []
    
    section_html = content[section_start:table_end]
    
    # Extract all field names
    fields = re.findall(r'<td class="key">([^<]+)</td>', section_html)
    return [f.strip() for f in fields]

print("External Heat Source Section Fields:")
print("=" * 80)

for lang in LANGUAGES:
    fields = extract_external_fields(lang)
    if fields:
        print(f"\n{lang.upper()}:")
        for i, field in enumerate(fields[:4], 1):  # First 4 fields
            print(f"  {i}. {field}")
    else:
        print(f"\n{lang.upper()}: NOT FOUND")

print("\n" + "=" * 80)
