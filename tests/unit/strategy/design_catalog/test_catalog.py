"""PROJ-427 Phase 2: DesignCatalog unit tests (TDD-first).

DesignCatalog is the per-empire in-memory runtime lookup layer
introduced in Phase 2:

- ``lookup(design_id)`` is a pure in-memory dict access; no filesystem
  call, no JSON parsing.
- Per-turn filtered / list views for UI.
- Pending built-count increments held in memory (flushed through
  ``DesignRepository`` at save time by Phase 4).
- ``repopulate_from(repository)`` is the explicit refresh entry point;
  catalog is **never** repopulated mid production-tick.

Phase 2 is additive: no existing ``DesignLibrary`` caller is migrated.
The catalog plus its owning ``DesignRepository`` is exposed through
``SessionRuntimeServices`` per the PROJ-423 cross-plan absorption note.
"""
from __future__ import annotations

import os
import json
import tempfile

import pytest


def _write_design_json(folder: str, design_id: str, name: str) -> None:
    os.makedirs(folder, exist_ok=True)
    payload = {
        "name": name,
        "ship_class": "Fighter",
        "vehicle_type": "Fighter",
        "mass": 50.0,
        "layers": {},
        "_metadata": {"is_obsolete": False, "times_built": 0},
    }
    with open(os.path.join(folder, f"{design_id}.json"), "w") as fh:
        json.dump(payload, fh)


@pytest.fixture
def tmp_save_root():
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp


# ---------------------------------------------------------------------------
# In-memory lookup; no disk on hot path
# ---------------------------------------------------------------------------


def test_lookup_returns_design_by_id_without_disk_access(tmp_save_root):
    """After ``repopulate_from(repo)``, ``lookup(design_id)`` must hit
    in-memory state without calling back into the repository."""
    from game.strategy.systems.design_catalog import DesignCatalog
    from game.strategy.systems.design_repository import DesignRepository

    folder = os.path.join(tmp_save_root, "designs", "empire_0")
    _write_design_json(folder, "alpha", "Alpha")
    repo = DesignRepository(tmp_save_root, empire_id=0)

    catalog = DesignCatalog(empire_id=0)
    catalog.repopulate_from(repo)

    # After repopulate, lookups must not touch the repository again.
    class _Boom:
        def scan_designs(self):  # pragma: no cover - defensive
            raise AssertionError("catalog.lookup must not call scan_designs")

        def load_design_data(self, design_id):  # pragma: no cover - defensive
            raise AssertionError(
                f"catalog.lookup must not call load_design_data({design_id!r})"
            )

    catalog._repository_for_test = _Boom()  # type: ignore[attr-defined]

    md = catalog.lookup("alpha")
    assert md is not None
    assert md.design_id == "alpha"
    assert md.name == "Alpha"


def test_lookup_returns_none_for_missing(tmp_save_root):
    from game.strategy.systems.design_catalog import DesignCatalog
    from game.strategy.systems.design_repository import DesignRepository

    repo = DesignRepository(tmp_save_root, empire_id=0)
    catalog = DesignCatalog(empire_id=0)
    catalog.repopulate_from(repo)
    assert catalog.lookup("nope") is None


# ---------------------------------------------------------------------------
# UI filtered / list views
# ---------------------------------------------------------------------------


def test_filtered_views_for_ui_per_turn(tmp_save_root):
    """``list_designs()`` returns the per-empire metadata list cached
    in memory; same object identity on repeated calls within the same
    catalog (no disk re-read)."""
    from game.strategy.systems.design_catalog import DesignCatalog
    from game.strategy.systems.design_repository import DesignRepository

    folder = os.path.join(tmp_save_root, "designs", "empire_0")
    _write_design_json(folder, "alpha", "Alpha")
    _write_design_json(folder, "beta", "Beta")

    repo = DesignRepository(tmp_save_root, empire_id=0)
    catalog = DesignCatalog(empire_id=0)
    catalog.repopulate_from(repo)

    first = catalog.list_designs()
    second = catalog.list_designs()
    assert first is second
    names = {d.name for d in first}
    assert names == {"Alpha", "Beta"}


