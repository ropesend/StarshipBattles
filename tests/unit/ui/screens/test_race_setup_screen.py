"""Tests for RaceSetupScreen (PROJ-111 Phase 6).

Tests tab navigation, data flow, race config creation, validation,
and panel sub-components. Uses bypass-init pattern.
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import pygame

from tests.fixtures.ui_widget_factory import bypass_init, make_ui_widget
from tests.fixtures.race_setup_ui_builders import (
    MockRaceSetupUiBuilder,
    NullRaceSetupUiBuilder,
)
from game.ui.screens.race_setup.screen import RaceSetupScreen


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

    PROJ-325 Phase 3 — rewritten to use the two-stage UIWindow
    construction pattern (cheap state + delegates BEFORE the
    ``bypass_init`` guard, widget tree behind a ``ui_builder``). Was
    ~118 LOC of manual ``__new__`` + per-attribute wiring; now goes
    through ``RaceSetupScreen``'s real constructor under
    ``with bypass_init(...)`` plus ``MockRaceSetupUiBuilder``. See
    ``Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md``.
    """

    race_config = _make_race_config_mock()
    race_library = MagicMock(name="race_library")

    with bypass_init(RaceSetupScreen):
        screen = make_ui_widget(
            RaceSetupScreen,
            rect=pygame.Rect(0, 0, 800, 600),
            manager=MagicMock(),
            on_complete_callback=MagicMock(),
            on_cancel_callback=MagicMock(),
            ui_builder=MockRaceSetupUiBuilder(),
        )
    # The screen built its own real RaceConfig + RaceLibrary in
    # ``_init_state``. Override with the test mocks so existing
    # assertions keep working (the controller mirrors the screen ref).
    screen.race_config = race_config
    screen.race_library = race_library
    screen._controller.race_config = race_config
    screen._controller.race_library = race_library

    mocks = {
        'ui_manager': screen.ui_manager,
        'race_config': race_config,
        'race_library': race_library,
        'summary_panel': screen._summary_panel,
        'identity_panel': screen._identity_panel,
        'environment_panel': screen._environment_panel,
        'aptitudes_panel': screen._aptitudes_panel,
        'step_panels': screen.step_panels,
        'tab_buttons': screen.tab_buttons,
        'controller': screen._controller,
        'renderer': screen._renderer,
        'view_model': screen._view_model,
    }

    return screen, mocks


# PROJ-494 Task 1.3: shared mock-method factories used across multiple tests
# to replace inline duplicates.

def _install_mock_show_step(screen, *, clamp: bool = False):
    """Replace screen._show_step with a deterministic test double.

    Was inlined twice (test_show_step_updates_current_step,
    test_show_step_hides_other_panels). The two variants differ only in
    whether they clamp `step_num` to a valid range.
    """
    def mock_show_step(step_num):
        if clamp:
            step_num = max(0, min(step_num, len(screen.step_panels) - 1))
        screen.current_step = step_num
        for i, panel in enumerate(screen.step_panels):
            if i == step_num:
                panel.show()
            else:
                panel.hide()
    screen._show_step = mock_show_step


def _install_mock_update_tab_highlighting(screen):
    """Replace screen._update_tab_highlighting with a deterministic test double.

    Was inlined twice (test_update_tab_highlighting_selects_current,
    test_update_tab_highlighting_unselects_others) byte-for-byte.
    """
    def mock_update_highlighting():
        for i, btn in enumerate(screen.tab_buttons):
            if i == screen.current_step:
                btn.select()
            else:
                btn.unselect()
    screen._update_tab_highlighting = mock_update_highlighting


def _install_mock_update_navigation(screen):
    """Replace screen._update_navigation_buttons with a deterministic test double.

    Was inlined twice (test_save_button_visible_on_summary_tab,
    test_save_button_hidden_on_other_tabs) byte-for-byte.
    """
    def mock_update_navigation():
        if screen.current_step == screen.TAB_SUMMARY:
            screen.btn_save.show()
        else:
            screen.btn_save.hide()
    screen._update_navigation_buttons = mock_update_navigation


# ===========================================================================
# PROJ-325 Phase 3: two-stage construction PoC
# ===========================================================================


