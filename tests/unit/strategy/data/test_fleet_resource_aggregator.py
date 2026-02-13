"""
Unit tests for FleetResourceAggregator.

PROJ-119 Task 1.5: TCG-STR-005 - FleetResourceAggregator lacks atomic operation tests.
Tests focus on atomic resource operations and cargo management.
"""

import pytest
from unittest.mock import MagicMock

from game.core.constants import ResourceType


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_fleet():
    """Create a mock Fleet."""
    fleet = MagicMock()
    fleet.ships = []
    fleet.speed = 10
    fleet.can_use_warp.return_value = True
    fleet.get_warp_limiting_ship.return_value = None
    return fleet


@pytest.fixture
def mock_ship():
    """Create a mock ship with resource methods."""
    ship = MagicMock()
    ship.get_all_resource_costs_per_hex.return_value = {ResourceType.FUEL: 10.0}
    ship.get_current_resource.return_value = 100.0
    ship.consume_resource = MagicMock()
    ship.get_warp_resource_costs.return_value = {ResourceType.FUEL: 50.0}
    ship.get_cargo_capacity.return_value = 100
    ship.get_current_cargo.return_value = 0
    ship.load_cargo = MagicMock(return_value=100)
    ship.unload_cargo = MagicMock(return_value=0)
    return ship


@pytest.fixture
def resource_aggregator(mock_fleet):
    """Create a FleetResourceAggregator with mock fleet."""
    from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator
    return FleetResourceAggregator(mock_fleet)


# =============================================================================
# Test: Initialization
# =============================================================================

class TestFleetResourceAggregatorInit:
    """Tests for FleetResourceAggregator initialization."""

    def test_aggregator_can_be_created(self, mock_fleet):
        """FleetResourceAggregator can be instantiated."""
        from game.strategy.data.fleet_resource_aggregator import FleetResourceAggregator

        aggregator = FleetResourceAggregator(mock_fleet)

        assert aggregator is not None
        assert aggregator._fleet is mock_fleet


# =============================================================================
# Test: Movement Resource Methods
# =============================================================================

class TestMovementResources:
    """Tests for movement resource methods."""

    def test_get_movement_resource_costs_empty_fleet(self, resource_aggregator, mock_fleet):
        """Empty fleet has no movement costs."""
        mock_fleet.get_combat_capable_ships.return_value = []

        result = resource_aggregator.get_movement_resource_costs()

        assert result == {}

    def test_get_movement_resource_costs_single_ship(self, resource_aggregator, mock_fleet, mock_ship):
        """Single ship movement costs returned."""
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.get_movement_resource_costs()

        assert ResourceType.FUEL in result
        assert result[ResourceType.FUEL] == 10.0

    def test_get_movement_resource_costs_multiple_ships(self, resource_aggregator, mock_fleet, mock_ship):
        """Multiple ship movement costs are summed."""
        ship2 = MagicMock()
        ship2.get_all_resource_costs_per_hex.return_value = {ResourceType.FUEL: 15.0}
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship, ship2]

        result = resource_aggregator.get_movement_resource_costs()

        assert result[ResourceType.FUEL] == 25.0  # 10 + 15

    def test_has_resources_for_movement_true(self, resource_aggregator, mock_fleet, mock_ship):
        """Returns True when ship has enough resources."""
        mock_ship.get_current_resource.return_value = 100.0  # More than 10 cost
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.has_resources_for_movement()

        assert result is True

    def test_has_resources_for_movement_false(self, resource_aggregator, mock_fleet, mock_ship):
        """Returns False when ship lacks resources."""
        mock_ship.get_current_resource.return_value = 5.0  # Less than 10 cost
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.has_resources_for_movement()

        assert result is False

    def test_has_resources_for_movement_empty_fleet(self, resource_aggregator, mock_fleet):
        """Empty fleet has resources (vacuously true)."""
        mock_fleet.get_combat_capable_ships.return_value = []

        result = resource_aggregator.has_resources_for_movement()

        assert result is True


# =============================================================================
# Test: Atomic Movement Resource Consumption
# =============================================================================

