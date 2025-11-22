#!/usr/bin/env python3#!/usr/bin/env python3

"""Get s_1_8 field names for missing languages.""""""Check what fields are in Czech and Finnish test files."""



from pathlib import Pathimport bs4

from bs4 import BeautifulSoupfrom pathlib import Path



for lang in ['sv', 'pl', 'cs', 'hu', 'fi']:# Now check both langs for heating section

    html = BeautifulSoup(Path(f'scripts/testdata/s_1_8_{lang}.html').read_text(encoding='utf-8'), 'html.parser')for lang in ['cs', 'fi']:

        html_file = Path(f'scripts/testdata/s_1_0_{lang}.html')

    print(f"\n{lang.upper()}:")    text = html_file.read_text(encoding='utf-8')

    for table in html.find_all('table'):    soup = bs4.BeautifulSoup(text, 'html.parser')

        for row in table.find_all('tr'):    

            tds = row.find_all('td')    tables = soup.find_all('table')

            if len(tds) >= 2:    

                fname = tds[0].get_text(strip=True)    # Find heating section

                if '1-' in fname or '1–' in fname or '13-' in fname or '13–' in fname:    heating_table = None

                    fval = tds[1].get_text(strip=True)    for table in tables:

                    print(f"  {fname}: {fval}")        th = table.find('th')

        if th:
            header_text = th.get_text().upper()
            # Check for variations: TOPENÍ (with diacritic), TOPENI (without), LÄMMITYS, HEATING
            if any(kw in header_text for kw in ['TOPENI', 'LÄMMITYS', 'HEATING']):
                heating_table = table
                break
    
    print(f"\n{lang.upper()} HEATING SECTION:")
    if heating_table:
        rows = heating_table.find_all('tr')
        for i, row in enumerate(rows):
            key_cell = row.find('td', class_='key')
            if key_cell:
                key_text = key_cell.get_text(strip=True)
                print(f"  {i:2d}. {key_text}")
    else:
        print("  NOT FOUND")
