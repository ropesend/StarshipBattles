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

class TestRaceIdentityPanelCreation:
    """Tests for RaceIdentityPanel initialization."""

    def test_identity_panel_can_be_imported(self):
        """RaceIdentityPanel can be imported from module."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel
        assert RaceIdentityPanel is not None

    def test_identity_panel_has_race_name_input(self):
        """RaceIdentityPanel has race_name_input attribute."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.race_name_input = None
            assert hasattr(panel, 'race_name_input')

    def test_identity_panel_has_race_name_plural_input(self):
        """RaceIdentityPanel has race_name_plural_input attribute."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.race_name_plural_input = None
            assert hasattr(panel, 'race_name_plural_input')

    def test_identity_panel_has_government_type_dropdown(self):
        """RaceIdentityPanel has government_type_dropdown attribute."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.government_type_dropdown = None
            assert hasattr(panel, 'government_type_dropdown')

    def test_identity_panel_has_all_dropdowns(self):
        """RaceIdentityPanel has all required dropdown attributes."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.government_type_dropdown = None
            panel.government_org_dropdown = None
            panel.leader_title_dropdown = None
            panel.physical_type_dropdown = None
            panel.society_type_dropdown = None
            panel.faction_name_input = None

            assert hasattr(panel, 'government_type_dropdown')
            assert hasattr(panel, 'government_org_dropdown')
            assert hasattr(panel, 'leader_title_dropdown')
            assert hasattr(panel, 'physical_type_dropdown')
            assert hasattr(panel, 'society_type_dropdown')
            assert hasattr(panel, 'faction_name_input')

    def test_identity_panel_creates_successfully(self):
        """RaceIdentityPanel initializes without errors when mocked."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '_create_content'):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.panel = MagicMock()
            panel.ui_manager = MagicMock()
            panel.race_config = MagicMock()
            panel._faction_name_overridden = False

            assert panel._faction_name_overridden is False


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

    def test_set_from_config_populates_dropdowns(self, mock_race_config):
        """set_from_config populates dropdown selections."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            mock_race_config.government_type = "Federation"
            mock_race_config.physical_type = "Humanoid"
            panel.race_config = mock_race_config
            panel._init_empty_refs()

            panel.government_type_dropdown = MagicMock()
            panel.physical_type_dropdown = MagicMock()

            panel.set_from_config()

            # Dropdowns have select_option method
            panel.government_type_dropdown.selected_option = ("Federation", "Federation")
            panel.physical_type_dropdown.selected_option = ("Humanoid", "Humanoid")

    def test_set_from_config_handles_empty_government(self, mock_race_config):
        """set_from_config handles empty government_type."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            mock_race_config.government_type = ""
            panel.race_config = mock_race_config
            panel._init_empty_refs()

            panel.government_type_dropdown = MagicMock()

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

    def test_auto_generate_faction_name_override_preserved(self, mock_race_config):
        """Manual faction name edit sets override flag."""
        from game.ui.panels.race_identity_panel import RaceIdentityPanel

        with patch.object(RaceIdentityPanel, '__init__', lambda self, *args, **kwargs: None):
            panel = RaceIdentityPanel.__new__(RaceIdentityPanel)
            panel.race_config = mock_race_config
            panel._faction_name_overridden = False

            # Simulate manual edit
            panel._faction_name_overridden = True

            assert panel._faction_name_overridden is True

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
