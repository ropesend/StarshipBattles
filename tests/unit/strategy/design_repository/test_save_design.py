"""PROJ-434 Phase 0: DesignRepository.save_design (rich workshop flow).

The rich variant on the repository welds metadata embedding +
overwrite-protection against built designs + on-disk write. It does
NOT invalidate any catalog cache — that's the catalog wrapper's job
(``DesignCatalog.save_design`` calls this + then ``invalidate(...)``).

Parity contract with ``DesignLibrary.save_design``:
- Returns ``(success: bool, message: str)``.
- Refuses to overwrite a design whose id is in ``built_designs``.
- Preserves ``created_date`` / ``times_built`` / ``is_obsolete`` from
  the existing on-disk metadata when updating.
- Embeds the new metadata via ``DesignMetadata.embed_in_ship_data``.
"""
from __future__ import annotations

import json
import os
import tempfile
from unittest.mock import MagicMock

import pytest

from game.strategy.systems.design_repository import DesignRepository


def _mock_ship(name="Test Ship", ship_class="Escort",
               vehicle_type="Ship", mass=1000.0):
    ship = MagicMock()
    ship.name = name
    ship.ship_class = ship_class
    ship.vehicle_type = vehicle_type
    ship.mass = mass
    ship.theme_id = "Federation"
    ship.layers = {}
    ship.to_dict.return_value = {
        "name": name,
        "ship_class": ship_class,
        "vehicle_type": vehicle_type,
        "mass": mass,
        "layers": {},
    }
    return ship


@pytest.fixture
def tmp_save_root():
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp


def test_save_design_writes_file_with_metadata(tmp_save_root):
    """Saving writes ``<id>.json`` under per-empire folder with embedded
    ``_metadata``."""
    repo = DesignRepository(tmp_save_root, empire_id=0)
    ok, msg = repo.save_design(_mock_ship(), "Test Ship", set())
    assert ok, msg
    target = os.path.join(
        tmp_save_root, "designs", "empire_0", "test_ship.json"
    )
    assert os.path.exists(target)
    with open(target) as fh:
        payload = json.load(fh)
    assert "_metadata" in payload
    assert payload["name"] == "Test Ship"


def test_save_design_prevents_overwrite_of_built_design(tmp_save_root):
    """Overwrite of an already-built design is refused with a message
    containing the word "built" (mirrors DesignLibrary contract)."""
    repo = DesignRepository(tmp_save_root, empire_id=0)
    repo.save_design(_mock_ship(name="Built Ship"), "Built Ship", set())
    ok, msg = repo.save_design(
        _mock_ship(name="Built Ship"), "Built Ship", {"built_ship"}
    )
    assert ok is False
    assert "built" in msg.lower()


def test_save_design_can_update_unbuilt_design(tmp_save_root):
    """An unbuilt design can be re-saved."""
    repo = DesignRepository(tmp_save_root, empire_id=0)
    ok1, _ = repo.save_design(_mock_ship(name="Unbuilt"), "Unbuilt", set())
    assert ok1
    ok2, _ = repo.save_design(_mock_ship(name="Unbuilt"), "Unbuilt", set())
    assert ok2


def test_save_design_preserves_times_built_on_update(tmp_save_root):
    """Updating a design must preserve ``_metadata.times_built`` from disk."""
    repo = DesignRepository(tmp_save_root, empire_id=0)
    repo.save_design(_mock_ship(name="Reused"), "Reused", set())
    # Bump times_built once.
    repo.increment_built_count("reused")
    # Now re-save (still allowed because the design id isn't in built_designs).
    repo.save_design(_mock_ship(name="Reused"), "Reused", set())
    target = os.path.join(
        tmp_save_root, "designs", "empire_0", "reused.json"
    )
    with open(target) as fh:
        payload = json.load(fh)
    assert payload["_metadata"]["times_built"] == 1
