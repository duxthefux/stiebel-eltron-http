#!/usr/bin/env python3
"""Directly insert the French power consumption header with curly apostrophe."""

with open('custom_components/stiebel_eltron_http/mapping.py', 'rb') as f:
    data = f.read()

# The line we want to add after
straight_line = b'        "CONSOMMATION D\'\\xc3\\x89LECTRICIT\\xc3\\x89",  # fr (s_1_8) - straight apostrophe (0x27)'

# The new line with curly apostrophe (U+2019 = e2 80 99)
curly_line = b'        "CONSOMMATION D\\xe2\\x80\\x99\\xc3\\x89LECTRICIT\\xc3\\x89",  # fr (s_1_8) - curly apostrophe U+2019'

# Find the position
pos = data.find(straight_line)
if pos == -1:
    print("ERROR: Could not find the straight apostrophe line")
    print("Searching for simpler pattern...")
    pos = data.find(b"CONSOMMATION D'")
    if pos >= 0:
        # Show context
        print("Found CONSOMMATION at position", pos)
        print("Context:")
        print(data[pos-50:pos+150].decode('utf-8', errors='replace'))
else:
    print(f"Found straight apostrophe line at position {pos}")
    
    # Find the end of this line
    newline_pos = data.find(b'\n', pos)
    
    # Insert the curly apostrophe line after it
    new_data = data[:newline_pos+1] + curly_line + b'\n' + data[newline_pos+1:]
    
    # Write back
    with open('custom_components/stiebel_eltron_http/mapping.py', 'wb') as f:
        f.write(new_data)
    
    print("Successfully added French power consumption header with curly apostrophe!")
    
    # Verify
    verify_data = open('custom_components/stiebel_eltron_http/mapping.py', 'rb').read()
    if b'\xe2\x80\x99' in verify_data:
        print("✓ Verified: Curly apostrophe (U+2019) is now in the file!")
    else:
        print("✗ Failed: Curly apostrophe not found after write")
