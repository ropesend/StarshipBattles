import pytest
import math
import pygame
from pygame.math import Vector2
from unittest.mock import MagicMock, patch

from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.entities.ship import Ship
from game.simulation.entities.projectile import Projectile
from game.engine.spatial import SpatialGrid
from game.core.constants import AttackType


@pytest.fixture
def engine_with_ships(fresh_registries):
    """Create a BattleEngine with two test ships."""
    mock_logger = MagicMock()
    engine = BattleEngine(logger=mock_logger)

    # Create dummy ships
    ship1 = Ship("TestShip1", 0, 0, (255, 0, 0), team_id=0, registries=fresh_registries)
    ship2 = Ship("TestShip2", 200, 0, (0, 0, 255), team_id=1, registries=fresh_registries)

    # Override some ship properties for stable testing
    ship1.radius = 20
    ship2.radius = 20

    # Add dummy components for HP
    dummy_comp1 = MagicMock()
    dummy_comp1.current_hp = 100
    dummy_comp1.max_hp = 100

    dummy_comp2 = MagicMock()
    dummy_comp2.current_hp = 100
    dummy_comp2.max_hp = 100

    # Manually constructing minimal layer structure
    ship1.layers = {
        'CORE': {'components': [dummy_comp1]}
    }
    ship2.layers = {
        'CORE': {'components': [dummy_comp2]}
    }

    ship1.is_alive = True
    ship2.is_alive = True

    engine.ships = [ship1, ship2]

    return engine, ship1, ship2


class TestBattleEngineCore:
    def test_spatial_grid_integration(self, engine_with_ships, fresh_registries):
        """
        Test engine.update() to verify that ships and projectiles are correctly inserted into the grid every tick.
        Test object removal from the grid when is_alive becomes False.
        """
        engine, ship1, ship2 = engine_with_ships

        # Add a backup ship to Team 0
        ship3 = Ship("BackupShip", -100, 0, (0, 255, 0), team_id=0, registries=fresh_registries)
        ship3.radius = 20
        ship3.is_alive = True
        engine.ships.append(ship3)

        # 1. Verify insertion after update
        engine.update()

        found_ships_1 = engine.grid.query_radius(ship1.position, 100)
        assert ship1 in found_ships_1, "Ship1 should be in spatial grid after update"

        found_ships_2 = engine.grid.query_radius(ship2.position, 100)
        assert ship2 in found_ships_2, "Ship2 should be in spatial grid after update"

        # 2. Add a projectile and verify insertion (Integration check)
        # Using mock projectile to simplify
        proj = MagicMock()
        proj.position = Vector2(50, 50)
        proj.velocity = Vector2(10, 0)
        proj.is_alive = True
        proj.type = AttackType.PROJECTILE  # Ensure clean Enum usage

        # Add via manager or engine method?
        # Engine update expects projectiles in manager
        engine.projectile_manager.add_projectile(proj)

        engine.update()
        found_objs = engine.grid.query_radius(Vector2(50, 50), 100)
        assert proj in found_objs, "Projectile should be in spatial grid after update"

        # 3. Test removal when dead
        ship1.is_alive = False
        proj.is_alive = False

        engine.update()

        found_objs_dead_ship = engine.grid.query_radius(ship1.position, 100)
        assert ship1 not in found_objs_dead_ship, "Dead ship should NOT be in spatial grid"

        found_objs_dead_proj = engine.grid.query_radius(Vector2(50, 50) + proj.velocity, 100)
        assert proj not in found_objs_dead_proj, "Dead projectile should NOT be in spatial grid"

    def test_system_delegation(self, engine_with_ships):
        """
        Verify that BattleEngine delegates tasks to subsystems.
        """
        engine, ship1, ship2 = engine_with_ships

        # Patch systems to verify calls
        with patch.object(engine.collision_system, 'process_ramming') as mock_ram, \
             patch.object(engine.projectile_manager, 'update') as mock_proj_update, \
             patch.object(engine.collision_system, 'process_beam_attack') as mock_beam:

            # 1. Run update - checks ramming and projectile update
            engine.update()

            mock_ram.assert_called()
            mock_proj_update.assert_called()

            # 2. Check Beam Attack delegation
            # Simulate a ship firing a beam during update
            beam_attack = {'type': AttackType.BEAM, 'damage': 10}

            ship1.comp_trigger_pulled = True
            with patch.object(ship1.combat_engine, 'fire_weapons', return_value=[beam_attack]):
                engine.update()

            mock_beam.assert_called()

    def test_remove_ship_removes_ai_controller(self, fresh_registries):
        """
        Test that remove_ship() removes both the ship and its AI controller.

        Regression test for PROJ-12 Phase 7 Fix 7.1:
        BattleEngine wraps ships in ShipControllableAdapter, so the comparison
        ai.ship == ship must unwrap the adapter via ai.ship.ship == ship.
        """
        from game.simulation.factories.ai_factory import AIControllerFactory
        mock_logger = MagicMock()
        engine = BattleEngine(logger=mock_logger)
        engine._ai_factory = AIControllerFactory(engine.grid)

        # Create test ships
        ship1 = Ship("Ship1", 0, 0, (255, 0, 0), team_id=0, registries=fresh_registries)
        ship2 = Ship("Ship2", 200, 0, (0, 0, 255), team_id=1, registries=fresh_registries)

        # Start battle - this creates AI controllers with adapters
        engine.start([ship1], [ship2])

        # Verify both ships and AI controllers are present
        assert len(engine.ships) == 2
        assert len(engine.ai_controllers) == 2

        # Find the AI controller for ship1
        ship1_ai = None
        for ai in engine.ai_controllers:
            if ai.ship.ship == ship1:  # ai.ship is adapter, ai.ship.ship is raw ship
                ship1_ai = ai
                break
        assert ship1_ai is not None, "Should have AI controller for ship1"

        # Remove ship1
        result = engine.remove_ship(ship1)

        # Verify ship was removed
        assert result is True
        assert ship1 not in engine.ships
        assert len(engine.ships) == 1

        # Verify AI controller was also removed (this was the bug)
        assert len(engine.ai_controllers) == 1
        assert ship1_ai not in engine.ai_controllers

        # Verify remaining AI controller is for ship2
        remaining_ai = engine.ai_controllers[0]
        assert remaining_ai.ship.ship == ship2


