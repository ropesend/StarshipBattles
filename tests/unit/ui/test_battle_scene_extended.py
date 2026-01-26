import pytest
import sys

import pygame
from game.ui.screens.battle_scene import BattleScene
from game.simulation.entities.ship import Ship
from game.simulation.entities.ship_loader import initialize_ship_data
from game.simulation.components.component import load_components, create_component
from game.simulation.components.component_constants import LayerType
from unittest.mock import MagicMock
from game.ai.strategy_manager import StrategyManager
from game.core.registry import RegistryManager
from tests.fixtures.paths import get_unit_test_data_dir


class TestBattleSceneExtended:
    """Test BattleScene simulation loop, victory conditions, and headless mode."""

    @pytest.fixture(autouse=True)
    def setup_strategy_manager(self):
        """Setup and teardown for AI Strategy Manager."""
        # Note: pygame, registry, and data loading handled by conftest fixtures
        # initialize_ship_data() and load_components() are patched to be no-ops
        # because the reset_game_state fixture already loaded the data

        # AI Strategy Manager still needs to be loaded per-test
        test_data_path = str(get_unit_test_data_dir())
        manager = StrategyManager.instance()
        manager.load_data(
             test_data_path,
             targeting_file="test_targeting_policies.json",
             movement_file="test_movement_policies.json",
             strategy_file="test_combat_strategies.json"
        )
        manager._loaded = True

        yield

        # Cleanup: AI Strategy Manager should still be cleared
        StrategyManager.instance().clear()

    def test_is_battle_over_victory(self):
        """Verify is_battle_over identifies when one team is eliminated."""
        scene = BattleScene(1000, 1000)

        ship1 = Ship("T1", 0, 0, (255,0,0), team_id=0, ship_class="Escort")
        ship2 = Ship("T2", 1000, 1000, (0,0,255), team_id=1, ship_class="Escort")

        # Ensure they are fully equipped ships
        for s in [ship1, ship2]:
            s.add_component(create_component('bridge'), LayerType.CORE)
            s.add_component(create_component('crew_quarters'), LayerType.CORE)
            s.add_component(create_component('life_support'), LayerType.CORE)
            s.add_component(create_component('standard_engine'), LayerType.OUTER)
            s.recalculate_stats()

        scene.start([ship1], [ship2])
        assert not scene.is_battle_over(), "Battle should NOT be over at start with active ships"

        # Kill ship2
        ship2.is_alive = False
        assert scene.is_battle_over()
        assert scene.get_winner() == 0

    def test_update_loop_tick_counter(self):
        """Verify update loop increments sim_tick_counter."""
        scene = BattleScene(1000, 1000)
        ship1 = Ship("T1", 0, 0, (255,0,0), team_id=0, ship_class="Escort")
        ship2 = Ship("T2", 1000, 1000, (0,0,255), team_id=1, ship_class="Escort")
        for s in [ship1, ship2]:
            s.add_component(create_component('bridge'), LayerType.CORE)
            s.add_component(create_component('crew_quarters'), LayerType.CORE)
            s.add_component(create_component('life_support'), LayerType.CORE)
            s.add_component(create_component('standard_engine'), LayerType.OUTER)
            s.recalculate_stats()

        scene.start([ship1], [ship2])

        assert scene.sim_tick_counter == 0
        scene.update([])
        assert scene.sim_tick_counter == 1

    def test_headless_mode_initialization(self):
        """Verify headless mode sets start time and skips camera fit."""
        scene = BattleScene(1000, 1000)
        # Mock camera to ensure fit_objects isn't called normally if fit_objects fails without screen
        scene.camera = MagicMock()

        scene.start([], [], headless=True)
        assert scene.headless_mode
        assert scene.headless_start_time is not None

        scene.camera.fit_objects.assert_not_called()

    def test_process_beam_attack_logic(self):
        """Verify _process_beam_attack applies damage to target."""
        scene = BattleScene(1000, 1000)
        ship = Ship("Target", 0, 0, (255,255,255), team_id=1)
        ship.radius = 20
        # Mock take_damage
        ship.take_damage = MagicMock()

        # Mock the ability that will be returned by get_ability
        mock_ability = MagicMock()
        mock_ability.calculate_hit_chance.return_value = 1.0
        mock_ability.get_damage.return_value = 25

        # Mock the component to return the mock ability
        mock_comp = MagicMock()
        mock_comp.shots_hit = 0
        mock_comp.get_ability.return_value = mock_ability

        beam = {
            'type': 'beam',
            'damage': 25,
            'target': ship,
            'origin': pygame.math.Vector2(0,0),
            'direction': pygame.math.Vector2(1,0),
            'range': 100,
            'component': mock_comp
        }

        scene.engine.collision_system.process_beam_attack(beam, scene.engine.recent_beams)
        ship.take_damage.assert_called_with(25)
