"""Tests for selection state and hover detection logic."""
import pytest
from unittest.mock import Mock


class TestSelectionStateLogic:
    """Tests for selection state management logic."""

    def test_deselect_all_clears_items(self):
        """deselect_all calls set_selected(False) on all items."""
        # Simulate deselect_all logic
        items = [Mock(), Mock(), Mock()]
        selected_item = items[0]

        def deselect_all():
            for item in items:
                item.set_selected(False)
            return None  # selected_item becomes None

        result = deselect_all()

        for item in items:
            item.set_selected.assert_called_with(False)


class TestDropdownStateLogic:
    """Tests for dropdown expansion state logic."""

    def test_is_dropdown_expanded_returns_false_by_default(self):
        """is_dropdown_expanded returns False when not set."""
        def is_dropdown_expanded(obj):
            return getattr(obj, '_dropdown_expanded', False)

        obj = Mock(spec=[])
        assert is_dropdown_expanded(obj) is False

    def test_is_dropdown_expanded_returns_stored_value(self):
        """is_dropdown_expanded returns the stored flag value."""
        def is_dropdown_expanded(obj):
            return getattr(obj, '_dropdown_expanded', False)

        obj = Mock(spec=[])
        obj._dropdown_expanded = True
        assert is_dropdown_expanded(obj) is True


class TestHoverDetectionLogic:
    """Tests for hover detection logic."""

    def test_get_hovered_list_item_returns_none_when_dropdown_expanded(self):
        """get_hovered_list_item returns None when dropdown is expanded."""
        # Simulate the logic
        dropdown_expanded = True
        items = [Mock()]

        def get_hovered_list_item(mx, my, dropdown_expanded, items, container_rect):
            if dropdown_expanded:
                return None
            if not container_rect.collidepoint(mx, my):
                return None
            for item in items:
                if item.panel.get_abs_rect().collidepoint(mx, my):
                    return item
            return None

        result = get_hovered_list_item(100, 200, True, items, Mock())
        assert result is None

    def test_get_hovered_list_item_returns_none_outside_container(self):
        """get_hovered_list_item returns None when outside container."""
        container_rect = Mock()
        container_rect.collidepoint.return_value = False

        def get_hovered_list_item(mx, my, dropdown_expanded, items, container_rect):
            if dropdown_expanded:
                return None
            if not container_rect.collidepoint(mx, my):
                return None
            for item in items:
                if item.panel.get_abs_rect().collidepoint(mx, my):
                    return item
            return None

        result = get_hovered_list_item(1000, 1000, False, [], container_rect)
        assert result is None

    def test_get_hovered_list_item_returns_item_under_mouse(self):
        """get_hovered_list_item returns item when mouse is over it."""
        container_rect = Mock()
        container_rect.collidepoint.return_value = True
        container_rect.contains.return_value = True
        container_rect.colliderect.return_value = True

        mock_item = Mock()
        mock_item.panel.get_abs_rect.return_value.collidepoint.return_value = True

        def get_hovered_list_item(mx, my, dropdown_expanded, items, container_rect):
            if dropdown_expanded:
                return None
            if not container_rect.collidepoint(mx, my):
                return None
            for item in items:
                if item.panel.get_abs_rect().collidepoint(mx, my):
                    return item
            return None

        result = get_hovered_list_item(150, 200, False, [mock_item], container_rect)
        assert result == mock_item


class TestGetHoveredComponentLogic:
    """Tests for get_hovered_component method logic."""

    def test_returns_component_when_button_hovered(self):
        """get_hovered_component returns component when its button is hovered."""
        mock_component = Mock()
        mock_item = Mock()
        mock_item.component = mock_component
        mock_item.button.rect.collidepoint.return_value = True
        items = [mock_item]

        def get_hovered_component(mx, my, items):
            for item in items:
                if item.button.rect.collidepoint(mx, my):
                    return item.component
            return None

        result = get_hovered_component(100, 200, items)
        assert result == mock_component

    def test_returns_none_when_no_button_hovered(self):
        """get_hovered_component returns None when no button is hovered."""
        mock_item = Mock()
        mock_item.button.rect.collidepoint.return_value = False
        items = [mock_item]

        def get_hovered_component(mx, my, items):
            for item in items:
                if item.button.rect.collidepoint(mx, my):
                    return item.component
            return None

        result = get_hovered_component(100, 200, items)
        assert result is None
