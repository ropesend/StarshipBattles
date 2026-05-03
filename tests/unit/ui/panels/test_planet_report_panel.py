"""Tests for PlanetReportPanel (PROJ-142 Phase 2 Task 2.2).

Tests the planet report panel widget for displaying planet information
with atmosphere graphs and resource grids.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
import pygame


# --- Helpers ---

def _make_mock_planet():
    """Create a mock Planet with typical attributes."""
    planet = MagicMock()

    planet.name = "Terra Nova"
    planet.planet_type = MagicMock()
    planet.planet_type.name = "TERRESTRIAL"
    planet.atmosphere = {
        'N2': 78000,
        'O2': 21000,
        'Ar': 900,
        'CO2': 40
    }
    planet.deposits = {
        'minerals': {'quantity': 5000, 'quality': 0.8},
        'metals': {'quantity': 3000, 'quality': 0.6},
        'organics': {'quantity': 2000, 'quality': 0.9},
        'exotics': {'quantity': 100, 'quality': 0.3},
        'volatiles': {'quantity': 1500, 'quality': 0.5}
    }
    planet.facilities = []
    planet.owner_id = None

    return planet


def _make_mock_facility(name: str, design_id: str):
    """Create a mock facility."""
    facility = MagicMock()
    facility.name = name
    facility.design_id = design_id
    facility.is_operational = True
    facility.design_data = {}
    return facility


# --- PlanetReportPanel Import Tests ---

# --- Number Formatting Tests ---

class TestNumberFormatting:
    """Tests for compact number formatting (delegated to shared utility)."""

    def test_format_small_number(self):
        """Numbers < 1000 display as integers."""
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(500) == "500"

    def test_format_thousand(self):
        """Numbers 1000-999999 display with 'k' suffix."""
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(5000) == "5k"

    def test_format_large_thousand(self):
        """Large thousands format correctly."""
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(500000) == "500k"

    def test_format_million(self):
        """Numbers >= 1000000 display with 'M' suffix."""
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(5000000) == "5.0M"

    def test_format_million_decimal(self):
        """Millions display with one decimal place."""
        from game.ui.utils.formatters import format_compact_number
        assert format_compact_number(1500000) == "1.5M"


# --- Resource Grid Tests ---

class TestResourceGrid:
    """Tests for resource grid functionality."""

    def test_resource_grid_items_list_exists(self):
        """_resource_grid_items is a list."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        panel._resource_grid_items = []

        assert isinstance(panel._resource_grid_items, list)

    def test_update_resource_grid_calls_build(self):
        """_update_resource_grid calls _build_resource_grid."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        panel._build_resource_grid = MagicMock()

        panel._update_resource_grid()

        panel._build_resource_grid.assert_called_once()


# --- Portrait Tests ---

class TestPortrait:
    """Tests for planet portrait generation."""

    def test_portrait_uses_provided_surface(self):
        """_update_portrait uses provided portrait_surface."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        portrait = pygame.Surface((150, 150))
        panel.portrait_image = MagicMock()
        panel.planet = _make_mock_planet()

        panel._update_portrait(portrait)

        panel.portrait_image.set_image.assert_called_once()

    def test_portrait_generates_placeholder(self):
        """_update_portrait generates placeholder when no surface."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        panel.portrait_image = MagicMock()
        panel.planet = _make_mock_planet()

        panel._update_portrait(None)

        panel.portrait_image.set_image.assert_called_once()


# --- Height Required Tests ---

class TestHeightRequired:
    """Tests for get_height_required method."""

    def test_height_includes_resource_panel(self):
        """get_height_required includes RESOURCE_PANEL_HEIGHT."""
        from game.ui.panels.planet_report_panel import (
            PlanetReportPanel,
            RESOURCE_PANEL_HEIGHT
        )

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        height = panel.get_height_required()

        assert height == 350 + RESOURCE_PANEL_HEIGHT

    def test_height_is_integer(self):
        """get_height_required returns integer."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        height = panel.get_height_required()

        assert isinstance(height, int)


# --- Kill / Cleanup Tests ---

