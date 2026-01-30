"""Tests for Fleet module - resource methods (movement, warp, edge cases)."""
import pytest
from unittest.mock import MagicMock

from game.strategy.data.fleet import Fleet
from game.strategy.data.hex_math import HexCoord


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

        costs = fleet.get_movement_resource_costs()

        assert costs == {'fuel': 10.0}

    def test_movement_resource_costs_multiple_ships(self, make_resource_ship):
        """Test movement resource costs aggregate across multiple ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_resource_ship(resource_costs_per_hex={'fuel': 10.0})
        ship2 = make_resource_ship(resource_costs_per_hex={'fuel': 15.0})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.get_movement_resource_costs()

        assert costs == {'fuel': 25.0}

    def test_movement_resource_costs_mixed_resource_types(self, make_resource_ship):
        """Test movement costs with different resource types from different ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_resource_ship(resource_costs_per_hex={'fuel': 10.0, 'energy': 5.0})
        ship2 = make_resource_ship(resource_costs_per_hex={'fuel': 8.0, 'glag': 2.0})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.get_movement_resource_costs()

        assert costs == {'fuel': 18.0, 'energy': 5.0, 'glag': 2.0}

    def test_movement_resource_costs_empty_fleet(self):
        """Test movement resource costs for empty fleet returns empty dict."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        costs = fleet.get_movement_resource_costs()

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

        assert fleet.has_resources_for_movement() is True

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

        assert fleet.has_resources_for_movement() is False

    def test_has_resources_for_movement_insufficient_energy_one_ship(self, make_resource_ship):
        """Test has_resources_for_movement returns False when one ship lacks energy."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_resource_ship(
            resource_costs_per_hex={'fuel': 10.0, 'energy': 20.0},
            current_resources={'fuel': 100.0, 'energy': 10.0}  # Energy insufficient
        )
        fleet.ships.append(ship1)

        assert fleet.has_resources_for_movement() is False

    def test_has_resources_for_movement_zero_cost_resources(self, make_resource_ship):
        """Test has_resources_for_movement handles zero-cost resources correctly."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_resource_ship(
            resource_costs_per_hex={'fuel': 0.0, 'energy': 0.0},
            current_resources={'fuel': 0.0, 'energy': 0.0}
        )
        fleet.ships.append(ship)

        assert fleet.has_resources_for_movement() is True

    def test_has_resources_for_movement_empty_fleet(self):
        """Test has_resources_for_movement returns True for empty fleet."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        assert fleet.has_resources_for_movement() is True

    def test_consume_movement_resources_success_single_hex(self, make_resource_ship):
        """Test successful consumption of movement resources for 1 hex."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_resource_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        fleet.ships.append(ship)

        result = fleet.consume_movement_resources(hexes=1)

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

        result = fleet.consume_movement_resources(hexes=3)

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

        result = fleet.consume_movement_resources(hexes=1)

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

        result = fleet.consume_movement_resources(hexes=1)

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

        result = fleet.consume_movement_resources(hexes=1)

        assert result is True
        # Zero-cost should not trigger consume call
        ship.consume_resource.assert_not_called()

    def test_consume_movement_resources_empty_fleet(self):
        """Test consumption succeeds for empty fleet (no-op)."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        result = fleet.consume_movement_resources(hexes=1)

        assert result is True


