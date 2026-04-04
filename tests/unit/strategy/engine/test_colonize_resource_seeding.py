"""
Tests for resource seeding during colonization.

Phase 3: Fleet cargo resources are transferred to the new colony's
stockpile during colonization. The starter complex also provides
initial seed resources.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.engine.order_processor import OrderProcessor
from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord


def _make_cargo_ship(cargo=None):
    """Create a mock ship with cargo contents."""
    ship = MagicMock()
    ship.cargo_contents = dict(cargo or {})
    ship.is_combat_capable = lambda: True
    ship.get_calculated_stats = lambda: {'mass': 500, 'strategic_movement': 5}

    def get_cargo_capacity(ct):
        return 100000

    def get_current_cargo(ct):
        return ship.cargo_contents.get(ct, 0)

    def unload_cargo(ct, amt):
        cur = ship.cargo_contents.get(ct, 0)
        actual = min(amt, cur)
        if actual > 0:
            ship.cargo_contents[ct] = cur - actual
        return actual

    def load_cargo(ct, amt):
        ship.cargo_contents[ct] = ship.cargo_contents.get(ct, 0) + amt
        return amt

    ship.get_cargo_capacity = get_cargo_capacity
    ship.get_current_cargo = get_current_cargo
    ship.unload_cargo = unload_cargo
    ship.load_cargo = load_cargo
    return ship


class TestTransferCargoResourcesToColony:
    """Tests for _transfer_cargo_resources_to_colony()."""

    def test_transfers_resource_cargo_to_stockpile(self):
        """Resource cargo from fleet is added to planet stockpile."""
        ship = _make_cargo_ship({"metals": 500, "organics": 200})
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.ships.append(ship)

        planet = MagicMock()
        planet.name = "New Colony"
        planet.stockpile = {}

        def add_to_stockpile(res, amt):
            planet.stockpile[res] = planet.stockpile.get(res, 0.0) + amt
            return 0.0
        planet.add_to_stockpile = add_to_stockpile

        processor = OrderProcessor.__new__(OrderProcessor)
        processor._transfer_cargo_resources_to_colony(fleet, planet)

        assert planet.stockpile["metals"] == 500.0
        assert planet.stockpile["organics"] == 200.0
        # Cargo removed from fleet
        assert ship.cargo_contents.get("metals", 0) == 0
        assert ship.cargo_contents.get("organics", 0) == 0

    def test_skips_empty_cargo(self):
        """Resources with 0 cargo are not transferred."""
        ship = _make_cargo_ship({})
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.ships.append(ship)

        planet = MagicMock()
        planet.name = "Empty Colony"
        planet.stockpile = {}
        planet.add_to_stockpile = MagicMock()

        processor = OrderProcessor.__new__(OrderProcessor)
        processor._transfer_cargo_resources_to_colony(fleet, planet)

        planet.add_to_stockpile.assert_not_called()

    def test_does_not_transfer_colony_pods(self):
        """Colony pod cargo types are not transferred as resources."""
        ship = _make_cargo_ship({
            "metals": 100,
            "colony_pod": 1,  # Should NOT be transferred
        })
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.ships.append(ship)

        planet = MagicMock()
        planet.name = "Test Colony"
        planet.stockpile = {}

        def add_to_stockpile(res, amt):
            planet.stockpile[res] = planet.stockpile.get(res, 0.0) + amt
            return 0.0
        planet.add_to_stockpile = add_to_stockpile

        processor = OrderProcessor.__new__(OrderProcessor)
        processor._transfer_cargo_resources_to_colony(fleet, planet)

        assert "metals" in planet.stockpile
        assert "colony_pod" not in planet.stockpile
        # Pod still in cargo
        assert ship.cargo_contents.get("colony_pod", 0) == 1
