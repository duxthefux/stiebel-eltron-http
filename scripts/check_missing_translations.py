import json

langs = ['cs', 'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']

# Load English as reference
en = json.load(open('custom_components/stiebel_eltron_http/translations/en.json', encoding='utf-8'))
en_keys = set(en['entity']['sensor'].keys())

print(f'English has {len(en_keys)} sensor translations\n')

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
    'dual_mode_temp_ww'
]

for lang in langs:
    filepath = f'custom_components/stiebel_eltron_http/translations/{lang}.json'
    data = json.load(open(filepath, encoding='utf-8'))
    lang_keys = set(data['entity']['sensor'].keys())
    
    missing = en_keys - lang_keys
    missing_important = [s for s in missing_sensors if s in missing]
    
    if missing:
        print(f'{lang}.json: {len(missing)} missing total')
        if missing_important:
            print(f'  Important missing: {", ".join(missing_important)}')