class TestPanelKill:
    """Tests for panel cleanup."""

    def test_kill_clears_resource_items(self):
        """kill clears resource grid items."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        item = MagicMock()
        panel._resource_grid_items = [item]
        panel.resource_panel = MagicMock()
        panel.panel = MagicMock()

        panel.kill()

        item.kill.assert_called_once()

    def test_kill_destroys_resource_panel(self):
        """kill destroys resource_panel."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        panel._resource_grid_items = []
        panel.resource_panel = MagicMock()
        panel.panel = MagicMock()

        panel.kill()

        panel.resource_panel.kill.assert_called_once()

    def test_kill_destroys_main_panel(self):
        """kill destroys main panel."""
        from game.ui.panels.planet_report_panel import PlanetReportPanel

        with patch.object(PlanetReportPanel, '__init__', lambda self, *a, **kw: None):
            panel = PlanetReportPanel.__new__(PlanetReportPanel)

        panel._resource_grid_items = []
        panel.resource_panel = MagicMock()
        panel.panel = MagicMock()

        panel.kill()

        panel.panel.kill.assert_called_once()


# --- compute_planet_production Tests ---

class TestComputePlanetProduction:
    """Tests for compute_planet_production function."""

    def test_unowned_planet_returns_empty(self, mock_registries):
        """Unowned planet returns empty dict."""
        from game.strategy.services.planet_economy_projector import compute_planet_production

        planet = _make_mock_planet()
        planet.owner_id = None

        result = compute_planet_production(planet, mock_registries)

        assert result == {}

    def test_function_accepts_planet(self, mock_registries):
        """compute_planet_production accepts planet argument."""
        from game.strategy.services.planet_economy_projector import compute_planet_production

        planet = _make_mock_planet()
        planet.owner_id = None

        # Should not raise
        result = compute_planet_production(planet, mock_registries)

        assert isinstance(result, dict)


# --- _get_harvester_info Tests ---

class TestGetHarvesterInfo:
    """Tests for _get_harvester_info helper."""

    def test_inline_harvester_returned(self):
        """Inline ResourceHarvester ability is returned."""
        from game.strategy.services.planet_economy_projector import _get_harvester_info

        comp = {
            'id': 'mining_facility',
            'abilities': {
                'ResourceHarvester': {
                    'resource_type': 'minerals',
                    'base_harvest_rate': 10.0
                }
            }
        }

        result = _get_harvester_info(comp, None)

        assert result is not None
        assert result['resource_type'] == 'minerals'

    def test_non_dict_returns_none(self):
        """Non-dict component returns None."""
        from game.strategy.services.planet_economy_projector import _get_harvester_info

        result = _get_harvester_info("not_a_dict", None)

        assert result is None

    def test_no_abilities_returns_none(self):
        """Component without abilities key returns None (falls to registry lookup)."""
        from game.strategy.services.planet_economy_projector import _get_harvester_info

        comp = {'id': 'basic_component'}
        registries = MagicMock()
        registries.components.get.return_value = None

        result = _get_harvester_info(comp, registries)

        assert result is None


# ===========================================================================
# Per-resource projection grid (transposed: icon-column header, metric rows)
# ===========================================================================
#
# When `view: ColonyDemographicView` is supplied, the resource panel renders a
# transposed grid: each resource is a column (icon + abbreviation header),
# each metric is a row. The pure helper
# `_projection_grid_rows(planet, view, displayed_ids)` returns the rows so
# cell text is testable without pygame.
#
# Row order: header, Qty, Qual, Harvest, Upkeep, Yard, Net, Stored, Cap.
#
# Sign convention in the flow rows (per design.md):
#   Harvest =  proj.harvest        (income — positive)
#   Upkeep  = -proj.upkeep         (display as a drain)
#   Yard    = -proj.yard           (display as a drain)
#   Net     =  proj.net            (already harvest - upkeep - yard)
#
# Cells with no data render "-" (Qty/Qual for non-deposit resources, flow
# rows for resources missing from projections, Stored/Cap for resources
# without stockpile entries).