class TestWarpResourceMethods:
    """Test cases for fleet warp resource methods (Group 4.2)."""

    @pytest.fixture
    def make_warp_ship(self):
        """Factory for creating mock ship instances with warp costs."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(
            warp_resource_costs: dict = None,
            current_resources: dict = None,
            is_combat_capable: bool = True
        ):
            mock = MagicMock(spec=ShipInstance)
            mock.is_combat_capable.return_value = is_combat_capable
            mock.get_warp_resource_costs.return_value = warp_resource_costs or {}

            current = current_resources or {}
            mock.get_current_resource.side_effect = lambda r: current.get(r, 0)

            mock._consumed = {}
            def consume(resource_type, amount):
                mock._consumed[resource_type] = mock._consumed.get(resource_type, 0) + amount
                return True
            mock.consume_resource.side_effect = consume

            return mock
        return _make

    def test_warp_resource_costs_single_ship(self, make_warp_ship):
        """Test warp resource costs with a single ship."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_warp_ship(warp_resource_costs={'energy': 500.0})
        fleet.ships.append(ship)

        costs = fleet.get_warp_resource_costs()

        assert costs == {'energy': 500.0}

    def test_warp_resource_costs_multiple_ships(self, make_warp_ship):
        """Test warp resource costs aggregate across multiple ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_warp_ship(warp_resource_costs={'energy': 500.0})
        ship2 = make_warp_ship(warp_resource_costs={'energy': 300.0})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.get_warp_resource_costs()

        assert costs == {'energy': 800.0}

    def test_warp_resource_costs_mixed_resource_types(self, make_warp_ship):
        """Test warp costs with different resource types (energy and fuel)."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_warp_ship(warp_resource_costs={'energy': 500.0, 'fuel': 100.0})
        ship2 = make_warp_ship(warp_resource_costs={'energy': 300.0, 'fuel': 50.0})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.get_warp_resource_costs()

        assert costs == {'energy': 800.0, 'fuel': 150.0}

    def test_warp_resource_costs_empty_fleet(self):
        """Test warp resource costs for empty fleet returns empty dict."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        costs = fleet.get_warp_resource_costs()

        assert costs == {}

    def test_has_resources_for_warp_sufficient_all_ships(self, make_warp_ship):
        """Test has_resources_for_warp returns True when all ships have enough."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_warp_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        ship2 = make_warp_ship(
            warp_resource_costs={'energy': 300.0},
            current_resources={'energy': 800.0}
        )
        fleet.ships.extend([ship1, ship2])

        assert fleet.has_resources_for_warp() is True

    def test_has_resources_for_warp_insufficient_energy_one_ship(self, make_warp_ship):
        """Test has_resources_for_warp returns False when one ship lacks energy."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_warp_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        ship2 = make_warp_ship(
            warp_resource_costs={'energy': 300.0},
            current_resources={'energy': 100.0}  # Insufficient
        )
        fleet.ships.extend([ship1, ship2])

        assert fleet.has_resources_for_warp() is False

    def test_has_resources_for_warp_insufficient_fuel_one_ship(self, make_warp_ship):
        """Test has_resources_for_warp returns False when one ship lacks fuel."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_warp_ship(
            warp_resource_costs={'energy': 500.0, 'fuel': 100.0},
            current_resources={'energy': 1000.0, 'fuel': 50.0}  # Fuel insufficient
        )
        fleet.ships.append(ship)

        assert fleet.has_resources_for_warp() is False

    def test_has_resources_for_warp_zero_cost_resources(self, make_warp_ship):
        """Test has_resources_for_warp handles zero-cost resources correctly."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_warp_ship(
            warp_resource_costs={'energy': 0.0},
            current_resources={'energy': 0.0}
        )
        fleet.ships.append(ship)

        assert fleet.has_resources_for_warp() is True

    def test_has_resources_for_warp_empty_fleet(self):
        """Test has_resources_for_warp returns True for empty fleet."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        assert fleet.has_resources_for_warp() is True

    def test_consume_warp_resources_success_all_ships(self, make_warp_ship):
        """Test successful consumption of warp resources from all ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_warp_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        ship2 = make_warp_ship(
            warp_resource_costs={'energy': 300.0},
            current_resources={'energy': 800.0}
        )
        fleet.ships.extend([ship1, ship2])

        result = fleet.consume_warp_resources()

        assert result is True
        ship1.consume_resource.assert_called_with('energy', 500.0)
        ship2.consume_resource.assert_called_with('energy', 300.0)

    def test_consume_warp_resources_failure_atomicity(self, make_warp_ship):
        """Test that warp consumption fails atomically when any ship lacks resources."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_warp_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        ship2 = make_warp_ship(
            warp_resource_costs={'energy': 300.0},
            current_resources={'energy': 100.0}  # Insufficient
        )
        fleet.ships.extend([ship1, ship2])

        result = fleet.consume_warp_resources()

        assert result is False
        ship1.consume_resource.assert_not_called()
        ship2.consume_resource.assert_not_called()

    def test_consume_warp_resources_atomicity_multi_resource(self, make_warp_ship):
        """Test warp atomicity with multiple resource types."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_warp_ship(
            warp_resource_costs={'energy': 500.0, 'fuel': 100.0},
            current_resources={'energy': 1000.0, 'fuel': 50.0}  # Fuel insufficient
        )
        fleet.ships.append(ship)

        result = fleet.consume_warp_resources()

        assert result is False
        ship.consume_resource.assert_not_called()

    def test_consume_warp_resources_zero_cost_resources(self, make_warp_ship):
        """Test warp consumption succeeds with zero-cost resources."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_warp_ship(
            warp_resource_costs={'energy': 0.0},
            current_resources={'energy': 0.0}
        )
        fleet.ships.append(ship)

        result = fleet.consume_warp_resources()

        assert result is True
        ship.consume_resource.assert_not_called()

    def test_consume_warp_resources_empty_fleet(self):
        """Test warp consumption succeeds for empty fleet (no-op)."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        result = fleet.consume_warp_resources()

        assert result is True


class TestBackwardCompatibility:
    """Test cases for backward compatibility wrappers (Group 4.3)."""

    @pytest.fixture
    def make_compat_ship(self):
        """Factory for creating mock ship instances."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(
            warp_resource_costs: dict = None,
            current_resources: dict = None,
            is_combat_capable: bool = True,
            fuel_cost_per_hex: float = 0.0
        ):
            mock = MagicMock(spec=ShipInstance)
            mock.is_combat_capable.return_value = is_combat_capable
            mock.get_warp_resource_costs.return_value = warp_resource_costs or {}
            mock.get_fuel_cost_per_hex.return_value = fuel_cost_per_hex
            mock.get_all_resource_costs_per_hex.return_value = {'fuel': fuel_cost_per_hex} if fuel_cost_per_hex else {}

            current = current_resources or {}
            mock.get_current_resource.side_effect = lambda r: current.get(r, 0)
            mock.get_current_fuel.return_value = current.get('fuel', 0)

            mock._consumed = {}
            def consume(resource_type, amount):
                mock._consumed[resource_type] = mock._consumed.get(resource_type, 0) + amount
                return True
            mock.consume_resource.side_effect = consume
            mock.consume_fuel.side_effect = lambda amt: True

            return mock
        return _make

    def test_backward_compat_consume_fleet_fuel_wrapper(self, make_compat_ship):
        """Test consume_fleet_fuel uses legacy fuel methods."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_compat_ship(
            fuel_cost_per_hex=10.0,
            current_resources={'fuel': 100.0}
        )
        fleet.ships.append(ship)

        result = fleet.consume_fleet_fuel(hexes=1)

        assert result is True


class TestEdgeCases:
    """Test cases for edge cases (Group 4.4)."""

    @pytest.fixture
    def make_edge_ship(self):
        """Factory for creating mock ship instances."""
        from game.strategy.data.ship_instance import ShipInstance

        def _make(
            resource_costs_per_hex: dict = None,
            warp_resource_costs: dict = None,
            current_resources: dict = None,
            is_combat_capable: bool = True,
            is_destroyed: bool = False,
            is_derelict: bool = False
        ):
            mock = MagicMock(spec=ShipInstance)
            mock.is_combat_capable.return_value = is_combat_capable and not is_destroyed and not is_derelict
            mock.is_destroyed = is_destroyed
            mock.is_derelict = is_derelict
            mock.get_all_resource_costs_per_hex.return_value = resource_costs_per_hex or {}
            mock.get_warp_resource_costs.return_value = warp_resource_costs or {}

            current = current_resources or {}
            mock.get_current_resource.side_effect = lambda r: current.get(r, 0)

            mock._consumed = {}
            def consume(resource_type, amount):
                mock._consumed[resource_type] = mock._consumed.get(resource_type, 0) + amount
                return True
            mock.consume_resource.side_effect = consume

            return mock
        return _make

    def test_destroyed_ships_excluded_from_movement_calculation(self, make_edge_ship):
        """Test that destroyed ships are excluded from movement cost calculations."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        active_ship = make_edge_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        destroyed_ship = make_edge_ship(
            resource_costs_per_hex={'fuel': 50.0},  # Should be ignored
            current_resources={'fuel': 0.0},
            is_destroyed=True,
            is_combat_capable=False
        )
        fleet.ships.extend([active_ship, destroyed_ship])

        costs = fleet.get_movement_resource_costs()

        # Only active ship's cost should be counted
        assert costs == {'fuel': 10.0}

    def test_derelict_ships_excluded_from_warp_calculation(self, make_edge_ship):
        """Test that derelict ships are excluded from warp cost calculations."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        active_ship = make_edge_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        derelict_ship = make_edge_ship(
            warp_resource_costs={'energy': 1000.0},  # Should be ignored
            current_resources={'energy': 0.0},
            is_derelict=True,
            is_combat_capable=False
        )
        fleet.ships.extend([active_ship, derelict_ship])

        costs = fleet.get_warp_resource_costs()

        # Only active ship's cost should be counted
        assert costs == {'energy': 500.0}

    def test_mixed_destroyed_and_combat_capable_ships(self, make_edge_ship):
        """Test mixed fleet with both destroyed and active ships."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        active1 = make_edge_ship(
            resource_costs_per_hex={'fuel': 10.0},
            current_resources={'fuel': 100.0}
        )
        destroyed = make_edge_ship(
            resource_costs_per_hex={'fuel': 20.0},
            is_destroyed=True,
            is_combat_capable=False
        )
        derelict = make_edge_ship(
            resource_costs_per_hex={'fuel': 30.0},
            is_derelict=True,
            is_combat_capable=False
        )
        active2 = make_edge_ship(
            resource_costs_per_hex={'fuel': 15.0},
            current_resources={'fuel': 80.0}
        )
        fleet.ships.extend([active1, destroyed, derelict, active2])

        costs = fleet.get_movement_resource_costs()

        # Only active ships' costs
        assert costs == {'fuel': 25.0}

    def test_very_large_fleet(self, make_edge_ship):
        """Test resource calculations with a very large fleet."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))

        # Add 100 ships
        for i in range(100):
            ship = make_edge_ship(
                resource_costs_per_hex={'fuel': 1.0},
                current_resources={'fuel': 100.0}
            )
            fleet.ships.append(ship)

        costs = fleet.get_movement_resource_costs()

        assert costs == {'fuel': 100.0}  # 100 ships * 1.0 fuel each

    def test_ships_with_no_resource_costs(self, make_edge_ship):
        """Test fleet where ships have no resource costs."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship1 = make_edge_ship(resource_costs_per_hex={})
        ship2 = make_edge_ship(resource_costs_per_hex={})
        fleet.ships.extend([ship1, ship2])

        costs = fleet.get_movement_resource_costs()

        assert costs == {}
        assert fleet.has_resources_for_movement() is True
        assert fleet.consume_movement_resources(hexes=1) is True

    def test_floating_point_precision_in_resource_consumption(self, make_edge_ship):
        """Test that floating point precision is handled correctly."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        # Use values that could cause floating point issues
        ship = make_edge_ship(
            resource_costs_per_hex={'fuel': 0.1},
            current_resources={'fuel': 1.0}
        )
        fleet.ships.append(ship)

        # Moving 3 hexes should cost 0.3 fuel (common floating point issue: 0.1 + 0.1 + 0.1)
        result = fleet.consume_movement_resources(hexes=3)

        assert result is True
        # The cost should be 0.3 (0.1 * 3)
        call_args = ship.consume_resource.call_args[0]
        assert call_args[0] == 'fuel'
        assert abs(call_args[1] - 0.3) < 0.0001  # Allow small floating point tolerance

    def test_warp_capability_check_integration(self, make_edge_ship):
        """Test integration between can_use_warp and resource checks."""
        fleet = Fleet("f1", 0, HexCoord(0, 0))
        ship = make_edge_ship(
            warp_resource_costs={'energy': 500.0},
            current_resources={'energy': 1000.0}
        )
        fleet.ships.append(ship)

        # Even with resources, has_resources_for_warp only checks resources
        # The actual warp capability (has warp drive) is checked by can_use_warp
        assert fleet.has_resources_for_warp() is True

        # Consumption should still work
        result = fleet.consume_warp_resources()
        assert result is True
