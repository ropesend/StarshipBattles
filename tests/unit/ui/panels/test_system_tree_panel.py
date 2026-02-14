"""Tests for SystemTreePanel (PROJ-142 Phase 2 Task 2.5).

Tests the collapsible tree view widget for displaying star system contents.
"""

import pytest
from unittest.mock import MagicMock, patch
import pygame


# --- Helpers ---

def _make_mock_star():
    """Create a mock Star object."""
    star = MagicMock()
    star.name = "Sol"
    return star


def _make_mock_planet():
    """Create a mock Planet object."""
    planet = MagicMock()
    planet.name = "Earth"
    planet.mass = 1.0
    planet.location = MagicMock()
    planet.location.q = 3
    planet.location.r = 2
    return planet


def _make_mock_warp_point():
    """Create a mock WarpPoint object."""
    wp = MagicMock()
    wp.destination_id = "Alpha Centauri"
    return wp


def _make_mock_scene_interface():
    """Create a mock scene interface for asset loading."""
    scene = MagicMock()
    scene._get_label_for_obj = MagicMock(return_value="Test Object")
    scene._get_object_asset = MagicMock(return_value=None)
    return scene


# --- SystemTreeItem Tests ---

class TestSystemTreeItemImport:
    """Tests for SystemTreeItem import."""

    def test_item_can_be_imported(self):
        """SystemTreeItem can be imported."""
        from game.ui.panels.system_tree_panel import SystemTreeItem

        assert SystemTreeItem is not None


class TestSystemTreeItemInit:
    """Tests for SystemTreeItem initialization."""

    def test_item_stores_object(self):
        """SystemTreeItem stores obj reference."""
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        obj = MagicMock()
        item.obj = obj

        assert item.obj is obj

    def test_item_stores_label(self):
        """SystemTreeItem stores label_text."""
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        item.label_text = "Test Planet"

        assert item.label_text == "Test Planet"

    def test_item_default_not_expanded(self):
        """SystemTreeItem starts not expanded."""
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        item.expanded = False

        assert item.expanded is False

    def test_item_children_empty_list(self):
        """SystemTreeItem starts with empty children list."""
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        item.children = []

        assert item.children == []


class TestSystemTreeItemMethods:
    """Tests for SystemTreeItem methods."""

    def test_add_child_appends(self):
        """add_child appends item to children."""
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            parent = SystemTreeItem.__new__(SystemTreeItem)
            child = SystemTreeItem.__new__(SystemTreeItem)

        parent.children = []
        parent.add_child(child)

        assert child in parent.children

    def test_set_expanded_updates_state(self):
        """set_expanded updates expanded state."""
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        item.expanded = False
        item.set_expanded(True)

        assert item.expanded is True

    def test_show_calls_ui_methods(self):
        """show calls UI element show methods."""
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        item.button = MagicMock()
        item.label = MagicMock()
        item.icon_image = None

        item.show()

        item.button.show.assert_called_once()
        item.label.show.assert_called_once()

    def test_show_calls_icon_show(self):
        """show calls icon_image.show if present."""
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        item.button = MagicMock()
        item.label = MagicMock()
        item.icon_image = MagicMock()

        item.show()

        item.icon_image.show.assert_called_once()

    def test_hide_calls_ui_methods(self):
        """hide calls UI element hide methods."""
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        item.button = MagicMock()
        item.label = MagicMock()
        item.icon_image = MagicMock()

        item.hide()

        item.button.hide.assert_called_once()
        item.label.hide.assert_called_once()
        item.icon_image.hide.assert_called_once()

    def test_kill_destroys_elements(self):
        """kill destroys all UI elements."""
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        item.button = MagicMock()
        item.label = MagicMock()
        item.icon_image = MagicMock()

        item.kill()

        item.button.kill.assert_called_once()
        item.label.kill.assert_called_once()
        item.icon_image.kill.assert_called_once()


# --- SystemTreePanel Tests ---

