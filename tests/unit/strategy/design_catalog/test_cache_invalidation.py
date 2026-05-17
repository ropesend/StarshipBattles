"""PROJ-434 Phase 0: QA-Obs-3 cache invalidation contract on
``DesignCatalog.save_design``.

QA-Obs-3 (2026-05-16): after the workshop saves a new design, the
same-empire viewer's Build Queue MUST see the new design on the next
read without a turn advance. ``DesignLibrary`` enforced this by
popping the cache key in ``save_design``. The catalog version moves
that contract onto ``DesignCatalog.save_design`` -> calls
``DesignRepository.save_design`` then ``invalidate(design_id)`` which
re-seeds the in-memory list.
"""
from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest

from game.strategy.systems.design_catalog import DesignCatalog
from game.strategy.systems.design_repository import DesignRepository


def _mock_ship(name="Fresh Design"):
    ship = MagicMock()
    ship.name = name
    ship.ship_class = "Frigate"
    ship.vehicle_type = "Ship"
    ship.mass = 1000.0
    ship.theme_id = "Federation"
    ship.layers = {}
    ship.to_dict.return_value = {
        "name": name,
        "ship_class": "Frigate",
        "vehicle_type": "Ship",
        "mass": 1000.0,
        "layers": {},
    }
    return ship


@pytest.fixture
def wired(tmp_path):
    repo = DesignRepository(str(tmp_path), empire_id=0)
    cat = DesignCatalog(empire_id=0)
    cat.attach_repository(repo)
    return cat, repo


def test_save_design_through_catalog_writes_disk_and_invalidates_cache(wired):
    """The catalog's ``save_design`` orchestrates repo.save_design + the
    in-memory upsert, so the next ``list_designs()`` sees the new entry."""
    cat, repo = wired
    # Initially empty.
    assert cat.list_designs() == []

    ok, msg = cat.save_design(_mock_ship(name="Fresh Design"),
                              "Fresh Design", set())
    assert ok, msg

    # New design must show up immediately on the next read.
    names = [d.name for d in cat.list_designs()]
    assert "Fresh Design" in names


def test_invalidate_clears_single_design(wired):
    """``invalidate(design_id)`` removes a single entry from the catalog
    so the next read re-loads it from the repository."""
    cat, repo = wired
    cat.save_design(_mock_ship(name="First"), "First", set())
    cat.save_design(_mock_ship(name="Second"), "Second", set())
    assert cat.lookup("first") is not None

    cat.invalidate("first")
    # After invalidate the entry was dropped from the in-memory list
    # but a fresh repopulate from the repository restores it.
    assert cat.lookup("first") is None
    cat.repopulate_from(repo)
    assert cat.lookup("first") is not None


def test_invalidate_full_clears_all(wired):
    """``invalidate(None)`` wipes the entire in-memory list view."""
    cat, repo = wired
    cat.save_design(_mock_ship(name="A"), "A", set())
    cat.save_design(_mock_ship(name="B"), "B", set())
    assert len(cat.list_designs()) == 2

    cat.invalidate(None)
    assert cat.list_designs() == []
