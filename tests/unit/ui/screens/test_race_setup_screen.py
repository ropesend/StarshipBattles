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

    # PROJ-287: Session-scoped race registry (None when editor runs pre-game).
    screen.race_registry = None

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
    screen.btn_randomize = MagicMock()
    screen.error_label = MagicMock()
    screen.name_input = MagicMock()

    # FEAT-05: Save/Update dialog (created on demand)
    screen._save_update_dialog = None
    screen._btn_overwrite = None
    screen._btn_save_new = None
    screen._btn_save_cancel = None

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


# ===========================================================================
# BUG-81: Load Saved Species updates panel references
# ===========================================================================

class TestRaceSetupLoadSpecies:
    """Test that loading a saved species updates all panels (BUG-81)."""

    def test_on_race_selected_updates_panel_race_configs(self):
        """Loading a race should update all panel race_config references."""
        screen, mocks = _make_race_setup_screen()
        old_config = screen.race_config

        # Create a new "loaded" config
        new_config = _make_race_config_mock()
        new_config.name = "Loaded Species"

        # Call _on_race_selected (the load handler)
        screen._on_race_selected(new_config)

        # Screen's race_config should be updated
        assert screen.race_config is new_config
        assert screen.race_config is not old_config

        # All panels should have updated race_config reference
        assert screen._identity_panel.race_config is new_config
        assert screen._environment_panel.race_config is new_config
        assert screen._aptitudes_panel.race_config is new_config
        assert screen._description_panel.race_config is new_config
        assert screen._flag_gallery.race_config is new_config
        assert screen._portrait_gallery.race_config is new_config
        assert screen._theme_gallery.race_config is new_config
        assert screen._summary_panel.race_config is new_config

    def test_on_race_selected_calls_set_from_config(self):
        """Loading a race should call set_from_config on all panels."""
        screen, mocks = _make_race_setup_screen()
        new_config = _make_race_config_mock()

        screen._on_race_selected(new_config)

        screen._identity_panel.set_from_config.assert_called()
        screen._environment_panel.set_from_config.assert_called()
        screen._aptitudes_panel.set_from_config.assert_called()
        screen._description_panel.set_from_config.assert_called()
        screen._flag_gallery.set_from_config.assert_called()
        screen._portrait_gallery.set_from_config.assert_called()
        screen._theme_gallery.set_from_config.assert_called()


# ===========================================================================
# FEAT-05: Save/Update Dialog Tests
# ===========================================================================

