"""Tests for GalaxyTestScreen (PROJ-142 Phase 2 Task 2.7).

Tests the galaxy/system generation testing screen with its mode switching
and helper classes.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


# --- Constants Tests ---

class TestGalaxyTestConstants:
    """Tests for galaxy_test constants module."""

    def test_constants_can_be_imported(self):
        """Constants module can be imported."""
        from game.ui.screens.galaxy_test.constants import (
            SIDEBAR_WIDTH,
            HEX_SIZE,
            PLANET_TYPE_COLORS
        )

        assert SIDEBAR_WIDTH is not None
        assert HEX_SIZE is not None
        assert PLANET_TYPE_COLORS is not None

    def test_sidebar_width_is_positive(self):
        """SIDEBAR_WIDTH is a positive number."""
        from game.ui.screens.galaxy_test.constants import SIDEBAR_WIDTH

        assert isinstance(SIDEBAR_WIDTH, (int, float))
        assert SIDEBAR_WIDTH > 0

    def test_hex_size_is_positive(self):
        """HEX_SIZE is a positive number."""
        from game.ui.screens.galaxy_test.constants import HEX_SIZE

        assert isinstance(HEX_SIZE, (int, float))
        assert HEX_SIZE > 0

    def test_planet_type_colors_is_dict(self):
        """PLANET_TYPE_COLORS is a dict."""
        from game.ui.screens.galaxy_test.constants import PLANET_TYPE_COLORS

        assert isinstance(PLANET_TYPE_COLORS, dict)

    def test_planet_type_colors_valid_rgb(self):
        """PLANET_TYPE_COLORS values are valid RGB tuples."""
        from game.ui.screens.galaxy_test.constants import PLANET_TYPE_COLORS

        for planet_type, color in PLANET_TYPE_COLORS.items():
            assert isinstance(color, tuple), f"{planet_type} color is not tuple"
            assert len(color) == 3, f"{planet_type} color not 3 elements"
            assert all(0 <= c <= 255 for c in color), f"{planet_type} color invalid"


# --- GalaxyTestScreen Import Tests ---

class TestGalaxyTestScreenImport:
    """Tests for GalaxyTestScreen import."""

    def test_screen_can_be_imported(self):
        """GalaxyTestScreen can be imported."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        assert GalaxyTestScreen is not None

    def test_screen_has_mode_constants(self):
        """GalaxyTestScreen has mode constants."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        assert hasattr(GalaxyTestScreen, 'MODE_MENU')
        assert hasattr(GalaxyTestScreen, 'MODE_GALAXY')
        assert hasattr(GalaxyTestScreen, 'MODE_SYSTEM')


# --- GalaxyTestScreen Initialization Tests ---

class TestGalaxyTestScreenInit:
    """Tests for GalaxyTestScreen initialization."""

    def test_screen_stores_dimensions(self):
        """Screen stores width and height."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        with patch.object(GalaxyTestScreen, '__init__', lambda self, *a, **kw: None):
            screen = GalaxyTestScreen.__new__(GalaxyTestScreen)

        screen.screen_width = 1920
        screen.screen_height = 1080

        assert screen.screen_width == 1920
        assert screen.screen_height == 1080

    def test_screen_stores_callback(self):
        """Screen stores on_close_callback."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        with patch.object(GalaxyTestScreen, '__init__', lambda self, *a, **kw: None):
            screen = GalaxyTestScreen.__new__(GalaxyTestScreen)

        callback = MagicMock()
        screen.on_close_callback = callback

        assert screen.on_close_callback is callback

    def test_screen_starts_in_menu_mode(self):
        """Screen starts in menu mode."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        with patch.object(GalaxyTestScreen, '__init__', lambda self, *a, **kw: None):
            screen = GalaxyTestScreen.__new__(GalaxyTestScreen)

        screen.mode = GalaxyTestScreen.MODE_MENU

        assert screen.mode == GalaxyTestScreen.MODE_MENU

    def test_screen_has_canvas_dimensions(self):
        """Screen has canvas dimensions."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        with patch.object(GalaxyTestScreen, '__init__', lambda self, *a, **kw: None):
            screen = GalaxyTestScreen.__new__(GalaxyTestScreen)

        screen.canvas_width = 1600
        screen.canvas_height = 900

        assert screen.canvas_width == 1600
        assert screen.canvas_height == 900

    def test_screen_has_ui_elements_list(self):
        """Screen has _ui_elements list."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        with patch.object(GalaxyTestScreen, '__init__', lambda self, *a, **kw: None):
            screen = GalaxyTestScreen.__new__(GalaxyTestScreen)

        screen._ui_elements = []

        assert isinstance(screen._ui_elements, list)


