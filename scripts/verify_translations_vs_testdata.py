#!/usr/bin/env python3
"""Verify that all translations in JSON files match actual test data fields."""

import json
from pathlib import Path
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).parent
TESTDATA_DIR = SCRIPT_DIR / "testdata"
TRANSLATIONS_DIR = SCRIPT_DIR.parent / "custom_components" / "stiebel_eltron_http" / "translations"

def get_all_fields_from_testdata(lang):
    """Extract all field names from all test data pages for a language."""
    all_fields = set()
    
    pages = ['s_1_0', 's_1_1', 's_1_8', 's_2_7']
    
    for page in pages:
        html_file = TESTDATA_DIR / f"{page}_{lang}.html"
        if html_file.exists():
            soup = BeautifulSoup(html_file.open(encoding='utf-8'), 'html.parser')
            keys = soup.find_all('td', class_='key')
            for key in keys:
                field_name = key.get_text(strip=True)
                if field_name:
                    all_fields.add(field_name)
    
    return all_fields

def main():
    """Check all languages."""
    langs = ['cs', 'da', 'es', 'fi', 'fr', 'hu', 'it', 'nl', 'pl', 'sv']
    
    # Sensors to skip (not in test data as confirmed by user)
    skip_sensors = {'room_temperature', 'room_humidity'}
    
    print("=" * 80)
    print("VERIFYING TRANSLATIONS AGAINST TEST DATA")
    print("=" * 80)
    
    for lang in langs:
        print(f"\n{lang.upper()}:")
        
        # Load JSON translations
        json_file = TRANSLATIONS_DIR / f"{lang}.json"
        if not json_file.exists():
            print(f"  ⚠ Translation file not found")
            continue
        
        json_data = json.load(json_file.open(encoding='utf-8'))
        sensors = json_data.get('entity', {}).get('sensor', {})
        
        # Get all fields from test data
        testdata_fields = get_all_fields_from_testdata(lang)
        
        # Check each sensor translation
        mismatches = []
        matched = 0
        
        for sensor_key, sensor_data in sensors.items():
            if sensor_key in skip_sensors:
                continue
            
            translation = sensor_data.get('name', '')
            
            # Check if translation exists in test data
            if translation and translation not in testdata_fields:
                mismatches.append(f"    ERROR {sensor_key}: '{translation}' NOT in test data")
            elif translation:
                matched += 1
        
        print(f"  OK Matched: {matched} translations found in test data")
        
        if mismatches:
            print(f"  WARNING Issues found ({len(mismatches)}):")
            for mismatch in mismatches[:10]:  # Show first 10
                try:
                    print(mismatch)
                except UnicodeEncodeError:
                    # If print fails, encode to ASCII with replacement
                    print(mismatch.encode('ascii', 'replace').decode('ascii'))
            if len(mismatches) > 10:
                print(f"    ... and {len(mismatches) - 10} more")
        else:
            print(f"  SUCCESS All translations match test data!")
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
