# BUG-27: NameError: name 'OrderType' is not defined
# Tests that OrderType is properly imported in strategy_screen.py

import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock

from game.strategy.data.ship_instance import ShipInstance


def make_mock_ship_instance(name="Test Ship", owner_id=0, registries=None):
    """Create a mock ShipInstance for testing.

    PROJ-211: Added registries parameter for DI compliance.
    """
    ship = ShipInstance(
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
    if registries is not None:
        ship._registries = registries
    return ship


class TestBug27OrderTypeImport:
    """Regression tests for BUG-27: OrderType import missing in strategy_screen."""

    def test_ordertype_import_in_strategy_ui(self):
        """Verify that OrderType is importable from strategy_ui module."""
        from game.ui.screens.strategy_ui import StrategyUI
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.order_types import OrderType, FleetOrder
        # If we get here without ImportError, the module loads correctly
        assert OrderType.MOVE is not None
        assert OrderType.COLONIZE is not None

    def test_show_detailed_report_fleet_with_orders(self, fresh_registries):
        """Test that showing fleet with orders doesn't raise NameError."""
        pygame.display.set_mode((800, 600))

        from game.ui.screens.strategy_ui import StrategyUI
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.order_types import FleetOrder, OrderType
        from game.strategy.data.empire import Empire
        from game.core.hex_math import HexCoord

        # Setup mock scene
        scene = MagicMock()
        scene.camera = MagicMock()
        scene.camera.zoom = 1.0
        scene.current_empire = Empire(1, "Test", (255, 0, 0))
        scene.turn_engine = MagicMock()
        scene.turn_engine.validate_colonize_order.return_value = MagicMock(is_valid=False)

        ui = StrategyUI(scene, 800, 600)

        # Create fleet with MOVE order
        # PROJ-211: Pass registries for DI compliance (ship assignment triggers speed calc)
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships = [make_mock_ship_instance("TestShip", 1, registries=fresh_registries)]
        fleet.orders = [FleetOrder(OrderType.MOVE, HexCoord(1, 1))]

        # This should not raise NameError anymore
        ui.show_detailed_report(fleet)

        # Verify the report was generated (contains fleet info)
        assert "Fleet" in ui.detail_text.html_text
        assert "MOVE" in ui.detail_text.html_text

    def test_show_detailed_report_fleet_with_colonize_order(self, fresh_registries):
        """Test fleet with COLONIZE order doesn't raise NameError."""
        pygame.display.set_mode((800, 600))

        from game.ui.screens.strategy_ui import StrategyUI
        from game.strategy.data.fleet import Fleet
        from game.strategy.data.order_types import FleetOrder, OrderType
        from game.strategy.data.empire import Empire
        from game.core.hex_math import HexCoord
        from game.strategy.data.planet import Planet, PlanetType

        scene = MagicMock()
        scene.camera = MagicMock()
        scene.camera.zoom = 1.0
        scene.current_empire = Empire(1, "Test", (255, 0, 0))
        scene.turn_engine = MagicMock()
        scene.turn_engine.validate_colonize_order.return_value = MagicMock(is_valid=False)

        ui = StrategyUI(scene, 800, 600)

        # Create a mock planet target
        mock_planet = MagicMock()
        mock_planet.name = "Test Planet"

        # Create fleet with COLONIZE order
        # PROJ-211: Pass registries for DI compliance (ship assignment triggers speed calc)
        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships = [make_mock_ship_instance("ColonyShip", 1, registries=fresh_registries)]
        fleet.orders = [FleetOrder(OrderType.COLONIZE, mock_planet)]

        # This should not raise NameError anymore
        ui.show_detailed_report(fleet)

        assert "Fleet" in ui.detail_text.html_text
        assert "COLONIZE" in ui.detail_text.html_text
