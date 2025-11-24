import json
import re

# Get all sensor keys from sensor.py
sensor_content = open('custom_components/stiebel_eltron_http/sensor.py', encoding='utf-8').read()
const_content = open('custom_components/stiebel_eltron_http/const.py', encoding='utf-8').read()

# Extract all _KEY constants
all_keys = set(re.findall(r'([A-Z_]+_KEY)', sensor_content))
# Map KEY constants to translation keys (remove _KEY suffix)
translation_keys = set()
for key in all_keys:
    if key.endswith('_KEY'):
        translation_key = key[:-4].lower()
        translation_keys.add(translation_key)

# Load translation files
en = json.load(open('custom_components/stiebel_eltron_http/translations/en.json', encoding='utf-8'))
de = json.load(open('custom_components/stiebel_eltron_http/translations/de.json', encoding='utf-8'))

en_sensors = set(en['entity']['sensor'].keys())
de_sensors = set(de['entity']['sensor'].keys())

missing_en = translation_keys - en_sensors - {'mac_address'}
missing_de = translation_keys - de_sensors - {'mac_address'}

print('=== Missing in English ===')
for s in sorted(missing_en):
    print(f'  {s}')

print('\n=== Missing in German ===')
for s in sorted(missing_de):
    print(f'  {s}')

print('\n=== In English but not in sensor.py ===')
extra_en = en_sensors - translation_keys
for s in sorted(extra_en):
    print(f'  {s}: "{en["entity"]["sensor"][s]["name"]}"')

print('\n=== In German but not in sensor.py ===')
extra_de = de_sensors - translation_keys
for s in sorted(extra_de):
    print(f'  {s}: "{de["entity"]["sensor"][s]["name"]}"')