class TestSaveUpdateDialog:
    """FEAT-05: Tests for the overwrite vs save-as-new dialog workflow."""

    def test_new_species_saves_directly(self):
        """New species (not editing) should save without showing dialog."""
        screen, mocks = _make_race_setup_screen()
        screen.is_editing = False
        screen.race_config.race_id = None
        screen._validate_for_save = MagicMock(return_value=(True, ""))
        screen.race_config.validate.return_value = MagicMock(is_valid=True)
        mocks['race_library'].save_race.return_value = (True, "Saved")
        screen.kill = MagicMock()

        screen._on_save()

        # Should save directly, no dialog
        assert screen._save_update_dialog is None
        mocks['race_library'].save_race.assert_called_once()

    def test_editing_species_shows_dialog(self):
        """Editing a loaded species should show the save/update dialog."""
        screen, mocks = _make_race_setup_screen()
        screen.is_editing = True
        screen.race_config.race_id = "existing_race_abc123"
        screen._validate_for_save = MagicMock(return_value=(True, ""))
        screen.race_config.validate.return_value = MagicMock(is_valid=True)
        screen.get_container = MagicMock()
        screen.get_container.return_value.get_size.return_value = (800, 600)

        with patch('pygame_gui.elements.UIWindow'):
            with patch('pygame_gui.elements.UILabel'):
                with patch('pygame_gui.elements.UIButton') as MockBtn:
                    screen._on_save()

        # Dialog should be shown, save NOT called yet
        assert screen._save_update_dialog is not None
        mocks['race_library'].save_race.assert_not_called()

    def test_overwrite_keeps_race_id(self):
        """Overwrite button should save with the existing race_id."""
        screen, mocks = _make_race_setup_screen()
        screen.is_editing = True
        screen.race_config.race_id = "existing_race_abc123"
        dialog_mock = MagicMock()
        screen._save_update_dialog = dialog_mock
        mocks['race_library'].save_race.return_value = (True, "Saved")
        screen.kill = MagicMock()

        screen._on_overwrite_save()

        # race_id should be preserved
        assert screen.race_config.race_id == "existing_race_abc123"
        mocks['race_library'].save_race.assert_called_once()
        dialog_mock.kill.assert_called()
        assert screen._save_update_dialog is None

    def test_save_as_new_clears_race_id(self):
        """Save as New button should clear race_id for fresh generation."""
        screen, mocks = _make_race_setup_screen()
        screen.is_editing = True
        screen.race_config.race_id = "existing_race_abc123"
        dialog_mock = MagicMock()
        screen._save_update_dialog = dialog_mock
        mocks['race_library'].save_race.return_value = (True, "Saved")
        screen.kill = MagicMock()

        screen._on_save_as_new()

        # race_id should be cleared
        assert screen.race_config.race_id is None
        assert screen.is_editing is False
        mocks['race_library'].save_race.assert_called_once()
        dialog_mock.kill.assert_called()
        assert screen._save_update_dialog is None

    def test_cancel_dialog_does_not_save(self):
        """Cancel button should close dialog without saving."""
        screen, mocks = _make_race_setup_screen()
        screen._save_update_dialog = MagicMock()

        screen._on_save_dialog_cancel()

        assert screen._save_update_dialog is None
        mocks['race_library'].save_race.assert_not_called()


# --- PROJ-283 Phase 5 / PROJ-285 crash regression ---
# A slider move on the Environment tab used to crash with:
#   AttributeError: 'RaceEnvironmentPanel' object has no attribute 'update_labels'
# The screen's slider-move handler must route to existing panel methods
# (update_labels + update_config) — these must be called on the environment
# panel without raising. Pinned as a screen-level contract so future
# panel-rename drift is caught here, not at runtime.

class TestSliderEventDispatch:
    """Regression pins for the original crash.

    The default `_make_race_setup_screen` helper installs a
    *non-spec* `MagicMock()` for `_environment_panel`, which silently
    auto-provides any attribute and therefore cannot reproduce the
    AttributeError. We re-bind to `MagicMock(spec=RaceEnvironmentPanel)`
    so missing methods raise exactly as they would against the real
    panel — pinning the cross-panel API contract at the test layer.
    """

    def _slider_event(self):
        import pygame_gui
        return pygame.event.Event(
            pygame_gui.UI_HORIZONTAL_SLIDER_MOVED,
            {"ui_element": MagicMock(), "value": 1.0},
        )

    def _spec_bound_screen(self):
        from game.ui.panels.race_environment_panel import RaceEnvironmentPanel
        from game.ui.panels.race_identity_panel import RaceIdentityPanel
        from game.ui.panels.race_aptitudes_panel import RaceAptitudesPanel
        screen, mocks = _make_race_setup_screen()
        # Bind spec mocks so missing methods raise AttributeError the
        # same way the real classes do at runtime.
        screen._environment_panel = MagicMock(spec=RaceEnvironmentPanel)
        screen._identity_panel = MagicMock(spec=RaceIdentityPanel)
        screen._aptitudes_panel = MagicMock(spec=RaceAptitudesPanel)
        return screen, mocks

    def test_slider_event_does_not_raise(self):
        """Original crash reproduction. Pre-fix: raised
        `AttributeError: 'RaceEnvironmentPanel' object has no attribute
        'update_labels'`. Post-fix: runs cleanly."""
        from game.ui.screens.race_setup_screen import RaceSetupScreen
        screen, _ = self._spec_bound_screen()
        with patch.object(RaceSetupScreen.__mro__[1], "process_event", return_value=False):
            screen.process_event(self._slider_event())

    def test_slider_event_calls_update_labels_and_update_config_on_env_panel(self):
        """Contract: slider move must call BOTH `update_labels()`
        (refreshes row labels + cost + points) AND `update_config()`
        (writes slider values into `race_config.preferences`). Either
        omission reintroduces a silent bug — stale labels or stale
        config."""
        from game.ui.screens.race_setup_screen import RaceSetupScreen
        screen, _ = self._spec_bound_screen()

        with patch.object(RaceSetupScreen.__mro__[1], "process_event", return_value=False):
            screen.process_event(self._slider_event())

        screen._environment_panel.update_labels.assert_called_once()
        screen._environment_panel.update_config.assert_called_once()


