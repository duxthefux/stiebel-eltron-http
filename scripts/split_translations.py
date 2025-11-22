"""Extract translations to language-specific files."""

import re
from pathlib import Path

# Read mapping.py
mapping_file = Path("custom_components/stiebel_eltron_http/mapping.py")
content = mapping_file.read_text(encoding="utf-8")

# Find HEADER_ALIASES section
start_marker = "HEADER_ALIASES: dict[CanonicalKey, list[str]] = {"
end_marker = "\n}\n\n# A small whitelist"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx == -1 or end_idx == -1:
    print("Could not find HEADER_ALIASES section")
    exit(1)

aliases_section = content[start_idx:end_idx + 2]  # Include the closing }

# Parse entries
entries = {}
current_key = None
current_list = []

for line in aliases_section.split('\n'):
    # Check for Canonical Key start
    if 'CanonicalKey.' in line and ': [' in line:
        # Save previous if exists
        if current_key and current_list:
            entries[current_key] = current_list
        
        # Start new
        match = re.search(r'CanonicalKey\.(\w+):', line)
        if match:
            current_key = match.group(1)
            current_list = []
    
    # Check for string entries
    elif '"' in line and current_key:
        # Extract string and comment
        match = re.search(r'"([^"]+)"[,\s]*(?:#\s*(.+))?', line)
        if match:
            string_val = match.group(1)
            comment = match.group(2).strip() if match.group(2) else ""
            current_list.append((string_val, comment))
    
    # Check for closing bracket
    elif line.strip() == '],' and current_key:
        entries[current_key] = current_list
        current_key = None
        current_list = []

# Organize by language
lang_codes = ["de", "en", "fr", "nl", "it", "sv", "es", "pl", "cs", "hu", "fi", "da"]
lang_names = {
    "de": "German", "en": "English", "fr": "French", "nl": "Dutch",
    "it": "Italian", "sv": "Swedish", "es": "Spanish", "pl": "Polish",
    "cs": "Czech", "hu": "Hungarian", "fi": "Finnish", "da": "Danish"
}

by_lang = {lang: {} for lang in lang_codes}

for canonical_key, translations in entries.items():
    for string_val, comment in translations:
        # Determine language
        lang = None
        todo_comment = None
        
        # Check if comment is just a language code
        if comment in lang_codes:
            lang = comment
        # Check if comment contains TODO
        elif "TODO" in comment:
            # Try to extract language from comment
            for lc in lang_codes:
                if lc in comment:
                    lang = lc
                    todo_comment = comment
                    break
        # Check for page indicators like (s_1_1) or (s_0_0)
        elif comment and any(c in comment for c in lang_codes):
            # Extract lang code
            for lc in lang_codes:
                if lc in comment:
                    lang = lc
                    # Keep the comment for context
                    todo_comment = comment if "TODO" in comment else None
                    break
        
        if lang:
            if canonical_key not in by_lang[lang]:
                by_lang[lang][canonical_key] = []
            by_lang[lang][canonical_key].append((string_val, todo_comment))

# Write language files
output_dir = Path("custom_components/stiebel_eltron_http/i18n")

for lang in lang_codes:
    lines = [
        f'"""Translation mappings for {lang.upper()} ({lang_names[lang]})."""',
        '',
        'from .canonical_keys import CanonicalKey',
        '',
        '',
        f'TRANSLATIONS_{lang.upper()} = {{',
    ]
    
    for canonical_key in sorted(by_lang[lang].keys()):
        translations = by_lang[lang][canonical_key]
        
        if len(translations) == 1:
            string_val, todo = translations[0]
            comment_str = f"  # {todo}" if todo else ""
            lines.append(f'    CanonicalKey.{canonical_key}: "{string_val}",{comment_str}')
        else:
            # Multiple translations (variants)
            variant_strs = []
            has_todo = False
            for string_val, todo in translations:
                if todo:
                    has_todo = True
                variant_strs.append(f'"{string_val}"')
            
            todo_comment = ""
            if has_todo:
                # Get first TODO comment
                for _, todo in translations:
                    if todo:
                        todo_comment = f"  # {todo}"
                        break
            
            lines.append(f'    CanonicalKey.{canonical_key}: [{", ".join(variant_strs)}],{todo_comment}')
    
    lines.append('}')
    lines.append('')
    
    output_file = output_dir / f"{lang}.py"
    output_file.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Wrote {lang}.py with {len(by_lang[lang])} keys")

print(f"\n✓ Created {len(lang_codes)} language files")
