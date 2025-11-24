"""Script to add HK and buffer field translations to all language i18n files."""

from pathlib import Path

# Field mappings from testdata analysis
field_mappings = {
    'fr': {
        'hk1_actual': 'TEMP. ACTUELLE CC1',
        'hk1_set': 'CONSIGNE TEMP. CC1',
        'hk2_actual': 'TEMP. ACTUELLE CC2',
        'hk2_set': 'CONSIGNE TEMP. CC2',
        'buffer_actual': 'TEMP EFFECTIVE BALLON',
        'buffer_set': 'CONSIGNE TEMP. BALLON',
    },
    'nl': {
        'hk1_actual': 'ACTUELE TEMPERATUUR HK 1',
        'hk1_set': 'GEVRAAGDE TEMP. HK 1',
        'hk2_actual': 'ACTUELE TEMPERATUUR HK 2',
        'hk2_set': 'GEVRAAGDE TEMP. HK 2',
        'buffer_actual': 'WERKELIJKE TEMP. BUFFER',
        'buffer_set': 'GEVRAAGDE TEMP. BUFFER',
    },
    'it': {
        'hk1_actual': 'TEMP EFFETTIVA HK 1',
        'hk1_set': 'TEMP NOMINALE HK 1',
        'hk2_actual': 'TEMP EFFETTIVA HK 2',
        'hk2_set': 'TEMP NOMINALE HK 2',
        'buffer_actual': 'TEMP EFF TAMPONE',
        'buffer_set': 'TEMP NOM TAMPONE',
    },
    'sv': {
        'hk1_actual': 'AKT TEMPERATUR HK 1',
        'hk1_set': 'BÖRTEMPERATUR HK 1',
        'hk2_actual': 'AKT TEMPERATUR HK 2',
        'hk2_set': 'BÖRTEMPERATUR HK 2',
        'buffer_actual': 'AKT BUFFERTTEMPERATUR',
        'buffer_set': 'BÖRTEMP BUFFER',
    },
    'es': {
        'hk1_actual': 'TEMPERATURA REAL HK 1',
        'hk1_set': 'TEMPERATURA DE REF. HK 1',
        'hk2_actual': 'TEMPERATURA REAL HK 2',
        'hk2_set': 'TEMPERATURA DE REF. HK 2',
        'buffer_actual': 'TEMP. REAL ACUMULADOR',
        'buffer_set': 'TEMP. DE REF. ACUMULADOR',
    },
    'pl': {
        'hk1_actual': 'TEMP RZECZYWISTA HK 1',
        'hk1_set': 'TEMPERATURA ZADANA HK 1',
        'hk2_actual': 'TEMP RZECZYWISTA HK 2',
        'hk2_set': 'TEMPERATURA ZADANA HK 2',
        'buffer_actual': 'TEMP RZECZYWISTA BUFOR',
        'buffer_set': 'TEMP ZADANA BUFOR',
    },
    'cs': {
        'hk1_actual': 'SKUTECNA TEPLOTA HK 1',
        'hk1_set': 'POZADOVANA TEPLOTA HK 1',
        'hk2_actual': 'SKUTECNA TEPLOTA HK 2',
        'hk2_set': 'POZADOVANA TEPLOTA HK 2',
        'buffer_actual': 'SKUTECNA TEPLOTA ZÁSOBNÍK',
        'buffer_set': 'POZADOVANA TEPLOTA ZÁSOBNÍK',
    },
    'hu': {
        'hk1_actual': 'TÉNYLEGES HÕMÉRSÉKLET HK 1',
        'hk1_set': 'NÉVL. HÕMÉRS. HK 1',
        'hk2_actual': 'TÉNYLEGES HÕMÉRSÉKLET HK 2',
        'hk2_set': 'NÉVL. HÕMÉRS. HK 2',
        'buffer_actual': 'TÉNYLEGES HÕMÉRSÉKLET PUFFER',
        'buffer_set': 'NÉVL. HÕMÉRS. PUFFER',
    },
    'fi': {
        'hk1_actual': 'TOSILÄMPÖT HK 1',
        'hk1_set': 'OHJELÄMPÖT HK 1',
        'hk2_actual': 'TOSILÄMPÖT HK 2',
        'hk2_set': 'OHJELÄMPÖT HK 2',
        'buffer_actual': 'TOSILÄMPÖT PUSKURI',
        'buffer_set': 'OHJELÄMPÖT PUSKURI',
    },
    'da': {
        'hk1_actual': 'AKTUEL TEMPERATUR HK 1',
        'hk1_set': 'INDST. TEMPERATUR HK 1',
        'hk2_actual': 'AKTUEL TEMPERATUR HK 2',
        'hk2_set': 'INDST. TEMPERATUR HK 2',
        'buffer_actual': 'AKTUEL TEMP. BUFFER',
        'buffer_set': 'INDST. TEMP. BUFFER',
    },
}

for lang, fields in field_mappings.items():
    print(f"\n{lang.upper()}:")
    print(f"    CanonicalKey.ACTUAL_TEMPERATURE_HK_1: [")
    print(f"        \"{fields['hk1_actual']}\",")
    print(f"    ],")
    print(f"    CanonicalKey.SET_TEMPERATURE_HK_1: [")
    print(f"        \"{fields['hk1_set']}\",")
    print(f"    ],")
    print(f"    CanonicalKey.ACTUAL_TEMPERATURE_HK_2: [")
    print(f"        \"{fields['hk2_actual']}\",")
    print(f"    ],")
    print(f"    CanonicalKey.SET_TEMPERATURE_HK_2: [")
    print(f"        \"{fields['hk2_set']}\",")
    print(f"    ],")
    print(f"    CanonicalKey.ACTUAL_BUFFER_TEMPERATURE: [")
    print(f"        \"{fields['buffer_actual']}\",")
    print(f"    ],")
    print(f"    CanonicalKey.SET_BUFFER_TEMPERATURE: [")
    print(f"        \"{fields['buffer_set']}\",")
    print(f"    ],")
