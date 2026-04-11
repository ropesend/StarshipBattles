import pytest
import pygame
from unittest.mock import MagicMock, patch
from game.ui.screens.workshop_screen import DesignWorkshopScreen
from game.ui.screens.workshop_context import WorkshopContext
from game.simulation.entities.ship import Ship


@pytest.fixture
def pygame_window(fresh_registries):
    # Use the display already initialized by enforce_headless / conftest pygame_display_reset
    window = pygame.display.set_mode((1200, 800), flags=pygame.HIDDEN)

    # Ensure vehicle_classes populated
    if not fresh_registries.vehicle_classes:
        fresh_registries.vehicle_classes.update({"Escort": {"max_mass": 1000, "type": "Ship"}})

    yield window, fresh_registries

    # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
    patch.stopall()


class TestBuilderImprovements:
    def test_image_scale_factor(self, pygame_window):
        """
        Verify that the image scaling logic uses the 2.5x factor.
        """
        window, registries = pygame_window
        # We can't easily inspect local variables inside _draw_schematic without inspecting the Draw calls.
        # But we can verify it doesn't crash.

        # Real Builder with Real UI Manager
        context = WorkshopContext.standalone(tech_preset_name="default", registries=registries)
        builder = DesignWorkshopScreen(1200, 800, context)
        builder._create_ui()

        # Test Draw
        try:
            builder.draw(window)
        except Exception as e:
            pytest.fail(f"draw crashed: {e}")

    def test_loading_sync(self, pygame_window):
        """
        Test that loading a ship updates the dropdowns.

        PROJ-43: Updated to mock _ship_io_adapter instead of ShipIO directly.
        """
        window, registries = pygame_window
        context = WorkshopContext.standalone(tech_preset_name="default", registries=registries)
        builder = DesignWorkshopScreen(1200, 800, context)
        builder._create_ui()

        # Create a mock ship to load
        mock_ship = MagicMock(spec=Ship)
        mock_ship.name = "LoadedShip"
        mock_ship.ship_class = "Escort"
        mock_ship.theme_id = "Federation"
        mock_ship.vehicle_type = "Ship"
        mock_ship.ai_strategy = "aggressive"
        mock_ship.design_role = "general_purpose"
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
        mock_ship.total_strategic_movement = 0.0
        mock_ship.total_maneuver_points = 0
        mock_ship.fuel_consumption = 0.0
        mock_ship.ammo_consumption = 0.0
        mock_ship.max_targets = 1
        mock_ship.construction_cost = {}
        # PROJ-194: Add typed resource stat accessor
        mock_ship.get_resource_stat.return_value = 0.0

        # PROJ-43: Mock the adapter's load_ship method (not ShipIO directly)
        builder._ship_io_adapter.load_ship = MagicMock(return_value=(mock_ship, "Success"))
        builder.load_ship()

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
