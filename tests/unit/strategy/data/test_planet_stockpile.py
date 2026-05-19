"""
Tests for Planet local stockpile system.

Phase 1 of local resource storage: Verify that planets can hold, add,
consume, and serialize local resource stockpiles independently of the
empire-wide resource pool.
"""
import pytest
from game.strategy.data.planet import Planet
from tests.fixtures.strategy_entities import create_test_planet


class TestPlanetStockpileFields:
    """Test that stockpile and max_stockpile fields exist and initialize correctly."""

    def test_stockpile_defaults_to_empty_dict(self):
        """New planet has empty stockpile."""
        planet = create_test_planet(has_facilities=False, has_population=False)
        assert planet.stockpile == {}

    def test_max_stockpile_defaults_to_empty_dict(self):
        """New planet has empty max_stockpile."""
        planet = create_test_planet(has_facilities=False, has_population=False)
        assert planet.max_stockpile == {}

    def test_stockpile_can_be_set_at_construction(self):
        """Stockpile can be initialized with values."""
        planet = create_test_planet(
            has_facilities=False,
            has_population=False,
            _stockpile={"metals": 500.0, "fuel": 100.0},
        )
        assert planet.stockpile == {"metals": 500.0, "fuel": 100.0}

    def test_max_stockpile_can_be_set_at_construction(self):
        """Max stockpile can be initialized with values."""
        planet = create_test_planet(
            has_facilities=False,
            has_population=False,
            _max_stockpile={"metals": 10000.0},
        )
        assert planet.max_stockpile == {"metals": 10000.0}


class TestAddToStockpile:
    """Tests for Planet.add_to_stockpile() method."""

    def test_add_to_empty_stockpile(self):
        """Adding to empty stockpile creates the entry."""
        planet = create_test_planet(has_facilities=False, has_population=False)
        overflow = planet.add_to_stockpile("metals", 100.0)

        assert planet.stockpile["metals"] == 100.0
        assert overflow == 0.0

    def test_add_to_existing_stockpile(self):
        """Adding to existing stockpile accumulates."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 200.0},
        )
        overflow = planet.add_to_stockpile("metals", 300.0)

        assert planet.stockpile["metals"] == 500.0
        assert overflow == 0.0

    def test_add_respects_max_stockpile(self):
        """Adding beyond capacity caps at max and returns overflow."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 800.0},
            _max_stockpile={"metals": 1000.0},
        )
        overflow = planet.add_to_stockpile("metals", 300.0)

        assert planet.stockpile["metals"] == 1000.0
        assert overflow == pytest.approx(100.0)

    def test_add_with_no_max_is_unlimited(self):
        """Without a max_stockpile entry, storage is unlimited."""
        planet = create_test_planet(has_facilities=False, has_population=False)
        overflow = planet.add_to_stockpile("metals", 1_000_000.0)

        assert planet.stockpile["metals"] == 1_000_000.0
        assert overflow == 0.0

    def test_add_multiple_resource_types(self):
        """Different resource types are tracked independently."""
        planet = create_test_planet(has_facilities=False, has_population=False)
        planet.add_to_stockpile("metals", 100.0)
        planet.add_to_stockpile("fuel", 50.0)

        assert planet.stockpile["metals"] == 100.0
        assert planet.stockpile["fuel"] == 50.0


class TestConsumeFromStockpile:
    """Tests for Planet.consume_from_stockpile() method."""

    def test_consume_succeeds_with_sufficient_resources(self):
        """Consuming available resources returns True and deducts."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 500.0},
        )
        result = planet.consume_from_stockpile("metals", 200.0)

        assert result is True
        assert planet.stockpile["metals"] == pytest.approx(300.0)

    def test_consume_fails_with_insufficient_resources(self):
        """Consuming more than available returns False with no deduction."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 100.0},
        )
        result = planet.consume_from_stockpile("metals", 200.0)

        assert result is False
        assert planet.stockpile["metals"] == 100.0  # Unchanged

    def test_consume_fails_for_missing_resource(self):
        """Consuming a resource not in stockpile returns False."""
        planet = create_test_planet(has_facilities=False, has_population=False)
        result = planet.consume_from_stockpile("metals", 10.0)

        assert result is False

    def test_consume_exact_amount(self):
        """Consuming exactly available amount succeeds."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 100.0},
        )
        result = planet.consume_from_stockpile("metals", 100.0)

        assert result is True
        assert planet.stockpile["metals"] == 0.0


class TestHasStockpile:
    """Tests for Planet.has_stockpile() method."""

    def test_has_stockpile_with_sufficient_resources(self):
        """Returns True when all costs are available."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 500.0, "organics": 200.0},
        )
        assert planet.has_stockpile({"metals": 100.0, "organics": 50.0}) is True

    def test_has_stockpile_with_insufficient_resources(self):
        """Returns False when any cost exceeds available."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 50.0, "organics": 200.0},
        )
        assert planet.has_stockpile({"metals": 100.0, "organics": 50.0}) is False

    def test_has_stockpile_with_missing_resource(self):
        """Returns False when a required resource is not in stockpile."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 500.0},
        )
        assert planet.has_stockpile({"metals": 100.0, "exotics": 10.0}) is False

    def test_has_stockpile_empty_costs(self):
        """Empty costs dict always returns True."""
        planet = create_test_planet(has_facilities=False, has_population=False)
        assert planet.has_stockpile({}) is True

    def test_get_stockpile_resource(self):
        """get_stockpile() returns amount for a specific resource."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 250.0},
        )
        assert planet.get_stockpile("metals") == 250.0
        assert planet.get_stockpile("organics") == 0.0


class TestStockpileSerialization:
    """Tests for stockpile round-trip through to_dict/from_dict."""

    def test_stockpile_serialized_in_to_dict(self):
        """Stockpile is included in serialized dict."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 123.0, "fuel": 45.0},
            _max_stockpile={"metals": 5000.0, "fuel": 1000.0},
        )
        data = planet.to_dict()

        assert data["stockpile"] == {"metals": 123.0, "fuel": 45.0}
        assert data["max_stockpile"] == {"metals": 5000.0, "fuel": 1000.0}

    def test_stockpile_round_trips(self):
        """Stockpile survives to_dict → from_dict cycle."""
        planet = create_test_planet(
            has_facilities=False, has_population=False,
            _stockpile={"metals": 500.0, "organics": 200.0},
            _max_stockpile={"metals": 10000.0, "organics": 5000.0},
        )
        data = planet.to_dict()
        restored = Planet.from_dict(data)

        assert restored.stockpile == {"metals": 500.0, "organics": 200.0}
        assert restored.max_stockpile == {"metals": 10000.0, "organics": 5000.0}

    def test_missing_stockpile_in_data_defaults_to_empty(self):
        """Loading old save data without stockpile fields defaults to empty dicts."""
        planet = create_test_planet(has_facilities=False, has_population=False)
        data = planet.to_dict()
        # Simulate old save without stockpile
        data.pop("stockpile", None)
        data.pop("max_stockpile", None)

        restored = Planet.from_dict(data)
        assert restored.stockpile == {}
        assert restored.max_stockpile == {}
