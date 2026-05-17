"""PROJ-427 Phase 0: explicit no-disk-read guard for production ticks.

This test is the structural-mitigation anchor identified by the TD-05
risk table: it asserts that running a production tick does NOT cause a
disk read through ``DesignLibrary.scan_designs`` / ``load_design_data``.

Today the test is marked ``xfail(strict=True)`` because the current code
path (Phase 0 baseline) DOES read design JSON from disk during a tick.
Phase 3 of PROJ-427 migrates the runtime production / construction
queue / quickstart spawn chain off ``DesignLibrary`` onto
``DesignCatalog`` (pure in-memory lookup), at which point this test
must be **unmarked** and expected to pass green.

When this file is touched outside Phase 3, that's a signal something
deeper has changed and the test should be re-evaluated.
"""
from __future__ import annotations

import pytest

from game.strategy.data.planetary_facility import PlanetaryFacility


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


@pytest.mark.xfail(
    strict=True,
    reason=(
        "PROJ-427 Phase 0: current code reads design JSON during the "
        "production tick (ProductionSpawner instantiates DesignLibrary "
        "and calls load_design_data per spawn). Phase 3 migrates the "
        "runtime spawn chain onto DesignCatalog and unmarks this test."
    ),
)
def test_production_tick_does_not_read_design_disk(production_setup, monkeypatch):
    """Run a production tick with DesignLibrary.scan_designs and
    load_design_data patched to raise. The tick must complete without
    invoking either method.

    Pre-Phase-3: this fails because the spawn chain calls
    ``DesignLibrary(save_path, empire.id).load_design_data(design_id)``
    inline. Phase 3 flips this to expected-pass.
    """
    planet = production_setup['planet']
    empire = production_setup['empire']
    engine = production_setup['engine']
    empires = production_setup['empires']
    temp_dir = production_setup['temp_dir']

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

    # Patch DesignLibrary's disk-touching methods at the module
    # boundary used by ProductionSpawner so any invocation fails the
    # test with a clear AssertionError.
    def _boom_scan(self):  # pragma: no cover - defensive
        raise AssertionError(
            "PROJ-427: scan_designs MUST NOT be called during a "
            "production tick (Phase 3 contract)."
        )

    def _boom_load(self, design_id):  # pragma: no cover - defensive
        raise AssertionError(
            f"PROJ-427: load_design_data({design_id!r}) MUST NOT be "
            f"called during a production tick (Phase 3 contract)."
        )

    monkeypatch.setattr(
        "game.strategy.systems.design_library.DesignLibrary.scan_designs",
        _boom_scan,
    )
    monkeypatch.setattr(
        "game.strategy.systems.design_library.DesignLibrary.load_design_data",
        _boom_load,
    )

    # Run a full turn of construction ticks; expect no disk reads.
    for tick in range(1, 101):
        engine.production_engine.process_construction_tick(
            tick, empires, None, save_path=temp_dir,
        )
