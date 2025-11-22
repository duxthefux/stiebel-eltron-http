import json
from pathlib import Path

langs = ['fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

print('Checking for room_temperature mapping bug in all languages:\n')
print('=' * 80)

for lang in langs:
    path = Path(f'custom_components/stiebel_eltron_http/translations/{lang}.json')
    if path.exists():
        data = json.load(open(path, encoding='utf-8'))
        sensors = data.get('entity', {}).get('sensor', {})
        
        rt = sensors.get('room_temperature', {}).get('name', 'MISSING')
        rh = sensors.get('room_relative_humidity', {}).get('name', 'MISSING')
        hk1 = sensors.get('actual_temperature_hk_1', {}).get('name', 'MISSING')
        hk2 = sensors.get('actual_temperature_hk_2', {}).get('name', 'MISSING')
        shk1 = sensors.get('set_temperature_hk_1', {}).get('name', 'MISSING')
        shk2 = sensors.get('set_temperature_hk_2', {}).get('name', 'MISSING')
        buf_act = sensors.get('actual_buffer_temperature', {}).get('name', 'MISSING')
        buf_set = sensors.get('set_buffer_temperature', {}).get('name', 'MISSING')
        
        print(f'\n{lang.upper()}:')
        print(f'  room_temperature: {rt}')
        print(f'  room_relative_humidity: {rh}')
        print(f'  actual_temperature_hk_1: {hk1}')
        print(f'  actual_temperature_hk_2: {hk2}')
        print(f'  set_temperature_hk_1: {shk1}')
        print(f'  set_temperature_hk_2: {shk2}')
        print(f'  actual_buffer_temperature: {buf_act}')
        print(f'  set_buffer_temperature: {buf_set}')
        
        # Check for bugs
        bugs = []
        if 'HK' in rt or 'hk' in rt.lower():
            bugs.append(f"❌ BUG: room_temperature has HK reference: '{rt}'")
        if hk1 == 'MISSING':
            bugs.append("❌ MISSING: actual_temperature_hk_1")
        if hk2 == 'MISSING':
            bugs.append("❌ MISSING: actual_temperature_hk_2")
        if rh == 'MISSING':
            bugs.append("⚠️  MISSING: room_relative_humidity (optional sensor)")
        if shk1 == 'MISSING':
            bugs.append("❌ MISSING: set_temperature_hk_1")
        if shk2 == 'MISSING':
            bugs.append("❌ MISSING: set_temperature_hk_2")
        if buf_act == 'MISSING':
            bugs.append("❌ MISSING: actual_buffer_temperature")
        if buf_set == 'MISSING':
            bugs.append("❌ MISSING: set_buffer_temperature")
            
        if bugs:
            print('  Issues:')
            for bug in bugs:
                print(f'    {bug}')

print('\n' + '=' * 80)
