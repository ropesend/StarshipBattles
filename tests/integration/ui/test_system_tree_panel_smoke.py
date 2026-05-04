"""SystemTreePanel integration smoke test.

PROJ-321 deleted the 664-LOC ``tests/unit/ui/panels/test_system_tree_panel.py``
because every test was a ``__new__`` bypass-init that exercised no real
production behavior. The deletion is defensible — those tests had no value —
but it removed the only systematic check that ``SystemTreePanel`` still
constructs and rebuilds.

This smoke test, added by PROJ-326 Phase 2 Task 2.2, restores that floor of
coverage. It exercises the panel against a real ``pygame_gui.UIManager`` (no
``__new__`` bypass) and asserts on observable behavior:

  - The panel constructs and registers a scrolling container.
  - ``set_items([], ...)`` is a no-op (empty content path).
  - ``set_items([...], ...)`` builds tree items from a real content list.
  - ``set_items`` called twice tears down the previous items (BUG-26 guard:
    we mutate ``self.items`` while iterating without crashing).

If a future change breaks panel construction the suite catches it here.

Origin: PROJ-321 review MAJ-001 + PROJ-326 Phase 2 Task 2.2.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pytest

from game.ui.panels.system_tree_panel import SystemTreePanel


@pytest.fixture
def stub_scene_interface():
    """Stand-in for the real scene_interface DI handle.

    SystemTreePanel.set_items only reaches into ``_get_label_for_obj`` and
    ``_get_object_asset``. A MagicMock satisfies both without dragging the
    full strategy-screen scene into the test.
    """
    iface = MagicMock()
    iface._get_label_for_obj.side_effect = lambda obj: getattr(obj, "name", "Item")
    iface._get_object_asset.return_value = pygame.Surface((16, 16))
    iface.scene = None  # No empire context for hazard hints
    return iface


class _OpaqueObj:
    """Plain object that fails every is_* protocol check.

    SystemTreePanel.set_items routes such objects through the "others" bucket
    (line 220+ in system_tree_panel.py) — the simplest path to exercise.

    Real ``MagicMock`` instances auto-create attributes on access, which makes
    them satisfy ``hasattr(obj, 'planet_type')`` etc. and get misclassified.
    A plain class with only ``name`` avoids that.
    """

    def __init__(self, name: str) -> None:
        self.name = name


def _opaque_obj(name: str) -> _OpaqueObj:
    return _OpaqueObj(name)


def test_system_tree_panel_constructs(ui_manager):
    """Panel constructs without error, with a real UIManager + container."""
    panel = SystemTreePanel(
        relative_rect=pygame.Rect(0, 0, 300, 400),
        manager=ui_manager,
        container=None,
    )
    assert panel.scrolling_container is not None
    assert panel.items == []
    assert panel.root_items == []


def test_set_items_empty_is_a_noop(ui_manager, stub_scene_interface):
    """An empty content list is a clean no-op (early-return path)."""
    panel = SystemTreePanel(
        relative_rect=pygame.Rect(0, 0, 300, 400),
        manager=ui_manager,
        container=None,
    )
    panel.set_items([], stub_scene_interface)
    assert panel.items == []
    assert panel.root_items == []


def test_set_items_with_content_populates_tree(ui_manager, stub_scene_interface):
    """With opaque (non-planet/star/warp) content, items land in the 'others' bucket."""
    panel = SystemTreePanel(
        relative_rect=pygame.Rect(0, 0, 300, 400),
        manager=ui_manager,
        container=None,
    )
    contents = [_opaque_obj("Alpha"), _opaque_obj("Beta")]

    panel.set_items(contents, stub_scene_interface)

    assert len(panel.items) >= 2  # at minimum one tree row per object
    assert len(panel.root_items) >= 2


def test_set_items_twice_clears_previous_items(ui_manager, stub_scene_interface):
    """Rebuilding the tree (BUG-26 guard): no AttributeError / RuntimeError on re-set."""
    panel = SystemTreePanel(
        relative_rect=pygame.Rect(0, 0, 300, 400),
        manager=ui_manager,
        container=None,
    )
    panel.set_items([_opaque_obj("First")], stub_scene_interface)
    first_count = len(panel.items)
    assert first_count >= 1

    panel.set_items([_opaque_obj("Second"), _opaque_obj("Third")], stub_scene_interface)

    # Old items were cleared, new items are present.
    assert len(panel.items) >= 2
    # Verify the previous "First" item is gone — its label should not appear.
    labels = [getattr(item, "label_text", None) for item in panel.items]
    assert "First" not in labels
