"""Extract all language files from testdata.

This script processes all 12 languages and generates their respective translation files.
"""

import re
from pathlib import Path
from bs4 import BeautifulSoup

TESTDATA_DIR = Path(__file__).parent / "testdata"
I18N_DIR = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "i18n"

LANGUAGES = {
    "de": "German",
    "en": "English",
    "fr": "French",
    "nl": "Dutch",
    "it": "Italian",
    "sv": "Swedish",
    "es": "Spanish",
    "pl": "Polish",
    "cs": "Czech",
    "hu": "Hungarian",
    "fi": "Finnish",
    "da": "Danish",
}

def extract_field_names_from_html(html_path):
    """Extract all field names from an HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    field_names = set()
    
    # Find section headers in <th> tags
    for th in soup.find_all('th'):
        text = th.get_text(strip=True)
        if text and len(text) > 1:
            field_names.add(text)
    
    # Find field names in <td class="key"> tags
    for td in soup.find_all('td', class_='key'):
        text = td.get_text(strip=True)
        if text:
            field_names.add(text)
    
    # Find headings in <h3> tags (like Betriebsart on start page)
    for h3 in soup.find_all('h3'):
        text = h3.get_text(strip=True)
        if text and len(text) > 1:
            field_names.add(text)
    
    # Find navigation menu items in <a> tags (like WARMWASSER, HEIZEN)
    for a in soup.find_all('a', href=True):
        # Only get menu navigation links, not other links
        if 'onclick="return checkChanges(this);"' in str(a):
            text = a.get_text(strip=True)
            if text and len(text) > 1:
                field_names.add(text)
    
    return field_names

def extract_language_fields(lang_code):
    """Extract all field names for a specific language from testdata."""
    lang_files = sorted(TESTDATA_DIR.glob(f"*_{lang_code}.html"))
    
    all_fields = set()
    for html_file in lang_files:
        fields = extract_field_names_from_html(html_file)
        all_fields.update(fields)
    
    return all_fields

def read_mapping_py():
    """Read and parse mapping.py HEADER_ALIASES."""
    mapping_file = Path(__file__).parent.parent / "custom_components" / "stiebel_eltron_http" / "mapping.py"
    with open(mapping_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract HEADER_ALIASES dictionary
    match = re.search(r'HEADER_ALIASES:.*?= \{(.*?)\n\}', content, re.DOTALL)
    if not match:
        raise ValueError("Could not find HEADER_ALIASES in mapping.py")
    
    aliases_text = match.group(1)
    
    # Parse entries
    all_translations = {}
    entries = re.finditer(r'CanonicalKey\.(\w+):\s*\[(.*?)\]', aliases_text, re.DOTALL)
    
    for entry in entries:
        key_name = entry.group(1)
        values_text = entry.group(2)
        values = re.findall(r'"([^"]+)"', values_text)
        all_translations[key_name] = values
    
    return all_translations

def generate_language_file(lang_code, lang_name, testdata_fields, all_translations):
    """Generate a language translation file."""
    # Normalize testdata fields for case-insensitive matching
    testdata_fields_normalized = {field.lower(): field for field in testdata_fields}
    
    # Filter translations that appear in testdata (case-insensitive)
    lang_translations = {}
    total_found = 0
    
    for key_name, values in all_translations.items():
        testdata_values = []
        for value in values:
            # Check if this translation appears in testdata (case-insensitive)
            if value.lower() in testdata_fields_normalized:
                testdata_values.append(value)
                total_found += 1
        
        if testdata_values:
            lang_translations[key_name] = testdata_values
    
    # Generate file content
    lines = [
        f'"""{lang_name} ({lang_code}) translations.',
        '',
        'Extracted from mapping.py HEADER_ALIASES.',
        f'Only includes strings that appear in {lang_name} test data files.',
        '"""',
        '',
        'from .canonical_keys import CanonicalKey',
        '',
        '',
        'TRANSLATIONS: dict[CanonicalKey, list[str]] = {',
    ]
    
    # Sort keys for consistent output
    for key_name in sorted(lang_translations.keys()):
        values = lang_translations[key_name]
        lines.append(f'    CanonicalKey.{key_name}: [')
        for value in values:
            # Escape quotes and backslashes in the value
            escaped_value = value.replace('\\', '\\\\').replace('"', '\\"')
            lines.append(f'        "{escaped_value}",')
        lines.append('    ],')
    
    lines.append('}')
    
    return '\n'.join(lines) + '\n', len(lang_translations), total_found

def main():
    """Extract all languages from testdata."""
    print("=" * 80)
    print("EXTRACTING ALL LANGUAGES FROM TESTDATA")
    print("=" * 80)
    print()
    
    # Read mapping.py once
    all_translations = read_mapping_py()
    print(f"Loaded {len(all_translations)} canonical keys from mapping.py")
    print()
    
    # Process each language
    results = []
    for lang_code, lang_name in LANGUAGES.items():
        print(f"Processing {lang_name} ({lang_code})...")
        
        # Extract fields from testdata
        testdata_fields = extract_language_fields(lang_code)
        print(f"  Found {len(testdata_fields)} unique fields in testdata")
        
        # Generate language file
        content, num_keys, num_translations = generate_language_file(
            lang_code, lang_name, testdata_fields, all_translations
        )
        
        # Write file
        output_file = I18N_DIR / f"{lang_code}.py"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ Created {output_file.name}")
        print(f"    Keys: {num_keys}, Translations: {num_translations}")
        print()
        
        results.append((lang_code, lang_name, num_keys, num_translations))
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    for lang_code, lang_name, num_keys, num_translations in results:
        print(f"  {lang_name:12} ({lang_code}): {num_keys:2} keys, {num_translations:3} translations")
    print()
    print(f"Total: {sum(r[3] for r in results)} translations across {len(LANGUAGES)} languages")

if __name__ == "__main__":
    main()
