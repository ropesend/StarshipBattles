"""Tests for StrategyMenuPanel dropdown component."""

import pytest
from unittest.mock import MagicMock, patch

from game.ui.screens.strategy_menu_panel import (
    StrategyMenuPanel,
    MENU_SAVE_GAME,
    MENU_LOAD_GAME,
    MENU_SETTINGS,
    MENU_CONTROLS,
    MENU_QUIT_TO_MENU,
    MENU_QUIT_GAME,
    MENU_BUTTONS,
    PANEL_WIDTH,
    PANEL_HEIGHT,
    BUTTON_COUNT,
)


# --- Helpers ---

def _make_panel(callback=None):
    """Create a StrategyMenuPanel with mocked pygame_gui dependencies."""
    import pygame
    rect = pygame.Rect(0, 0, PANEL_WIDTH, PANEL_HEIGHT)
    manager = MagicMock()
    cb = callback or MagicMock()
    with patch.object(StrategyMenuPanel, '__init__', lambda self, *a, **kw: None):
        panel = StrategyMenuPanel.__new__(StrategyMenuPanel)
    panel.on_option_callback = cb
    panel._option_buttons = {}
    panel.ui_manager = manager
    return panel, cb


# --- Constants Tests ---

class TestMenuPanelConstants:
    """Verify module-level constants are correct."""

    def test_button_count(self):
        assert BUTTON_COUNT == 6

    def test_menu_buttons_length(self):
        assert len(MENU_BUTTONS) == 6

    def test_menu_buttons_labels(self):
        labels = [label for label, _ in MENU_BUTTONS]
        assert labels == [
            "Save Game", "Load Game", "Settings",
            "Controls", "Quit to Menu", "Quit Game",
        ]

    def test_menu_buttons_option_ids(self):
        option_ids = [oid for _, oid in MENU_BUTTONS]
        assert option_ids == [
            MENU_SAVE_GAME, MENU_LOAD_GAME, MENU_SETTINGS,
            MENU_CONTROLS, MENU_QUIT_TO_MENU, MENU_QUIT_GAME,
        ]

    def test_panel_width_accommodates_buttons(self):
        from game.ui.screens.strategy_menu_panel import BUTTON_WIDTH, PANEL_PADDING
        assert PANEL_WIDTH == BUTTON_WIDTH + 2 * PANEL_PADDING

    def test_panel_height_accommodates_buttons(self):
        from game.ui.screens.strategy_menu_panel import (
            BUTTON_HEIGHT, BUTTON_GAP, PANEL_PADDING,
        )
        expected = (
            BUTTON_COUNT * BUTTON_HEIGHT
            + (BUTTON_COUNT + 1) * BUTTON_GAP
            + 2 * PANEL_PADDING
        )
        assert PANEL_HEIGHT == expected

    def test_option_id_strings_are_unique(self):
        option_ids = [oid for _, oid in MENU_BUTTONS]
        assert len(option_ids) == len(set(option_ids))


# --- Button Creation Tests ---

class TestMenuPanelButtonCreation:
    """Verify _create_buttons populates button mapping correctly."""

    @pytest.fixture
    def panel_with_buttons(self):
        """Create a panel and run _create_buttons with mocked UIButton."""
        import pygame
        callback = MagicMock()
        panel, _ = _make_panel(callback)

        # Track created buttons
        created_buttons = []

        def fake_button(*args, **kwargs):
            btn = MagicMock()
            btn._text = kwargs.get('text', '')
            created_buttons.append(btn)
            return btn

        with patch('game.ui.screens.strategy_menu_panel.pygame_gui.elements.UIButton', side_effect=fake_button):
            panel._create_buttons()

        return panel, created_buttons

    def test_creates_six_buttons(self, panel_with_buttons):
        panel, buttons = panel_with_buttons
        assert len(panel._option_buttons) == 6

    def test_button_labels_match(self, panel_with_buttons):
        panel, buttons = panel_with_buttons
        labels = [btn._text for btn in buttons]
        expected = [label for label, _ in MENU_BUTTONS]
        assert labels == expected

    def test_button_option_mapping(self, panel_with_buttons):
        panel, buttons = panel_with_buttons
        option_ids = list(panel._option_buttons.values())
        expected = [oid for _, oid in MENU_BUTTONS]
        assert option_ids == expected


