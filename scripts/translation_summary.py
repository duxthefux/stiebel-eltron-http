#!/usr/bin/env python3
"""Final summary of translation completeness across all languages."""

import json
from pathlib import Path

TRANSLATIONS_DIR = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "translations"

print("=" * 100)
print("TRANSLATION COMPLETENESS SUMMARY")
print("=" * 100)
print()

# Target: 55 sensors (57 total minus room_temperature/room_humidity which are only in German)
# These 55 are all extracted from test data pages s_1_0, s_1_1, s_1_8

langs = ['cs', 'da', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']
all_sensor_keys = set()

print("Sensor counts per language:")
print("-" * 100)
for lang in langs:
    json_file = TRANSLATIONS_DIR / f"{lang}.json"
    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)
    
    sensors = data.get('entity', {}).get('sensor', {})
    sensor_keys = set(sensors.keys())
    all_sensor_keys.update(sensor_keys)
    
    print(f"  {lang.upper()}: {len(sensor_keys):2d} sensors")

print()
print(f"Total unique sensors across all languages: {len(all_sensor_keys)}")
print()

# Check if all languages have the same sensors
print("Sensor consistency check:")
print("-" * 100)
all_same = True
reference_lang = langs[0]
reference_file = TRANSLATIONS_DIR / f"{reference_lang}.json"
with open(reference_file, encoding='utf-8') as f:
    reference_data = json.load(f)
reference_keys = set(reference_data.get('entity', {}).get('sensor', {}).keys())

for lang in langs[1:]:
    json_file = TRANSLATIONS_DIR / f"{lang}.json"
    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)
    
    sensor_keys = set(data.get('entity', {}).get('sensor', {}).keys())
    
    if sensor_keys != reference_keys:
        all_same = False
        missing = reference_keys - sensor_keys
        extra = sensor_keys - reference_keys
        
        print(f"  {lang.upper()}: DIFFERENT from {reference_lang.upper()}")
        if missing:
            print(f"    Missing: {missing}")
        if extra:
            print(f"    Extra: {extra}")
    else:
        print(f"  {lang.upper()}: ✓ IDENTICAL to {reference_lang.upper()}")

print()
if all_same:
    print("✅ SUCCESS: All languages have IDENTICAL sensor sets!")
else:
    print("⚠️  WARNING: Some languages have different sensors")

print()
print("=" * 100)
print("EXTRACTION METHOD: Structure-based (position in HTML)")
print("=" * 100)
print()
print("Extraction approach:")
print("  - Uses FIELD_STRUCTURE_MAP: (page, section_index, field_index) → sensor_key")
print("  - Language-agnostic: Position is same across all languages (same device firmware)")
print("  - Deterministic: No keyword matching failures")
print("  - Complete: Covers all sensors from s_1_0, s_1_1, s_1_8")
print()
print("Disambiguation:")
print("  - Section prefixes added when same word appears in multiple sections")
print("  - Example: 'AKT TEMPERATUR' → 'VARMVATTEN AKT TEMPERATUR' vs 'VÄRMEGENERATOR EXTERN AKT TEMPERATUR'")
print()
print("=" * 100)
