"""PROJ-FMS-A Phase 4: production output normalisation.

Verifies:
- Planet-built mine / fighter / satellite -> Planet.staging_yard (CarriedVehicle-shaped).
- Fleet-built mine / fighter / satellite -> ship VehicleBay (flagship-first).
- Fleet build with no bay capacity -> production order fails cleanly (no add_ship).
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.production_spawner import ProductionSpawner


def _make_empire(eid: int = 1) -> MagicMock:
    e = MagicMock()
    e.id = eid
    return e


def _make_planet() -> MagicMock:
    p = MagicMock()
    p.name = "TestPlanet"
    p.add_to_staging_yard = MagicMock(return_value=True)
    return p


class TestPlanetBuiltSmallCraftToStaging:
    """All three small-craft types (mine/fighter/satellite) land in staging."""

    @pytest.mark.parametrize("vtype", ["mine", "fighter", "satellite"])
    def test_routes_to_staging_yard(self, vtype):
        spawner = ProductionSpawner(registries=MagicMock())
        empire = _make_empire()
        planet = _make_planet()
        item = {
            'design_id': f'design_{vtype}',
            'type': vtype,
            'design_data': {'name': f'{vtype}_proto'},
        }
        spawner.spawn_completed_item(
            item, empire, planet, galaxy=None,
            tick=0,
        )
        # Routed to staging_yard, not _spawn_ship.
        planet.add_to_staging_yard.assert_called_once()
        # PROJ-450 Phase 2: typed CarriedVehicle entry.
        from game.strategy.data.carried_vehicle import CarriedVehicle
        staging_item = planet.add_to_staging_yard.call_args[0][0]
        assert isinstance(staging_item, CarriedVehicle)
        assert staging_item.vehicle_type == vtype


class TestFleetBuiltSmallCraftToBay:
    def _make_fleet_with_bay(self, capacity_mass: float = 500.0):
        """Build a real Fleet with one ship whose ShipCargoManager will
        accept a carried vehicle."""
        from game.core.hex_math import HexCoord
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.ship_instance import ShipInstance

        # Mock the ship: provide a stub _cargo_mgr with can_accept_vehicle/load_vehicle.
        ship = MagicMock(spec=ShipInstance)
        ship.name = "Flagship"
        cargo_mgr = MagicMock()
        cargo_mgr.can_accept_vehicle = MagicMock(return_value=True)
        cargo_mgr.load_vehicle = MagicMock(return_value=True)
        ship._cargo_mgr = cargo_mgr
        fleet = Fleet(fleet_id=10, owner_id=1, location=HexCoord(0, 0))
        fleet.ships.append(ship)
        return fleet, ship, cargo_mgr

    def test_fleet_built_fighter_loads_into_flagship_bay(self):
        from game.core.registry import GameRegistries
        # Provide a stub registries with a non-None marker so the spawner
        # doesn't bail; the design_data path is bypassed via mocked stats.
        regs = MagicMock(spec=GameRegistries)
        spawner = ProductionSpawner(registries=regs)
        empire = _make_empire()
        fleet, ship, cargo_mgr = self._make_fleet_with_bay()
        item = {
            'design_id': 'fighter_x',
            'type': 'fighter',
            'design_data': {'name': 'Fighter X'},
        }
        # Stub calculate_design_stats to return tiny mass.
        with patch(
            "game.strategy.engine.production_spawner.calculate_design_stats"
            if False  # path doesn't exist at module level — patch the import inline.
            else "game.simulation.entities.ship_design_stats.calculate_design_stats",
            return_value={'mass': 25, 'max_hp': 20},
        ):
            spawner.spawn_completed_item(
                item, empire, fleet, galaxy=None,
                tick=0,
            )
        # Confirm cargo_mgr.load_vehicle invoked exactly once (flagship).
        cargo_mgr.can_accept_vehicle.assert_called()
        cargo_mgr.load_vehicle.assert_called_once()

    def test_no_bay_capacity_fails_cleanly(self):
        from game.core.registry import GameRegistries
        regs = MagicMock(spec=GameRegistries)
        spawner = ProductionSpawner(registries=regs)
        empire = _make_empire()
        fleet, ship, cargo_mgr = self._make_fleet_with_bay()
        # Bay refuses the vehicle (no capacity / type mismatch).
        cargo_mgr.can_accept_vehicle.return_value = False
        item = {
            'design_id': 'mine_big',
            'type': 'mine',
            'design_data': {'name': 'Big Mine'},
        }
        with patch(
            "game.simulation.entities.ship_design_stats.calculate_design_stats",
            return_value={'mass': 50, 'max_hp': 5},
        ):
            spawner.spawn_completed_item(
                item, empire, fleet, galaxy=None,
                tick=0,
            )
        # No load_vehicle invocation — production output silently dropped
        # (with a warning logged).
        cargo_mgr.load_vehicle.assert_not_called()