def _make_projection(rid, *, harvest=0.0, upkeep=0.0, yard=0.0):
    from game.strategy.services.planet_economy_projector import (
        ResourceProjection,
    )
    return ResourceProjection(
        resource_id=rid,
        harvest=harvest,
        upkeep=upkeep,
        yard=yard,
        net=harvest - upkeep - yard,
    )


def _make_view_with_projections(projections):
    from game.strategy.facade.dto.colony_demographic_view import (
        ColonyDemographicView,
    )
    return ColonyDemographicView(
        planet_id=1,
        planet_name="Test",
        species=(),
        resource_projections=tuple(projections),
        total_upkeep={},
    )


def _make_planet(*, deposits=None, stockpile=None, max_stockpile=None):
    """Stub planet exposing only the dict attributes the helper reads."""
    return MagicMock(
        deposits=deposits or {},
        stockpile=stockpile or {},
        max_stockpile=max_stockpile or {},
    )


# Indices of named rows in the helper's output. Pinned in
# `test_eight_metric_rows_in_canonical_order` — referenced everywhere
# else as a single source of truth.
_HEADER_ROW = 0
_QTY_ROW = 1
_QUAL_ROW = 2
_HARVEST_ROW = 3
_UPKEEP_ROW = 4
_YARD_ROW = 5
_NET_ROW = 6
_STORED_ROW = 7
_CAP_ROW = 8


