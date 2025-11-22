#!/usr/bin/env python3
"""Extract VD heating sum field names from all s_1_1 pages by position."""

from bs4 import BeautifulSoup

languages = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]

def find_vd_heating_sum_position(lang):
    """Find the position of VD heating sum field."""
    filename = f"scripts/testdata/s_1_1_{lang}.html"
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, "html.parser")
        vd_fields = [td.get_text(strip=True) for td in soup.find_all("td", class_="key") if td.get_text(strip=True).startswith("VD")]
        
        for idx, field in enumerate(vd_fields):
            if lang == "de" and "HEIZEN SUMME" in field:
                return idx, field
            elif "HEATING" in field and ("TOTAL" in field or "SUM" in field):
                return idx, field
        
        return None, None
    except Exception as e:
        return None, f"ERROR: {e}"

# Find German position
de_pos, de_field = find_vd_heating_sum_position("de")
print(f"German VD heating sum: '{de_field}' at VD position {de_pos}\n")

# Extract from all languages
results = []
for lang in languages:
    filename = f"scripts/testdata/s_1_1_{lang}.html"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, "html.parser")
        vd_fields = [td.get_text(strip=True) for td in soup.find_all("td", class_="key") if td.get_text(strip=True).startswith("VD")]
        
        if de_pos is not None and len(vd_fields) > de_pos:
            field_name = vd_fields[de_pos]
            results.append((lang, field_name))
            print(f'    "{field_name}",  # {lang}')
        else:
            print(f"    # {lang} - VD position {de_pos} NOT FOUND")
            
    except Exception as e:
        print(f"    # {lang} - ERROR: {e}")

print(f"\n\nFound {len(results)}/12 languages")
print("\nMapping format for mapping.py:")
print("CanonicalKey.VD_HEATING_SUM: [")
for lang, field in results:
    print(f'    "{field}",  # {lang}')
print("],")
