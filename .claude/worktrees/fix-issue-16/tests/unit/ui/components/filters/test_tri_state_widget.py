"""Tests for TriStateFilterWidget."""
import pytest
from unittest.mock import MagicMock, patch, call

import pygame

from game.ui.filters.filter_state import FilterState


class TestTriStateFilterWidget:
    """Tests for the tri-state radio button filter widget."""

    @pytest.fixture
    def mock_manager(self):
        return MagicMock()

    @pytest.fixture
    def mock_container(self):
        container = MagicMock()
        container.get_relative_rect.return_value = pygame.Rect(0, 0, 300, 400)
        return container

    @pytest.fixture
    def widget_rect(self):
        return pygame.Rect(0, 0, 250, 30)

    @patch("game.ui.components.filters.tri_state_widget.UIButton")
    @patch("game.ui.components.filters.tri_state_widget.UILabel")
    def test_initial_state_is_ignore(
        self, mock_label_cls, mock_btn_cls, mock_manager, mock_container, widget_rect
    ):
        from game.ui.components.filters.tri_state_widget import TriStateFilterWidget

        widget = TriStateFilterWidget("warp", "Warp Capable", widget_rect, mock_manager, mock_container)
        assert widget.current_state is FilterState.IGNORE

    @patch("game.ui.components.filters.tri_state_widget.UIButton")
    @patch("game.ui.components.filters.tri_state_widget.UILabel")
    def test_creates_label_and_three_buttons(
        self, mock_label_cls, mock_btn_cls, mock_manager, mock_container, widget_rect
    ):
        from game.ui.components.filters.tri_state_widget import TriStateFilterWidget

        widget = TriStateFilterWidget("warp", "Warp Capable", widget_rect, mock_manager, mock_container)
        mock_label_cls.assert_called_once()
        assert mock_btn_cls.call_count == 3

    @patch("game.ui.components.filters.tri_state_widget.UIButton")
    @patch("game.ui.components.filters.tri_state_widget.UILabel")
    def test_set_state_to_yes(
        self, mock_label_cls, mock_btn_cls, mock_manager, mock_container, widget_rect
    ):
        from game.ui.components.filters.tri_state_widget import TriStateFilterWidget

        widget = TriStateFilterWidget("warp", "Warp Capable", widget_rect, mock_manager, mock_container)
        widget.set_state(FilterState.YES)
        assert widget.current_state is FilterState.YES

    @patch("game.ui.components.filters.tri_state_widget.UIButton")
    @patch("game.ui.components.filters.tri_state_widget.UILabel")
    def test_set_state_to_no(
        self, mock_label_cls, mock_btn_cls, mock_manager, mock_container, widget_rect
    ):
        from game.ui.components.filters.tri_state_widget import TriStateFilterWidget

        widget = TriStateFilterWidget("warp", "Warp Capable", widget_rect, mock_manager, mock_container)
        widget.set_state(FilterState.NO)
        assert widget.current_state is FilterState.NO

    @patch("game.ui.components.filters.tri_state_widget.UIButton")
    @patch("game.ui.components.filters.tri_state_widget.UILabel")
    def test_set_state_to_ignore(
        self, mock_label_cls, mock_btn_cls, mock_manager, mock_container, widget_rect
    ):
        from game.ui.components.filters.tri_state_widget import TriStateFilterWidget

        widget = TriStateFilterWidget("warp", "Warp Capable", widget_rect, mock_manager, mock_container)
        widget.set_state(FilterState.YES)
        widget.set_state(FilterState.IGNORE)
        assert widget.current_state is FilterState.IGNORE

    @patch("game.ui.components.filters.tri_state_widget.UIButton")
    @patch("game.ui.components.filters.tri_state_widget.UILabel")
    def test_set_state_updates_visuals(
        self, mock_label_cls, mock_btn_cls, mock_manager, mock_container, widget_rect
    ):
        from game.ui.components.filters.tri_state_widget import TriStateFilterWidget

        # Each UIButton() call returns a new mock
        btn_yes = MagicMock()
        btn_no = MagicMock()
        btn_ignore = MagicMock()
        mock_btn_cls.side_effect = [btn_yes, btn_no, btn_ignore]

        widget = TriStateFilterWidget("warp", "Warp Capable", widget_rect, mock_manager, mock_container)

        # Initial state: IGNORE — btn_ignore should be selected
        btn_ignore.select.assert_called()

        # Reset mocks
        btn_yes.reset_mock()
        btn_no.reset_mock()
        btn_ignore.reset_mock()

        # Switch to YES
        widget.set_state(FilterState.YES)
        btn_yes.select.assert_called()
        btn_no.unselect.assert_called()
        btn_ignore.unselect.assert_called()

    @patch("game.ui.components.filters.tri_state_widget.UIButton")
    @patch("game.ui.components.filters.tri_state_widget.UILabel")
    def test_kill_destroys_all_children(
        self, mock_label_cls, mock_btn_cls, mock_manager, mock_container, widget_rect
    ):
        from game.ui.components.filters.tri_state_widget import TriStateFilterWidget

        mock_label = MagicMock()
        mock_label_cls.return_value = mock_label
        btn_yes = MagicMock()
        btn_no = MagicMock()
        btn_ignore = MagicMock()
        mock_btn_cls.side_effect = [btn_yes, btn_no, btn_ignore]

        widget = TriStateFilterWidget("warp", "Warp Capable", widget_rect, mock_manager, mock_container)
        widget.kill()

        mock_label.kill.assert_called_once()
        btn_yes.kill.assert_called_once()
        btn_no.kill.assert_called_once()
        btn_ignore.kill.assert_called_once()

    @patch("game.ui.components.filters.tri_state_widget.UIButton")
    @patch("game.ui.components.filters.tri_state_widget.UILabel")
    def test_attribute_name_stored(
        self, mock_label_cls, mock_btn_cls, mock_manager, mock_container, widget_rect
    ):
        from game.ui.components.filters.tri_state_widget import TriStateFilterWidget

        widget = TriStateFilterWidget("warp_capable", "Warp Capable", widget_rect, mock_manager, mock_container)
        assert widget.attribute_name == "warp_capable"
