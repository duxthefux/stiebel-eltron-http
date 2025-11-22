"""Map section headers to language codes based on actual test data."""
from bs4 import BeautifulSoup
from pathlib import Path

sections_map = {
    'HEATING_SECTION': {},
    'DHW_SECTION': {},
    'PROCESS_DATA_SECTION': {},
    'EFFICIENCY_SECTION': {},
    'POWER_CONSUMPTION_SECTION': {},
    'AMOUNT_OF_HEAT_SECTION': {},
    'RUNTIME_SECTION': {},
}

# Keywords to identify each section type
section_keywords = {
    'HEATING_SECTION': ['HEATING', 'HEIZUNG', 'CHAUFFAGE', 'VERWARMING', 'RISCALDAMENTO', 'UPPVÄRMNING', 'CALEFACCIÓN', 'OGRZEWANIE', 'TOPENI', 'FÛTÉS', 'LÄMMITYS', 'VARME'],
    'DHW_SECTION': ['DHW', 'WARMWASSER', 'EAU CHAUDE', 'WARM WATER', 'ACQUA CALDA', 'VARMVATTEN', 'AGUA CALIENTE', 'CIEPLA WODA', 'TEPLA VODA', 'MELEGVÍZ', 'LÄMMINVESI', 'VARMT VAND'],
    'PROCESS_DATA_SECTION': ['PROCESS DATA', 'PROZESSDATEN', 'DONNEES PROCESS', 'PROCESGEGEVENS', 'DATI PROCESSO', 'PROCESSDATA', 'DATOS DE PROCESO', 'DANE PROCESU', 'PROCESNI DATA', 'FOLYAMATADATOK', 'PROSESSITIEDOT', 'PROCESDATA'],
    'EFFICIENCY_SECTION': ['EFFICIENCY', 'EFFIZIENZ', 'EFFICACITÉ', 'EFFICIËNTIE', 'EFFICIENZA', 'VERKNINGSGRAD', 'EFICIENCIA', 'EFEKTYWNOŚĆ', 'ÚČINNOST', 'HATÉKONYSÁG', 'TEHOKKUUS', 'EFFEKTIVITET'],
    'POWER_CONSUMPTION_SECTION': ['POWER CONSUMPTION', 'LEISTUNGSAUFNAHME', 'PUISSANCE ABSORBEE', 'VERBRUIK', 'POTENZA ASSORBITA', 'EFFEKTFÖRBRUKNING', 'CONSUMO ELÉCTRICO', 'POBOR MOCY', 'PRIKON', 'TELJESÍTMÉNYFELVETEL', 'TEHONKULUTUS', 'ENERGIFORBRUG'],
    'AMOUNT_OF_HEAT_SECTION': ['AMOUNT OF HEAT', 'WÄRMEMENGE', 'QUANTITE DE CHALEUR', 'WARMTEHOEVEELHEID', 'QUANTITÀ CALORE', 'VÄRMEMÄNGD', 'CAUDAL CALORÍFICO', 'ILOSC CIEPLA', 'MNOZSTVI TEPLA', 'HÕMENNYISÉG', 'LÄMPÖMÄÄRÄ', 'VARMEMÆNGDE'],
    'RUNTIME_SECTION': ['RUNTIME', 'LAUFZEIT', 'DURÉE FONCTIONNEMENT', 'LOOPTIJD', 'DURATA IN FUNZ', 'DRIFTTID', 'TIEMPO DE FUNCIONAMIENTO', 'CZAS PRACY', 'PROVOZNI DOBA', 'MÛKÖDÉSI IDÕ', 'KÄYNTIAIKA', 'DRIFTSTID'],
}

for html_file in sorted(Path('scripts/testdata').glob('s_1_*.html')):
    if html_file.stem.startswith('_'):
        continue
    
    lang = html_file.stem.split('_')[-1]
    soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), 'html.parser')
    
    # Get all table headers
    for th in soup.find_all('th'):
        text = th.get_text(strip=True)
        if not text or len(text) < 3:
            continue
            
        # Try to match to a section type (exact match only for better precision)
        for section_type, keywords in section_keywords.items():
            if text in keywords:
                sections_map[section_type][lang] = text
                break

# Print the exact mappings
print("EXACT SECTION HEADERS FROM TEST DATA:")
print("="*80)
for section_type in sorted(sections_map.keys()):
    print(f"\n{section_type}:")
    for lang in ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']:
        if lang in sections_map[section_type]:
            print(f'        "{sections_map[section_type][lang]}",  # {lang}')
