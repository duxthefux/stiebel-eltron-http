"""Extract German translations from mapping.py to i18n/de.py.

Uses a permissive approach:
1. Exclude all non-German languages explicitly
2. Accept anything with German words, ß, or umlauts (ä,ö,ü)
"""

import re
from pathlib import Path

def extract_german_translations():
    """Extract German translations from mapping.py."""
    mapping_path = Path(__file__).parent.parent / 'custom_components' / 'stiebel_eltron_http' / 'mapping.py'
    
    with open(mapping_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find HEADER_ALIASES dictionary
    match = re.search(r'HEADER_ALIASES:.*?= \{(.*?)\n\}', content, re.DOTALL)
    if not match:
        print("Could not find HEADER_ALIASES")
        return
    
    aliases_text = match.group(1)
    
    # Parse entries
    german_translations = {}
    
    # Find each CanonicalKey entry
    entries = re.finditer(r'CanonicalKey\.(\w+):\s*\[(.*?)\]', aliases_text, re.DOTALL)
    
    for entry in entries:
        key_name = entry.group(1)
        values_text = entry.group(2)
        
        # Extract quoted strings
        values = re.findall(r'"([^"]+)"', values_text)
        
        # Filter for German
        german_values = []
        for value in values:
            if is_german(value):
                german_values.append(value)
        
        if german_values:
            german_translations[key_name] = german_values
    
    return german_translations

def is_german(text: str) -> bool:
    """Check if text is likely German - PERMISSIVE approach.
    
    Strategy:
    1. Exclude non-German languages explicitly
    2. Accept anything with German indicators (words, ß, umlauts)
    """
    text_upper = text.upper()
    
    # Exclude non-German languages explicitly
    # Finnish indicators
    finnish = {
        'LÄMPÖ', 'LÄMMIN', 'LÄHTÖ', 'TULO', 'HÖYRYSTIMEN', 'HOYRYSTIMEN',
        'JÄNNITE', 'JÄÄTYMISENES', 'KÄYNTINOP', 'KÄYTTÖTAPA', 'LÄMPÖMÄÄRÄ',
        'TULOLÄMPÖTILA', 'LÄHTÖLÄMPÖTILA', 'KONDENS', 'KUUMAKAASULÄMPÖT',
        'KUUMAKAASU', 'ÖLJYSÄILIÖLÄMPÖT', 'ÖLJYKAMMION', 'ULKOLÄMPÖTILA',
        'PALUUVIRT', 'MENOVIRT', 'YHT', 'LÄMMINVESI', 'LÄMMINV', 'VIRTAAMA'
    }
    
    # Swedish indicators
    swedish = {
        'VÄRME', 'VARM', 'BÖRVARVTAL', 'KONDENSORTEMPERATUR', 'VÄRMEMÄNGD',
        'FLÄKTEFFEKT', 'HETGASTEMPERATUR', 'OLJESUMPTEMPERATUR', 'OLJESUMP',
        'UTETEMPERATUR', 'FRAMLEDNINGS', 'VARMEGASTEMPERATUR', 'TRYCK',
        'SPÄNNING', 'KOMPRESSORNS', 'KONDENSATOR', 'FROSTSKYDDSTEMPERATUR', 
        'SUMMA', 'RETURLEDNINGS'
    }
    
    # Danish/Norwegian indicators
    danish_norwegian = {
        'UDETEMPERATUR', 'FREMLØB', 'FREMLØBSTEMPERATUR', 'FREMLOBSTEMPERATUR',
        'FORDAMPER', 'OLIE', 'OLIESUMPFTEMPERATUR', 'OLIESUMPTEMPERATUR',
        'VANDVOLUMEN', 'AKTUEL'
    }
    
    # English indicators
    english = {
        'ACTUAL TEMPERATURE', 'COMPRESSOR INLET', 'CONDENSER TEMPERATURE',
        'EVAPORATOR', 'FROST PROTECTION', 'HOT GAS', 'INVERTER', 'OIL SUMP',
        'OUTSIDE TEMPERATURE', 'RETURN TEMPERATURE', 'SUPPLY TEMPERATURE',
        'FLOW TEMPERATURE', 'ROOM TEMPERATURE', 'WATER FLOW', 'AMBIENT',
        'INLET', 'OUTLET', 'VOLTAGE', 'CURRENT', 'PRESSURE', 'RELATIVE',
        'FAN POWER'
    }
    
    # Italian indicators
    italian = {
        'TEMPERATURA EFFETTIVA', 'TEMPERATURA INGRESSO', 'TEMPERATURA USCITA',
        'TEMPERATURA MANDATA', 'TEMPERATURA RITORNO', 'TEMPERATURA ESTERNA',
        'TEMPERATURA DEL', 'TEMPERATURA DI', 'COPPA OLIO', 'GAS CALDO'
    }
    
    # Spanish indicators  
    spanish = {
        'TEMPERATURA REAL', 'TEMPERATURA DE', 'COMPRESOR', 'EVAPORADOR',
        'EXTERIOR', 'RETORNO', 'SALIDA'
    }
    
    # Polish indicators
    polish = {
        'TEMPERATURA WLOTU', 'TEMPERATURA WYLOTU', 'SPREZARKI', 'SPRĘŻARKI',
        'PAROWNIKA', 'SKRAPLACZA', 'TEMPERATURA POWROTU', 'TEMPERATURA ZASILANIA',
        'TEMP RZECZYWISTA'
    }
    
    # French indicators
    french = {
        'TEMPERATURE REELLE', 'TEMPERATURE ENTREE', 'TEMPERATURE DEPART',
        'TEMPERATURE RETOUR', 'TEMPERATURE EXTERIEURE', 'CONDENSEUR',
        'COMPRESSEUR', 'GAZ CHAUDS', 'CARTER HUILE', 'DE DEPART', 'DE RETOUR'
    }
    
    # Czech/Hungarian indicators
    czech_hungarian = {
        'TEPLOTA', 'SKUTECNA', 'VSTUPNI', 'VYSTUPNI'
    }
    
    # Check exclusions
    all_exclusions = (finnish | swedish | danish_norwegian | english | 
                     italian | spanish | polish | french | czech_hungarian)
    
    if any(indicator in text_upper for indicator in all_exclusions):
        return False
    
    # Now identify German positively
    # German-specific words
    german_words = {
        'HEIZUNG', 'HEIZEN', 'PROZESS', 'WARMWASSER', 'TRINKWASSER', 'ISTTEMPERATUR',
        'SOLLTEMPERATUR', 'STROMVERBRAUCH', 'LEISTUNGSAUFNAHME', 'STROMBEZUG',
        'STROMERZEUGT', 'AUSSENTEMPERATUR', 'VORLAUFTEMPERATUR', 'RÜCKLAUFTEMPERATUR',
        'RUCKLAUFTEMPERATUR', 'HEIZKREIS', 'RAUMTEMPERATUR', 'RAUM', 'BETRIEBSART', 
        'VERDICHTER', 'VERDAMPFER', 'VERFLÜSSIGER', 'VERFLUESSIGERTEMPERATUR', 
        'HOCHDRUCK', 'NIEDERDRUCK', 'ÖLSUMPFTEMPERATUR', 'OELSUMPFTEMPERATUR', 
        'KONDENSATORTEMPERATUR', 'VENTILATORLEISTUNG', 'LUFTERLEISTUNG', 'LÜFTERLEISTUNG',
        'FROSTSCHUTZTEMPERATUR', 'HEISSGAS', 'SPANNUNG', 'STROM', 'VOLUMENSTROM', 
        'WÄRMEMENGE', 'WARMEMENGE', 'DURCHFLUSS', 'TAG', 'RELATIV', 'EINTRITTSTEMPERATUR', 
        'AUSTRITTSTEMPERATUR', 'EINTRITT', 'AUSTRITT', 'GESAMT', 'SUMME', 'DRUCK'
    }
    
    if any(word in text_upper for word in german_words):
        return True
    
    # ß is unique to German
    if 'ß' in text.lower():
        return True
    
    # If has German umlauts (ä, ö, ü) and passed exclusion filters, likely German
    if any(c in text.lower() for c in 'äöü'):
        return True
    
    return False

def generate_de_py(translations):
    """Generate the de.py file content."""
    lines = [
        '"""German (de) translations.',
        '',
        'Extracted from mapping.py HEADER_ALIASES.',
        '"""',
        '',
        'from .canonical_keys import CanonicalKey',
        '',
        '',
        'TRANSLATIONS: dict[CanonicalKey, list[str]] = {'
    ]
    
    for key_name in sorted(translations.keys()):
        values = translations[key_name]
        lines.append(f'    CanonicalKey.{key_name}: [')
        for value in values:
            # Escape quotes in the value
            escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
            lines.append(f'        "{escaped_value}",')
        lines.append('    ],')
    
    lines.append('}')
    
    return '\n'.join(lines)

if __name__ == '__main__':
    translations = extract_german_translations()
    
    if not translations:
        print("No German translations found!")
        exit(1)
    
    print(f"Found {len(translations)} keys with German translations")
    
    # Count total translations
    total = sum(len(v) for v in translations.values())
    print(f"Total: {total} German translations")
    
    # Generate file
    output_path = Path(__file__).parent.parent / 'custom_components' / 'stiebel_eltron_http' / 'i18n' / 'de.py'
    content = generate_de_py(translations)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Created: {output_path}")
