#!/usr/bin/env python3
"""Extract VD heating sum (compressor heating total energy) from all s_1_1 pages."""

from bs4 import BeautifulSoup

languages = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]

print("VD_HEATING_SUM (compressor heating total energy) field names:\n")

for lang in languages:
    filename = f"scripts/testdata/s_1_1_{lang}.html"
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Find the heat amount section (contains "HEIZEN SUMME", "HEATING TOTAL", etc.)
        # This section comes BEFORE the runtime section
        # Look for pattern: VD <heating> DAY, then VD <heating> TOTAL/SUM
        all_keys = [td.get_text(strip=True) for td in soup.find_all("td", class_="key")]
        
        # Search for the heating sum pattern
        # German: "VD HEIZEN SUMME"
        # English: "VD HEATING TOTAL"
        # Pattern: Should be after a "DAY" field and before "DHW" or "WARMWASSER" fields
        
        for i, key in enumerate(all_keys):
            # Look for heating sum patterns
            if any(pattern in key.upper() for pattern in [
                "HEIZEN SUMME",
                "HEATING TOTAL",
                "CHAUFF. TOTAL",
                "VERWARMEN TOTAAL",
                "RISC SOMMA",
                "UPPVÄRMNING SUMMA",
                "CALEF. TOTAL",  # Spanish heating total
                "OGRZ SUMA",  # Polish heating sum (not DHW)
                "TOPENI SOUCET",
                "FÛTÉS ÖSSZEG",
                "LÄMM YHT",  # Finnish heating total (not DHW)
                "VARME SUM"
            ]) and not any(dhw in key.upper() for dhw in ["WARMWASSER", "DHW", "AGUA CAL", "CIEPLA WODA", "TEPLA VODA", "MELEGVÍZ", "LÄMMINV", "VARMT VAND"]):
                print(f'    "{key}",  # {lang}')
                break
        else:
            print(f"    # {lang} - NOT FOUND")
            
    except Exception as e:
        print(f"    # {lang} - ERROR: {e}")

print("\n\nFor mapping.py:")
