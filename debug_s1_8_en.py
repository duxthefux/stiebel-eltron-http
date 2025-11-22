#!/usr/bin/env python3
"""Debug English s_1_8 parsing."""

import importlib.util
import sys
from pathlib import Path
from bs4 import BeautifulSoup


def _load_module_from_path(module_name: str, path: Path):
    if module_name in sys.modules:
        return sys.modules[module_name]
    
    spec = importlib.util.spec_from_file_location(module_name, str(path))
    module = importlib.util.module_from_spec(spec)
    parent = module_name.rpartition(".")[0]
    module.__package__ = parent
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# Load parsing module
root = Path("custom_components/stiebel_eltron_http")
parsing = _load_module_from_path("custom_components.stiebel_eltron_http.parsing", root / "parsing.py")

# Load English testdata
html_path = Path('scripts/testdata/s_1_8_en.html')
html = html_path.read_text(encoding='utf-8')
soup = BeautifulSoup(html, 'html.parser')

tables = soup.find_all('table')
print(f"\nFound {len(tables)} tables\n")

for idx, table in enumerate(tables, start=1):
    rows = table.find_all('tr')
    if not rows:
        continue
    
    headers = rows[0].find_all(['th'])
    section_title = headers[0].get_text(strip=True) if headers else ""
    
    print(f"{'='*60}")
    print(f"Table {idx}: {section_title}")
    print(f"{'='*60}")
    
    # Try amount_power parsing
    print("\nTrying parse_amount_power_table:")
    try:
        result = parsing.parse_amount_power_table(table)
        for key, value in result.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Try efficiency parsing
    print("\nTrying parse_efficiency_table:")
    try:
        result = parsing.parse_efficiency_table(table)
        for key, value in result.items():
            print(f"  {key}: {value}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print()
