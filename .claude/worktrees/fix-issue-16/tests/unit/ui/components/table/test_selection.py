"""Tests for selection strategy classes."""

import pytest


class TestSingleSelect:
    """Tests for SingleSelect strategy."""

    def test_handle_click_selects_index(self):
        """handle_click should select the clicked index."""
        from game.ui.components.table.selection import SingleSelect

        strategy = SingleSelect()
        result = strategy.handle_click(5, False)

        assert result == {5}
        assert strategy.get_selected_indices() == {5}

    def test_handle_click_replaces_previous_selection(self):
        """Clicking a different index replaces the selection."""
        from game.ui.components.table.selection import SingleSelect

        strategy = SingleSelect()
        strategy.handle_click(5, False)
        result = strategy.handle_click(3, False)

        assert result == {3}
        assert strategy.get_selected_indices() == {3}

    def test_handle_click_ctrl_ignored(self):
        """Ctrl+click behaves same as regular click in SingleSelect."""
        from game.ui.components.table.selection import SingleSelect

        strategy = SingleSelect()
        strategy.handle_click(5, False)
        result = strategy.handle_click(3, True)  # Ctrl held

        assert result == {3}
        assert strategy.get_selected_indices() == {3}

    def test_clear_empties_selection(self):
        """clear() should empty the selection."""
        from game.ui.components.table.selection import SingleSelect

        strategy = SingleSelect()
        strategy.handle_click(5, False)
        strategy.clear()

        assert strategy.get_selected_indices() == set()

    def test_set_selected_sets_indices(self):
        """set_selected() should set specific indices."""
        from game.ui.components.table.selection import SingleSelect

        strategy = SingleSelect()
        strategy.set_selected({7})

        assert strategy.get_selected_indices() == {7}

    def test_initial_state_is_empty(self):
        """Initial state should have no selection."""
        from game.ui.components.table.selection import SingleSelect

        strategy = SingleSelect()
        assert strategy.get_selected_indices() == set()


class TestMultiSelect:
    """Tests for MultiSelect strategy."""

    def test_handle_click_selects_index(self):
        """handle_click without ctrl selects just that index."""
        from game.ui.components.table.selection import MultiSelect

        strategy = MultiSelect()
        result = strategy.handle_click(5, False)

        assert result == {5}
        assert strategy.get_selected_indices() == {5}

    def test_handle_click_ctrl_adds_to_selection(self):
        """Ctrl+click adds to existing selection."""
        from game.ui.components.table.selection import MultiSelect

        strategy = MultiSelect()
        strategy.handle_click(5, False)
        result = strategy.handle_click(3, True)  # Ctrl held

        assert result == {5, 3}
        assert strategy.get_selected_indices() == {5, 3}

    def test_handle_click_ctrl_toggles_off(self):
        """Ctrl+click on selected index toggles it off."""
        from game.ui.components.table.selection import MultiSelect

        strategy = MultiSelect()
        strategy.handle_click(5, False)
        strategy.handle_click(3, True)  # Add 3
        result = strategy.handle_click(5, True)  # Toggle off 5

        assert result == {3}
        assert strategy.get_selected_indices() == {3}

    def test_handle_click_ctrl_cannot_deselect_last(self):
        """Cannot deselect the last selected item with Ctrl+click."""
        from game.ui.components.table.selection import MultiSelect

        strategy = MultiSelect()
        strategy.handle_click(3, False)
        result = strategy.handle_click(3, True)  # Try to toggle off last

        assert result == {3}  # Still selected
        assert strategy.get_selected_indices() == {3}

    def test_clear_empties_selection(self):
        """clear() should empty the selection."""
        from game.ui.components.table.selection import MultiSelect

        strategy = MultiSelect()
        strategy.handle_click(5, False)
        strategy.handle_click(3, True)
        strategy.clear()

        assert strategy.get_selected_indices() == set()

    def test_set_selected_sets_indices(self):
        """set_selected() should set specific indices."""
        from game.ui.components.table.selection import MultiSelect

        strategy = MultiSelect()
        strategy.set_selected({1, 2, 3})

        assert strategy.get_selected_indices() == {1, 2, 3}

    def test_initial_state_is_empty(self):
        """Initial state should have no selection."""
        from game.ui.components.table.selection import MultiSelect

        strategy = MultiSelect()
        assert strategy.get_selected_indices() == set()

    def test_click_without_ctrl_replaces_selection(self):
        """Clicking without ctrl replaces entire selection."""
        from game.ui.components.table.selection import MultiSelect

        strategy = MultiSelect()
        strategy.handle_click(5, False)
        strategy.handle_click(3, True)
        result = strategy.handle_click(7, False)  # No ctrl

        assert result == {7}
        assert strategy.get_selected_indices() == {7}


class TestNoSelect:
    """Tests for NoSelect strategy."""

    def test_handle_click_returns_empty(self):
        """handle_click should always return empty set."""
        from game.ui.components.table.selection import NoSelect

        strategy = NoSelect()
        result = strategy.handle_click(5, False)

        assert result == set()

    def test_handle_click_with_ctrl_returns_empty(self):
        """handle_click with ctrl should also return empty set."""
        from game.ui.components.table.selection import NoSelect

        strategy = NoSelect()
        result = strategy.handle_click(3, True)

        assert result == set()

    def test_get_selected_indices_always_empty(self):
        """get_selected_indices should always return empty set."""
        from game.ui.components.table.selection import NoSelect

        strategy = NoSelect()
        strategy.handle_click(5, False)
        strategy.handle_click(3, True)

        assert strategy.get_selected_indices() == set()

    def test_set_selected_ignored(self):
        """set_selected should be ignored."""
        from game.ui.components.table.selection import NoSelect

        strategy = NoSelect()
        strategy.set_selected({1, 2, 3})

        assert strategy.get_selected_indices() == set()

    def test_clear_is_noop(self):
        """clear() should work without error."""
        from game.ui.components.table.selection import NoSelect

        strategy = NoSelect()
        strategy.clear()  # Should not raise

        assert strategy.get_selected_indices() == set()


class TestISelectionStrategy:
    """Tests for the base interface."""

    def test_base_class_raises_not_implemented(self):
        """Base class methods should raise NotImplementedError."""
        from game.ui.components.table.selection import ISelectionStrategy

        strategy = ISelectionStrategy()

        with pytest.raises(NotImplementedError):
            strategy.handle_click(0, False)

        with pytest.raises(NotImplementedError):
            strategy.get_selected_indices()

        with pytest.raises(NotImplementedError):
            strategy.clear()

        with pytest.raises(NotImplementedError):
            strategy.set_selected(set())
