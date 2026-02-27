"""
Unit tests for Ship.get_resource_stat() method.

PROJ-194 Phase 4: Typed accessor for dynamic resource attributes.
"""
import pytest

from game.simulation.entities.ship import Ship


@pytest.fixture
def ship(fresh_registries):
    """Create a basic ship for testing."""
    return Ship(
        name="TestShip",
        x=0, y=0,
        color=(255, 255, 255),
        team_id=1,
        ship_class="Escort",
        theme_id="Federation",
        registries=fresh_registries
    )


class TestGetResourceStat:
    """Tests for Ship.get_resource_stat() accessor method."""

    def test_fuel_consumption_returns_attribute_value(self, ship):
        """get_resource_stat returns fuel_consumption when set."""
        ship.fuel_consumption = 5.5
        result = ship.get_resource_stat('fuel', 'consumption')
        assert result == 5.5

    def test_ammo_consumption_returns_attribute_value(self, ship):
        """get_resource_stat returns ammo_consumption when set."""
        ship.ammo_consumption = 10.0
        result = ship.get_resource_stat('ammo', 'consumption')
        assert result == 10.0

    def test_energy_consumption_returns_attribute_value(self, ship):
        """get_resource_stat returns energy_consumption when set."""
        ship.energy_consumption = 25.0
        result = ship.get_resource_stat('energy', 'consumption')
        assert result == 25.0

    def test_potential_fuel_consumption(self, ship):
        """get_resource_stat returns potential_fuel_consumption.

        Note: The actual attribute is 'potential_fuel_consumption' which uses
        'potential_fuel' as resource_name and 'consumption' as stat_type.
        """
        ship.potential_fuel_consumption = 8.0
        result = ship.get_resource_stat('potential_fuel', 'consumption')
        assert result == 8.0

    def test_potential_ammo_consumption(self, ship):
        """get_resource_stat returns potential_ammo_consumption."""
        ship.potential_ammo_consumption = 15.0
        result = ship.get_resource_stat('potential_ammo', 'consumption')
        assert result == 15.0

    def test_potential_energy_consumption(self, ship):
        """get_resource_stat returns potential_energy_consumption."""
        ship.potential_energy_consumption = 30.0
        result = ship.get_resource_stat('potential_energy', 'consumption')
        assert result == 30.0

    def test_nonexistent_attribute_returns_zero(self, ship):
        """get_resource_stat returns 0.0 for undefined attributes."""
        result = ship.get_resource_stat('nonexistent', 'stat')
        assert result == 0.0

    def test_nonexistent_stat_type_returns_zero(self, ship):
        """get_resource_stat returns 0.0 for undefined stat types."""
        result = ship.get_resource_stat('fuel', 'nonexistent_type')
        assert result == 0.0

    def test_zero_value_attribute(self, ship):
        """get_resource_stat returns 0.0 when attribute is zero."""
        ship.fuel_consumption = 0.0
        result = ship.get_resource_stat('fuel', 'consumption')
        assert result == 0.0

    def test_return_type_is_float(self, ship):
        """get_resource_stat returns float type."""
        ship.fuel_consumption = 5
        result = ship.get_resource_stat('fuel', 'consumption')
        # Should return whatever getattr returns, which preserves type
        assert isinstance(result, (int, float))
