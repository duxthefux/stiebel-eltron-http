import sys
sys.path.insert(0, 'custom_components/stiebel_eltron_http')

from mapping import HEADER_ALIASES

counts = {k: len(v) for k, v in HEADER_ALIASES.items()}
keys_gt_12 = {k: c for k, c in counts.items() if c > 12}

print(f'Keys with more than 12 entries: {len(keys_gt_12)}')
print(f'Keys with exactly 12: {sum(1 for c in counts.values() if c == 12)}')
print(f'Keys with less than 12: {sum(1 for c in counts.values() if c < 12)}')
print('\nExamples with >12:')
for k, c in list(keys_gt_12.items())[:10]:
    print(f'  {k.name}: {c} entries')
