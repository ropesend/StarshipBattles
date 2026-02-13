"""Tests for ShipResourceManager - extracted resource management from ShipInstance."""
import pytest
from unittest.mock import Mock, MagicMock


class TestShipResourceManager:
    """Test suite for ShipResourceManager."""

    @pytest.fixture
    def mock_ship_instance(self):
        """Create a mock ShipInstance with required attributes.

        PROJ-95: resource_levels always contains actual values (no None-means-full).
        """
        ship = Mock()
        # Resources always stored with actual values
        ship.resource_levels = {
            'fuel': 1000,
            'energy': 500,
            'ammo': 100,
        }
        ship.get_calculated_stats = Mock(return_value={
            'resource_storage': {
                'fuel': 1000,
                'energy': 500,
                'ammo': 100,
            },
            'resource_consumption_per_hex': {
                'fuel': 10,
            },
            'resource_consumption_per_turn': {
                'energy': 5,
            },
            'warp_resource_costs': {
                'fuel': 50,
                'energy': 25,
            },
        })
        return ship

    @pytest.fixture
    def resource_manager(self, mock_ship_instance):
        """Create a ShipResourceManager with a mock ship."""
        from game.strategy.data.ship_resource_manager import ShipResourceManager
        return ShipResourceManager(mock_ship_instance)

    # --- Generic Resource Tests ---

    def test_get_resource_capacity(self, resource_manager):
        """Get capacity for any resource type."""
        assert resource_manager.get_resource_capacity('fuel') == 1000
        assert resource_manager.get_resource_capacity('energy') == 500
        assert resource_manager.get_resource_capacity('ammo') == 100

    def test_get_resource_capacity_nonexistent(self, resource_manager):
        """Get capacity for nonexistent resource returns 0."""
        assert resource_manager.get_resource_capacity('nonexistent') == 0

    def test_get_current_resource(self, resource_manager, mock_ship_instance):
        """Get current level of any resource."""
        mock_ship_instance.resource_levels['ammo'] = 75
        assert resource_manager.get_current_resource('ammo') == 75

    def test_get_current_resource_full(self, resource_manager, mock_ship_instance):
        """Get current resource when full returns stored value.

        PROJ-95: Resources are always stored with actual values.
        """
        # ammo is already 100 (full) in mock_ship_instance.resource_levels
        assert resource_manager.get_current_resource('ammo') == 100

    def test_consume_resource_success(self, resource_manager, mock_ship_instance):
        """Consume any resource type."""
        mock_ship_instance.resource_levels['ammo'] = 80
        result = resource_manager.consume_resource('ammo', 30)
        assert result is True
        assert mock_ship_instance.resource_levels['ammo'] == 50

    def test_consume_resource_insufficient(self, resource_manager, mock_ship_instance):
        """Consume resource when insufficient."""
        mock_ship_instance.resource_levels['ammo'] = 20
        result = resource_manager.consume_resource('ammo', 50)
        assert result is False
        assert mock_ship_instance.resource_levels['ammo'] == 20

    def test_consume_resource_negative_amount(self, resource_manager, mock_ship_instance):
        """Cannot consume negative amount."""
        mock_ship_instance.resource_levels['ammo'] = 50
        result = resource_manager.consume_resource('ammo', -10)
        assert result is False
        assert mock_ship_instance.resource_levels['ammo'] == 50

    def test_consume_resource_zero_amount(self, resource_manager, mock_ship_instance):
        """Consuming zero amount succeeds without changing resource."""
        mock_ship_instance.resource_levels['ammo'] = 50
        result = resource_manager.consume_resource('ammo', 0)
        assert result is True
        assert mock_ship_instance.resource_levels['ammo'] == 50

    def test_consume_resource_exact_amount(self, resource_manager, mock_ship_instance):
        """Consuming exact remaining amount succeeds."""
        mock_ship_instance.resource_levels['ammo'] = 30
        result = resource_manager.consume_resource('ammo', 30)
        assert result is True
        assert mock_ship_instance.resource_levels['ammo'] == 0

    def test_consume_resource_nonexistent_type(self, resource_manager, mock_ship_instance):
        """Consuming nonexistent resource type fails gracefully."""
        result = resource_manager.consume_resource('nonexistent', 10)
        assert result is False

    def test_get_current_resource_nonexistent(self, resource_manager, mock_ship_instance):
        """Get current resource for nonexistent type returns 0."""
        result = resource_manager.get_current_resource('nonexistent')
        assert result == 0.0

    # --- Cost Calculation Tests ---

    def test_get_all_resource_costs_per_hex(self, resource_manager):
        """Get all per-hex costs."""
        result = resource_manager.get_all_resource_costs_per_hex()
        assert result == {'fuel': 10}

    def test_get_all_resource_costs_per_turn(self, resource_manager):
        """Get all per-turn costs."""
        result = resource_manager.get_all_resource_costs_per_turn()
        assert result == {'energy': 5}

    def test_get_warp_resource_costs(self, resource_manager):
        """Get all warp costs."""
        result = resource_manager.get_warp_resource_costs()
        assert result == {'fuel': 50, 'energy': 25}

    # --- Resupply Tests ---

    def test_resupply_partial(self, resource_manager, mock_ship_instance):
        """Resupply resource partially."""
        # Need to set up max_fuel key in stats
        mock_ship_instance.get_calculated_stats.return_value['max_fuel'] = 1000
        mock_ship_instance.resource_levels['fuel'] = 500

        result = resource_manager.resupply('fuel', 200)
        assert result == 200
        assert mock_ship_instance.resource_levels['fuel'] == 700

    def test_resupply_to_full(self, resource_manager, mock_ship_instance):
        """Resupply to full keeps value stored at max.

        PROJ-95: Resources always stored (no sparse dict convention).
        """
        mock_ship_instance.get_calculated_stats.return_value['max_fuel'] = 1000
        mock_ship_instance.resource_levels['fuel'] = 800

        result = resource_manager.resupply('fuel', 300)
        assert result == 200  # Capped at max
        assert mock_ship_instance.resource_levels['fuel'] == 1000  # Full value stored

    def test_resupply_already_full(self, resource_manager, mock_ship_instance):
        """Resupply when already full returns 0.

        PROJ-95: Resources always stored, so check against stored max value.
        """
        # fuel is already at max (1000) in resource_levels
        result = resource_manager.resupply('fuel', 100)
        assert result == 0

    def test_resupply_negative_amount(self, resource_manager, mock_ship_instance):
        """Resupply with negative amount effectively removes resource."""
        mock_ship_instance.resource_levels['fuel'] = 500
        result = resource_manager.resupply('fuel', -100)
        # Negative amount reduces current level (400), but capped at 0 minimum
        assert result == -100
        assert mock_ship_instance.resource_levels['fuel'] == 400

    def test_resupply_zero_capacity(self, resource_manager, mock_ship_instance):
        """Resupply when max capacity is 0 returns 0."""
        # Set up a resource with 0 capacity
        mock_ship_instance.get_calculated_stats.return_value['resource_storage'] = {
            'special': 0,
        }
        mock_ship_instance.resource_levels['special'] = 0
        result = resource_manager.resupply('special', 100)
        assert result == 0
        assert mock_ship_instance.resource_levels['special'] == 0

    def test_resupply_nonexistent_resource(self, resource_manager, mock_ship_instance):
        """Resupply nonexistent resource returns 0 (no capacity)."""
        result = resource_manager.resupply('nonexistent', 100)
        assert result == 0

    # --- Cost Methods Empty Stats ---

    def test_get_all_resource_costs_per_hex_empty(self, mock_ship_instance):
        """Get per-hex costs when stats have empty dict."""
        from game.strategy.data.ship_resource_manager import ShipResourceManager
        mock_ship_instance.get_calculated_stats.return_value = {}
        manager = ShipResourceManager(mock_ship_instance)
        result = manager.get_all_resource_costs_per_hex()
        assert result == {}

    def test_get_all_resource_costs_per_turn_empty(self, mock_ship_instance):
        """Get per-turn costs when stats have empty dict."""
        from game.strategy.data.ship_resource_manager import ShipResourceManager
        mock_ship_instance.get_calculated_stats.return_value = {}
        manager = ShipResourceManager(mock_ship_instance)
        result = manager.get_all_resource_costs_per_turn()
        assert result == {}

    def test_get_warp_resource_costs_empty(self, mock_ship_instance):
        """Get warp costs when stats have empty dict."""
        from game.strategy.data.ship_resource_manager import ShipResourceManager
        mock_ship_instance.get_calculated_stats.return_value = {}
        manager = ShipResourceManager(mock_ship_instance)
        result = manager.get_warp_resource_costs()
        assert result == {}


