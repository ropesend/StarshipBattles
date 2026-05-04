"""
Unit tests for RaceIdentityPanel.

PROJ-66 Phase 3: TDD tests for race identity configuration panel.
Tests race name, government, faction name, and identity field handling.

PROJ-322 Task 5.3 (APC-001-F03): the legacy `RaceIdentityPanel.__new__` +
`patch.object(__init__, ...)` blocks (both the helper at module scope and
the per-test inline ones) now route through the shared `make_ui_widget`
factory from `tests.fixtures.ui_widget_factory`.
"""

import pytest
from unittest.mock import MagicMock, patch

from tests.fixtures.ui_widget_factory import make_ui_widget


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_race_config():
    """Create a mock RaceConfig with identity properties."""
    config = MagicMock()
    config.race_name = ""
    config.race_name_plural = ""
    config.faction_name = ""
    config.government_type = ""
    config.government_organization = ""
    config.leader_title = ""
    config.leader_name = ""
    config.physical_type = ""
    config.society_type = ""
    return config


@pytest.fixture
def mock_ui_manager():
    """Create a mock pygame_gui UIManager."""
    return MagicMock()


@pytest.fixture
def mock_panel():
    """Create a mock UIPanel container."""
    panel = MagicMock()
    panel.get_relative_rect.return_value = MagicMock(width=600)
    return panel


def _bypass_init_panel(race_config=None):
    """Build a `RaceIdentityPanel` via the shared `make_ui_widget` factory.

    Replaces the legacy `__new__` + `patch.object(__init__, ...)` block.
    The factory mocks every `pygame_gui.elements.UI*` class for the duration
    of `__init__`, so heavy `_create_content` runs but is bounded; the real
    `_init_empty_refs()` runs as part of `__init__` so all dropdown / input
    refs exist (the elements are Mocks, but the attributes are present).

    `race_config` is required by production `__init__`; tests then
    overwrite specific element refs (e.g. `panel.race_name_input`) with a
    controlled `MagicMock` before exercising `update_config()` /
    `set_from_config()`.

    PROJ-322 Task 5.3 / APC-001-F03 (originally promoted from inline blocks
    in PROJ-323 Task 1.25; the factory cuts the bypass-init pattern entirely).
    """
    if race_config is None:
        race_config = MagicMock()
    from game.ui.panels.race_identity_panel import RaceIdentityPanel

    return make_ui_widget(RaceIdentityPanel, race_config=race_config)


# =============================================================================
# Test: RaceIdentityPanel Import and Creation
# =============================================================================

# =============================================================================
# Test: Configuration Updates (update_config)
# =============================================================================

class TestUpdateConfig:
    """Tests for update_config method."""

    def test_update_config_reads_race_name(self, mock_race_config):
        """update_config reads race_name from text input."""
        panel = _bypass_init_panel(race_config=mock_race_config)

        panel.race_name_input = MagicMock()
        panel.race_name_input.get_text.return_value = "Rossarian"

        panel.update_config()

        assert mock_race_config.race_name == "Rossarian"

    def test_update_config_reads_race_name_plural(self, mock_race_config):
        """update_config reads race_name_plural from text input."""
        panel = _bypass_init_panel(race_config=mock_race_config)

        panel.race_name_plural_input = MagicMock()
        panel.race_name_plural_input.get_text.return_value = "Rossarians"

        panel.update_config()

        assert mock_race_config.race_name_plural == "Rossarians"

    def test_update_config_reads_government_type(self, mock_race_config):
        """update_config reads government_type from dropdown."""
        panel = _bypass_init_panel(race_config=mock_race_config)

        panel.government_type_dropdown = MagicMock()
        panel.government_type_dropdown.selected_option = ("Empire", "Empire")

        panel.update_config()

        assert mock_race_config.government_type == "Empire"

    def test_update_config_reads_faction_name(self, mock_race_config):
        """update_config reads faction_name from text input."""
        panel = _bypass_init_panel(race_config=mock_race_config)

        panel.faction_name_input = MagicMock()
        panel.faction_name_input.get_text.return_value = "Rossarian Empire"

        panel.update_config()

        assert mock_race_config.faction_name == "Rossarian Empire"

    def test_update_config_handles_empty_dropdown(self, mock_race_config):
        """update_config handles empty dropdown selection."""
        panel = _bypass_init_panel(race_config=mock_race_config)

        panel.government_type_dropdown = MagicMock()
        panel.government_type_dropdown.selected_option = ("-- Select --", "")

        panel.update_config()

        assert mock_race_config.government_type == ""


