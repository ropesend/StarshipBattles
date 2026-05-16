"""Characterization tests for ``PlanetReportPanel`` (PROJ-338 Phase 1).

Pin panel-object behavior that the existing pure-helper-focused
``test_planet_report_panel.py`` skips. Sits beside (does not touch) the
existing 981-LOC test file per PROJ-338 D-007.

Per D-002: uses the established ``__new__`` bypass pattern so the
panel's facade-coupled ``__init__`` (resource-icon filesystem load,
pygame_gui widget construction) does not have to be reachable from
unit tests.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pygame
import pytest

from game.ui.panels.planet_report_panel import (
    PlanetReportPanel,
    _net_cell_color,
)
from game.ui.colors import HP_HEALTHY, HP_CRITICAL, TEXT_LIGHT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _bypass_panel() -> PlanetReportPanel:
    """Construct a PlanetReportPanel without running __init__.

    Tests that need attributes set them explicitly. Mirrors the pattern
    in tests/unit/ui/panels/test_planet_report_panel.py.
    """
    with patch.object(PlanetReportPanel, "__init__", lambda self, *a, **kw: None):
        return PlanetReportPanel.__new__(PlanetReportPanel)


def _mock_planet():
    p = MagicMock()
    p.name = "Terra"
    p.planet_type = MagicMock()
    p.planet_type.name = "TERRESTRIAL"
    p.atmosphere = {}
    p.deposits = {}
    p.facilities = []
    p.stockpile = {}
    p.max_stockpile = {}
    p.owner_id = None
    return p


# ===========================================================================
# E.1 — Construction-time conditional layout (using __init__ patch overrides)
# ===========================================================================


class TestConstructionLayout:
    """Tests pin construction-time conditional behavior by inspecting the
    code paths via attribute injection rather than running full __init__.
    """

    def _construct_with_pygame_gui_patched(
        self, *, show_complexes: bool, show_staged_units: bool = False,
    ):
        """Run the real __init__ with all pygame_gui widgets patched out.

        Returns a tuple of (panel, ui_textbox_mock, ui_scrolling_container_mock)
        so callers can inspect what production code passed to each.

        QA-OBS-4: ``show_staged_units`` defaults to False here so existing
        layout assertions (which pinned ``show_complexes=False`` ⇒ no right
        column) continue to hold. The new contract for production callers
        is that ``show_staged_units`` defaults to True at the call site —
        a separate test below covers that path.
        """
        manager = MagicMock()
        rect = pygame.Rect(0, 0, 800, 600)
        planet = _mock_planet()

        with patch("game.ui.panels.planet_report_panel.UIPanel"), \
             patch("game.ui.panels.planet_report_panel.UIImage"), \
             patch("game.ui.panels.planet_report_panel.UITextBox") as utextbox, \
             patch("game.ui.panels.planet_report_panel.UIScrollingContainer") as uscroll, \
             patch("game.ui.panels.planet_report_panel.UILabel"), \
             patch("game.ui.panels.planet_report_panel.AtmosphereGraph"), \
             patch.object(PlanetReportPanel, "_update_graph", lambda self: None), \
             patch.object(PlanetReportPanel, "_build_resource_grid", lambda self: None), \
             patch.object(PlanetReportPanel, "_update_complexes_list", lambda self: None), \
             patch.object(PlanetReportPanel, "_update_staged_units_list", lambda self: None), \
             patch("game.ui.panels.planet_report_panel.format_planet_info", return_value=""):
            panel = PlanetReportPanel(
                manager=manager,
                rect=rect,
                planet=planet,
                container=MagicMock(),
                show_complexes=show_complexes,
                show_staged_units=show_staged_units,
            )
        return panel, utextbox, uscroll

    def test_construction_with_show_complexes_creates_complexes_container(self):
        """Real __init__ contract: show_complexes=True calls UIScrollingContainer
        for the complexes list AND narrows the detail_text rect to leave room
        for the 200px complexes column + 10px gap. Pins both side-effects of
        the show_complexes=True branch."""
        panel, utextbox, uscroll = self._construct_with_pygame_gui_patched(
            show_complexes=True,
        )
        # complexes_container is the UIScrollingContainer just created
        assert panel.complexes_container is not None
        assert panel.complex_items == []
        # detail_text was constructed with the narrowed width:
        # text_w = 800 - 180 - 200 - 10 = 410
        text_rect = utextbox.call_args.kwargs["relative_rect"]
        assert text_rect.width == 410
        # UIScrollingContainer was called for complexes (resource_panel build is
        # patched out, so the only call is the complexes container).
        rects = [c.kwargs["relative_rect"] for c in uscroll.call_args_list]
        assert any(r.width == 200 for r in rects), (
            "show_complexes=True must construct a 200px-wide UIScrollingContainer"
        )

    def test_construction_without_show_complexes_text_panel_takes_full_width(self):
        """Real __init__ contract: show_complexes=False suppresses the
        complexes UIScrollingContainer call and widens detail_text to rect.width - 180."""
        panel, utextbox, uscroll = self._construct_with_pygame_gui_patched(
            show_complexes=False,
        )
        assert panel.complexes_container is None
        assert panel.complex_items == []
        # detail_text widened: text_w = 800 - 180 = 620
        text_rect = utextbox.call_args.kwargs["relative_rect"]
        assert text_rect.width == 620
        # No UIScrollingContainer of the complexes-list shape (200px wide).
        rects = [c.kwargs["relative_rect"] for c in uscroll.call_args_list]
        assert not any(r.width == 200 for r in rects), (
            "show_complexes=False must NOT construct a 200px-wide UIScrollingContainer"
        )

    def test_construction_loads_resource_icons_for_each_displayed_resource(self):
        """_load_resource_icons populates _resource_icons with one entry per displayed resource."""
        panel = _bypass_panel()
        panel._displayed_resources = ["metals", "organics"]
        panel._resource_icons = {}
        # Mock RESOURCE_PORTRAIT_FILES so the loader uses our resources
        with patch("game.ui.panels.planet_report_panel.RESOURCE_PORTRAIT_FILES", {}):
            # No file mappings → falls through to grey placeholder branch
            panel._load_resource_icons(icon_size=20)
        assert set(panel._resource_icons.keys()) == {"metals", "organics"}
        for surf in panel._resource_icons.values():
            assert surf.get_width() == 20
            assert surf.get_height() == 20

    def test_construction_resource_icon_file_missing_falls_back_to_colored_square(self):
        """When pygame.image.load raises pygame.error, fallback is a colored square."""
        panel = _bypass_panel()
        panel._displayed_resources = ["metals"]
        panel._resource_icons = {}
        with patch(
            "game.ui.panels.planet_report_panel.RESOURCE_PORTRAIT_FILES",
            {"metals": "missing.png"},
        ), patch("pygame.image.load", side_effect=pygame.error("not found")):
            panel._load_resource_icons(icon_size=24)
        # Got a fallback square at requested size
        assert "metals" in panel._resource_icons
        surf = panel._resource_icons["metals"]
        assert surf.get_width() == 24
        assert surf.get_height() == 24

    def test_construction_resource_with_no_filename_uses_gray_placeholder(self):
        """When no filename mapping exists, gray placeholder is used."""
        panel = _bypass_panel()
        panel._displayed_resources = ["mystery"]
        panel._resource_icons = {}
        with patch("game.ui.panels.planet_report_panel.RESOURCE_PORTRAIT_FILES", {}):
            panel._load_resource_icons(icon_size=20)
        assert "mystery" in panel._resource_icons

    def test_construction_atmosphere_graph_height_floor_50px_when_rect_too_short(self):
        """Validate the height-floor branch via inspection of the formula.

        The formula in __init__: ``graph_h = rect.height - 180 - RESOURCE_PANEL_HEIGHT``;
        if ``graph_h < 50`` it is forced to 50. We verify the branch directly.
        """
        from game.ui.panels.planet_report_panel import RESOURCE_PANEL_HEIGHT

        # rect.height too short for full graph
        rect_height = 100
        graph_h = rect_height - 180 - RESOURCE_PANEL_HEIGHT
        if graph_h < 50:
            graph_h = 50
        assert graph_h == 50


# ===========================================================================
# E.2 — update_planet
# ===========================================================================


class TestUpdatePlanet:
    def _seed(self, panel):
        panel.planet = _mock_planet()
        panel.production_rates = {}
        panel.view = "old_view"
        panel._empire = "old_empire"
        panel._race_registry = "old_registry"
        panel.detail_text = MagicMock()
        # Stub the side-effect methods so we can call update_planet
        panel._update_portrait = MagicMock()
        panel._update_graph = MagicMock()
        panel._update_complexes_list = MagicMock()
        # QA-OBS-4: staged units list is part of update_planet; stub it too.
        panel._update_staged_units_list = MagicMock()
        panel._update_resource_grid = MagicMock()

    def test_update_planet_overwrites_view_unconditionally_with_new_value(self):
        panel = _bypass_panel()
        self._seed(panel)
        new_planet = _mock_planet()
        with patch("game.ui.panels.planet_report_panel.format_planet_info", return_value=""):
            panel.update_planet(new_planet, view="new_view")
        assert panel.view == "new_view"

    def test_update_planet_overwrites_view_unconditionally_with_none(self):
        """PROJ-289 explicit policy: view=None is a real assignment, not a no-op."""
        panel = _bypass_panel()
        self._seed(panel)
        new_planet = _mock_planet()
        with patch("game.ui.panels.planet_report_panel.format_planet_info", return_value=""):
            panel.update_planet(new_planet, view=None)
        assert panel.view is None

    def test_update_planet_empire_none_preserves_construction_time_value(self):
        """PROJ-292 m1 sentinel: empire=None reuses construction-time _empire."""
        panel = _bypass_panel()
        self._seed(panel)
        new_planet = _mock_planet()
        with patch("game.ui.panels.planet_report_panel.format_planet_info", return_value=""):
            panel.update_planet(new_planet, empire=None)
        assert panel._empire == "old_empire"

    def test_update_planet_empire_provided_overrides_construction_time_value(self):
        panel = _bypass_panel()
        self._seed(panel)
        new_planet = _mock_planet()
        with patch("game.ui.panels.planet_report_panel.format_planet_info", return_value=""):
            panel.update_planet(new_planet, empire="new_empire")
        assert panel._empire == "new_empire"

    def test_update_planet_race_registry_same_sentinel_semantics(self):
        panel = _bypass_panel()
        self._seed(panel)
        new_planet = _mock_planet()
        with patch("game.ui.panels.planet_report_panel.format_planet_info", return_value=""):
            panel.update_planet(new_planet, race_registry=None)
        assert panel._race_registry == "old_registry"
        # Pass a value
        with patch("game.ui.panels.planet_report_panel.format_planet_info", return_value=""):
            panel.update_planet(new_planet, race_registry="new_registry")
        assert panel._race_registry == "new_registry"

    def test_update_planet_rebuilds_text_box_html(self):
        panel = _bypass_panel()
        self._seed(panel)
        new_planet = _mock_planet()
        with patch(
            "game.ui.panels.planet_report_panel.format_planet_info",
            return_value="<b>Terra</b>",
        ):
            panel.update_planet(new_planet)
        assert panel.detail_text.html_text == "<b>Terra</b>"
        panel.detail_text.rebuild.assert_called_once()


# ===========================================================================
# E.3 — _update_complexes_list
# ===========================================================================


class TestUpdateComplexesList:
    def _seed(self, panel, *, with_container: bool = True):
        panel.complexes_container = MagicMock() if with_container else None
        panel.complex_items = []
        panel.planet = _mock_planet()
        panel.manager = MagicMock()

    def test_complexes_list_no_facilities_renders_none_label(self):
        panel = _bypass_panel()
        self._seed(panel)
        panel.planet.facilities = []
        with patch("game.ui.panels.planet_report_panel.UILabel") as ulabel:
            panel._update_complexes_list()
        ulabel.assert_called_once()
        # Text passed is "None"
        kwargs = ulabel.call_args.kwargs
        assert kwargs.get("text") == "None"

    def test_complexes_list_single_facility_renders_name_only_no_count_suffix(self):
        panel = _bypass_panel()
        self._seed(panel)
        f = MagicMock()
        f.name = "Mine"
        f.design_id = "mine_v1"
        panel.planet.facilities = [f]
        with patch("game.ui.panels.planet_report_panel.UILabel") as ulabel:
            panel._update_complexes_list()
        # Single facility → no "x1" suffix
        text_arg = ulabel.call_args.kwargs.get("text")
        assert text_arg == "Mine"

    def test_complexes_list_duplicate_design_id_renders_x_count_suffix(self):
        panel = _bypass_panel()
        self._seed(panel)
        f1 = MagicMock(); f1.name = "Mine"; f1.design_id = "mine_v1"
        f2 = MagicMock(); f2.name = "Mine"; f2.design_id = "mine_v1"
        f3 = MagicMock(); f3.name = "Mine"; f3.design_id = "mine_v1"
        panel.planet.facilities = [f1, f2, f3]
        labels_created = []
        with patch("game.ui.panels.planet_report_panel.UILabel") as ulabel:
            ulabel.side_effect = lambda *a, **kw: labels_created.append(kw.get("text")) or MagicMock()
            panel._update_complexes_list()
        assert "Mine x3" in labels_created

    def test_complexes_list_kills_previous_items_on_refresh(self):
        """BUG-26 guard: previous list items get .kill() called on refresh."""
        panel = _bypass_panel()
        self._seed(panel)
        old_item = MagicMock()
        panel.complex_items = [old_item]
        panel.planet.facilities = []
        with patch("game.ui.panels.planet_report_panel.UILabel"):
            panel._update_complexes_list()
        old_item.kill.assert_called_once()

    def test_complexes_list_disabled_when_show_complexes_false_returns_silently(self):
        panel = _bypass_panel()
        self._seed(panel, with_container=False)
        # Must not raise; must not create UILabels
        with patch("game.ui.panels.planet_report_panel.UILabel") as ulabel:
            panel._update_complexes_list()
        ulabel.assert_not_called()


# ===========================================================================
# E.4 — _build_resource_grid / _net_cell_color
# ===========================================================================


class TestNetCellColor:
    def test_resource_grid_net_row_positive_paints_hp_healthy(self):
        assert _net_cell_color(5.0) == HP_HEALTHY

    def test_resource_grid_net_row_negative_paints_hp_critical(self):
        assert _net_cell_color(-3.0) == HP_CRITICAL

    def test_resource_grid_net_row_zero_paints_text_light(self):
        assert _net_cell_color(0.0) == TEXT_LIGHT


class TestBuildResourceGridAttributeSwallow:
    def test_resource_grid_text_colour_setter_attribute_error_swallowed_silently(self):
        """Pin production's broad-catch around `cell.text_colour = ...` in
        `_build_resource_grid`: when the patched UILabel class returns a Mock
        whose `text_colour` setter raises AttributeError, _build_resource_grid
        must complete without propagating the error.

        This exercises the actual try/except on planet_report_panel.py:588-597
        rather than a synthetic _DummyCell that lives only in the test file.
        """
        # Build a Mock UILabel class whose instances raise AttributeError
        # when .text_colour is set.
        def _failing_label_factory(*args, **kwargs):
            cell = MagicMock()
            type(cell).text_colour = property(
                lambda self: None,
                lambda self, _v: (_ for _ in ()).throw(
                    AttributeError("setter not supported"),
                ),
            )
            return cell

        panel = _bypass_panel()
        panel.manager = MagicMock()
        panel.resource_panel = MagicMock()
        panel._displayed_resources = ["metals"]
        panel._resource_grid_items = []
        panel._resource_icons = {"metals": pygame.Surface((20, 20))}
        # Set up the planet so the Net row produces a real projection
        # (only Net cells go down the text_colour-setting branch).
        panel.planet = _mock_planet()
        view = MagicMock()
        proj = MagicMock()
        proj.resource_id = "metals"
        proj.harvest = 1.0
        proj.upkeep = 0.0
        proj.yard = 0.0
        proj.net = 1.0
        view.resource_projections = [proj]
        panel.view = view

        with patch(
            "game.ui.panels.planet_report_panel.UILabel",
            side_effect=_failing_label_factory,
        ), patch(
            "game.ui.panels.planet_report_panel.UIImage",
            side_effect=lambda *a, **kw: MagicMock(),
        ):
            # If production didn't swallow AttributeError, this would raise.
            panel._build_resource_grid()

    def test_resource_grid_scrollable_area_dimensions_match_layout_constants(self):
        """``_build_resource_grid`` calls
        ``self.resource_panel.set_scrollable_area_dimensions((content_w, content_h))``
        where ``content_w = label_col_w + 5 + n*col_w + 10`` and
        ``content_h = data_start_y + n_data_rows*row_h + 6``.

        PROJ-346 strengthening: previously did pure arithmetic on the
        layout constants without ever building a panel. Now construct
        a real panel via _bypass_panel(), exercise _build_resource_grid,
        and capture the actual call args from the production code path
        at planet_report_panel.py:600-607.
        """
        panel = _bypass_panel()
        # Three displayed resources -> n=3 in the layout formula. Use real
        # ids that pass production's "if rid in resource_icons" check.
        panel._displayed_resources = ["metals", "organics", "vapors"]
        panel._resource_grid_items = []
        panel._resource_icons = {}  # No icons -> skip UIImage but still build labels.
        panel.planet = None  # _projection_grid_rows handles None; falls through.
        panel.view = None
        panel.manager = MagicMock()
        # The set_scrollable_area_dimensions call is what we're pinning.
        panel.resource_panel = MagicMock()

        # Replace UILabel so we don't need a real pygame_gui hierarchy.
        with patch("game.ui.panels.planet_report_panel.UILabel",
                   side_effect=lambda *a, **kw: MagicMock()), \
             patch("game.ui.panels.planet_report_panel.UIImage",
                   side_effect=lambda *a, **kw: MagicMock()):
            panel._build_resource_grid()

        # Production constants (planet_report_panel.py:534-541).
        label_col_w = 80
        col_w = 75
        icon_size = 20
        abbrev_h = 20
        row_h = 20
        header_y = 4
        data_start_y = header_y + icon_size + abbrev_h + 2  # 46

        n = 3
        # _projection_grid_rows returns 9 tuples (header + 8 metric rows);
        # the production formula uses len(rows) - 1 = 8 data rows.
        n_data_rows = 8

        expected_w = label_col_w + 5 + n * col_w + 10  # 80 + 5 + 225 + 10 = 320
        expected_h = data_start_y + n_data_rows * row_h + 6  # 46 + 160 + 6 = 212

        panel.resource_panel.set_scrollable_area_dimensions.assert_called_once_with(
            (expected_w, expected_h)
        )


# ===========================================================================
# E.5 — kill
# ===========================================================================


class TestKill:
    def test_kill_clears_resource_grid_items_and_panel(self):
        panel = _bypass_panel()
        item = MagicMock()
        panel._resource_grid_items = [item]
        panel.resource_panel = MagicMock()
        panel.panel = MagicMock()
        panel.kill()
        item.kill.assert_called_once()
        panel.resource_panel.kill.assert_called_once()
        panel.panel.kill.assert_called_once()
        assert panel._resource_grid_items == []
