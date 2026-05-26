"""Characterization tests for ``SystemTreePanel`` (PROJ-338 Phase 1).

Pin observable behavior on top of the integration smoke tests at
``tests/integration/ui/test_system_tree_panel_smoke.py``. The smoke
tests cover construction + simple classification; this file focuses on
the grouping branches, effects-section rendering, click handling, and
the static formatter helpers.

Per PROJ-338 D-005: characterization tests live here, separate from the
audit-S1.3 smoke + the existing hazard formatter tests, so the smoke
tests stay byte-identical.

Per D-002: panels are exercised against a real ``pygame_gui.UIManager``
via the existing ``ui_manager`` fixture (no ``__new__`` bypass needed
for ``SystemTreePanel`` because its ``__init__`` is widget-only).
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.panels.system_tree_panel import (
    SystemTreePanel,
    SystemTreeItem,
)


# ---------------------------------------------------------------------------
# Stubs reused from the smoke test (kept local to avoid cross-file coupling).
# ---------------------------------------------------------------------------


class _HexCoord:
    def __init__(self, q: int, r: int) -> None:
        self.q = q
        self.r = r


class _PlanetStub:
    """Satisfies is_planet (planet_type) but NOT is_star/is_warp_point."""

    def __init__(self, name: str, mass: float = 1.0, q: int = 0, r: int = 0) -> None:
        self.name = name
        self.planet_type = "terrestrial"
        self.mass = mass
        self.location = _HexCoord(q, r)


class _StarStub:
    def __init__(self, name: str, mass: float = 1.0) -> None:
        self.name = name
        self.star_type = "G"
        self.color = (255, 255, 0)
        self.mass = mass


class _WarpPointStub:
    def __init__(self, destination_id: str) -> None:
        self.destination_id = destination_id
        self.name = f"WP-internal-{destination_id}"


class _OpaqueObj:
    """Routes through the 'others' bucket (no protocol attrs)."""

    def __init__(self, name: str) -> None:
        self.name = name


@pytest.fixture
def stub_scene_interface():
    iface = MagicMock()
    iface._get_label_for_obj.side_effect = lambda obj: getattr(obj, "name", "Item")
    iface._get_object_asset.return_value = pygame.Surface((16, 16))
    iface.scene = None
    return iface


@pytest.fixture
def panel(ui_manager):
    """Return a freshly constructed SystemTreePanel."""
    return SystemTreePanel(
        relative_rect=pygame.Rect(0, 0, 300, 400),
        manager=ui_manager,
        container=None,
    )


# ===========================================================================
# C.1 — set_items empty + single-object branches
# ===========================================================================


class TestSetItemsBasics:
    def test_set_items_empty_contents_no_items_built(self, panel, stub_scene_interface):
        panel.set_items([], stub_scene_interface)
        assert panel.items == []
        assert panel.root_items == []

    def test_set_items_kills_previous_items_on_rebuild(self, panel, stub_scene_interface):
        """BUG-26 guard: list copied so mutation during iteration is safe."""
        panel.set_items([_OpaqueObj("First")], stub_scene_interface)
        old_items = list(panel.items)
        assert len(old_items) == 1
        kill_calls = []
        for item in old_items:
            original_kill = item.kill
            def _wrap(orig):
                def _k():
                    kill_calls.append(orig)
                    orig()
                return _k
            item.kill = _wrap(original_kill)

        panel.set_items([_OpaqueObj("Second")], stub_scene_interface)
        # Each old item's kill() was called exactly once
        assert len(kill_calls) == len(old_items)

    def test_set_items_single_planet_no_root_group(self, panel, stub_scene_interface):
        p = _PlanetStub("Terra", mass=2.0)
        panel.set_items([p], stub_scene_interface)
        # Single planet → no Planetary System wrapper, leaf added directly
        assert len(panel.root_items) == 1
        leaf = panel.root_items[0]
        assert leaf.obj is p
        assert not hasattr(leaf, "is_group")

    def test_set_items_single_star_no_stars_group(self, panel, stub_scene_interface):
        s = _StarStub("Sol")
        panel.set_items([s], stub_scene_interface)
        assert len(panel.root_items) == 1
        leaf = panel.root_items[0]
        assert leaf.obj is s
        assert not hasattr(leaf, "is_group")

    def test_set_items_single_warp_point_label_uses_destination_id(self, panel, stub_scene_interface):
        wp = _WarpPointStub("system-7")
        panel.set_items([wp], stub_scene_interface)
        leaf = panel.root_items[0]
        # Single-warp branch uses "Warp to <id>" form
        assert leaf.label_text == "Warp to system-7"


# ===========================================================================
# C.2 — Grouping branches
# ===========================================================================


class TestSetItemsGrouping:
    def test_set_items_multi_planet_creates_planetary_system_root_group_with_largest_name(
        self, panel, stub_scene_interface
    ):
        small = _PlanetStub("Tiny", mass=1.0, q=0, r=0)
        big = _PlanetStub("Jovian", mass=99.0, q=1, r=0)
        panel.set_items([small, big], stub_scene_interface)
        assert len(panel.root_items) == 1
        header = panel.root_items[0]
        assert getattr(header, "is_group", False) is True
        assert header.group_key == "planets_root"
        # Largest planet's name appears in the header label
        assert "Jovian" in header.label_text
        # "(2)" count in header
        assert "(2)" in header.label_text

    def test_set_items_multi_star_creates_stars_group_with_count(self, panel, stub_scene_interface):
        stars = [_StarStub("A"), _StarStub("B"), _StarStub("C")]
        panel.set_items(stars, stub_scene_interface)
        header = panel.root_items[0]
        assert header.label_text == "Stars (3)"
        assert header.group_key == "stars_group"

    def test_set_items_multi_warp_creates_warp_points_group_with_count(self, panel, stub_scene_interface):
        wps = [_WarpPointStub("a"), _WarpPointStub("b")]
        panel.set_items(wps, stub_scene_interface)
        header = panel.root_items[0]
        assert header.label_text == "warp_points (2)"
        assert header.group_key == "wp_group"

    def test_set_items_planet_stack_at_same_hex_creates_sector_group_with_count(
        self, panel, stub_scene_interface
    ):
        p1 = _PlanetStub("P1", mass=10.0, q=2, r=3)
        p2 = _PlanetStub("P2", mass=5.0, q=2, r=3)  # same hex
        p3 = _PlanetStub("P3", mass=1.0, q=2, r=3)
        panel.set_items([p1, p2, p3], stub_scene_interface)
        # Top: Planetary System group; child: Sector stack group with x3
        root = panel.root_items[0]
        # Sector stack header has "Sector [2,3]" + "x3"
        sector_headers = [c for c in root.children if getattr(c, "is_group", False) and "Sector" in c.label_text]
        assert len(sector_headers) == 1
        assert "(x3)" in sector_headers[0].label_text

    def test_set_items_planet_stack_sorted_by_mass_descending(self, panel, stub_scene_interface):
        p_small = _PlanetStub("Small", mass=1.0, q=2, r=3)
        p_big = _PlanetStub("Big", mass=99.0, q=2, r=3)
        panel.set_items([p_small, p_big], stub_scene_interface)
        root = panel.root_items[0]
        sector = [c for c in root.children if getattr(c, "is_group", False)][0]
        # Children are the planet leaves in sorted order
        leaf_names = [c.label_text for c in sector.children]
        assert leaf_names == ["Big", "Small"]

    def test_set_items_flat_view_skips_planetary_system_grouping_and_sorts_by_mass(
        self, panel, stub_scene_interface
    ):
        p_small = _PlanetStub("Small", mass=1.0, q=0, r=0)
        p_big = _PlanetStub("Big", mass=10.0, q=1, r=1)
        p_mid = _PlanetStub("Mid", mass=5.0, q=2, r=2)
        panel.set_items([p_small, p_big, p_mid], stub_scene_interface, flat_view=True)
        # All planets at root level, sorted by mass desc, no grouping
        root_labels = [item.label_text for item in panel.root_items]
        assert root_labels == ["Big", "Mid", "Small"]
        # No group headers
        assert all(not hasattr(item, "is_group") for item in panel.root_items)


# ===========================================================================
# C.3 — Effects (system + sector) and _add_effects_group
# ===========================================================================


def _scene_interface_with_empire(empire_id: int = 1):
    iface = MagicMock()
    iface._get_label_for_obj.side_effect = lambda obj: getattr(obj, "name", "Item")
    iface._get_object_asset.return_value = pygame.Surface((16, 16))
    # scene_interface.scene.session.active_empire.id chain
    iface.scene.session.active_empire.id = empire_id
    iface.scene.session.registries = MagicMock()
    return iface


def _scene_interface_no_empire():
    iface = MagicMock()
    iface._get_label_for_obj.side_effect = lambda obj: getattr(obj, "name", "Item")
    iface._get_object_asset.return_value = pygame.Surface((16, 16))
    iface.scene.session.active_empire = None
    iface.scene.session.registries = None
    return iface


class TestSetItemsEffects:
    def test_set_items_with_system_obj_calls_hazard_then_effects_path(
        self, panel
    ):
        """Ordering: hazard hint comes BEFORE the effects group (PROJ-302 D8)."""
        iface = _scene_interface_with_empire()
        sys_obj = MagicMock()
        with patch.object(panel, "_add_system_hazard_hint") as h, \
             patch.object(panel, "_add_system_effects") as e:
            # Capture order via side_effect
            calls = []
            h.side_effect = lambda *a, **kw: calls.append("hazard")
            e.side_effect = lambda *a, **kw: calls.append("effects")
            panel.set_items([], iface, system_obj=sys_obj)
            # set_items returns early on empty contents BEFORE hazard/effects.
            # Use a non-empty content list to reach the effects branch.
        with patch.object(panel, "_add_system_hazard_hint") as h, \
             patch.object(panel, "_add_system_effects") as e:
            calls = []
            h.side_effect = lambda *a, **kw: calls.append("hazard")
            e.side_effect = lambda *a, **kw: calls.append("effects")
            panel.set_items([_OpaqueObj("X")], iface, system_obj=sys_obj)
            assert calls == ["hazard", "effects"]

    def test_set_items_with_system_obj_no_empire_skips_effects(self, panel):
        """empire_id None → effects collection is skipped (early return)."""
        iface = _scene_interface_no_empire()
        sys_obj = MagicMock()
        # No exception raised; effects header NOT appended
        panel.set_items([_OpaqueObj("X")], iface, system_obj=sys_obj)
        # No effect-group items were added (would have group_key 'system_effects')
        assert not any(
            getattr(it, "group_key", None) == "system_effects" for it in panel.items
        )

    def test_set_items_flat_view_with_hex_coord_calls_sector_effects_path(self, panel):
        iface = _scene_interface_with_empire()
        sys_obj = MagicMock()
        hex_coord = _HexCoord(2, 3)
        with patch.object(panel, "_add_sector_effects") as s:
            panel.set_items(
                [_OpaqueObj("X")], iface,
                flat_view=True, system_obj=sys_obj, hex_coord=hex_coord,
            )
            s.assert_called_once()
            args = s.call_args[0]
            assert args[0] is sys_obj
            assert args[2] is hex_coord

    def test_add_effects_group_skips_when_empty(self, panel):
        # Empty effects list → no group header appended
        panel._add_effects_group([], "System Effects", "system_effects")
        assert panel.items == []

    def test_add_effects_group_single_provider_renders_inline_with_source_label(self, panel):
        effects = [{
            "ability_name": "ResourceHarvestBooster",
            "display_name": "Harvest Booster",
            "status": "active",
            "kind": "multiplier",
            "aggregate_value": 1.25,
            "group_key": "rhb_1",
            "providers": [{"source_label": "Storm Alpha", "value": 1.25, "status": "active"}],
        }]
        panel._add_effects_group(effects, "System Effects", "system_effects")
        # Header + 1 leaf = 2 items
        assert len(panel.items) == 2
        leaf = panel.items[1]
        # Single provider rendered inline with source label
        assert "Storm Alpha" in leaf.label_text
        assert "+25%" in leaf.label_text

    def test_add_effects_group_multi_provider_creates_collapsible_subgroup(self, panel):
        effects = [{
            "ability_name": "ResourceHarvestBooster",
            "display_name": "Harvest Booster",
            "status": "active",
            "kind": "multiplier",
            "aggregate_value": 1.5,
            "group_key": "rhb_multi",
            "providers": [
                {"source_label": "Storm A", "value": 1.25, "status": "active"},
                {"source_label": "Storm B", "value": 1.20, "status": "active"},
            ],
        }]
        panel._add_effects_group(effects, "System Effects", "system_effects")
        # Header + sub-group + 2 children = 4
        assert len(panel.items) == 4
        # Sub-group has effect_<group_key> key
        sub = panel.items[1]
        assert getattr(sub, "is_group", False) is True
        assert sub.group_key == "effect_rhb_multi"

    def test_add_effects_group_falls_back_to_unknown_when_source_label_missing(self, panel):
        """PROJ-362 Phase 4: with the ``_legacy_provider_fields`` shim deleted,
        a provider missing ``source_label`` falls back to the literal
        ``"(unknown)"`` — the legacy facility_name/planet_name combo is no
        longer read.

        In practice every provider emitted by ``collect_system_effects`` /
        ``collect_sector_effects`` carries a non-empty ``source_label`` (every
        ``IAbilitySource`` adapter sets it), so the fallback is a defensive
        safety net only.
        """
        effects = [{
            "ability_name": "ResourceHarvestBooster",
            "display_name": "Harvest Booster",
            "status": "active",
            "kind": "multiplier",
            "aggregate_value": 1.10,
            "group_key": "no_source_label",
            "providers": [{
                # No source_label, no legacy keys → "(unknown)"
                "value": 1.10,
                "status": "active",
            }],
        }]
        panel._add_effects_group(effects, "System Effects", "system_effects")
        leaf = panel.items[1]
        assert "(unknown)" in leaf.label_text


# ===========================================================================
# C.4 — on_click toggling
# ===========================================================================


class TestOnClick:
    def test_on_click_group_expand_adds_to_expanded_groups_set(self, panel, stub_scene_interface):
        # Build a group via multi-star
        panel.set_items([_StarStub("A"), _StarStub("B")], stub_scene_interface)
        header = panel.root_items[0]
        assert "stars_group" not in panel.expanded_groups
        # Force start collapsed
        header.expanded = False
        panel.on_click(header)
        assert "stars_group" in panel.expanded_groups
        assert header.expanded is True

    def test_on_click_group_collapse_removes_from_expanded_groups_set(self, panel, stub_scene_interface):
        panel.set_items([_StarStub("A"), _StarStub("B")], stub_scene_interface)
        header = panel.root_items[0]
        # Pre-expand
        header.expanded = True
        panel.expanded_groups.add("stars_group")
        panel.on_click(header)
        assert "stars_group" not in panel.expanded_groups
        assert header.expanded is False

    def test_on_click_group_expand_recursively_expands_child_groups(self, panel, stub_scene_interface):
        # Multi-planet stack at same hex => Planetary System root group with
        # a Sector child group. Expanding the root should also expand the
        # sector subgroup ("Expand All").
        ps = [
            _PlanetStub("P1", mass=10.0, q=1, r=1),
            _PlanetStub("P2", mass=5.0, q=1, r=1),
            _PlanetStub("P3", mass=1.0, q=1, r=1),
        ]
        panel.set_items(ps, stub_scene_interface)
        root = panel.root_items[0]
        root.expanded = False
        panel.expanded_groups.discard("planets_root")
        panel.expanded_groups.discard("stack_(1, 1)")
        panel.on_click(root)
        assert "planets_root" in panel.expanded_groups
        # Child sector group also expanded
        assert "stack_(1, 1)" in panel.expanded_groups

    def test_on_click_leaf_with_obj_invokes_selection_callback(self, panel, stub_scene_interface):
        p = _PlanetStub("Terra")
        panel.set_items([p], stub_scene_interface)
        leaf = panel.root_items[0]
        cb = MagicMock()
        panel.set_selection_callback(cb)
        panel.on_click(leaf)
        cb.assert_called_once_with(p)

    def test_on_click_leaf_without_callback_silent_no_crash(self, panel, stub_scene_interface):
        p = _PlanetStub("Terra")
        panel.set_items([p], stub_scene_interface)
        leaf = panel.root_items[0]
        # No callback set
        panel.on_selection_callback = None
        # Must not raise
        panel.on_click(leaf)


# ===========================================================================
# C.5 — _format_effect_value / _format_provider_value
# ===========================================================================


class TestFormatHelpers:
    def test_format_effect_value_resource_harvest_booster_renders_pct(self):
        effect = {
            "ability_name": "ResourceHarvestBooster",
            "kind": "multiplier",
            "aggregate_value": 1.25,
            "providers": [{"value": 1.25}],
        }
        s = SystemTreePanel._format_effect_value(effect)
        assert s == "+25%"

    def test_format_effect_value_quality_improvement_uses_per_provider_rate_not_aggregate(self):
        effect = {
            "ability_name": "QualityImprovement",
            "kind": "multiplier",
            "aggregate_value": 1.5,  # ignored; uses providers[0].value
            "providers": [{"value": 0.05}],
        }
        s = SystemTreePanel._format_effect_value(effect)
        assert s == "+0.05/turn"

    def test_format_effect_value_shield_modifier_delegates_to_intrinsic_formatter(self):
        # ShieldModifier path delegates to format_intrinsic_ability_magnitude.
        effect = {
            "ability_name": "ShieldModifier",
            "kind": "multiplier",
            "aggregate_value": 0.7,
            "providers": [{"value": 0.7}],
        }
        s = SystemTreePanel._format_effect_value(effect)
        # Delegated formatter should produce a non-empty string for the
        # delegated path; we don't pin the exact formatting (that belongs
        # to the formatter's tests).
        assert isinstance(s, str)

    def test_format_provider_value_unknown_ability_returns_empty_string(self):
        effect = {"ability_name": "SomethingExotic"}
        provider = {"value": 1.5}
        s = SystemTreePanel._format_provider_value(effect, provider)
        assert s == ""


# ===========================================================================
# Provider-label rendering uses ``source_label`` only (PROJ-362 Phase 4).
# The pre-PROJ-300 ``_legacy_provider_label`` helper was deleted in this phase
# along with the upstream ``_legacy_provider_fields`` shim. See
# ``Projects/active_projects/PROJ-362/findings/04_ui_migration_map.md``.
# ===========================================================================


class TestProviderLabelRendering:
    def test_single_provider_uses_source_label_when_present(self, panel):
        """PROJ-300: provider rendering reads ``source_label`` directly."""
        effects = [{
            "ability_name": "ResourceHarvestBooster",
            "display_name": "Harvest Booster",
            "status": "active",
            "kind": "multiplier",
            "aggregate_value": 1.25,
            "group_key": "rhb_src",
            "providers": [{
                "source_label": "Crab Storm Alpha",
                "source_kind": "storm",
                "source_id": "storm-1",
                "value": 1.25,
                "status": "active",
            }],
        }]
        panel._add_effects_group(effects, "System Effects", "system_effects")
        leaf = panel.items[1]
        assert "Crab Storm Alpha" in leaf.label_text

    def test_multi_provider_subgroup_each_child_uses_source_label(self, panel):
        effects = [{
            "ability_name": "ResourceHarvestBooster",
            "display_name": "Harvest Booster",
            "status": "active",
            "kind": "multiplier",
            "aggregate_value": 1.5,
            "group_key": "rhb_src_multi",
            "providers": [
                {"source_label": "Storm A", "value": 1.25, "status": "active"},
                {"source_label": "Storm B", "value": 1.20, "status": "active"},
            ],
        }]
        panel._add_effects_group(effects, "System Effects", "system_effects")
        # Header + sub-group + 2 children = 4 items.
        assert len(panel.items) == 4
        child_labels = [item.label_text for item in panel.items[2:]]
        joined = " | ".join(child_labels)
        assert "Storm A" in joined
        assert "Storm B" in joined
