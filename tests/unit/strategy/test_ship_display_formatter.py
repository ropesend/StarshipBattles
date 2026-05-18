"""Tests for ShipDisplayFormatter - extracted display methods from ShipInstance."""
import pytest
from unittest.mock import Mock


class TestShipDisplayFormatter:
    """Tests for ShipDisplayFormatter class."""

    @pytest.fixture
    def mock_ship_instance(self):
        """Create a mock ShipInstance for testing.

        PROJ-95: consumable_levels always contains actual values.
        PROJ-436 Phase 3c: ShipDisplayFormatter now reads via
        ``ship._resource_mgr.get_current_resource(...)``; the fixture
        wires a real ``ShipConsumableManager`` around the mock ship so
        the dict-vs-Container substrate stays hidden behind the
        stable manager API.
        """
        from game.strategy.data.ship_consumable_manager import (
            ShipConsumableManager,
        )
        ship = Mock()
        ship.design_data = {'name': 'TestShip'}
        ship.design_id = 'test_ship'
        ship.serial = 42
        ship.is_alive = True
        ship.is_derelict = False
        ship.current_hp = None
        # Resources always stored with actual values
        ship.consumable_levels = {
            'fuel': 500,
            'energy': 200,
            'ammo': 100,
        }
        ship.components = {}
        ship.get_calculated_stats = Mock(return_value={
            'max_hp': 100,
            'resource_storage': {
                'fuel': 500,
                'energy': 200,
                'ammo': 100,
            }
        })
        # Mock is_damaged method
        ship.is_damaged = Mock(return_value=False)
        ship._resource_mgr = ShipConsumableManager(ship)
        return ship

    def test_get_display_id_with_serial(self, mock_ship_instance):
        """Test get_display_id returns formatted ID with serial."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_display_id() == "TestShip-000042"

    def test_get_display_id_without_serial(self, mock_ship_instance):
        """Test get_display_id returns None when no serial."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.serial = None
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_display_id() is None

    def test_get_display_id_uses_design_name(self, mock_ship_instance):
        """Test get_display_id uses design name from design_data."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.design_data = {'name': 'USS Enterprise'}
        mock_ship_instance.serial = 1701
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_display_id() == "USS Enterprise-001701"

    def test_get_status_text_ok(self, mock_ship_instance):
        """Test get_status_text returns OK for healthy ship."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_status_text() == "OK"

    def test_get_status_text_destroyed(self, mock_ship_instance):
        """Test get_status_text returns DESTROYED."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.is_alive = False
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_status_text() == "DESTROYED"

    def test_get_status_text_derelict(self, mock_ship_instance):
        """Test get_status_text returns DERELICT."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.is_derelict = True
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_status_text() == "DERELICT"

    def test_get_status_text_damaged(self, mock_ship_instance):
        """Test get_status_text returns DAMAGED."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.is_damaged = Mock(return_value=True)
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_status_text() == "DAMAGED"

    def test_get_hp_display_full_health(self, mock_ship_instance):
        """Test get_hp_display with full health."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_hp_display() == "100/100"

    def test_get_hp_display_damaged(self, mock_ship_instance):
        """Test get_hp_display with damage."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.current_hp = 75
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_hp_display() == "75/100"

    def test_get_resource_display_full(self, mock_ship_instance):
        """Test get_resource_display with full resources."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_resource_display('fuel') == "500/500"
        assert formatter.get_resource_display('energy') == "200/200"

    def test_get_resource_display_partial(self, mock_ship_instance):
        """Test get_resource_display with partial resources."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.consumable_levels = {'fuel': 250}
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_resource_display('fuel') == "250/500"

    def test_get_resource_display_not_available(self, mock_ship_instance):
        """Test get_resource_display for unavailable resource."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.get_calculated_stats = Mock(return_value={
            'max_hp': 100,
            'resource_storage': {}
        })
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_resource_display('fuel') == "N/A"

    def test_get_resource_percentage_full(self, mock_ship_instance):
        """Test get_resource_percentage with full resources."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_resource_percentage('fuel') == 1.0

    def test_get_resource_percentage_partial(self, mock_ship_instance):
        """Test get_resource_percentage with partial resources."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.consumable_levels = {'fuel': 250}
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_resource_percentage('fuel') == 0.5

    def test_get_resource_percentage_empty(self, mock_ship_instance):
        """Test get_resource_percentage with empty resources."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.consumable_levels = {'fuel': 0}
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_resource_percentage('fuel') == 0.0

    def test_get_resource_percentage_zero_max(self, mock_ship_instance):
        """Test get_resource_percentage with zero max capacity."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.consumable_levels = {'fuel': 100}
        mock_ship_instance.get_calculated_stats = Mock(return_value={
            'max_hp': 100,
            'resource_storage': {'fuel': 0}
        })
        formatter = ShipDisplayFormatter(mock_ship_instance)

        # With key in resource_storage but value 0, should return 0
        assert formatter.get_resource_percentage('fuel') == 0.0

    def test_get_resource_percentage_negative_max(self, mock_ship_instance):
        """Test get_resource_percentage with negative max capacity returns 0."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.consumable_levels = {'fuel': 100}
        mock_ship_instance.get_calculated_stats = Mock(return_value={
            'max_hp': 100,
            'resource_storage': {'fuel': -10}
        })
        formatter = ShipDisplayFormatter(mock_ship_instance)

        # Negative max should return 0 (guards against division by negative)
        assert formatter.get_resource_percentage('fuel') == 0.0

    def test_get_resource_percentage_nonexistent_resource(self, mock_ship_instance):
        """Test get_resource_percentage for resource not in consumable_levels."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.consumable_levels = {}  # Empty
        formatter = ShipDisplayFormatter(mock_ship_instance)

        # Resource not tracked returns 0.0
        assert formatter.get_resource_percentage('nonexistent') == 0.0

    def test_get_resource_display_negative_max(self, mock_ship_instance):
        """Test get_resource_display with negative max returns N/A."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.get_calculated_stats = Mock(return_value={
            'max_hp': 100,
            'resource_storage': {'fuel': -10}
        })
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_resource_display('fuel') == "N/A"

    def test_get_resource_display_zero_max(self, mock_ship_instance):
        """Test get_resource_display with zero max returns N/A."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.get_calculated_stats = Mock(return_value={
            'max_hp': 100,
            'resource_storage': {'fuel': 0}
        })
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_resource_display('fuel') == "N/A"

    def test_get_hp_display_zero_max_hp(self, mock_ship_instance):
        """Test get_hp_display with zero max HP."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.current_hp = 0
        mock_ship_instance.get_calculated_stats = Mock(return_value={
            'max_hp': 0,
            'resource_storage': {}
        })
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_hp_display() == "0/0"

    def test_get_display_id_fallback_to_design_id(self, mock_ship_instance):
        """Test get_display_id uses design_id when name not in design_data."""
        from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
        mock_ship_instance.design_data = {}  # No 'name' key
        mock_ship_instance.design_id = 'fallback_design'
        mock_ship_instance.serial = 123
        formatter = ShipDisplayFormatter(mock_ship_instance)

        assert formatter.get_display_id() == "fallback_design-000123"
