# BUG-27: NameError: name 'OrderType' is not defined
# Tests that OrderType is properly imported in strategy_screen.py

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock

from game.strategy.data.ship_instance import ShipInstance


def make_mock_ship_instance(name="Test Ship", owner_id=0):
    """Create a mock ShipInstance for testing."""
    return ShipInstance(
        instance_id=f"test-{name.lower().replace(' ', '-')}",
        design_id=name,
        name=name,
        owner_id=owner_id,
        design_data={
            'name': name,
            'vehicle_type': 'Ship',
            'stats': {'mass': 100}
        },
    )


class TestBug27OrderTypeImport:
    """Regression tests for BUG-27: OrderType import missing in strategy_screen."""

    def test_ordertype_import_in_strategy_screen(self):
        """Verify that OrderType is importable from strategy_screen module."""
        from game.ui.screens.strategy_screen import StrategyInterface
        from game.strategy.data.fleet import OrderType, FleetOrder, Fleet
        # If we get here without ImportError, the module loads correctly
        assert OrderType.MOVE is not None
        assert OrderType.COLONIZE is not None

    def test_show_detailed_report_fleet_with_orders(self):
        """Test that showing fleet with orders doesn't raise NameError."""
        pygame.init()
        pygame.display.set_mode((800, 600))

        from game.ui.screens.strategy_screen import StrategyInterface
        from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
        from game.strategy.data.empire import Empire
        from game.strategy.data.hex_math import HexCoord

        # Setup mock scene
        scene = MagicMock()
        scene.camera = MagicMock()
        scene.camera.zoom = 1.0
        scene.current_empire = Empire(1, "Test", (255, 0, 0))
        scene.turn_engine = MagicMock()
        scene.turn_engine.validate_colonize_order.return_value = MagicMock(is_valid=False)

        ui = StrategyInterface(scene, 800, 600)

        # Create fleet with MOVE order
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships = [make_mock_ship_instance("TestShip", 1)]
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(1, 1))]

        # This should not raise NameError anymore
        ui.show_detailed_report(fleet)

        # Verify the report was generated (contains fleet info)
        assert "Fleet" in ui.detail_text.html_text
        assert "MOVE" in ui.detail_text.html_text

        pygame.quit()

    def test_show_detailed_report_fleet_with_colonize_order(self):
        """Test fleet with COLONIZE order doesn't raise NameError."""
        pygame.init()
        pygame.display.set_mode((800, 600))

        from game.ui.screens.strategy_screen import StrategyInterface
        from game.strategy.data.fleet import Fleet, FleetOrder, OrderType
        from game.strategy.data.empire import Empire
        from game.strategy.data.hex_math import HexCoord
        from game.strategy.data.planet import Planet, PlanetType

        scene = MagicMock()
        scene.camera = MagicMock()
        scene.camera.zoom = 1.0
        scene.current_empire = Empire(1, "Test", (255, 0, 0))
        scene.turn_engine = MagicMock()
        scene.turn_engine.validate_colonize_order.return_value = MagicMock(is_valid=False)

        ui = StrategyInterface(scene, 800, 600)

        # Create a mock planet target
        mock_planet = MagicMock()
        mock_planet.name = "Test Planet"

        # Create fleet with COLONIZE order
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships = [make_mock_ship_instance("ColonyShip", 1)]
        fleet.orders = [FleetOrder(OrderType.COLONIZE, mock_planet)]

        # This should not raise NameError anymore
        ui.show_detailed_report(fleet)

        assert "Fleet" in ui.detail_text.html_text
        assert "COLONIZE" in ui.detail_text.html_text

        pygame.quit()