class TestProjectionGridRows:
    """Pure data-shape tests for the transposed (icon-column) grid."""

    def test_header_row_is_resource_ids(self):
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        rows = _projection_grid_rows(_make_planet(), None, ["metals", "organics", "fuel"])

        assert rows[_HEADER_ROW] == ("", "metals", "organics", "fuel")

    def test_eight_metric_rows_in_canonical_order(self):
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        rows = _projection_grid_rows(_make_planet(), None, ["metals"])

        labels = [r[0] for r in rows]
        assert labels == [
            "", "Qty", "Qual", "Harvest", "Upkeep", "Yard", "Net", "Stored", "Cap",
        ]

    def test_qty_cell_from_planet_deposits(self):
        from game.ui.panels.planet_report_panel import _projection_grid_rows
        from game.ui.utils.formatters import format_compact_number

        planet = _make_planet(deposits={"metals": {"quantity": 5000, "quality": 0.8}})

        rows = _projection_grid_rows(planet, None, ["metals"])

        assert rows[_QTY_ROW][1] == format_compact_number(5000)

    def test_qual_cell_from_planet_deposits(self):
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        planet = _make_planet(deposits={"metals": {"quantity": 5000, "quality": 0.8}})

        rows = _projection_grid_rows(planet, None, ["metals"])

        assert rows[_QUAL_ROW][1] == "0.8"

    def test_qty_qual_cells_dash_when_no_deposit(self):
        """fuel/energy/ammo are operational — no deposits, so Qty/Qual = '-'."""
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        rows = _projection_grid_rows(_make_planet(), None, ["fuel"])

        assert rows[_QTY_ROW][1] == "-"
        assert rows[_QUAL_ROW][1] == "-"

    def test_harvest_row_uses_signed_format(self):
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        view = _make_view_with_projections([_make_projection("metals", harvest=8.0)])

        rows = _projection_grid_rows(_make_planet(), view, ["metals"])

        assert rows[_HARVEST_ROW][1] == "+8.0"

    def test_upkeep_row_displayed_as_drain(self):
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        view = _make_view_with_projections([_make_projection("organics", upkeep=10.0)])

        rows = _projection_grid_rows(_make_planet(), view, ["organics"])

        assert rows[_UPKEEP_ROW][1] == "-10.0"

    def test_yard_row_displayed_as_drain(self):
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        view = _make_view_with_projections([_make_projection("metals", yard=4.2)])

        rows = _projection_grid_rows(_make_planet(), view, ["metals"])

        assert rows[_YARD_ROW][1] == "-4.2"

    def test_net_row_uses_signed_format_directly(self):
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        view = _make_view_with_projections([
            _make_projection("organics", harvest=12.4, upkeep=10.0, yard=1.5),
        ])

        rows = _projection_grid_rows(_make_planet(), view, ["organics"])

        # net = 12.4 - 10.0 - 1.5 = 0.9
        assert rows[_NET_ROW][1] == "+0.9"

    def test_zero_drain_in_projection_shows_signed_zero(self):
        """Resource present in projection but with zero upkeep/yard still
        renders aligned numerics (`+0.0`), not blank — keeps the grid
        readable when only one stream is non-zero."""
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        view = _make_view_with_projections([_make_projection("vapors", harvest=5.1)])

        rows = _projection_grid_rows(_make_planet(), view, ["vapors"])

        assert rows[_UPKEEP_ROW][1] == "+0.0"
        assert rows[_YARD_ROW][1] == "+0.0"

    def test_flow_rows_dash_when_resource_not_in_projections(self):
        """fuel/energy/ammo aren't harvested by planets — flow rows show '-'
        rather than misleading +0.0, since 'no projection signal' is
        semantically distinct from 'projected zero'."""
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        view = _make_view_with_projections([_make_projection("metals", harvest=8.0)])

        rows = _projection_grid_rows(_make_planet(), view, ["fuel"])

        assert rows[_HARVEST_ROW][1] == "-"
        assert rows[_UPKEEP_ROW][1] == "-"
        assert rows[_YARD_ROW][1] == "-"
        assert rows[_NET_ROW][1] == "-"

    def test_flow_rows_dash_when_view_is_none(self):
        """Unowned planet — view is None — flow rows blank for every column."""
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        rows = _projection_grid_rows(_make_planet(), None, ["metals"])

        assert rows[_HARVEST_ROW][1] == "-"
        assert rows[_UPKEEP_ROW][1] == "-"
        assert rows[_YARD_ROW][1] == "-"
        assert rows[_NET_ROW][1] == "-"

    def test_stored_cap_rows_from_planet_stockpile(self):
        from game.ui.panels.planet_report_panel import _projection_grid_rows
        from game.ui.utils.formatters import format_compact_number

        planet = _make_planet(
            stockpile={"metals": 18000.0},
            max_stockpile={"metals": 50000.0},
        )

        rows = _projection_grid_rows(planet, None, ["metals"])

        assert rows[_STORED_ROW][1] == format_compact_number(18000.0)
        assert rows[_CAP_ROW][1] == format_compact_number(50000.0)

    def test_stored_cap_rows_dash_when_no_stockpile_entry(self):
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        rows = _projection_grid_rows(_make_planet(), None, ["metals"])

        assert rows[_STORED_ROW][1] == "-"
        assert rows[_CAP_ROW][1] == "-"

    def test_stored_cap_work_for_operational_resources(self):
        """fuel/energy/ammo have no deposits but planets can stock them.
        Stored/Cap MUST populate so operational columns aren't all '-'."""
        from game.ui.panels.planet_report_panel import _projection_grid_rows
        from game.ui.utils.formatters import format_compact_number

        planet = _make_planet(
            stockpile={"fuel": 500.0},
            max_stockpile={"fuel": 5000.0},
        )

        rows = _projection_grid_rows(planet, None, ["fuel"])

        assert rows[_STORED_ROW][1] == format_compact_number(500.0)
        assert rows[_CAP_ROW][1] == format_compact_number(5000.0)

    def test_each_row_has_one_label_plus_one_cell_per_resource(self):
        """Every row tuple is (label, cell_for_res0, cell_for_res1, ...).
        Same width across all rows so callers can index by column."""
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        rows = _projection_grid_rows(_make_planet(), None, ["metals", "organics", "fuel"])

        for row in rows:
            assert len(row) == 4  # 1 label + 3 resource columns

    def test_data_driven_resource_list_grows_columns(self):
        """The displayed_ids list IS the column set — adding a new resource
        just appears as another column with no code change. Generic contract."""
        from game.ui.panels.planet_report_panel import _projection_grid_rows

        rows = _projection_grid_rows(
            _make_planet(), None, ["metals", "organics", "fuel", "dilithium"],
        )

        assert all(len(row) == 5 for row in rows)
        assert rows[_HEADER_ROW] == ("", "metals", "organics", "fuel", "dilithium")


