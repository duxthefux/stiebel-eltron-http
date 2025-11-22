"""Rebuild all language files by extracting from original mapping.py."""

import subprocess
import re
from pathlib import Path
from collections import defaultdict

# Get original mapping.py
result = subprocess.run(
    ["git", "show", "12e5eeb:custom_components/stiebel_eltron_http/mapping.py"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)

content = result.stdout

# Language codes and names
LANG_INFO = {
    "de": "German", "en": "English", "fr": "French", "nl": "Dutch",
    "it": "Italian", "sv": "Swedish", "es": "Spanish", "pl": "Polish",
    "cs": "Czech", "hu": "Hungarian", "fi": "Finnish", "da": "Danish"
}

# Extract HEADER_ALIASES section
start_idx = content.find("HEADER_ALIASES: dict[CanonicalKey, list[str]] = {")
end_idx = content.find("\n}\n\n# A small whitelist", start_idx)
aliases_section = content[start_idx:end_idx + 2]

# Parse each canonical key entry
entries = {}
lines = aliases_section.split('\n')
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check for CanonicalKey start
    if 'CanonicalKey.' in line and ': [' in line:
        match = re.search(r'CanonicalKey\.(\w+):', line)
        if match:
            canonical_key = match.group(1)
            translations = []
            
            # Collect all translation lines until ]
            i += 1
            while i < len(lines) and '],' not in lines[i]:
                trans_line = lines[i]
                # Extract string and comment
                if '"' in trans_line:
                    str_match = re.search(r'"([^"]+)"[,\s]*(?:#\s*(.+))?', trans_line)
                    if str_match:
                        text = str_match.group(1)
                        comment = str_match.group(2).strip() if str_match.group(2) else ""
                        translations.append((text, comment))
                i += 1
            
            entries[canonical_key] = translations
    i += 1

# Organize by language
by_lang = {lang: defaultdict(list) for lang in LANG_INFO}

for canonical_key, translations in entries.items():
    for text, comment in translations:
        # Determine language from comment
        lang = None
        
        # Direct language code
        if comment in LANG_INFO:
            lang = comment
        # With page info like "de (s_1_0)"
        elif comment:
            for lc in LANG_INFO:
                if comment.startswith(lc + " ") or comment == lc:
                    lang = lc
                    break
        
        if lang:
            by_lang[lang][canonical_key].append((text, comment))

# Write language files
output_dir = Path("custom_components/stiebel_eltron_http/i18n")

for lang, name in LANG_INFO.items():
    translations = by_lang[lang]
    
    lines = [
        f'"""Translation mappings for {lang.upper()} ({name})."""',
        '',
        'from .canonical_keys import CanonicalKey',
        '',
        '',
        f'TRANSLATIONS_{lang.upper()} = {{',
    ]
    
    for canonical_key in sorted(translations.keys()):
        items = translations[canonical_key]
        
        if len(items) == 1:
            text, comment = items[0]
            # Check if it's a TODO comment
            if "TODO" in comment:
                lines.append(f'    CanonicalKey.{canonical_key}: "{text}",  # {comment}')
            else:
                lines.append(f'    CanonicalKey.{canonical_key}: "{text}",')
        else:
            # Multiple variants - make a list
            texts = [f'"{text}"' for text, _ in items]
            # Check for TODO in any comment
            has_todo = any("TODO" in comment for _, comment in items)
            if has_todo:
                todo_comment = next((comment for _, comment in items if "TODO" in comment), "")
                lines.append(f'    CanonicalKey.{canonical_key}: [{", ".join(texts)}],  # {todo_comment}')
            else:
                lines.append(f'    CanonicalKey.{canonical_key}: [{", ".join(texts)}],')
    
    lines.append('}')
    lines.append('')
    
    output_file = output_dir / f"{lang}.py"
    output_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f"✓ {lang}.py - {len(translations)} keys")

print(f"\n✓ Rebuilt all {len(LANG_INFO)} language files")