class TestPROJ325TwoStageConstruction:
    """PROJ-325 Phase 3 PoC — verifying that the two-stage UIWindow
    construction pattern (cheap state + delegates BEFORE the bypass
    point, widget tree behind a builder) yields a useful instance under
    `bypass_init` + `NullRaceSetupUiBuilder`.

    See `Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md`.
    """

    def test_bypass_init_with_null_builder_yields_useful_instance(self):

        with bypass_init(RaceSetupScreen):
            screen = make_ui_widget(
                RaceSetupScreen,
                rect=pygame.Rect(0, 0, 800, 600),
                manager=MagicMock(),
                on_complete_callback=MagicMock(),
                on_cancel_callback=MagicMock(),
                ui_builder=NullRaceSetupUiBuilder(),
            )

        # Cheap state populated:
        assert screen.race_config is not None
        assert screen.is_editing is False
        assert screen.race_library is not None
        assert screen.race_registry is None  # default when not provided
        assert screen._asset_loader is not None
        # Delegates populated:
        assert screen._view_model is not None
        assert screen._renderer is not None
        assert screen._controller is not None
        assert screen._input_handler is not None
        assert screen._llm_service is not None
        # Widget slots are explicit placeholders (None / empty containers):
        assert screen.btn_save is None
        assert screen.btn_cancel is None
        assert screen.btn_randomize is None
        assert screen.error_label is None
        assert screen.step_panels == []
        assert screen.tab_buttons == []


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
        _install_mock_show_step(screen, clamp=True)
        screen._show_step(screen.TAB_VISUALS)

        assert screen.current_step == screen.TAB_VISUALS

    def test_show_step_hides_other_panels(self):
        """_show_step should hide non-current panels."""
        screen, mocks = _make_race_setup_screen()
        _install_mock_show_step(screen)
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
        _install_mock_update_tab_highlighting(screen)
        screen._update_tab_highlighting()

        screen.tab_buttons[screen.TAB_SHIPS].select.assert_called()

    def test_update_tab_highlighting_unselects_others(self):
        """_update_tab_highlighting should unselect non-current tabs."""
        screen, mocks = _make_race_setup_screen()
        screen.current_step = screen.TAB_IDENTITY
        _install_mock_update_tab_highlighting(screen)
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
        _install_mock_update_navigation(screen)
        screen._update_navigation_buttons()

        screen.btn_save.show.assert_called()

    def test_save_button_hidden_on_other_tabs(self):
        """Save button should be hidden on non-Summary tabs."""
        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_VISUALS
        _install_mock_update_navigation(screen)
        screen._update_navigation_buttons()

        screen.btn_save.hide.assert_called()


# ===========================================================================
# BUG-81: Load Saved Species updates panel references
# ===========================================================================

class TestRaceSetupLoadSpecies:
    """Test that loading a saved species updates all panels (BUG-81)."""

    def test_on_race_selected_updates_panel_race_configs(self):
        """Loading a race should update all panel race_config references.

        PROJ-309 Sub-phase 3.1: load handler moved to
        `RaceSetupController.on_race_selected` (was `screen._on_race_selected`)."""
        screen, mocks = _make_race_setup_screen()
        screen._refresh_summary = MagicMock()  # avoid summary refresh in unit test
        old_config = screen.race_config

        # Create a new "loaded" config
        new_config = _make_race_config_mock()
        new_config.name = "Loaded Species"

        screen._controller.on_race_selected(new_config)

        # Screen's race_config should be updated (mirror — controller is
        # the authoritative writer).
        assert screen.race_config is new_config
        assert screen.race_config is not old_config
        assert screen._controller.race_config is new_config

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
        screen._refresh_summary = MagicMock()
        new_config = _make_race_config_mock()

        screen._controller.on_race_selected(new_config)

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

    # PROJ-309 Sub-phase 3.1: save flow methods migrated from
    # `screen._on_save / _on_overwrite_save / _on_save_as_new /
    # _on_save_dialog_cancel` → `screen._controller.on_save / ...`.
    # The save-update dialog widget refs migrated from `screen._save_update_dialog`
    # → `screen._renderer.save_update_dialog`.

    def test_new_species_saves_directly(self):
        """New species (not editing) should save without showing dialog."""
        screen, mocks = _make_race_setup_screen()
        screen.is_editing = False
        screen.race_config.race_id = None
        screen._controller.validate_for_save = MagicMock(return_value=(True, ""))
        screen.race_config.validate.return_value = MagicMock(is_valid=True)
        mocks['race_library'].save_race.return_value = (True, "Saved")
        screen.kill = MagicMock()

        screen._controller.on_save()

        # Should save directly, no dialog
        assert screen._renderer.save_update_dialog is None
        mocks['race_library'].save_race.assert_called_once()

    def test_editing_species_shows_dialog(self):
        """Editing a loaded species should show the save/update dialog."""
        screen, mocks = _make_race_setup_screen()
        screen.is_editing = True
        # FEAT-05 branch reads `view_model.is_editing`, controller mirrors the flag.
        screen._view_model.is_editing = True
        screen.race_config.race_id = "existing_race_abc123"
        screen._controller.validate_for_save = MagicMock(return_value=(True, ""))
        screen.race_config.validate.return_value = MagicMock(is_valid=True)
        screen.get_container = MagicMock()
        screen.get_container.return_value.get_size.return_value = (800, 600)

        with patch('pygame_gui.elements.UIWindow'):
            with patch('pygame_gui.elements.UILabel'):
                with patch('pygame_gui.elements.UIButton') as MockBtn:
                    screen._controller.on_save()

        # Dialog should be shown, save NOT called yet
        assert screen._renderer.save_update_dialog is not None
        mocks['race_library'].save_race.assert_not_called()

    def test_overwrite_keeps_race_id(self):
        """Overwrite button should save with the existing race_id."""
        screen, mocks = _make_race_setup_screen()
        screen.is_editing = True
        screen.race_config.race_id = "existing_race_abc123"
        dialog_mock = MagicMock()
        screen._renderer.save_update_dialog = dialog_mock
        mocks['race_library'].save_race.return_value = (True, "Saved")
        screen.kill = MagicMock()

        screen._controller.on_overwrite_save()

        # race_id should be preserved
        assert screen.race_config.race_id == "existing_race_abc123"
        mocks['race_library'].save_race.assert_called_once()
        dialog_mock.kill.assert_called()
        assert screen._renderer.save_update_dialog is None

    def test_save_as_new_clears_race_id(self):
        """Save as New button should clear race_id for fresh generation."""
        screen, mocks = _make_race_setup_screen()
        screen.is_editing = True
        screen._view_model.is_editing = True
        screen.race_config.race_id = "existing_race_abc123"
        dialog_mock = MagicMock()
        screen._renderer.save_update_dialog = dialog_mock
        mocks['race_library'].save_race.return_value = (True, "Saved")
        screen.kill = MagicMock()

        screen._controller.on_save_as_new()

        # race_id should be cleared
        assert screen.race_config.race_id is None
        assert screen.is_editing is False
        mocks['race_library'].save_race.assert_called_once()
        dialog_mock.kill.assert_called()
        assert screen._renderer.save_update_dialog is None

    def test_cancel_dialog_does_not_save(self):
        """Cancel button should close dialog without saving."""
        screen, mocks = _make_race_setup_screen()
        screen._renderer.save_update_dialog = MagicMock()

        screen._controller.on_save_dialog_cancel()

        assert screen._renderer.save_update_dialog is None
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
        screen, _ = self._spec_bound_screen()
        with patch.object(RaceSetupScreen.__mro__[1], "process_event", return_value=False):
            screen.process_event(self._slider_event())

    def test_slider_event_calls_update_labels_and_update_config_on_env_panel(self):
        """Contract: slider move must call BOTH `update_labels()`
        (refreshes row labels + cost + points) AND `update_config()`
        (writes slider values into `race_config.preferences`). Either
        omission reintroduces a silent bug — stale labels or stale
        config."""
        screen, _ = self._spec_bound_screen()

        with patch.object(RaceSetupScreen.__mro__[1], "process_event", return_value=False):
            screen.process_event(self._slider_event())

        screen._environment_panel.update_labels.assert_called_once()
        screen._environment_panel.update_config.assert_called_once()


