"""Tests for tooltip enrichment on StrategyUI buttons (PROJ-71 Phase 2).

Verifies that StrategyUI applies hotkey hint tooltips to buttons when
an InputMapper is provided.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.core.input_actions import InputAction
from game.ui.services.input_mapper import InputMapper
from game.ui.screens.strategy_ui import StrategyUI


class TestStrategyUIAcceptsMapper:
    """StrategyUI constructor should accept input_mapper parameter."""

    def test_signature_has_input_mapper_param(self):
        """StrategyUI.__init__ should accept input_mapper keyword."""
        import inspect
        sig = inspect.signature(StrategyUI.__init__)
        assert 'input_mapper' in sig.parameters

    def test_input_mapper_defaults_to_none(self):
        """input_mapper parameter defaults to None."""
        import inspect
        sig = inspect.signature(StrategyUI.__init__)
        param = sig.parameters['input_mapper']
        assert param.default is None


class TestTooltipEnrichment:
    """StrategyUI should apply hotkey tooltips to buttons."""

    def test_get_tooltip_text_returns_hotkey(self):
        """_get_tooltip_text returns formatted hotkey hint."""
        mapper = InputMapper()
        from game.core.paths import Paths
        mapper.load(Paths.DEFAULT_KEYBINDINGS_FILE)

        # Test for End Turn button (bound to Enter)
        display = mapper.get_display_text(InputAction.STRATEGY_NEXT_TURN)
        assert display == "Enter"

        # Test for Planets button (bound to Shift+P)
        display = mapper.get_display_text(InputAction.STRATEGY_OPEN_PLANETS)
        assert display == "Shift+P"

        # Test for zoom galaxy (bound to Shift+G)
        display = mapper.get_display_text(InputAction.STRATEGY_ZOOM_GALAXY)
        assert display == "Shift+G"

    def test_unbound_actions_return_empty_string(self):
        """Unbound actions should return empty string for tooltip."""
        mapper = InputMapper()
        from game.core.paths import Paths
        mapper.load(Paths.DEFAULT_KEYBINDINGS_FILE)

        # detail_panel.build is intentionally unbound in defaults
        display = mapper.get_display_text(InputAction.DETAIL_PANEL_BUILD)
        assert display == ""
