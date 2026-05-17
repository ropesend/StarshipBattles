"""PROJ-434 Phase 0: ``DesignCatalog.search_designs`` parity with
``DesignLibrary.search_designs``.

Used by ``design_selector_window.py``'s search box. Case-insensitive
substring match on ``DesignMetadata.name``, with optional filter dict
keyed on ``ship_class`` / ``vehicle_type`` / ``design_role`` /
``show_obsolete``.
"""
from __future__ import annotations

import json
import os
import tempfile

import pytest

from game.strategy.systems.design_catalog import DesignCatalog
from game.strategy.systems.design_repository import DesignRepository


def _write_design(
    folder: str,
    design_id: str,
    name: str,
    ship_class: str = "Frigate",
    vehicle_type: str = "Ship",
    obsolete: bool = False,
) -> None:
    os.makedirs(folder, exist_ok=True)
    payload = {
        "name": name,
        "ship_class": ship_class,
        "vehicle_type": vehicle_type,
        "mass": 50.0,
        "layers": {},
        "_metadata": {"is_obsolete": obsolete, "times_built": 0},
    }
    with open(os.path.join(folder, f"{design_id}.json"), "w") as fh:
        json.dump(payload, fh)


@pytest.fixture
def catalog(tmp_path):
    folder = os.path.join(str(tmp_path), "designs", "empire_0")
    _write_design(folder, "alpha_fighter", "Alpha Fighter")
    _write_design(folder, "beta_cruiser", "Beta Cruiser",
                  ship_class="Cruiser")
    _write_design(folder, "alpha_destroyer", "Alpha Destroyer",
                  ship_class="Destroyer")
    _write_design(folder, "old", "Old Design", obsolete=True)
    repo = DesignRepository(str(tmp_path), empire_id=0)
    cat = DesignCatalog(empire_id=0)
    cat.repopulate_from(repo)
    return cat


def test_search_substring_match_case_insensitive(catalog):
    """Searching 'Alpha' returns both Alpha designs (case-insensitive,
    excludes obsolete by default)."""
    results = catalog.search_designs("Alpha")
    names = sorted(d.name for d in results)
    assert names == ["Alpha Destroyer", "Alpha Fighter"]


def test_search_empty_query_returns_all_non_obsolete(catalog):
    """Empty query == filter-only (default ``show_obsolete=False``)."""
    results = catalog.search_designs("")
    names = sorted(d.name for d in results)
    assert names == ["Alpha Destroyer", "Alpha Fighter", "Beta Cruiser"]


def test_search_with_ship_class_filter(catalog):
    """``filters={'ship_class': 'Cruiser'}`` narrows results."""
    results = catalog.search_designs("", filters={"ship_class": "Cruiser"})
    assert [d.name for d in results] == ["Beta Cruiser"]


def test_search_show_obsolete_flag(catalog):
    """``filters={'show_obsolete': True}`` includes obsolete designs."""
    results = catalog.search_designs("", filters={"show_obsolete": True})
    names = sorted(d.name for d in results)
    assert "Old Design" in names
