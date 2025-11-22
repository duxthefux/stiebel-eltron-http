#!/usr/bin/env python3
from bs4 import BeautifulSoup

html = open('scripts/testdata/s_1_0_de.html', encoding='utf-8').read()
soup = BeautifulSoup(html, 'html.parser')
labels = [td.get_text(strip=True) for td in soup.find_all('td', class_='label')]

print("German s_1_0 field labels:\n")
for i, label in enumerate(labels[:20]):
    print(f"{i}: {label}")