class TestNetCellColor:
    """Net column colour: green positive, red negative, default zero."""

    def test_positive_net_is_green(self):
        from game.ui.panels.planet_report_panel import _net_cell_color
        from game.ui.colors import HP_HEALTHY
        assert _net_cell_color(1.0) == HP_HEALTHY

    def test_negative_net_is_red(self):
        from game.ui.panels.planet_report_panel import _net_cell_color
        from game.ui.colors import HP_CRITICAL
        assert _net_cell_color(-1.0) == HP_CRITICAL

    def test_zero_net_is_default(self):
        from game.ui.panels.planet_report_panel import _net_cell_color
        from game.ui.colors import TEXT_LIGHT
        assert _net_cell_color(0.0) == TEXT_LIGHT


# ---------------------------------------------------------------------------
# PROJ-292 Phase 4 (H3): `_build_projection_grid` net-cell colour code
# wraps `cell.text_colour = color` in a try/except to tolerate pygame_gui
# versions that don't expose a setter. Pre-fix: the catch was
# `except (AttributeError, Exception)` — a catch-all that swallows real
# bugs (RuntimeError, TypeError, etc.). Post-fix: narrow to
# `except AttributeError` only.
# ---------------------------------------------------------------------------


class _RaisingCell:
    """Stand-in for a `UILabel` whose `text_colour` setter raises the
    given exception. Used to assert the try/except's catch scope."""

    def __init__(self, exc: Exception):
        self._exc = exc

    @property
    def text_colour(self):
        return None

    @text_colour.setter
    def text_colour(self, _value):
        raise self._exc

    def rebuild(self):
        pass


def _make_panel_for_projection_grid(view, *, displayed_resources=("metals",)):
    """Bypass-init a `PlanetReportPanel` with the minimum attributes
    `_build_projection_grid` reads. Callers patch `UILabel`/`UIImage` to
    control the cells the method constructs.

    `displayed_resources` controls how many columns the grid renders —
    in production this comes from `ResourceCatalog`; tests pin it
    explicitly so label-count assertions stay deterministic."""
    from game.ui.panels.planet_report_panel import PlanetReportPanel

    panel = PlanetReportPanel.__new__(PlanetReportPanel)
    panel.manager = MagicMock()
    panel.view = view
    panel.resource_panel = MagicMock()
    panel.resource_panel.relative_rect = MagicMock()
    panel.resource_panel.relative_rect.width = 800
    panel._resource_grid_items = []
    panel._resource_icons = {res: MagicMock() for res in displayed_resources}
    panel._displayed_resources = list(displayed_resources)
    panel.planet = MagicMock(deposits={}, stockpile={}, max_stockpile={})
    return panel


def _make_view_with_one_drained_resource():
    """Single-row projection view so `_build_projection_grid` hits
    exactly one net-cell colour-setting code path."""
    from game.strategy.services.planet_economy_projector import ResourceProjection

    # Use a stub object because `ColonyDemographicView` may have other
    # required fields; we only need `resource_projections` for this path.
    view = MagicMock()
    view.resource_projections = [
        ResourceProjection(
            resource_id="metals",
            harvest=10.0, upkeep=1.0, yard=2.0, net=7.0,
        ),
    ]
    return view


