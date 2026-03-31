"""
Tests for fleet cargo resource methods used by fleet construction.

Phase 6: Fleet-bound shipyards draw construction resources from
fleet cargo (cargo_contents across ships) instead of empire pool.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord


def _make_ship(cargo_capacity=None, cargo_contents=None):
    """Create a mock ship with cargo capacity and contents."""
    ship = MagicMock()
    ship.cargo_contents = dict(cargo_contents or {})
    _cap = dict(cargo_capacity or {})

    def get_cargo_capacity(cargo_type):
        return _cap.get(cargo_type, 0)

    def get_current_cargo(cargo_type):
        return ship.cargo_contents.get(cargo_type, 0)

    def load_cargo(cargo_type, amount):
        space = _cap.get(cargo_type, 0) - ship.cargo_contents.get(cargo_type, 0)
        actual = min(amount, max(0, space))
        if actual > 0:
            ship.cargo_contents[cargo_type] = ship.cargo_contents.get(cargo_type, 0) + actual
        return actual

    def unload_cargo(cargo_type, amount):
        current = ship.cargo_contents.get(cargo_type, 0)
        actual = min(amount, current)
        if actual > 0:
            ship.cargo_contents[cargo_type] = current - actual
        return actual

    ship.get_cargo_capacity = get_cargo_capacity
    ship.get_current_cargo = get_current_cargo
    ship.load_cargo = load_cargo
    ship.unload_cargo = unload_cargo
    ship.is_combat_capable = True
    return ship


def _make_fleet(ships=None):
    """Create a fleet with mock ships."""
    fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
    if ships:
        for ship in ships:
            fleet.ships.append(ship)
    return fleet


class TestFleetHasCargoResources:
    """Tests for fleet.has_cargo_resources() method."""

    def test_has_resources_with_sufficient_cargo(self):
        """Returns True when fleet has enough cargo of all types."""
        ship = _make_ship(
            cargo_capacity={"metals": 1000},
            cargo_contents={"metals": 500},
        )
        fleet = _make_fleet([ship])

        assert fleet.has_cargo_resources({"metals": 200}) is True

    def test_has_resources_with_insufficient_cargo(self):
        """Returns False when fleet lacks enough cargo."""
        ship = _make_ship(
            cargo_capacity={"metals": 1000},
            cargo_contents={"metals": 50},
        )
        fleet = _make_fleet([ship])

        assert fleet.has_cargo_resources({"metals": 200}) is False

    def test_has_resources_across_multiple_ships(self):
        """Aggregates cargo across all ships in fleet."""
        ship1 = _make_ship(cargo_capacity={"metals": 500}, cargo_contents={"metals": 100})
        ship2 = _make_ship(cargo_capacity={"metals": 500}, cargo_contents={"metals": 150})
        fleet = _make_fleet([ship1, ship2])

        assert fleet.has_cargo_resources({"metals": 250}) is True
        assert fleet.has_cargo_resources({"metals": 251}) is False

    def test_has_resources_multiple_types(self):
        """Checks all resource types independently."""
        ship = _make_ship(
            cargo_capacity={"metals": 1000, "organics": 500},
            cargo_contents={"metals": 300, "organics": 100},
        )
        fleet = _make_fleet([ship])

        assert fleet.has_cargo_resources({"metals": 200, "organics": 50}) is True
        assert fleet.has_cargo_resources({"metals": 200, "organics": 200}) is False

    def test_has_resources_empty_costs(self):
        """Empty costs dict always returns True."""
        fleet = _make_fleet([])
        assert fleet.has_cargo_resources({}) is True

    def test_has_resources_missing_type(self):
        """Returns False for cargo type not carried by any ship."""
        ship = _make_ship(cargo_capacity={"metals": 1000}, cargo_contents={"metals": 500})
        fleet = _make_fleet([ship])

        assert fleet.has_cargo_resources({"exotics": 10}) is False


class TestFleetConsumeCargoResource:
    """Tests for fleet.consume_cargo_resource() method."""

    def test_consume_from_single_ship(self):
        """Consumes cargo from a single ship."""
        ship = _make_ship(cargo_capacity={"metals": 1000}, cargo_contents={"metals": 500})
        fleet = _make_fleet([ship])

        result = fleet.consume_cargo_resource("metals", 200)

        assert result is True
        assert ship.cargo_contents["metals"] == 300

    def test_consume_fails_insufficient(self):
        """Returns False if insufficient cargo (no partial consumption)."""
        ship = _make_ship(cargo_capacity={"metals": 1000}, cargo_contents={"metals": 50})
        fleet = _make_fleet([ship])

        result = fleet.consume_cargo_resource("metals", 200)

        assert result is False
        assert ship.cargo_contents["metals"] == 50  # Unchanged

    def test_consume_across_multiple_ships(self):
        """Consumes across ships when single ship doesn't have enough."""
        ship1 = _make_ship(cargo_capacity={"metals": 500}, cargo_contents={"metals": 100})
        ship2 = _make_ship(cargo_capacity={"metals": 500}, cargo_contents={"metals": 200})
        fleet = _make_fleet([ship1, ship2])

        result = fleet.consume_cargo_resource("metals", 250)

        assert result is True
        total_remaining = ship1.cargo_contents["metals"] + ship2.cargo_contents["metals"]
        assert total_remaining == 50


class TestFleetGetCargoResource:
    """Tests for fleet.get_cargo_resource() method."""

    def test_get_cargo_resource_total(self):
        """Returns total cargo across all ships."""
        ship1 = _make_ship(cargo_capacity={"metals": 500}, cargo_contents={"metals": 100})
        ship2 = _make_ship(cargo_capacity={"metals": 500}, cargo_contents={"metals": 200})
        fleet = _make_fleet([ship1, ship2])

        assert fleet.get_cargo_resource("metals") == 300

    def test_get_cargo_resource_missing_type(self):
        """Returns 0 for cargo type not carried."""
        fleet = _make_fleet([_make_ship()])
        assert fleet.get_cargo_resource("exotics") == 0
