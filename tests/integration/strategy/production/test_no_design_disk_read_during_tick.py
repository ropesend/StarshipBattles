"""PROJ-427 Phase 3: explicit no-disk-read guard for production ticks.

Asserts that running a production tick triggers ZERO disk reads through
``DesignRepository.scan_designs`` / ``scan_designs_with_data`` /
``load_design_data``. Designs are resolved through the in-memory
``DesignCatalog`` wired into ``ProductionSpawner`` at session bootstrap;
the production tick must never repopulate the catalog from disk.
"""
from __future__ import annotations

from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.systems.design_catalog import DesignCatalog


def _make_shipyard(instance_id: str = "shipyard_proj427") -> PlanetaryFacility:
    return PlanetaryFacility(
        instance_id=instance_id,
        design_id="shipyard_complex",
        name="Space Shipyard",
        design_data={
            "layers": {
                "CORE": [{
                    "id": "space_shipyard",
                    "abilities": {"SpaceShipyard": {"value": 1}},
                }]
            }
        },
        is_operational=True,
    )


def test_production_tick_does_not_read_design_disk(production_setup, monkeypatch):
    """Run a production tick with ``DesignRepository`` disk-touching
    methods patched to raise. The tick must complete without invoking
    any of them.
    """
    planet = production_setup['planet']
    empire = production_setup['empire']
    engine = production_setup['engine']
    empires = production_setup['empires']

    # Seed an in-memory catalog for the empire so the spawner finds the
    # design without needing a repository scan.
    test_ship_data = {
        "name": "Test Ship",
        "ship_class": "Frigate",
        "vehicle_type": "Ship",
        "layers": {"CORE": [], "INNER": [], "OUTER": [], "ARMOR": []},
        "resources": {"fuel": 0.0, "energy": 0.0, "ammo": 0.0},
        "expected_stats": {"max_hp": 100, "max_speed": 10, "mass": 100.0},
        "_metadata": {"is_obsolete": False, "times_built": 0},
    }
    catalog = DesignCatalog(empire_id=empire.id)
    catalog.upsert_design("test_ship", test_ship_data)
    engine.production_engine.set_design_catalogs_by_empire({empire.id: catalog})

    # Wire a shipyard with a single, instantly-completable ship item so
    # the tick has spawn work to do.
    shipyard = _make_shipyard()
    shipyard.construction_queue = [{
        "design_id": "test_ship",
        "type": "ship",
        "turns_remaining": 1,
        "total_cost": {"metals": 100.0},
        "resources_consumed": {"metals": 0.0},
    }]
    planet.facilities.append(shipyard)

    def _boom_scan(self):  # pragma: no cover - defensive
        raise AssertionError(
            "PROJ-427: DesignRepository.scan_designs MUST NOT be called "
            "during a production tick."
        )

    def _boom_scan_with_data(self):  # pragma: no cover - defensive
        raise AssertionError(
            "PROJ-427: DesignRepository.scan_designs_with_data MUST NOT "
            "be called during a production tick."
        )

    def _boom_load(self, design_id):  # pragma: no cover - defensive
        raise AssertionError(
            f"PROJ-427: DesignRepository.load_design_data({design_id!r}) "
            f"MUST NOT be called during a production tick."
        )

    monkeypatch.setattr(
        "game.strategy.systems.design_repository.DesignRepository.scan_designs",
        _boom_scan,
    )
    monkeypatch.setattr(
        "game.strategy.systems.design_repository.DesignRepository.scan_designs_with_data",
        _boom_scan_with_data,
    )
    monkeypatch.setattr(
        "game.strategy.systems.design_repository.DesignRepository.load_design_data",
        _boom_load,
    )

    # Run a full turn of construction ticks; expect no disk reads.
    for tick in range(1, 101):
        engine.production_engine.process_construction_tick(
            tick, empires, None,
        )