# =============================================================================
# Test: Set From Config
# =============================================================================

class TestSetFromConfig:
    """Tests for set_from_config method."""

    def test_set_from_config_populates_race_name(self, mock_race_config):
        """set_from_config sets race_name text input."""
        mock_race_config.race_name = "Terrakin"
        panel = _bypass_init_panel(race_config=mock_race_config)
        # Reset the dropdowns + inputs (factory's _create_content created
        # mocks; the test wants its own controlled MagicMock).
        panel._init_empty_refs()

        panel.race_name_input = MagicMock()

        panel.set_from_config()

        panel.race_name_input.set_text.assert_called_with("Terrakin")

    def test_set_from_config_recreates_dropdowns(self, mock_race_config):
        """set_from_config kills old dropdowns and creates new ones with correct values."""
        mock_race_config.government_type = "Federation"
        mock_race_config.physical_type = "Humanoid"
        mock_race_config.government_organization = "Democracy"
        mock_race_config.leader_title = "President"
        mock_race_config.society_type = "Diplomats"
        panel = _bypass_init_panel(race_config=mock_race_config)
        # Override _create_content's auto-mocked dropdowns with controlled
        # mocks bearing the relative_rect / ui_container attrs the production
        # code reads when killing + recreating them.
        for attr in ['physical_type_dropdown', 'government_type_dropdown',
                     'government_org_dropdown', 'leader_title_dropdown',
                     'society_type_dropdown']:
            mock_dd = MagicMock()
            mock_dd.relative_rect = MagicMock()
            mock_dd.ui_container = MagicMock()
            setattr(panel, attr, mock_dd)

        old_dropdowns = {
            'physical': panel.physical_type_dropdown,
            'gov_type': panel.government_type_dropdown,
            'gov_org': panel.government_org_dropdown,
            'leader': panel.leader_title_dropdown,
            'society': panel.society_type_dropdown,
        }

        with patch('game.ui.panels.race_identity_panel.pygame_gui.elements.UIDropDownMenu') as MockDD:
            MockDD.return_value = MagicMock()
            panel.set_from_config()

        # Old dropdowns were killed
        for name, old_dd in old_dropdowns.items():
            old_dd.kill.assert_called_once(), f"{name} dropdown was not killed"

        # New dropdown was created for each (5 dropdowns total)
        assert MockDD.call_count == 5

    def test_set_from_config_passes_correct_starting_option(self, mock_race_config):
        """set_from_config passes the config value as starting_option to new dropdowns."""
        mock_race_config.government_type = "Empire"
        mock_race_config.physical_type = ""  # empty = should use EMPTY_OPTION
        mock_race_config.government_organization = "Autocracy"
        mock_race_config.leader_title = "Emperor"
        mock_race_config.society_type = "Conquerors"
        panel = _bypass_init_panel(race_config=mock_race_config)

        for attr in ['physical_type_dropdown', 'government_type_dropdown',
                     'government_org_dropdown', 'leader_title_dropdown',
                     'society_type_dropdown']:
            mock_dd = MagicMock()
            mock_dd.relative_rect = MagicMock()
            mock_dd.ui_container = MagicMock()
            setattr(panel, attr, mock_dd)

        with patch('game.ui.panels.race_identity_panel.pygame_gui.elements.UIDropDownMenu') as MockDD:
            MockDD.return_value = MagicMock()
            panel.set_from_config()

        # Extract starting_option from each call's kwargs
        starting_options = [
            call.kwargs['starting_option']
            for call in MockDD.call_args_list
        ]

        # Order: physical, government_type, government_org, leader_title, society
        assert starting_options[0] == "-- Select --"  # empty physical_type
        assert starting_options[1] == "Empire"
        assert starting_options[2] == "Autocracy"
        assert starting_options[3] == "Emperor"
        assert starting_options[4] == "Conquerors"

    def test_set_from_config_handles_none_dropdown(self, mock_race_config):
        """set_from_config handles None dropdowns gracefully."""
        mock_race_config.government_type = ""
        panel = _bypass_init_panel(race_config=mock_race_config)
        # Force all dropdowns back to None — the factory's _create_content
        # populated them with mocks; the production set_from_config must
        # handle the None case without erroring.
        panel._init_empty_refs()

        # Should not error
        panel.set_from_config()


