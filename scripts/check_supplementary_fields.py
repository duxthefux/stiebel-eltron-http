from bs4 import BeautifulSoup

for lang in ['de','en','fr','nl','it','sv','es','pl','cs','hu','fi','da']:
    html = open(f'scripts/testdata/s_1_1_{lang}.html', encoding='utf-8').read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get all field names
    fields = [td.get_text(strip=True) for td in soup.find_all('td', class_='spalte1')]
    
    # Look for supplementary/additional heater related fields
    # Keywords vary by language
    supp_keywords = [
        'NHZ', 'ZUSATZ',  # de - Zusatzheizung (supplementary heater)
        'SUPPL', 'ADDITIONAL',  # en
        'APPOINT', 'COMPLEMENT',  # fr
        'BIJVERW', 'AANVULLEND',  # nl
        'INTEGR', 'AGGIUNT',  # it
        'TILLÄGG', 'EXTRA',  # sv
        'COMPLEMENTA', 'ADICIONAL',  # es
        'DODATKOW',  # pl
        'DOPLŇKOV', 'PŘÍDAVN',  # cs
        'KIEGÉSZÍT', 'PÓTFŰT',  # hu
        'LISÄLÄMM',  # fi
        'TILSKUDS', 'EKSTRA',  # da
    ]
    
    supp_fields = [f for f in fields if any(kw in f.upper() for kw in supp_keywords)]
    
    print(f'\n{lang.upper()}: {len(supp_fields)} supplementary fields')
    for f in supp_fields:
        print(f'  {f}')
