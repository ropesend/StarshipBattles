"""Tests for DesignStatsPanel (PROJ-111 Phase 6 Task 6.8).

Tests the shared design stats panel widget for displaying ship statistics.
"""

import contextlib as contextlib_module

import pytest
from unittest.mock import MagicMock, patch

import pygame

from tests.fixtures.ui_widget_factory import make_ui_widget


# --- Helpers ---

def _make_stat_row():
    """Create a mock StatRow."""
    from game.ui.panels.design_stats_panel import StatRow

    with patch.object(StatRow, '__init__', lambda self, *a, **kw: None):
        row = StatRow.__new__(StatRow)

    row.key = "test_key"
    row.label = MagicMock()
    row.value = MagicMock()
    row.unit = MagicMock()
    row._last_val = None
    row._last_unit = None
    row._visible = True

    return row


# --- StatRow Tests ---

class TestStatRow:
    """Tests for StatRow helper class."""

    def test_stat_row_update_changes_value(self):
        """StatRow.update changes value text."""
        row = _make_stat_row()

        row.update("100", "tons")

        row.value.set_text.assert_called_with("100")
        row.unit.set_text.assert_called_with("tons")

    def test_stat_row_update_caches_value(self):
        """StatRow.update caches value to avoid redundant updates."""
        row = _make_stat_row()

        # First update
        row.update("100", "tons")
        row._last_val = "100"
        row._last_unit = "tons"

        # Reset mocks
        row.value.set_text.reset_mock()
        row.unit.set_text.reset_mock()

        # Same value - should not call set_text
        row.update("100", "tons")

        row.value.set_text.assert_not_called()
        row.unit.set_text.assert_not_called()

    def test_stat_row_update_detects_change(self):
        """StatRow.update detects value change after caching."""
        row = _make_stat_row()

        # First update
        row.update("100", "tons")
        row._last_val = "100"
        row._last_unit = "tons"

        # Reset mocks
        row.value.set_text.reset_mock()
        row.unit.set_text.reset_mock()

        # Different value - should call set_text
        row.update("200", "tons")

        row.value.set_text.assert_called_with("200")

    def test_stat_row_set_visible_shows_elements(self):
        """StatRow.set_visible(True) shows all elements."""
        row = _make_stat_row()
        row._visible = False

        row.set_visible(True)

        row.label.show.assert_called()
        row.value.show.assert_called()
        row.unit.show.assert_called()

    def test_stat_row_set_visible_hides_elements(self):
        """StatRow.set_visible(False) hides all elements."""
        row = _make_stat_row()
        row._visible = True

        row.set_visible(False)

        row.label.hide.assert_called()
        row.value.hide.assert_called()
        row.unit.hide.assert_called()

    def test_stat_row_set_visible_caches_state(self):
        """StatRow.set_visible caches visibility state."""
        row = _make_stat_row()
        row._visible = True

        # Already visible - should not call show
        row.set_visible(True)

        row.label.show.assert_not_called()


# =============================================================================
# PROJ-339: DesignStatsPanel-level characterization
#
# D-009 fixture-discovery resolution: `make_ui_widget` from the shared
# factory CAN construct a `DesignStatsPanel` with `ship=None` directly
# (no fixture-discovery cost), and CAN drive `_build_layout` when given
# a tiny stub ship that exposes the attributes the dynamic-section
# generators read (`pod_storage_mass`, `cargo_storage`,
# `construction_cost`, `get_resource_stat`, `resources` w/ a noop
# `get_resource_names`). The fixture below pins that minimum surface.
# =============================================================================


class _StubShip:
    """Minimum-surface ship for DesignStatsPanel construction.

    Exposes every attribute / method the production code reads during
    `_build_layout` + `_build_sections` + `update_stats` for a vehicle
    with no abilities / no layers / no resources. Tests that need extra
    behavior subclass and override.
    """

    vehicle_type = 'Ship'
    layers = {}  # mapping LayerType -> Layer
    layer_status = {}
    mass = 0.0
    mass_limits_ok = True
    max_mass_budget = 1000.0
    pod_storage_mass = 0
    cargo_storage = {}
    construction_cost = {}

    def __init__(self) -> None:
        self._resources = MagicMock()
        self._resources.get_resource_names = MagicMock(return_value=[])

    @property
    def resources(self):
        return self._resources

    def get_all_components(self):
        return []

    def get_missing_requirements(self):
        return []

    def get_validation_warnings(self):
        return []

    def get_resource_stat(self, res, stat_type):
        return 0

    def get_total_resource_endurance(self, *args, **kwargs):
        return 0


_PYGAME_GUI_PATCHES = (
    'game.ui.panels.design_stats_panel.UILabel',
    'game.ui.panels.design_stats_panel.UIScrollingContainer',
    'game.ui.panels.design_stats_panel.UITextBox',
)


