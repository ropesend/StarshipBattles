"""Tests for ShipCargoManager - extracted cargo operations from ShipInstance."""
import pytest
from unittest.mock import Mock, MagicMock


class TestShipCargoManager:
    """Tests for ShipCargoManager class."""

    @pytest.fixture
    def mock_ship_instance(self):
        """Create a mock ShipInstance for testing."""
        ship = Mock()
        ship.cargo_contents = {}
        ship.get_calculated_stats = Mock(return_value={
            'cargo_storage': {
                'passengers': 100,
                'generic': 500,
            }
        })
        return ship

    def test_get_cargo_capacity_returns_capacity_for_type(self, mock_ship_instance):
        """Test get_cargo_capacity returns correct capacity."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        manager = ShipCargoManager(mock_ship_instance)

        assert manager.get_cargo_capacity('passengers') == 100
        assert manager.get_cargo_capacity('generic') == 500

    def test_get_cargo_capacity_returns_zero_for_unknown_type(self, mock_ship_instance):
        """Test get_cargo_capacity returns 0 for unknown cargo type."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        manager = ShipCargoManager(mock_ship_instance)

        assert manager.get_cargo_capacity('unknown') == 0

    def test_get_current_cargo_returns_zero_when_empty(self, mock_ship_instance):
        """Test get_current_cargo returns 0 when no cargo loaded."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        manager = ShipCargoManager(mock_ship_instance)

        assert manager.get_current_cargo('passengers') == 0

    def test_get_current_cargo_returns_loaded_amount(self, mock_ship_instance):
        """Test get_current_cargo returns correct loaded amount."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        mock_ship_instance.cargo_contents = {'passengers': 50}
        manager = ShipCargoManager(mock_ship_instance)

        assert manager.get_current_cargo('passengers') == 50

    def test_get_cargo_space_available_full_capacity(self, mock_ship_instance):
        """Test get_cargo_space_available with empty cargo."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        manager = ShipCargoManager(mock_ship_instance)

        assert manager.get_cargo_space_available('passengers') == 100

    def test_get_cargo_space_available_partial(self, mock_ship_instance):
        """Test get_cargo_space_available with partial load."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        mock_ship_instance.cargo_contents = {'passengers': 30}
        manager = ShipCargoManager(mock_ship_instance)

        assert manager.get_cargo_space_available('passengers') == 70

    def test_load_cargo_full_amount(self, mock_ship_instance):
        """Test loading cargo within capacity."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        manager = ShipCargoManager(mock_ship_instance)

        loaded = manager.load_cargo('passengers', 50)

        assert loaded == 50
        assert mock_ship_instance.cargo_contents['passengers'] == 50

    def test_load_cargo_capped_at_capacity(self, mock_ship_instance):
        """Test loading cargo capped at available space."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        manager = ShipCargoManager(mock_ship_instance)

        loaded = manager.load_cargo('passengers', 150)

        assert loaded == 100  # Capped at capacity
        assert mock_ship_instance.cargo_contents['passengers'] == 100

    def test_load_cargo_zero_or_negative(self, mock_ship_instance):
        """Test loading zero or negative cargo returns 0."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        manager = ShipCargoManager(mock_ship_instance)

        assert manager.load_cargo('passengers', 0) == 0
        assert manager.load_cargo('passengers', -10) == 0
        assert 'passengers' not in mock_ship_instance.cargo_contents

    def test_load_cargo_adds_to_existing(self, mock_ship_instance):
        """Test loading cargo adds to existing amount."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        mock_ship_instance.cargo_contents = {'passengers': 40}
        manager = ShipCargoManager(mock_ship_instance)

        loaded = manager.load_cargo('passengers', 30)

        assert loaded == 30
        assert mock_ship_instance.cargo_contents['passengers'] == 70

    def test_unload_cargo_full_amount(self, mock_ship_instance):
        """Test unloading cargo within available amount."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        mock_ship_instance.cargo_contents = {'passengers': 50}
        manager = ShipCargoManager(mock_ship_instance)

        unloaded = manager.unload_cargo('passengers', 30)

        assert unloaded == 30
        assert mock_ship_instance.cargo_contents['passengers'] == 20

    def test_unload_cargo_capped_at_available(self, mock_ship_instance):
        """Test unloading cargo capped at current amount."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        mock_ship_instance.cargo_contents = {'passengers': 30}
        manager = ShipCargoManager(mock_ship_instance)

        unloaded = manager.unload_cargo('passengers', 50)

        assert unloaded == 30
        assert 'passengers' not in mock_ship_instance.cargo_contents  # Removed when zero

    def test_unload_cargo_zero_or_negative(self, mock_ship_instance):
        """Test unloading zero or negative cargo returns 0."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        mock_ship_instance.cargo_contents = {'passengers': 50}
        manager = ShipCargoManager(mock_ship_instance)

        assert manager.unload_cargo('passengers', 0) == 0
        assert manager.unload_cargo('passengers', -10) == 0
        assert mock_ship_instance.cargo_contents['passengers'] == 50

    def test_unload_cargo_removes_zero_entries(self, mock_ship_instance):
        """Test unloading all cargo removes the dict entry."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        mock_ship_instance.cargo_contents = {'passengers': 50}
        manager = ShipCargoManager(mock_ship_instance)

        manager.unload_cargo('passengers', 50)

        assert 'passengers' not in mock_ship_instance.cargo_contents

    def test_unload_cargo_nonexistent_type(self, mock_ship_instance):
        """Test unloading cargo type that doesn't exist."""
        from game.strategy.data.ship_cargo_manager import ShipCargoManager
        manager = ShipCargoManager(mock_ship_instance)

        unloaded = manager.unload_cargo('passengers', 10)

        assert unloaded == 0
