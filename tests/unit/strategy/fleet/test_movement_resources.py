"""Tests for Fleet module - movement resource methods.

PROJ-48: Split from test_resources.py
"""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.core.hex_math import HexCoord


class TestMovementResourceMethods:
    """Test cases for fleet movement resource methods (Group 4.1)."""

    @pytest.fixture
    def make_resource_ship(self):
        """Factory for creating mock ship instances with resource costs."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(
            resource_costs_per_hex: dict = None,
            current_resources: dict = None,
            is_combat_capable: bool = True
        ):
            mock = MagicMock(spec=ShipInstance)
            mock.is_combat_capable.return_value = is_combat_capable
            mock.get_all_resource_costs_per_hex.return_value = resource_costs_per_hex or {}

            # Setup get_current_resource to return from current_resources dict
            current = current_resources or {}
            mock.get_current_resource.side_effect = lambda r: current.get(r, 0)

            # Track consumed resources for verification
            mock._consumed = {}
            def consume(resource_type, amount):
                mock._consumed[resource_type] = mock._consumed.get(resource_type, 0) + amount
                return True
            mock.consume_resource.side_effect = consume

            return mock
        return _make

    def test_movement_resource_costs_single_ship(self, make_resource_ship):
        """Test movement resource costs with a single ship."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_resource_ship(resource_costs_per_hex={'fuel': 10.0})
        fleet.ships.append(ship)

        costs = fleet.resources.get_movement_resource_costs()

        assert costs == {'fuel': 10.0}

    def test_movement_resource_costs_multiple_ships(self, make_resource_ship):
        """Test movement resource costs aggregate across multiple ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_resource_ship(resource_costs_per_hex={'fuel': 10.0})
        ship2 = make_resource_ship(resource_costs_per_hex={'fuel': 15.0})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.resources.get_movement_resource_costs()

        assert costs == {'fuel': 25.0}

    def test_movement_resource_costs_mixed_resource_types(self, make_resource_ship):
        """Test movement costs with different resource types from different ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_resource_ship(resource_costs_per_hex={'fuel': 10.0, 'energy': 5.0})
        ship2 = make_resource_ship(resource_costs_per_hex={'fuel': 8.0, 'glag': 2.0})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.resources.get_movement_resource_costs()

        assert costs == {'fuel': 18.0, 'energy': 5.0, 'glag': 2.0}

    def test_movement_resource_costs_empty_fleet(self):
        """Test movement resource costs for empty fleet returns empty dict."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        costs = fleet.resources.get_movement_resource_costs()

        assert costs == {}

    def test_has_resources_for_movement_sufficient_all_ships(self, make_resource_ship):
        """Test has_resources_for_movement returns True when all ships have enough."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_resource_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        ship2 = make_resource_ship(
            resource_costs_per_hex={'fuel': 15.0},
            current_resources={'fuel': 50.0}
        )
        fleet.ships.extend([ship1, ship2])

        assert fleet.resources.has_resources_for_movement() is True

    def test_has_resources_for_movement_insufficient_fuel_one_ship(self, make_resource_ship):
        """Test has_resources_for_movement returns False when one ship lacks fuel."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_resource_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        ship2 = make_resource_ship(
            resource_costs_per_hex={'fuel': 15.0},
            current_resources={'fuel': 5.0}  # Insufficient
        )
        fleet.ships.extend([ship1, ship2])

        assert fleet.resources.has_resources_for_movement() is False

    def test_has_resources_for_movement_insufficient_energy_one_ship(self, make_resource_ship):
        """Test has_resources_for_movement returns False when one ship lacks energy."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_resource_ship(
            resource_costs_per_hex={'fuel': 10.0, 'energy': 20.0},
            current_resources={'fuel': 100.0, 'energy': 10.0}  # Energy insufficient
        )
        fleet.ships.append(ship1)

        assert fleet.resources.has_resources_for_movement() is False

    def test_has_resources_for_movement_zero_cost_resources(self, make_resource_ship):
        """Test has_resources_for_movement handles zero-cost resources correctly."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_resource_ship(
            resource_costs_per_hex={'fuel': 0.0, 'energy': 0.0},
            current_resources={'fuel': 0.0, 'energy': 0.0}
        )
        fleet.ships.append(ship)

        assert fleet.resources.has_resources_for_movement() is True

    def test_has_resources_for_movement_empty_fleet(self):
        """Test has_resources_for_movement returns True for empty fleet."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        assert fleet.resources.has_resources_for_movement() is True

    def test_consume_movement_resources_success_single_hex(self, make_resource_ship):
        """Test successful consumption of movement resources for 1 hex."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_resource_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        fleet.ships.append(ship)

        result = fleet.resources.consume_movement_resources(hexes=1)

        assert result is True
        ship.consume_resource.assert_called_with('fuel', 10.0)

    def test_consume_movement_resources_success_multiple_hexes(self, make_resource_ship):
        """Test successful consumption of movement resources for multiple hexes."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_resource_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        fleet.ships.append(ship)

        result = fleet.resources.consume_movement_resources(hexes=3)

        assert result is True
        ship.consume_resource.assert_called_with('fuel', 30.0)

    def test_consume_movement_resources_failure_atomicity(self, make_resource_ship):
        """Test that consumption fails atomically when any ship lacks resources."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_resource_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        ship2 = make_resource_ship(
            resource_costs_per_hex={'fuel': 15.0},
            current_resources={'fuel': 5.0}  # Insufficient
        )
        fleet.ships.extend([ship1, ship2])

        result = fleet.resources.consume_movement_resources(hexes=1)

        assert result is False
        # Verify no resources were consumed (atomicity)
        ship1.consume_resource.assert_not_called()
        ship2.consume_resource.assert_not_called()

    def test_consume_movement_resources_atomicity_multi_resource(self, make_resource_ship):
        """Test atomicity with multiple resource types."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_resource_ship(
            resource_costs_per_hex={'fuel': 10.0, 'energy': 20.0},
            current_resources={'fuel': 100.0, 'energy': 5.0}  # Energy insufficient
        )
        fleet.ships.append(ship)

        result = fleet.resources.consume_movement_resources(hexes=1)

        assert result is False
        ship.consume_resource.assert_not_called()

    def test_consume_movement_resources_zero_cost_resources(self, make_resource_ship):
        """Test consumption succeeds with zero-cost resources."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_resource_ship(
            resource_costs_per_hex={'fuel': 0.0},
            current_resources={'fuel': 0.0}
        )
        fleet.ships.append(ship)

        result = fleet.resources.consume_movement_resources(hexes=1)

        assert result is True
        # Zero-cost should not trigger consume call
        ship.consume_resource.assert_not_called()

    def test_consume_movement_resources_empty_fleet(self):
        """Test consumption succeeds for empty fleet (no-op)."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        result = fleet.resources.consume_movement_resources(hexes=1)

        assert result is True
