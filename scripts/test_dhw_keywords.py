import re

heating_fields = {
    'nl': 'VERWARMEN 13-24 M',
    'it': 'RISCALDAMENTO 13-24 M',
    'da': 'VARME 13-24 M',
}

dhw_keywords = [
    "warm", "dhw", "warmwasser",
    "eau", "chaude", "sanitaire",
    "water",
    "acqua", "calda",
    "varm", "vatten",
    "agua", "caliente",
    "cwu", "wod",
    "voda", "tepl",
    "meleg", "víz", "viz",
    "lämmin", "vesi", "lammin",
    "vand",
]

for lang, text in heating_fields.items():
    nkey = re.sub(r'\s+', ' ', text).strip().lower()
    matches = [kw for kw in dhw_keywords if kw in nkey]
    print(f'{lang}: "{nkey}"')
    print(f'  Matches DHW keywords: {matches}')
    print(f'  Would be classified as: {"DHW" if matches else "HEATING"}')
    print()
