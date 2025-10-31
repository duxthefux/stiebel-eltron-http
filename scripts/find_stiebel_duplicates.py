"""
Find and report potential duplicate stiebel_eltron_http config entries in a Home Assistant
`.storage/core.config_entries` file.

Usage:
  python scripts/find_stiebel_duplicates.py --config-dir "C:\path\to\.homeassistant"

The script is read-only by default and will report entries grouped by normalized MAC
(unique_id or data.device id). It helps identify duplicates so you can remove/merge
them in the Home Assistant UI.

It does NOT modify any files. If you want a safe, automated merge helper, I can add
one but prefer to keep it manual to avoid accidental data loss.
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_HA_DIR = Path.home() / ".homeassistant"


def normalize_mac(mac: str | None) -> str | None:
    if not mac:
        return None
    return re.sub(r"[^0-9a-fA-F]", "", mac).lower()


def load_core_config_entries(config_dir: Path) -> dict:
    path = config_dir / ".storage" / "core.config_entries"
    if not path.exists():
        raise FileNotFoundError(f"Could not find core.config_entries at {path}")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def gather_stiebel_entries(core_json: dict) -> List[Dict[str, Any]]:
    entries = core_json.get("data", {}).get("entries", [])
    stiebel = [e for e in entries if e.get("domain") == "stiebel_eltron_http"]
    return stiebel


def load_device_registry(config_dir: Path) -> dict | None:
    path = config_dir / ".storage" / "core.device_registry"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def gather_devices(device_json: dict | None) -> List[Dict[str, Any]]:
    if not device_json:
        return []
    return device_json.get("data", {}).get("devices", [])


def report_duplicates(entries: List[Dict[str, Any]]) -> None:
    # Group entries by normalized unique_id and by host
    by_norm_mac: Dict[str, List[Dict[str, Any]]] = {}
    by_host: Dict[str, List[Dict[str, Any]]] = {}

    for e in entries:
        unique_id = e.get("unique_id")
        data = e.get("data", {}) or {}
        host = data.get("host") or data.get("CONF_HOST") or data.get("host_name")
        device_id = data.get("device_id") or data.get("CONF_DEVICE_ID") or data.get("mac") or data.get("mac_address")
        norm = normalize_mac(unique_id) or normalize_mac(device_id)
        if norm:
            by_norm_mac.setdefault(norm, []).append(e)
        if host:
            by_host.setdefault(host, []).append(e)

    print("Found %d stiebel_eltron_http entries" % (len(entries)))
    print()

    duplicates_found = False
    print("Entries grouped by normalized MAC (unique_id/device id):")
    for norm, group in by_norm_mac.items():
        print(f"- {norm}: {len(group)} entry(ies)")
        for g in group:
            print(f"    entry_id={g.get('entry_id')}, title={g.get('title')}, unique_id={g.get('unique_id')}, data_host={g.get('data',{}).get('host')}")
        if len(group) > 1:
            duplicates_found = True
    print()

    print("Entries grouped by host:")
    for host, group in by_host.items():
        print(f"- {host}: {len(group)} entry(ies)")
        for g in group:
            print(f"    entry_id={g.get('entry_id')}, title={g.get('title')}, unique_id={g.get('unique_id')}")
        if len(group) > 1:
            duplicates_found = True
    print()

    if duplicates_found:
        print("POTENTIAL DUPLICATES FOUND. Review the groups above and remove or merge duplicates in Home Assistant UI.")
    else:
        print("No obvious duplicates found by normalized MAC or host.")


def report_device_registry(devices: List[Dict[str, Any]], stiebel_entries: List[Dict[str, Any]], check_macs: List[str] | None = None) -> None:
    if not devices:
        print("No device registry data found (.storage/core.device_registry) or file missing.")
        return

    # Build mapping from normalized MAC -> device entries
    mac_map: Dict[str, List[Dict[str, Any]]] = {}
    for d in devices:
        # identifiers and connections are lists of tuples/pairs
        ids = d.get("identifiers") or []
        conns = d.get("connections") or []
        candidates: List[str] = []
        for ident in ids:
            if isinstance(ident, (list, tuple)) and len(ident) >= 2:
                candidates.append(str(ident[1]))
        for conn in conns:
            if isinstance(conn, (list, tuple)) and len(conn) >= 2:
                candidates.append(str(conn[1]))

        for c in candidates:
            norm = normalize_mac(c)
            if norm:
                mac_map.setdefault(norm, []).append(d)

    print("Device registry entries (matching MACs):")
    for norm, devs in mac_map.items():
        print(f"- {norm}: {len(devs)} device(s)")
        for dv in devs:
            print(f"    id={dv.get('id')}, name={dv.get('name')}, manufacturer={dv.get('manufacturer')}, model={dv.get('model')}")

    # If the user provided MACs to check, show mapping
    if check_macs:
        print()
        print("Checking requested MACs against device registry and stiebel entries:")
        for raw in check_macs:
            n = normalize_mac(raw)
            print(f"MAC {raw} -> normalized {n}")
            devs = mac_map.get(n)
            if devs:
                for dv in devs:
                    print(f"  Found device registry entry id={dv.get('id')}, name={dv.get('name')}")
            else:
                print("  No device registry entry found for this MAC")

            # find any stiebel config entries that reference this MAC
            matches = []
            for e in stiebel_entries:
                uid = normalize_mac(e.get('unique_id'))
                data = e.get('data') or {}
                device_id = normalize_mac(data.get('device_id') or data.get('mac') or data.get('mac_address'))
                if n and (n == uid or n == device_id):
                    matches.append(e)
            if matches:
                for m in matches:
                    print(f"  -> referenced by config entry {m.get('entry_id')} title={m.get('title')} unique_id={m.get('unique_id')}")
            else:
                print("  Not referenced by any stiebel_eltron_http config entry")


def load_entity_registry(config_dir: Path) -> dict | None:
    path = config_dir / ".storage" / "core.entity_registry"
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def gather_entities(entity_json: dict | None) -> List[Dict[str, Any]]:
    if not entity_json:
        return []
    return entity_json.get("data", {}).get("entities", [])


def build_json_report(config_dir: Path, entries: List[Dict[str, Any]], devices: List[Dict[str, Any]], entities: List[Dict[str, Any]], check_macs: List[str] | None) -> dict:
    """Build a structured report correlating config entries, devices, and entities.

    The returned dict is safe to serialize to JSON for offline inspection.
    """
    report: Dict[str, Any] = {
        "meta": {"config_dir": str(config_dir), "generated_by": "find_stiebel_duplicates.py"},
        "stiebel_entries": [],
        "devices": [],
        "entities": [],
        "mac_checks": {},
    }

    # entries
    for e in entries:
        report["stiebel_entries"].append({
            "entry_id": e.get("entry_id"),
            "title": e.get("title"),
            "unique_id": e.get("unique_id"),
            "data": e.get("data"),
            "options": e.get("options"),
        })

    # devices
    for d in devices:
        report["devices"].append({
            "id": d.get("id"),
            "name": d.get("name"),
            "manufacturer": d.get("manufacturer"),
            "model": d.get("model"),
            "identifiers": d.get("identifiers"),
            "connections": d.get("connections"),
        })

    # entities
    for ent in entities:
        report["entities"].append({
            "entity_id": ent.get("entity_id"),
            "unique_id": ent.get("unique_id"),
            "device_id": ent.get("device_id"),
            "area_id": ent.get("area_id"),
            "config_entry_id": ent.get("config_entry_id"),
        })

    # check MACs mapping to devices and entries
    if check_macs:
        for raw in check_macs:
            n = normalize_mac(raw)
            report["mac_checks"][raw] = {"normalized": n, "devices": [], "stiebel_entries": []}
            if n:
                for d in devices:
                    # any identifier/connection matching normalized value
                    ids = [str(x[1]) for x in (d.get("identifiers") or []) if isinstance(x, (list, tuple)) and len(x) > 1]
                    conns = [str(x[1]) for x in (d.get("connections") or []) if isinstance(x, (list, tuple)) and len(x) > 1]
                    if any(normalize_mac(x) == n for x in ids + conns):
                        report["mac_checks"][raw]["devices"].append(d.get("id"))
                for e in entries:
                    uid = normalize_mac(e.get("unique_id"))
                    data = e.get("data") or {}
                    device_id = normalize_mac(data.get("device_id") or data.get("mac") or data.get("mac_address"))
                    if n and (n == uid or n == device_id):
                        report["mac_checks"][raw]["stiebel_entries"].append(e.get("entry_id"))

    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-dir", type=str, default=str(DEFAULT_HA_DIR), help="Path to Home Assistant config directory")
    parser.add_argument("--check-macs", type=str, default=None, help="Comma-separated MAC addresses to check against device registry and config entries")
    parser.add_argument("--output-json", action="store_true", help="Write a JSON report to <config_dir>/.stiebel_duplicates_report.json")
    args = parser.parse_args()

    config_dir = Path(args.config_dir)
    if not config_dir.exists():
        print(f"Config dir {config_dir} does not exist")
        raise SystemExit(1)

    try:
        core = load_core_config_entries(config_dir)
    except FileNotFoundError as exc:
        print(exc)
        raise SystemExit(1)

    entries = gather_stiebel_entries(core)
    if not entries:
        print("No stiebel_eltron_http entries found in core.config_entries")
        raise SystemExit(0)

    report_duplicates(entries)

    # Also load device registry and report MAC/device correlations if available
    device_json = load_device_registry(config_dir)
    devices = gather_devices(device_json)
    check_macs = [m.strip() for m in args.check_macs.split(",")] if args.check_macs else None
    report_device_registry(devices, entries, check_macs)

    # Also load entity registry and optionally write a JSON report
    entity_json = load_entity_registry(config_dir)
    entities = gather_entities(entity_json)

    if args.output_json:
        report = build_json_report(config_dir, entries, devices, entities, check_macs)
        outpath = config_dir / ".stiebel_duplicates_report.json"
        with outpath.open("w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        print(f"Wrote JSON report to {outpath}")


if __name__ == "__main__":
    main()
