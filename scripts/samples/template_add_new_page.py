#!/usr/bin/env python3
"""Template for adding a new ISG page to the scraper.

This file shows the code changes needed in scraper.py when adding a new page.
Copy the relevant sections and customize for your specific page.

Usage:
    1. Review the sections below
    2. Copy to your scraper.py file
    3. Replace placeholders marked with ### USER: comments
    4. Update the structure-based extraction logic
"""

# =============================================================================
# STEP 1: Add page to fetch list (in async_fetch_data method)
# =============================================================================

async def async_fetch_data(self) -> dict[str, Any]:
    """Fetch data from all pages."""
    pages = [
        ("?s=1,0", self._extract_info_system),      # Start page
        ("?s=1,1", self._extract_info_heatpump),    # Heat pump page
        ("?s=1,8", self._extract_info_efficiency),  # Efficiency page
        ("?s=2,7", self._extract_info_diagnosis),   # Diagnosis/software page
        # ### USER: Add your new page here
        ("?s=1,9", self._extract_info_new_page),    # NEW PAGE - customize URL and method name
    ]


# =============================================================================
# STEP 2: Create extraction method
# =============================================================================

def _extract_info_new_page(self, html: str) -> dict[str, Any]:
    """Extract data from new page using structure-based mapping.
    
    ### USER: Update docstring with actual page name/description
    Example: Extract data from inverter page (s=1,9)
    """
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(html, "html.parser")
    data = {}
    sections = soup.find_all('table', class_='info')
    
    for section_idx, section in enumerate(sections):
        # Skip header row (first row with <th> or class="head")
        all_rows = section.find_all('tr')
        field_rows = [row for row in all_rows if not row.find('th')]
        
        for field_idx, row in enumerate(field_rows):
            cells = row.find_all('td')
            if len(cells) < 2:
                continue
            
            # Look up sensor key using structure map
            # ### USER: Update page name in map_key tuple
            map_key = ("s_1_9", section_idx, field_idx)  # Change "s_1_9" to your page
            sensor_key = FIELD_STRUCTURE_MAP.get(map_key)
            
            if sensor_key:
                value_text = cells[1].get_text(strip=True)
                # Parse value based on expected type
                value = self._parse_value(value_text, sensor_key)
                if value is not None:
                    data[sensor_key] = value
    
    return data


# =============================================================================
# STEP 3: Add structure mapping (in scripts/map_translations_structure_based.py)
# =============================================================================

FIELD_STRUCTURE_MAP = {
    # ... existing mappings ...
    
    # ============================================================================
    # ### USER: Update page identifier and description
    # s_1_9: Inverter power page
    # ============================================================================
    
    # ### USER: Add mappings for each field
    # Format: ('page_id', section_index, field_index): 'sensor_key'
    
    # Section 0: First section name
    ('s_1_9', 0, 0): 'new_sensor_1',  # First field in first section
    ('s_1_9', 0, 1): 'new_sensor_2',  # Second field in first section
    # ... add more fields from section 0
    
    # Section 1: Second section name  
    ('s_1_9', 1, 0): 'new_sensor_3',  # First field in second section
    # ... add more fields from section 1
    
    # ### USER: Continue for all sections and fields
}


# =============================================================================
# STEP 4: Add sensor keys to const.py
# =============================================================================

# ### USER: Add your sensor key constants to custom_components/stiebel_eltron_http/const.py

# Sensor keys for new page
NEW_SENSOR_1_KEY = "new_sensor_1"
NEW_SENSOR_2_KEY = "new_sensor_2"
NEW_SENSOR_3_KEY = "new_sensor_3"
# ... add all new sensor keys


# =============================================================================
# NOTES
# =============================================================================

"""
After adding the code above:

1. Extract translations using: 
   python scripts/samples/extract_with_section_prefixes.py s_1_9

2. Add translations to translations/*.json files

3. Extract section names using:
   python scripts/samples/extract_section_names.py s_1_9

4. Add section names and field aliases to i18n/*.py files

5. Add sensor entity definitions to sensor.py

6. Add canonical keys to i18n/canonical_keys.py

7. Add tests to tests/test_scraper_localization.py

See ADDING_NEW_SENSORS.md for complete workflow.
"""
