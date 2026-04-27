"""Tests for fleet build button visibility in strategy UI (PROJ-67 Phase 5)."""
import pytest
from unittest.mock import MagicMock, patch

from game.ui.screens.strategy_ui import StrategyUI
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.empire import Empire
from game.strategy.data.ship_instance import ShipInstance


def make_mock_ship_instance(name="Test Ship", owner_id=0, has_yard=False, registries=None):
    """Create a mock ShipInstance for testing.

    PROJ-211: Accepts optional registries for DI compliance. Required for tests
    that call get_calculated_stats() (triggered by show_detailed_report).
    """
    design_data = {
        'name': name,
        'vehicle_type': 'Ship',
        'stats': {'mass': 100}
    }

    ship = ShipInstance(
        instance_id=f"test-{name.lower().replace(' ', '-')}",
        design_id=name,
        name=name,
        owner_id=owner_id,
        design_data=design_data,
    )

    # PROJ-211: Set registries for DI compliance
    if registries is not None:
        ship.set_registries(registries)

    # Mock has_space_shipyard ability if requested
    if has_yard:
        # The has_space_shipyard check uses get_all_abilities()
        # We need to mock this to return a SpaceShipyard ability
        ship.get_all_abilities = MagicMock(return_value=[
            MagicMock(ability_type='SpaceShipyard')
        ])

    return ship


class MockScene:
    def __init__(self):
        self.camera = MagicMock()
        self.camera.zoom = 1.0
        self.current_empire = Empire(1, "Test Empire", (255, 0, 0))
        self.galaxy = MagicMock()
        # PROJ-198: turn_engine is accessed via session
        self.session = MagicMock()
        self.session.turn_engine = MagicMock()
        self.session.turn_engine.validate_colonize_order.return_value = MagicMock(is_valid=True)


@pytest.fixture
def strategy_ui(ui_manager):
    scene = MockScene()
    ui = StrategyUI(scene, 800, 600)
    return ui


def test_build_button_visible_for_owned_fleet_with_shipyard(strategy_ui, fresh_registries):
    """Test that build button is visible for owned fleet with space shipyard."""
    # Setup fleet with yard ship
    fleet = Fleet(1, strategy_ui.scene.current_empire.id, (0, 0))
    yard_ship = make_mock_ship_instance("Yard Ship", strategy_ui.scene.current_empire.id, has_yard=True, registries=fresh_registries)
    fleet.ships = [yard_ship]

    # PROJ-210: Mock capabilities.has_space_shipyard (now accessed via property)
    fleet._capabilities = MagicMock()
    fleet._capabilities.has_space_shipyard = True

    # Act
    strategy_ui.show_detailed_report(fleet)

    # Assert
    assert strategy_ui.btn_build_fleet.visible == 1, "Build button should be visible for owned fleet with shipyard"


def test_build_button_hidden_for_owned_fleet_without_shipyard(strategy_ui, fresh_registries):
    """Test that build button is hidden for owned fleet without space shipyard."""
    # Setup fleet without yard ship
    fleet = Fleet(1, strategy_ui.scene.current_empire.id, (0, 0))
    ship = make_mock_ship_instance("Regular Ship", strategy_ui.scene.current_empire.id, has_yard=False, registries=fresh_registries)
    fleet.ships = [ship]

    # PROJ-210: Mock capabilities.has_space_shipyard (now accessed via property)
    fleet._capabilities = MagicMock()
    fleet._capabilities.has_space_shipyard = False

    # Act
    strategy_ui.show_detailed_report(fleet)

    # Assert
    assert strategy_ui.btn_build_fleet.visible == 0, "Build button should be hidden for fleet without shipyard"


def test_build_button_hidden_for_enemy_fleet_with_shipyard(strategy_ui, fresh_registries):
    """Test that build button is hidden for enemy fleet even with space shipyard."""
    # Setup enemy fleet with yard
    fleet = Fleet(2, 999, (0, 0))  # Enemy owner_id
    yard_ship = make_mock_ship_instance("Enemy Yard Ship", 999, has_yard=True, registries=fresh_registries)
    fleet.ships = [yard_ship]

    # PROJ-210: Mock capabilities.has_space_shipyard (now accessed via property)
    fleet._capabilities = MagicMock()
    fleet._capabilities.has_space_shipyard = True

    # Act
    strategy_ui.show_detailed_report(fleet)

    # Assert
    assert strategy_ui.btn_build_fleet.visible == 0, "Build button should be hidden for enemy fleet"


