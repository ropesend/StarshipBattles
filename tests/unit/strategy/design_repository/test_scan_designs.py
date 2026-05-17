"""PROJ-434 Phase 0: DesignRepository.scan_designs parity with DesignLibrary.

Pin every UI-caller-visible behavior of ``scan_designs`` that the
deferred Phase 6 UI surface depends on. Each test mirrors a
corresponding ``DesignLibrary.scan_designs`` characterization, ensuring
byte-for-byte parity so Phase 1 / Phase 2 caller migrations cannot
introduce a behavior drift.
"""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from game.strategy.systems.design_repository import DesignRepository


def _write_design(folder: str, design_id: str, name: str = "Test",
                  vehicle_type: str = "Ship",
                  ship_class: str = "Fighter") -> None:
    os.makedirs(folder, exist_ok=True)
    payload = {
        "name": name,
        "ship_class": ship_class,
        "vehicle_type": vehicle_type,
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


def test_scan_designs_empty_folder_returns_empty_list(tmp_save_root):
    """Mirrors ``DesignLibrary.scan_designs`` on empty input."""
    repo = DesignRepository(tmp_save_root, empire_id=0)
    assert repo.scan_designs() == []


def test_scan_designs_skips_corrupt_files(tmp_save_root):
    """Mirrors ``DesignLibrary``'s "log + continue" path on corrupt JSON."""
    folder = os.path.join(tmp_save_root, "designs", "empire_0")
    os.makedirs(folder, exist_ok=True)
    _write_design(folder, "ok_design", name="OK")
    # Write a corrupt JSON file alongside.
    with open(os.path.join(folder, "broken.json"), "w") as fh:
        fh.write("{not-json")
    repo = DesignRepository(tmp_save_root, empire_id=0)
    designs = repo.scan_designs()
    assert len(designs) == 1
    assert designs[0].name == "OK"


def test_scan_designs_preserves_vehicle_type_field(tmp_save_root):
    """``vehicle_type`` must survive the scan (BuildQueueController filters
    by vehicle_type to populate Drop Pod / Fighter / Satellite categories)."""
    folder = os.path.join(tmp_save_root, "designs", "empire_0")
    _write_design(folder, "alpha", name="Alpha", vehicle_type="Fighter")
    _write_design(folder, "beta", name="Beta", vehicle_type="Drop Pod")
    repo = DesignRepository(tmp_save_root, empire_id=0)
    by_name = {d.name: d for d in repo.scan_designs()}
    assert by_name["Alpha"].vehicle_type == "Fighter"
    assert by_name["Beta"].vehicle_type == "Drop Pod"