def _make_panel(ship=None, show_requirements=False):
    """Build a `DesignStatsPanel` via the shared make_ui_widget factory.

    Returns the constructed panel; production `__init__` ran with all
    pygame_gui.elements.UI* classes patched to MagicMock, so every
    real attribute is set but no real surfaces are allocated.
    """
    return make_ui_widget(
        DesignStatsPanel,
        ship=ship,
        show_requirements=show_requirements,
    )


@contextlib_module.contextmanager
def _patched_pygame_gui_for_rebuild():
    """Re-patch the pygame_gui.elements imports inside the panel module
    so that calls to `rebuild` / `_build_layout` performed AFTER
    construction also produce Mock widgets instead of real ones.

    `make_ui_widget` only patches for the duration of `__init__`; any
    later widget construction (e.g. `rebuild(other_ship)`) hits the
    real pygame_gui classes which then complain about Mock containers.
    This helper restores the patches for the duration of the with-block.
    """
    patches = [patch(target, MagicMock(side_effect=lambda *a, **kw: MagicMock()))
               for target in _PYGAME_GUI_PATCHES]
    started = []
    try:
        for p in patches:
            started.append(p.start())
        yield
    finally:
        for p in patches:
            p.stop()


# Late imports so the module-level lint hint doesn't trip on the
# fixture-discovery scaffolding above.
from game.ui.panels.design_stats_panel import DesignStatsPanel  # noqa: E402


class TestDesignStatsPanelConstruction:
    """PROJ-339 top-3: panel-level construction + rebuild semantics."""

    def test_construct_with_none_ship_then_rebuild_populates_rows_map(self):
        """Constructing with `ship=None` leaves `rows_map` empty;
        calling `rebuild(real_ship)` populates it."""
        panel = _make_panel(ship=None)
        assert panel.rows_map == {}
        assert panel.layer_rows == []
        assert panel.stats_scroll is None

        with _patched_pygame_gui_for_rebuild():
            panel.rebuild(_StubShip())

        assert len(panel.rows_map) > 0
        assert len(panel.layer_rows) == 4  # always 4 layer slots reserved
        assert panel.stats_scroll is not None

    def test_show_requirements_false_omits_textboxes(self):
        """`show_requirements=False` at construction → no req/recs
        textboxes are built (req_box_left/right stay None)."""
        panel = _make_panel(ship=_StubShip(), show_requirements=False)
        assert panel.req_box_left is None
        assert panel.req_box_right is None


class TestDesignStatsPanelNeedsRebuild:
    """PROJ-339 top-3 + happy-path: needs_rebuild diff semantics."""

    def test_needs_rebuild_false_when_logistics_keys_unchanged(self):
        """A ship with the same logistics + section visibility as the
        constructed-with ship → `needs_rebuild` returns False."""
        ship = _StubShip()
        panel = _make_panel(ship=ship)
        # Same ship → same logistics keys + visible sections.
        assert panel.needs_rebuild(ship) is False

    def test_needs_rebuild_true_on_visible_section_keys_change(self):
        """A ship that exposes a different ability set → different
        visible_section_keys → `needs_rebuild` returns True."""
        ship_a = _StubShip()
        panel = _make_panel(ship=ship_a)
        baseline = set(panel.visible_section_keys)

        # Build a ship that adds a Weapons section by exposing a
        # WeaponAbility-bearing component.
        class _ShipWithWeapon(_StubShip):
            def get_all_components(self):
                comp = MagicMock()
                comp.has_ability = lambda name: name == 'WeaponAbility'
                return [comp]

        ship_b = _ShipWithWeapon()
        # Sanity — at least one section should differ.
        from game.ui.screens.builder.stats_config import (
            SECTIONS_CONFIG, ALWAYS_VISIBLE, resolve_section_visibility,
        )
        new_visible = {
            k for k, sec in SECTIONS_CONFIG.items()
            if resolve_section_visibility(sec, ship_b, 'Ship', ALWAYS_VISIBLE)
        }
        assert new_visible != baseline

        assert panel.needs_rebuild(ship_b) is True


class TestDesignStatsPanelBuildLayout:
    """PROJ-339 happy-path: _build_layout vehicle-type filtering."""

    def test_build_layout_filters_sections_by_vehicle_type(self):
        """A `Drop Pod` vehicle_type only renders the always-visible
        sections for that type (just `main`), not the full Ship set."""
        class _DropPodShip(_StubShip):
            vehicle_type = 'Drop Pod'

        panel = _make_panel(ship=_DropPodShip())

        # Drop Pod's always-visible list is just ['main'].
        assert 'main' in panel.visible_section_keys
        # 'Ship'-only always-visible sections must be absent for Drop Pod
        # (e.g. crewlogistics and logistics rely on Ship's always-list).
        assert 'crewlogistics' not in panel.visible_section_keys
        assert 'logistics' not in panel.visible_section_keys


