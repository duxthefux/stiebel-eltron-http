#!/usr/bin/env python3
"""Extract START_BETRIEBSART field names by position from all s_1_0 pages."""

from bs4 import BeautifulSoup

# All 12 languages
languages = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]

def extract_field_by_position(language):
    """Extract field name at same position as German FESTWERTBETRIEB."""
    filename = f"scripts/testdata/s_1_0_{language}.html"
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find all field labels (class="key")
        field_labels = []
        for row in soup.find_all("tr"):
            label_cell = row.find("td", class_="key")
            if label_cell:
                label_text = label_cell.get_text(strip=True)
                if label_text:
                    field_labels.append(label_text)
        
        # For German, find FESTWERTBETRIEB position
        if language == "de":
            for idx, label in enumerate(field_labels):
                if "FESTWERT" in label:
                    print(f"German field at position {idx}: {label}")
                    return idx, label
        else:
            # For other languages, use position 5 (found from German)
            if len(field_labels) > 5:
                return 5, field_labels[5]
            
        return None, None
        
    except Exception as e:
        return None, f"ERROR: {e}"

# First pass: Find German position
de_position, de_field = extract_field_by_position("de")
print(f"\nGerman BETRIEBSART field: '{de_field}' at position {de_position}\n")

# Extract from all languages at the same position
print("START_BETRIEBSART field names by language:\n")
results = []

for lang in languages:
    filename = f"scripts/testdata/s_1_0_{lang}.html"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find all field labels (class="key")
        field_labels = []
        for row in soup.find_all("tr"):
            label_cell = row.find("td", class_="key")
            if label_cell:
                label_text = label_cell.get_text(strip=True)
                if label_text:
                    field_labels.append(label_text)
        
        # Extract field at position de_position
        if de_position is not None and len(field_labels) > de_position:
            field_name = field_labels[de_position]
            results.append((lang, field_name))
            print(f'    "{field_name}",  # {lang}')
        else:
            print(f"    # {lang} - POSITION {de_position} NOT FOUND (only {len(field_labels)} fields)")
            
    except Exception as e:
        print(f"    # {lang} - ERROR: {e}")

print(f"\n\nFound {len(results)}/12 languages")
print("\nMapping format for mapping.py:")
print("CanonicalKey.START_BETRIEBSART: [")
for lang, field in results:
    print(f'    "{field}",  # {lang}')
print("],")