class TestAtomicMovementConsumption:
    """Tests for atomic consume_movement_resources()."""

    def test_consume_returns_true_on_success(self, resource_aggregator, mock_fleet, mock_ship):
        """Returns True when all ships have enough resources."""
        mock_ship.get_current_resource.return_value = 100.0
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.consume_movement_resources(hexes=1)

        assert result is True

    def test_consume_returns_false_when_insufficient(self, resource_aggregator, mock_fleet, mock_ship):
        """Returns False when ship lacks resources."""
        mock_ship.get_current_resource.return_value = 5.0  # Less than 10 cost
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.consume_movement_resources(hexes=1)

        assert result is False

    def test_consume_no_resources_consumed_on_failure(self, resource_aggregator, mock_fleet, mock_ship):
        """No resources consumed when operation fails (atomic)."""
        mock_ship.get_current_resource.return_value = 5.0  # Insufficient
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        resource_aggregator.consume_movement_resources(hexes=1)

        mock_ship.consume_resource.assert_not_called()

    def test_consume_all_ships_checked_before_consuming(self, resource_aggregator, mock_fleet):
        """All ships verified before any consumption (atomic)."""
        ship1 = MagicMock()
        ship1.get_all_resource_costs_per_hex.return_value = {ResourceType.FUEL: 10.0}
        ship1.get_current_resource.return_value = 100.0  # Has enough

        ship2 = MagicMock()
        ship2.get_all_resource_costs_per_hex.return_value = {ResourceType.FUEL: 10.0}
        ship2.get_current_resource.return_value = 5.0  # Not enough

        mock_fleet.get_combat_capable_ships.return_value = [ship1, ship2]

        result = resource_aggregator.consume_movement_resources(hexes=1)

        # Should fail and neither ship should have resources consumed
        assert result is False
        ship1.consume_resource.assert_not_called()
        ship2.consume_resource.assert_not_called()

    def test_consume_scales_with_hexes(self, resource_aggregator, mock_fleet, mock_ship):
        """Resource consumption scales with hex count."""
        mock_ship.get_current_resource.return_value = 100.0
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        resource_aggregator.consume_movement_resources(hexes=5)

        # Should consume 10 * 5 = 50 fuel
        mock_ship.consume_resource.assert_called_with(ResourceType.FUEL, 50.0)


# =============================================================================
# Test: Warp Resource Methods
# =============================================================================

class TestWarpResources:
    """Tests for warp resource methods."""

    def test_get_warp_resource_costs(self, resource_aggregator, mock_fleet, mock_ship):
        """Warp costs are aggregated from ships."""
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.get_warp_resource_costs()

        assert ResourceType.FUEL in result
        assert result[ResourceType.FUEL] == 50.0

    def test_has_resources_for_warp_true(self, resource_aggregator, mock_fleet, mock_ship):
        """Returns True when ship has enough warp resources."""
        mock_ship.get_current_resource.return_value = 100.0  # More than 50 cost
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.has_resources_for_warp()

        assert result is True

    def test_has_resources_for_warp_false(self, resource_aggregator, mock_fleet, mock_ship):
        """Returns False when ship lacks warp resources."""
        mock_ship.get_current_resource.return_value = 30.0  # Less than 50 cost
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.has_resources_for_warp()

        assert result is False


# =============================================================================
# Test: Atomic Warp Resource Consumption
# =============================================================================

class TestAtomicWarpConsumption:
    """Tests for atomic consume_warp_resources()."""

    def test_consume_warp_returns_true_on_success(self, resource_aggregator, mock_fleet, mock_ship):
        """Returns True when all ships have enough warp resources."""
        mock_ship.get_current_resource.return_value = 100.0
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.consume_warp_resources()

        assert result is True

    def test_consume_warp_returns_false_when_insufficient(self, resource_aggregator, mock_fleet, mock_ship):
        """Returns False when ship lacks warp resources."""
        mock_ship.get_current_resource.return_value = 30.0  # Less than 50 cost
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.consume_warp_resources()

        assert result is False

    def test_consume_warp_no_resources_on_failure(self, resource_aggregator, mock_fleet, mock_ship):
        """No resources consumed when warp fails (atomic)."""
        mock_ship.get_current_resource.return_value = 30.0  # Insufficient
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        resource_aggregator.consume_warp_resources()

        mock_ship.consume_resource.assert_not_called()


# =============================================================================
# Test: Capability Summary Methods
# =============================================================================

