"""Extract all field names for the newly added canonical keys from test data."""
import bs4
from pathlib import Path

# Fields we need to find translations for
fields_to_find = {
    # From HEATING section (s_1_0)
    'TARGET_TEMPERATURE_HK1': ('SET', 'TEMP', 'HK', '1'),
    'ACTUAL_TEMPERATURE_HK1': ('ACTUAL', 'TEMP', 'HK', '1'),
    'TARGET_TEMPERATURE_DHW': ('SET', 'TEMP'),  # In DHW section
    
    # From ELECTRIC REHEATING section (s_1_0) - already have these
    # 'BIVALENCE_TEMPERATURE_HEATING': already complete
    # 'BIVALENCE_TEMPERATURE_DHW': already complete
    # 'LOWER_LIMIT_HEATING': already complete
    # 'LOWER_LIMIT_DHW': already complete
    
    # From RUNTIME section (s_1_1)
    'RUNTIME_COMPRESSOR_HEATING': ('VD', 'HEAT'),
    'RUNTIME_COMPRESSOR_DHW': ('VD', 'WARM', 'WATER'),
    'RUNTIME_COMPRESSOR_DEFROST': ('VD', 'DEFROST'),
    'RUNTIME_SUPPLEMENTARY_HEATER_1': ('NHZ', '1'),
    'RUNTIME_SUPPLEMENTARY_HEATER_2': ('NHZ', '2'),
    'RUNTIME_SUPPLEMENTARY_HEATER_TOTAL': ('NHZ', '1/2'),
    'DEFROST_TIME': ('TIME', 'DEFROST'),
    'DEFROST_STARTS': ('STARTS', 'DEFROST'),
    
    # From STARTS section (s_1_1)
    'COMPRESSOR_STARTS': ('COMPRESSOR',),  # or 'VERDICHTER'
    
    # From diagnostic page (s_2_7)
    'HEAT_PUMP_TYPE': ('WP-TYP', 'HP TYPE'),
    'HEAT_PUMP_ID': ('HP-ID',),
    'PARAMETER_SET': ('PARAMETERSATZ', 'PARAMETER SET'),
}

langs = ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']

def extract_from_s_1_0_heating(lang):
    """Extract HK1 temperatures from HEATING section."""
    file_path = Path(f'scripts/testdata/s_1_0_{lang}.html')
    if not file_path.exists():
        return {}
    
    text = file_path.read_text(encoding='utf-8')
    soup = bs4.BeautifulSoup(text, 'html.parser')
    results = {}
    
    # Find HEATING section
    for table in soup.find_all('table'):
        header = table.find('th')
        if not header:
            continue
        
        header_text = header.get_text(strip=True).upper()
        
        if any(kw in header_text for kw in ['HEIZUNG', 'HEATING', 'CHAUFFAGE', 'VERWARMING', 
                                              'RISCALDAMENTO', 'UPPVÄRMNING', 'CALEFACCIÓN',
                                              'OGRZEWANIE', 'TOPENI', 'FÛTÉS', 'LÄMMITYS', 'VARME']):
            rows = table.find_all('tr')
            for row in rows:
                key_td = row.find('td', class_='key')
                if not key_td:
                    continue
                
                key_text = key_td.get_text(strip=True)
                key_upper = key_text.upper()
                
                # TARGET_TEMPERATURE_HK1
                if ('HK' in key_upper or 'CC' in key_upper or 'VK' in key_upper or 'FK' in key_upper or 'LK' in key_upper or 'OK' in key_upper or 'UK' in key_upper) and '1' in key_text:
                    if any(word in key_upper for word in ['SET', 'SOLL', 'TARGET', 'CONSIGNE', 'GEVRAAGD', 'REGOLAZIONE', 'BÖRVÄRDE', 'MÅLVÄRDE', 'CONSIGNA', 'ZADANA', 'POŽADOVANÁ', 'BEÁLLÍTOTT', 'ASETUSARVO', 'ØNSKET', 'INDST']):
                        if 'TEMP' in key_upper or 'HÕMÉRS' in key_upper or 'LÄMPÖT' in key_upper:
                            results['TARGET_TEMPERATURE_HK1'] = key_text
                
                # ACTUAL_TEMPERATURE_HK1
                if ('HK' in key_upper or 'CC' in key_upper or 'VK' in key_upper or 'FK' in key_upper or 'LK' in key_upper or 'OK' in key_upper or 'UK' in key_upper) and '1' in key_text:
                    if any(word in key_upper for word in ['ACTUAL', 'IST', 'REELLE', 'REELL', 'ACTUELE', 'WERKELIJKE', 'EFFETTIVA', 'REALE', 'VERKLIG', 'AKT', 'REAL', 'RZECZYWISTA', 'SKUTECNA', 'TÉNYLEGES', 'TOT', 'FAKTISK']):
                        if 'TEMP' in key_upper or 'HÕMÉRS' in key_upper or 'LÄMPÖT' in key_upper or 'ARVO' in key_upper:
                            results['ACTUAL_TEMPERATURE_HK1'] = key_text
            break
    
    return results

