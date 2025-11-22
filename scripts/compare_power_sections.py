"""Check power consumption section names across languages and pages."""
from pathlib import Path
from bs4 import BeautifulSoup

langs = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']
pages = ['s_1_1', 's_1_8']

print("Power/Consumption Section Names by Language and Page:\n")
print(f"{'Lang':<6} {'s_1_1':<40} s_1_8")
print("-" * 90)

for lang in langs:
    row = [lang]
    
    for page in pages:
        html_file = Path(f"scripts/testdata/{page}_{lang}.html")
        if html_file.exists():
            soup = BeautifulSoup(html_file.read_text('utf-8'), 'html.parser')
            
            # Find the section header (looking for power/consumption related terms)
            found = None
            for th in soup.find_all('th', colspan="2"):
                text = th.get_text(strip=True).upper()
                # Keywords that indicate power consumption section
                keywords = ['LEISTUNG', 'POWER', 'CONSOM', 'STROOM', 'VERBRUIK', 
                           'POTENZA', 'EFFEKT', 'CONSUMO', 'POBOR', 'PRIKON',
                           'TELJES', 'TEHO', 'ENERGI']
                if any(kw in text for kw in keywords):
                    found = th.get_text(strip=True)
                    break
            
            row.append(found if found else "NOT FOUND")
        else:
            row.append("FILE MISSING")
    
    print(f"{row[0]:<6} {row[1]:<40} {row[2]}")

print("\n" + "=" * 90)
print("Analysis: Languages with DIFFERENT terms for s_1_1 vs s_1_8:")
print("(These should be kept as separate list entries in POWER_CONSUMPTION_SECTION)")
