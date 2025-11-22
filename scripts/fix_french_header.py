import sys

# Create the correct French header with curly apostrophe (U+2019)
header = "CONSOMMATION D" + chr(0x2019) + "ÉLECTRICITÉ"
print(f"Header: {header}")
print(f"Hex: {header.encode('utf-8').hex()}")
print(f"Apostrophe: {ord(header[14]):#x}")

# Now update the mapping.py file
with open('custom_components/stiebel_eltron_http/mapping.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the line with straight apostrophe and add the curly one after it
search_str = '        "CONSOMMATION D\'ÉLECTRICITÉ",  # fr (s_1_8) - curly apostrophe (U+2019)'
if search_str in content:
    print("Line with curly apostrophe already exists!")
else:
    # Add it after the straight apostrophe line
    insert_after = '        "CONSOMMATION D\'ÉLECTRICITÉ",  # fr (s_1_8) - straight apostrophe (0x27)'
    new_line = f'        "{header}",  # fr (s_1_8) - curly apostrophe U+2019'
    
    content = content.replace(
        insert_after,
        insert_after + '\n' + new_line
    )
    
    with open('custom_components/stiebel_eltron_http/mapping.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Added French power section header with curly apostrophe!")
