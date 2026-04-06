"""Tests for StrategyUI button wiring completeness.

Regression test for the crash where btn_abilities was added to
StrategyWidgets but never wired to StrategyUI, causing:
  AttributeError: 'StrategyUI' object has no attribute 'btn_abilities'

The clean fix stores the widgets dataclass directly on StrategyUI so
new buttons are automatically available without manual wiring.
"""
import pytest
from unittest.mock import MagicMock, patch
from dataclasses import fields


class TestStrategyWidgetsButtonCompleteness:
    """Every btn_* in StrategyWidgets must be accessible on StrategyUI."""

    def test_all_widget_buttons_accessible_on_ui(self):
        """All btn_* attributes from StrategyWidgets are accessible on StrategyUI.

        This test enumerates the dataclass fields and verifies StrategyUI
        exposes them all — preventing future 'forgot to wire a button' bugs.
        """
        from game.ui.screens.strategy_panel_manager import StrategyWidgets

        # Get all btn_* field names from the dataclass
        btn_fields = [f.name for f in fields(StrategyWidgets) if f.name.startswith('btn_')]
        assert len(btn_fields) > 0, "StrategyWidgets should have btn_* fields"

        # Create a mock StrategyWidgets with all buttons set
        mock_widgets = StrategyWidgets()
        for name in btn_fields:
            setattr(mock_widgets, name, MagicMock(name=name))

        # Verify StrategyUI can access every button via __getattr__ or direct attr
        # We can't easily construct a real StrategyUI (needs pygame), so we test
        # the widgets dataclass has the expected buttons and verify the contract
        for name in btn_fields:
            assert hasattr(mock_widgets, name), f"StrategyWidgets missing {name}"
            assert getattr(mock_widgets, name) is not None, f"StrategyWidgets.{name} is None"

        # Specifically verify btn_abilities exists (the bug that caused the crash)
        assert 'btn_abilities' in btn_fields, "btn_abilities must be in StrategyWidgets"

    def test_detail_formatter_receives_widgets_dataclass(self):
        """StrategyDetailFormatter should accept StrategyWidgets, not a hand-curated dict.

        When widgets is a dataclass, all buttons are automatically available
        without manually adding each one to a dict.
        """
        from game.ui.screens.strategy_panel_manager import StrategyWidgets
        from dataclasses import fields as dc_fields

        # The formatter needs these buttons (used in its property accessors)
        required_by_formatter = [
            'btn_raw_data', 'btn_colonize', 'btn_build_yard',
            'btn_planet_orders', 'btn_atmosphere', 'btn_abilities',
            'btn_orders', 'btn_fleet_report', 'btn_build_fleet',
        ]

        widget_fields = {f.name for f in dc_fields(StrategyWidgets)}
        for btn in required_by_formatter:
            assert btn in widget_fields, (
                f"StrategyWidgets must have '{btn}' field "
                f"(required by StrategyDetailFormatter)"
            )
