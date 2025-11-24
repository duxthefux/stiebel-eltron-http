#!/usr/bin/env python3
import json
from pathlib import Path

# Expected labels from s_0_0 extraction
expected = {
    'cs': 'Provozní režim',
    'da': 'Driftsmåde',
    'de': 'Betriebsart',
    'en': 'Operating mode',
    'es': 'Modo de servicio',
    'fi': 'Käyttötapa',
    'fr': 'Mode de fonctionnement',
    'hu': 'Üzemmód',
    'it': 'Modalità di esercizio',
    'nl': 'Bedrijfsmodus',
    'pl': 'Tryb pracy',
    'sv': 'Driftsläge'
}

print("Verifying start_operation_mode translations from s_0_0:")
print("=" * 70)

all_match = True
for lang, expected_label in expected.items():
    json_path = Path(f"custom_components/stiebel_eltron_http/translations/{lang}.json")
    
    if not json_path.exists():
        print(f"{lang.upper()}: ERROR - File not found")
        all_match = False
        continue
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    current = data.get('entity', {}).get('sensor', {}).get('start_operation_mode', {}).get('name', 'MISSING')
    
    if current == expected_label:
        print(f"{lang.upper()}: OK - \"{expected_label}\"")
    else:
        print(f"{lang.upper()}: MISMATCH")
        print(f"  Expected (from s_0_0): \"{expected_label}\"")
        print(f"  Current (in JSON):      \"{current}\"")
        all_match = False

print("=" * 70)
if all_match:
    print("RESULT: All s_0_0 translations are CORRECT!")
else:
    print("RESULT: Some translations need updating")
