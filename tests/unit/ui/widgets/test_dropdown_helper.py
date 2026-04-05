"""Tests for the shared dropdown recreation utility.

Phase 3 of the Design Workshop tech debt plan.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestRecreateDropdown:
    """Tests for recreate_dropdown() utility function."""

    def _make_mock_dropdown(self, rect=None):
        """Create a mock UIDropDownMenu."""
        dd = MagicMock()
        dd.relative_rect = rect or MagicMock()
        dd.ui_container = MagicMock()
        return dd

    def test_preserves_rect(self):
        """New dropdown uses the old dropdown's rect."""
        from game.ui.widgets.dropdown_helper import recreate_dropdown

        old_rect = MagicMock()
        old_dd = self._make_mock_dropdown(rect=old_rect)
        manager = MagicMock()

        with patch('game.ui.widgets.dropdown_helper.UIDropDownMenu') as MockDD:
            MockDD.return_value = MagicMock()
            recreate_dropdown(old_dd, ['a', 'b'], 'a', manager)
            _, kwargs = MockDD.call_args
            assert kwargs['relative_rect'] is old_rect

    def test_preserves_container(self):
        """New dropdown uses the old dropdown's container."""
        from game.ui.widgets.dropdown_helper import recreate_dropdown

        container = MagicMock()
        old_dd = self._make_mock_dropdown()
        old_dd.ui_container = container
        manager = MagicMock()

        with patch('game.ui.widgets.dropdown_helper.UIDropDownMenu') as MockDD:
            MockDD.return_value = MagicMock()
            recreate_dropdown(old_dd, ['a', 'b'], 'a', manager)
            _, kwargs = MockDD.call_args
            assert kwargs['container'] is container

    def test_kills_old_dropdown(self):
        """Old dropdown is killed before creating the new one."""
        from game.ui.widgets.dropdown_helper import recreate_dropdown

        old_dd = self._make_mock_dropdown()
        manager = MagicMock()

        with patch('game.ui.widgets.dropdown_helper.UIDropDownMenu'):
            recreate_dropdown(old_dd, ['a', 'b'], 'a', manager)
            old_dd.kill.assert_called_once()

    def test_selects_valid_option(self):
        """When selected value is in options, it's used."""
        from game.ui.widgets.dropdown_helper import recreate_dropdown

        old_dd = self._make_mock_dropdown()
        manager = MagicMock()

        with patch('game.ui.widgets.dropdown_helper.UIDropDownMenu') as MockDD:
            MockDD.return_value = MagicMock()
            recreate_dropdown(old_dd, ['alpha', 'beta'], 'beta', manager)
            _, kwargs = MockDD.call_args
            assert kwargs['starting_option'] == 'beta'

    def test_falls_back_to_first_option(self):
        """When selected value is not in options, falls back to first."""
        from game.ui.widgets.dropdown_helper import recreate_dropdown

        old_dd = self._make_mock_dropdown()
        manager = MagicMock()

        with patch('game.ui.widgets.dropdown_helper.UIDropDownMenu') as MockDD:
            MockDD.return_value = MagicMock()
            recreate_dropdown(old_dd, ['alpha', 'beta'], 'missing', manager)
            _, kwargs = MockDD.call_args
            assert kwargs['starting_option'] == 'alpha'

    def test_handles_empty_options(self):
        """Empty options list uses empty string as fallback."""
        from game.ui.widgets.dropdown_helper import recreate_dropdown

        old_dd = self._make_mock_dropdown()
        manager = MagicMock()

        with patch('game.ui.widgets.dropdown_helper.UIDropDownMenu') as MockDD:
            MockDD.return_value = MagicMock()
            recreate_dropdown(old_dd, [], 'x', manager)
            _, kwargs = MockDD.call_args
            assert kwargs['options_list'] == ['']
            assert kwargs['starting_option'] == ''

    def test_none_dropdown_returns_none(self):
        """Passing None as old_dropdown returns None without error."""
        from game.ui.widgets.dropdown_helper import recreate_dropdown

        result = recreate_dropdown(None, ['a'], 'a', MagicMock())
        assert result is None

    def test_container_override(self):
        """Explicit container parameter overrides old dropdown's container."""
        from game.ui.widgets.dropdown_helper import recreate_dropdown

        old_dd = self._make_mock_dropdown()
        override_container = MagicMock()
        manager = MagicMock()

        with patch('game.ui.widgets.dropdown_helper.UIDropDownMenu') as MockDD:
            MockDD.return_value = MagicMock()
            recreate_dropdown(old_dd, ['a'], 'a', manager, container=override_container)
            _, kwargs = MockDD.call_args
            assert kwargs['container'] is override_container