class TestBattleEngineAIControllerInjection:
    """Tests for PROJ-17: ai_controllers parameter in start() and add_ship_mid_battle()."""

    def test_start_with_precreated_ai_controllers(self, fresh_registries):
        """Verify start() accepts and uses pre-created AI controllers."""
        from game.simulation.systems.battle_engine import BattleEngine
        from game.simulation.entities.ship import Ship
        from game.ui.orchestration import BattleOrchestrator
        from game.engine.spatial import SpatialGrid

        # Create engine with mock logger
        mock_logger = MagicMock()
        engine = BattleEngine(logger=mock_logger)

        # Create test ships
        ship1 = Ship("Ship1", 0, 0, (255, 0, 0), registries=fresh_registries)
        ship2 = Ship("Ship2", 100, 0, (0, 0, 255), registries=fresh_registries)

        # Use orchestrator to create AI controllers (proper layer usage)
        orchestrator = BattleOrchestrator(engine.grid)
        ai_controllers = orchestrator.create_ai_controllers([ship1], [ship2])

        # Start battle with pre-created controllers
        engine.start([ship1], [ship2], ai_controllers=ai_controllers)

        # Verify controllers were used
        assert len(engine.ai_controllers) == 2
        assert engine.ai_controllers == ai_controllers

    def test_add_ship_mid_battle_with_precreated_controller(self, fresh_registries):
        """Verify add_ship_mid_battle() accepts pre-created AI controller."""
        from game.simulation.systems.battle_engine import BattleEngine
        from game.simulation.entities.ship import Ship
        from game.ui.orchestration import BattleOrchestrator
        from game.simulation.factories.ai_factory import AIControllerFactory

        mock_logger = MagicMock()
        engine = BattleEngine(logger=mock_logger)
        engine._ai_factory = AIControllerFactory(engine.grid)

        ship1 = Ship("Ship1", 0, 0, (255, 0, 0), registries=fresh_registries)
        ship2 = Ship("Ship2", 100, 0, (0, 0, 255), registries=fresh_registries)
        engine.start([ship1], [ship2])

        initial_count = len(engine.ai_controllers)

        # Create reinforcement with pre-created controller
        reinforcement = Ship("Reinforcement", 200, 0, (0, 255, 0), registries=fresh_registries)
        orchestrator = BattleOrchestrator(engine.grid)
        ai_controller = orchestrator.create_ai_for_ship(reinforcement, enemy_team_id=1)

        engine.add_ship_mid_battle(reinforcement, team_id=0, ai_controller=ai_controller)

        # Verify controller was added
        assert len(engine.ai_controllers) == initial_count + 1
        assert ai_controller in engine.ai_controllers
        assert reinforcement in engine.ships
        assert reinforcement.team_id == 0

