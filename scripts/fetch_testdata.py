"""Fetch ISG pages from a given base URL and save them under scripts/testdata.

Usage examples (PowerShell):
  py -3 .\\scripts\\fetch_testdata.py --base http://servicewelt.localiot
  py -3 .\\scripts\\fetch_testdata.py --base http://192.168.1.50 --endpoints "/?s=1,1" "/?s=2,7"
  py -3 .\\scripts\\fetch_testdata.py --base http://servicewelt.localiot --all-languages

The script uses the builtin urllib to avoid extra dependencies.
With --all-languages, it will detect all available languages from s=5,3,
fetch all endpoints for each language, then restore the original language.
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


def fetch_text(url: str, timeout: int = 10) -> str | None:
    """Fetch the text content from a URL."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "stiebel-test-fetch/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            # ISG pages use UTF-8 encoding
            return resp.read().decode('utf-8')
    except urllib.error.URLError as exc:
        print(f"Unexpected error fetching {url}: {exc.reason}")
        return None
    except Exception as exc:
        print(f"Unexpected error fetching {url}: {exc}")
        return None


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


def get_available_languages(base_url: str, timeout: int = 10) -> list[tuple[str, str]]:
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


def set_language(base_url: str, language_code: str, timeout: int = 10) -> bool:
    """Set the ISG interface language.
    
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
        print(f"  Warning: Failed to set language to {language_code}: {exc}")
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
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout seconds")
    args = parser.parse_args(argv)

    base = args.base
    outdir = args.outdir
    endpoints = args.endpoints or DEFAULT_ENDPOINTS

    os.makedirs(outdir, exist_ok=True)

    if args.all_languages:
        # Multi-language mode: detect all languages, switch to each, download all pages
        print("=== Multi-language fetch mode ===")
        
        # First, detect current language to restore later
        print("\nDetecting current language...")
        initial_html = fetch_text(urljoin(base, "/?s=0"), timeout=args.timeout)
        initial_lang = _detect_language(initial_html) if initial_html else "de"
        print(f"Current language detected as: {initial_lang}")
        
        # Get available languages
        available_langs = get_available_languages(base, timeout=args.timeout)
        
        any_failed = False
        
        for lang_code, lang_name in available_langs:
            print(f"\n=== Fetching pages for language: {lang_name} ({lang_code}) ===")
            
            # Set the language on the device
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
