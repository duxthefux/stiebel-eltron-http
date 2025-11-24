#!/usr/bin/env python3
"""Compare which sensors exist in each language's test data."""

import json
from pathlib import Path
from bs4 import BeautifulSoup

TRANSLATIONS_DIR = Path("custom_components/stiebel_eltron_http/translations")
TESTDATA_DIR = Path(__file__).parent / "testdata"
LANGUAGES = ["cs", "da", "es", "fi", "fr", "hu", "it", "nl", "pl", "sv"]

# Load all translations
lang_sensors = {}
for lang in LANGUAGES:
    json_file = TRANSLATIONS_DIR / f"{lang}.json"
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    lang_sensors[lang] = set(data.get('entity', {}).get('sensor', {}).keys())

# Get all unique sensor keys
all_sensors = set()
for sensors in lang_sensors.values():
    all_sensors.update(sensors)

# Check which sensors are in each language's test data
print("Sensor availability across languages:")
print("=" * 100)

for sensor in sorted(all_sensors):
    langs_with_sensor = [lang.upper() for lang in LANGUAGES if sensor in lang_sensors[lang]]
    langs_without_sensor = [lang.upper() for lang in LANGUAGES if sensor not in lang_sensors[lang]]
    
    if langs_without_sensor:
        print(f"\n{sensor}:")
        print(f"  HAS ({len(langs_with_sensor)}): {', '.join(langs_with_sensor)}")
        print(f"  MISSING ({len(langs_without_sensor)}): {', '.join(langs_without_sensor)}")

print("\n" + "=" * 100)
print("\nTranslation counts:")
for lang in LANGUAGES:
    count = len(lang_sensors[lang])
    print(f"{lang.upper()}: {count} sensors")
