"""Tests for PanelFactory utility class.

PROJ-204 Phase 5: Test panel bootstrap factory.
"""
import pytest
from unittest.mock import MagicMock, patch
import pygame


class TestPanelFactory:
    """Tests for PanelFactory.create_titled_panel method."""

    @pytest.fixture
    def mock_manager(self):
        """Create a mock pygame_gui manager."""
        return MagicMock()

    def test_create_titled_panel_returns_tuple(self, mock_manager):
        """Factory returns a (panel, label) tuple."""
        from game.ui.widgets.panel_factory import PanelFactory

        with patch('game.ui.widgets.panel_factory.UIPanel') as mock_panel_cls, \
             patch('game.ui.widgets.panel_factory.UILabel') as mock_label_cls:
            mock_panel = MagicMock()
            mock_label = MagicMock()
            mock_panel_cls.return_value = mock_panel
            mock_label_cls.return_value = mock_label

            result = PanelFactory.create_titled_panel(
                rect=pygame.Rect(0, 0, 300, 400),
                manager=mock_manager,
                title="Test Title",
                object_id="#test_panel"
            )

            assert isinstance(result, tuple)
            assert len(result) == 2
            assert result[0] == mock_panel
            assert result[1] == mock_label

    def test_create_titled_panel_creates_panel_with_correct_params(self, mock_manager):
        """Panel is created with correct rect, manager, and object_id."""
        from game.ui.widgets.panel_factory import PanelFactory

        rect = pygame.Rect(10, 20, 300, 400)

        with patch('game.ui.widgets.panel_factory.UIPanel') as mock_panel_cls, \
             patch('game.ui.widgets.panel_factory.UILabel'):

            PanelFactory.create_titled_panel(
                rect=rect,
                manager=mock_manager,
                title="Title",
                object_id="#my_panel"
            )

            mock_panel_cls.assert_called_once()
            call_kwargs = mock_panel_cls.call_args[1]
            assert call_kwargs['relative_rect'] == rect
            assert call_kwargs['manager'] == mock_manager
            assert call_kwargs['object_id'] == "#my_panel"

    def test_create_titled_panel_creates_label_inside_panel(self, mock_manager):
        """Label is created inside the panel as container."""
        from game.ui.widgets.panel_factory import PanelFactory

        with patch('game.ui.widgets.panel_factory.UIPanel') as mock_panel_cls, \
             patch('game.ui.widgets.panel_factory.UILabel') as mock_label_cls:
            mock_panel = MagicMock()
            mock_panel_cls.return_value = mock_panel

            PanelFactory.create_titled_panel(
                rect=pygame.Rect(0, 0, 300, 400),
                manager=mock_manager,
                title="Ship Structure",
                object_id="#panel"
            )

            mock_label_cls.assert_called_once()
            call_kwargs = mock_label_cls.call_args[1]
            assert call_kwargs['text'] == "Ship Structure"
            assert call_kwargs['manager'] == mock_manager
            assert call_kwargs['container'] == mock_panel

    def test_create_titled_panel_label_positioned_at_top(self, mock_manager):
        """Label is positioned at the top of the panel."""
        from game.ui.widgets.panel_factory import PanelFactory

        with patch('game.ui.widgets.panel_factory.UIPanel'), \
             patch('game.ui.widgets.panel_factory.UILabel') as mock_label_cls:

            PanelFactory.create_titled_panel(
                rect=pygame.Rect(0, 0, 300, 400),
                manager=mock_manager,
                title="Title",
                object_id="#panel"
            )

            call_kwargs = mock_label_cls.call_args[1]
            label_rect = call_kwargs['relative_rect']
            # Label should be near top
            assert label_rect.y <= 10
            # Label should have reasonable width
            assert label_rect.width >= 100

    def test_create_titled_panel_with_no_title(self, mock_manager):
        """Panel without title doesn't create label."""
        from game.ui.widgets.panel_factory import PanelFactory

        with patch('game.ui.widgets.panel_factory.UIPanel') as mock_panel_cls, \
             patch('game.ui.widgets.panel_factory.UILabel') as mock_label_cls:
            mock_panel = MagicMock()
            mock_panel_cls.return_value = mock_panel

            result = PanelFactory.create_titled_panel(
                rect=pygame.Rect(0, 0, 300, 400),
                manager=mock_manager,
                title=None,
                object_id="#panel"
            )

            mock_label_cls.assert_not_called()
            assert result == (mock_panel, None)