def extract_from_s_1_0_dhw(lang):
    """Extract DHW target temperature from DHW section."""
    file_path = Path(f'scripts/testdata/s_1_0_{lang}.html')
    if not file_path.exists():
        return {}
    
    text = file_path.read_text(encoding='utf-8')
    soup = bs4.BeautifulSoup(text, 'html.parser')
    results = {}
    
    # Find DHW section
    for table in soup.find_all('table'):
        header = table.find('th')
        if not header:
            continue
        
        header_text = header.get_text(strip=True).upper()
        
        if any(kw in header_text for kw in ['WARMWASSER', 'DHW', 'WARM WATER', 'EAU CHAUDE', 'ECS', 
                                              'ACQUA CALDA', 'VARMVATTEN', 'AGUA CALIENTE', 
                                              'CIEPLA WODA', 'TEPLA VODA', 'MELEGVÍZ', 'LÄMMINVESI', 
                                              'VARMT VAND']):
            rows = table.find_all('tr')
            for row in rows:
                key_td = row.find('td', class_='key')
                if not key_td:
                    continue
                
                key_text = key_td.get_text(strip=True)
                key_upper = key_text.upper()
                
                # TARGET_TEMPERATURE_DHW - usually just "SET TEMPERATURE" or "SOLLTEMPERATUR" in DHW section
                if any(word in key_upper for word in ['SET', 'SOLL', 'TARGET', 'CONSIGNE', 'GEVRAAGD', 'REGOLAZIONE', 'BÖRVÄRDE', 'CONSIGNA', 'ZADANA', 'POŽADOVANÁ', 'BEÁLLÍTOTT', 'ASETUSARVO', 'ØNSKET']):
                    if 'TEMP' in key_upper or 'HÕMÉRS' in key_upper or 'LÄMPÖT' in key_upper:
                        # Make sure it doesn't have HK in it (that would be heating circuit)
                        if 'HK' not in key_upper and 'CC' not in key_upper and 'VK' not in key_upper:
                            results['TARGET_TEMPERATURE_DHW'] = key_text
            break
    
    return results

print("=" * 80)
print("HEATING SECTION FIELDS (s_1_0)")
print("=" * 80)

all_results = {}
for lang in langs:
    heating_results = extract_from_s_1_0_heating(lang)
    dhw_results = extract_from_s_1_0_dhw(lang)
    
    combined = {**heating_results, **dhw_results}
    all_results[lang] = combined
    
    if combined:
        print(f"\n{lang}:")
        for field, value in combined.items():
            print(f"  {field}: {value}")

# Print as Python dictionary format for easy copy-paste
print("\n" + "=" * 80)
print("FORMATTED FOR HEADER_ALIASES:")
print("=" * 80)

fields = ['TARGET_TEMPERATURE_HK1', 'ACTUAL_TEMPERATURE_HK1', 'TARGET_TEMPERATURE_DHW']
for field in fields:
    print(f"\nCanonicalKey.{field}: [")
    for lang in langs:
        if field in all_results.get(lang, {}):
            value = all_results[lang][field]
            print(f'    "{value}",  # {lang}')
    print("],")
