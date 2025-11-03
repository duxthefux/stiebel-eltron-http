"""
Custom integration to integrate Stiebel Eltron ISG without Modbus with Home Assistant.

For more details about this integration, please refer to
https://github.com/pmq/stiebel_eltron_http
"""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

try:
    from homeassistant.const import CONF_HOST, Platform
    from homeassistant.helpers.aiohttp_client import async_get_clientsession
    from homeassistant.loader import async_get_loaded_integration
except Exception:  # pragma: no cover - tests inject minimal homeassistant stubs
    # Provide minimal fallbacks when Home Assistant is not available during tests.
    CONF_HOST = "host"

    class Platform:  # simple stub used only for declaration in this module
        SENSOR = "sensor"
        BINARY_SENSOR = "binary_sensor"

    def async_get_clientsession(hass):
        return None

    def async_get_loaded_integration(hass, domain):
        return None
import re
from pathlib import Path

from .const import DOMAIN, LOGGER, DEFAULT_LANGUAGE, CONF_LANGUAGE
from .const import CONF_FETCH_ENERGY, DEFAULT_FETCH_ENERGY
from .const import CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES
try:
    # Import integration parts that rely on Home Assistant. When running
    # unit tests that load individual modules by path, importing the package
    # __init__ may occur; guard these imports so tests can load submodules
    # without requiring Home Assistant to be installed.
    from .coordinator import StiebelEltronHttpDataUpdateCoordinator
    from .data import StiebelEltronHttpConfigEntry, StiebelEltronHttpData
    from .scraper import StiebelEltronScrapingClient
except Exception:  # pragma: no cover - test environment may not have HA
    StiebelEltronHttpDataUpdateCoordinator = None
    StiebelEltronHttpConfigEntry = object
    StiebelEltronHttpData = object
    StiebelEltronScrapingClient = None
    from . import dedupe

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

PLATFORMS: list[Platform | str] = [
    Platform.SENSOR,
    "binary_sensor",
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: StiebelEltronHttpConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = StiebelEltronHttpDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        # Allow the update interval to be configured via entry.options.
        update_interval=timedelta(
            minutes=int(
                entry.options.get(
                    CONF_UPDATE_INTERVAL,
                    entry.data.get(
                        CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL_MINUTES
                    ),
                )
            )
        ),
    )

    entry.runtime_data = StiebelEltronHttpData(
        client=StiebelEltronScrapingClient(
            host=entry.data[CONF_HOST],
            session=async_get_clientsession(hass),
            language=entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE),
            fetch_energy=entry.options.get(CONF_FETCH_ENERGY, entry.data.get(CONF_FETCH_ENERGY, DEFAULT_FETCH_ENERGY)),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Schedule a background deduplication task that looks for multiple
    # config entries that refer to the same physical device (same MAC)
    # and removes duplicates conservatively. This runs in the background
    # and is best-effort to avoid blocking startup.
    hass.async_create_task(_deduplicate_entries(hass))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: StiebelEltronHttpConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: StiebelEltronHttpConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, entry: StiebelEltronHttpConfigEntry) -> bool:
    """Migrate old config entries.

    We introduce a new config key `CONF_FETCH_ENERGY` in version 2. For entries
    at version 1, ensure the key exists with a sensible default.
    """
    current_version = entry.version
    LOGGER.debug("Migrating config entry %s from version %s", entry.entry_id, current_version)

    # Step 1: ensure older entries have the fetch flag present in their data
    if current_version == 1:
        new_data = dict(entry.data)
        if CONF_FETCH_ENERGY not in new_data:
            new_data[CONF_FETCH_ENERGY] = DEFAULT_FETCH_ENERGY

        # bump to version 2
        entry.version = 2
        hass.config_entries.async_update_entry(entry, data=new_data)
        LOGGER.info("Migrated config entry %s to version 2", entry.entry_id)

    # Step 2: move fetch flag from data into options so runtime settings live in entry.options
    # This migrates version 2 -> 3. Use existing option value when present, otherwise move from data.
    if entry.version == 2:
        new_data = dict(entry.data)
        new_options = dict(entry.options or {})

        if CONF_FETCH_ENERGY in new_data:
            val = new_data.pop(CONF_FETCH_ENERGY)
        else:
            val = new_options.get(CONF_FETCH_ENERGY, DEFAULT_FETCH_ENERGY)

        new_options[CONF_FETCH_ENERGY] = val

        # bump to version 3
        entry.version = 3
        hass.config_entries.async_update_entry(entry, data=new_data, options=new_options)
        LOGGER.info("Migrated config entry %s to version 3 (moved fetch flag into options)", entry.entry_id)

    return True