# ---------------------------------------------------------------------------
# Pending built-count increments — in-memory only
# ---------------------------------------------------------------------------


def test_pending_built_count_increment_does_not_write_to_disk(tmp_save_root):
    """``record_built(design_id)`` updates the in-memory pending map;
    the underlying JSON file is untouched until flushed (Phase 4)."""
    from game.strategy.systems.design_catalog import DesignCatalog
    from game.strategy.systems.design_repository import DesignRepository

    folder = os.path.join(tmp_save_root, "designs", "empire_0")
    _write_design_json(folder, "alpha", "Alpha")
    repo = DesignRepository(tmp_save_root, empire_id=0)
    catalog = DesignCatalog(empire_id=0)
    catalog.repopulate_from(repo)

    catalog.record_built("alpha")
    catalog.record_built("alpha")
    catalog.record_built("beta")

    assert catalog.pending_built_counts == {"alpha": 2, "beta": 1}

    # JSON on disk is unchanged.
    with open(os.path.join(folder, "alpha.json")) as fh:
        payload = json.load(fh)
    assert payload["_metadata"]["times_built"] == 0


# ---------------------------------------------------------------------------
# Explicit refresh
# ---------------------------------------------------------------------------


def test_refresh_repopulates_from_repository(tmp_save_root):
    """``repopulate_from(repo)`` rebuilds the in-memory map from the
    repository's current scan. New designs appear, removed designs
    disappear."""
    from game.strategy.systems.design_catalog import DesignCatalog
    from game.strategy.systems.design_repository import DesignRepository

    folder = os.path.join(tmp_save_root, "designs", "empire_0")
    _write_design_json(folder, "alpha", "Alpha")
    repo = DesignRepository(tmp_save_root, empire_id=0)
    catalog = DesignCatalog(empire_id=0)
    catalog.repopulate_from(repo)
    assert catalog.lookup("alpha") is not None
    assert catalog.lookup("beta") is None

    _write_design_json(folder, "beta", "Beta")
    catalog.repopulate_from(repo)
    assert catalog.lookup("beta") is not None


# ---------------------------------------------------------------------------
# Per-empire isolation
# ---------------------------------------------------------------------------


def test_catalog_is_per_empire(tmp_save_root):
    """Two catalogs constructed against the same save_root but
    different empire_ids see distinct contents."""
    from game.strategy.systems.design_catalog import DesignCatalog
    from game.strategy.systems.design_repository import DesignRepository

    folder0 = os.path.join(tmp_save_root, "designs", "empire_0")
    folder1 = os.path.join(tmp_save_root, "designs", "empire_1")
    _write_design_json(folder0, "alpha", "Alpha 0")
    _write_design_json(folder1, "alpha", "Alpha 1")

    repo0 = DesignRepository(tmp_save_root, empire_id=0)
    repo1 = DesignRepository(tmp_save_root, empire_id=1)

    cat0 = DesignCatalog(empire_id=0)
    cat0.repopulate_from(repo0)
    cat1 = DesignCatalog(empire_id=1)
    cat1.repopulate_from(repo1)

    assert cat0.empire_id == 0
    assert cat1.empire_id == 1
    assert cat0.lookup("alpha").name == "Alpha 0"
    assert cat1.lookup("alpha").name == "Alpha 1"


# ---------------------------------------------------------------------------
# No filesystem / no JSON in the catalog itself
# ---------------------------------------------------------------------------


def test_catalog_construction_has_no_filesystem_dependency():
    """Constructing a DesignCatalog must not require a save folder or
    repository — empty catalog is a valid initial state."""
    from game.strategy.systems.design_catalog import DesignCatalog

    catalog = DesignCatalog(empire_id=5)
    assert catalog.empire_id == 5
    assert catalog.lookup("anything") is None
    assert catalog.list_designs() == []
    assert catalog.pending_built_counts == {}
