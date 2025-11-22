import json

de = json.load(open('custom_components/stiebel_eltron_http/translations/de.json', encoding='utf-8'))
en = json.load(open('custom_components/stiebel_eltron_http/translations/en.json', encoding='utf-8'))

sensors_de = de['entity']['sensor']
sensors_en = en['entity']['sensor']

print('=== GERMAN (de.json) ===')
print('Room sensors:')
print(f"  room_temperature: {sensors_de.get('room_temperature', {}).get('name', 'MISSING')}")
print(f"  room_relative_humidity: {sensors_de.get('room_relative_humidity', {}).get('name', 'MISSING')}")
print('\nHK sensors:')
print(f"  actual_temperature_hk_1: {sensors_de.get('actual_temperature_hk_1', {}).get('name', 'MISSING')}")
print(f"  actual_temperature_hk_2: {sensors_de.get('actual_temperature_hk_2', {}).get('name', 'MISSING')}")
print(f"  set_temperature_hk_1: {sensors_de.get('set_temperature_hk_1', {}).get('name', 'MISSING')}")
print(f"  set_temperature_hk_2: {sensors_de.get('set_temperature_hk_2', {}).get('name', 'MISSING')}")
print('\nBuffer sensors:')
print(f"  actual_buffer_temperature: {sensors_de.get('actual_buffer_temperature', {}).get('name', 'MISSING')}")
print(f"  set_buffer_temperature: {sensors_de.get('set_buffer_temperature', {}).get('name', 'MISSING')}")

print('\n=== ENGLISH (en.json) ===')
print('Room sensors:')
print(f"  room_temperature: {sensors_en.get('room_temperature', {}).get('name', 'MISSING')}")
print(f"  room_relative_humidity: {sensors_en.get('room_relative_humidity', {}).get('name', 'MISSING')}")
print('\nHK sensors:')
print(f"  actual_temperature_hk_1: {sensors_en.get('actual_temperature_hk_1', {}).get('name', 'MISSING')}")
print(f"  actual_temperature_hk_2: {sensors_en.get('actual_temperature_hk_2', {}).get('name', 'MISSING')}")
print(f"  set_temperature_hk_1: {sensors_en.get('set_temperature_hk_1', {}).get('name', 'MISSING')}")
print(f"  set_temperature_hk_2: {sensors_en.get('set_temperature_hk_2', {}).get('name', 'MISSING')}")
