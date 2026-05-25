"""Mode-scoped data lifecycle.

Symmetric loader for game data. The default game data path
(`data/`), the Combat Lab data path (`combat_lab/data/`), and any future
mod path (`mods/<name>/data/`) are all just directories that hold the
same set of JSON files. The loader does not privilege any one path —
each mode picks which to load on entry and clears the registry on exit.

Invariant: the global registry is populated only while a mode owns it.
Boot leaves the registry empty; the main menu has no game data loaded.

Public API:
    load_data_from_path(data_dir): hydrate registry from a directory.
    unload_data(): clear registry; reset active data path.
    get_active_data_path(): inspect the currently loaded path.
    register_data_cache_invalidator(fn): plug a downstream JSON cache
        into the lifecycle so it resets on every load/unload.
"""
from __future__ import annotations

import logging
import os
from typing import Callable, List, Optional

from game.core.paths import Paths
from game.core.registry import (
    get_default_registry_manager,
    get_default_registry_provider,
)
from game.core.resources import ResourceCatalog
from game.simulation.components.component import load_components, load_modifiers
from game.simulation.entities.ship_loader import (
    initialize_ship_data,
    load_vehicle_classes,
)

logger = logging.getLogger(__name__)

# Process-global list of downstream cache invalidators. Modules with
# JSON-backed module-level caches register an invalidator at import
# time; load/unload fires every registered callback so caches do not
# outlive the data set they were derived from.
_cache_invalidators: List[Callable[[], None]] = []


def register_data_cache_invalidator(fn: Callable[[], None]) -> None:
    """Register a callback to fire on every data-set transition.

    Modules that hold JSON-derived caches at module scope should call
    this at import time. Both `load_data_from_path` and `unload_data`
    invoke every registered invalidator after clearing the registry.
    """
    if fn not in _cache_invalidators:
        _cache_invalidators.append(fn)


def _invoke_invalidators() -> None:
    for fn in _cache_invalidators:
        try:
            fn()
        except Exception:  # Intentional broad catch: an invalidator failure must not block mode transitions
            logger.exception("Data cache invalidator failed")


def load_data_from_path(data_dir: str) -> None:
    """Hydrate the global registry from JSON files in `data_dir`.

    Symmetric across stock / combat-lab / mod paths. After this returns:
      - components, modifiers, vehicle_classes, resources registries
        are populated from `data_dir`.
      - ResourceCatalog for the active path is attached to the manager.
      - Component derivatives are present on disk (idempotent).
      - All registered downstream caches have been invalidated.
      - `RegistryManager.active_data_path` records `data_dir`.

    Uses the registry's `unfrozen()` context internally — safe to call
    whether the registry is currently frozen or not.

    Raises:
        RuntimeError: if no default RegistryManager has been installed
            (call ApplicationContext.create_production() first).
    """
    logger.info(f"Loading game data from {data_dir}")
    mgr = get_default_registry_manager()
    if mgr is None:
        raise RuntimeError(
            "No default RegistryManager installed. "
            "Call ApplicationContext.create_production() before load_data_from_path()."
        )

    provider = get_default_registry_provider()
    with mgr.unfrozen():
        mgr.clear()

        load_modifiers(
            os.path.join(data_dir, "modifiers.json"),
            registry_provider=provider,
        )
        load_components(
            os.path.join(data_dir, "components.json"),
            registry_provider=provider,
        )
        load_vehicle_classes(
            os.path.join(data_dir, "vehicleclasses.json"),
            registry_provider=provider,
        )

        # ResourceCatalog: optional per data set. combat_lab/data does
        # not ship a resources.json today (it reuses stock resources),
        # so fall back to the default file when the active path has
        # none. Future mods that add resources put a resources.json in
        # their data dir and it picks up automatically.
        resources_file = os.path.join(data_dir, "resources.json")
        if not os.path.isfile(resources_file):
            resources_file = Paths.RESOURCES_FILE
        catalog = ResourceCatalog.from_json(resources_file)
        for defn in catalog.all_definitions():
            mgr.resources[defn.id] = {
                "id": defn.id,
                "name": defn.name,
                "description": defn.description,
                "display_group": defn.display_group,
                "has_quality": defn.has_quality,
            }
        mgr.set_resource_catalog(catalog)

        # Ship templates / vehicle layers — scans Paths.ROOT_DIR for
        # the in-repo ship-template tree. Future mods with their own
        # templates would generalise this; out of scope here.
        initialize_ship_data(Paths.ROOT_DIR, registry_provider=provider)

        # Note: component-derivative PNG generation is a file-system
        # scan that does NOT depend on registry data; it stays in
        # `game.app_bootstrap.bootstrap()` (runs once per process) so
        # parallel test workers don't race on the manifest file.

        _invoke_invalidators()

    mgr.active_data_path = data_dir


def unload_data() -> None:
    """Clear the registry and reset the active data path.

    Called when a mode exits back to the main menu. Idempotent — a
    second call on an already-empty registry is harmless. Fires every
    registered cache invalidator so downstream caches do not survive
    the unload.
    """
    logger.info("Unloading game data")
    mgr = get_default_registry_manager()
    if mgr is None:
        return

    with mgr.unfrozen():
        mgr.clear()
        _invoke_invalidators()

    mgr.active_data_path = None


def get_active_data_path() -> Optional[str]:
    """Return the registry's active data path, or None if none is loaded."""
    mgr = get_default_registry_manager()
    if mgr is None:
        return None
    return getattr(mgr, "active_data_path", None)


def _clear_data_cache_invalidators() -> None:
    """Test seam: drop every registered invalidator.

    Production code should not call this. Exposed for tests that need
    to count invalidator fires deterministically without cross-test
    contamination from other modules' import-time registrations.
    """
    _cache_invalidators.clear()
