"""Extract German translations from current HEADER_ALIASES."""
import sys
sys.path.insert(0, ".")

from custom_components.stiebel_eltron_http.mapping import HEADER_ALIASES, CanonicalKey

# Read the old mapping to get language comments
import subprocess
result = subprocess.run(
    ["git", "show", "12e5eeb:custom_components/stiebel_eltron_http/mapping.py"],
    capture_output=True
)

# Use bytes mode to avoid encoding issues
content = result.stdout.decode("utf-8", errors="ignore")

# Build mapping of text -> language from original file
text_to_lang = {}
for line in content.split('\n'):
    if '"' in line and '#' in line:
        import re
        match = re.search(r'"([^"]+)"\s*,?\s*#\s*(\w+)', line)
        if match:
            text = match.group(1)
            lang_or_comment = match.group(2)
            # Simple check if it's a language code
            if lang_or_comment in ['de', 'en', 'fr', 'nl', 'it', 'sv', 'es', 'pl', 'cs', 'hu', 'fi', 'da']:
                text_to_lang[text] = lang_or_comment

# Extract German translations
de_translations = {}

for canonical_key, aliases in HEADER_ALIASES.items():
    german_variants = []
    
    for alias in aliases:
        # Check if this alias is German
        lang = text_to_lang.get(alias)
        if lang == 'de':
            german_variants.append(alias)
    
    if german_variants:
        if len(german_variants) == 1:
            de_translations[canonical_key] = german_variants[0]
        else:
            de_translations[canonical_key] = german_variants

# Write the file
lines = [
    '"""Translation mappings for DE (German)."""',
    '',
    'from .canonical_keys import CanonicalKey',
    '',
    '',
    'TRANSLATIONS_DE = {',
]

for canonical_key in sorted(de_translations.keys(), key=lambda k: str(k)):
    value = de_translations[canonical_key]
    
    if isinstance(value, list):
        vals_str = ', '.join(f'"{v}"' for v in value)
        lines.append(f'    CanonicalKey.{canonical_key}: [{vals_str}],')
    else:
        # Check for TODO markers in original
        todo_marker = ""
        if canonical_key in [CanonicalKey.ACTUAL_TEMPERATURE_1, CanonicalKey.RELATIVE_HUMIDITY_1, CanonicalKey.ROOM_TEMPERATURE_SECTION]:
            todo_marker = "  # TODO: check with real device (no test data)"
        lines.append(f'    CanonicalKey.{canonical_key}: "{value}",{todo_marker}')

lines.append('}')
lines.append('')

output = '\n'.join(lines)
with open("custom_components/stiebel_eltron_http/i18n/de.py", "w", encoding="utf-8") as f:
    f.write(output)

print(f"✓ Rebuilt de.py with {len(de_translations)} German translations")
