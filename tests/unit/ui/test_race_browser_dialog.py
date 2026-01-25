"""
Unit tests for RaceBrowserDialog.

PROJ-12 Phase 4: TDD tests written before extraction.
Tests the race browser dialog functionality.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_race_library():
    """Create a mock RaceLibrary."""
    library = MagicMock()
    library.get_all_races.return_value = []
    return library


@pytest.fixture
def mock_race_config():
    """Create a mock RaceConfig."""
    config = MagicMock()
    config.name = "Test Race"
    config.flag_id = "flag_01"
    config.portrait_id = "portrait_01"
    config.theme_id = "theme_01"
    return config


@pytest.fixture
def mock_ui_manager():
    """Create a mock pygame_gui UIManager."""
    manager = MagicMock()
    return manager


# =============================================================================
# Test: RaceBrowserDialog Creation
# =============================================================================

class TestRaceBrowserDialogCreation:
    """Tests for RaceBrowserDialog initialization."""

    def test_race_browser_dialog_can_be_imported(self):
        """RaceBrowserDialog can be imported from separate module."""
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog

        assert RaceBrowserDialog is not None

    def test_race_browser_dialog_has_preview_constants(self):
        """RaceBrowserDialog has expected preview size constants."""
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog

        assert hasattr(RaceBrowserDialog, 'PREVIEW_SIZE')
        assert hasattr(RaceBrowserDialog, 'ROW_HEIGHT')
        assert RaceBrowserDialog.PREVIEW_SIZE == 60
        assert RaceBrowserDialog.ROW_HEIGHT == 80


# =============================================================================
# Test: Race Selection Logic
# =============================================================================

class TestRaceSelectionLogic:
    """Tests for race selection behavior."""

    def test_select_row_updates_selected_race(self, mock_race_config, mock_race_library):
        """Selecting a row updates selected_race attribute."""
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog

        # Create dialog with mocked pygame dependencies
        with patch.object(RaceBrowserDialog, '__init__', lambda self, *args, **kwargs: None):
            dialog = RaceBrowserDialog.__new__(RaceBrowserDialog)
            dialog.race_rows = []
            dialog.selected_race = None
            dialog.selected_row_index = -1
            dialog.btn_load = MagicMock()

            # Add a mock row
            mock_button = MagicMock()
            mock_row = {
                'race': mock_race_config,
                'index': 0,
                'button': mock_button,
                'elements': []
            }
            dialog.race_rows.append(mock_row)

            # Select the row
            dialog._select_row(0)

            assert dialog.selected_race == mock_race_config
            assert dialog.selected_row_index == 0
            dialog.btn_load.enable.assert_called()

    def test_select_row_deselects_previous(self, mock_race_config, mock_race_library):
        """Selecting a new row deselects the previous one."""
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog

        with patch.object(RaceBrowserDialog, '__init__', lambda self, *args, **kwargs: None):
            dialog = RaceBrowserDialog.__new__(RaceBrowserDialog)
            dialog.race_rows = []
            dialog.selected_race = None
            dialog.selected_row_index = 0  # Previously selected
            dialog.btn_load = MagicMock()

            # Add two mock rows
            mock_button1 = MagicMock()
            mock_button2 = MagicMock()

            dialog.race_rows = [
                {'race': mock_race_config, 'index': 0, 'button': mock_button1, 'elements': []},
                {'race': MagicMock(), 'index': 1, 'button': mock_button2, 'elements': []}
            ]

            # Select second row
            dialog._select_row(1)

            mock_button1.unselect.assert_called()
            mock_button2.select.assert_called()

    def test_select_invalid_row_disables_load(self, mock_race_library):
        """Selecting an invalid row index disables load button."""
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog

        with patch.object(RaceBrowserDialog, '__init__', lambda self, *args, **kwargs: None):
            dialog = RaceBrowserDialog.__new__(RaceBrowserDialog)
            dialog.race_rows = []
            dialog.selected_race = MagicMock()
            dialog.selected_row_index = 0
            dialog.btn_load = MagicMock()

            # Select invalid index
            dialog._select_row(-1)

            assert dialog.selected_race is None
            dialog.btn_load.disable.assert_called()


# =============================================================================
# Test: Preview Loading
# =============================================================================

class TestPreviewLoading:
    """Tests for portrait/flag preview loading."""

    def test_load_portrait_preview_returns_none_for_none_id(self):
        """_load_portrait_preview returns None when portrait_id is None."""
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        with patch.object(RaceBrowserDialog, '__init__', lambda self, *args, **kwargs: None):
            dialog = RaceBrowserDialog.__new__(RaceBrowserDialog)
            dialog._asset_loader = RaceAssetLoader()
            dialog.PREVIEW_SIZE = 60

            result = dialog._load_portrait_preview(None)

            assert result is None

    def test_load_flag_preview_returns_none_for_none_id(self):
        """_load_flag_preview returns None when flag_id is None."""
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        with patch.object(RaceBrowserDialog, '__init__', lambda self, *args, **kwargs: None):
            dialog = RaceBrowserDialog.__new__(RaceBrowserDialog)
            dialog._asset_loader = RaceAssetLoader()
            dialog.PREVIEW_SIZE = 60

            result = dialog._load_flag_preview(None)

            assert result is None

    def test_load_portrait_preview_returns_none_for_missing_path(self):
        """_load_portrait_preview returns None when path doesn't exist."""
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog
        from game.ui.screens.race_asset_loader import RaceAssetLoader

        with patch.object(RaceBrowserDialog, '__init__', lambda self, *args, **kwargs: None):
            dialog = RaceBrowserDialog.__new__(RaceBrowserDialog)
            dialog._asset_loader = RaceAssetLoader()
            dialog.PREVIEW_SIZE = 60

            with patch('os.path.exists', return_value=False):
                result = dialog._load_portrait_preview("nonexistent_portrait")

            assert result is None


