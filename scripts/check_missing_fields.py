#!/usr/bin/env python3
"""Check actual field names in Finnish and French HTML files."""

from pathlib import Path
from bs4 import BeautifulSoup

def extract_field_names(html_path, keywords):
    """Extract field names containing specific keywords."""
    html = BeautifulSoup(Path(html_path).read_text(encoding='utf-8'), 'html.parser')
    rows = html.find_all('tr')
    
    matching_fields = []
    for row in rows:
        tds = row.find_all('td')
        if len(tds) >= 2:
            field_name = tds[0].get_text(strip=True)
            field_value = tds[1].get_text(strip=True)
            
            # Check if any keyword is in the field name (case insensitive)
            if any(kw.lower() in field_name.lower() for kw in keywords):
                matching_fields.append((field_name, field_value))
    
    return matching_fields

print("=" * 80)
print("FINNISH (fi) - Fields with 'lämpötila', 'varaaja', 'tavoite', 'hk', 'kierto'")
print("=" * 80)
fi_fields = extract_field_names(
    'scripts/testdata/s_1_0_fi.html',
    ['lämpötila', 'varaaja', 'tavoite', 'hk', 'kierto']
)
for name, value in fi_fields:
    print(f"{name}: {value}")

print("\n" + "=" * 80)
print("FRENCH (fr) - Fields with 'bivalence', 'température'")
print("=" * 80)
fr_fields = extract_field_names(
    'scripts/testdata/s_1_0_fr.html',
    ['bivalence', 'température']
)
for name, value in fr_fields:
    print(f"{name}: {value}")
