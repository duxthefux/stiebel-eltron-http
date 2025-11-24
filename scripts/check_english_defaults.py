#!/usr/bin/env python3
"""Check for English default labels in non-English translation files."""

import json
from pathlib import Path

TRANSLATIONS_DIR = Path("custom_components/stiebel_eltron_http/translations")
LANGUAGES = ["cs", "da", "es", "fi", "fr", "hu", "it", "nl", "pl", "sv"]

# Load English translations as reference
en_file = TRANSLATIONS_DIR / "en.json"
with open(en_file, 'r', encoding='utf-8') as f:
    en_data = json.load(f)

en_sensors = en_data.get('entity', {}).get('sensor', {})

print("Checking for English default labels in non-English translations:")
print("=" * 80)

for lang in LANGUAGES:
    lang_file = TRANSLATIONS_DIR / f"{lang}.json"
    
    if not lang_file.exists():
        continue
    
    with open(lang_file, 'r', encoding='utf-8') as f:
        lang_data = json.load(f)
    
    lang_sensors = lang_data.get('entity', {}).get('sensor', {})
    
    english_labels = []
    
    for sensor_key, sensor_data in lang_sensors.items():
        lang_name = sensor_data.get('name', '')
        
        # Check if this sensor exists in English
        if sensor_key in en_sensors:
            en_name = en_sensors[sensor_key].get('name', '')
            
            # If the translation is identical to English, it's probably a default
            if lang_name == en_name:
                english_labels.append(f"  {sensor_key}: \"{lang_name}\"")
    
    if english_labels:
        print(f"\n{lang.upper()}: {len(english_labels)} English labels found:")
        for label in english_labels[:10]:  # Show first 10
            print(label)
        if len(english_labels) > 10:
            print(f"  ... and {len(english_labels) - 10} more")
    else:
        print(f"\n{lang.upper()}: ✓ All labels translated")

print("\n" + "=" * 80)
