#!/usr/bin/env python3
"""Extract h3 heading text for Betriebsart from all s_0_0 pages."""

from bs4 import BeautifulSoup
import glob

langs = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

print("START page (s_0_0) headings for Betriebsart:\n")

for lang in langs:
    files = glob.glob(f'scripts/testdata/s_0_0_{lang}.html')
    if not files:
        print(f"{lang}: NO FILE")
        continue
    
    html = open(files[0], encoding='utf-8').read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find h3 containing Betrieb/Operation/Mode/Drift keywords
    h3 = soup.find('h3', string=lambda t: t and any(
        word in t.upper() for word in ['BETRIEB', 'OPERATION', 'MODE', 'DRIFT', 'DRIFTS', 'UZEM', 'KÄYTTÖ', 'KAYTTO']
    ))
    
    if h3:
        print(f'{lang}: {h3.get_text(strip=True)}')
    else:
        print(f'{lang}: NOT FOUND')

print("\n\nMapping format (headings for matching):")
print("These should be ADDED to START_BETRIEBSART aliases for s_0_0 page matching:")
