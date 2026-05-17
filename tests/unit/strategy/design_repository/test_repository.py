"""PROJ-427 Phase 1: DesignRepository unit tests (TDD-first).

DesignRepository is the new filesystem + JSON persistence layer
extracted from DesignLibrary. Phase 1 is purely additive: the
repository must work standalone with no caller migration.

Contract (per phase_1_checklist.md):

- Resolves the save-folder path from constructor inputs.
- Creates the save folder if missing.
- ``scan_designs()`` returns ``DesignLoadResult``-shape-compatible
  ``DesignMetadata`` entries (the existing list contract from
  ``DesignLibrary.scan_designs``).
- ``save_design(...)`` writes design JSON to the correct per-empire
  path.
- ``load_design_data(...)`` returns a ``DesignLoadResult`` with the
  current ``data`` / ``error`` / ``error_type`` shape unchanged.
- ``mark_design_obsolete(...)`` flips the ``_metadata.is_obsolete``
  flag on disk.
- ``increment_built_count(...)`` persists the ``times_built`` delta to
  disk.

Phase 2 layers ``DesignCatalog`` on top; Phases 3-6 migrate callers.
``DesignLibrary`` is **not** removed in this phase.
"""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from game.strategy.systems.design_library import DesignLoadResult


def _write_design(designs_folder: str, design_id: str, name: str = "Test") -> None:
    os.makedirs(designs_folder, exist_ok=True)
    payload = {
        "name": name,
        "ship_class": "Fighter",
        "vehicle_type": "Fighter",
        "mass": 50.0,
        "layers": {},
        "_metadata": {
            "is_obsolete": False,
            "times_built": 0,
        },
    }
    with open(os.path.join(designs_folder, f"{design_id}.json"), "w") as fh:
        json.dump(payload, fh)


@pytest.fixture
def tmp_save_root():
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp


# ---------------------------------------------------------------------------
# Folder resolution + creation
# ---------------------------------------------------------------------------


def test_locates_save_folder_for_empire(tmp_save_root):
    """Repository resolves to ``<save_root>/designs/empire_<id>``."""
    from game.strategy.systems.design_repository import DesignRepository

    repo = DesignRepository(tmp_save_root, empire_id=2)
    expected = os.path.join(tmp_save_root, "designs", "empire_2")
    assert repo.designs_folder == expected


def test_creates_save_folder_if_missing(tmp_save_root):
    """Constructing the repository creates the per-empire designs folder
    if it does not already exist on disk."""
    from game.strategy.systems.design_repository import DesignRepository

    target = os.path.join(tmp_save_root, "designs", "empire_7")
    assert not os.path.exists(target)
    DesignRepository(tmp_save_root, empire_id=7)
    assert os.path.isdir(target)


def test_repository_uses_temp_folder_when_no_save_path():
    """No-savegame mode (standalone Workshop) routes to a temp folder
    rooted on ``starship_battles_temp_designs``, mirroring DesignLibrary's
    behavior so the additive extraction is byte-compatible."""
    from game.strategy.systems.design_repository import DesignRepository

    repo = DesignRepository(None, empire_id=3)
    assert "starship_battles_temp_designs" in repo.designs_folder
    assert "empire_3" in repo.designs_folder


# ---------------------------------------------------------------------------
# scan_designs shape — must be byte-identical to DesignLibrary.scan_designs
# ---------------------------------------------------------------------------


def test_scan_designs_returns_design_metadata_list(tmp_save_root):
    """``scan_designs()`` returns a ``list[DesignMetadata]``: same shape
    as ``DesignLibrary.scan_designs()`` today."""
    from game.strategy.data.design_metadata import DesignMetadata
    from game.strategy.systems.design_repository import DesignRepository

    designs_folder = os.path.join(tmp_save_root, "designs", "empire_0")
    _write_design(designs_folder, "alpha", name="Alpha Frigate")
    _write_design(designs_folder, "beta", name="Beta Cruiser")

    repo = DesignRepository(tmp_save_root, empire_id=0)
    result = repo.scan_designs()

    assert isinstance(result, list)
    assert len(result) == 2
    for entry in result:
        assert isinstance(entry, DesignMetadata)
    names = {d.name for d in result}
    assert names == {"Alpha Frigate", "Beta Cruiser"}