# =============================================================================
# Test: Callback Handling
# =============================================================================

class TestCallbackHandling:
    """Tests for callback invocation."""

    def test_cancel_callback_invoked_on_cancel_button(self, mock_race_library):
        """Cancel callback is invoked when cancel button pressed."""
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog

        with patch.object(RaceBrowserDialog, '__init__', lambda self, *args, **kwargs: None):
            dialog = RaceBrowserDialog.__new__(RaceBrowserDialog)
            dialog.on_cancel_callback = MagicMock()
            dialog.on_select_callback = MagicMock()
            dialog.btn_cancel = MagicMock()
            dialog.btn_load = MagicMock()
            dialog.race_rows = []
            dialog.selected_race = None
            dialog.kill = MagicMock()

            # Simulate button press event
            event = MagicMock()
            event.type = 32866  # pygame_gui.UI_BUTTON_PRESSED value
            event.ui_element = dialog.btn_cancel

            # Mock the parent process_event
            with patch('pygame_gui.elements.UIWindow.process_event', return_value=False):
                dialog.process_event(event)

            dialog.on_cancel_callback.assert_called_once()

    def test_select_callback_invoked_on_load_button(self, mock_race_config, mock_race_library):
        """Select callback is invoked when load button pressed with selection."""
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog

        with patch.object(RaceBrowserDialog, '__init__', lambda self, *args, **kwargs: None):
            dialog = RaceBrowserDialog.__new__(RaceBrowserDialog)
            dialog.on_cancel_callback = MagicMock()
            dialog.on_select_callback = MagicMock()
            dialog.btn_cancel = MagicMock()
            dialog.btn_load = MagicMock()
            dialog.race_rows = []
            dialog.selected_race = mock_race_config
            dialog.kill = MagicMock()

            # Simulate button press event
            event = MagicMock()
            event.type = 32866  # pygame_gui.UI_BUTTON_PRESSED
            event.ui_element = dialog.btn_load

            with patch('pygame_gui.elements.UIWindow.process_event', return_value=False):
                dialog.process_event(event)

            dialog.on_select_callback.assert_called_once_with(mock_race_config)


# =============================================================================
# Test: Empty Library Handling
# =============================================================================

class TestEmptyLibraryHandling:
    """Tests for handling empty race library."""

    def test_no_races_label_shown_when_library_empty(self, mock_race_library):
        """No races label is shown when library is empty."""
        from game.ui.screens.race_browser_dialog import RaceBrowserDialog

        mock_race_library.get_all_races.return_value = []

        with patch.object(RaceBrowserDialog, '__init__', lambda self, *args, **kwargs: None):
            dialog = RaceBrowserDialog.__new__(RaceBrowserDialog)
            dialog.race_library = mock_race_library
            dialog.race_rows = []
            dialog.no_races_label = MagicMock()
            dialog.scroll_container = MagicMock()

            dialog._load_races()

            dialog.no_races_label.show.assert_called()
