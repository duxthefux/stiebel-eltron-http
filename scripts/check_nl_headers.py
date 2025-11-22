import re

text = open('scripts/testdata/s_1_0_nl.html', encoding='utf-8').read()
matches = list(re.finditer(r'<th[^>]*>([^<]+)</th>', text))
print(f'Found {len(matches)} headers:')
for i, m in enumerate(matches):
    print(f'  {i}: "{m.group(1)}"')
