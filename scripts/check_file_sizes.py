"""Check language file sizes after conversion."""

from pathlib import Path

i18n_dir = Path('custom_components/stiebel_eltron_http/i18n')
files = sorted(i18n_dir.glob('*.py'))

print("Language file sizes after dynamic loading conversion:")
print("-" * 60)

lang_files = []
for f in files:
    if f.stem in ['__init__', 'canonical_keys', 'json_loader']:
        continue
    lines = f.read_text(encoding='utf-8').count('\n')
    lang_files.append((f.name, lines))
    print(f"  {f.name:15} {lines:4} lines")

print("-" * 60)
print(f"Total: {len(lang_files)} language files")
avg_lines = sum(lines for _, lines in lang_files) / len(lang_files)
print(f"Average: {avg_lines:.1f} lines per file")
