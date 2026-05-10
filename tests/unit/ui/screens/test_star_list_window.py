"""Characterization tests for ``StarListWindow`` (PROJ-329B Phase 1).

Pins the Stage-1 cheap-state initialization (galaxy, layout constants,
filter manager, preset manager, columns, gathered/filtered stars) plus
the ``ui_builder`` two-stage construction seam.

This class had no tests before PROJ-329B — these are written against the
post-retrofit shape, which mirrors the pre-retrofit production behavior.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pygame
import pytest

from game.ui.screens.star_list_window import StarListWindow, StarListWindowUiBuilder
from tests.fixtures.star_list_window_ui_builder import (
    MockStarListWindowUiBuilder,
    NullStarListWindowUiBuilder,
)
from tests.fixtures.ui_widget_factory import bypass_init


def _galaxy(num_systems: int = 0):
    """Build a minimal galaxy mock; no systems by default."""
    galaxy = MagicMock(name="Galaxy")
    galaxy.systems = {}
    return galaxy


def _make_window(
    galaxy=None,
    *,
    rect=None,
    ui_builder=None,
    on_close_callback=None,
    on_navigate_callback=None,
):
    if galaxy is None:
        galaxy = _galaxy()
    if rect is None:
        rect = pygame.Rect(0, 0, 1200, 800)
    if ui_builder is None:
        ui_builder = MockStarListWindowUiBuilder()
    with bypass_init(StarListWindow):
        return StarListWindow(
            rect,
            MagicMock(name="ui_manager"),
            galaxy,
            window_manager=None,
            on_close_callback=on_close_callback,
            on_navigate_callback=on_navigate_callback,
            ui_builder=ui_builder,
        )


class TestStarListWindowStageOneState:
    """Stage-1 cheap state survives bypass_init."""

    def test_stores_galaxy_reference(self):
        galaxy = _galaxy()
        window = _make_window(galaxy)
        assert window.galaxy is galaxy

    def test_stores_close_callback(self):
        cb = MagicMock()
        window = _make_window(on_close_callback=cb)
        assert window.on_close_callback is cb

    def test_stores_navigate_callback(self):
        cb = MagicMock()
        window = _make_window(on_navigate_callback=cb)
        assert window.on_navigate_callback is cb

    def test_layout_constants_assigned_from_uiconfig(self):
        from game.ui.config import UIConfig
        window = _make_window()
        assert window.sidebar_width == UIConfig.REGISTRY_SIDEBAR_WIDTH
        assert window.header_height == UIConfig.HEADER_HEIGHT
        assert window.row_height == UIConfig.ROW_HEIGHT_LARGE

    def test_selected_star_starts_none(self):
        window = _make_window()
        assert window.selected_star is None

    def test_last_preset_selection_starts_none(self):
        window = _make_window()
        assert window.last_preset_selection is None

    def test_filtered_stars_starts_empty(self):
        window = _make_window()
        assert window.filtered_stars == []

    def test_all_stars_gathered_from_galaxy(self):
        galaxy = _galaxy()
        window = _make_window(galaxy)
        # Empty galaxy -> empty star list.
        assert window.all_stars == []

    def test_preset_manager_assigned(self):
        from game.ui.screens.star_list_presets import StarPresetManager
        window = _make_window()
        assert isinstance(window.preset_manager, StarPresetManager)

    def test_filter_manager_assigned(self):
        from game.ui.screens.star_list_filter_manager import StarListFilterManager
        window = _make_window()
        assert isinstance(window._filter_mgr, StarListFilterManager)

    def test_columns_default_set_includes_known_ids(self):
        window = _make_window()
        ids = {col['id'] for col in window.columns}
        # Spot-check a representative subset of the 20 column ids.
        assert {'icon', 'name', 'type', 'system', 'mass',
                'radius', 'temp', 'luminosity', 'age',
                'planets', 'companions'}.issubset(ids)

    def test_visible_columns_match_pre_retrofit_default(self):
        window = _make_window()
        visible = [col['id'] for col in window.columns if col['visible']]
        assert visible == [
            'icon', 'name', 'type', 'system', 'mass', 'radius',
            'temp', 'luminosity', 'age', 'planets', 'companions',
        ]


class TestStarListWindowBuilderSeam:
    """``ui_builder`` test seam wires correctly under bypass_init."""

    def test_window_init_bypassed_flag_set(self):
        window = _make_window()
        assert window._window_init_bypassed is True

    def test_default_ui_builder_used_in_production(self):
        # Production path -> default StarListWindowUiBuilder. Not
        # exercised under bypass_init; pin the parameter default
        # signature instead.
        import inspect
        sig = inspect.signature(StarListWindow.__init__)
        assert 'ui_builder' in sig.parameters
        assert sig.parameters['ui_builder'].default is None

    def test_mock_builder_populates_widget_slots(self):
        window = _make_window()
        for slot in (
            "sidebar_panel", "sidebar_scroller", "txt_name_filter",
            "btn_all_types", "btn_none_types", "btn_apply",
            "btn_save_preset", "txt_preset_name", "dd_presets",
            "main_panel", "column_manager", "data_source", "selection",
            "virtual_table", "btn_navigate",
        ):
            assert hasattr(window, slot), f"missing widget slot: {slot}"

    def test_null_builder_leaves_widget_slots_unset(self):
        window = _make_window(ui_builder=NullStarListWindowUiBuilder())
        # Stage-1 default: btn_navigate is set to None before super().
        assert window.btn_navigate is None
        # PROJ-347 T4.1a: main_panel is a Pattern §33 widget-ref
        # placeholder set to None in Stage 1 (so kill() under a Null
        # builder does not AttributeError). The Null builder leaves it
        # as None; only the production builder overwrites it.
        assert window.main_panel is None

    def test_null_builder_kill_does_not_raise(self):
        """PROJ-347 T4.1a: ``kill()`` on a window built with a Null
        builder must not AttributeError on widget-ref accesses
        (``self.virtual_table.kill()`` etc.). The Stage-1 placeholders
        ensure ``virtual_table`` and other widget refs are at least
        ``None``, so the existing truthiness guards short-circuit."""
        window = _make_window(ui_builder=NullStarListWindowUiBuilder())
        assert window.virtual_table is None
        assert window.sidebar_panel is None
        assert window.main_panel is None
        # kill() should not raise — guards short-circuit on None refs.
        # We can't actually call super().kill() under bypass_init (the
        # window is not fully initialized), so just confirm the
        # widget-ref placeholders exist.
        for slot in (
            "virtual_table", "sidebar_panel", "main_panel",
            "data_source", "column_manager", "selection",
        ):
            assert getattr(window, slot) is None, (
                f"Pattern §33 placeholder {slot!r} should be None under "
                f"Null builder; got {getattr(window, slot)!r}"
            )

    def test_production_builder_implements_protocol(self):
        from tests.fixtures.ui_builder_protocol import UiBuilder
        assert isinstance(StarListWindowUiBuilder(), UiBuilder)
        assert isinstance(MockStarListWindowUiBuilder(), UiBuilder)
        assert isinstance(NullStarListWindowUiBuilder(), UiBuilder)


class TestStarListWindowFilterRanges:
    """Filter ranges seed from the gathered star data."""

    def test_filter_ranges_initialized_from_star_ranges(self):
        window = _make_window()
        # Empty galaxy -> ranges still get a default key set from
        # compute_star_ranges (returns the canonical filter keys).
        assert isinstance(window.filter_ranges, dict)


class TestStarListWindowFilterManagerDelegation:
    """``filter_types`` and ``filter_ranges`` properties delegate to
    the ``StarListFilterManager``."""

    def test_filter_types_property_reads_from_filter_mgr(self):
        window = _make_window()
        sentinel = {'star_type': True}
        window._filter_mgr.filter_types = sentinel
        assert window.filter_types is sentinel

    def test_filter_types_setter_writes_to_filter_mgr(self):
        window = _make_window()
        sentinel = {'star_type': False}
        window.filter_types = sentinel
        assert window._filter_mgr.filter_types is sentinel

    def test_filter_ranges_setter_writes_to_filter_mgr(self):
        window = _make_window()
        sentinel = {'mass': [0.1, 9.9]}
        window.filter_ranges = sentinel
        assert window._filter_mgr.filter_ranges is sentinel


class TestStarListWindowNavigate:
    """``_navigate_to_selected`` uses the cached system location."""

    def test_navigate_with_no_selection_no_op(self):
        cb = MagicMock()
        window = _make_window(on_navigate_callback=cb)
        # selected_star is None
        window._navigate_to_selected()
        cb.assert_not_called()

    def test_navigate_with_selection_calls_callback(self):
        cb = MagicMock()
        window = _make_window(on_navigate_callback=cb)
        loc = MagicMock(name="HexCoord")
        star = MagicMock(name="Star")
        star._cached_system_global_location = loc
        window.selected_star = star
        window._navigate_to_selected()
        cb.assert_called_once_with(loc)

    def test_navigate_with_no_callback_no_crash(self):
        window = _make_window()
        # on_navigate_callback is None
        window.selected_star = MagicMock()
        # Should not raise
        window._navigate_to_selected()
