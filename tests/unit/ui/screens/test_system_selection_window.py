"""
Tests for SystemSelectionWindow - system selection dialog for warp point targeting.
"""
import pytest
import pygame
import pygame_gui
from unittest.mock import Mock, MagicMock, patch

from game.core.hex_math import HexCoord


class TestSystemSelectionWindow:
    """Tests for SystemSelectionWindow dialog."""

    @pytest.fixture
    def pygame_setup(self):
        """Set up display for tests."""
        pygame.display.set_mode((800, 600))
        yield

    @pytest.fixture
    def ui_manager(self, pygame_setup):
        """Create pygame_gui UIManager."""
        return pygame_gui.UIManager((800, 600))

    @pytest.fixture
    def mock_system(self):
        """Create a mock star system with real HexCoord for global_location."""
        def _make_system(name: str, q: int, r: int):
            system = Mock()
            system.name = name
            system.global_location = HexCoord(q, r)  # Use real HexCoord for hex_distance
            return system
        return _make_system

    @pytest.fixture
    def systems(self, mock_system):
        """Create a list of mock systems."""
        return [
            mock_system("Zeta Prime", 10, 10),
            mock_system("Alpha Centauri", 0, 0),
            mock_system("Betelgeuse", 5, 5),
        ]

    @pytest.fixture
    def current_system(self, mock_system):
        """Create the current system for distance calculation."""
        return mock_system("Current", 0, 0)

    def test_init_creates_window(self, ui_manager, systems, current_system):
        """Test that SystemSelectionWindow initializes without error."""
        from game.ui.screens.system_selection_window import SystemSelectionWindow

        callback = Mock()
        rect = pygame.Rect(100, 100, 450, 500)

        window = SystemSelectionWindow(
            rect=rect,
            manager=ui_manager,
            systems=systems,
            current_system=current_system,
            on_selection_callback=callback, window_manager=None
        )

        assert window is not None
        assert window.selection_list is not None
        assert window.btn_confirm is not None
        assert window.btn_cancel is not None

    def test_systems_sorted_alphabetically(self, ui_manager, systems, current_system):
        """Test that systems are displayed in alphabetical order."""
        from game.ui.screens.system_selection_window import SystemSelectionWindow

        callback = Mock()
        rect = pygame.Rect(100, 100, 450, 500)

        window = SystemSelectionWindow(
            rect=rect,
            manager=ui_manager,
            systems=systems,
            current_system=current_system,
            on_selection_callback=callback, window_manager=None
        )

        # Get the item list from the selection list
        item_list = window.selection_list.item_list
        # Extract just the system names (before the " (dist:" part)
        names = [item["text"].split(" (dist:")[0] for item in item_list]

        assert names == ["Alpha Centauri", "Betelgeuse", "Zeta Prime"]

    def test_display_format_includes_distance(self, ui_manager, systems, current_system):
        """Test that display strings include distance in format 'Name (dist: N)'."""
        from game.ui.screens.system_selection_window import SystemSelectionWindow

        callback = Mock()
        rect = pygame.Rect(100, 100, 450, 500)

        window = SystemSelectionWindow(
            rect=rect,
            manager=ui_manager,
            systems=systems,
            current_system=current_system,
            on_selection_callback=callback, window_manager=None
        )

        # Check format of display strings
        item_list = window.selection_list.item_list
        for item in item_list:
            text = item["text"]
            assert "(dist:" in text, f"Missing distance in '{text}'"
            assert text.endswith(")"), f"Should end with ')': '{text}'"

    def test_confirm_calls_callback_with_system_name(self, ui_manager, systems, current_system):
        """Test that confirm button calls callback with actual system name (not display string)."""
        from game.ui.screens.system_selection_window import SystemSelectionWindow

        callback = Mock()
        rect = pygame.Rect(100, 100, 450, 500)

        window = SystemSelectionWindow(
            rect=rect,
            manager=ui_manager,
            systems=systems,
            current_system=current_system,
            on_selection_callback=callback, window_manager=None
        )

        # Simulate selection of Betelgeuse
        # Find the display string for Betelgeuse
        item_list = window.selection_list.item_list
        betelgeuse_display = next(
            item["text"] for item in item_list
            if item["text"].startswith("Betelgeuse")
        )

        # Mock the selection
        window.selection_list.get_single_selection = Mock(return_value=betelgeuse_display)
        window.btn_confirm.check_pressed = Mock(return_value=True)
        window.btn_cancel.check_pressed = Mock(return_value=False)

        # Mock kill to prevent pygame_gui errors
        window.kill = Mock()

        window.update(0.1)

        # Callback should be called with the actual system name, not the display string
        callback.assert_called_once_with("Betelgeuse")

    def test_cancel_does_not_call_callback(self, ui_manager, systems, current_system):
        """Test that cancel button does not call the callback."""
        from game.ui.screens.system_selection_window import SystemSelectionWindow

        callback = Mock()
        rect = pygame.Rect(100, 100, 450, 500)

        window = SystemSelectionWindow(
            rect=rect,
            manager=ui_manager,
            systems=systems,
            current_system=current_system,
            on_selection_callback=callback, window_manager=None
        )

        # Mock button presses
        window.btn_confirm.check_pressed = Mock(return_value=False)
        window.btn_cancel.check_pressed = Mock(return_value=True)
        window.kill = Mock()

        window.update(0.1)

        callback.assert_not_called()
        window.kill.assert_called_once()

    def test_confirm_without_selection_does_nothing(self, ui_manager, systems, current_system):
        """Test that confirm with no selection does not call callback or crash."""
        from game.ui.screens.system_selection_window import SystemSelectionWindow

        callback = Mock()
        rect = pygame.Rect(100, 100, 450, 500)

        window = SystemSelectionWindow(
            rect=rect,
            manager=ui_manager,
            systems=systems,
            current_system=current_system,
            on_selection_callback=callback, window_manager=None
        )

        # No selection made
        window.selection_list.get_single_selection = Mock(return_value=None)
        window.btn_confirm.check_pressed = Mock(return_value=True)
        window.btn_cancel.check_pressed = Mock(return_value=False)
        window.kill = Mock()

        # Should not crash
        window.update(0.1)

        # Callback should not be called
        callback.assert_not_called()
        # Window should not be killed either (no selection = do nothing)
        window.kill.assert_not_called()

    def test_distance_calculation_correct(self, ui_manager, mock_system):
        """Test that distance is calculated correctly using hex_distance."""
        from game.ui.screens.system_selection_window import SystemSelectionWindow
        from game.core.hex_math import hex_distance

        # Create systems at known positions
        # hex_distance uses max(|dq|, |dr|, |ds|) where s = -q - r
        systems = [
            mock_system("Near", 2, 2),    # Distance from (0,0): max(2, 2, 4) = 4
            mock_system("Far", 10, 0),    # Distance from (0,0): max(10, 0, 10) = 10
        ]
        current = mock_system("Origin", 0, 0)
        callback = Mock()

        rect = pygame.Rect(100, 100, 450, 500)

        window = SystemSelectionWindow(
            rect=rect,
            manager=ui_manager,
            systems=systems,
            current_system=current,
            on_selection_callback=callback, window_manager=None
        )

        # Check the display strings contain correct distances
        item_list = window.selection_list.item_list
        texts = {item["text"] for item in item_list}
        assert any("Near (dist: 4)" in t for t in texts)
        assert any("Far (dist: 10)" in t for t in texts)


