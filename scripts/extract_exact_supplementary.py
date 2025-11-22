from bs4 import BeautifulSoup

# Get all fields from German (without class restriction)
soup_de = BeautifulSoup(open('scripts/testdata/s_1_1_de.html', encoding='utf-8').read(), 'html.parser')
rows_de = soup_de.find_all('tr')
fields_de = []
for r in rows_de:
    cells = r.find_all('td')
    if len(cells) >= 1:
        fields_de.append(cells[0].get_text(strip=True))

# Find positions
nhz_heating_pos = fields_de.index('NHZ HEIZEN SUMME')
nhz_dhw_pos = fields_de.index('NHZ WARMWASSER SUMME')

print(f'NHZ HEIZEN SUMME at position: {nhz_heating_pos}')
print(f'NHZ WARMWASSER SUMME at position: {nhz_dhw_pos}')
print('\\n' + '='*80)
print('EXACT FIELD NAMES FROM ALL LANGUAGES:')
print('='*80 + '\\n')

for lang in ['de','en','fr','nl','it','sv','es','pl','cs','hu','fi','da']:
    soup = BeautifulSoup(open(f'scripts/testdata/s_1_1_{lang}.html', encoding='utf-8').read(), 'html.parser')
    rows = soup.find_all('tr')
    fields = []
    for r in rows:
        cells = r.find_all('td')
        if len(cells) >= 1:
            fields.append(cells[0].get_text(strip=True))
    
    heating = fields[nhz_heating_pos] if nhz_heating_pos < len(fields) else "MISSING"
    dhw = fields[nhz_dhw_pos] if nhz_dhw_pos < len(fields) else "MISSING"
    
    print(f'{lang}:')
    print(f'  TOTAL_SUPPLEMENTARY_HEATING: "{heating}"')
    print(f'  TOTAL_SUPPLEMENTARY_DHW: "{dhw}"')
