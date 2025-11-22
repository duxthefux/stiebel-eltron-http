"""Extract all German field names from German testdata files."""

import re
from pathlib import Path
from bs4 import BeautifulSoup

TESTDATA_DIR = Path(__file__).parent / "testdata"

def extract_field_names_from_html(html_path):
    """Extract all field names from an HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    field_names = set()
    
    # Find section headers in <th> tags
    for th in soup.find_all('th'):
        text = th.get_text(strip=True)
        if text and len(text) > 1:
            field_names.add(text)
    
    # Find field names in <td class="key"> tags
    for td in soup.find_all('td', class_='key'):
        text = td.get_text(strip=True)
        if text:
            field_names.add(text)
    
    # Find headings in <h3> tags (like Betriebsart on start page)
    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        if text and len(text) > 1:
            field_names.add(text)
    
    # Find navigation menu items in <a> tags (like WARMWASSER, HEIZEN)
    for a in soup.find_all('a', href=True):
        # Only get menu navigation links, not other links
        if 'onclick="return checkChanges(this);"' in str(a):
            text = a.get_text(strip=True)
            if text and len(text) > 1:
                field_names.add(text)
    
    return field_names

def main():
    """Extract all German field names from test data."""
    # Find all German test data files
    german_files = sorted(TESTDATA_DIR.glob("*_de.html"))
    
    print(f"Found {len(german_files)} German test data files:")
    for f in german_files:
        print(f"  - {f.name}")
    print()
    
    all_german_fields = set()
    
    for html_file in german_files:
        fields = extract_field_names_from_html(html_file)
        all_german_fields.update(fields)
        print(f"{html_file.name}: {len(fields)} fields")
    
    print(f"\n{'='*80}")
    print(f"Total unique German field names: {len(all_german_fields)}")
    print(f"{'='*80}\n")
    
    # Sort and display
    sorted_fields = sorted(all_german_fields)
    for field in sorted_fields:
        print(f"  {field}")
    
    # Save to file
    output_file = Path(__file__).parent.parent / "extracted_german_fields.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for field in sorted_fields:
            f.write(f"{field}\n")
    
    print(f"\nSaved to: {output_file}")

if __name__ == "__main__":
    main()