class TestDesignStatsPanelUpdateStats:
    """PROJ-339: layer-row population + requirements rendering."""

    def test_update_stats_populates_layer_rows_and_hides_unused_slots(self):
        """`update_stats` shows one layer_row per `ship.layers` entry
        and hides the remaining slots.

        Strips `rows_map` so update_stats doesn't try to call the
        configured stat-getters against the stub ship; layer_rows is
        the only thing under test here.
        """
        from game.core.constants import LayerType

        class _ShipWithLayers(_StubShip):
            layers = {
                LayerType.HULL: MagicMock(),
                LayerType.CORE: MagicMock(),
            }
            layer_status = {
                LayerType.HULL: {'ratio': 0.5, 'limit': 1.0, 'ok': True, 'mass': 100},
                LayerType.CORE: {'ratio': 0.3, 'limit': 1.0, 'ok': True, 'mass': 50},
            }

        ship = _ShipWithLayers()
        panel = _make_panel(ship=ship)
        # Drop rows_map so update_stats focuses purely on layer_rows.
        panel.rows_map = {}
        # Reset visible flags so we can observe the side effects.
        for row in panel.layer_rows:
            row.set_visible(True)

        panel.update_stats(ship)

        # First two slots visible, last two hidden.
        visible_flags = [row._visible for row in panel.layer_rows]
        assert visible_flags == [True, True, False, False]

    def test_update_stats_requirements_lists_missing_and_mass_overflow(self):
        """When `show_requirements=True`: missing reqs render in red,
        over-mass-budget appends an entry, and each over-budget layer
        appends one entry. All three classes coexist in the html.

        Drops `rows_map` and `layer_rows` so update_stats focuses on
        the requirements path.
        """
        from game.core.constants import LayerType

        class _OverbudgetShip(_StubShip):
            mass_limits_ok = False
            mass = 1500
            max_mass_budget = 1000
            layer_status = {
                LayerType.CORE: {
                    'ratio': 0.6, 'limit': 0.5, 'ok': False, 'mass': 600,
                },
            }
            layers = {LayerType.CORE: MagicMock()}

            def get_missing_requirements(self):
                return ["Need a bridge"]

            def get_validation_warnings(self):
                return []

        ship = _OverbudgetShip()
        panel = _make_panel(ship=ship, show_requirements=True)
        panel.rows_map = {}
        panel.layer_rows = []
        # Make req_box mocks observable.
        panel.req_box_left = MagicMock()
        panel.req_box_right = MagicMock()

        panel.update_stats(ship)

        html_left = panel.req_box_left.html_text
        # missing-reqs entry rendered
        assert "Need a bridge" in html_left
        # mass-overflow entry rendered
        assert "over mass" in html_left.lower()
        # per-layer overflow entry rendered
        assert "CORE over by" in html_left
        panel.req_box_left.rebuild.assert_called()

    def test_update_stats_requirements_clean_renders_all_met(self):
        """No missing reqs + within mass budget + all layers within →
        '✓ All met' renders on the left box."""
        ship = _StubShip()
        panel = _make_panel(ship=ship, show_requirements=True)
        panel.rows_map = {}
        panel.layer_rows = []
        panel.req_box_left = MagicMock()
        panel.req_box_right = MagicMock()

        panel.update_stats(ship)

        html_left = panel.req_box_left.html_text
        assert "All met" in html_left
        # Right box renders the no-recs path.
        html_right = panel.req_box_right.html_text
        assert "No recommendations" in html_right


class TestDesignStatsPanelHandleEvent:
    """PROJ-339: section-header click toggles `collapsed_sections`."""

    def test_handle_event_collapse_click_updates_collapsed_sections(self):
        """A left-click on a header label's abs_rect adds the section
        key to `collapsed_sections`; a second click removes it."""
        ship = _StubShip()
        panel = _make_panel(ship=ship)
        # Ensure there is at least one header to click.
        assert panel.section_header_buttons
        sec_key = next(iter(panel.section_header_buttons.keys()))
        header_label = panel.section_header_buttons[sec_key]
        # Stub get_abs_rect to a known point.
        click_rect = pygame.Rect(50, 50, 100, 25)
        header_label.get_abs_rect = MagicMock(return_value=click_rect)

        click_event = MagicMock(
            type=pygame.MOUSEBUTTONDOWN, button=1, pos=(60, 60),
        )

        # First click → adds to collapsed_sections
        consumed = panel.handle_event(click_event)
        assert consumed is True
        assert sec_key in panel.collapsed_sections

        # Second click → removes from collapsed_sections
        consumed = panel.handle_event(click_event)
        assert consumed is True
        assert sec_key not in panel.collapsed_sections

    def test_handle_event_outside_headers_returns_false(self):
        """A left-click whose position misses every header label returns
        False and does not mutate `collapsed_sections`."""
        ship = _StubShip()
        panel = _make_panel(ship=ship)
        # Pin every header to a click_rect far from (0, 0).
        for label in panel.section_header_buttons.values():
            label.get_abs_rect = MagicMock(
                return_value=pygame.Rect(500, 500, 50, 25),
            )
        baseline = set(panel.collapsed_sections)

        click_event = MagicMock(
            type=pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0),
        )
        assert panel.handle_event(click_event) is False
        assert set(panel.collapsed_sections) == baseline
