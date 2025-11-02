"""Fetch ISG pages from a given base URL and save them under scripts/testdata.

Usage examples (PowerShell):
  py -3 .\scripts\fetch_testdata.py --base http://servicewelt.localiot
  py -3 .\scripts\fetch_testdata.py --base http://192.168.1.50 --endpoints "/?s=1,1" "/?s=2,7"

The script uses the builtin urllib to avoid extra dependencies.
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.request
import urllib.error
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
    """Fetch url and return decoded text or None on error."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "stiebel-test-fetch/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            # Attempt to decode as utf-8, fall back to latin-1
            try:
                text = data.decode("utf-8")
            except Exception:
                text = data.decode("latin-1", errors="replace")
        return text

    except urllib.error.HTTPError as exc:
        print(f"HTTP error fetching {url}: {exc.code} {exc.reason}")
    except urllib.error.URLError as exc:
        print(f"URL error fetching {url}: {exc}")
    except Exception as exc:
        print(f"Unexpected error fetching {url}: {exc}")
    return None


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
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout seconds")
    args = parser.parse_args(argv)

    base = args.base
    outdir = args.outdir
    endpoints = args.endpoints or DEFAULT_ENDPOINTS

    os.makedirs(outdir, exist_ok=True)

    any_failed = False
    for ep in endpoints:
        full = urljoin(base, ep)
        print(f"Fetching {full} ...")
        html = fetch_text(full, timeout=args.timeout)
        if html is None:
            any_failed = True
            continue

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