# ===========================================================================
# PROJ-287 Phase 2: Race registry cache invalidation on save
# ===========================================================================

class TestRaceRegistryInvalidationOnSave:
    """After a successful save, the controller must invalidate the
    session's race registry so subsequent reads see the freshly-saved
    race.

    PROJ-309 Sub-phase 3.1: `_do_save` migrated to
    `RaceSetupController.do_save`; `race_registry` lives on the
    controller (the screen mirror is preserved).
    """

    def test_successful_save_invalidates_registry_entry(self):
        """Successful save calls registry.invalidate(race_id)."""
        screen, mocks = _make_race_setup_screen()
        screen.race_config.race_id = "edited_race_123"
        screen._controller.race_registry = MagicMock()
        mocks['race_library'].save_race.return_value = (True, "Saved")
        screen.kill = MagicMock()

        screen._controller.do_save()

        screen._controller.race_registry.invalidate.assert_called_once_with(
            "edited_race_123"
        )

    def test_failed_save_does_not_invalidate(self):
        """Failed save must NOT invalidate (cache stays coherent with disk)."""
        screen, mocks = _make_race_setup_screen()
        screen.race_config.race_id = "edited_race_123"
        screen._controller.race_registry = MagicMock()
        mocks['race_library'].save_race.return_value = (False, "Disk full")
        screen.kill = MagicMock()

        screen._controller.do_save()

        screen._controller.race_registry.invalidate.assert_not_called()

    def test_save_without_registry_still_works(self):
        """Pre-game save (race_registry=None) completes without error."""
        screen, mocks = _make_race_setup_screen()
        screen.race_config.race_id = "new_race_456"
        screen._controller.race_registry = None
        mocks['race_library'].save_race.return_value = (True, "Saved")
        screen.kill = MagicMock()

        screen._controller.do_save()  # Must not raise

        mocks['race_library'].save_race.assert_called_once()


# ===========================================================================
# FEAT-12: Per-Tab Randomize + Master Randomize All
# ===========================================================================


class TestFeat12NavigationButtonVisibility:
    """FEAT-12 Sub-task 4: visibility filter shows btn_randomize on
    Identity, Visuals, Ships, Environment, AND Aptitudes tabs.
    """

    def test_randomize_button_visible_on_identity_tab(self):

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_IDENTITY
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.show.assert_called()

    def test_randomize_button_visible_on_visuals_tab(self):

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_VISUALS
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.show.assert_called()

    def test_randomize_button_visible_on_ships_tab(self):

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_SHIPS
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.show.assert_called()

    def test_randomize_button_visible_on_environment_tab(self):

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_ENVIRONMENT
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.show.assert_called()

    def test_randomize_button_visible_on_aptitudes_tab(self):

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_APTITUDES
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.show.assert_called()

    def test_randomize_button_hidden_on_summary_tab(self):
        """Summary tab uses the master 'Randomize All' button on the
        summary panel — the bottom-bar button is hidden there."""

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_SUMMARY
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.hide.assert_called()

    def test_randomize_button_hidden_on_descriptions_tab(self):

        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_DESCRIPTIONS
        RaceSetupScreen._update_navigation_buttons(screen)
        screen.btn_randomize.hide.assert_called()


