"""Find files with mixed language translations."""
from pathlib import Path
import re

i18n_dir = Path("custom_components/stiebel_eltron_http/i18n")

for lang_file in sorted(i18n_dir.glob("[a-z][a-z].py")):
    content = lang_file.read_text("utf-8")
    
    # Find lists with many items (more than 4 commas suggests mixed languages)
    long_lists = re.findall(r'CanonicalKey\.(\w+): \[([^\]]+)\]', content)
    suspicious = [(k, v) for k, v in long_lists if v.count(",") > 4]
    
    if suspicious:
        print(f"\n{lang_file.name}: {len(suspicious)} suspicious entries")
        for key, value in suspicious[:3]:
            item_count = value.count(",") + 1
            print(f"  - {key}: {item_count} items")
