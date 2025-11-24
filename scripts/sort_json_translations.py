#!/usr/bin/env python3
"""Sort sensors in translation JSON files alphabetically."""

import json
from pathlib import Path
from collections import OrderedDict


def sort_json_sensors(json_path: Path):
    """Sort the sensors in a translation JSON file alphabetically."""
    # Read the JSON file
    data = json.loads(json_path.read_text(encoding='utf-8'))
    
    # Sort the sensors
    if 'entity' in data and 'sensor' in data['entity']:
        sensors = data['entity']['sensor']
        sorted_sensors = OrderedDict(sorted(sensors.items()))
        data['entity']['sensor'] = sorted_sensors
    
    # Sort binary_sensors too if present
    if 'entity' in data and 'binary_sensor' in data['entity']:
        binary_sensors = data['entity']['binary_sensor']
        sorted_binary = OrderedDict(sorted(binary_sensors.items()))
        data['entity']['binary_sensor'] = sorted_binary
    
    # Write back with nice formatting
    json_path.write_text(
        json.dumps(data, indent=4, ensure_ascii=False) + '\n',
        encoding='utf-8'
    )
    
    return len(data.get('entity', {}).get('sensor', {}))


def main():
    """Sort all translation JSON files."""
    translations_dir = Path('custom_components/stiebel_eltron_http/translations')
    
    print("\n" + "="*70)
    print("SORTING TRANSLATION JSON FILES")
    print("="*70 + "\n")
    
    json_files = sorted(translations_dir.glob('*.json'))
    
    for json_file in json_files:
        sensor_count = sort_json_sensors(json_file)
        print(f"✓ Sorted {json_file.name}: {sensor_count} sensors")
    
    print("\n" + "="*70)
    print(f"COMPLETE: Sorted {len(json_files)} translation files")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
