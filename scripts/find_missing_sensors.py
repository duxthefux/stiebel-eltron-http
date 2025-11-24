#!/usr/bin/env python3
"""Ensure all languages have all sensors by extracting from test data with fallback to section prefixes."""

import json
from pathlib import Path
from bs4 import BeautifulSoup

TRANSLATIONS_DIR = Path("custom_components/stiebel_eltron_http/translations")
TESTDATA_DIR = Path(__file__).parent / "testdata"
LANGUAGES = ["cs", "da", "es", "fi", "fr", "hu", "it", "nl", "pl", "sv"]

# First, collect all sensor keys from all languages
all_sensor_keys = set()
for lang in LANGUAGES:
    json_file = TRANSLATIONS_DIR / f"{lang}.json"
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_sensor_keys.update(data.get('entity', {}).get('sensor', {}).keys())

# Remove room sensors (not in test data)
all_sensor_keys.discard('room_temperature')
all_sensor_keys.discard('room_humidity')
all_sensor_keys.discard('start_operation_mode')  # This is from s_0_0, not table data

print(f"Total sensor keys to check: {len(all_sensor_keys)}")
print("=" * 80)

# For each language, show which sensors are missing
for lang in LANGUAGES:
    json_file = TRANSLATIONS_DIR / f"{lang}.json"
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    current_sensors = set(data.get('entity', {}).get('sensor', {}).keys())
    missing = all_sensor_keys - current_sensors
    
    if missing:
        print(f"\n{lang.upper()} missing {len(missing)} sensors:")
        for sensor in sorted(missing):
            print(f"  - {sensor}")
