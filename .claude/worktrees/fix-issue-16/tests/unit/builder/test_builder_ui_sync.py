"""
Tests for Builder UI synchronization with Ship state.

PROJ-38: Migrated to use fresh_registries fixture for cleaner test setup.
PROJ-211: Updated to pass VehicleClassService to BuilderRightPanel.
"""
import pytest
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch

from game.simulation.entities.ship import Ship
from game.ui.services.vehicle_class_service import VehicleClassService


class TestBuilderUISync:

    @pytest.fixture(autouse=True)
    def setup_ui(self, fresh_registries):
        """Set up the UI components for testing.

        PROJ-195: Pure DI pattern - uses fresh_registries directly, no singleton hydration.
        """
        from game.ai.policy_manager import get_default_policy_manager
        from tests.infrastructure.session_cache import SessionRegistryCache

        # Store registries for use in test methods
        self.registries = fresh_registries

        # Load policy data from session cache
        cache = SessionRegistryCache.instance()
        cache.load_all_data()

        # Populate PolicyManager
        policy_mgr = get_default_policy_manager()
        policy_mgr.targeting_policies = cache.get_targeting_policies()
        policy_mgr.movement_policies = cache.get_movement_policies()
        policy_mgr._loaded = True

        # PolicyManager already loaded above — no additional cleanup needed

        pygame.display.set_mode((800, 600))  # Dummy mode
        manager = pygame_gui.UIManager((800, 600))

        # Mock Builder
        mock_builder = MagicMock()
        test_ship = Ship("Test Ship", 0, 0, (255, 255, 255), ship_class="Escort", registries=fresh_registries)
        mock_builder.ship = test_ship

        # MVVM: viewmodel.ship must return the same ship for Panel refactoring
        mock_builder.viewmodel.ship = test_ship

        # Mock Theme Manager
        mock_builder.theme_manager.get_available_themes.return_value = ["Federation", "Klingon"]

        # PROJ-211: Create VehicleClassService for DI
        vehicle_class_service = VehicleClassService(fresh_registries)

        # Mock image loading to avoid file IO errors during refresh_controls -> update_portrait_image
        with patch('pygame.image.load'):
            with patch('game.ui.screens.builder.right_panel.BuilderRightPanel.update_portrait_image'):
                from game.ui.screens.builder.right_panel import BuilderRightPanel
                panel = BuilderRightPanel(
                    mock_builder, manager, pygame.Rect(0, 0, 300, 600),
                    vehicle_class_service=vehicle_class_service
                )

        # Store for use in tests
        self.manager = manager
        self.mock_builder = mock_builder
        self.test_ship = test_ship
        self.panel = panel

        yield

        # Teardown
        # CRITICAL: Clean up ALL mocks first (prevents mock object pollution)
        patch.stopall()

        # Clean up UIManager to prevent ResourceLoader state pollution in parallel execution.
        # This is necessary because UIManager's internal ResourceLoader caches fonts globally,
        # and without cleanup, subsequent tests on the same worker may fail to load fonts.
        if hasattr(self, 'manager') and self.manager:
            self.manager.clear_and_reset()

    def _get_option_value(self, option):
        """Helper to handle pygame_gui returning (id, text) tuples or raw values."""
        if isinstance(option, tuple):
            return option[0]
        return option

    def test_refresh_controls_syncs_ui(self):
        """Verify that refresh_controls updates UI elements to match ship state."""
        # 1. Modify Ship State from defaults (Escort, Federation)
        self.mock_builder.ship.name = "New Name"

        # Ensure we pick a class that definitely exists and isn't Escort
        target_class = "Cruiser"
        classes = self.registries.vehicle_classes
        if target_class not in classes:
            target_class = list(classes.keys())[-1]

        self.mock_builder.ship.ship_class = target_class
        self.mock_builder.ship.theme_id = "Klingon"

        # Set AI to something non-default
        # Default is usually optimal_firing_range
        self.mock_builder.ship.movement_policy = "ramming_speed"

        # 2. Call Refresh (mocking portrait update to avoid side effects)
        with patch.object(self.panel, 'update_portrait_image') as mock_update_img:
            self.panel.refresh_controls()
            mock_update_img.assert_called_once()

        # 3. Assert UI values match Ship State

        # Name
        assert self.panel.name_entry.get_text() == "New Name"

        # Theme
        val = self._get_option_value(self.panel.theme_dropdown.selected_option)
        assert val == "Klingon"

        # Class
        val = self._get_option_value(self.panel.class_dropdown.selected_option)
        assert val == target_class

        # Movement policy dropdown
        val = self._get_option_value(self.panel.movement_dropdown.selected_option)
        assert val == "Ram"  # "ramming_speed" maps to "Ram" display name

    def test_type_change_filtering(self):
        """Verify that changing vehicle type filters the class list."""
        # Dynamically find a type that is NOT 'Ship' and has classes
        target_type = None
        target_class = None

        # Group classes by type
        type_map = {}
        for name, data in self.registries.vehicle_classes.items():
            ctype = data.get('type', 'Ship')
            if ctype not in type_map:
                type_map[ctype] = []
            type_map[ctype].append(name)

        # Prefer 'Station' or 'Fighter' if available
        candidates = ['Station', 'Fighter', 'Defense Satellite', 'Unknown']
        for c in candidates:
            if c in type_map and len(type_map[c]) > 0:
                target_type = c
                target_class = type_map[c][0]
                break

        if not target_type:
            # Fallback to any type that isn't 'Ship' (if possible) or just skip
            for t, classes in type_map.items():
                if classes:
                    target_type = t
                    target_class = classes[0]
                    break

        if not target_type:
            pytest.skip("No vehicle classes found to test type filtering.")

        self.mock_builder.ship.vehicle_type = target_type
        self.mock_builder.ship.ship_class = target_class

        with patch.object(self.panel, 'update_portrait_image'):
            self.panel.refresh_controls()

        # Verify Type Dropdown
        val = self._get_option_value(self.panel.vehicle_type_dropdown.selected_option)
        assert val == target_type

        # Verify Class Dropdown selected option
        val = self._get_option_value(self.panel.class_dropdown.selected_option)
        assert val == target_class

        # Verify Class Dropdown ONLY contains classes of this type
        for option in self.panel.class_dropdown.options_list:
            # Check if option is a valid class of this type
            # option might be tuple
            opt_val = self._get_option_value(option)
            c_def = self.registries.vehicle_classes.get(opt_val)
            if c_def:
                assert c_def.get('type', 'Ship') == target_type, f"Class {opt_val} should be type {target_type}"

    def test_revert_protection(self):
        """Regression test: Changes to ship MUST reflect in UI after refresh."""
        # Start state: Escort
        val = self._get_option_value(self.panel.class_dropdown.selected_option)
        assert val == "Escort"

        # Change state
        self.mock_builder.ship.ship_class = "Battleship"

        # Trigger sync
        with patch.object(self.panel, 'update_portrait_image'):
            self.panel.refresh_controls()

        # Assert sync happened
        val = self._get_option_value(self.panel.class_dropdown.selected_option)
        assert val == "Battleship", "UI did not update to reflect ship class change. Fix may have reverted."
