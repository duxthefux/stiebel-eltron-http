#!/usr/bin/env python3
with open('custom_components/stiebel_eltron_http/mapping.py', 'rb') as f:
    data = f.read()

# Find the comment line
marker = b'# fr (s_1_8) - straight apostrophe (0x27)'
pos = data.find(marker)

if pos == -1:
    print("Could not find marker")
else:
    # Find end of this line
    eol = data.find(b'\n', pos)
    
    # Create the new line with curly apostrophe
    # U+2019 in UTF-8 is: e2 80 99
    # É in UTF-8 is: c3 89
    new_line = b'        "CONSOMMATION D\xe2\x80\x99\xc3\x89LECTRICIT\xc3\x89",  # fr (s_1_8) - curly apostrophe U+2019\n'
    
    # Insert after the current line
    new_data = data[:eol+1] + new_line + data[eol+1:]
    
    # Write
    with open('custom_components/stiebel_eltron_http/mapping.py', 'wb') as f:
        f.write(new_data)
    
    # Verify
    verify = open('custom_components/stiebel_eltron_http/mapping.py', 'rb').read()
    if b'\xe2\x80\x99' in verify:
        print("✓ Success! Curly apostrophe added")
        # Count occurrences
        count = verify.count(b'CONSOMMATION D')
        print(f"  Total CONSOMMATION lines: {count}")
    else:
        print("✗ Failed")