class TestCapabilitySummary:
    """Tests for capability summary methods."""

    def test_fuel_endurance_calculation(self, resource_aggregator, mock_fleet, mock_ship):
        """Fuel endurance calculated correctly."""
        mock_ship.get_current_resource.return_value = 100.0
        mock_ship.get_all_resource_costs_per_hex.return_value = {ResourceType.FUEL: 10.0}
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.fuel_endurance()

        assert result == 10  # 100 / 10

    def test_fuel_endurance_unlimited(self, resource_aggregator, mock_fleet, mock_ship):
        """Returns -1 for unlimited endurance (no fuel cost)."""
        mock_ship.get_all_resource_costs_per_hex.return_value = {}  # No fuel cost
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.fuel_endurance()

        assert result == -1

    def test_fuel_endurance_limited_by_slowest_ship(self, resource_aggregator, mock_fleet):
        """Endurance limited by ship with least fuel."""
        ship1 = MagicMock()
        ship1.get_current_resource.return_value = 100.0
        ship1.get_all_resource_costs_per_hex.return_value = {ResourceType.FUEL: 10.0}

        ship2 = MagicMock()
        ship2.get_current_resource.return_value = 30.0  # Less fuel
        ship2.get_all_resource_costs_per_hex.return_value = {ResourceType.FUEL: 10.0}

        mock_fleet.get_combat_capable_ships.return_value = [ship1, ship2]

        result = resource_aggregator.fuel_endurance()

        assert result == 3  # 30 / 10 (limited by ship2)

    def test_warp_jumps_remaining_no_warp(self, resource_aggregator, mock_fleet):
        """Returns 0 when fleet cannot warp."""
        mock_fleet.can_use_warp.return_value = False

        result = resource_aggregator.warp_jumps_remaining()

        assert result == 0

    def test_warp_jumps_remaining_calculation(self, resource_aggregator, mock_fleet, mock_ship):
        """Warp jumps calculated correctly."""
        mock_ship.get_current_resource.return_value = 150.0
        mock_ship.get_warp_resource_costs.return_value = {ResourceType.FUEL: 50.0}
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]
        mock_fleet.can_use_warp.return_value = True

        result = resource_aggregator.warp_jumps_remaining()

        assert result == 3  # 150 / 50

    def test_get_capability_summary(self, resource_aggregator, mock_fleet, mock_ship):
        """Capability summary includes all expected fields."""
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]
        mock_fleet.can_use_warp.return_value = True

        result = resource_aggregator.get_capability_summary()

        assert 'speed' in result
        assert 'can_warp' in result
        assert 'fuel_endurance' in result
        assert 'warp_jumps' in result
        assert 'movement_resource_costs' in result
        assert 'warp_resource_costs' in result


# =============================================================================
# Test: Cargo Methods
# =============================================================================

class TestCargoMethods:
    """Tests for cargo management methods."""

    def test_get_fleet_cargo_capacity(self, resource_aggregator, mock_fleet, mock_ship):
        """Fleet cargo capacity summed from ships."""
        mock_ship.get_cargo_capacity.return_value = 100
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.get_fleet_cargo_capacity("passengers")

        assert result == 100

    def test_get_fleet_cargo_capacity_multiple_ships(self, resource_aggregator, mock_fleet):
        """Multiple ship cargo capacities are summed."""
        ship1 = MagicMock()
        ship1.get_cargo_capacity.return_value = 100

        ship2 = MagicMock()
        ship2.get_cargo_capacity.return_value = 50

        mock_fleet.get_combat_capable_ships.return_value = [ship1, ship2]

        result = resource_aggregator.get_fleet_cargo_capacity("passengers")

        assert result == 150

    def test_get_fleet_cargo_current(self, resource_aggregator, mock_fleet, mock_ship):
        """Fleet current cargo summed from all ships."""
        mock_ship.get_current_cargo.return_value = 50
        mock_fleet.ships = [mock_ship]

        result = resource_aggregator.get_fleet_cargo_current("passengers")

        assert result == 50

    def test_load_cargo_distributes_to_ships(self, resource_aggregator, mock_fleet, mock_ship):
        """Cargo is distributed to ships with capacity."""
        mock_ship.load_cargo.return_value = 75  # Loaded 75 of 100
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.load_cargo_to_fleet("passengers", 100)

        assert result == 75
        mock_ship.load_cargo.assert_called_with("passengers", 100)

    def test_load_cargo_zero_amount_returns_zero(self, resource_aggregator, mock_fleet, mock_ship):
        """Loading 0 cargo returns 0."""
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.load_cargo_to_fleet("passengers", 0)

        assert result == 0
        mock_ship.load_cargo.assert_not_called()

    def test_load_cargo_negative_amount_returns_zero(self, resource_aggregator, mock_fleet, mock_ship):
        """Loading negative cargo returns 0."""
        mock_fleet.get_combat_capable_ships.return_value = [mock_ship]

        result = resource_aggregator.load_cargo_to_fleet("passengers", -50)

        assert result == 0

    def test_unload_cargo_from_fleet(self, resource_aggregator, mock_fleet, mock_ship):
        """Cargo is unloaded from ships."""
        mock_ship.unload_cargo.return_value = 50
        mock_fleet.ships = [mock_ship]

        result = resource_aggregator.unload_cargo_from_fleet("passengers", 100)

        assert result == 50
        mock_ship.unload_cargo.assert_called_with("passengers", 100)

    def test_unload_cargo_zero_amount_returns_zero(self, resource_aggregator, mock_fleet, mock_ship):
        """Unloading 0 cargo returns 0."""
        mock_fleet.ships = [mock_ship]

        result = resource_aggregator.unload_cargo_from_fleet("passengers", 0)

        assert result == 0
        mock_ship.unload_cargo.assert_not_called()
