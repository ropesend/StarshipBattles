"""
Tests for AIControllerFactory.

PROJ-43 Phase 8: Verify the AI factory correctly creates controllers
for ships and isolates AI layer imports from BattleEngine.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestAIControllerFactory:
    """Tests for AIControllerFactory."""

    def test_factory_exists(self):
        """AIControllerFactory should be importable."""
        from game.simulation.factories.ai_factory import AIControllerFactory
        assert AIControllerFactory is not None

    def test_factory_has_create_for_ship_method(self):
        """Factory should have create_for_ship method."""
        from game.simulation.factories.ai_factory import AIControllerFactory
        assert hasattr(AIControllerFactory, 'create_for_ship')

    def test_factory_has_create_for_ships_method(self):
        """Factory should have create_for_ships method."""
        from game.simulation.factories.ai_factory import AIControllerFactory
        assert hasattr(AIControllerFactory, 'create_for_ships')

    def test_create_for_ship_returns_ai_controller(self):
        """create_for_ship should return an AIController."""
        from game.simulation.factories.ai_factory import AIControllerFactory
        from game.simulation.entities.ship import Ship
        from game.engine.spatial import SpatialGrid
        from game.core.config import PhysicsConfig

        ship = Ship(name="Test Ship", x=0, y=0, color=(255, 0, 0))
        grid = SpatialGrid(cell_size=PhysicsConfig.SPATIAL_GRID_CELL_SIZE)

        factory = AIControllerFactory(grid)
        controller = factory.create_for_ship(ship, enemy_team_id=1)

        assert controller is not None
        assert hasattr(controller, 'update')
        assert hasattr(controller, 'ship')

    def test_create_for_ships_returns_list(self):
        """create_for_ships should return a list of controllers."""
        from game.simulation.factories.ai_factory import AIControllerFactory
        from game.simulation.entities.ship import Ship
        from game.engine.spatial import SpatialGrid
        from game.core.config import PhysicsConfig

        ships = [
            Ship(name="Ship 1", x=0, y=0, color=(255, 0, 0), team_id=0),
            Ship(name="Ship 2", x=100, y=0, color=(0, 255, 0), team_id=0),
        ]
        grid = SpatialGrid(cell_size=PhysicsConfig.SPATIAL_GRID_CELL_SIZE)

        factory = AIControllerFactory(grid)
        controllers = factory.create_for_ships(ships, enemy_team_id=1)

        assert len(controllers) == 2
        for ctrl in controllers:
            assert hasattr(ctrl, 'update')
            assert hasattr(ctrl, 'ship')

    def test_factory_creates_controller_with_correct_enemy_team(self):
        """Controllers should have the correct enemy team ID."""
        from game.simulation.factories.ai_factory import AIControllerFactory
        from game.simulation.entities.ship import Ship
        from game.engine.spatial import SpatialGrid
        from game.core.config import PhysicsConfig

        ship = Ship(name="Test Ship", x=0, y=0, color=(255, 0, 0), team_id=0)
        grid = SpatialGrid(cell_size=PhysicsConfig.SPATIAL_GRID_CELL_SIZE)

        factory = AIControllerFactory(grid)
        controller = factory.create_for_ship(ship, enemy_team_id=1)

        # Verify enemy team is set (AIController stores this)
        assert controller.enemy_team_id == 1

    def test_factory_wraps_ship_in_adapter(self):
        """Factory should wrap Ship in ShipControllableAdapter."""
        from game.simulation.factories.ai_factory import AIControllerFactory
        from game.simulation.entities.ship import Ship
        from game.engine.spatial import SpatialGrid
        from game.core.config import PhysicsConfig
        from game.ai.interfaces import ShipControllableAdapter

        ship = Ship(name="Test Ship", x=0, y=0, color=(255, 0, 0))
        grid = SpatialGrid(cell_size=PhysicsConfig.SPATIAL_GRID_CELL_SIZE)

        factory = AIControllerFactory(grid)
        controller = factory.create_for_ship(ship, enemy_team_id=1)

        # The controller's ship should be a ShipControllableAdapter
        assert isinstance(controller.ship, ShipControllableAdapter)
        # And the adapter should wrap our original ship
        assert controller.ship.ship is ship

    def test_factory_exported_from_package(self):
        """AIControllerFactory should be exported from factories package."""
        from game.simulation.factories import AIControllerFactory
        assert AIControllerFactory is not None


class TestAIControllerFactoryIntegration:
    """Integration tests for AIControllerFactory with BattleEngine."""

    def test_factory_controllers_work_with_battle_engine(self):
        """Controllers from factory should work with BattleEngine."""
        from game.simulation.factories.ai_factory import AIControllerFactory
        from game.simulation.systems.battle_engine import BattleEngine
        from game.simulation.entities.ship import Ship
        from game.engine.spatial import SpatialGrid
        from game.core.config import PhysicsConfig

        # Create ships
        ship1 = Ship(name="Player Ship", x=0, y=0, color=(255, 0, 0), team_id=0)
        ship2 = Ship(name="Enemy Ship", x=500, y=0, color=(0, 255, 0), team_id=1)

        # Create engine with its own grid
        engine = BattleEngine()

        # Factory needs engine's grid for AI to work correctly
        factory = AIControllerFactory(engine.grid)

        # Create controllers
        player_controllers = factory.create_for_ships([ship1], enemy_team_id=1)
        enemy_controllers = factory.create_for_ships([ship2], enemy_team_id=0)
        all_controllers = player_controllers + enemy_controllers

        # Start battle with pre-created controllers
        engine.start([ship1], [ship2], ai_controllers=all_controllers)

        # Run one update tick - should not raise
        engine.update()

        # Verify controllers were used
        assert len(engine.ai_controllers) == 2
