
import unittest
import pygame
from battle import BattleScene, BATTLE_LOG
from ship import Ship, initialize_ship_data
from components import load_components, create_component, LayerType
import os
from unittest import mock

class TestBattleSceneExtended(unittest.TestCase):
    """Test BattleScene simulation loop, victory conditions, and headless mode."""
    
    @classmethod
    def setUpClass(cls):
        pygame.init()
        # Ensure data dir is accessible
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        initialize_ship_data(base_dir)
        load_components(os.path.join(base_dir, "data", "components.json"))
        
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_is_battle_over_victory(self):
        """Verify is_battle_over identifies when one team is eliminated."""
        scene = BattleScene(1000, 1000)
        
        ship1 = Ship("T1", 0, 0, (255,0,0), team_id=0)
        ship2 = Ship("T2", 1000, 1000, (0,0,255), team_id=1)
        
        # Ensure they have bridges, crew, AND ENGINES so they aren't derelict
        for s in [ship1, ship2]:
            s.add_component(create_component('bridge'), LayerType.CORE)
            s.add_component(create_component('crew_quarters'), LayerType.CORE)
            s.add_component(create_component('life_support'), LayerType.CORE)
            s.add_component(create_component('standard_engine'), LayerType.INNER)
            s.recalculate_stats()
        
        scene.start([ship1], [ship2])
        self.assertFalse(scene.is_battle_over(), "Battle should NOT be over at start with active ships")
        
        # Kill ship2
        ship2.is_alive = False
        self.assertTrue(scene.is_battle_over())
        self.assertEqual(scene.get_winner(), 0)

    def test_update_loop_tick_counter(self):
        """Verify update loop increments sim_tick_counter."""
        scene = BattleScene(1000, 1000)
        ship1 = Ship("T1", 0, 0, (255,0,0), team_id=0)
        ship2 = Ship("T2", 1000, 1000, (0,0,255), team_id=1)
        for s in [ship1, ship2]:
            s.add_component(create_component('bridge'), LayerType.CORE)
            s.add_component(create_component('crew_quarters'), LayerType.CORE)
            s.add_component(create_component('life_support'), LayerType.CORE)
            s.add_component(create_component('standard_engine'), LayerType.INNER)
            s.recalculate_stats()
        
        scene.start([ship1], [ship2])
        
        self.assertEqual(scene.sim_tick_counter, 0)
        scene.update([])
        self.assertEqual(scene.sim_tick_counter, 1)

    def test_headless_mode_initialization(self):
        """Verify headless mode sets start time and skips camera fit."""
        scene = BattleScene(1000, 1000)
        # Mock camera to ensure fit_objects isn't called normally if fit_objects fails without screen
        scene.camera = mock.MagicMock()
        
        scene.start([], [], headless=True)
        self.assertTrue(scene.headless_mode)
        self.assertIsNotNone(scene.headless_start_time)
        
        scene.camera.fit_objects.assert_not_called()

    def test_process_beam_attack_logic(self):
        """Verify _process_beam_attack applies damage to target."""
        scene = BattleScene(1000, 1000)
        ship = Ship("Target", 0, 0, (255,255,255), team_id=1)
        ship.radius = 20
        # Mock take_damage
        ship.take_damage = mock.MagicMock()
        
        mock_comp = mock.MagicMock()
        mock_comp.shots_hit = 0
        mock_comp.calculate_hit_chance.return_value = 1.0
        
        beam = {
            'type': 'beam',
            'damage': 25,
            'target': ship,
            'origin': pygame.math.Vector2(0,0),
            'direction': pygame.math.Vector2(1,0),
            'range': 100,
            'component': mock_comp
        }
        
        scene._process_beam_attack(beam)
        ship.take_damage.assert_called_with(25)

if __name__ == '__main__':
    unittest.main()
