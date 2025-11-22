#!/usr/bin/env python3
"""Extract ROOM TEMPERATURE section headers from all s_1_0 pages."""

from bs4 import BeautifulSoup

languages = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]

print("ROOM TEMPERATURE SECTION headers from s_1_0 pages:\n")

results = []
for lang in languages:
    filename = f"scripts/testdata/s_1_0_{lang}.html"
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Look for <th> containing room temperature keywords
        keywords = ["RAUM", "ROOM", "AMBI", "KAMER", "TMP", "TEMP", "POKOJOV", "SZOBA", "HUONE"]
        
        th = soup.find("th", string=lambda t: t and any(kw in t.upper() for kw in keywords))
        
        if th:
            text = th.get_text(strip=True)
            results.append((lang, text))
            print(f'    "{text}",  # {lang}')
        else:
            print(f"    # {lang} - NOT FOUND")
            
    except Exception as e:
        print(f"    # {lang} - ERROR: {e}")

print(f"\n\nFound {len(results)}/12 languages")

if len(results) < 12:
    print("\n\nMissing languages - checking manually:")
    for lang in languages:
        if lang not in [l for l, _ in results]:
            try:
                soup = BeautifulSoup(open(f"scripts/testdata/s_1_0_{lang}.html", encoding="utf-8").read(), "html.parser")
                all_th = [th.get_text(strip=True) for th in soup.find_all("th")]
                print(f"\n{lang} - All <th> headers:")
                for th in all_th[:10]:
                    print(f"  {th}")
            except:
                pass
