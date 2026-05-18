"""
Tests for fleet cargo resource methods used by fleet construction.

Phase 6: Fleet-bound shipyards draw construction resources from
fleet cargo (cargo_contents across ships) instead of empire pool.

PROJ-322 Task 6.3 (DUP-003): the per-file `_make_ship` cargo mock helper
has been replaced by a shared `make_cargo_mock_ship` factory at
`tests.fixtures.cargo_mock_ship`. This file's `_make_ship` is now a thin
alias for compatibility with the existing test bodies.
"""
import pytest

from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord
from tests.fixtures.cargo_mock_ship import make_cargo_mock_ship


def _make_ship(cargo_capacity=None, cargo_contents=None):
    """Thin alias over the shared `make_cargo_mock_ship` factory.

    Kept for compatibility with the existing test bodies in this file;
    new tests should import `make_cargo_mock_ship` directly.
    """
    return make_cargo_mock_ship(
        cargo_capacity=cargo_capacity,
        cargo_contents=cargo_contents,
    )


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

    def test_has_resources_rounds_fractional_costs_symmetric_with_consume(self):
        """F-A-010 / DI-2026-05-18-006: affordability uses int(round(amount)).

        ``consume_cargo_resource`` charges ``int(round(amount))`` against
        the integer-typed cargo store. The affordability predicate must
        round the same way so the two sides agree on what gets charged.

        Concretely: amount=0.6 rounds to 1, amount=0.4 rounds to 0.
        """
        ship = _make_ship(
            cargo_capacity={"metals": 10},
            cargo_contents={"metals": 1},
        )
        fleet = _make_fleet([ship])

        # 1.4 rounds to 1; we have 1 → affordable.
        assert fleet.has_cargo_resources({"metals": 1.4}) is True
        # 1.6 rounds to 2; we have 1 → not affordable.
        assert fleet.has_cargo_resources({"metals": 1.6}) is False
        # 0.4 rounds to 0; we have 1 → trivially affordable.
        assert fleet.has_cargo_resources({"metals": 0.4}) is True
        # 0.6 rounds to 1; we have 1 → affordable.
        assert fleet.has_cargo_resources({"metals": 0.6}) is True

    def test_has_resources_round_to_zero_against_empty_cargo(self):
        """A sub-0.5 cost against empty cargo is treated as 0-cost (matches
        what consume actually charges)."""
        ship = _make_ship(
            cargo_capacity={"metals": 10},
            cargo_contents={"metals": 0},
        )
        fleet = _make_fleet([ship])
        # 0.1 rounds to 0; consume would also charge 0; both sides agree.
        assert fleet.has_cargo_resources({"metals": 0.1}) is True


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
