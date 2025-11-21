"""Fetch ISG pages from a given base URL and save them under scripts/testdata.

Usage examples (PowerShell):
  py -3 .\\scripts\\fetch_testdata.py --base http://servicewelt.localiot
  py -3 .\\scripts\\fetch_testdata.py --base http://192.168.1.50 --endpoints "/?s=1,1" "/?s=2,7"
  py -3 .\\scripts\\fetch_testdata.py --base http://servicewelt.localiot --all-languages
  py -3 .\\scripts\\fetch_testdata.py --base http://servicewelt.localiot --all-languages --no-harmonize

The script uses the builtin urllib to avoid extra dependencies.
With --all-languages, it will detect all available languages from s=5,3,
fetch all endpoints for each language, then restore the original language.

By default (or with --harmonize), numeric values are normalized to fixed
reference values so that all language variants have identical data, differing
only in language labels. This makes cross-language testing more reliable.
Use --no-harmonize to keep original values from the device.

Requires beautifulsoup4 for value harmonization: pip install beautifulsoup4
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from urllib.parse import urljoin

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("Warning: BeautifulSoup4 not available, value harmonization will be skipped")
    print("Install with: pip install beautifulsoup4")


DEFAULT_ENDPOINTS = [
    "/?s=0",  # Start / index page
    "/?s=1,1",  # Heat pump / process data
    "/?s=1,0",  # Info / system
    "/?s=1,8",  # Energy balance (sometimes present)
    "/?s=2,7",  # Diagnosis / system
    "/?s=5,0",  # Profile / network
]

DEFAULT_FILENAMES = {
    "/?s=0": "s_0_0.html",
    "/?s=1,1": "s_1_1.html",
    "/?s=1,0": "s_1_0.html",
    "/?s=1,8": "s_1_8.html",
    "/?s=2,7": "s_2_7.html",
    "/?s=5,0": "s_5_0.html",
}


def sanitize_filename(path: str) -> str:
    """Make a filesystem-safe filename for a given endpoint."""
    if path in DEFAULT_FILENAMES:
        return DEFAULT_FILENAMES[path]
    name = path.lstrip("/")
    name = name.replace("?", "_").replace("=", "_").replace(",", "_")
    if not name:
        name = "index"
    return f"{name}.html"


def fetch_text(url: str, timeout: int = 20, retries: int = 3, retry_delay: float = 2.0) -> str | None:
    """Fetch the text content from a URL with retry logic."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "stiebel-test-fetch/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                # ISG pages use UTF-8 encoding
                return resp.read().decode('utf-8')
        except urllib.error.URLError as exc:
            if attempt < retries - 1:
                print(f"  Attempt {attempt + 1}/{retries} failed for {url}: {exc.reason}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"  All {retries} attempts failed for {url}: {exc.reason}")
                return None
        except Exception as exc:
            if attempt < retries - 1:
                print(f"  Attempt {attempt + 1}/{retries} failed for {url}: {exc}, retrying in {retry_delay}s...")
                time.sleep(retry_delay)
            else:
                print(f"  All {retries} attempts failed for {url}: {exc}")
                return None
    return None


def harmonize_values(html: str) -> str:
    """Harmonize numeric values across language versions for consistent testing.
    
    Replaces actual sensor values with fixed reference values so that
    testdata files differ only in language labels, not in values.
    This makes cross-language testing more reliable and easier to maintain.
    
    Only modifies <td class="value"> cells, leaving labels untouched.
    
    Reference values used:
    - Temperatures: 23.3°C, -5.0°C (depending on context)
    - Pressures: 5.22bar
    - Flow rates: 31.9l/min
    - Powers: 1.2kW, 0.5kW
    - Energies: 12345.6kWh, 123.4kWh
    - Percentages: 53.3%, 100%
    - Voltages: 230V
    - Currents: 8.5A
    - RPM: 3500/3600
    - Counts/starts: 42, 123
    - Runtime: 12345h
    """
    if not html or not HAS_BS4:
        return html
    
    # Store the original for pattern matching
    import re
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
    except Exception:
        # If parsing fails, return original
        return html
    
    # Find all table data cells with class="value" (these contain sensor readings)
    # Do NOT modify cells with class="key" (those are labels that must stay in original language)
    for td in soup.find_all('td', class_='value'):
        text = td.get_text(strip=True)
        if not text:
            continue
        
        # Temperature patterns (with degree symbol or °C)
        if '°C' in text or '°' in text:
            # Replace with reference temperature value
            # Frost protection is the only one that should be negative
            if 'frost' in text.lower() or 'freeze' in text.lower() or 'frostschutz' in text.lower():
                td.string = '-5,0°C'
            elif 'outside' in text.lower() or 'aussen' in text.lower() or 'ambient' in text.lower():
                td.string = '8,5°C'
            else:
                # All other temperatures use standard reference value
                td.string = '23,3°C'
        
        # Pressure patterns (bar)
        elif 'bar' in text.lower():
            td.string = '5,22bar'
        
        # Flow rate patterns (l/min)
        elif 'l/min' in text.lower() or 'liter' in text.lower():
            td.string = '31,9l/min'
        
        # Energy patterns (kWh, MWh, KWh) - MUST be checked BEFORE power (kW, W)
        # Case-insensitive to handle both "kWh" and "KWh"
        elif 'MWh' in text or 'Mwh' in text or 'mwh' in text or 'MWH' in text:
            td.string = '12,3MWh'
        elif 'kWh' in text or 'KWh' in text or 'kwh' in text or 'KWH' in text:
            # Different magnitudes for different contexts
            parts = re.search(r'([\d,\.]+)', text)
            if parts:
                val_str = parts.group(1).replace(',', '.')
                # Handle European number format (comma as decimal separator)
                val = float(val_str)
                if val > 10000:
                    td.string = '12345,6kWh'
                elif val > 1000:
                    td.string = '1234,5kWh'
                else:
                    td.string = '123,4kWh'
        
        # Power patterns (kW, W) - checked AFTER energy patterns
        elif 'kW' in text or 'KW' in text:
            td.string = '1,2kW'
        elif text.endswith('W') or 'watt' in text.lower():
            td.string = '500W'
        
        # Percentage patterns
        elif '%' in text:
            if '100' in text:
                td.string = '100%'
            else:
                td.string = '53,3%'
        
        # Voltage patterns (V)
        elif text.endswith('V') or 'volt' in text.lower():
            td.string = '230V'
        
        # Current patterns (A)
        elif text.endswith('A') or 'ampere' in text.lower():
            td.string = '8,5A'
        
        # RPM patterns (compressor speed)
        elif 'rpm' in text.lower() or '/min' in text:
            if 'soll' in text.lower() or 'target' in text.lower() or 'setpoint' in text.lower():
                td.string = '3600/min'
            else:
                td.string = '3500/min'
        
        # Frequency patterns (Hz - compressor speed)
        elif text.endswith('Hz') or text.endswith('hz'):
            # Always use same value for consistency
            td.string = '42Hz'
        
        # Runtime hours
        elif text.endswith('h') and re.match(r'^\d+h$', text):
            # Different magnitudes for different contexts
            num = int(re.search(r'\d+', text).group())
            if num > 10000:
                td.string = '12345h'
            elif num > 1000:
                td.string = '1234h'
            else:
                td.string = '123h'
        
        # Plain numbers (counts, starts, etc.)
        elif re.match(r'^[\d,\.]+$', text):
            # Check if we're in an efficiency table (parent table contains EFFIZIENZ/EFFICIENCY)
            parent_table = td.find_parent('table')
            is_efficiency = False
            if parent_table:
                table_text = parent_table.get_text()
                is_efficiency = 'EFFIZIENZ' in table_text or 'EFFICIENCY' in table_text or 'EFFICACITÉ' in table_text
            
            if is_efficiency:
                # Efficiency values are always 123 (representing 1.23 or 123%)
                td.string = '123'
            else:
                # Different magnitudes for other contexts
                num_str = text.replace(',', '.').replace('.', '', text.count('.') - 1)
                try:
                    num = float(num_str)
                    if num > 1000:
                        td.string = '1234'
                    elif num > 100:
                        td.string = '123'
                    else:
                        td.string = '42'
                except ValueError:
                    pass
    
    return str(soup)


def sanitize_html(html: str) -> str:
    """Remove sensitive data from HTML content.
    
    Replaces:
    - MAC addresses with AA:BB:CC:11:22:33
    - IP addresses with 192.168.1.100
    - WiFi SSID names (if present)
    """
    if not html:
        return html
    
    # Replace MAC addresses (formats: AA:BB:CC:DD:EE:FF or AA-BB-CC-DD-EE-FF)
    mac_pattern = re.compile(
        r'\b([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})\b'
    )
    html = mac_pattern.sub('AA:BB:CC:11:22:33', html)
    
    # Replace private IP addresses (192.168.x.x, 10.x.x.x, 172.16-31.x.x)
    # Keep localhost (127.0.0.1) and version numbers (e.g., 1.4.00.0040)
    ip_pattern = re.compile(
        r'\b(?:(?:192\.168|10\.|172\.(?:1[6-9]|2[0-9]|3[01]))\.\d{1,3}\.\d{1,3})\b'
    )
    html = ip_pattern.sub('192.168.1.100', html)
    
    return html


def get_available_languages(base_url: str, timeout: int = 20) -> list[tuple[str, str]]:
    """Fetch language selection page and extract available languages.
    
    Returns list of tuples: [(language_code, language_name), ...]
    e.g., [('de', 'DEUTSCH'), ('en', 'ENGLISH')]
    """
    lang_page_url = urljoin(base_url, "/?s=5,3")
    print(f"Fetching language selection page: {lang_page_url}")
    html = fetch_text(lang_page_url, timeout=timeout)
    if not html:
        print("Warning: Could not fetch language page, using defaults")
        return [("de", "DEUTSCH"), ("en", "ENGLISH")]
    
    # Extract language options from the page
    # Looking for patterns like: <input type="radio" ... value="DEUTSCH" ... >
    # followed by <label>DEUTSCH</label>
    languages = []
    
    # Pattern for radio buttons with language names
    # ISG uses: <input ... value="DEUTSCH" ...><label>DEUTSCH</label>
    # Language names can contain special characters (ČEŠTINA, FRANÇAIS, etc.)
    # Match any non-quote characters in the value attribute
    radio_pattern = re.compile(
        r'<input[^>]*name=["\']valspracheeinstellung["\'][^>]*value=["\']([^"\']+)["\'][^>]*>',
        re.IGNORECASE
    )
    
    for match in radio_pattern.finditer(html):
        name = match.group(1).strip().upper()
        value = name  # ISG uses language name as value
        
        # Map language names to ISO codes
        lang_code = None
        if name == "DEUTSCH":
            lang_code = "de"
        elif name == "ENGLISH":
            lang_code = "en"
        elif name == "FRANÇAIS":
            lang_code = "fr"
        elif name == "NEDERLANDS":
            lang_code = "nl"
        elif name == "ITALIANO":
            lang_code = "it"
        elif name == "SVENSKA":
            lang_code = "sv"
        elif name == "POLSKI":
            lang_code = "pl"
        elif name == "ČEŠTINA":
            lang_code = "cs"
        elif name == "MAGYAR":
            lang_code = "hu"
        elif name == "ESPAÑOL":
            lang_code = "es"
        elif name == "SUOMI":
            lang_code = "fi"
        elif name == "DANSK":
            lang_code = "da"
        
        if lang_code:
            languages.append((lang_code, name))
            print(f"  Found language: {name} (code: {lang_code}, value: {value})")
    
    if not languages:
        print("Warning: No languages detected, using defaults")
        return [("de", "DEUTSCH"), ("en", "ENGLISH")]
    
    return languages


def set_language(base_url: str, language_code: str, timeout: int = 20, retries: int = 3) -> bool:
    """Set the ISG interface language with retry logic.
    
    Posts to save.php with JSON data to change the language.
    Returns True if successful.
    """
    lang_page_url = urljoin(base_url, "/?s=5,3")
    save_url = urljoin(base_url, "/save.php")
    
    # Map language codes to ISG language names
    lang_name_map = {
        "de": "DEUTSCH",
        "en": "ENGLISH",
        "fr": "FRANÇAIS",
        "nl": "NEDERLANDS",
        "it": "ITALIANO",
        "sv": "SVENSKA",
        "pl": "POLSKI",
        "cs": "ČEŠTINA",
        "hu": "MAGYAR",
        "es": "ESPAÑOL",
        "fi": "SUOMI",
        "da": "DANSK",
    }
    
    lang_name = lang_name_map.get(language_code, "ENGLISH")
    
    # The ISG expects JSON data in the format: [{"name":"valspracheeinstellung","value":"ENGLISH"}]
    # This is posted to save.php as form data with key "data"
    import json
    form_data = [{"name": "valspracheeinstellung", "value": lang_name}]
    json_data = json.dumps(form_data)
    
    # URL encode the JSON string as form data
    data = f"data={urllib.parse.quote(json_data)}".encode('utf-8')
    
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                save_url,
                data=data,
                headers={
                    "User-Agent": "stiebel-test-fetch/1.0",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Referer": lang_page_url,
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                response = resp.read().decode('utf-8')
            
            print(f"  Language set to: {language_code}")
            # Give the device a moment to process and persist the change
            time.sleep(2)
            return True
            
        except Exception as exc:
            if attempt < retries - 1:
                print(f"  Attempt {attempt + 1}/{retries} to set language to {language_code} failed: {exc}, retrying...")
                time.sleep(2)
            else:
                print(f"  Warning: All {retries} attempts failed to set language to {language_code}: {exc}")
                return False
    
    return False


def _detect_language(html: str) -> str:
    """Heuristic language detection (returns 'de' or 'en')."""
    if not isinstance(html, str):
        return "en"

    low = html.lower()

    # If a language switch element exists, infer language from the visible
    # link text. Interpret the link text as the current UI language.
    if "eingestelle_sprache" in low:
        if "english" in low:
            return "en"
        if "deutsch" in low or "german" in low:
            return "de"

    german_signals = [
        "raumtemperatur",
        "heizung",
        "warmwasser",
        "raumfeuchte",
        "trinkwasser",
        "reglersteuerung",
        "wärme",
        "wärmemenge",
    ]

    for sig in german_signals:
        if sig in low:
            return "de"

    return "en"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fetch ISG pages and save to scripts/testdata.")
    parser.add_argument("--base", required=True, help="Base URL of the ISG (e.g. http://servicewelt.localiot)")
    parser.add_argument("--outdir", default=os.path.join(os.path.dirname(__file__), "testdata"), help="Output folder")
    parser.add_argument("--endpoints", nargs="*", help="Endpoints to fetch (overrides defaults)")
    parser.add_argument(
        "--lang",
        choices=("auto", "de", "en", "both"),
        default="auto",
        help="How to write language variants: auto (detect & write suffix), de/en (write that suffix), both (write both suffixes)",
    )
    parser.add_argument(
        "--all-languages",
        action="store_true",
        help="Fetch all available languages by switching language on device (overrides --lang)",
    )
    parser.add_argument(
        "--harmonize",
        action="store_true",
        default=True,
        help="Harmonize numeric values across languages (default: True)",
    )
    parser.add_argument(
        "--no-harmonize",
        action="store_false",
        dest="harmonize",
        help="Skip value harmonization, keep original values",
    )
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout seconds")
    args = parser.parse_args(argv)

    base = args.base
    outdir = args.outdir
    endpoints = args.endpoints or DEFAULT_ENDPOINTS

    os.makedirs(outdir, exist_ok=True)

    if args.all_languages:
        # Multi-language mode: detect all languages, switch to each, download all pages
        print("=== Multi-language fetch mode ===")
        if args.harmonize:
            print("Value harmonization: ENABLED (all languages will have identical values)")
        else:
            print("Value harmonization: DISABLED (original values will be preserved)")
        
        # First, detect current language to restore later
        print("\nDetecting current language...")
        initial_html = fetch_text(urljoin(base, "/?s=0"), timeout=args.timeout)
        initial_lang = _detect_language(initial_html) if initial_html else "de"
        print(f"Current language detected as: {initial_lang}")
        
        # Get available languages
        available_langs = get_available_languages(base, timeout=args.timeout)
        
        any_failed = False
        
        # Reorder languages so current language is processed first
        # This avoids immediate language switch and potential issues
        lang_order = []
        other_langs = []
        for lang_code, lang_name in available_langs:
            if lang_code == initial_lang:
                lang_order.insert(0, (lang_code, lang_name))  # Put current language first
            else:
                other_langs.append((lang_code, lang_name))
        lang_order.extend(other_langs)
        
        is_first = True
        for lang_code, lang_name in lang_order:
            print(f"\n=== Fetching pages for language: {lang_name} ({lang_code}) ===")
            
            # Set the language on the device (skip if it's the first language which is already set)
            if is_first and lang_code == initial_lang:
                print(f"  Using current language: {lang_code} (no switch needed)")
                is_first = False
            else:
                if not set_language(base, lang_code, timeout=args.timeout):
                    print(f"Skipping {lang_code} due to language switch failure")
                    continue
            
            # Fetch all endpoints for this language
            for ep in endpoints:
                full = urljoin(base, ep)
                print(f"  Fetching {full} ...")
                html = fetch_text(full, timeout=args.timeout)
                if html is None:
                    any_failed = True
                    continue
                
                # Sanitize sensitive data
                html = sanitize_html(html)
                
                # Harmonize values to make all language variants identical except for labels
                if args.harmonize:
                    html = harmonize_values(html)
                
                # Save with language suffix
                base_fname = sanitize_filename(ep)
                base_noext = os.path.splitext(base_fname)[0]
                suffixed = os.path.join(outdir, base_noext + f"_{lang_code}.html")
                
                try:
                    with open(suffixed, "w", encoding="utf-8") as fh:
                        fh.write(html)
                    print(f"  Wrote: {suffixed}")
                except Exception as exc:
                    print(f"  Failed writing {suffixed}: {exc}")
                    any_failed = True
        
        # Restore initial language
        print(f"\n=== Restoring initial language: {initial_lang} ===")
        set_language(base, initial_lang, timeout=args.timeout)
        
        return 0 if not any_failed else 2
    
    # Original single-language mode
    any_failed = False
    for ep in endpoints:
        full = urljoin(base, ep)
        print(f"Fetching {full} ...")
        html = fetch_text(full, timeout=args.timeout)
        if html is None:
            any_failed = True
            continue

        # Sanitize sensitive data
        html = sanitize_html(html)
        
        # Harmonize values to make testing more consistent
        if args.harmonize:
            html = harmonize_values(html)
        
        detected = _detect_language(html)

        # Decide which language variants to write (only suffixed files).
        if args.lang == "both":
            want = ["de", "en"]
        elif args.lang == "auto":
            want = [detected]
        else:
            want = [args.lang]

        base_fname = sanitize_filename(ep)
        base_noext = os.path.splitext(base_fname)[0]
        for lang in want:
            suffixed = os.path.join(outdir, base_noext + f"_{lang}.html")
            try:
                with open(suffixed, "w", encoding="utf-8") as fh:
                    fh.write(html)
                print(f"Wrote language variant: {suffixed}")
            except Exception as exc:
                print(f"Failed writing language variant {suffixed}: {exc}")

    return 0 if not any_failed else 2


if __name__ == "__main__":
    raise SystemExit(main())