class TestNetCellColorExceptionHandling:
    """PROJ-292 H3: narrow the catch in `_build_projection_grid` so only
    `AttributeError` from pygame_gui's text_colour-setter variance is
    swallowed. Other exceptions must propagate so real bugs surface."""

    def test_attribute_error_silently_swallowed(self):
        """Pre-existing + post-fix behaviour: an `AttributeError` raised
        by `cell.text_colour = ...` is swallowed — pygame_gui version
        variance on the setter is expected and non-essential."""
        view = _make_view_with_one_drained_resource()
        panel = _make_panel_for_projection_grid(view)

        with patch(
            "game.ui.panels.planet_report_panel.UILabel",
            side_effect=lambda *a, **kw: _RaisingCell(AttributeError("no setter")),
        ), patch(
            "game.ui.panels.planet_report_panel.UIImage", return_value=MagicMock(),
        ):
            # No exception should propagate.
            panel._build_resource_grid()

    def test_runtime_error_propagates(self):
        """Post-fix: a non-AttributeError exception (e.g. programming
        bug in the colour pipeline) must propagate instead of being
        silently swallowed."""
        view = _make_view_with_one_drained_resource()
        panel = _make_panel_for_projection_grid(view)

        with patch(
            "game.ui.panels.planet_report_panel.UILabel",
            side_effect=lambda *a, **kw: _RaisingCell(RuntimeError("real bug")),
        ), patch(
            "game.ui.panels.planet_report_panel.UIImage", return_value=MagicMock(),
        ):
            with pytest.raises(RuntimeError, match="real bug"):
                panel._build_resource_grid()


# ---------------------------------------------------------------------------
# PROJ-292 m9 (Phase 5 Task 5.8): UI assembly test for _build_projection_grid.
# The grid code constructs N×5 labels + an optional stockpile summary
# line per call — this test pins the label count and rect non-overlap so
# a refactor that adds/removes labels or mangles rect math is caught.
# ---------------------------------------------------------------------------


def _rect(*args, **kwargs):
    """Tiny `pygame.Rect`-like helper carrying `x`, `y`, `w`, `h`.
    Used only so the rect-assertion doesn't depend on pygame's C-level
    Rect — it lets us capture construction args from the mock."""
    return args, kwargs


class TestProjectionGridAssembly:
    """Pin the label/image counts and rect non-overlap for
    `_build_projection_grid` so future refactors can't silently drop
    rows, duplicate cells, or alias rects.

    Layout (transposed): for N displayed resources,
      - header row = N UIImage icons + N UILabel abbreviations
      - 8 data rows × (1 row-label + N value cells) = 8 + 8N UILabels
      - Grand total: UILabels = N + 8 + 8N = 8 + 9N.
                     UIImages = N.
    """

    def _make_view_with_n_resources(self, n: int):
        from game.strategy.services.planet_economy_projector import ResourceProjection

        view = MagicMock()
        view.resource_projections = tuple(
            ResourceProjection(
                resource_id=f"res{i}",
                harvest=10.0 * (i + 1), upkeep=1.0, yard=0.5, net=8.0,
            )
            for i in range(n)
        )
        return view

    def test_label_count_scales_with_resource_count(self):
        """N=3 columns -> UILabel count = 8 + 9N = 35."""
        view = self._make_view_with_n_resources(3)
        panel = _make_panel_for_projection_grid(
            view, displayed_resources=("res0", "res1", "res2"),
        )

        with patch(
            "game.ui.panels.planet_report_panel.UILabel", return_value=MagicMock(),
        ) as mock_label, patch(
            "game.ui.panels.planet_report_panel.UIImage", return_value=MagicMock(),
        ):
            panel._build_resource_grid()

        n = 3
        expected_label_count = 8 + 9 * n
        assert mock_label.call_count == expected_label_count, (
            f"Expected {expected_label_count} UILabel constructions for "
            f"a {n}-resource transposed grid; got {mock_label.call_count}"
        )

    def test_image_count_equals_resource_count(self):
        """One icon per displayed resource — no extra images."""
        view = self._make_view_with_n_resources(3)
        panel = _make_panel_for_projection_grid(
            view, displayed_resources=("res0", "res1", "res2"),
        )

        with patch(
            "game.ui.panels.planet_report_panel.UILabel", return_value=MagicMock(),
        ), patch(
            "game.ui.panels.planet_report_panel.UIImage", return_value=MagicMock(),
        ) as mock_image:
            panel._build_resource_grid()

        assert mock_image.call_count == 3

    def test_label_count_with_eight_resources(self):
        """N=8 (full catalog) -> UILabel count = 8 + 9*8 = 80."""
        view = self._make_view_with_n_resources(0)  # zero projections, all '-' flow rows
        panel = _make_panel_for_projection_grid(
            view,
            displayed_resources=tuple(f"res{i}" for i in range(8)),
        )

        with patch(
            "game.ui.panels.planet_report_panel.UILabel", return_value=MagicMock(),
        ) as mock_label, patch(
            "game.ui.panels.planet_report_panel.UIImage", return_value=MagicMock(),
        ):
            panel._build_resource_grid()

        assert mock_label.call_count == 8 + 9 * 8

    def test_grid_cells_do_not_overlap(self):
        """No two UILabel rects produced by `_build_projection_grid`
        share the same (x, y) anchor point. Proves the per-row + per-col
        positioning math doesn't alias cells on top of each other."""
        view = self._make_view_with_n_resources(3)
        panel = _make_panel_for_projection_grid(
            view, displayed_resources=("res0", "res1", "res2"),
        )

        captured_rects = []

        def _capture(*args, relative_rect=None, **kwargs):
            if relative_rect is not None:
                captured_rects.append((
                    relative_rect.x, relative_rect.y,
                    relative_rect.width, relative_rect.height,
                ))
            return MagicMock()

        with patch(
            "game.ui.panels.planet_report_panel.UILabel", side_effect=_capture,
        ), patch(
            "game.ui.panels.planet_report_panel.UIImage", side_effect=_capture,
        ):
            panel._build_resource_grid()

        anchors = [(x, y) for (x, y, w, h) in captured_rects]
        assert len(anchors) == len(set(anchors)), (
            f"Label/image anchors collide — rects overlap: {captured_rects}"
        )


