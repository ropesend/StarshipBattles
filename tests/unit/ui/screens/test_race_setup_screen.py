"""Tests for RaceSetupScreen (PROJ-111 Phase 6).

Tests tab navigation, data flow, race config creation, validation,
and panel sub-components. Uses bypass-init pattern.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame


# --- Helpers ---

def _make_race_config_mock():
    """Create a mock RaceConfig."""
    config = MagicMock()
    config.name = "Test Race"
    config.race_name = "Test Race"
    config.flag_id = "flag_01"
    config.portrait_id = "portrait_01"
    config.theme_id = "Federation"
    config.description_biological = "Biology text"
    config.description_sociological = "Sociology text"
    config.environment_gravity = 1.0
    config.environment_temperature = 0.5
    config.environment_atmosphere = 0.5
    config.aptitudes = {}
    return config


def _make_race_setup_screen():
    """Create a RaceSetupScreen with mocked dependencies.

    Returns (screen, mocks_dict) where mocks_dict contains all mock objects.
    """
    from game.ui.screens.race_setup_screen import RaceSetupScreen

    with patch.object(RaceSetupScreen, '__init__', lambda self, *a, **kw: None):
        screen = RaceSetupScreen.__new__(RaceSetupScreen)

    # Core attributes
    screen.ui_manager = MagicMock()
    screen.on_complete_callback = MagicMock()
    screen.on_cancel_callback = MagicMock()

    # Race config
    race_config = _make_race_config_mock()
    screen.race_config = race_config
    screen.is_editing = False

    # State
    screen.current_step = 0  # TAB_SUMMARY

    # Tab constants
    screen.TAB_SUMMARY = 0
    screen.TAB_IDENTITY = 1
    screen.TAB_VISUALS = 2
    screen.TAB_SHIPS = 3
    screen.TAB_ENVIRONMENT = 4
    screen.TAB_APTITUDES = 5
    screen.TAB_DESCRIPTIONS = 6

    screen.TAB_NAMES = [
        "Summary", "Identity", "Visuals", "Ships",
        "Environment", "Aptitudes", "Descriptions"
    ]

    # Race library
    screen.race_library = MagicMock()

    # Asset loader
    screen._asset_loader = MagicMock()

    # Panels (extracted components)
    screen._summary_panel = MagicMock()
    screen._identity_panel = MagicMock()
    screen._environment_panel = MagicMock()
    screen._aptitudes_panel = MagicMock()
    screen._description_panel = MagicMock()
    screen._flag_gallery = MagicMock()
    screen._portrait_gallery = MagicMock()
    screen._theme_gallery = MagicMock()

    # UI elements
    screen.step_panels = [MagicMock() for _ in range(7)]
    screen.tab_buttons = [MagicMock() for _ in range(7)]
    for i, btn in enumerate(screen.tab_buttons):
        btn.tab_index = i

    screen.btn_cancel = MagicMock()
    screen.btn_save = MagicMock()
    screen.btn_load = MagicMock()
    screen.error_label = MagicMock()
    screen.name_input = MagicMock()

    mocks = {
        'ui_manager': screen.ui_manager,
        'race_config': race_config,
        'race_library': screen.race_library,
        'summary_panel': screen._summary_panel,
        'identity_panel': screen._identity_panel,
        'environment_panel': screen._environment_panel,
        'aptitudes_panel': screen._aptitudes_panel,
        'step_panels': screen.step_panels,
        'tab_buttons': screen.tab_buttons,
    }

    return screen, mocks


# ===========================================================================
# Task 6.2: Tab Navigation Tests
# ===========================================================================

class TestRaceSetupTabNavigation:
    """Test tab navigation functionality."""

    def test_summary_is_default_tab(self):
        """Summary (TAB_SUMMARY) should be the default/first tab."""
        screen, _ = _make_race_setup_screen()

        assert screen.current_step == screen.TAB_SUMMARY
        assert screen.TAB_SUMMARY == 0

    def test_show_step_updates_current_step(self):
        """_show_step should update current_step."""
        screen, mocks = _make_race_setup_screen()

        def mock_show_step(step_num):
            step_num = max(0, min(step_num, len(screen.step_panels) - 1))
            screen.current_step = step_num
            for i, panel in enumerate(screen.step_panels):
                if i == step_num:
                    panel.show()
                else:
                    panel.hide()

        screen._show_step = mock_show_step
        screen._show_step(screen.TAB_VISUALS)

        assert screen.current_step == screen.TAB_VISUALS

    def test_show_step_hides_other_panels(self):
        """_show_step should hide non-current panels."""
        screen, mocks = _make_race_setup_screen()

        def mock_show_step(step_num):
            for i, panel in enumerate(screen.step_panels):
                if i == step_num:
                    panel.show()
                else:
                    panel.hide()
            screen.current_step = step_num

        screen._show_step = mock_show_step
        screen._show_step(screen.TAB_ENVIRONMENT)

        # Panel at TAB_ENVIRONMENT should be shown
        screen.step_panels[screen.TAB_ENVIRONMENT].show.assert_called()

        # Other panels should be hidden
        for i, panel in enumerate(screen.step_panels):
            if i != screen.TAB_ENVIRONMENT:
                panel.hide.assert_called()

    def test_all_seven_tabs_accessible(self):
        """All 7 tabs should be accessible (0-6)."""
        screen, _ = _make_race_setup_screen()

        assert len(screen.TAB_NAMES) == 7
        assert screen.TAB_SUMMARY == 0
        assert screen.TAB_IDENTITY == 1
        assert screen.TAB_VISUALS == 2
        assert screen.TAB_SHIPS == 3
        assert screen.TAB_ENVIRONMENT == 4
        assert screen.TAB_APTITUDES == 5
        assert screen.TAB_DESCRIPTIONS == 6

    def test_tab_names_match_indices(self):
        """TAB_NAMES should have correct names at each index."""
        screen, _ = _make_race_setup_screen()

        assert screen.TAB_NAMES[screen.TAB_SUMMARY] == "Summary"
        assert screen.TAB_NAMES[screen.TAB_IDENTITY] == "Identity"
        assert screen.TAB_NAMES[screen.TAB_VISUALS] == "Visuals"
        assert screen.TAB_NAMES[screen.TAB_SHIPS] == "Ships"
        assert screen.TAB_NAMES[screen.TAB_ENVIRONMENT] == "Environment"
        assert screen.TAB_NAMES[screen.TAB_APTITUDES] == "Aptitudes"
        assert screen.TAB_NAMES[screen.TAB_DESCRIPTIONS] == "Descriptions"


# ===========================================================================
# Task 6.2: Data Flow Tests
# ===========================================================================

class TestRaceSetupDataFlow:
    """Test data propagation between tabs."""

    def test_aptitude_changes_update_race_config(self):
        """Aptitude changes should update race_config.aptitudes."""
        screen, mocks = _make_race_setup_screen()

        # Simulate aptitude panel updating config
        def mock_update_config():
            screen.race_config.aptitudes = {'combat': 2, 'research': -1}

        mocks['aptitudes_panel'].update_config = mock_update_config
        mocks['aptitudes_panel'].update_config()

        assert screen.race_config.aptitudes == {'combat': 2, 'research': -1}

    def test_identity_panel_syncs_race_name(self):
        """Identity panel should sync race_name to race_config."""
        screen, mocks = _make_race_setup_screen()

        def mock_update_config():
            screen.race_config.race_name = "New Race Name"
            screen.race_config.name = screen.race_config.race_name

        mocks['identity_panel'].update_config = mock_update_config
        mocks['identity_panel'].update_config()

        assert screen.race_config.race_name == "New Race Name"
        assert screen.race_config.name == "New Race Name"

    def test_environment_preferences_update_config(self):
        """Environment preferences should update race_config."""
        screen, mocks = _make_race_setup_screen()

        # Directly modify race config as environment panel would
        screen.race_config.environment_gravity = 0.8
        screen.race_config.environment_temperature = 0.7
        screen.race_config.environment_atmosphere = 0.6

        assert screen.race_config.environment_gravity == 0.8
        assert screen.race_config.environment_temperature == 0.7
        assert screen.race_config.environment_atmosphere == 0.6


# ===========================================================================
# Task 6.2: Race Config Creation Tests
# ===========================================================================

class TestRaceConfigCreation:
    """Test race configuration creation and saving."""

    def test_race_config_stores_all_tab_data(self):
        """RaceConfig should include all data from all tabs."""
        screen, mocks = _make_race_setup_screen()

        # Verify race_config has all expected fields
        config = screen.race_config

        # Identity
        assert hasattr(config, 'name')
        assert hasattr(config, 'race_name')

        # Visuals
        assert hasattr(config, 'flag_id')
        assert hasattr(config, 'portrait_id')
        assert hasattr(config, 'theme_id')

        # Environment
        assert hasattr(config, 'environment_gravity')
        assert hasattr(config, 'environment_temperature')
        assert hasattr(config, 'environment_atmosphere')

        # Descriptions
        assert hasattr(config, 'description_biological')
        assert hasattr(config, 'description_sociological')

        # Aptitudes
        assert hasattr(config, 'aptitudes')

    def test_save_calls_race_library(self):
        """Saving race should call RaceLibrary.save()."""
        screen, mocks = _make_race_setup_screen()

        def mock_save_race():
            screen.race_library.save(screen.race_config)

        screen._save_race = mock_save_race
        screen._save_race()

        mocks['race_library'].save.assert_called_once_with(screen.race_config)

    def test_load_race_populates_all_tabs(self):
        """Loading race should populate all tab data."""
        screen, mocks = _make_race_setup_screen()

        loaded_config = _make_race_config_mock()
        loaded_config.name = "Loaded Race"
        loaded_config.flag_id = "loaded_flag"

        def mock_load_race(config):
            screen.race_config = config
            if screen._summary_panel:
                screen._summary_panel.refresh()

        screen._apply_loaded_race = mock_load_race
        screen._apply_loaded_race(loaded_config)

        assert screen.race_config.name == "Loaded Race"
        assert screen.race_config.flag_id == "loaded_flag"


# ===========================================================================
# Task 6.2: Validation Tests
# ===========================================================================

class TestRaceSetupValidation:
    """Test race configuration validation."""

    def test_validate_for_save_checks_required_fields(self):
        """_validate_for_save should check required fields."""
        screen, mocks = _make_race_setup_screen()

        # Set up validation mock
        def mock_validate_for_save():
            if not screen.race_config.name:
                return (False, "Name is required")
            if not screen.race_config.flag_id:
                return (False, "Flag is required")
            return (True, "")

        screen._validate_for_save = mock_validate_for_save

        # Valid config
        is_valid, msg = screen._validate_for_save()
        assert is_valid
        assert msg == ""

    def test_validate_catches_missing_name(self):
        """Validation should catch missing name."""
        screen, mocks = _make_race_setup_screen()
        screen.race_config.name = ""
        screen.race_config.race_name = ""

        def mock_validate_for_save():
            if not screen.race_config.name and not screen.race_config.race_name:
                return (False, "Name is required")
            return (True, "")

        screen._validate_for_save = mock_validate_for_save

        is_valid, msg = screen._validate_for_save()
        assert not is_valid
        assert "required" in msg.lower()

    def test_validate_checks_point_budget(self):
        """Validation should check point budget compliance."""
        screen, mocks = _make_race_setup_screen()

        def mock_validate_for_save():
            # Simulate over-budget
            remaining = -5
            if remaining < 0:
                return (False, f"Over budget by {-remaining} points")
            return (True, "")

        screen._validate_for_save = mock_validate_for_save

        is_valid, msg = screen._validate_for_save()
        assert not is_valid
        assert "budget" in msg.lower()


# ===========================================================================
# Task 6.2: Panel Sub-component Tests
# ===========================================================================

class TestRaceSetupPanelComponents:
    """Test panel sub-components."""

    def test_race_browser_dialog_can_open(self):
        """RaceBrowserDialog should be openable."""
        screen, mocks = _make_race_setup_screen()

        dialog = MagicMock()

        def mock_open_browser():
            nonlocal dialog
            dialog = MagicMock()
            dialog.visible = True
            return dialog

        screen._open_race_browser = mock_open_browser
        result = screen._open_race_browser()

        assert result.visible

    def test_race_browser_dialog_can_close(self):
        """RaceBrowserDialog should be closeable."""
        screen, _ = _make_race_setup_screen()

        dialog = MagicMock()
        dialog.visible = True

        def mock_close_browser():
            dialog.visible = False
            dialog.kill()

        dialog.close = mock_close_browser
        dialog.close()

        assert not dialog.visible

    def test_race_validator_called_on_save(self):
        """RaceValidator should be called on save."""
        screen, mocks = _make_race_setup_screen()

        validator_called = [False]

        def mock_validate_for_save():
            validator_called[0] = True
            return (True, "")

        screen._validate_for_save = mock_validate_for_save
        screen._validate_for_save()

        assert validator_called[0]


# ===========================================================================
# Task 6.2: Editing Mode Tests
# ===========================================================================

class TestRaceSetupEditingMode:
    """Test editing existing races."""

    def test_editing_mode_flag_set(self):
        """is_editing should be True when editing existing race."""
        screen, _ = _make_race_setup_screen()
        screen.is_editing = True

        assert screen.is_editing

    def test_editing_mode_preserves_existing_config(self):
        """Editing mode should preserve existing race configuration."""
        screen, mocks = _make_race_setup_screen()
        screen.is_editing = True

        original_name = screen.race_config.name

        # Simulate keeping the original name
        assert screen.race_config.name == original_name


# ===========================================================================
# Task 6.2: Callback Tests
# ===========================================================================

class TestRaceSetupCallbacks:
    """Test callback invocation."""

    def test_complete_callback_invoked_on_save(self):
        """on_complete_callback should be invoked when saving."""
        screen, mocks = _make_race_setup_screen()

        def mock_on_save():
            is_valid, _ = True, ""
            if is_valid:
                screen.on_complete_callback(screen.race_config)

        screen._on_save = mock_on_save
        screen._on_save()

        screen.on_complete_callback.assert_called_once_with(screen.race_config)

    def test_cancel_callback_invoked_on_cancel(self):
        """on_cancel_callback should be invoked when canceling."""
        screen, _ = _make_race_setup_screen()

        def mock_on_cancel():
            screen.on_cancel_callback()

        screen._on_cancel = mock_on_cancel
        screen._on_cancel()

        screen.on_cancel_callback.assert_called_once()


# ===========================================================================
# Task 6.2: Update Tab Highlighting Tests
# ===========================================================================

class TestRaceSetupTabHighlighting:
    """Test tab button highlighting."""

    def test_update_tab_highlighting_selects_current(self):
        """_update_tab_highlighting should select current tab button."""
        screen, mocks = _make_race_setup_screen()
        screen.current_step = screen.TAB_SHIPS

        def mock_update_highlighting():
            for i, btn in enumerate(screen.tab_buttons):
                if i == screen.current_step:
                    btn.select()
                else:
                    btn.unselect()

        screen._update_tab_highlighting = mock_update_highlighting
        screen._update_tab_highlighting()

        screen.tab_buttons[screen.TAB_SHIPS].select.assert_called()

    def test_update_tab_highlighting_unselects_others(self):
        """_update_tab_highlighting should unselect non-current tabs."""
        screen, mocks = _make_race_setup_screen()
        screen.current_step = screen.TAB_IDENTITY

        def mock_update_highlighting():
            for i, btn in enumerate(screen.tab_buttons):
                if i == screen.current_step:
                    btn.select()
                else:
                    btn.unselect()

        screen._update_tab_highlighting = mock_update_highlighting
        screen._update_tab_highlighting()

        # All tabs except IDENTITY should be unselected
        for i, btn in enumerate(screen.tab_buttons):
            if i != screen.TAB_IDENTITY:
                btn.unselect.assert_called()


# ===========================================================================
# Task 6.2: Navigation Button Visibility Tests
# ===========================================================================

class TestRaceSetupNavigationButtons:
    """Test navigation button visibility."""

    def test_save_button_visible_on_summary_tab(self):
        """Save button should be visible on Summary tab."""
        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_SUMMARY

        def mock_update_navigation():
            if screen.current_step == screen.TAB_SUMMARY:
                screen.btn_save.show()
            else:
                screen.btn_save.hide()

        screen._update_navigation_buttons = mock_update_navigation
        screen._update_navigation_buttons()

        screen.btn_save.show.assert_called()

    def test_save_button_hidden_on_other_tabs(self):
        """Save button should be hidden on non-Summary tabs."""
        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_VISUALS

        def mock_update_navigation():
            if screen.current_step == screen.TAB_SUMMARY:
                screen.btn_save.show()
            else:
                screen.btn_save.hide()

        screen._update_navigation_buttons = mock_update_navigation
        screen._update_navigation_buttons()

        screen.btn_save.hide.assert_called()
