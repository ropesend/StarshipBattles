"""PROJ-434 Phase 0: ``DesignCatalog.filter_designs`` parity with
``DesignLibrary.filter_designs``.

Used by ``design_selector_window.py`` filter chips. Filters on
``ship_class`` / ``vehicle_type`` / ``design_role``, and the
``show_obsolete`` toggle.
"""
from __future__ import annotations

import json
import os

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
    _write_design(folder, "f1", "Frigate One", ship_class="Frigate",
                  vehicle_type="Ship")
    _write_design(folder, "f2", "Fighter Two", ship_class="Fighter",
                  vehicle_type="Fighter")
    _write_design(folder, "p1", "Pod One", ship_class="Pod",
                  vehicle_type="Drop Pod")
    _write_design(folder, "old", "Obsolete", obsolete=True,
                  ship_class="Frigate")
    repo = DesignRepository(str(tmp_path), empire_id=0)
    cat = DesignCatalog(empire_id=0)
    cat.repopulate_from(repo)
    return cat


def test_filter_designs_by_ship_class(catalog):
    results = catalog.filter_designs(ship_class="Frigate")
    names = sorted(d.name for d in results)
    # 'Obsolete' is also Frigate but obsolete; default is show_obsolete=False
    assert names == ["Frigate One"]


def test_filter_designs_by_vehicle_type(catalog):
    results = catalog.filter_designs(vehicle_type="Drop Pod")
    assert [d.name for d in results] == ["Pod One"]


def test_filter_designs_obsolete_toggle(catalog):
    excluded = catalog.filter_designs(show_obsolete=False)
    assert all(not d.is_obsolete for d in excluded)
    included = catalog.filter_designs(show_obsolete=True)
    names = {d.name for d in included}
    assert "Obsolete" in names
