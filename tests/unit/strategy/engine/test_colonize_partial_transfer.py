"""Tests for partial population and cargo transfer during colonization.

Phase 4: When the COLONIZE order has population/cargo amounts specified,
process_colonize should only transfer those amounts (clamped to available).
"""
from unittest.mock import MagicMock, patch
from game.strategy.engine.order_processor import OrderProcessor
from game.strategy.data.order_types import Order, OrderType


def _make_fleet(passengers=1000, metals=500, organics=300):
    fleet = MagicMock()
    fleet.id = 1
    fleet.location = MagicMock()
    fleet.orders = []
    fleet.ships = []

    cargo = {'passengers': passengers, 'metals': metals, 'organics': organics}
    unloaded = {}

    fleet.resources.get_fleet_cargo_current = MagicMock(
        side_effect=lambda ct: cargo.get(ct, 0)
    )
    fleet.resources.unload_cargo_from_fleet = MagicMock(
        side_effect=lambda ct, amt: min(amt, cargo.get(ct, 0))
    )
    fleet.resources.load_cargo_to_fleet = MagicMock()

    def pop_order():
        if fleet.orders:
            fleet.orders.pop(0)
    fleet.pop_order = pop_order
    fleet.get_current_order = lambda: fleet.orders[0] if fleet.orders else None

    return fleet


def _make_planet():
    planet = MagicMock()
    planet.id = 10
    planet.name = "TestWorld"
    planet.owner_id = None
    planet.populations = []
    planet.facilities = []
    planet.staging_yard = []
    planet.stockpile = {}

    def add_to_stockpile(res, amt):
        planet.stockpile[res] = planet.stockpile.get(res, 0) + amt
    planet.add_to_stockpile = add_to_stockpile
    return planet


class TestColonizePartialTransfer:
    """Test that colonization respects specified population/cargo amounts."""

    def test_partial_population_transfer(self):
        """Only specified population amount should be transferred."""
        fleet = _make_fleet(passengers=1000)
        planet = _make_planet()
        empire = MagicMock()
        empire.id = 0
        empire.race_config.race_id = "human"

        # COLONIZE order with dict target specifying 500 population
        order = Order(OrderType.COLONIZE, target={
            'planet': planet,
            'population': 500,
            'cargo': None,
        })
        fleet.orders = [order]

        proc = OrderProcessor.__new__(OrderProcessor)
        # Call the method directly
        result = proc._transfer_founding_population(fleet, planet, empire, 500)

        # Should transfer 500, not all 1000
        fleet.resources.unload_cargo_from_fleet.assert_called_once_with("passengers", 500)
        assert result == 500

    def test_none_population_transfers_all(self):
        """None population_amount should transfer all passengers."""
        fleet = _make_fleet(passengers=1000)
        planet = _make_planet()
        empire = MagicMock()
        empire.id = 0
        empire.race_config.race_id = "human"

        proc = OrderProcessor.__new__(OrderProcessor)
        result = proc._transfer_founding_population(fleet, planet, empire, None)

        fleet.resources.unload_cargo_from_fleet.assert_called_once_with("passengers", 1000)
        assert result == 1000

    def test_partial_cargo_transfer(self):
        """Only specified cargo amounts should be transferred."""
        fleet = _make_fleet(passengers=0, metals=500, organics=300)
        planet = _make_planet()

        proc = OrderProcessor.__new__(OrderProcessor)
        proc._transfer_cargo_resources_to_colony(fleet, planet, {'metals': 200})

        # Only metals should be transferred, and only 200
        assert planet.stockpile.get('metals', 0) == 200
        # Organics should NOT be transferred (not in cargo_amounts)
        assert planet.stockpile.get('organics', 0) == 0

    def test_none_cargo_transfers_all(self):
        """None cargo_amounts should transfer all cargo."""
        fleet = _make_fleet(passengers=0, metals=500, organics=300)
        planet = _make_planet()

        proc = OrderProcessor.__new__(OrderProcessor)
        proc._transfer_cargo_resources_to_colony(fleet, planet, None)

        # All resources should be transferred
        assert planet.stockpile.get('metals', 0) == 500
        assert planet.stockpile.get('organics', 0) == 300

    def test_population_clamped_to_available(self):
        """If specified population exceeds available, clamp to available."""
        fleet = _make_fleet(passengers=200)
        planet = _make_planet()
        empire = MagicMock()
        empire.id = 0
        empire.race_config.race_id = "human"

        proc = OrderProcessor.__new__(OrderProcessor)
        result = proc._transfer_founding_population(fleet, planet, empire, 9999)

        # Clamped to 200 (available)
        fleet.resources.unload_cargo_from_fleet.assert_called_once_with("passengers", 200)
        assert result == 200
