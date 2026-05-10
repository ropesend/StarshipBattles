"""Tests for UIConfig.

Moved from tests/unit/core/test_config.py to respect layer boundaries:
UIConfig is UI-layer code (game.ui.config), not core-layer.
"""
from game.ui.config import UIConfig


class TestUIConfig:
    """Tests for UIConfig (game.ui.config)."""

    def test_panel_dimensions(self):
        """Panel dimension values exist."""
        assert hasattr(UIConfig, 'PANEL_PADDING')
        assert isinstance(UIConfig.PANEL_PADDING, int)

    def test_toast_dimensions(self):
        """Toast notification dimensions exist and have correct values."""
        assert UIConfig.TOAST_WIDTH == 300
        assert UIConfig.TOAST_HEIGHT == 60

    def test_confirmation_dialog_dimensions(self):
        """Confirmation dialog dimensions exist and have correct values."""
        assert UIConfig.CONFIRM_DIALOG_WIDTH == 400
        assert UIConfig.CONFIRM_DIALOG_HEIGHT == 200

    def test_uiconfig_location(self):
        """UIConfig is in game.ui.config, not game.core.config (PROJ-113)."""
        assert UIConfig.PANEL_PADDING == 5
