"""Quick test harness to exercise the scraper parsing logic with a sample ISG HTML.

Run from the repository root. This script imports the custom component module
and calls the parsing helpers to show extracted values.
"""

import os
import sys

# Make repository root importable so "custom_components" package can be found
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from custom_components.stiebel_eltron_http.scraper import StiebelEltronScrapingClient

import argparse


def parse_and_print(client: StiebelEltronScrapingClient, html: str, source: str) -> None:
    print(f"\n=== Parsing {source} ===")
    print("Auto-detected language:", client._auto_detect_language(html))

    print("--- info_system ---")
    sys_result = client._extract_info_system(html)
    for k, v in sys_result.items():
        print(k, "=", v)

    print("--- info_heatpump ---")
    hp_result = client._extract_info_heatpump(html)
    for k, v in hp_result.items():
        print(k, "=", v)

    print("--- diagnosis ---")
    diag_result = client._extract_diagnosis_system(html)
    for k, v in diag_result.items():
        print(k, "=", v)


def main():
    parser = argparse.ArgumentParser(description="Test scraper parsing against HTML files.")
    parser.add_argument("files", nargs="*", help="HTML files to parse (defaults provided)")
    args = parser.parse_args()

    # Default to explicit localized snapshots (no plain, non-localized files).
    default_files = [
        os.path.join(os.path.dirname(__file__), "testdata", "s_1_1_de.html"),
        os.path.join(os.path.dirname(__file__), "testdata", "s_1_1_en.html"),
        os.path.join(os.path.dirname(__file__), "testdata", "s_2_7_de.html"),
        os.path.join(os.path.dirname(__file__), "testdata", "s_2_7_en.html"),
    ]

    files = args.files or default_files

    client = StiebelEltronScrapingClient(host="local.iot", session=None)

    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                html = fh.read()
        except Exception as exc:
            print(f"Failed to read {f}: {exc}")
            continue

        parse_and_print(client, html, f)


if __name__ == '__main__':
    main()