class TestShipResourceManagerIntegration:
    """Integration tests with real ShipInstance."""

    @pytest.fixture
    def ship_with_resources(self):
        """Create a real ShipInstance with fuel/energy capacity."""
        from game.strategy.data.ship_instance import ShipInstance

        ship = ShipInstance(
            instance_id="test-001",
            design_id="test-frigate",
            name="Test Frigate",
            owner_id=1,
            design_data={
                'name': 'Test Frigate',
                'hull_type': 'frigate',
                'layers': {
                    'CORE': [
                        {'id': 'fuel_tank', 'type': 'fuel_tank'},
                        {'id': 'reactor', 'type': 'reactor'},
                    ]
                }
            },
        )
        return ship

    def test_delegation_to_resource_manager(self, ship_with_resources):
        """ShipInstance methods delegate to resource manager.

        PROJ-91: Uses generic resource API. Type-specific methods
        (get_current_fuel, get_fuel_cost_per_hex, etc.) were removed.
        """
        # Access through ShipInstance facade
        ship = ship_with_resources

        # These should work via delegation (generic API)
        fuel = ship.get_current_resource('fuel')
        assert isinstance(fuel, (int, float))

        fuel_cost = ship.get_all_resource_costs_per_hex().get('fuel', 0.0)
        assert isinstance(fuel_cost, (int, float))
