"""PROJ-434 Phase 0: DesignRepository.load_design_data — already added by
PROJ-427 Phase 1 but pin the UI-facing parity contract used by
``BuildQueueController`` / ``BuildQueueDragHandler``.
"""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from game.strategy.systems.design_repository import (
    DesignLoadResult,
    DesignRepository,
)


@pytest.fixture
def tmp_save_root():
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp


def _write_design(folder: str, design_id: str, name: str = "Test") -> None:
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


def test_load_design_data_returns_ok_with_data(tmp_save_root):
    folder = os.path.join(tmp_save_root, "designs", "empire_0")
    _write_design(folder, "alpha", name="Alpha")
    repo = DesignRepository(tmp_save_root, empire_id=0)
    result = repo.load_design_data("alpha")
    assert isinstance(result, DesignLoadResult)
    assert result.success
    assert result.data["name"] == "Alpha"


def test_load_design_data_not_found(tmp_save_root):
    repo = DesignRepository(tmp_save_root, empire_id=0)
    result = repo.load_design_data("nope")
    assert not result.success
    assert result.error_type == "not_found"


def test_get_design_path_returns_full_path_under_per_empire_folder(
    tmp_save_root,
):
    """``BuildQueuePortraitLoader`` uses ``get_design_path`` to key its
    portrait cache. Must return ``<save_root>/designs/empire_<id>/<id>.json``."""
    repo = DesignRepository(tmp_save_root, empire_id=2)
    path = repo.get_design_path("frigate_alpha")
    expected = os.path.join(
        tmp_save_root, "designs", "empire_2", "frigate_alpha.json"
    )
    assert path == expected


def test_mark_obsolete_alias(tmp_save_root):
    """``mark_obsolete`` is the UI-facing alias for ``mark_design_obsolete``
    (DesignLibrary parity: callers use ``library.mark_obsolete(id, flag)``).
    """
    folder = os.path.join(tmp_save_root, "designs", "empire_0")
    _write_design(folder, "alpha", name="Alpha")
    repo = DesignRepository(tmp_save_root, empire_id=0)
    ok, _ = repo.mark_obsolete("alpha", True)
    assert ok
    with open(os.path.join(folder, "alpha.json")) as fh:
        payload = json.load(fh)
    assert payload["_metadata"]["is_obsolete"] is True
