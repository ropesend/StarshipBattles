"""Tests for ShipResourceManager - extracted resource management from ShipInstance."""
import pytest
from unittest.mock import Mock, MagicMock


class TestShipResourceManager:
    """Test suite for ShipResourceManager."""

    @pytest.fixture
    def mock_ship_instance(self):
        """Create a mock ShipInstance with required attributes."""
        ship = Mock()
        ship.resource_levels = {}
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

    # --- Fuel Tests ---

    def test_get_current_fuel_full(self, resource_manager, mock_ship_instance):
        """When fuel not in resource_levels, returns max fuel."""
        result = resource_manager.get_current_fuel()
        assert result == 1000

    def test_get_current_fuel_partial(self, resource_manager, mock_ship_instance):
        """When fuel is tracked, returns tracked value."""
        mock_ship_instance.resource_levels['fuel'] = 750
        result = resource_manager.get_current_fuel()
        assert result == 750

    def test_consume_fuel_success(self, resource_manager, mock_ship_instance):
        """Consuming fuel when sufficient."""
        mock_ship_instance.resource_levels['fuel'] = 500
        result = resource_manager.consume_fuel(100)
        assert result is True
        assert mock_ship_instance.resource_levels['fuel'] == 400

    def test_consume_fuel_insufficient(self, resource_manager, mock_ship_instance):
        """Consuming fuel when insufficient returns False."""
        mock_ship_instance.resource_levels['fuel'] = 50
        result = resource_manager.consume_fuel(100)
        assert result is False
        assert mock_ship_instance.resource_levels['fuel'] == 50  # Unchanged

    def test_consume_fuel_from_full(self, resource_manager, mock_ship_instance):
        """Consuming fuel when at full (not in resource_levels)."""
        result = resource_manager.consume_fuel(100)
        assert result is True
        assert mock_ship_instance.resource_levels['fuel'] == 900

    def test_get_fuel_cost_per_hex(self, resource_manager):
        """Get fuel cost per hex from stats."""
        result = resource_manager.get_fuel_cost_per_hex()
        assert result == 10

    def test_get_warp_fuel_cost(self, resource_manager):
        """Get warp fuel cost from stats."""
        result = resource_manager.get_warp_fuel_cost()
        assert result == 50

    # --- Energy Tests ---

    def test_get_current_energy_full(self, resource_manager):
        """When energy not in resource_levels, returns max energy."""
        result = resource_manager.get_current_energy()
        assert result == 500

    def test_get_current_energy_partial(self, resource_manager, mock_ship_instance):
        """When energy is tracked, returns tracked value."""
        mock_ship_instance.resource_levels['energy'] = 250
        result = resource_manager.get_current_energy()
        assert result == 250

    def test_consume_energy_success(self, resource_manager, mock_ship_instance):
        """Consuming energy when sufficient."""
        mock_ship_instance.resource_levels['energy'] = 300
        result = resource_manager.consume_energy(100)
        assert result is True
        assert mock_ship_instance.resource_levels['energy'] == 200

    def test_consume_energy_insufficient(self, resource_manager, mock_ship_instance):
        """Consuming energy when insufficient returns False."""
        mock_ship_instance.resource_levels['energy'] = 25
        result = resource_manager.consume_energy(50)
        assert result is False
        assert mock_ship_instance.resource_levels['energy'] == 25  # Unchanged

    def test_get_warp_energy_cost(self, resource_manager):
        """Get warp energy cost from stats."""
        result = resource_manager.get_warp_energy_cost()
        assert result == 25

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

    def test_get_current_resource_full(self, resource_manager):
        """Get current resource when full returns max."""
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
        """Resupply to full removes from tracking."""
        mock_ship_instance.get_calculated_stats.return_value['max_fuel'] = 1000
        mock_ship_instance.resource_levels['fuel'] = 800

        result = resource_manager.resupply('fuel', 300)
        assert result == 200  # Capped at max
        assert 'fuel' not in mock_ship_instance.resource_levels

    def test_resupply_already_full(self, resource_manager, mock_ship_instance):
        """Resupply when already full returns 0."""
        # fuel not in resource_levels means it's full
        result = resource_manager.resupply('fuel', 100)
        assert result == 0


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
        """ShipInstance methods delegate to resource manager."""
        # Access through ShipInstance facade
        ship = ship_with_resources

        # These should work via delegation
        fuel = ship.get_current_fuel()
        assert isinstance(fuel, (int, float))

        fuel_cost = ship.get_fuel_cost_per_hex()
        assert isinstance(fuel_cost, (int, float))
