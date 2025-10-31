"""Dedupe planner and performer helpers.

This module exposes a pure planner that computes which entry in a group
should be kept (primary) and which keys would be merged from duplicates.
It also exposes an async performer that applies the merges/removals using
Home Assistant's config_entries API.
"""
from typing import Dict, List


def _completeness_score(ent) -> int:
    score = 0
    try:
        score += (len(ent.options) if ent.options else 0) * 10
    except Exception:
        score += 0
    try:
        score += (len(ent.data) if ent.data else 0) * 2
    except Exception:
        score += 0
    try:
        score += int(getattr(ent, "version", 0))
    except Exception:
        score += 0
    return score


def plan_group(group: List) -> Dict:
    """Create a dedupe plan for a single group of entries.

    Returns a dict with keys:
      - primary: the chosen primary entry object
      - duplicates: list of duplicate entry objects (ordered)
      - duplicate_plans: list of dicts for each duplicate with keys
            'dup', 'new_data_keys', 'new_option_keys'
      - merged_data: dict representing the merged data after copying missing keys
      - merged_options: dict representing the merged options after copying missing keys
      - merged_any: True if any keys would be merged
    """
    if not group:
        return {}

    sorted_group = sorted(group, key=lambda x: _completeness_score(x), reverse=True)
    primary = sorted_group[0]
    duplicates = sorted_group[1:]

    merged_data = dict(primary.data or {})
    merged_options = dict(primary.options or {})
    merged_any = False

    duplicate_plans = []
    for dup in duplicates:
        dup_data = dict(dup.data or {})
        dup_options = dict(dup.options or {})
        new_data_keys = [k for k in dup_data.keys() if k not in merged_data]
        for k in new_data_keys:
            merged_data[k] = dup_data[k]
        new_option_keys = [k for k in dup_options.keys() if k not in merged_options]
        for k in new_option_keys:
            merged_options[k] = dup_options[k]

        if new_data_keys or new_option_keys:
            merged_any = True

        duplicate_plans.append(
            {"dup": dup, "new_data_keys": new_data_keys, "new_option_keys": new_option_keys}
        )

    return {
        "primary": primary,
        "duplicates": duplicates,
        "duplicate_plans": duplicate_plans,
        "merged_data": merged_data,
        "merged_options": merged_options,
        "merged_any": merged_any,
    }


def plan_groups(groups: Dict[str, List]) -> Dict[str, Dict]:
    """Plan dedupe actions for all groups.

    Input: mapping uid -> list(entries)
    Output: mapping uid -> plan (as returned by plan_group)
    """
    plans: Dict[str, Dict] = {}
    for uid, group in groups.items():
        if not group or len(group) <= 1:
            continue
        plans[uid] = plan_group(group)
    return plans


async def perform_dedupe_actions(hass, plans: Dict[str, Dict]) -> None:
    """Perform merges and removals for the provided plans mapping.

    plans should be the output of `plan_groups`.
    """
    from . import LOGGER

    for uid, plan in plans.items():
        group = [plan["primary"]] + plan["duplicates"]
        primary = plan["primary"]

        merged_data = dict(primary.data or {})
        merged_options = dict(primary.options or {})
        merged_any = False

        for dup_plan in plan["duplicate_plans"]:
            dup = dup_plan["dup"]
            new_data_keys = dup_plan["new_data_keys"]
            new_option_keys = dup_plan["new_option_keys"]
            for k in new_data_keys:
                merged_data[k] = (dup.data or {}).get(k)
            for k in new_option_keys:
                merged_options[k] = (dup.options or {}).get(k)

            if new_data_keys or new_option_keys:
                merged_any = True
                LOGGER.info(
                    "Merging keys from duplicate %s into primary %s: data=%s options=%s",
                    dup.entry_id,
                    primary.entry_id,
                    new_data_keys,
                    new_option_keys,
                )

            LOGGER.info("Removing duplicate entry %s (title=%s) for MAC %s", dup.entry_id, dup.title, uid)
            try:
                await hass.config_entries.async_remove(dup.entry_id)
            except Exception as exc:  # pylint: disable=broad-except
                LOGGER.exception("Failed to process/remove duplicate entry %s: %s", dup.entry_id, exc)

        if merged_any:
            try:
                hass.config_entries.async_update_entry(primary, data=merged_data, options=merged_options)
                LOGGER.info("Updated primary entry %s with merged data/options", primary.entry_id)
            except Exception:
                LOGGER.exception("Failed to update primary entry %s after merging duplicates", primary.entry_id)
