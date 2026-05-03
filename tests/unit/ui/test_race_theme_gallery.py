"""
Unit tests for RaceThemeGallery.

PROJ-12 Phase 4: TDD tests written before extraction.
PROJ-166: Updated to use BaseGallery API (asset_buttons, on_asset_selected).
PROJ-322 Task 5.13 (APC-001-F13): the legacy `RaceThemeGallery.__new__` +
`patch.object(__init__, ...)` blocks now route through the shared
`make_ui_widget` factory via a module-scope `_bypass_init_gallery` helper.

Tests the race ship theme gallery panel functionality.
"""

import pytest
from unittest.mock import MagicMock

from tests.fixtures.ui_widget_factory import make_ui_widget


def _bypass_init_gallery(race_config, *, asset_buttons=None):
    """Build a `RaceThemeGallery` via the shared `make_ui_widget` factory.

    Replaces the inline `__new__` + `patch.object(__init__, ...)` blocks
    that wired ~5 attrs per test. The factory calls real `__init__` →
    `BaseGallery.__init__` → overridden `_create_content` → real
    theme-manager initialization (loads ship preview surfaces). With
    pygame_gui elements mocked the only side effect is the disk scan.

    Tests then overwrite `gallery.asset_buttons` for deterministic
    assertions.

    PROJ-322 Task 5.13 / APC-001-F13.
    """
    from game.ui.panels.race_theme_gallery import RaceThemeGallery

    gallery = make_ui_widget(
        RaceThemeGallery,
        race_config=race_config,
        x=0,
        y=0,
        width=600,
        height=400,
    )
    gallery.asset_buttons = asset_buttons if asset_buttons is not None else []
    return gallery


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_race_config():
    """Create a mock RaceConfig with theme_id property."""
    config = MagicMock()
    config.theme_id = None
    return config


@pytest.fixture
def mock_ui_manager():
    """Create a mock pygame_gui UIManager."""
    manager = MagicMock()
    return manager


@pytest.fixture
def mock_panel():
    """Create a mock UIPanel container."""
    panel = MagicMock()
    panel.get_relative_rect.return_value = MagicMock(
        width=600,
        height=400
    )
    return panel


# =============================================================================
# Test: RaceThemeGallery Import and Creation
# =============================================================================

# =============================================================================
# Test: Theme Selection
# =============================================================================

class TestThemeSelection:
    """Tests for theme selection functionality."""

    def test_on_asset_selected_updates_race_config(self, mock_race_config):
        """Selecting a theme updates race_config.theme_id via on_asset_selected."""
        gallery = _bypass_init_gallery(mock_race_config)

        gallery.on_asset_selected("terran")

        assert mock_race_config.theme_id == "terran"

    def test_on_asset_selected_calls_callback_if_provided(self, mock_race_config):
        """Selecting a theme calls the on_select callback if provided."""
        gallery = _bypass_init_gallery(mock_race_config)

        callback = MagicMock()
        gallery.on_select_callback = callback

        gallery.on_asset_selected("terran")

        callback.assert_called_once_with("terran")

    def test_on_asset_selected_no_callback_no_error(self, mock_race_config):
        """Selecting a theme with no callback doesn't raise an error."""
        gallery = _bypass_init_gallery(mock_race_config)

        # Should not raise
        gallery.on_asset_selected("terran")


# =============================================================================
# Test: Button Highlighting
# =============================================================================

class TestButtonHighlighting:
    """Tests for visual feedback on selection."""

    def test_on_asset_selected_highlights_selected_button(self, mock_race_config):
        """Selecting a theme highlights the corresponding button."""
        btn1 = MagicMock()
        btn2 = MagicMock()
        gallery = _bypass_init_gallery(
            mock_race_config,
            asset_buttons=[(btn1, "terran"), (btn2, "alien")],
        )

        gallery.on_asset_selected("terran")

        btn1.select.assert_called_once()
        btn2.unselect.assert_called_once()

    def test_on_asset_selected_deselects_other_buttons(self, mock_race_config):
        """Selecting a theme deselects all other buttons."""
        btn1 = MagicMock()
        btn2 = MagicMock()
        btn3 = MagicMock()
        gallery = _bypass_init_gallery(
            mock_race_config,
            asset_buttons=[
                (btn1, "terran"),
                (btn2, "alien"),
                (btn3, "robotic"),
            ],
        )

        gallery.on_asset_selected("alien")

        btn1.unselect.assert_called_once()
        btn2.select.assert_called_once()
        btn3.unselect.assert_called_once()


# =============================================================================
# Test: Configuration Binding
# =============================================================================

class TestConfigurationBinding:
    """Tests for setting values from config."""

    def test_set_from_config_selects_configured_theme(self, mock_race_config):
        """set_from_config selects the theme from race_config."""
        gallery = _bypass_init_gallery(mock_race_config)
        mock_race_config.theme_id = "terran"

        # Mock on_asset_selected to track call
        gallery.on_asset_selected = MagicMock()

        gallery.set_from_config()

        gallery.on_asset_selected.assert_called_once_with("terran")

    def test_set_from_config_no_theme_id_no_selection(self, mock_race_config):
        """set_from_config does nothing if no theme_id in config."""
        gallery = _bypass_init_gallery(mock_race_config)
        mock_race_config.theme_id = None  # No theme selected

        # Mock on_asset_selected to track call
        gallery.on_asset_selected = MagicMock()

        gallery.set_from_config()

        gallery.on_asset_selected.assert_not_called()


# =============================================================================
# Test: Button Click Handling
# =============================================================================

class TestButtonClickHandling:
    """Tests for button click event handling."""

    def test_handle_button_click_returns_true_for_theme_button(self, mock_race_config):
        """handle_button_click returns True when a theme button is clicked."""
        btn1 = MagicMock()
        btn2 = MagicMock()
        gallery = _bypass_init_gallery(
            mock_race_config,
            asset_buttons=[(btn1, "terran"), (btn2, "alien")],
        )

        result = gallery.handle_button_click(btn1)

        assert result is True

    def test_handle_button_click_returns_false_for_other_button(self, mock_race_config):
        """handle_button_click returns False when a different button is clicked."""
        btn1 = MagicMock()
        btn2 = MagicMock()
        other_btn = MagicMock()
        gallery = _bypass_init_gallery(
            mock_race_config,
            asset_buttons=[(btn1, "terran"), (btn2, "alien")],
        )

        result = gallery.handle_button_click(other_btn)

        assert result is False
