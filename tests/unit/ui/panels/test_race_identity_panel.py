"""
Unit tests for RaceIdentityPanel.

PROJ-66 Phase 3: TDD tests for race identity configuration panel.
Tests race name, government, faction name, and identity field handling.
"""

import pytest
from unittest.mock import MagicMock, patch


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
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.race_config = mock_race_config
            panel._init_empty_refs()

            panel.race_name_input = MagicMock()
            panel.race_name_input.get_text.return_value = "Rossarian"

            panel.update_config()

            assert mock_race_config.race_name == "Rossarian"

    def test_update_config_reads_race_name_plural(self, mock_race_config):
        """update_config reads race_name_plural from text input."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.race_config = mock_race_config
            panel._init_empty_refs()

            panel.race_name_plural_input = MagicMock()
            panel.race_name_plural_input.get_text.return_value = "Rossarians"

            panel.update_config()

            assert mock_race_config.race_name_plural == "Rossarians"

    def test_update_config_reads_government_type(self, mock_race_config):
        """update_config reads government_type from dropdown."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.race_config = mock_race_config
            panel._init_empty_refs()

            panel.government_type_dropdown = MagicMock()
            panel.government_type_dropdown.selected_option = ("Empire", "Empire")

            panel.update_config()

            assert mock_race_config.government_type == "Empire"

    def test_update_config_reads_faction_name(self, mock_race_config):
        """update_config reads faction_name from text input."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.race_config = mock_race_config
            panel._init_empty_refs()

            panel.faction_name_input = MagicMock()
            panel.faction_name_input.get_text.return_value = "Rossarian Empire"

            panel.update_config()

            assert mock_race_config.faction_name == "Rossarian Empire"

    def test_update_config_handles_empty_dropdown(self, mock_race_config):
        """update_config handles empty dropdown selection."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.race_config = mock_race_config
            panel._init_empty_refs()

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
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            mock_race_config.race_name = "Terrakin"
            panel.race_config = mock_race_config
            panel._init_empty_refs()

            panel.race_name_input = MagicMock()

            panel.set_from_config()

            panel.race_name_input.set_text.assert_called_with("Terrakin")

    def test_set_from_config_recreates_dropdowns(self, mock_race_config):
        """set_from_config kills old dropdowns and creates new ones with correct values."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            mock_race_config.government_type = "Federation"
            mock_race_config.physical_type = "Humanoid"
            mock_race_config.government_organization = "Democracy"
            mock_race_config.leader_title = "President"
            mock_race_config.society_type = "Diplomats"
            panel.race_config = mock_race_config
            panel.ui_manager = MagicMock()
            panel._init_empty_refs()

            # Create mock dropdowns with required attributes
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
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            mock_race_config.government_type = "Empire"
            mock_race_config.physical_type = ""  # empty = should use EMPTY_OPTION
            mock_race_config.government_organization = "Autocracy"
            mock_race_config.leader_title = "Emperor"
            mock_race_config.society_type = "Conquerors"
            panel.race_config = mock_race_config
            panel.ui_manager = MagicMock()
            panel._init_empty_refs()

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
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            mock_race_config.government_type = ""
            panel.race_config = mock_race_config
            panel.ui_manager = MagicMock()
            panel._init_empty_refs()

            # All dropdowns are None from _init_empty_refs
            # Should not error
            panel.set_from_config()


# =============================================================================
# Test: Faction Name Auto-Generation
# =============================================================================

class TestFactionAutoGeneration:
    """Tests for faction name auto-generation."""

    def test_auto_generate_faction_name_both_set(self):
        """Faction auto-generates as 'RaceName GovernmentType'."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel._init_empty_refs()

            result = panel._auto_generate_faction_name("Rossarian", "Empire")

            assert result == "Rossarian Empire"

    def test_auto_generate_faction_name_race_only(self):
        """Faction uses race_name alone when government not set."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel._init_empty_refs()

            result = panel._auto_generate_faction_name("Rossarian", "")

            assert result == "Rossarian"

    def test_auto_generate_faction_name_government_only(self):
        """Faction uses government_type alone when race not set."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel._init_empty_refs()

            result = panel._auto_generate_faction_name("", "Empire")

            assert result == "Empire"

    def test_auto_generate_faction_name_neither_set(self):
        """Faction returns empty string when both unset."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel._init_empty_refs()

            result = panel._auto_generate_faction_name("", "")

            assert result == ""

    def test_auto_generate_faction_name_resets_when_not_overridden(self, mock_race_config):
        """Auto-generation updates when not manually overridden."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.race_config = mock_race_config
            panel._init_empty_refs()
            panel._faction_name_overridden = False

            panel.faction_name_input = MagicMock()

            # When not overridden, faction updates
            panel._update_faction_if_not_overridden("Terrakin", "Alliance")

            panel.faction_name_input.set_text.assert_called_with("Terrakin Alliance")


# =============================================================================
# Test: Update Labels
# =============================================================================

class TestUpdateLabels:
    """Tests for update_labels method (should be no-op for this panel)."""

    def test_update_labels_is_no_op(self):
        """update_labels does nothing for identity panel (labels are static)."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)

            # Should not raise
            panel.update_labels()


# =============================================================================
# Test: Leader Name Field (BUG-72)
# =============================================================================

class TestLeaderNameField:
    """Tests for leader_name text input (BUG-72)."""

    def test_identity_panel_has_leader_name_input(self):
        """RaceIdentityPanel has leader_name_input attribute."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel._init_empty_refs()
            assert hasattr(panel, 'leader_name_input')

    def test_update_config_reads_leader_name(self, mock_race_config):
        """update_config reads leader_name from text input."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.race_config = mock_race_config
            panel._init_empty_refs()

            panel.leader_name_input = MagicMock()
            panel.leader_name_input.get_text.return_value = "Zara IV"

            panel.update_config()

            assert mock_race_config.leader_name == "Zara IV"

    def test_set_from_config_populates_leader_name(self, mock_race_config):
        """set_from_config sets leader_name text input."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            mock_race_config.leader_name = "Emperor Zog"
            panel.race_config = mock_race_config
            panel._init_empty_refs()

            panel.leader_name_input = MagicMock()

            panel.set_from_config()

            panel.leader_name_input.set_text.assert_called_with("Emperor Zog")
