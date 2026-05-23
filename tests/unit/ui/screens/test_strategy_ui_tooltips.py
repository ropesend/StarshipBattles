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
        """get_display_text returns the formatted hotkey hint for an action.

        PROJ-478 Phase 2: rewritten to inject bindings rather than asserting
        against the production ``DEFAULT_KEYBINDINGS_FILE``. The mapping logic
        is what this test exercises; the production defaults file is exercised
        by integration tests and by ``test_default_keybindings_file_loads``.
        """
        from game.core.input_actions import KeyBinding

        mapper = InputMapper()
        # Seed empties for every action.
        mapper.load(None)
        # Inject controlled bindings — covers the three modifier shapes
        # (none, single-mod, mixed) that the production tooltip code must
        # render correctly.
        mapper.set_binding(
            InputAction.STRATEGY_NEXT_TURN,
            KeyBinding(key="K_RETURN", modifiers=frozenset()),
        )
        mapper.set_binding(
            InputAction.STRATEGY_OPEN_PLANETS,
            KeyBinding(key="K_p", modifiers=frozenset({"shift"})),
        )
        mapper.set_binding(
            InputAction.STRATEGY_ZOOM_GALAXY,
            KeyBinding(key="K_g", modifiers=frozenset({"shift"})),
        )

        assert mapper.get_display_text(InputAction.STRATEGY_NEXT_TURN) == "Enter"
        assert mapper.get_display_text(InputAction.STRATEGY_OPEN_PLANETS) == "Shift+P"
        assert mapper.get_display_text(InputAction.STRATEGY_ZOOM_GALAXY) == "Shift+G"

    def test_unbound_actions_return_empty_string(self):
        """Unbound actions should return empty string for tooltip."""
        mapper = InputMapper()
        # Empty load -> every action unbound; no dependency on production
        # defaults file.
        mapper.load(None)

        assert mapper.get_display_text(InputAction.DETAIL_PANEL_BUILD) == ""
