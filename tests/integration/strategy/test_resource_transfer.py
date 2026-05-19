"""
Integration tests for resource transfers between planets and fleets.

Phase 7: Verifies that resources can be loaded from planet stockpiles
to fleet cargo and unloaded back, using the transfer order system.
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.strategy.data.empire import Empire
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.order_handlers.transfer import TransferHandler
from game.strategy.engine.order_processor import OrderProcessor
from game.strategy.validation.transfer_validator import TransferValidator
from game.core.hex_math import HexCoord
from tests.fixtures.strategy_entities import create_test_planet


def _make_cargo_ship(cargo_capacity=None, cargo_contents=None):
    """Create a mock ship with resource cargo capacity."""
    ship = MagicMock()
    ship.cargo_contents = dict(cargo_contents or {})
    _cap = dict(cargo_capacity or {})
    ship.is_combat_capable = lambda: True
    ship.get_calculated_stats = lambda: {'mass': 500, 'strategic_movement': 5}

    def get_cargo_capacity(ct):
        return _cap.get(ct, 0)

    def get_current_cargo(ct):
        return ship.cargo_contents.get(ct, 0)

    def load_cargo(ct, amt):
        space = _cap.get(ct, 0) - ship.cargo_contents.get(ct, 0)
        actual = min(amt, max(0, space))
        if actual > 0:
            ship.cargo_contents[ct] = ship.cargo_contents.get(ct, 0) + actual
        return actual

    def unload_cargo(ct, amt):
        cur = ship.cargo_contents.get(ct, 0)
        actual = min(amt, cur)
        if actual > 0:
            ship.cargo_contents[ct] = cur - actual
        return actual

    ship.get_cargo_capacity = get_cargo_capacity
    ship.get_current_cargo = get_current_cargo
    ship.load_cargo = load_cargo
    ship.unload_cargo = unload_cargo

    # PROJ-425 Phase 6: production routes through ``ship._cargo_mgr``.
    cargo_mgr = MagicMock()
    cargo_mgr.get_cargo_capacity = get_cargo_capacity
    cargo_mgr.get_current_cargo = get_current_cargo
    cargo_mgr.load_cargo = load_cargo
    cargo_mgr.unload_cargo = unload_cargo
    ship._cargo_mgr = cargo_mgr
    return ship


class TestResourceTransferValidation:
    """Tests for resource transfer validation.

    PROJ-436 Phase 7: validation now consults the Core-layer
    ``ResourceCatalog`` + categorical sentinels instead of the deleted
    ``VALID_CARGO_TYPES`` hardcoded set. We exercise the validator
    end-to-end with ``skip_location_check`` so the cargo-type gate
    fires alone; an unknown type yields ``INVALID_CARGO_TYPE`` and a
    known type does not.
    """

    @pytest.mark.parametrize(
        "cargo_type",
        ["metals", "organics", "vapors", "radioactives", "exotics",
         "fuel", "energy", "ammo"],
    )
    def test_resource_cargo_types_are_valid(self, cargo_type):
        """All 8 resource types from ``data/resources.json`` are accepted."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        result = TransferValidator.validate(
            galaxy=None, fleet=fleet, target=fleet,
            cargo_type=cargo_type, direction="load", amount=1,
            skip_location_check=True,
        )
        assert result.error_code != "INVALID_CARGO_TYPE"

    def test_passengers_still_valid(self):
        """The ``passengers`` categorical sentinel remains accepted."""
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        result = TransferValidator.validate(
            galaxy=None, fleet=fleet, target=fleet,
            cargo_type="passengers", direction="load", amount=1,
            skip_location_check=True,
        )
        assert result.error_code != "INVALID_CARGO_TYPE"


class TestResourceLoadFromPlanet:
    """Tests for loading resources from planet stockpile to fleet cargo."""

    def test_load_metals_from_planet_to_fleet(self):
        """Loading metals transfers from planet.stockpile to fleet cargo."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 500.0},
        )

        ship = _make_cargo_ship(cargo_capacity={"metals": 1000})
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.ships.append(ship)

        empire = Empire(empire_id=0, name="Test", color=(255, 0, 0))
        empire.add_colony(planet)

        processor = TransferHandler()
        transferred = processor._dispatch_load_planet_resource(fleet, planet, "metals", 200)

        assert transferred == 200
        assert planet.get_stockpile("metals") == pytest.approx(300.0)
        assert ship.cargo_contents["metals"] == 200

    def test_load_capped_by_planet_stockpile(self):
        """Loading is capped by planet's available stockpile."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 50.0},
        )

        ship = _make_cargo_ship(cargo_capacity={"metals": 1000})
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.ships.append(ship)

        empire = Empire(empire_id=0, name="Test", color=(255, 0, 0))

        processor = TransferHandler()
        transferred = processor._dispatch_load_planet_resource(fleet, planet, "metals", 200)

        assert transferred == 50
        assert planet.get_stockpile("metals") == pytest.approx(0.0)

    def test_load_capped_by_fleet_cargo_capacity(self):
        """Loading is capped by fleet's available cargo space."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 1000.0},
        )

        ship = _make_cargo_ship(cargo_capacity={"metals": 100})
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.ships.append(ship)

        empire = Empire(empire_id=0, name="Test", color=(255, 0, 0))

        processor = TransferHandler()
        transferred = processor._dispatch_load_planet_resource(fleet, planet, "metals", 500)

        assert transferred == 100


class TestResourceUnloadToPlanet:
    """Tests for unloading resources from fleet cargo to planet stockpile."""

    def test_unload_metals_from_fleet_to_planet(self):
        """Unloading metals transfers from fleet cargo to planet.stockpile."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 100.0},
            _max_stockpile={"metals": 10000.0},
        )

        ship = _make_cargo_ship(
            cargo_capacity={"metals": 1000},
            cargo_contents={"metals": 500},
        )
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.ships.append(ship)

        empire = Empire(empire_id=0, name="Test", color=(255, 0, 0))

        processor = TransferHandler()
        transferred = processor._dispatch_unload_planet_resource(fleet, planet, "metals", 200)

        assert transferred == 200
        assert planet.get_stockpile("metals") == pytest.approx(300.0)
        assert ship.cargo_contents["metals"] == 300

    def test_unload_amount_zero_means_all(self):
        """Amount 0 unloads all available cargo."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _max_stockpile={"fuel": 10000.0},
        )

        ship = _make_cargo_ship(
            cargo_capacity={"fuel": 1000},
            cargo_contents={"fuel": 750},
        )
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        fleet.ships.append(ship)

        empire = Empire(empire_id=0, name="Test", color=(255, 0, 0))

        processor = TransferHandler()
        transferred = processor._dispatch_unload_planet_resource(fleet, planet, "fuel", 0)

        assert transferred == 750
        assert planet.get_stockpile("fuel") == pytest.approx(750.0)
        assert ship.cargo_contents["fuel"] == 0