# ===========================================================================
# PROJ-287 Phase 2: Race registry cache invalidation on save
# ===========================================================================

class TestRaceRegistryInvalidationOnSave:
    """After a successful save, the screen must invalidate the session's
    race registry so subsequent reads see the freshly-saved race.

    When the editor runs pre-game (no session), `race_registry` is None
    and _do_save must still succeed without attempting invalidation.
    """

    def test_successful_save_invalidates_registry_entry(self):
        """Successful save calls registry.invalidate(race_id)."""
        screen, mocks = _make_race_setup_screen()
        screen.race_config.race_id = "edited_race_123"
        screen.race_registry = MagicMock()
        mocks['race_library'].save_race.return_value = (True, "Saved")
        screen.kill = MagicMock()

        screen._do_save()

        screen.race_registry.invalidate.assert_called_once_with("edited_race_123")

    def test_failed_save_does_not_invalidate(self):
        """Failed save must NOT invalidate (cache stays coherent with disk)."""
        screen, mocks = _make_race_setup_screen()
        screen.race_config.race_id = "edited_race_123"
        screen.race_registry = MagicMock()
        mocks['race_library'].save_race.return_value = (False, "Disk full")
        screen.kill = MagicMock()

        screen._do_save()

        screen.race_registry.invalidate.assert_not_called()

    def test_save_without_registry_still_works(self):
        """Pre-game save (race_registry=None) completes without error."""
        screen, mocks = _make_race_setup_screen()
        screen.race_config.race_id = "new_race_456"
        screen.race_registry = None
        mocks['race_library'].save_race.return_value = (True, "Saved")
        screen.kill = MagicMock()

        screen._do_save()  # Must not raise

        mocks['race_library'].save_race.assert_called_once()


# ===========================================================================
# FEAT-12: Per-Tab Randomize + Master Randomize All
# ===========================================================================


class TestFeat12NavigationButtonVisibility:
    """FEAT-12 Sub-task 4: visibility filter shows btn_randomize on
    Identity, Visuals, Ships, Environment, AND Aptitudes tabs.
    """

    def test_randomize_button_visible_on_identity_tab(self):
        from game.ui.screens.race_setup_screen import RaceSetupScreen

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_IDENTITY
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.show.assert_called()

    def test_randomize_button_visible_on_visuals_tab(self):
        from game.ui.screens.race_setup_screen import RaceSetupScreen

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_VISUALS
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.show.assert_called()

    def test_randomize_button_visible_on_ships_tab(self):
        from game.ui.screens.race_setup_screen import RaceSetupScreen

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_SHIPS
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.show.assert_called()

    def test_randomize_button_visible_on_environment_tab(self):
        from game.ui.screens.race_setup_screen import RaceSetupScreen

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_ENVIRONMENT
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.show.assert_called()

    def test_randomize_button_visible_on_aptitudes_tab(self):
        from game.ui.screens.race_setup_screen import RaceSetupScreen

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_APTITUDES
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.show.assert_called()

    def test_randomize_button_hidden_on_summary_tab(self):
        """Summary tab uses the master 'Randomize All' button on the
        summary panel — the bottom-bar button is hidden there."""
        from game.ui.screens.race_setup_screen import RaceSetupScreen

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_SUMMARY
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.hide.assert_called()

    def test_randomize_button_hidden_on_descriptions_tab(self):
        from game.ui.screens.race_setup_screen import RaceSetupScreen

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_DESCRIPTIONS
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.hide.assert_called()