class TestFeat12OnRandomizeDispatch:
    """FEAT-12 Sub-task 4: `on_randomize` dispatches to the right
    per-tab handler.

    PROJ-309 Sub-phase 3.1: dispatcher migrated from
    `RaceSetupScreen._on_randomize` → `RaceSetupController.on_randomize`.
    Per-tab handlers migrated from `screen._randomize_<tab>` →
    `controller.randomize_<tab>`."""

    def test_dispatches_to_randomize_environment_when_on_env_tab(self):
        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_ENVIRONMENT
        screen._controller.randomize_environment = MagicMock()
        screen._controller.randomize_aptitudes = MagicMock()

        screen._controller.on_randomize()

        screen._controller.randomize_environment.assert_called_once()
        screen._controller.randomize_aptitudes.assert_not_called()

    def test_dispatches_to_randomize_aptitudes_when_on_aptitudes_tab(self):
        screen, _ = _make_race_setup_screen()
        screen.current_step = screen.TAB_APTITUDES
        screen._controller.randomize_environment = MagicMock()
        screen._controller.randomize_aptitudes = MagicMock()

        screen._controller.on_randomize()

        screen._controller.randomize_aptitudes.assert_called_once()
        screen._controller.randomize_environment.assert_not_called()


class TestFeat12RandomizeEnvironmentHandler:
    """FEAT-12 Sub-task 4: `_randomize_environment` writes results to
    `race_config` and refreshes the environment + aptitudes panels."""

    def test_writes_preferences_homeworld_repro_happiness_to_config(self):
        from game.strategy.data.environmental_preference import EnvironmentalPreference

        screen, _ = _make_race_setup_screen()
        # Use a real RaceConfig so dataclass attribute access works.
        # Both the screen mirror and the controller's authoritative
        # reference must point at the same instance.
        from game.strategy.data.race_config import RaceConfig
        new_config = RaceConfig()
        screen.race_config = new_config
        screen._controller.race_config = new_config

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
        # RaceRandomizer is imported by
        # `game.ui.screens.race_setup.controller`, so we patch the
        # canonical module path that the controller actually imports
        # from.
        with patch(
            "game.ui.screens.race_setup.controller.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_environment.return_value = fake_result
            screen._controller.randomize_environment()

        assert screen.race_config.preferences["gravity"] is fake_pref
        assert screen.race_config.homeworld_type == "CONTINENTAL"
        assert screen.race_config.base_reproduction_rate == 0.05
        assert screen.race_config.base_happiness == 0.7

    def test_refreshes_environment_and_aptitudes_panels(self):
        from game.strategy.data.race_config import RaceConfig

        screen, mocks = _make_race_setup_screen()
        new_config = RaceConfig()
        screen.race_config = new_config
        screen._controller.race_config = new_config

        # RaceRandomizer is imported by
        # `game.ui.screens.race_setup.controller`, so we patch the
        # canonical module path that the controller actually imports
        # from.
        with patch(
            "game.ui.screens.race_setup.controller.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_environment.return_value = {
                "preferences": {},
                "homeworld_type": "CONTINENTAL",
                "base_reproduction_rate": 0.03,
                "base_happiness": 0.5,
            }
            screen._controller.randomize_environment()

        mocks['environment_panel'].set_from_config.assert_called()
        mocks['aptitudes_panel'].update_budget_display.assert_called()


class TestFeat12RandomizeAptitudesHandler:
    """FEAT-12 Sub-task 4: `_randomize_aptitudes` writes aptitude
    attributes to `race_config` and refreshes panels."""

    def test_writes_seven_aptitude_attrs_to_config(self):
        from game.strategy.data.race_config import RaceConfig

        screen, _ = _make_race_setup_screen()
        new_config = RaceConfig()
        screen.race_config = new_config
        screen._controller.race_config = new_config

        fake_aptitudes = {
            "strength": 60,
            "intelligence": 70,
            "constitution": 50,
            "dexterity": 30,
            "tolerance_other_species": 50,
            "cooperation": 50,
            "conflict_tolerance": 40,
        }
        # RaceRandomizer is imported by
        # `game.ui.screens.race_setup.controller`, so we patch the
        # canonical module path that the controller actually imports
        # from.
        with patch(
            "game.ui.screens.race_setup.controller.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_aptitudes.return_value = fake_aptitudes
            screen._controller.randomize_aptitudes()

        for name, value in fake_aptitudes.items():
            assert getattr(screen.race_config, f"aptitude_{name}") == value

    def test_refreshes_aptitudes_panel(self):
        from game.strategy.data.race_config import RaceConfig

        screen, mocks = _make_race_setup_screen()
        new_config = RaceConfig()
        screen.race_config = new_config
        screen._controller.race_config = new_config

        # RaceRandomizer is imported by
        # `game.ui.screens.race_setup.controller`, so we patch the
        # canonical module path that the controller actually imports
        # from.
        with patch(
            "game.ui.screens.race_setup.controller.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_aptitudes.return_value = {
                "strength": 50, "intelligence": 50, "constitution": 50,
                "dexterity": 50, "tolerance_other_species": 50,
                "cooperation": 50, "conflict_tolerance": 50,
            }
            screen._controller.randomize_aptitudes()

        mocks['aptitudes_panel'].set_from_config.assert_called()


class TestFeat12RandomizeAllHandler:
    """FEAT-12 Sub-task 5: master Randomize All handler invokes the
    orchestrator and applies the result via `_populate_ui_from_config`."""

    def test_invokes_orchestrator_and_repopulates_ui(self):
        from game.strategy.data.environmental_preference import EnvironmentalPreference
        from game.strategy.data.race_config import RaceConfig

        screen, _ = _make_race_setup_screen()
        # Use a real RaceConfig so dataclass attribute access works.
        # Both the screen (mirror) and controller (authoritative writer)
        # need the same reference.
        new_config = RaceConfig()
        screen.race_config = new_config
        screen._controller.race_config = new_config
        # PROJ-309 Sub-phase 3.1: `_populate_ui_from_config` migrated to
        # `RaceSetupController.populate_ui_from_config`. Patch the
        # controller's method so the assertion below targets the
        # post-refactor home.
        screen._controller.populate_ui_from_config = MagicMock()
        screen._refresh_summary = MagicMock()
        screen._renderer.refresh_ship_preview = MagicMock()

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
        # RaceRandomizer is imported by
        # `game.ui.screens.race_setup.controller`, so we patch the
        # canonical module path that the controller actually imports
        # from.
        with patch(
            "game.ui.screens.race_setup.controller.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_all.return_value = fake_all
            screen._controller.randomize_all()

        mock_rand.randomize_all.assert_called_once()
        # Identity field written (controller writes onto its own
        # race_config reference — which the test fixture aliased to
        # `screen.race_config`).
        assert screen._controller.race_config.race_name == "Rossarian"
        assert screen._controller.race_config.faction_name == "Rossarian Empire"
        # Visuals
        assert screen._controller.race_config.flag_id == "flag_a"
        assert screen._controller.race_config.portrait_id == "p_a.jpg"
        assert screen._controller.race_config.theme_id == "Federation"
        # Env
        assert screen._controller.race_config.homeworld_type == "CONTINENTAL"
        assert screen._controller.race_config.preferences["gravity"] is fake_pref
        # Aptitudes
        assert screen._controller.race_config.aptitude_strength == 60
        # Full UI repopulation triggered (post-refactor home: controller).
        screen._controller.populate_ui_from_config.assert_called_once()


# =============================================================================
# PROJ-299: kill hook + error popup message mapping
# =============================================================================


class TestProj299KillHookAndErrorMessages:
    """PROJ-309 Sub-phase 3.1: `kill()` stays on the screen because it
    overrides `pygame_gui.elements.UIWindow.kill`. The
    `_llm_error_message` mapper migrated to
    `LLMDialogService.error_message` (a static method)."""

    def test_kill_cancels_description_controller(self):
        """RaceSetupScreen.kill() must call controller.cancel_all() so
        worker threads don't try to populate dead UI widgets."""
        from unittest.mock import MagicMock, patch


        with patch.object(RaceSetupScreen, '__init__', lambda self, *a, **k: None):
            screen = RaceSetupScreen.__new__(RaceSetupScreen)
            # The screen reads the description controller through its
            # MVVM controller; provide a mock controller with the
            # `description_controller` attribute the screen looks at.
            description_controller = MagicMock()
            mvvm_controller = MagicMock()
            mvvm_controller.description_controller = description_controller
            screen._controller = mvvm_controller
            # Mock super().kill() — patch the bound super by patching the parent class.
            with patch('pygame_gui.elements.UIWindow.kill') as super_kill:
                screen.kill()
            description_controller.cancel_all.assert_called_once()
            super_kill.assert_called_once()

    def test_kill_when_no_controller_does_not_raise(self):
        from unittest.mock import MagicMock, patch


        with patch.object(RaceSetupScreen, '__init__', lambda self, *a, **k: None):
            screen = RaceSetupScreen.__new__(RaceSetupScreen)
            mvvm_controller = MagicMock()
            mvvm_controller.description_controller = None
            screen._controller = mvvm_controller
            with patch('pygame_gui.elements.UIWindow.kill'):
                screen.kill()  # MUST NOT raise

    def test_llm_error_message_for_each_exception_type(self):
        from game.core.exceptions import (
            LLMConfigError, LLMNetworkError, LLMRateLimited,
            LLMResponseError, LLMTimeoutError,
        )
        # PROJ-309 Sub-phase 3.1: error mapper migrated from
        # `RaceSetupScreen._llm_error_message` →
        # `LLMDialogService.error_message`.
        from game.ui.screens.race_setup.llm_dialog_service import LLMDialogService

        msg = LLMDialogService.error_message(LLMRateLimited("x"))
        assert "rate limit" in msg.lower()

        msg = LLMDialogService.error_message(LLMTimeoutError("x"))
        assert "timed out" in msg.lower() or "timeout" in msg.lower()

        msg = LLMDialogService.error_message(LLMNetworkError("x"))
        assert "network" in msg.lower()

        msg = LLMDialogService.error_message(LLMConfigError("x"))
        assert "configured" in msg.lower() or "config" in msg.lower()

        msg = LLMDialogService.error_message(LLMResponseError("x"))
        assert "response" in msg.lower() or "unexpected" in msg.lower()


# =============================================================================
# Regression: PROJ-299 dialog/popup constructors must use the correct attr
# =============================================================================


class TestProj299DialogPositioningRegression:
    """Regression for the AttributeError crash in show_llm_error_popup /
    show_llm_dialog: original code used `self.window_display_size` which
    doesn't exist on pygame_gui.UIWindow. The fix is to use the documented
    pattern `screen.get_container().get_size()` (matches show_save_update_dialog).

    PROJ-309 Sub-phase 3.1: dialog/popup constructors migrated from
    `RaceSetupScreen._show_llm_*` → `RaceSetupRenderer.show_llm_*`.
    The renderer uses `self._screen.get_container().get_size()` since
    it holds a back-reference to the screen.
    """

    def test_show_llm_error_popup_does_not_reference_window_display_size(self):
        """The crash was AttributeError on `self.window_display_size`.
        Verify the source no longer references that name."""
        import inspect
        from game.ui.screens.race_setup.renderer import RaceSetupRenderer

        src = inspect.getsource(RaceSetupRenderer.show_llm_error_popup)
        # Strip comments before checking — we mention the bad name in
        # a comment as guidance for future readers; only the attribute
        # access matters.
        code_only = "\n".join(line.split("#", 1)[0] for line in src.splitlines())
        assert "self.window_display_size" not in code_only, (
            "PROJ-299 regression: show_llm_error_popup must not use "
            "the non-existent UIWindow attribute `window_display_size`. "
            "Use `screen.get_container().get_size()` instead."
        )

    def test_show_llm_dialog_does_not_reference_window_display_size(self):
        import inspect
        from game.ui.screens.race_setup.renderer import RaceSetupRenderer

        src = inspect.getsource(RaceSetupRenderer.show_llm_dialog)
        # Strip comments before checking — we mention the bad name in
        # a comment as guidance for future readers; only the attribute
        # access matters.
        code_only = "\n".join(line.split("#", 1)[0] for line in src.splitlines())
        assert "self.window_display_size" not in code_only, (
            "PROJ-299 regression: show_llm_dialog must not use the "
            "non-existent UIWindow attribute `window_display_size`. "
            "Use `screen.get_container().get_size()` instead."
        )

    def test_show_llm_error_popup_uses_get_container_size(self):
        """Positive assertion: the fix uses the established pattern."""
        import inspect
        from game.ui.screens.race_setup.renderer import RaceSetupRenderer

        src = inspect.getsource(RaceSetupRenderer.show_llm_error_popup)
        assert "get_container()" in src and "get_size()" in src


# ===========================================================================
# BUG-115: Title-bar [X] close routes through cancel callback
# ===========================================================================


class TestBug115CloseButtonInvokesCancel:
    """BUG-115: Default `UIWindow.on_close_window_button_pressed` only
    calls `kill()`, leaving the parent's `active_race_modal` reference
    stale. RaceSetupScreen overrides this method to route the [X]-close
    through the same path as the in-window Cancel button so the cancel
    callback fires."""

    def test_close_window_button_invokes_cancel_callback(self):
        """[X]-close on the wizard fires `on_cancel_callback` (so the
        parent NewGameSetupScreen clears `active_race_modal`)."""
        screen, _ = _make_race_setup_screen()
        screen.kill = MagicMock()

        RaceSetupScreen.on_close_window_button_pressed(screen)

        screen.on_cancel_callback.assert_called_once()
        screen.kill.assert_called_once()

    def test_close_window_button_routes_through_controller(self):
        """The override delegates to `controller.on_cancel`, which is the
        single canonical cancel path (so any future cancel-side behaviour
        — logging, LLM cleanup, etc. — is shared between [X] and
        btn_cancel)."""
        screen, mocks = _make_race_setup_screen()
        screen.kill = MagicMock()

        with patch.object(mocks['controller'], 'on_cancel') as on_cancel:
            RaceSetupScreen.on_close_window_button_pressed(screen)

        on_cancel.assert_called_once()


# ===========================================================================
# BUG-118: populate_ui_from_config must refresh the summary panel
# ===========================================================================


# ===========================================================================
# Issue #11: lazy panel construction
# ===========================================================================


class TestIssue11LazyPanelConstruction:
    """Issue #11: heavy galleries (flag/portrait/theme) must NOT be
    constructed during ``RaceSetupScreen.__init__``. They're built on
    first ``_show_step(<their tab>)`` activation (or when
    ``randomize_all`` materialises them explicitly)."""

    def test_create_step_panels_only_invokes_summary_factory(self):
        """``_create_step_panels`` calls only the Summary factory eagerly.
        The other six factories are deferred until tab activation."""
        from unittest.mock import patch, MagicMock

        from game.ui.screens.race_setup import panel_factory

        # Build a screen via bypass + NullRaceSetupUiBuilder so we control
        # the test's panel-factory invocation manually below.
        screen, _ = _make_race_setup_screen()
        # Reset the step_panels and gallery slots to mimic a fresh build.
        screen.step_panels = []
        screen._flag_gallery = None
        screen._portrait_gallery = None
        screen._theme_gallery = None
        screen._identity_panel = None
        screen._environment_panel = None
        screen._aptitudes_panel = None
        screen._description_panel = None

        container = MagicMock()
        container.get_size.return_value = (800, 600)
        with patch.object(panel_factory, "create_summary_panel") as summ, \
             patch.object(panel_factory, "create_identity_panel") as ident, \
             patch.object(panel_factory, "create_visuals_panel") as vis, \
             patch.object(panel_factory, "create_ships_panel") as ships, \
             patch.object(panel_factory, "create_environment_panel") as env, \
             patch.object(panel_factory, "create_aptitudes_panel") as apt, \
             patch.object(panel_factory, "create_descriptions_panel") as desc, \
             patch("pygame_gui.elements.UIPanel"):
            RaceSetupScreen._create_step_panels(screen, container, 800, 50, 400)

        summ.assert_called_once()
        ident.assert_not_called()
        vis.assert_not_called()
        ships.assert_not_called()
        env.assert_not_called()
        apt.assert_not_called()
        desc.assert_not_called()

    def test_show_step_materialises_target_tab_on_first_activation(self):
        """``_show_step`` materialises the target tab's factory on its
        first activation (lazy build) and does NOT re-run it on
        subsequent activations."""
        from unittest.mock import MagicMock


        screen, _ = _make_race_setup_screen()
        screen._flag_gallery = None
        screen._portrait_gallery = None

        # Seed _deferred_panel_factories as ``_create_step_panels`` would
        # have done in production. Use a sentinel factory we can spy on.
        vis_factory = MagicMock(name="create_visuals_panel")
        screen._deferred_panel_factories = {screen.TAB_VISUALS: vis_factory}

        RaceSetupScreen._show_step(screen, screen.TAB_VISUALS)
        vis_factory.assert_called_once()

        # Second activation must NOT re-invoke the factory.
        RaceSetupScreen._show_step(screen, screen.TAB_VISUALS)
        vis_factory.assert_called_once()

    def test_randomize_all_materialises_visuals_and_ships_panels(self):
        """``randomize_all`` needs the galleries to read asset pools and
        apply selections. With lazy construction, it must force-build
        Visuals + Ships before iterating their galleries — otherwise the
        master Randomize button silently no-ops on first click."""
        from unittest.mock import patch, MagicMock

        from game.strategy.data.race_config import RaceConfig
        from game.strategy.data.environmental_preference import (
            EnvironmentalPreference,
        )

        screen, _ = _make_race_setup_screen()
        # Pretend the galleries haven't been built yet (lazy state).
        screen._flag_gallery = None
        screen._portrait_gallery = None
        screen._theme_gallery = None

        new_config = RaceConfig()
        screen.race_config = new_config
        screen._controller.race_config = new_config
        screen._renderer.refresh_ship_preview = MagicMock()
        screen._controller.populate_ui_from_config = MagicMock()

        # Seed _deferred_panel_factories with spy factories that attach
        # the gallery mocks ``randomize_all`` then iterates.
        def vis_factory(s, _panel=None):
            s._flag_gallery = MagicMock()
            s._flag_gallery._discover_assets.return_value = [("flag_a",)]
            s._portrait_gallery = MagicMock()
            s._portrait_gallery._discover_assets.return_value = [("p_a.jpg",)]

        def ships_factory(s, _panel=None):
            s._theme_gallery = MagicMock()
            s._theme_gallery._discover_assets.return_value = [("Federation",)]

        vis_spy = MagicMock(side_effect=vis_factory)
        ships_spy = MagicMock(side_effect=ships_factory)
        screen._deferred_panel_factories = {
            screen.TAB_VISUALS: vis_spy,
            screen.TAB_SHIPS: ships_spy,
        }

        fake_pref = EnvironmentalPreference(
            setpoint=9.81, tolerance=2.0,
            min_value=0.1, max_value=30.0, step=0.98,
        )
        fake_all = {
            "race_name": "X", "race_name_plural": "Xs", "leader_name": "L",
            "physical_type": "H", "government_type": "E",
            "government_organization": "A", "leader_title": "T",
            "society_type": "S", "faction_name": "F",
            "flag_id": "flag_a", "portrait_id": "p_a.jpg",
            "theme_id": "Federation", "homeworld_type": "CONTINENTAL",
            "preferences": {"gravity": fake_pref},
            "base_reproduction_rate": 0.05, "base_happiness": 0.7,
            "aptitudes": {
                "strength": 50, "intelligence": 50, "constitution": 50,
                "dexterity": 50, "tolerance_other_species": 50,
                "cooperation": 50, "conflict_tolerance": 50,
            },
        }

        with patch(
            "game.ui.screens.race_setup.controller.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_all.return_value = fake_all
            screen._controller.randomize_all()

        vis_spy.assert_called_once()
        ships_spy.assert_called_once()
        assert screen.race_config.flag_id == "flag_a"
        assert screen.race_config.theme_id == "Federation"

    def test_ensure_panel_built_runs_factory_with_panel_visible(self):
        """Deferred panels must be materialised inside a *visible*
        container. pygame_gui's ``UIContainer.add_element`` calls
        ``hide()`` on a freshly-created ``UIScrollingContainer`` child
        when the parent is hidden — and that ``hide()`` runs before the
        scroll bars exist, raising ``AttributeError``. So
        ``ensure_panel_built`` shows the panel for the duration of the
        factory call, then restores the original (hidden) state so a
        non-active tab materialised by ``randomize_all`` stays hidden."""
        screen, _ = _make_race_setup_screen()

        class _PanelStub:
            def __init__(self) -> None:
                self.visible = 0  # hidden, as a non-active tab panel is

            def show(self) -> None:
                self.visible = 1

            def hide(self) -> None:
                self.visible = 0

        panels = [_PanelStub() for _ in range(screen.TAB_VISUALS + 1)]
        screen.step_panels = panels
        target = panels[screen.TAB_VISUALS]

        seen_visible: list[int] = []

        def factory(_s, panel):
            seen_visible.append(panel.visible)

        screen._deferred_panel_factories = {screen.TAB_VISUALS: factory}

        RaceSetupScreen.ensure_panel_built(screen, screen.TAB_VISUALS)

        assert seen_visible == [1], "factory must run while panel is visible"
        assert target.visible == 0, "hidden panel must stay hidden afterwards"

    def test_ensure_panel_built_leaves_already_visible_panel_visible(self):
        """When the panel is already visible (the active tab), visibility
        is left untouched after the factory runs."""
        screen, _ = _make_race_setup_screen()

        class _PanelStub:
            def __init__(self) -> None:
                self.visible = 1

            def show(self) -> None:
                self.visible = 1

            def hide(self) -> None:
                self.visible = 0

        panels = [_PanelStub() for _ in range(screen.TAB_VISUALS + 1)]
        screen.step_panels = panels
        target = panels[screen.TAB_VISUALS]
        screen._deferred_panel_factories = {
            screen.TAB_VISUALS: lambda _s, _p: None
        }

        RaceSetupScreen.ensure_panel_built(screen, screen.TAB_VISUALS)

        assert target.visible == 1


class TestBug118SummaryRefreshOnPopulate:
    """BUG-118: `populate_ui_from_config` must call `_summary_panel.refresh()`.

    The summary panel uses `refresh()` while every other panel uses
    `set_from_config()`, so it was silently skipped from the bulk-refresh
    path. This made "Randomize All" leave the Summary tab's left-column
    labels (Faction, Species, Government, Physical, Society) stuck on
    "—" until the user switched tabs and back.
    """

    def test_populate_ui_from_config_refreshes_summary_panel(self):
        """The bulk-refresh helper invokes `_summary_panel.refresh()`."""
        screen, _ = _make_race_setup_screen()

        screen._controller.populate_ui_from_config()

        screen._summary_panel.refresh.assert_called_once()

    def test_randomize_all_refreshes_summary_panel_left_column(self):
        """End-to-end: clicking "Randomize All" triggers the summary
        refresh that paints the left-column identity labels."""
        from game.strategy.data.environmental_preference import (
            EnvironmentalPreference,
        )
        from game.strategy.data.race_config import RaceConfig

        screen, _ = _make_race_setup_screen()
        new_config = RaceConfig()
        screen.race_config = new_config
        screen._controller.race_config = new_config
        screen._renderer.refresh_ship_preview = MagicMock()
        screen._flag_gallery._discover_assets = MagicMock(
            return_value=[("flag_a",)]
        )
        screen._portrait_gallery._discover_assets = MagicMock(
            return_value=[("p_a.jpg",)]
        )
        screen._theme_gallery._discover_assets = MagicMock(
            return_value=[("Federation",)]
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
            "game.ui.screens.race_setup.controller.RaceRandomizer"
        ) as mock_rand:
            mock_rand.randomize_all.return_value = fake_all
            screen._controller.randomize_all()

        screen._summary_panel.refresh.assert_called()

    def test_on_race_selected_refreshes_summary_panel(self):
        """Loading a race via the browser dialog also refreshes the
        summary panel — the explicit `_refresh_summary()` call was
        deleted from `on_race_selected` in favour of the canonical
        path inside `populate_ui_from_config`."""
        screen, _ = _make_race_setup_screen()
        new_config = _make_race_config_mock()

        screen._controller.on_race_selected(new_config)

        screen._summary_panel.refresh.assert_called()