class TestBattleEngineAIFactory:
    """Tests for PROJ-43: ai_factory parameter for decoupled AI creation."""

    def test_engine_with_ai_factory_creates_controllers_on_start(self, fresh_registries):
        """Verify start() uses ai_factory to create controllers when provided."""
        from game.simulation.systems.battle_engine import BattleEngine
        from game.simulation.entities.ship import Ship
        from game.simulation.factories.ai_factory import AIControllerFactory

        mock_logger = MagicMock()
        engine = BattleEngine(logger=mock_logger)

        # Create factory using engine's grid
        factory = AIControllerFactory(engine.grid)
        engine_with_factory = BattleEngine(logger=mock_logger, ai_factory=factory)

        ship1 = Ship("Ship1", 0, 0, (255, 0, 0), registries=fresh_registries)
        ship2 = Ship("Ship2", 100, 0, (0, 0, 255), registries=fresh_registries)

        # Start without explicit ai_controllers - should use factory
        engine_with_factory.start([ship1], [ship2])

        # Verify controllers were created via factory
        assert len(engine_with_factory.ai_controllers) == 2
        assert ship1.team_id == 0
        assert ship2.team_id == 1

    def test_engine_with_ai_factory_creates_controller_for_mid_battle_ship(self, fresh_registries):
        """Verify add_ship_mid_battle() uses ai_factory when no controller provided."""
        from game.simulation.systems.battle_engine import BattleEngine
        from game.simulation.entities.ship import Ship
        from game.simulation.factories.ai_factory import AIControllerFactory

        mock_logger = MagicMock()

        # Create engine with factory
        engine = BattleEngine(logger=mock_logger)
        factory = AIControllerFactory(engine.grid)
        engine_with_factory = BattleEngine(logger=mock_logger, ai_factory=factory)

        ship1 = Ship("Ship1", 0, 0, (255, 0, 0), registries=fresh_registries)
        ship2 = Ship("Ship2", 100, 0, (0, 0, 255), registries=fresh_registries)
        engine_with_factory.start([ship1], [ship2])

        initial_count = len(engine_with_factory.ai_controllers)

        # Add reinforcement without explicit controller
        reinforcement = Ship("Reinforcement", 200, 0, (0, 255, 0), registries=fresh_registries)
        engine_with_factory.add_ship_mid_battle(reinforcement, team_id=0)

        # Verify controller was created via factory
        assert len(engine_with_factory.ai_controllers) == initial_count + 1
        assert reinforcement in engine_with_factory.ships
        assert reinforcement.team_id == 0

    def test_explicit_ai_controllers_take_precedence_over_factory(self, fresh_registries):
        """Verify explicit ai_controllers parameter overrides factory."""
        from game.simulation.systems.battle_engine import BattleEngine
        from game.simulation.entities.ship import Ship
        from game.simulation.factories.ai_factory import AIControllerFactory
        from game.ui.orchestration import BattleOrchestrator

        mock_logger = MagicMock()

        # Create engine with factory
        engine = BattleEngine(logger=mock_logger)
        factory = AIControllerFactory(engine.grid)
        engine_with_factory = BattleEngine(logger=mock_logger, ai_factory=factory)

        ship1 = Ship("Ship1", 0, 0, (255, 0, 0), registries=fresh_registries)
        ship2 = Ship("Ship2", 100, 0, (0, 0, 255), registries=fresh_registries)

        # Create controllers explicitly via orchestrator
        orchestrator = BattleOrchestrator(engine_with_factory.grid)
        explicit_controllers = orchestrator.create_ai_controllers([ship1], [ship2])

        # Start with explicit controllers - should NOT use factory
        engine_with_factory.start([ship1], [ship2], ai_controllers=explicit_controllers)

        # Verify explicit controllers were used
        assert engine_with_factory.ai_controllers == explicit_controllers
