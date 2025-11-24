#!/usr/bin/env python3
"""Extract operation mode field label from s_0_0 test data."""

from bs4 import BeautifulSoup
from pathlib import Path

TESTDATA_DIR = Path(__file__).parent / "testdata"

langs = ['cs', 'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']

print("Operation mode labels from s_0_0:")
print("=" * 80)

for lang in langs:
    html_file = TESTDATA_DIR / f"s_0_0_{lang}.html"
    if html_file.exists():
        soup = BeautifulSoup(html_file.open(encoding='utf-8'), 'html.parser')
        
        # Find the h3 with "Betriebsart" or similar
        h3_tags = soup.find_all('h3')
        for h3 in h3_tags:
            text = h3.get_text(strip=True)
            # Look for operation mode heading (not "Systemstatus" or "Portalstatus")
            if 'status' not in text.lower() and text and len(text) < 50:
                # Check if this is near an input with operation mode values
                parent = h3.find_parent()
                if parent:
                    inputs = parent.find_all('input', attrs={'value': True})
                    # Check if any input has typical operation mode values
                    for inp in inputs:
                        val = inp.get('value', '').upper()
                        if any(w in val for w in ['BETRIEB', 'MODE', 'PROGRAM', 'COMFORT', 'ECO']):
                            print(f"{lang.upper():3}: {text}")
                            break
                    else:
                        continue
                    break