# ---------------------------------------------------------------------------
# save_design
# ---------------------------------------------------------------------------


def test_save_design_writes_json_to_correct_path(tmp_save_root):
    """``save_design`` writes a ``<design_id>.json`` file under the
    per-empire folder."""
    from game.strategy.systems.design_repository import DesignRepository

    repo = DesignRepository(tmp_save_root, empire_id=0)
    repo.save_design_data(
        "my_ship",
        {
            "name": "My Ship",
            "ship_class": "Frigate",
            "vehicle_type": "Ship",
            "mass": 100.0,
            "layers": {},
        },
    )
    expected = os.path.join(tmp_save_root, "designs", "empire_0", "my_ship.json")
    assert os.path.exists(expected)
    with open(expected) as fh:
        payload = json.load(fh)
    assert payload["name"] == "My Ship"


# ---------------------------------------------------------------------------
# load_design_data — DesignLoadResult shape preserved
# ---------------------------------------------------------------------------


def test_load_design_data_returns_design_load_result_ok(tmp_save_root):
    """Successful load returns ``DesignLoadResult.ok(data)`` — same shape
    as DesignLibrary.load_design_data today."""
    from game.strategy.systems.design_repository import DesignRepository

    designs_folder = os.path.join(tmp_save_root, "designs", "empire_0")
    _write_design(designs_folder, "alpha", name="Alpha Frigate")

    repo = DesignRepository(tmp_save_root, empire_id=0)
    result = repo.load_design_data("alpha")

    assert isinstance(result, DesignLoadResult)
    assert result.success is True
    assert result.data is not None
    assert result.data["name"] == "Alpha Frigate"
    assert result.error is None
    assert result.error_type is None


def test_load_design_data_returns_not_found_for_missing(tmp_save_root):
    """Missing design returns ``DesignLoadResult.not_found`` — same
    error_type token as DesignLibrary today."""
    from game.strategy.systems.design_repository import DesignRepository

    repo = DesignRepository(tmp_save_root, empire_id=0)
    result = repo.load_design_data("nope")

    assert isinstance(result, DesignLoadResult)
    assert result.success is False
    assert result.error_type == "not_found"


# ---------------------------------------------------------------------------
# mark_design_obsolete
# ---------------------------------------------------------------------------


def test_mark_design_obsolete_updates_repository_state(tmp_save_root):
    """``mark_design_obsolete`` flips ``_metadata.is_obsolete`` to True
    on disk."""
    from game.strategy.systems.design_repository import DesignRepository

    designs_folder = os.path.join(tmp_save_root, "designs", "empire_0")
    _write_design(designs_folder, "alpha")

    repo = DesignRepository(tmp_save_root, empire_id=0)
    ok, _msg = repo.mark_design_obsolete("alpha", is_obsolete=True)
    assert ok

    with open(os.path.join(designs_folder, "alpha.json")) as fh:
        payload = json.load(fh)
    assert payload["_metadata"]["is_obsolete"] is True


# ---------------------------------------------------------------------------
# increment_built_count
# ---------------------------------------------------------------------------


def test_increment_built_count_persists_to_disk(tmp_save_root):
    """``increment_built_count`` bumps ``_metadata.times_built`` and
    persists it to the JSON file."""
    from game.strategy.systems.design_repository import DesignRepository

    designs_folder = os.path.join(tmp_save_root, "designs", "empire_0")
    _write_design(designs_folder, "alpha")

    repo = DesignRepository(tmp_save_root, empire_id=0)
    assert repo.increment_built_count("alpha") is True

    with open(os.path.join(designs_folder, "alpha.json")) as fh:
        payload = json.load(fh)
    assert payload["_metadata"]["times_built"] == 1

    # Idempotent reapplication keeps counting up.
    repo.increment_built_count("alpha")
    with open(os.path.join(designs_folder, "alpha.json")) as fh:
        payload2 = json.load(fh)
    assert payload2["_metadata"]["times_built"] == 2
