"""Tests for UIElementRegistry helper class.

PROJ-204 Phase 5: Test element registry for UI cleanup.
"""
import pytest
from unittest.mock import MagicMock


class TestUIElementRegistry:
    """Tests for UIElementRegistry class."""

    def test_register_adds_element(self):
        """register() adds element to internal list."""
        from game.ui.widgets.ui_element_registry import UIElementRegistry

        registry = UIElementRegistry()
        element = MagicMock()

        registry.register(element)

        assert element in registry._elements

    def test_register_returns_element(self):
        """register() returns the element for chaining."""
        from game.ui.widgets.ui_element_registry import UIElementRegistry

        registry = UIElementRegistry()
        element = MagicMock()

        result = registry.register(element)

        assert result is element

    def test_kill_all_calls_kill_on_each(self):
        """kill_all() calls kill() on each registered element."""
        from game.ui.widgets.ui_element_registry import UIElementRegistry

        registry = UIElementRegistry()
        elem1 = MagicMock()
        elem2 = MagicMock()
        elem3 = MagicMock()

        registry.register(elem1)
        registry.register(elem2)
        registry.register(elem3)

        registry.kill_all()

        elem1.kill.assert_called_once()
        elem2.kill.assert_called_once()
        elem3.kill.assert_called_once()

    def test_kill_all_clears_list(self):
        """kill_all() clears the internal element list."""
        from game.ui.widgets.ui_element_registry import UIElementRegistry

        registry = UIElementRegistry()
        registry.register(MagicMock())
        registry.register(MagicMock())

        registry.kill_all()

        assert len(registry._elements) == 0

    def test_clear_does_not_kill(self):
        """clear() removes elements without calling kill()."""
        from game.ui.widgets.ui_element_registry import UIElementRegistry

        registry = UIElementRegistry()
        element = MagicMock()
        registry.register(element)

        registry.clear()

        element.kill.assert_not_called()
        assert len(registry._elements) == 0

    def test_len_returns_element_count(self):
        """len() returns number of registered elements."""
        from game.ui.widgets.ui_element_registry import UIElementRegistry

        registry = UIElementRegistry()
        registry.register(MagicMock())
        registry.register(MagicMock())

        assert len(registry) == 2

    def test_iter_yields_elements(self):
        """Registry is iterable over elements."""
        from game.ui.widgets.ui_element_registry import UIElementRegistry

        registry = UIElementRegistry()
        elem1 = MagicMock()
        elem2 = MagicMock()
        registry.register(elem1)
        registry.register(elem2)

        elements = list(registry)

        assert elements == [elem1, elem2]