# =============================================================================
# Test: Faction Name Auto-Generation
# =============================================================================

class TestFactionAutoGeneration:
    """Tests for faction name auto-generation."""

    def test_auto_generate_faction_name_both_set(self):
        """Faction auto-generates as 'RaceName GovernmentType'."""
        panel = _bypass_init_panel()

        result = panel._auto_generate_faction_name("Rossarian", "Empire")

        assert result == "Rossarian Empire"

    def test_auto_generate_faction_name_race_only(self):
        """Faction uses race_name alone when government not set."""
        panel = _bypass_init_panel()

        result = panel._auto_generate_faction_name("Rossarian", "")

        assert result == "Rossarian"

    def test_auto_generate_faction_name_government_only(self):
        """Faction uses government_type alone when race not set."""
        panel = _bypass_init_panel()

        result = panel._auto_generate_faction_name("", "Empire")

        assert result == "Empire"

    def test_auto_generate_faction_name_neither_set(self):
        """Faction returns empty string when both unset."""
        panel = _bypass_init_panel()

        result = panel._auto_generate_faction_name("", "")

        assert result == ""

    def test_auto_generate_faction_name_resets_when_not_overridden(self, mock_race_config):
        """Auto-generation updates when not manually overridden."""
        panel = _bypass_init_panel(race_config=mock_race_config)
        panel._faction_name_overridden = False

        panel.faction_name_input = MagicMock()

        # When not overridden, faction updates
        panel._update_faction_if_not_overridden("Terrakin", "Alliance")

        panel.faction_name_input.set_text.assert_called_with("Terrakin Alliance")


# =============================================================================
# Test: Update Labels
# =============================================================================

class TestUpdateLabels:
    """Tests for update_labels method (should be no-op for this panel).

    BUG-NOTE: update_labels exists as a no-op so the cross-panel API contract
    holds — race_setup_screen/input_handler.py:150,154 calls
    `_environment_panel.update_labels()` and `_aptitudes_panel.update_labels()`
    on a per-frame slider-drag basis, and RaceIdentityPanel exposes the same
    method even though it has no live-updating numeric labels. Removing the
    method silently would crash the input handler the first time it dispatches
    a slider-drag event with the identity tab focused.
    """

    def test_update_labels_is_no_op_returns_none_without_mutating_inputs(self):
        """update_labels exists, returns None, doesn't raise, and doesn't
        mutate any text inputs. Pin all three contract obligations rather
        than just calling the `pass` body."""
        panel = _bypass_init_panel()
        # Capture pre-call set_text counts for every input.
        pre_call_counts = {
            name: getattr(panel, name).set_text.call_count
            for name in ("race_name_input", "race_name_plural_input",
                         "leader_name_input", "faction_name_input")
            if getattr(panel, name, None) is not None
        }

        result = panel.update_labels()

        # Returns None (the explicit `pass` body has no return).
        assert result is None
        # No text input was touched (no-op contract).
        for name, before in pre_call_counts.items():
            assert getattr(panel, name).set_text.call_count == before, (
                f"update_labels must not mutate {name}.set_text"
            )


# =============================================================================
# Test: Leader Name Field (BUG-72)
# =============================================================================