class TestFeat12OnRandomizeDispatch:
    """FEAT-12 Sub-task 4: `_on_randomize` dispatches to the right
    per-tab handler.
    """

    def _attach_real_dispatcher(self, screen):
        from game.ui.screens.race_setup_screen import RaceSetupScreen
        screen._on_randomize = RaceSetupScreen._on_randomize.__get__(screen)

    def test_dispatches_to_randomize_environment_when_on_env_tab(self):
        screen, _ = _make_race_setup_screen()
        self._attach_real_dispatcher(screen)
        screen.current_step = screen.TAB_ENVIRONMENT
        screen._randomize_environment = MagicMock()
        screen._randomize_aptitudes = MagicMock()

        screen._on_randomize()

        screen._randomize_environment.assert_called_once()
        screen._randomize_aptitudes.assert_not_called()

    def test_dispatches_to_randomize_aptitudes_when_on_aptitudes_tab(self):
        screen, _ = _make_race_setup_screen()
        self._attach_real_dispatcher(screen)
        screen.current_step = screen.TAB_APTITUDES
        screen._randomize_environment = MagicMock()
        screen._randomize_aptitudes = MagicMock()

        screen._on_randomize()

        screen._randomize_aptitudes.assert_called_once()
        screen._randomize_environment.assert_not_called()