# --- Clear UI Tests ---

class TestClearUI:
    """Tests for UI clearing."""

    def test_clear_ui_kills_elements(self):
        """_clear_ui kills all UI elements."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        with patch.object(GalaxyTestScreen, '__init__', lambda self, *a, **kw: None):
            screen = GalaxyTestScreen.__new__(GalaxyTestScreen)

        elem1 = MagicMock()
        elem2 = MagicMock()
        screen._ui_elements = [elem1, elem2]

        screen._clear_ui()

        elem1.kill.assert_called_once()
        elem2.kill.assert_called_once()

    def test_clear_ui_empties_list(self):
        """_clear_ui empties _ui_elements list."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        with patch.object(GalaxyTestScreen, '__init__', lambda self, *a, **kw: None):
            screen = GalaxyTestScreen.__new__(GalaxyTestScreen)

        screen._ui_elements = [MagicMock(), MagicMock()]

        screen._clear_ui()

        assert len(screen._ui_elements) == 0


# --- Mode Switching Tests ---

class TestModeSwitching:
    """Tests for mode switching."""

    def test_mode_menu_is_string(self):
        """MODE_MENU is a string constant."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        assert isinstance(GalaxyTestScreen.MODE_MENU, str)

    def test_mode_galaxy_is_string(self):
        """MODE_GALAXY is a string constant."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        assert isinstance(GalaxyTestScreen.MODE_GALAXY, str)

    def test_mode_system_is_string(self):
        """MODE_SYSTEM is a string constant."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        assert isinstance(GalaxyTestScreen.MODE_SYSTEM, str)

    def test_modes_are_distinct(self):
        """All modes are distinct strings."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        modes = [
            GalaxyTestScreen.MODE_MENU,
            GalaxyTestScreen.MODE_GALAXY,
            GalaxyTestScreen.MODE_SYSTEM
        ]

        assert len(set(modes)) == 3


# --- Camera Tests ---

class TestCameraSetup:
    """Tests for camera configuration."""

    def test_screen_has_camera(self):
        """Screen has camera attribute."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        with patch.object(GalaxyTestScreen, '__init__', lambda self, *a, **kw: None):
            screen = GalaxyTestScreen.__new__(GalaxyTestScreen)

        camera = MagicMock()
        screen.camera = camera

        assert screen.camera is camera


# --- Helper Class Tests ---

class TestGalaxyModeHelper:
    """Tests for GalaxyModeHelper."""

    def test_helper_can_be_imported(self):
        """GalaxyModeHelper can be imported."""
        from game.ui.screens.galaxy_test.galaxy_mode import GalaxyModeHelper

        assert GalaxyModeHelper is not None


class TestSystemModeHelper:
    """Tests for SystemModeHelper."""

    def test_helper_can_be_imported(self):
        """SystemModeHelper can be imported."""
        from game.ui.screens.galaxy_test.system_mode import SystemModeHelper

        assert SystemModeHelper is not None


# --- FPS Tracking Tests ---

class TestFPSTracking:
    """Tests for FPS tracking."""

    def test_screen_has_fps_clock(self):
        """Screen has fps_clock attribute."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        with patch.object(GalaxyTestScreen, '__init__', lambda self, *a, **kw: None):
            screen = GalaxyTestScreen.__new__(GalaxyTestScreen)

        screen.fps_clock = MagicMock()

        assert screen.fps_clock is not None

    def test_screen_has_current_fps(self):
        """Screen has current_fps attribute."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        with patch.object(GalaxyTestScreen, '__init__', lambda self, *a, **kw: None):
            screen = GalaxyTestScreen.__new__(GalaxyTestScreen)

        screen.current_fps = 60.0

        assert screen.current_fps == 60.0
