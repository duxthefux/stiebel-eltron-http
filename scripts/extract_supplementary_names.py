from bs4 import BeautifulSoup

for lang in ['de','en','fr','nl','it','sv','es','pl','cs','hu','fi','da']:
    html = open(f'scripts/testdata/s_1_1_{lang}.html', encoding='utf-8').read()
    soup = BeautifulSoup(html, 'html.parser')
    
    rows = soup.find_all('tr')
    nhz_heating = None
    nhz_dhw = None
    
    for r in rows:
        cells = r.find_all('td')
        if len(cells) >= 2:
            field = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            
            # Look for fields that might be supplementary heating total
            # Pattern: Contains total indicator AND heating indicator
            field_upper = field.upper()
            is_total = any(word in field_upper for word in ['SUMME', 'TOTAL', 'SUMA', 'SOMMA', 'ÖSSZEG', 'YHT', 'SUM', 'CELKEM', 'ZUSAMMEN'])
            is_heating = any(word in field_upper for word in ['HEIZ', 'HEAT', 'CHAUFF', 'VERWAR', 'RISC', 'VÄRME', 'CALEF', 'GRZA', 'TOPENI', 'VYTÁP', 'FŰTÉS', 'FUTES', 'LÄMM', 'LAMM', 'VARME'])
            is_dhw = any(word in field_upper for word in ['WARMWASSER', 'DHW', 'EAU', 'WATER', 'ACQUA', 'VARM', 'AGUA', 'CWU', 'VODA', 'VÍZ', 'VIZ', 'VESI', 'VAND'])
            is_vd = 'VD' in field_upper
            is_supplementary = any(word in field_upper for word in ['NHZ', 'SUPPL', 'ZUSATZ', 'APPOINT', 'BIJV', 'INTEGR', 'TILLÄGG', 'COMPL', 'DODATOK', 'DOPLŇ', 'KIEGÉSZ', 'LISÄ', 'TILSKUD'])
            
            # Supplementary heating total
            if is_total and is_heating and is_supplementary and not nhz_heating:
                nhz_heating = field
            
            # Supplementary DHW total
            if is_total and is_dhw and is_supplementary and not nhz_dhw:
                nhz_dhw = field
    
    print(f'{lang}:')
    if nhz_heating:
        print(f'  Heating: {nhz_heating}')
    else:
        print(f'  Heating: NOT FOUND')
    
    if nhz_dhw:
        print(f'  DHW: {nhz_dhw}')
    else:
        print(f'  DHW: NOT FOUND')
    print()