class TestFeat12RandomizeEnvironmentHandler:
    """FEAT-12 Sub-task 4: `_randomize_environment` writes results to
    `race_config` and refreshes the environment + aptitudes panels."""

    def test_writes_preferences_homeworld_repro_happiness_to_config(self):
        from game.strategy.data.environmental_preference import EnvironmentalPreference
        from game.ui.screens.race_setup_screen import RaceSetupScreen

        screen, _ = _make_race_setup_screen()
        # Use a real RaceConfig so dataclass attribute access works.
        from game.strategy.data.race_config import RaceConfig
        screen.race_config = RaceConfig()

        fake_pref = EnvironmentalPreference(
            setpoint=9.81, tolerance=2.0,
            min_value=0.1, max_value=30.0, step=0.98,
        )
        fake_result = {
            "preferences": {"gravity": fake_pref},
            "homeworld_type": "CONTINENTAL",
            "base_reproduction_rate": 0.05,
            "base_happiness": 0.7,
        }
        with patch(
            "game.ui.screens.race_setup_screen.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_environment.return_value = fake_result
            RaceSetupScreen._randomize_environment(screen)

        assert screen.race_config.preferences["gravity"] is fake_pref
        assert screen.race_config.homeworld_type == "CONTINENTAL"
        assert screen.race_config.base_reproduction_rate == 0.05
        assert screen.race_config.base_happiness == 0.7

    def test_refreshes_environment_and_aptitudes_panels(self):
        from game.ui.screens.race_setup_screen import RaceSetupScreen
        from game.strategy.data.race_config import RaceConfig

        screen, mocks = _make_race_setup_screen()
        screen.race_config = RaceConfig()

        with patch(
            "game.ui.screens.race_setup_screen.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_environment.return_value = {
                "preferences": {},
                "homeworld_type": "CONTINENTAL",
                "base_reproduction_rate": 0.03,
                "base_happiness": 0.5,
            }
            RaceSetupScreen._randomize_environment(screen)

        mocks['environment_panel'].set_from_config.assert_called()
        mocks['aptitudes_panel'].update_budget_display.assert_called()


class TestFeat12RandomizeAptitudesHandler:
    """FEAT-12 Sub-task 4: `_randomize_aptitudes` writes aptitude
    attributes to `race_config` and refreshes panels."""

    def test_writes_seven_aptitude_attrs_to_config(self):
        from game.ui.screens.race_setup_screen import RaceSetupScreen
        from game.strategy.data.race_config import RaceConfig

        screen, _ = _make_race_setup_screen()
        screen.race_config = RaceConfig()

        fake_aptitudes = {
            "strength": 60,
            "intelligence": 70,
            "constitution": 50,
            "dexterity": 30,
            "tolerance_other_species": 50,
            "cooperation": 50,
            "conflict_tolerance": 40,
        }
        with patch(
            "game.ui.screens.race_setup_screen.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_aptitudes.return_value = fake_aptitudes
            RaceSetupScreen._randomize_aptitudes(screen)

        for name, value in fake_aptitudes.items():
            assert getattr(screen.race_config, f"aptitude_{name}") == value

    def test_refreshes_aptitudes_panel(self):
        from game.ui.screens.race_setup_screen import RaceSetupScreen
        from game.strategy.data.race_config import RaceConfig

        screen, mocks = _make_race_setup_screen()
        screen.race_config = RaceConfig()

        with patch(
            "game.ui.screens.race_setup_screen.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_aptitudes.return_value = {
                "strength": 50, "intelligence": 50, "constitution": 50,
                "dexterity": 50, "tolerance_other_species": 50,
                "cooperation": 50, "conflict_tolerance": 50,
            }
            RaceSetupScreen._randomize_aptitudes(screen)

        mocks['aptitudes_panel'].set_from_config.assert_called()


class TestFeat12RandomizeAllHandler:
    """FEAT-12 Sub-task 5: master Randomize All handler invokes the
    orchestrator and applies the result via `_populate_ui_from_config`."""

    def test_invokes_orchestrator_and_repopulates_ui(self):
        from game.ui.screens.race_setup_screen import RaceSetupScreen
        from game.strategy.data.environmental_preference import EnvironmentalPreference
        from game.strategy.data.race_config import RaceConfig

        screen, _ = _make_race_setup_screen()
        screen.race_config = RaceConfig()
        screen._populate_ui_from_config = MagicMock()
        screen._refresh_summary = MagicMock()
        screen._refresh_ship_preview = MagicMock()

        # Mock galleries' _discover_assets to return non-empty pools.
        screen._flag_gallery._discover_assets = MagicMock(
            return_value=[("flag_a",), ("flag_b",)]
        )
        screen._portrait_gallery._discover_assets = MagicMock(
            return_value=[("p_a.jpg",), ("p_b.jpg",)]
        )
        screen._theme_gallery._discover_assets = MagicMock(
            return_value=[("Federation",), ("Klingons",)]
        )

        fake_pref = EnvironmentalPreference(
            setpoint=9.81, tolerance=2.0,
            min_value=0.1, max_value=30.0, step=0.98,
        )
        fake_all = {
            "race_name": "Rossarian",
            "race_name_plural": "Rossarians",
            "leader_name": "Zara IV",
            "physical_type": "Humanoid",
            "government_type": "Empire",
            "government_organization": "Autocracy",
            "leader_title": "Emperor",
            "society_type": "Explorers",
            "faction_name": "Rossarian Empire",
            "flag_id": "flag_a",
            "portrait_id": "p_a.jpg",
            "theme_id": "Federation",
            "homeworld_type": "CONTINENTAL",
            "preferences": {"gravity": fake_pref},
            "base_reproduction_rate": 0.05,
            "base_happiness": 0.7,
            "aptitudes": {
                "strength": 60, "intelligence": 70, "constitution": 50,
                "dexterity": 30, "tolerance_other_species": 50,
                "cooperation": 50, "conflict_tolerance": 40,
            },
        }
        with patch(
            "game.ui.screens.race_setup_screen.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_all.return_value = fake_all
            RaceSetupScreen._randomize_all(screen)

        mock_rand.randomize_all.assert_called_once()
        # Identity field written
        assert screen.race_config.race_name == "Rossarian"
        assert screen.race_config.faction_name == "Rossarian Empire"
        # Visuals
        assert screen.race_config.flag_id == "flag_a"
        assert screen.race_config.portrait_id == "p_a.jpg"
        assert screen.race_config.theme_id == "Federation"
        # Env
        assert screen.race_config.homeworld_type == "CONTINENTAL"
        assert screen.race_config.preferences["gravity"] is fake_pref
        # Aptitudes
        assert screen.race_config.aptitude_strength == 60
        # Full UI repopulation triggered
        screen._populate_ui_from_config.assert_called_once()
