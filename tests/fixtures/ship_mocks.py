"""Shared ship-mock factories for UI-family tests.

PROJ-494 T2.10: hoisted from `tests/unit/ui/screens/test_fleet_report_filters.py`
so other fleet-report / ship-display tests can reuse the same mock.

The `make_mock_ship` factory builds a `MagicMock(spec=ShipInstance)` configured
to satisfy the production read paths that fleet-report / sort / filter logic
exercises:
- `instance_id`, `serial`, `design_id`, `name`, `design_data.expected_stats`
- `get_calculated_stats`, `get_cargo_capacity`, `get_current_cargo`
- `get_hp_percentage`, `current_hp`, `is_alive`, `is_derelict`, `is_damaged`
- `_resource_mgr` (real `ShipConsumableManager`)
- `_cargo_mgr.has_cargo` / `.total_cargo_units` / `.get_all_cargo`
  (closures over the mock's `cargo_contents` dict)
- `is_combat_capable`
"""
from unittest.mock import MagicMock

from game.strategy.data.ship_instance import ShipInstance


def make_mock_ship(
    serial=None,
    design_name="Destroyer",
    hp_pct=1.0,
    is_alive=True,
    is_derelict=False,
    is_damaged=False,
    mass=1000,
    max_fuel=100,
    current_fuel=100,
    max_energy=100,
    current_energy=100,
    warp_tonnage=None,  # If set, adds WarpJump ability with this max_tonnage
):
    """Helper to create a mock ship for testing.

    PROJ-494 T2.10: hoisted from `test_fleet_report_filters.py` (lines 12-113
    in the pre-hoist version).
    """
    ship = MagicMock(spec=ShipInstance)
    ship.serial = serial
    ship.design_id = design_name.lower().replace(" ", "_")
    ship.name = design_name
    # PROJ-475 Phase 2 Task 2.6: the spaceyard filter / sort key the
    # facade-projected lookup by ``instance_id``; ``ShipInstance`` sets it in
    # ``__init__`` so it is not on the class spec — set it explicitly here.
    ship.instance_id = f"{ship.design_id}-{id(ship)}"
    ship.is_alive = is_alive
    ship.is_derelict = is_derelict
    ship.is_damaged.return_value = is_damaged

    # Set up design_data with optional warp ability
    layers = {}
    expected_stats = {
        'mass': mass,
        'max_hp': 100,
        'resource_storage': {'fuel': max_fuel, 'energy': max_energy},
        'warp_max_tonnage': warp_tonnage if warp_tonnage is not None else 0,
    }

    ship.design_data = {
        'name': design_name,
        'expected_stats': expected_stats,
        'layers': layers
    }

    # Configure get_calculated_stats() to return the expected_stats
    # This is needed since code now uses get_calculated_stats() instead of expected_stats
    ship.get_calculated_stats.return_value = expected_stats

    # PROJ-162: Mock get_cargo_capacity to return 0 by default (sort_ships calls this)
    # PROJ-425 Phase 6: production reads via ``ship._cargo_mgr``; also keep
    # the entity-level mock for any remaining direct probes in this file.
    ship.get_cargo_capacity = MagicMock(return_value=0)
    ship.get_current_cargo = MagicMock(return_value=0)
    ship._cargo_mgr.get_cargo_capacity = MagicMock(return_value=0)
    ship._cargo_mgr.get_current_cargo = MagicMock(return_value=0)

    # Set HP percentage
    ship.get_hp_percentage.return_value = hp_pct

    # Set current_hp based on hp_pct
    if hp_pct < 1.0:
        ship.current_hp = int(100 * hp_pct)
    else:
        ship.current_hp = None

    # PROJ-95: Resource levels always store actual values (no sparse dict convention)
    ship.consumable_levels = {
        'fuel': current_fuel,
        'energy': current_energy,
    }
    # PROJ-436 Phase 3c: production reads / writes through the stable
    # manager API (``ship._resource_mgr.get_current_resource`` /
    # ``ship._cargo_mgr.has_cargo`` / ``.total_cargo_units`` /
    # ``.get_all_cargo``). Wire the cargo-related manager methods to
    # read from this mock's ``cargo_contents`` so per-test assignments
    # like ``ship.cargo_contents = {...}`` keep working without
    # rewriting every test setup.
    from game.strategy.data.ship_consumable_manager import (
        ShipConsumableManager,
    )
    ship._resource_mgr = ShipConsumableManager(ship)
    # ``ShipCargoManager`` is heavier (uses design_data for bays) — keep
    # the existing MagicMock for bay-related methods but route the
    # cargo-content reads through a thin closure that follows the mock
    # ship's ``cargo_contents`` dict assignments.
    ship._cargo_mgr.has_cargo = MagicMock(
        side_effect=lambda: bool(ship.cargo_contents) and any(
            v > 0 for v in ship.cargo_contents.values()
        )
    )
    ship._cargo_mgr.total_cargo_units = MagicMock(
        side_effect=lambda: sum(
            int(v) for v in (ship.cargo_contents or {}).values()
        )
    )
    ship._cargo_mgr.get_all_cargo = MagicMock(
        side_effect=lambda: dict(ship.cargo_contents or {})
    )

    # Combat capable status
    ship.is_combat_capable.return_value = is_alive and not is_derelict

    return ship
