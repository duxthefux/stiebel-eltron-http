"""Copy missing translations from English to other languages as fallback."""
import json
from pathlib import Path

langs = ['cs', 'da', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']

# Load English translations
en_file = Path('custom_components/stiebel_eltron_http/translations/en.json')
en_data = json.load(en_file.open(encoding='utf-8'))
en_sensors = en_data['entity']['sensor']

# These are known translations from test data
known_translations = {
    'cs': {
        'dual_mode_temp_hzg': 'BIVALENTNI TEPLOTA TOPENI',
    },
    'nl': {
        'dual_mode_temp_hzg': 'BIVALENTIETEMPERATUUR HZG',
        'dual_mode_temp_ww': 'BIVALENTIETEMPERATUUR WW',
    },
    'it': {
        'dual_mode_temp_hzg': 'TEMP DI BIVALENZA HZG',
    },
}

# Sensors to add (missing in most languages)
missing_sensors = [
    'dhw_produced_today',
    'efficiency_dhw_today',
    'efficiency_dhw_1_12m',
    'efficiency_dhw_13_24m',
    'efficiency_heating_today',
    'efficiency_heating_1_12m',
    'efficiency_heating_13_24m',
    'heat_produced_today',
    'room_humidity',
    'room_temperature',
    'total_dhw_produced',
    'total_heat_produced',
    'dual_mode_temp_hzg',
    'dual_mode_temp_ww',
]

for lang in langs:
    lang_file = Path(f'custom_components/stiebel_eltron_http/translations/{lang}.json')
    lang_data = json.load(lang_file.open(encoding='utf-8'))
    lang_sensors = lang_data['entity']['sensor']
    
    added = []
    for sensor in missing_sensors:
        if sensor not in lang_sensors:
            # Use known translation if available, otherwise use English
            if lang in known_translations and sensor in known_translations[lang]:
                name = known_translations[lang][sensor]
            else:
                name = en_sensors[sensor]['name']
            
            lang_sensors[sensor] = {'name': name}
            added.append(f'{sensor} = "{name}"')
    
    if added:
        # Save updated file
        lang_file.write_text(json.dumps(lang_data, indent=4, ensure_ascii=False), encoding='utf-8')
        print(f'\n{lang}.json - Added {len(added)} translations:')
        for item in added:
            print(f'  {item}')

print('\n\nDone! All language files updated.')