async def _deduplicate_entries(hass: HomeAssistant) -> None:
    """Detect and remove duplicate config entries that point to the same MAC.

    Strategy (conservative):
      - Group entries by normalized unique_id or device id (hex-only lowercase MAC).
      - For each group with >1 entries, select a primary entry with the largest
        combined size of `data` and `options` (heuristic for most-complete entry).
      - Remove the other entries via `async_remove` and log actions.

    This runs in background and is best-effort. It will not attempt complex
    merges; it simply removes duplicates and leaves the primary intact.
    """
    try:
        entries = hass.config_entries.async_entries(DOMAIN)
        groups: dict[str, list] = {}
        report: dict = {"found": 0, "groups": {}}

        def norm(val: str | None) -> str | None:
            if not val:
                return None
            return re.sub(r"[^0-9a-fA-F]", "", str(val)).lower()

        for e in entries:
            uid = norm(e.unique_id) or norm(e.data.get("device_id") if isinstance(e.data, dict) else None) or norm(e.data.get("mac_address") if isinstance(e.data, dict) else None)
            if not uid:
                continue
            groups.setdefault(uid, []).append(e)

        for uid, group in groups.items():
            if len(group) <= 1:
                continue
            # choose primary with a smarter heuristic:
            # - more option keys (prefer entries configured via UI)
            # - more data keys
            # - higher entry.version
            def completeness_score(ent):
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

            sorted_group = sorted(group, key=lambda x: completeness_score(x), reverse=True)
            primary = sorted_group[0]
            duplicates = sorted_group[1:]

            LOGGER.info("Found %d duplicate stiebel_eltron_http entries for MAC %s; keeping entry %s", len(group), uid, primary.entry_id)
            # record into report
            report["groups"][uid] = {
                "primary": primary.entry_id,
                "entries": [{"entry_id": e.entry_id, "title": e.title, "unique_id": e.unique_id} for e in group],
            }
            # Merge missing data/options from duplicates into primary, then remove duplicates
            merged_data = dict(primary.data or {})
            merged_options = dict(primary.options or {})
            merged_any = False
            for dup in duplicates:
                try:
                    dup_data = dict(dup.data or {})
                    dup_options = dict(dup.options or {})
                    # copy missing data keys
                    new_data_keys = [k for k in dup_data.keys() if k not in merged_data]
                    for k in new_data_keys:
                        merged_data[k] = dup_data[k]
                    # copy missing option keys
                    new_option_keys = [k for k in dup_options.keys() if k not in merged_options]
                    for k in new_option_keys:
                        merged_options[k] = dup_options[k]

                    if new_data_keys or new_option_keys:
                        merged_any = True
                        LOGGER.info(
                            "Merging keys from duplicate %s into primary %s: data=%s options=%s",
                            dup.entry_id,
                            primary.entry_id,
                            new_data_keys,
                            new_option_keys,
                        )

                    # remove the duplicate entry
                    LOGGER.info("Removing duplicate entry %s (title=%s) for MAC %s", dup.entry_id, dup.title, uid)
                    await hass.config_entries.async_remove(dup.entry_id)
                except Exception as exc:  # pylint: disable=broad-except
                    LOGGER.exception("Failed to process/remove duplicate entry %s: %s", dup.entry_id, exc)

            # If we merged anything, update the primary entry with the unioned data/options
            if merged_any:
                try:
                    hass.config_entries.async_update_entry(primary, data=merged_data, options=merged_options)
                    LOGGER.info("Updated primary entry %s with merged data/options", primary.entry_id)
                except Exception:  # pylint: disable=broad-except
                    LOGGER.exception("Failed to update primary entry %s after merging duplicates", primary.entry_id)

        report["found"] = sum(1 for g in report["groups"].values())

        # Write a dry-run report file to HA config dir so the operator can inspect
        # proposed actions before they are applied. To actually apply the changes
        # create an empty file named '.stiebel_dedupe_apply' in the HA config dir.
        try:
            # Helper to write JSON using a background thread to avoid blocking the
            # main event loop (Path.open / open are blocking calls).
            def _write_json(path: Path, obj: dict) -> None:
                import json

                with path.open("w", encoding="utf-8") as fh:
                    json.dump(obj, fh, indent=2)

            config_dir = hass.config.path()
            report_path = config_dir and Path(config_dir) / ".stiebel_dedupe_report.json"
            apply_flag = config_dir and Path(config_dir) / ".stiebel_dedupe_apply"
            if report_path:
                # write using Home Assistant's executor to avoid blocking the event loop
                await hass.async_add_executor_job(_write_json, report_path, report)
                LOGGER.info("Wrote dedupe report to %s", report_path)

            # If the operator placed the apply flag file, perform the deletions now
            apply_exists = False
            if apply_flag:
                # check existence in executor
                apply_exists = await hass.async_add_executor_job(apply_flag.exists)

            if apply_exists:
                LOGGER.info("Apply flag found (%s): performing dedupe actions now", apply_flag)
                # Re-run the logic to perform merges/removals (we already did a dry-run above)
                await _perform_dedupe_actions(hass, groups)
                applied_path = Path(config_dir) / ".stiebel_dedupe_applied.json"
                await hass.async_add_executor_job(
                    _write_json,
                    applied_path,
                    {"applied": True, "groups": list(report["groups"].keys())},
                )
                LOGGER.info("Wrote dedupe applied report to %s", applied_path)
        except Exception:
            LOGGER.exception("Failed to write dedupe report or apply actions")
    except Exception:  # keep dedupe best-effort
        LOGGER.exception("Deduplication task failed")


async def _perform_dedupe_actions(hass: HomeAssistant, groups: dict) -> None:
    """Perform merges and removals for the provided groups mapping.

    This extracts the merging/removal logic from the dry-run function so we can
    call it when the user confirms via the apply flag file.
    """
    # Delegate actual performing work to the dedupe module's performer. We keep
    # this thin wrapper to preserve the original internal API so callers in
    # this module do not need to be changed elsewhere.
    plans = dedupe.plan_groups(groups)
    if plans:
        await dedupe.perform_dedupe_actions(hass, plans)