class TestLeaderNameField:
    """Tests for leader_name text input (BUG-72)."""

    def test_identity_panel_has_leader_name_input(self):
        """RaceIdentityPanel has leader_name_input attribute."""
        panel = _bypass_init_panel()
        assert hasattr(panel, 'leader_name_input')

    def test_update_config_reads_leader_name(self, mock_race_config):
        """update_config reads leader_name from text input."""
        panel = _bypass_init_panel(race_config=mock_race_config)

        panel.leader_name_input = MagicMock()
        panel.leader_name_input.get_text.return_value = "Zara IV"

        panel.update_config()

        assert mock_race_config.leader_name == "Zara IV"

    def test_set_from_config_populates_leader_name(self, mock_race_config):
        """set_from_config sets leader_name text input."""
        mock_race_config.leader_name = "Emperor Zog"
        panel = _bypass_init_panel(race_config=mock_race_config)
        # Reset dropdowns to None so set_from_config short-circuits past
        # the dropdown-recreation path (real pygame_gui.UIDropDownMenu
        # construction would be attempted otherwise).
        panel._init_empty_refs()

        panel.leader_name_input = MagicMock()

        panel.set_from_config()

        panel.leader_name_input.set_text.assert_called_with("Emperor Zog")


# =============================================================================
# PROJ-339: characterization gap-fillers
# =============================================================================


class TestFactionOverrideHandling:
    """PROJ-339: pin faction-override semantics surfaced via `handle_event`
    and `set_from_config`."""

    def test_faction_override_blocks_auto_regen_on_race_name_edit(
        self, mock_race_config,
    ):
        """After a `UI_TEXT_ENTRY_CHANGED` event on the faction input,
        `_faction_name_overridden` flips True. A subsequent text-entry
        event on the race-name input does NOT mutate the faction
        input's text — production code's `if not _overridden:` guard
        skips `_update_faction_if_not_overridden`.
        """
        import pygame_gui

        panel = _bypass_init_panel(race_config=mock_race_config)
        # Replace the auto-mocked inputs with controlled mocks so we can
        # assert call-state precisely.
        panel.faction_name_input = MagicMock()
        panel.race_name_input = MagicMock()
        panel.race_name_input.get_text.return_value = "Rossarian"
        panel.government_type_dropdown = MagicMock()
        panel.government_type_dropdown.selected_option = ("Empire", "Empire")

        # Step 1 — user manually edits faction. Panel sees the event and
        # flips the override flag.
        faction_event = MagicMock(type=pygame_gui.UI_TEXT_ENTRY_CHANGED)
        faction_event.ui_element = panel.faction_name_input
        panel.handle_event(faction_event)
        assert panel._faction_name_overridden is True

        # Step 2 — race-name change event. With override active, the
        # faction input's set_text MUST NOT be called.
        panel.faction_name_input.set_text.reset_mock()
        race_event = MagicMock(type=pygame_gui.UI_TEXT_ENTRY_CHANGED)
        race_event.ui_element = panel.race_name_input
        panel.handle_event(race_event)
        panel.faction_name_input.set_text.assert_not_called()

    def test_set_from_config_does_not_set_override_when_loaded_matches_auto(
        self, mock_race_config,
    ):
        """Loading a config whose `faction_name` equals the auto-generated
        value (race_name + government_type) does NOT flip
        `_faction_name_overridden` — production tracks "manually edited"
        as "different from auto-gen"."""
        mock_race_config.race_name = "Rossarian"
        mock_race_config.government_type = "Empire"
        # Auto-generated value would be "Rossarian Empire".
        mock_race_config.faction_name = "Rossarian Empire"
        panel = _bypass_init_panel(race_config=mock_race_config)
        # Force fresh refs so we don't read auto-mocked widgets from
        # _create_content.
        panel._init_empty_refs()
        panel.faction_name_input = MagicMock()

        panel.set_from_config()

        assert panel._faction_name_overridden is False


class TestGetDropdownValueEmptyOption:
    """PROJ-339: pin `_get_dropdown_value` mapping of EMPTY_OPTION → ''."""

    def test_get_dropdown_value_treats_empty_option_as_blank(self):
        """When the dropdown's selected_option is EMPTY_OPTION (the
        '-- Select --' sentinel), `_get_dropdown_value` returns ''."""
        panel = _bypass_init_panel()
        dd = MagicMock()
        # The pygame_gui dropdown reports a string when not in a tuple form.
        dd.selected_option = panel.EMPTY_OPTION

        assert panel._get_dropdown_value(dd) == ""

        # Tuple form likewise — production unpacks `(display, value)`
        # and treats EMPTY_OPTION the same.
        dd.selected_option = (panel.EMPTY_OPTION, panel.EMPTY_OPTION)
        assert panel._get_dropdown_value(dd) == ""
