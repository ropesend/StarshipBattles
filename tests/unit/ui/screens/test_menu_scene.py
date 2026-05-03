"""Tests for MenuScene main menu functionality.

PROJ-111 Phase 3 Task 3.3: MenuScene Tests

Uses bypass-init pattern to avoid pygame_gui initialization issues.
Note: These tests patch at the target module level to avoid cross-worker
contamination in parallel test execution.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock


class TestMenuScene:
    """Tests for MenuScene initialization and behavior."""

    @pytest.fixture
    def mock_scene_class(self):
        """Create MenuScene with mocked dependencies."""
        mock_ui_manager = MagicMock()
        created_buttons = []

        def mock_button_init(*args, **kwargs):
            btn = MagicMock()
            btn.kill = MagicMock()
            created_buttons.append(btn)
            return btn

        mock_ui_button_class = MagicMock(side_effect=mock_button_init)

        with patch('game.ui.screens.menu_scene.pygame_gui.UIManager', return_value=mock_ui_manager):
            with patch('game.ui.screens.menu_scene.UIButton', mock_ui_button_class):
                with patch('game.ui.screens.menu_scene.os.path.exists', return_value=False):
                    from game.ui.screens.menu_scene import MenuScene
                    yield MenuScene, mock_ui_manager, created_buttons

    def test_init_creates_correct_number_of_buttons_from_config(self, mock_scene_class):
        """Test initialization creates correct number of buttons from config."""
        MenuScene, mock_ui_manager, created_buttons = mock_scene_class
        callback1 = MagicMock()
        callback2 = MagicMock()
        callback3 = MagicMock()

        button_config = [
            ("New Game", callback1),
            ("Load Game", callback2),
            ("Settings", callback3),
        ]

        created_buttons.clear()
        scene = MenuScene(800, 600, button_config)

        assert len(scene.buttons) == 3

    def test_button_click_dispatches_to_correct_callback(self, mock_scene_class):
        """Test button click dispatches to correct callback."""
        MenuScene, _, created_buttons = mock_scene_class

        # Import pygame_gui here to get the constant
        import pygame_gui

        callback1 = MagicMock()
        callback2 = MagicMock()

        button_config = [
            ("Button1", callback1),
            ("Button2", callback2),
        ]

        created_buttons.clear()
        scene = MenuScene(800, 600, button_config)

        # Get the button that was created for Button1
        button1 = scene.buttons[0]

        # Simulate button press event
        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = button1

        scene.handle_event(event)

        callback1.assert_called_once()
        callback2.assert_not_called()

    def test_handle_event_passes_events_to_ui_manager(self, mock_scene_class):
        """Test handle_event() passes events to UIManager."""
        MenuScene, mock_ui_manager, _ = mock_scene_class
        button_config = [("Test", MagicMock())]
        scene = MenuScene(800, 600, button_config)

        event = MagicMock()
        event.type = 12345  # Some other event type

        scene.handle_event(event)

        scene.ui_manager.process_events.assert_called_with(event)

    def test_update_calls_ui_manager_update(self, mock_scene_class):
        """Test update() calls UIManager.update()."""
        MenuScene, _, _ = mock_scene_class
        button_config = [("Test", MagicMock())]
        scene = MenuScene(800, 600, button_config)

        scene.update(0.016)

        scene.ui_manager.update.assert_called_with(0.016)

    def test_draw_fills_background_and_draws_ui(self, mock_scene_class):
        """Test draw() fills background and calls UIManager.draw_ui()."""
        MenuScene, _, _ = mock_scene_class
        button_config = [("Test", MagicMock())]
        scene = MenuScene(800, 600, button_config)

        mock_screen = MagicMock()
        scene.draw(mock_screen)

        mock_screen.fill.assert_called_with(MenuScene.BG_COLOR)
        scene.ui_manager.draw_ui.assert_called_with(mock_screen)

    def test_empty_button_config_initializes_without_error(self, mock_scene_class):
        """Test empty button_config (0 buttons) initializes without error."""
        MenuScene, _, _ = mock_scene_class
        button_config = []

        scene = MenuScene(800, 600, button_config)

        assert len(scene.buttons) == 0
        assert len(scene._button_callbacks) == 0

    def test_button_config_with_single_button(self, mock_scene_class):
        """Test button_config with single button."""
        MenuScene, _, _ = mock_scene_class
        callback = MagicMock()
        button_config = [("Single Button", callback)]

        scene = MenuScene(800, 600, button_config)

        assert len(scene.buttons) == 1
        assert len(scene._button_callbacks) == 1

    def test_handle_resize_updates_dimensions(self, mock_scene_class):
        """Test handle_resize() updates width and height."""
        MenuScene, _, _ = mock_scene_class
        button_config = [("Test", MagicMock())]
        scene = MenuScene(800, 600, button_config)

        scene.handle_resize(1920, 1080)

        assert scene.width == 1920
        assert scene.height == 1080
        scene.ui_manager.set_window_resolution.assert_called_with((1920, 1080))

    def test_handle_resize_recreates_buttons(self, mock_scene_class):
        """Test handle_resize() recreates buttons for new layout."""
        MenuScene, _, created_buttons = mock_scene_class
        callback = MagicMock()
        button_config = [("Test", callback)]

        created_buttons.clear()
        scene = MenuScene(800, 600, button_config)

        # Old buttons should be killed
        old_buttons = scene.buttons.copy()
        initial_button_count = len(old_buttons)

        scene.handle_resize(1920, 1080)

        # Old buttons should have been killed
        for btn in old_buttons:
            btn.kill.assert_called()

        # New buttons should be created (same count for same config)
        assert len(scene.buttons) == initial_button_count

    def test_get_ui_manager_returns_manager(self, mock_scene_class):
        """Test get_ui_manager() returns the UI manager."""
        MenuScene, _, _ = mock_scene_class
        button_config = [("Test", MagicMock())]
        scene = MenuScene(800, 600, button_config)

        manager = scene.get_ui_manager()

        assert manager == scene.ui_manager

    def test_button_callbacks_dictionary_mapping(self, mock_scene_class):
        """Test _button_callbacks maps buttons to callbacks correctly."""
        MenuScene, _, _ = mock_scene_class
        callback1 = MagicMock()
        callback2 = MagicMock()
        button_config = [
            ("First", callback1),
            ("Second", callback2),
        ]

        scene = MenuScene(800, 600, button_config)

        # Verify callbacks are stored
        assert len(scene._button_callbacks) == 2

        # Each button should map to its callback
        for i, btn in enumerate(scene.buttons):
            assert btn in scene._button_callbacks
            assert scene._button_callbacks[btn] == button_config[i][1]

    def test_button_click_unknown_element_no_error(self, mock_scene_class):
        """Test button click with unknown element doesn't crash."""
        MenuScene, _, _ = mock_scene_class
        import pygame_gui

        button_config = [("Test", MagicMock())]
        scene = MenuScene(800, 600, button_config)

        # Event with unknown element
        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = MagicMock()  # Unknown element

        # Should not raise
        scene.handle_event(event)


class TestMenuSceneConstants:
    """Tests for MenuScene constants and defaults."""

    @pytest.fixture
    def mock_scene_class(self):
        """Create MenuScene with mocked dependencies."""
        mock_ui_manager = MagicMock()

        with patch('game.ui.screens.menu_scene.pygame_gui.UIManager', return_value=mock_ui_manager):
            with patch('game.ui.screens.menu_scene.UIButton', MagicMock()):
                with patch('game.ui.screens.menu_scene.os.path.exists', return_value=False):
                    from game.ui.screens.menu_scene import MenuScene
                    yield MenuScene

    def test_stores_width_and_height(self, mock_scene_class):
        """Test scene stores width and height."""
        MenuScene = mock_scene_class
        scene = MenuScene(1024, 768, [])

        assert scene.width == 1024
        assert scene.height == 768

    def test_stores_button_config(self, mock_scene_class):
        """Test scene stores button_config."""
        MenuScene = mock_scene_class
        button_config = [("A", MagicMock()), ("B", MagicMock())]
        scene = MenuScene(800, 600, button_config)

        assert scene.button_config == button_config
