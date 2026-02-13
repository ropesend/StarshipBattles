"""
Tests for AIControllerFactory.

PROJ-43 Phase 8: Verify the AI factory correctly creates controllers
for ships and isolates AI layer imports from BattleEngine.

PROJ-126: Factory moved to game/ai/ layer to fix architecture violation.
Factory now uses two-phase initialization (set_grid after construction).
"""
import pytest
from unittest.mock import MagicMock, patch


class TestAIControllerFactory:
    """Tests for AIControllerFactory."""

    def test_factory_exists(self):
        """AIControllerFactory should be importable from AI layer."""
        from game.ai.ai_factory import AIControllerFactory
        assert AIControllerFactory is not None

    def test_factory_has_create_for_ship_method(self):
        """Factory should have create_for_ship method."""
        from game.ai.ai_factory import AIControllerFactory
        assert hasattr(AIControllerFactory, 'create_for_ship')

    def test_factory_has_create_for_ships_method(self):
        """Factory should have create_for_ships method."""
        from game.ai.ai_factory import AIControllerFactory
        assert hasattr(AIControllerFactory, 'create_for_ships')

    def test_factory_has_set_grid_method(self):
        """Factory should have set_grid method."""
        from game.ai.ai_factory import AIControllerFactory
        assert hasattr(AIControllerFactory, 'set_grid')

    def test_create_for_ship_returns_ai_controller(self, fresh_registries):
        """create_for_ship should return an AIController."""
        from game.ai.ai_factory import AIControllerFactory
        from game.simulation.entities.ship import Ship
        from game.engine.spatial import SpatialGrid
        from game.core.config import PhysicsConfig

        ship = Ship(name="Test Ship", x=0, y=0, color=(255, 0, 0), registries=fresh_registries)
        grid = SpatialGrid(cell_size=PhysicsConfig.SPATIAL_GRID_CELL_SIZE)

        factory = AIControllerFactory()
        factory.set_grid(grid)
        controller = factory.create_for_ship(ship, enemy_team_id=1)

        assert controller is not None
        assert hasattr(controller, 'update')
        assert hasattr(controller, 'ship')

    def test_create_for_ship_without_grid_raises(self, fresh_registries):
        """create_for_ship should raise if set_grid not called."""
        from game.ai.ai_factory import AIControllerFactory
        from game.simulation.entities.ship import Ship

        ship = Ship(name="Test Ship", x=0, y=0, color=(255, 0, 0), registries=fresh_registries)

        factory = AIControllerFactory()
        # Don't call set_grid

        with pytest.raises(RuntimeError, match="set_grid"):
            factory.create_for_ship(ship, enemy_team_id=1)

    def test_create_for_ships_returns_list(self, fresh_registries):
        """create_for_ships should return a list of controllers."""
        from game.ai.ai_factory import AIControllerFactory
        from game.simulation.entities.ship import Ship
        from game.engine.spatial import SpatialGrid
        from game.core.config import PhysicsConfig

        ships = [
            Ship(name="Ship 1", x=0, y=0, color=(255, 0, 0), team_id=0, registries=fresh_registries),
            Ship(name="Ship 2", x=100, y=0, color=(0, 255, 0), team_id=0, registries=fresh_registries),
        ]
        grid = SpatialGrid(cell_size=PhysicsConfig.SPATIAL_GRID_CELL_SIZE)

        factory = AIControllerFactory()
        factory.set_grid(grid)
        controllers = factory.create_for_ships(ships, enemy_team_id=1)

        assert len(controllers) == 2
        for ctrl in controllers:
            assert hasattr(ctrl, 'update')
            assert hasattr(ctrl, 'ship')

    def test_factory_creates_controller_with_correct_enemy_team(self, fresh_registries):
        """Controllers should have the correct enemy team ID."""
        from game.ai.ai_factory import AIControllerFactory
        from game.simulation.entities.ship import Ship
        from game.engine.spatial import SpatialGrid
        from game.core.config import PhysicsConfig

        ship = Ship(name="Test Ship", x=0, y=0, color=(255, 0, 0), team_id=0, registries=fresh_registries)
        grid = SpatialGrid(cell_size=PhysicsConfig.SPATIAL_GRID_CELL_SIZE)

        factory = AIControllerFactory()
        factory.set_grid(grid)
        controller = factory.create_for_ship(ship, enemy_team_id=1)

        # Verify enemy team is set (AIController stores this)
        assert controller.enemy_team_id == 1

    def test_factory_wraps_ship_in_adapter(self, fresh_registries):
        """Factory should wrap Ship in ShipControllableAdapter."""
        from game.ai.ai_factory import AIControllerFactory
        from game.simulation.entities.ship import Ship
        from game.engine.spatial import SpatialGrid
        from game.core.config import PhysicsConfig
        from game.ai.interfaces import ShipControllableAdapter

        ship = Ship(name="Test Ship", x=0, y=0, color=(255, 0, 0), registries=fresh_registries)
        grid = SpatialGrid(cell_size=PhysicsConfig.SPATIAL_GRID_CELL_SIZE)

        factory = AIControllerFactory()
        factory.set_grid(grid)
        controller = factory.create_for_ship(ship, enemy_team_id=1)

        # The controller's ship should be a ShipControllableAdapter
        assert isinstance(controller.ship, ShipControllableAdapter)
        # And the adapter should wrap our original ship
        assert controller.ship.ship is ship

    def test_factory_exported_from_ai_package(self):
        """AIControllerFactory should be exported from ai package."""
        from game.ai import AIControllerFactory
        assert AIControllerFactory is not None


class TestAIControllerFactoryIntegration:
    """Integration tests for AIControllerFactory with BattleEngine."""

    def test_factory_controllers_work_with_battle_engine(self, fresh_registries):
        """Controllers from factory should work with BattleEngine."""
        from game.ai.ai_factory import AIControllerFactory
        from game.simulation.systems.battle_engine import BattleEngine
        from game.simulation.entities.ship import Ship

        # Create ships
        ship1 = Ship(name="Player Ship", x=0, y=0, color=(255, 0, 0), team_id=0, registries=fresh_registries)
        ship2 = Ship(name="Enemy Ship", x=500, y=0, color=(0, 255, 0), team_id=1, registries=fresh_registries)

        # Create factory (no grid yet)
        factory = AIControllerFactory()

        # Create engine with factory - engine will call set_grid automatically
        engine = BattleEngine(ai_factory=factory)

        # Factory now has the grid, can create controllers
        player_controllers = factory.create_for_ships([ship1], enemy_team_id=1)
        enemy_controllers = factory.create_for_ships([ship2], enemy_team_id=0)
        all_controllers = player_controllers + enemy_controllers

        # Start battle with pre-created controllers
        engine.start([ship1], [ship2], ai_controllers=all_controllers)

        # Run one update tick - should not raise
        engine.update()

        # Verify controllers were used
        assert len(engine.ai_controllers) == 2

    def test_factory_injected_via_battle_engine_constructor(self, fresh_registries):
        """Factory injected to BattleEngine should have grid set automatically."""
        from game.ai.ai_factory import AIControllerFactory
        from game.simulation.systems.battle_engine import BattleEngine
        from game.simulation.entities.ship import Ship

        factory = AIControllerFactory()
        assert factory._grid is None  # Grid not set yet

        engine = BattleEngine(ai_factory=factory)
        assert factory._grid is engine.grid  # Engine set the grid

        # Can now create controllers
        ship = Ship(name="Test", x=0, y=0, color=(255, 0, 0), registries=fresh_registries)
        controller = factory.create_for_ship(ship, enemy_team_id=1)
        assert controller is not None