# --- Event Processing Tests ---

class TestMenuPanelEventProcessing:
    """Verify process_event dispatches button presses correctly."""

    @pytest.fixture
    def panel_with_mock_buttons(self):
        """Create a panel with mock buttons in the option mapping."""
        callback = MagicMock()
        panel, _ = _make_panel(callback)

        # Create mock buttons and populate mapping
        buttons = {}
        for label, option_id in MENU_BUTTONS:
            btn = MagicMock()
            btn._text = label
            panel._option_buttons[btn] = option_id
            buttons[option_id] = btn

        return panel, callback, buttons

    def _make_button_event(self, button):
        """Create a mock UI_BUTTON_PRESSED event for the given button."""
        import pygame_gui
        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = button
        return event

    def test_save_game_button_calls_callback(self, panel_with_mock_buttons):
        panel, callback, buttons = panel_with_mock_buttons
        event = self._make_button_event(buttons[MENU_SAVE_GAME])
        result = panel.process_event(event)
        callback.assert_called_once_with(MENU_SAVE_GAME)
        assert result is True

    def test_load_game_button_calls_callback(self, panel_with_mock_buttons):
        panel, callback, buttons = panel_with_mock_buttons
        event = self._make_button_event(buttons[MENU_LOAD_GAME])
        result = panel.process_event(event)
        callback.assert_called_once_with(MENU_LOAD_GAME)
        assert result is True

    def test_settings_button_calls_callback(self, panel_with_mock_buttons):
        panel, callback, buttons = panel_with_mock_buttons
        event = self._make_button_event(buttons[MENU_SETTINGS])
        result = panel.process_event(event)
        callback.assert_called_once_with(MENU_SETTINGS)
        assert result is True

    def test_controls_button_calls_callback(self, panel_with_mock_buttons):
        panel, callback, buttons = panel_with_mock_buttons
        event = self._make_button_event(buttons[MENU_CONTROLS])
        result = panel.process_event(event)
        callback.assert_called_once_with(MENU_CONTROLS)
        assert result is True

    def test_quit_to_menu_button_calls_callback(self, panel_with_mock_buttons):
        panel, callback, buttons = panel_with_mock_buttons
        event = self._make_button_event(buttons[MENU_QUIT_TO_MENU])
        result = panel.process_event(event)
        callback.assert_called_once_with(MENU_QUIT_TO_MENU)
        assert result is True

    def test_quit_game_button_calls_callback(self, panel_with_mock_buttons):
        panel, callback, buttons = panel_with_mock_buttons
        event = self._make_button_event(buttons[MENU_QUIT_GAME])
        result = panel.process_event(event)
        callback.assert_called_once_with(MENU_QUIT_GAME)
        assert result is True

    def test_unrelated_button_does_not_call_callback(self, panel_with_mock_buttons):
        panel, callback, buttons = panel_with_mock_buttons
        import pygame_gui
        unrelated = MagicMock()
        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = unrelated
        # Should fall through to super (which is mocked, so no error)
        panel.process_event(event)
        callback.assert_not_called()

    def test_non_button_event_does_not_call_callback(self, panel_with_mock_buttons):
        panel, callback, buttons = panel_with_mock_buttons
        event = MagicMock()
        event.type = 999  # Not UI_BUTTON_PRESSED
        panel.process_event(event)
        callback.assert_not_called()


# --- Accessor Tests ---

class TestMenuPanelAccessors:
    """Verify get_option_buttons returns a copy."""

    def test_get_option_buttons_returns_copy(self):
        panel, _ = _make_panel()
        btn1 = MagicMock()
        panel._option_buttons[btn1] = "test"

        result = panel.get_option_buttons()
        assert result == {btn1: "test"}

        # Modifying returned dict should not affect original
        result[MagicMock()] = "extra"
        assert len(panel._option_buttons) == 1
