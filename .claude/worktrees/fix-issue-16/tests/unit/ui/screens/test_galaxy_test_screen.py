"""Tests for GalaxyTestScreen (PROJ-142 Phase 2 Task 2.7).

Tests the galaxy/system generation testing screen with its mode switching
and helper classes.
"""

import pytest
from unittest.mock import MagicMock, patch


# --- Constants Tests ---

class TestGalaxyTestConstants:
    """Tests for galaxy_test constants module."""

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

    def test_modes_are_distinct(self):
        """All modes are distinct strings."""
        from game.ui.screens.galaxy_test.screen import GalaxyTestScreen

        modes = [
            GalaxyTestScreen.MODE_MENU,
            GalaxyTestScreen.MODE_GALAXY,
            GalaxyTestScreen.MODE_SYSTEM
        ]

        assert len(set(modes)) == 3