# ---------------------------------------------------------------------------
# PROJ-347 T4.2: Pattern §33 widget-ref placeholders
# ---------------------------------------------------------------------------

class TestSystemSelectionWindowWidgetPlaceholders:
    """PROJ-347 T4.2 — Pattern §33 widget-ref placeholders.

    ``update()`` accesses ``self.btn_confirm.check_pressed()`` and
    ``self.btn_cancel.check_pressed()``. Stage 1 must set these to
    ``None`` before ``super().__init__`` so a Null builder test can
    construct via ``bypass_init`` without subsequent AttributeError on
    those slots.
    """

    def _make_window(self, *, ui_builder):
        from game.core.hex_math import HexCoord
        from game.ui.screens.system_selection_window import SystemSelectionWindow
        from tests.fixtures.ui_widget_factory import bypass_init

        current_system = MagicMock(name="current_system")
        current_system.name = "Current"
        current_system.global_location = HexCoord(0, 0)
        sys_a = MagicMock(name="Alpha")
        sys_a.name = "Alpha"
        sys_a.global_location = HexCoord(1, 1)
        rect = pygame.Rect(0, 0, 400, 400)
        with bypass_init(SystemSelectionWindow):
            return SystemSelectionWindow(
                rect,
                MagicMock(name="ui_manager"),
                [sys_a],
                current_system,
                MagicMock(name="callback"),
                window_manager=None,
                ui_builder=ui_builder,
            )

    def test_null_builder_leaves_widget_placeholders_as_none(self):
        from tests.fixtures.system_selection_window_ui_builder import (
            NullSystemSelectionWindowUiBuilder,
        )
        window = self._make_window(
            ui_builder=NullSystemSelectionWindowUiBuilder()
        )
        # PROJ-347 T4.2: Pattern §33 placeholders set in Stage 1.
        assert window.label is None
        assert window.selection_list is None
        assert window.btn_confirm is None
        assert window.btn_cancel is None