# ---------------------------------------------------------------------------
# Regression: pygame_gui's UILabel emits a UserWarning when the rect is
# smaller than the rendered text. The default theme font (arial-14) renders
# at ~20px tall, so every cell rect must be at least 20px tall. This test
# guards against ~110 startup warnings that appeared when row_h/abbrev_h
# were 14.
# ---------------------------------------------------------------------------


class TestResourceGridLabelSizing:
    """Cell rects in the resource grid must fit the default theme font."""

    # Default theme font is arial-14 (data/builder_theme.json). Its rendered
    # line height under pygame.freetype.get_rect() is ~20px. pygame_gui's
    # UILabel warns when rect.height < text height.
    _MIN_CELL_HEIGHT = 20

    def _capture_label_rects(self, n_resources: int):
        """Run `_build_resource_grid` and return only the UILabel
        relative_rects as `(x, y, w, h)` tuples. UIImage rects (icons)
        are excluded so size assertions reason about text-bearing cells
        only."""
        from game.strategy.services.planet_economy_projector import ResourceProjection

        view = MagicMock()
        view.resource_projections = tuple(
            ResourceProjection(
                resource_id=f"res{i}",
                harvest=10.0, upkeep=1.0, yard=0.5, net=8.0,
            )
            for i in range(n_resources)
        )
        panel = _make_panel_for_projection_grid(
            view,
            displayed_resources=tuple(f"res{i}" for i in range(n_resources)),
        )

        captured = []

        def _capture_label(*args, relative_rect=None, **kwargs):
            if relative_rect is not None:
                captured.append((
                    relative_rect.x, relative_rect.y,
                    relative_rect.width, relative_rect.height,
                ))
            return MagicMock()

        with patch(
            "game.ui.panels.planet_report_panel.UILabel", side_effect=_capture_label,
        ), patch(
            "game.ui.panels.planet_report_panel.UIImage", return_value=MagicMock(),
        ):
            panel._build_resource_grid()

        return captured

    def test_all_label_rects_tall_enough_for_default_font(self):
        """Every cell rect must be >= 20px tall to fit arial-14 text."""
        rects = self._capture_label_rects(n_resources=8)
        too_short = [r for r in rects if r[3] < self._MIN_CELL_HEIGHT]
        assert not too_short, (
            f"{len(too_short)} cell rect(s) are shorter than "
            f"{self._MIN_CELL_HEIGHT}px — pygame_gui will emit "
            f"'Label Rect is too small for text' UserWarnings. "
            f"Offenders: {too_short}"
        )

    def test_row_label_column_wide_enough_for_longest_label(self):
        """Row-label column must fit 'Harvest'/'Upkeep'/'Stored' (~50-55px
        rendered at arial-14) with reasonable slack."""
        rects = self._capture_label_rects(n_resources=8)
        # Row labels are at x=5 (label_col_w left edge after 5px margin).
        row_label_widths = {w for (x, y, w, h) in rects if x == 5}
        assert row_label_widths, "expected at least one row-label rect at x=5"
        assert all(w >= 70 for w in row_label_widths), (
            f"Row label column width(s) {row_label_widths} too small to "
            f"fit longest row label 'Harvest' (~55px text) with slack."
        )

    def test_value_cell_columns_wide_enough_for_typical_numbers(self):
        """Resource value cells must fit numbers like '+11347.5' (~50px
        rendered at arial-14) with slack — previous implementation
        compressed columns to 40-41px, leaving only 1px slack."""
        rects = self._capture_label_rects(n_resources=8)
        # Value cells share x positions stepped by col_w; widths are uniform.
        # Filter out the row-label column (x == 5) and the icon row.
        value_widths = {w for (x, y, w, h) in rects if x != 5}
        assert value_widths, "expected non-row-label cells to be captured"
        assert all(w >= 60 for w in value_widths), (
            f"Value cell width(s) {value_widths} too small to fit typical "
            f"signed numeric strings with comfortable slack."
        )


