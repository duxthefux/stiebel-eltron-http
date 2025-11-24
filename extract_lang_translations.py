"""Extract translations from test HTML files for missing sensors."""
import re
from pathlib import Path
from bs4 import BeautifulSoup

langs = ['cs', 'da', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']

# Map of what to search for and the sensor key name
search_patterns = {
    'dual_mode_temp_hzg': ['BIVALENZ.*HZG', 'DUAL MODE.*HZG', 'BIVALENT.*HZG'],
    'dual_mode_temp_ww': ['BIVALENZ.*WW', 'DUAL MODE.*WW', 'BIVALENT.*WW'],
    'efficiency_dhw_today': ['EFFIZIENZ.*WARMWASSER.*1.*24', 'EFFICIENCY.*DHW.*1.*24', 'EFFICACITE.*ECS.*1.*24'],
    'efficiency_heating_today': ['EFFIZIENZ.*HEIZEN.*1.*24', 'EFFICIENCY.*HEATING.*1.*24', 'EFFICACITE.*CHAUFFAGE.*1.*24'],
    'efficiency_dhw_1_12m': ['EFFIZIENZ.*WARMWASSER.*1.*12', 'EFFICIENCY.*DHW.*1.*12', 'EFFICACITE.*ECS.*1.*12'],
    'efficiency_heating_1_12m': ['EFFIZIENZ.*HEIZEN.*1.*12', 'EFFICIENCY.*HEATING.*1.*12', 'EFFICACITE.*CHAUFFAGE.*1.*12'],
    'efficiency_dhw_13_24m': ['EFFIZIENZ.*WARMWASSER.*13.*24', 'EFFICIENCY.*DHW.*13.*24', 'EFFICACITE.*ECS.*13.*24'],
    'efficiency_heating_13_24m': ['EFFIZIENZ.*HEIZEN.*13.*24', 'EFFICIENCY.*HEATING.*13.*24', 'EFFICACITE.*CHAUFFAGE.*13.*24'],
    'room_temperature': ['RAUMTEMPERATUR', 'ROOM TEMP', 'TEMP.*AMBIANTE', 'TEMPERATURA AMBIENTE', 'KAMERTEMPERATUUR'],
    'room_humidity': ['RAUMFEUCHTE', 'ROOM.*HUMIDITY', 'HUMIDITE', 'UMIDITA'],
}

results = {}

for lang in langs:
    testfile = Path(f'scripts/testdata/s_1_0_{lang}.html')
    if not testfile.exists():
        print(f'{lang}: No test file found')
        continue
    
    print(f'\n{lang.upper()}:')
    results[lang] = {}
    
    html = testfile.read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all table cells with class="key"
    key_cells = soup.find_all('td', class_='key')
    
    for sensor_key, patterns in search_patterns.items():
        found = False
        for cell in key_cells:
            cell_text = cell.get_text(strip=True)
            for pattern in patterns:
                if re.search(pattern, cell_text, re.IGNORECASE):
                    print(f'  {sensor_key}: "{cell_text}"')
                    results[lang][sensor_key] = cell_text
                    found = True
                    break
            if found:
                break

print('\n\n=== JSON format for easy copy-paste ===\n')
for lang, translations in results.items():
    if translations:
        print(f'{lang}:')
        for key, value in translations.items():
            print(f'  "{key}": {{ "name": "{value}" }},')
