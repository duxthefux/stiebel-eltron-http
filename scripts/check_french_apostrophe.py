with open('custom_components/stiebel_eltron_http/mapping.py', 'rb') as f:
    content = f.read()

# Find all CONSOMMATION lines
idx = 0
while True:
    idx = content.find(b'CONSOMMATION D', idx)
    if idx == -1:
        break
    
    # Extract the line
    line_start = content.rfind(b'\n', max(0, idx-100), idx) + 1
    line_end = content.find(b'\n', idx)
    line = content[line_start:line_end]
    
    # Find the apostrophe after D
    d_pos = line.find(b'D')
    if d_pos >= 0 and d_pos + 1 < len(line):
        apos_byte = line[d_pos+1:d_pos+4]
        print(f"Apostrophe bytes: {apos_byte.hex()}")
        print(f"Line: {line.decode('utf-8', errors='replace')}")
        print()
    
    idx += 1
