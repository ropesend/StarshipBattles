"""Tests for FleetResourceAggregator delegate class."""

import pytest
from unittest.mock import MagicMock


class TestFleetResourceAggregator:
    """Test FleetResourceAggregator delegate methods."""

    @pytest.fixture
    def mock_ship(self):
        """Create a mock ship with resource methods.

        PROJ-91: Uses generic resource API only. Type-specific methods
        (get_current_fuel, consume_fuel, etc.) were removed from ShipInstance.
        """
        ship = MagicMock()
        ship.is_combat_capable.return_value = True
        # Generic resource API (used by FleetResourceAggregator)
        ship.get_all_resource_costs_per_hex.return_value = {"fuel": 10.0, "energy": 5.0}
        ship.get_current_resource.return_value = 100.0
        ship.get_warp_resource_costs.return_value = {"energy": 50.0, "fuel": 25.0}
        # Cargo API
        ship.get_cargo_capacity.return_value = 100
        ship.get_current_cargo.return_value = 50
        ship.load_cargo.return_value = 50
        ship.unload_cargo.return_value = 50
        return ship

    @pytest.fixture
    def mock_fleet(self, mock_ship):
        """Create a mock fleet with ships."""
        fleet = MagicMock()
        fleet.get_combat_capable_ships.return_value = [mock_ship, mock_ship]
        fleet.ships = [mock_ship, mock_ship]
        fleet.speed = 5.0
        fleet.can_use_warp.return_value = True
        fleet.get_warp_limiting_ship.return_value = None
        return fleet

    @pytest.fixture
    def aggregator(self, mock_fleet):
        """Create aggregator with mock fleet."""
        from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator
        return FleetResourceAggregator(mock_fleet)

    # --- Movement Resource Tests ---

    def test_get_movement_resource_costs_aggregates(self, aggregator):
        """Movement costs aggregate across ships and resource types."""
        result = aggregator.get_movement_resource_costs()
        assert result == {"fuel": 20.0, "energy": 10.0}

    def test_has_resources_for_movement_all_available(self, aggregator):
        """Returns True when all ships have all resources."""
        assert aggregator.has_resources_for_movement() is True

    def test_consume_movement_resources_success(self, aggregator, mock_ship):
        """Consume movement resources from all ships."""
        result = aggregator.consume_movement_resources(1)
        assert result is True
        assert mock_ship.consume_resource.call_count == 4  # 2 ships x 2 resource types

    # --- Warp Resource Tests ---

    def test_get_warp_resource_costs_aggregates(self, aggregator):
        """Warp costs aggregate across ships."""
        result = aggregator.get_warp_resource_costs()
        assert result == {"energy": 100.0, "fuel": 50.0}

    def test_has_resources_for_warp_all_available(self, aggregator):
        """Returns True when all ships have warp resources."""
        assert aggregator.has_resources_for_warp() is True

    def test_consume_warp_resources_success(self, aggregator, mock_ship):
        """Consume warp resources from all ships."""
        result = aggregator.consume_warp_resources()
        assert result is True
        assert mock_ship.consume_resource.call_count == 4  # 2 ships x 2 resource types

    # --- Endurance Tests ---

    def test_fuel_endurance_returns_minimum(self, mock_fleet):
        """Fuel endurance is minimum across fleet."""
        from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator
        ship1 = MagicMock()
        ship1.is_combat_capable.return_value = True
        ship1.get_all_resource_costs_per_hex.return_value = {"fuel": 10.0}
        ship1.get_current_resource.return_value = 100.0  # 10 hexes

        ship2 = MagicMock()
        ship2.is_combat_capable.return_value = True
        ship2.get_all_resource_costs_per_hex.return_value = {"fuel": 20.0}
        ship2.get_current_resource.return_value = 100.0  # 5 hexes

        mock_fleet.get_combat_capable_ships.return_value = [ship1, ship2]
        agg = FleetResourceAggregator(mock_fleet)

        assert agg.fuel_endurance() == 5  # Minimum

    def test_fuel_endurance_no_fuel_consumption(self, mock_fleet):
        """Returns -1 when no ships consume fuel."""
        from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator
        ship = MagicMock()
        ship.is_combat_capable.return_value = True
        ship.get_all_resource_costs_per_hex.return_value = {}  # No fuel consumption
        mock_fleet.get_combat_capable_ships.return_value = [ship]
        agg = FleetResourceAggregator(mock_fleet)

        assert agg.fuel_endurance() == -1

    def test_warp_jumps_remaining_minimum_across_resources(self, mock_fleet):
        """Warp jumps is minimum across all resource constraints."""
        from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator
        ship = MagicMock()
        ship.is_combat_capable.return_value = True
        ship.get_warp_resource_costs.return_value = {"energy": 50.0, "fuel": 25.0}
        # Return 100 for energy, 50 for fuel
        ship.get_current_resource.side_effect = lambda r: 100.0 if r == 'energy' else 50.0

        mock_fleet.get_combat_capable_ships.return_value = [ship]
        mock_fleet.can_use_warp.return_value = True
        agg = FleetResourceAggregator(mock_fleet)

        assert agg.warp_jumps_remaining() == 2

    def test_warp_jumps_remaining_no_warp(self, mock_fleet):
        """Returns 0 when fleet cannot warp."""
        from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator
        mock_fleet.can_use_warp.return_value = False
        agg = FleetResourceAggregator(mock_fleet)

        assert agg.warp_jumps_remaining() == 0

    # --- Capability Summary ---

    def test_get_capability_summary(self, aggregator, mock_fleet):
        """Capability summary contains all expected keys."""
        result = aggregator.get_capability_summary()

        assert 'speed' in result
        assert 'can_warp' in result
        assert 'warp_limiting_ship' in result
        assert 'fuel_endurance' in result
        assert 'warp_jumps' in result
        assert 'movement_resource_costs' in result
        assert 'warp_resource_costs' in result

    # --- Cargo Tests ---

    def test_get_fleet_cargo_capacity(self, aggregator):
        """Cargo capacity sums across ships."""
        result = aggregator.get_fleet_cargo_capacity("passengers")
        assert result == 200  # 100 + 100

    def test_get_fleet_cargo_current(self, aggregator):
        """Current cargo sums across all ships."""
        result = aggregator.get_fleet_cargo_current("passengers")
        assert result == 100  # 50 + 50

    def test_load_cargo_to_fleet_distributes(self, aggregator, mock_ship):
        """Load cargo distributes to ships with capacity."""
        mock_ship.load_cargo.return_value = 30  # Each ship loads 30
        result = aggregator.load_cargo_to_fleet("passengers", 60)
        assert result == 60
        assert mock_ship.load_cargo.call_count == 2

    def test_load_cargo_to_fleet_stops_when_full(self, mock_fleet):
        """Stops loading when all ships are full."""
        from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator
        ship = MagicMock()
        ship.is_combat_capable.return_value = True
        ship.load_cargo.return_value = 0  # No capacity
        mock_fleet.get_combat_capable_ships.return_value = [ship]
        agg = FleetResourceAggregator(mock_fleet)

        result = agg.load_cargo_to_fleet("passengers", 100)
        assert result == 0

    def test_unload_cargo_from_fleet(self, aggregator, mock_ship):
        """Unload cargo collects from all ships."""
        mock_ship.unload_cargo.return_value = 25  # Each ship unloads 25
        result = aggregator.unload_cargo_from_fleet("passengers", 50)
        assert result == 50
        assert mock_ship.unload_cargo.call_count == 2

    def test_load_cargo_zero_amount(self, aggregator):
        """Loading zero returns zero without touching ships."""
        result = aggregator.load_cargo_to_fleet("passengers", 0)
        assert result == 0

    def test_unload_cargo_zero_amount(self, aggregator):
        """Unloading zero returns zero without touching ships."""
        result = aggregator.unload_cargo_from_fleet("passengers", 0)
        assert result == 0
