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


# ---------------------------------------------------------------------------
# Classification-path stubs.
#
# is_planet/is_star/is_warp_point in game.core.protocols.strategy_entities
# are duck-typed via ``_has_attrs(obj, ...)``. We use plain classes (not
# MagicMock) so attribute presence is explicit and we don't accidentally
# satisfy the wrong protocol via auto-spec.
#
# Required attributes (from production code paths in system_tree_panel.py):
#   - is_planet: ``planet_type``; planet rendering uses ``name``, ``mass``,
#     ``location.q``, ``location.r``
#   - is_star: ``star_type``, ``color``, ``mass``; rendering uses ``name``
#   - is_warp_point: ``destination_id``; rendering uses ``destination_id``
# ---------------------------------------------------------------------------


class _HexCoord:
    def __init__(self, q: int, r: int) -> None:
        self.q = q
        self.r = r


class _PlanetStub:
    """Satisfies is_planet (has planet_type) but NOT is_star/is_warp_point."""

    def __init__(self, name: str, mass: float = 1.0, q: int = 0, r: int = 0) -> None:
        self.name = name
        self.planet_type = "terrestrial"
        self.mass = mass
        self.location = _HexCoord(q, r)


class _StarStub:
    """Satisfies is_star (star_type, color, mass) but NOT is_planet/is_warp_point."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.star_type = "G"
        self.color = (255, 255, 0)
        self.mass = 1.0


class _WarpPointStub:
    """Satisfies is_warp_point (destination_id) but NOT is_planet/is_star."""

    def __init__(self, destination_id: str) -> None:
        self.destination_id = destination_id
        # name kept distinct from destination_id so we can confirm the panel
        # uses the warp-specific label format rather than the generic one.
        self.name = f"WP-internal-{destination_id}"


def test_set_items_classifies_planet_correctly(ui_manager, stub_scene_interface):
    """A single planet lands as a root-level leaf (no Planetary System wrapper)
    using its name as the label — confirms the planet branch at line 422-424."""
    panel = SystemTreePanel(
        relative_rect=pygame.Rect(0, 0, 300, 400),
        manager=ui_manager,
        container=None,
    )
    planet = _PlanetStub("Terra Prime", mass=5.0, q=2, r=3)

    panel.set_items([planet], stub_scene_interface)

    # Single planet, non-flat view, no other content => no "Planetary System"
    # group header (production code: `if len(planets) > 1` gate at line 404).
    # Exactly one root item, exactly one item total, and it points at the planet.
    assert len(panel.root_items) == 1
    assert len(panel.items) == 1
    leaf = panel.root_items[0]
    assert leaf.obj is planet
    assert leaf.label_text == "Terra Prime"
    # Planet-grouping path uses indent=0 for a single planet (line 384).
    assert leaf.indent == 0
    # Not flagged as a group header.
    assert not hasattr(leaf, "is_group")


def test_set_items_classifies_star_correctly(ui_manager, stub_scene_interface):
    """Stars route through the star branch.

    Exercises both star sub-paths (production: line 236-275):
      - single star => flat root leaf labelled by ``star.name``
      - multiple stars => "Stars (N)" group header + indented children
    """
    panel = SystemTreePanel(
        relative_rect=pygame.Rect(0, 0, 300, 400),
        manager=ui_manager,
        container=None,
    )

    # --- Single-star sub-path: no "Stars (N)" group, one flat root leaf. ---
    sol = _StarStub("Sol")
    panel.set_items([sol], stub_scene_interface)

    assert len(panel.root_items) == 1
    assert len(panel.items) == 1
    leaf = panel.root_items[0]
    assert leaf.obj is sol
    assert leaf.label_text == "Sol"
    assert not hasattr(leaf, "is_group")

    # --- Multi-star sub-path: group header with indented children. ---
    stars = [_StarStub("Alpha Centauri A"), _StarStub("Alpha Centauri B")]
    panel.set_items(stars, stub_scene_interface)

    # One group header at root + 2 star children => 3 items total, 1 root.
    assert len(panel.root_items) == 1
    assert len(panel.items) == 3
    header = panel.root_items[0]
    assert getattr(header, "is_group", False) is True
    assert header.group_key == "stars_group"
    assert header.label_text == "Stars (2)"
    # Header has no underlying obj (it's a synthetic grouping row).
    assert header.obj is None
    # Children carry the actual star objects, indented one level.
    child_objs = [c.obj for c in header.children]
    assert child_objs == stars
    assert all(c.indent == 1 for c in header.children)


def test_set_items_classifies_warp_point_correctly(ui_manager, stub_scene_interface):
    """A single warp point lands as a root-level leaf labelled
    ``Warp to <destination_id>`` (production: line 305-315)."""
    panel = SystemTreePanel(
        relative_rect=pygame.Rect(0, 0, 300, 400),
        manager=ui_manager,
        container=None,
    )
    wp = _WarpPointStub("system-42")

    panel.set_items([wp], stub_scene_interface)

    assert len(panel.root_items) == 1
    assert len(panel.items) == 1
    leaf = panel.root_items[0]
    assert leaf.obj is wp
    # Single-warp-point branch uses the "Warp to <id>" label, not the
    # group "To <id>" form (production: line 307 vs 295).
    assert leaf.label_text == "Warp to system-42"
    assert not hasattr(leaf, "is_group")
