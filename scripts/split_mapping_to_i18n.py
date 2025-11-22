"""Split mapping.py into i18n package with one file per language."""

import re
from pathlib import Path
from collections import defaultdict

# Language detection patterns
LANG_PATTERNS = {
    'de': ['TEMPERATUR', 'HEIZUNG', 'PROZESS', 'VERBRAUCH', 'EFFIZIENZ', 'RÜCKLAUF', 'VORLAUF', 'FROSTSCHUTZ', 'AUSSENTEMPERATUR', 'WARMWASSER', 'BETRIEBSART'],
    'en': ['TEMPERATURE', 'HEATING', 'PROCESS', 'CONSUMPTION', 'EFFICIENCY', 'RETURN', 'SUPPLY', 'FROST PROTECTION', 'OUTSIDE', 'DHW', 'HOT WATER'],
    'fr': ['TEMPÉRATURE', 'TEMP.', 'CHAUFFAGE', 'PROCESSUS', 'CONSOMMATION', 'EFFICACITÉ', 'RETOUR', 'DEPART', 'HORS GEL', 'ECS'],
    'nl': ['TEMPERATUUR', 'VERWARMING', 'PROCES', 'VERBRUIK', 'EFFICIENTIE', 'RETOUR', 'AANVOER', 'VORSTBEVEILIGING', 'BUITEN', 'WARM WATER'],
    'it': ['TEMPERATURA', 'RISCALDAMENTO', 'PROCESSO', 'CONSUMO', 'EFFICIENZA', 'RITORNO', 'MANDATA', 'ANTIGELO', 'ESTERNA', 'ACQUA CALDA'],
    'sv': ['TEMPERATUR', 'UPPVÄRMNING', 'PROCESS', 'FÖRBRUKNING', 'VERKNINGSGRAD', 'RETUR', 'FRAM', 'FROSTSKYDD', 'UTE'],
    'es': ['TEMPERATURA', 'CALEFACCIÓN', 'PROCESO', 'CONSUMO', 'EFICIENCIA', 'RETORNO', 'IMPULSIÓN', 'PROTECCIÓN ANTICONGELANTE', 'EXTERIOR', 'ACS'],
    'pl': ['TEMPERATURA', 'OGRZEWANIE', 'PROCES', 'POBOR', 'ZUŻYCIE', 'SPRAWNOŚĆ', 'POWRÓT', 'ZASILANIE', 'ZABEZPIECZENIE', 'ZEWNĘTRZNA'],
    'cs': ['TEPLOTA', 'TOPENI', 'PROCES', 'PŘÍKON', 'SPOTŘEBA', 'ÚČINNOST', 'ZPĚTNÁ', 'VÝSTUPNÍ', 'OCHRANA', 'VENKOVNÍ'],
    'hu': ['HŐMÉRSÉKLET', 'FŰTÉS', 'FOLYAMAT', 'TELJESÍTMÉNY', 'FOGYASZTÁS', 'HATÉKONYSÁG', 'VISSZATÉRŐ', 'ELŐREMENŐ', 'FAGYVÉDELEM', 'KÜLSŐ'],
    'fi': ['LÄMPÖTILA', 'LÄMMITYS', 'PROSESSI', 'KULUTUS', 'HYÖTYSUHDE', 'PALUU', 'MENO', 'PAKKASSUOJA', 'ULKO'],
    'da': ['TEMPERATUR', 'VARME', 'PROCES', 'FORBRUG', 'EFFEKTIVITET', 'RETUR', 'FREMLØB', 'FROSTVERN', 'UDE'],
}

def detect_language(text):
    """Detect language of a translation string."""
    text_upper = text.upper()
    
    # Check for exact matches first
    scores = defaultdict(int)
    for lang, patterns in LANG_PATTERNS.items():
        for pattern in patterns:
            if pattern in text_upper:
                scores[lang] += len(pattern)
    
    if scores:
        return max(scores, key=scores.get)
    
    # Fallback heuristics
    if any(c in text for c in 'ÄÖÜß'):
        return 'de'
    elif 'É' in text or 'È' in text or "D'" in text or "L'" in text:
        return 'fr'
    elif 'Ñ' in text or 'Á' in text:
        return 'es'
    elif 'Ø' in text or 'Å' in text:
        if 'Æ' in text:
            return 'da'
        return 'sv'
    elif 'Ł' in text or 'Ś' in text or 'Ź' in text or 'Ż' in text:
        return 'pl'
    elif 'Č' in text or 'Ř' in text or 'Ž' in text:
        return 'cs'
    elif 'Ő' in text or 'Ű' in text:
        return 'hu'
    elif 'Ä' in text and 'Ö' in text:
        return 'fi'
    
    return 'en'  # default

def parse_mapping_file():
    """Parse mapping.py and extract header aliases by language."""
    mapping_path = Path(__file__).parent.parent / 'custom_components' / 'stiebel_eltron_http' / 'mapping.py'
    
    with open(mapping_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the HEADER_ALIASES dictionary
    match = re.search(r'HEADER_ALIASES:.*?= \{(.*?)\n\}', content, re.DOTALL)
    if not match:
        raise ValueError("Could not find HEADER_ALIASES in mapping.py")
    
    aliases_content = match.group(1)
    
    # Parse each CanonicalKey entry
    language_translations = defaultdict(lambda: defaultdict(list))
    
    # Find each CanonicalKey entry
    key_pattern = r'CanonicalKey\.(\w+):\s*\[(.*?)\]'
    for key_match in re.finditer(key_pattern, aliases_content, re.DOTALL):
        canonical_key = key_match.group(1)
        values_str = key_match.group(2)
        
        # Extract each quoted string
        value_pattern = r'"([^"]+)"'
        for value_match in re.finditer(value_pattern, values_str):
            translation = value_match.group(1)
            
            # Detect language
            lang = detect_language(translation)
            language_translations[lang][canonical_key].append(translation)
    
    return language_translations

def main():
    """Main execution."""
    translations = parse_mapping_file()
    
    print("Detected languages and translation counts:")
    for lang in sorted(translations.keys()):
        total_translations = sum(len(v) for v in translations[lang].values())
        print(f"  {lang}: {total_translations} translations across {len(translations[lang])} keys")

if __name__ == '__main__':
    main()
