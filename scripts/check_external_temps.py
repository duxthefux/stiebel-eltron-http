#!/usr/bin/env python3
"""Check which languages got external temperature translations."""

import json
from pathlib import Path

LANGS = ['cs', 'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']

print("External temperature translations:")
print("=" * 80)

for lang in LANGS:
    json_path = Path(f"custom_components/stiebel_eltron_http/translations/{lang}.json")
    
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        sensors = data.get('entity', {}).get('sensor', {})
        ext_act = sensors.get('external_actual_temperature', {}).get('name', '')
        ext_set = sensors.get('external_set_temperature', {}).get('name', '')
        
        status = "OK" if ext_act and ext_set else "PARTIAL" if ext_act or ext_set else "MISSING"
        print(f"{lang.upper()}: {status:8} - Actual=\"{ext_act}\" Set=\"{ext_set}\"")

print("=" * 80)