class TestBuildOrderDisplay:
    """Tests for BUILD order display in fleet info."""

    def test_build_order_shows_in_fleet_detail(self, strategy_ui, fresh_registries):
        """Test that BUILD order shows in fleet detail text."""
        # Setup fleet with BUILD order
        fleet = Fleet(1, strategy_ui.scene.current_empire.id, (0, 0))
        ship = make_mock_ship_instance("Ship", strategy_ui.scene.current_empire.id, registries=fresh_registries)
        fleet.ships = [ship]
        fleet.orders = [Order(OrderType.BUILD)]
        fleet.construction_queue = [{'design_id': 'scout', 'turns_remaining': 3}]

        # Act
        strategy_ui.show_detailed_report(fleet)

        # Assert - check that detail text contains BUILD info
        text = strategy_ui.detail_text.html_text
        assert "BUILDING" in text, "BUILD order should appear in detail text"
        assert "1 items" in text, "Queue size should appear in BUILD description"


class TestMoveBlockingWhileBuilding:
    """Tests for blocking move commands while fleet is building."""

    def test_move_blocked_when_building(self):
        """Test that move command is rejected for building fleet."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations
        from game.core.hex_math import HexCoord

        # Setup
        mock_scene = MagicMock()
        mock_scene.camera.screen_to_world.return_value = MagicMock(x=100, y=100)
        mock_scene.empires = []
        mock_scene.hex_size = 10

        mock_facade = MagicMock()

        fleet_ops = FleetOperations(mock_scene, mock_facade)

        # Create building fleet
        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.orders = [Order(OrderType.BUILD)]

        # Act
        result = fleet_ops.handle_move_designation(100, 100, fleet)

        # Assert
        assert result is not None
        assert result['type'] == 'error'
        assert 'building' in result['message'].lower()

    def test_move_allowed_when_not_building(self):
        """Test that move command is allowed for non-building fleet."""
        from game.ui.screens.strategy_fleet_ops import FleetOperations
        from game.core.hex_math import HexCoord

        # Setup
        mock_scene = MagicMock()
        mock_scene.camera.screen_to_world.return_value = MagicMock(x=100, y=100)
        mock_scene.empires = []
        mock_scene.hex_size = 10

        mock_facade = MagicMock()
        mock_facade.get_fleet_path_preview.return_value = [HexCoord(0, 0), HexCoord(1, 0)]
        mock_facade.handle_command.return_value = MagicMock(is_valid=True)
        # PROJ-208: get_fleet_at_hex now uses facade.get_fleets_at_hex
        mock_facade.get_fleets_at_hex.return_value = []  # No fleet at target

        fleet_ops = FleetOperations(mock_scene, mock_facade)

        # Create non-building fleet
        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.orders = []  # No BUILD order

        # Act
        result = fleet_ops.handle_move_designation(100, 100, fleet)

        # Assert - should proceed with move (not blocked)
        assert result is not None
        assert result['type'] == 'success'


class TestFleetOrdersWindowBuildDisplay:
    """Tests for BUILD order display in OrdersWindow."""

    def test_build_order_description(self, ui_manager):
        """Test that BUILD order shows correct description."""
        from game.ui.screens.orders_window import OrdersWindow
        from game.core.hex_math import HexCoord
        import pygame

        # Create fleet with BUILD order and queue items
        fleet = Fleet(1, 0, HexCoord(0, 0))
        fleet.orders = [Order(OrderType.BUILD)]
        fleet.construction_queue = [
            {'design_id': 'scout', 'turns_remaining': 3},
            {'design_id': 'frigate', 'turns_remaining': 5}
        ]

        rect = pygame.Rect(100, 100, 400, 300)

        # Create window
        window = OrdersWindow(rect, ui_manager, fleet)

        # Get order description
        desc = window._get_order_description(fleet.orders[0])

        # Assert
        assert "BUILDING" in desc
        assert "2 items" in desc

        window.kill()