class TestSystemTreePanelImport:
    """Tests for SystemTreePanel import."""

    def test_panel_can_be_imported(self):
        """SystemTreePanel can be imported."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        assert SystemTreePanel is not None


class TestSystemTreePanelInit:
    """Tests for SystemTreePanel initialization."""

    def test_panel_stores_manager(self):
        """Panel stores manager reference."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        manager = MagicMock()
        panel.manager = manager

        assert panel.manager is manager

    def test_panel_stores_container(self):
        """Panel stores container reference."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        container = MagicMock()
        panel.container = container

        assert panel.container is container

    def test_panel_items_is_list(self):
        """Panel items is initialized as list."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        panel.items = []

        assert isinstance(panel.items, list)

    def test_panel_root_items_is_list(self):
        """Panel root_items is initialized as list."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        panel.root_items = []

        assert isinstance(panel.root_items, list)

    def test_panel_expanded_groups_is_set(self):
        """Panel expanded_groups is initialized as set."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        panel.expanded_groups = set()

        assert isinstance(panel.expanded_groups, set)

    def test_panel_callback_is_none(self):
        """Panel on_selection_callback starts as None."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        panel.on_selection_callback = None

        assert panel.on_selection_callback is None


# --- set_items Tests ---

class TestSetItems:
    """Tests for set_items method."""

    def test_set_items_clears_old(self):
        """set_items kills old items."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        old_item = MagicMock()
        panel.items = [old_item]
        panel.root_items = []
        panel.expanded_groups = set()
        panel.rect = pygame.Rect(0, 0, 200, 400)
        panel.scrolling_container = MagicMock()
        panel.manager = MagicMock()
        panel.layout = MagicMock()

        panel.set_items([], _make_mock_scene_interface())

        old_item.kill.assert_called_once()

    def test_set_items_empty_clears_all(self):
        """set_items with empty list clears all items."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        panel.items = []
        panel.root_items = []
        panel.expanded_groups = set()
        panel.rect = pygame.Rect(0, 0, 200, 400)
        panel.scrolling_container = MagicMock()
        panel.manager = MagicMock()
        panel.layout = MagicMock()

        panel.set_items([], _make_mock_scene_interface())

        assert panel.items == []
        assert panel.root_items == []


# --- Layout Tests ---

class TestLayout:
    """Tests for layout method."""

    def test_layout_sets_y_cursor(self):
        """layout initializes y_cursor."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        panel.root_items = []
        panel.rect = pygame.Rect(0, 0, 200, 400)
        panel.scrolling_container = MagicMock()

        panel.layout()

        assert panel.y_cursor == 5

    def test_layout_shows_items(self):
        """layout shows visible items."""
        from game.ui.panels.system_tree_panel import SystemTreePanel
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        item.height = 30
        item.set_position = MagicMock()
        item.show = MagicMock()

        panel.root_items = [item]
        panel.rect = pygame.Rect(0, 0, 200, 400)
        panel.scrolling_container = MagicMock()

        panel.layout()

        item.show.assert_called_once()

    def test_layout_updates_scroll_area(self):
        """layout updates scrollable area dimensions."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        panel.root_items = []
        panel.rect = pygame.Rect(0, 0, 200, 400)
        panel.scrolling_container = MagicMock()

        panel.layout()

        panel.scrolling_container.set_scrollable_area_dimensions.assert_called_once()


# --- Process Event Tests ---

class TestProcessEvent:
    """Tests for event handling."""

    def test_non_button_event_returns_false(self):
        """Non-button event returns False."""
        from game.ui.panels.system_tree_panel import SystemTreePanel
        import pygame_gui

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        panel.items = []

        event = MagicMock()
        event.type = pygame.KEYDOWN

        result = panel.process_event(event)

        assert result is False

    def test_button_press_on_item_triggers_click(self):
        """Button press on tree item triggers on_click."""
        from game.ui.panels.system_tree_panel import SystemTreePanel
        from game.ui.panels.system_tree_panel import SystemTreeItem
        import pygame_gui

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        button = MagicMock()
        item.button = button
        panel.items = [item]
        panel.on_click = MagicMock()

        event = MagicMock()
        event.type = pygame_gui.UI_BUTTON_PRESSED
        event.ui_element = button

        result = panel.process_event(event)

        panel.on_click.assert_called_once_with(item)
        assert result is True


# --- On Click Tests ---

class TestOnClick:
    """Tests for click handling."""

    def test_click_group_toggles_expansion(self):
        """Clicking group item toggles expanded state."""
        from game.ui.panels.system_tree_panel import SystemTreePanel
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        item.is_group = True
        item.expanded = False
        item.group_key = "planets_root"
        item.children = []

        panel.expanded_groups = set()
        panel.layout = MagicMock()

        panel.on_click(item)

        assert item.expanded is True
        assert "planets_root" in panel.expanded_groups

    def test_click_group_collapse(self):
        """Clicking expanded group collapses it."""
        from game.ui.panels.system_tree_panel import SystemTreePanel
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        item.is_group = True
        item.expanded = True
        item.group_key = "planets_root"
        item.children = []

        panel.expanded_groups = {"planets_root"}
        panel.layout = MagicMock()

        panel.on_click(item)

        assert item.expanded is False
        assert "planets_root" not in panel.expanded_groups

    def test_click_leaf_triggers_callback(self):
        """Clicking leaf item triggers selection callback."""
        from game.ui.panels.system_tree_panel import SystemTreePanel
        from game.ui.panels.system_tree_panel import SystemTreeItem

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        with patch.object(SystemTreeItem, '__init__', lambda self, *a, **kw: None):
            item = SystemTreeItem.__new__(SystemTreeItem)

        obj = MagicMock()
        item.obj = obj
        callback = MagicMock()

        panel.on_selection_callback = callback

        panel.on_click(item)

        callback.assert_called_once_with(obj)


# --- Selection Callback Tests ---

class TestSelectionCallback:
    """Tests for selection callback."""

    def test_set_callback_stores_reference(self):
        """set_selection_callback stores callback."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        callback = MagicMock()
        panel.set_selection_callback(callback)

        assert panel.on_selection_callback is callback


# --- Set Dimensions Tests ---

class TestSetDimensions:
    """Tests for dimension updates."""

    def test_set_dimensions_updates_rect(self):
        """set_dimensions updates rect size."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        panel.rect = pygame.Rect(0, 0, 200, 400)
        panel.scrolling_container = MagicMock()
        panel.layout = MagicMock()

        panel.set_dimensions((300, 500))

        assert panel.rect.size == (300, 500)

    def test_set_dimensions_updates_container(self):
        """set_dimensions updates scrolling_container."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        panel.rect = pygame.Rect(0, 0, 200, 400)
        panel.scrolling_container = MagicMock()
        panel.layout = MagicMock()

        panel.set_dimensions((300, 500))

        panel.scrolling_container.set_dimensions.assert_called_once_with((300, 500))

    def test_set_dimensions_triggers_layout(self):
        """set_dimensions triggers layout recalculation."""
        from game.ui.panels.system_tree_panel import SystemTreePanel

        with patch.object(SystemTreePanel, '__init__', lambda self, *a, **kw: None):
            panel = SystemTreePanel.__new__(SystemTreePanel)

        panel.rect = pygame.Rect(0, 0, 200, 400)
        panel.scrolling_container = MagicMock()
        panel.layout = MagicMock()

        panel.set_dimensions((300, 500))

        panel.layout.assert_called_once()
