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
def engine_with_ships():
    """Create a BattleEngine with two test ships."""
    mock_logger = MagicMock()
    engine = BattleEngine(logger=mock_logger)

    # Create dummy ships
    ship1 = Ship("TestShip1", 0, 0, (255, 0, 0), team_id=0)
    ship2 = Ship("TestShip2", 200, 0, (0, 0, 255), team_id=1)

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
    def test_spatial_grid_integration(self, engine_with_ships):
        """
        Test engine.update() to verify that ships and projectiles are correctly inserted into the grid every tick.
        Test object removal from the grid when is_alive becomes False.
        """
        engine, ship1, ship2 = engine_with_ships

        # Add a backup ship to Team 0
        ship3 = Ship("BackupShip", -100, 0, (0, 255, 0), team_id=0)
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
            with patch.object(ship1, 'fire_weapons', return_value=[beam_attack]):
                engine.update()

            mock_beam.assert_called()
