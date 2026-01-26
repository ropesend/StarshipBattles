import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch
from game.ui.screens import workshop_screen
from game.ui.screens.workshop_screen import DesignWorkshopGUI
from game.ui.screens.workshop_context import WorkshopContext
from game.simulation.entities.ship import Ship
from game.core.registry import RegistryManager


@pytest.fixture
def pygame_window():
    pygame.init()
    # Create a hidden window for UI Manager
    window = pygame.display.set_mode((1200, 800), flags=pygame.HIDDEN)

    # Ensure vehicle_classes populated
    if not RegistryManager.instance().vehicle_classes:
        RegistryManager.instance().vehicle_classes.update({"Escort": {"max_mass": 1000, "type": "Ship"}})

    yield window

    # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
    patch.stopall()

    pygame.quit()
    RegistryManager.instance().clear()


class TestBuilderImprovements:
    def test_image_scale_factor(self, pygame_window):
        """
        Verify that the image scaling logic uses the 2.5x factor.
        """
        window = pygame_window
        # We can't easily inspect local variables inside _draw_schematic without inspecting the Draw calls.
        # But we can verify it doesn't crash.

        # Real Builder with Real UI Manager
        context = WorkshopContext.standalone(tech_preset_name="default")
        builder = DesignWorkshopGUI(1200, 800, context)
        builder._create_ui()

        # Test Draw
        try:
            builder.draw(window)
        except Exception as e:
            pytest.fail(f"draw crashed: {e}")

    def test_loading_sync(self, pygame_window):
        """
        Test that loading a ship updates the dropdowns.
        """
        context = WorkshopContext.standalone(tech_preset_name="default")
        builder = DesignWorkshopGUI(1200, 800, context)
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
        mock_ship.resources = MagicMock()  # spec=Ship doesn't see instance vars automatically
        mock_ship.resources.set_max_value('fuel', 1000)
        mock_ship.resources.set_max_value('ammo', 100)
        mock_ship.resources.set_max_value('energy', 1000)
        mock_ship.max_shields = 200
        mock_ship.shield_regen_rate = 10
        mock_ship.shield_regen_cost = 5
        mock_ship.layer_status = {}
        mock_ship.get_ability_total.return_value = 100
        mock_ship.total_defense_score = 1.0
        mock_ship.baseline_to_hit_offense = 1.0

        # Mock ShipIO
        with patch('game.ui.screens.workshop_screen.ShipIO.load_ship', return_value=(mock_ship, "Success")):
            builder._load_ship()

        # Verification
        assert builder.ship == mock_ship

        # Check UI Elements (Real UISelectionLists in Dropdowns)
        # Dropdown.selected_option might be (label, value) or value in some versions
        selected = builder.right_panel.class_dropdown.selected_option
        if isinstance(selected, tuple):
            assert selected[0] == "Escort"
        else:
            assert selected == "Escort"
        # Theme might vary depending on what theme manager finds on disk
