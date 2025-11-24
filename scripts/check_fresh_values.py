"""Check actual values in fresh testdata."""
from pathlib import Path
from bs4 import BeautifulSoup

def check_file(filename):
    html = Path(f'scripts/testdata/{filename}').read_text(encoding='utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    
    print(f"\n=== {filename} ===")
    
    # Find EFFIZIENZ/EFFICIENCY section - show ALL rows in that table
    in_efficiency = False
    for table in soup.find_all('table'):
        table_text = table.get_text()
        if 'EFFIZIENZ' in table_text or 'EFFICIENCY' in table_text:
            in_efficiency = True
            print("  EFFICIENCY TABLE:")
            for row in table.find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    # Check if it's a value cell (has class="value")
                    is_value = 'value' in cells[1].get('class', [])
                    print(f"    {label}: {value} {'(class=value)' if is_value else ''}")
    
    # Also check process values
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 2:
            label = cells[0].get_text(strip=True)
            value = cells[1].get_text(strip=True)
            
            if 'VERDAMPFER' in label or 'EVAPORATOR' in label:
                if 'AUSTRITT' in label or 'OUTLET' in label:
                    is_value = 'value' in cells[1].get('class', [])
                    print(f"  {label}: {value} {'(class=value)' if is_value else ''}")

# Check the files that failed tests
check_file('s_1_8_de.html')
check_file('s_1_8_en.html')
check_file('s_1_1_de.html')
check_file('s_1_1_en.html')
