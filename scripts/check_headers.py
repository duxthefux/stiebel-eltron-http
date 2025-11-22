#!/usr/bin/env python3
import bs4

langs = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']
pages = ['s_1_0', 's_1_1', 's_2_7']

for page in pages:
    print("=" * 80)
    print(f"{page} SECTION HEADERS BY LANGUAGE")
    print("=" * 80)
    
    for lang in langs:
        html_file = f'scripts/testdata/{page}_{lang}.html'
        try:
            html = open(html_file, encoding='utf-8').read()
            soup = bs4.BeautifulSoup(html, 'html.parser')
            headers = [th.get_text(strip=True) for th in soup.find_all('th')]
            print(f"{lang}: {headers}")
        except FileNotFoundError:
            print(f"{lang}: FILE NOT FOUND")
    print()