# ---------------------------------------------------------------------------
# Regression: the resource grid lives in a UIScrollingContainer and must
# call set_scrollable_area_dimensions so horizontal/vertical scrollbars
# appear automatically when the resource catalog or grid grows past the
# viewport.
# ---------------------------------------------------------------------------


class TestResourceGridScrolling:
    """`_build_resource_grid` must size the scrollable content area."""

    def test_set_scrollable_area_dimensions_called(self):
        """After building the grid, the scrolling container is told how
        large its content is so scrollbars appear when needed."""
        from game.strategy.services.planet_economy_projector import ResourceProjection

        view = MagicMock()
        view.resource_projections = (
            ResourceProjection(
                resource_id="res0", harvest=1.0, upkeep=0.0, yard=0.0, net=1.0,
            ),
        )
        panel = _make_panel_for_projection_grid(
            view, displayed_resources=("res0",),
        )

        with patch(
            "game.ui.panels.planet_report_panel.UILabel", return_value=MagicMock(),
        ), patch(
            "game.ui.panels.planet_report_panel.UIImage", return_value=MagicMock(),
        ):
            panel._build_resource_grid()

        panel.resource_panel.set_scrollable_area_dimensions.assert_called_once()
        args, _ = panel.resource_panel.set_scrollable_area_dimensions.call_args
        (content_w, content_h) = args[0]
        assert content_w > 0 and content_h > 0, (
            f"scrollable area must be positive; got ({content_w}, {content_h})"
        )

    def test_content_width_grows_with_resource_count(self):
        """Adding more resource columns increases scrollable content width
        — proving the grid uses fixed cell widths rather than compressing
        to fit the viewport."""
        from game.strategy.services.planet_economy_projector import ResourceProjection

        def _content_width(n: int) -> int:
            view = MagicMock()
            view.resource_projections = tuple(
                ResourceProjection(
                    resource_id=f"res{i}", harvest=1.0, upkeep=0.0, yard=0.0, net=1.0,
                )
                for i in range(n)
            )
            panel = _make_panel_for_projection_grid(
                view,
                displayed_resources=tuple(f"res{i}" for i in range(n)),
            )
            with patch(
                "game.ui.panels.planet_report_panel.UILabel", return_value=MagicMock(),
            ), patch(
                "game.ui.panels.planet_report_panel.UIImage", return_value=MagicMock(),
            ):
                panel._build_resource_grid()
            args, _ = panel.resource_panel.set_scrollable_area_dimensions.call_args
            return args[0][0]

        assert _content_width(8) > _content_width(3), (
            "scrollable content width must grow with resource count "
            "(fixed col_w design); compression-to-fit re-introduces the "
            "tight-cell warnings the scrolling container is meant to avoid"
        )
