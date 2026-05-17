"""PROJ-434 Phase 0: ``FacadeSessionState.designs_by_empire`` resolves
through ``session.services.design_catalogs_by_empire`` rather than
through ``DesignLibrary`` instances.

QA-Obs-3 (2026-05-16): the per-empire UI cache MUST be served by the
catalog so workshop saves -> ``catalog.save_design`` -> ``invalidate``
flow through to the same-empire viewer's next read without a turn
advance.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from game.strategy.facade.slices._facade_state import FacadeSessionState
from game.strategy.systems.design_catalog import DesignCatalog
from game.strategy.systems.design_repository import DesignRepository


def _attach_catalog_to_session(session, *, empire_id: int,
                               catalog: DesignCatalog) -> None:
    """Bolt a per-empire catalog onto the mock session's services bag."""
    session.services = SimpleNamespace(
        design_catalogs_by_empire={empire_id: catalog},
    )


def test_designs_by_empire_reads_from_catalog(tmp_path):
    """``state.get_designs_for_empire(empire_id)`` returns the catalog's
    current ``list_designs()`` view."""
    repo = DesignRepository(str(tmp_path), empire_id=0)
    cat = DesignCatalog(empire_id=0)
    cat.attach_repository(repo)

    # Seed via the catalog so the in-memory list view is non-empty.
    ship = MagicMock()
    ship.name = "Alpha"
    ship.ship_class = "Frigate"
    ship.vehicle_type = "Ship"
    ship.mass = 1000.0
    ship.theme_id = "Federation"
    ship.layers = {}
    ship.to_dict.return_value = {
        "name": "Alpha", "ship_class": "Frigate",
        "vehicle_type": "Ship", "mass": 1000.0, "layers": {},
    }
    cat.save_design(ship, "Alpha", set())

    session = MagicMock()
    _attach_catalog_to_session(session, empire_id=0, catalog=cat)
    state = FacadeSessionState(session=session)

    designs = state.get_designs_for_empire(0)
    names = {d.name for d in designs}
    assert "Alpha" in names


def test_designs_by_empire_workshop_save_visible_same_turn(tmp_path):
    """QA-Obs-3 regression: ``catalog.save_design`` must make the new
    design visible on the *next* read of ``get_designs_for_empire`` —
    no turn advance, no manual cache clear."""
    repo = DesignRepository(str(tmp_path), empire_id=0)
    cat = DesignCatalog(empire_id=0)
    cat.attach_repository(repo)

    session = MagicMock()
    _attach_catalog_to_session(session, empire_id=0, catalog=cat)
    state = FacadeSessionState(session=session)

    assert state.get_designs_for_empire(0) == []

    # Workshop save.
    ship = MagicMock()
    ship.name = "Fresh"
    ship.ship_class = "Frigate"
    ship.vehicle_type = "Ship"
    ship.mass = 1000.0
    ship.theme_id = "Federation"
    ship.layers = {}
    ship.to_dict.return_value = {
        "name": "Fresh", "ship_class": "Frigate",
        "vehicle_type": "Ship", "mass": 1000.0, "layers": {},
    }
    ok, _msg = cat.save_design(ship, "Fresh", set())
    assert ok

    # Next read on the same turn — must surface the new design.
    designs = state.get_designs_for_empire(0)
    names = {d.name for d in designs}
    assert "Fresh" in names


def test_designs_by_empire_missing_catalog_returns_empty(tmp_path):
    """When the catalog map is missing the empire id, the accessor
    returns an empty list (safe fallback for early bootstrap / tests)."""
    session = MagicMock()
    session.services = SimpleNamespace(design_catalogs_by_empire={})
    state = FacadeSessionState(session=session)
    assert state.get_designs_for_empire(99) == []
