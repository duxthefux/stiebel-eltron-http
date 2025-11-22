from bs4 import BeautifulSoup

soup_de = BeautifulSoup(open('scripts/testdata/s_1_1_de.html', encoding='utf-8').read(), 'html.parser')
fields_de = [td.get_text(strip=True) for td in soup_de.find_all('td', class_='spalte1')]

nhz_heating_pos = fields_de.index('NHZ HEIZEN SUMME')
nhz_dhw_pos = fields_de.index('NHZ WARMWASSER SUMME')

print(f'NHZ HEIZEN SUMME at position: {nhz_heating_pos}')
print(f'NHZ WARMWASSER SUMME at position: {nhz_dhw_pos}')
print()

for lang in ['de','en','fr','nl','it','sv','es','pl','cs','hu','fi','da']:
    soup = BeautifulSoup(open(f'scripts/testdata/s_1_1_{lang}.html', encoding='utf-8').read(), 'html.parser')
    fields = [td.get_text(strip=True) for td in soup.find_all('td', class_='spalte1')]
    
    heating = fields[nhz_heating_pos]
    dhw = fields[nhz_dhw_pos]
    
    print(f'{lang}:')
    print(f'  Heating: {heating}')
    print(f'  DHW: {dhw}')
