#!/usr/bin/env python3
"""Check if any language has duplicate sensor names (same word used for different sensors).

If duplicates exist, we need to prefix with section name to disambiguate.
"""

import json
from pathlib import Path
from collections import Counter

TRANSLATIONS_DIR = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "translations"

def check_duplicates(lang: str):
    """Check for duplicate sensor names in a language."""
    json_file = TRANSLATIONS_DIR / f"{lang}.json"
    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)
    
    sensors = data.get('entity', {}).get('sensor', {})
    
    # Get all sensor names (values)
    sensor_names = [info.get('name', '') for info in sensors.values()]
    
    # Find duplicates
    name_counts = Counter(sensor_names)
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    
    if duplicates:
        print(f"\n{lang.upper()}: Found {len(duplicates)} duplicate sensor names:")
        for name, count in duplicates.items():
            print(f"  '{name}' appears {count} times")
            # Find which sensors use this name
            matching_sensors = [key for key, info in sensors.items() if info.get('name', '') == name]
            for sensor_key in matching_sensors:
                print(f"    - {sensor_key}")
    else:
        print(f"{lang.upper()}: No duplicates ✓")

def main():
    langs = ['cs', 'da', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']
    
    print("=" * 100)
    print("CHECKING FOR DUPLICATE SENSOR NAMES")
    print("=" * 100)
    
    for lang in langs:
        check_duplicates(lang)

if __name__ == '__main__':
    main()
