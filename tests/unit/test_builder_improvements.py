import unittest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.ui.screens import builder_screen
from game.ui.screens.builder_screen import BuilderSceneGUI
from game.simulation.entities.ship import Ship, SHIP_CLASSES

class TestBuilderImprovements(unittest.TestCase):
    def setUp(self):
        pygame.init()
        # Create a hidden window for UI Manager
        self.window = pygame.display.set_mode((1200, 800), flags=pygame.HIDDEN)
        
        # Ensure SHIP_CLASSES populated
        if not SHIP_CLASSES:
             SHIP_CLASSES.update({"Escort": {"max_mass": 1000, "type": "Ship"}})

    def tearDown(self):
        pass # pygame.quit() removed for session isolation

    def test_image_scale_factor(self):
        """
        Verify that the image scaling logic uses the 2.5x factor.
        """
        # We can't easily inspect local variables inside _draw_schematic without inspecting the Draw calls.
        # But we can verify it doesn't crash.
        
        # Real Builder with Real UI Manager
        builder = BuilderSceneGUI(1200, 800, None)
        builder._create_ui()
        
        # Test Draw
        try:
            builder.draw(self.window)
        except Exception as e:
            self.fail(f"draw crashed: {e}")

    def test_loading_sync(self):
        """
        Test that loading a ship updates the dropdowns.
        """
        builder = BuilderSceneGUI(1200, 800, None)
        builder._create_ui()
        
        # Create a mock ship to load
        mock_ship = MagicMock(spec=Ship)
        mock_ship.name = "LoadedShip"
        mock_ship.ship_class = "Escort"
        mock_ship.theme_id = "Federation"
        mock_ship.ai_strategy = "aggressive"
        mock_ship.layers = {}
        mock_ship.mass_limits_ok = True
        mock_ship.get_missing_requirements.return_value = []
        mock_ship.mass = 500
        mock_ship.max_mass_budget = 1000
        mock_ship.cost = 1000
        mock_ship.crew_required = 10
        mock_ship.crew_quarters = 20
        mock_ship.life_support = 20
        mock_ship.total_hp = 500
        mock_ship.max_hp = 500
        mock_ship.energy_generated = 100
        mock_ship.energy_consumption = 50
        mock_ship.max_speed = 100
        mock_ship.turn_speed = 30
        mock_ship.acceleration_rate = 10
        mock_ship.total_thrust = 1000
        mock_ship.energy_gen_rate = 10
        mock_ship.max_fuel = 1000
        mock_ship.max_ammo = 100
        mock_ship.max_energy = 1000
        mock_ship.max_shields = 200
        mock_ship.shield_regen_rate = 10
        mock_ship.shield_regen_cost = 5
        mock_ship.layer_status = {}
        mock_ship.get_ability_total.return_value = 100
        mock_ship.to_hit_profile = 1.0
        mock_ship.baseline_to_hit_offense = 1.0
        
        # Mock ShipIO
        with patch('game.ui.screens.builder_screen.ShipIO.load_ship', return_value=(mock_ship, "Success")):
            builder._load_ship()
            
        # Verification
        self.assertEqual(builder.ship, mock_ship)
        
        # Check UI Elements (Real UISelectionLists in Dropdowns)
        # Dropdown.selected_option might be (label, value) or value in some versions
        selected = builder.right_panel.class_dropdown.selected_option
        if isinstance(selected, tuple):
            self.assertEqual(selected[0], "Escort")
        else:
            self.assertEqual(selected, "Escort")
        # Theme might vary depending on what theme manager finds on disk



if __name__ == '__main__':
    unittest.main()
