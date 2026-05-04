"""
Unit tests for EmpireTreasuryPanel.

PROJ-99 Phase 2: Tests for treasury panel layout, formatting, and data binding.
"""
import pytest
from unittest.mock import MagicMock, patch

from game.strategy.engine.empire_economy_calculator import EmpireEconomySnapshot

PLANET_RESOURCE_NAMES = ["metals", "organics", "vapors", "radioactives", "exotics"]
from game.ui.panels.empire_treasury_panel import (
    EmpireTreasuryPanel,
    LABEL_COL_WIDTH,
    RESOURCE_COL_WIDTH,
    ICON_SIZE,
    ROW_HEIGHT,
)
from game.ui.utils.resource_display import RESOURCE_ABBREVIATIONS


# =============================================================================
# Fixtures
# =============================================================================

# =============================================================================
# PROJ-327 Phase 2 Task 2.11: scope-rescope notes
#
# `mock_ui_manager`, `mock_panel`, and `mock_resource_icons` are pure inputs:
# they are passed to `EmpireTreasuryPanel(...)` and the production code only
# reads from them (`panel.get_relative_rect()`, `ui_manager` as a `manager=`
# kwarg, `resource_icons[name]` as a lookup). No test in this file mutates
# any of these three fixtures. Rescoping them to module shaves ~17x the
# per-test MagicMock-tree construction cost without functional impact.
#
# `sample_snapshot` IS mutated by 4 tests in TestPopulationUpkeepRow
# (`sample_snapshot.total_population_upkeep = ...`). It MUST remain
# function-scoped, otherwise the mutations leak across tests.
#
# Original PROJ-322 Task 2.11 deferral cited "mutable MagicMocks accumulate
# assert state" (i.e. .assert_called_once_with after a call records state).
# That is true, but only `mock_panel.get_relative_rect`,
# `mock_container.assert_called_once`, `old_container.kill.assert_called_once`,
# and similar call-records are checked — and those are checked on either
# (a) the inner `mock_container`/`mock_header`/etc that come from `@patch`
# decorators (not these fixtures), or (b) `panel._scroll_container.kill`
# /element.kill (also not these fixtures). So accumulated call state on
# `mock_ui_manager` / `mock_panel` / `mock_resource_icons` is never asserted
# on in this file. Rescope is safe.
# =============================================================================


def _build_sample_snapshot() -> EmpireEconomySnapshot:
    """Build a sample EmpireEconomySnapshot with test data (constructor body)."""
    snapshot = EmpireEconomySnapshot()

    # Production
    snapshot.colony_production = {
        "metals": 100.0, "organics": 200.0, "vapors": 50.0,
        "radioactives": 25.0, "exotics": 10.0
    }
    snapshot.ship_production = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.trade_production = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.tribute_production = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.mining_production = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.total_production = snapshot.colony_production.copy()

    # Expenses
    snapshot.tribute_expenses = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.construction_expenses_ships = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.construction_expenses_complexes = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.total_expenses = {r: 0.0 for r in PLANET_RESOURCE_NAMES}

    # Treasury
    snapshot.net_resources = {
        "metals": 100.0, "organics": 200.0, "vapors": 50.0,
        "radioactives": 25.0, "exotics": 10.0
    }
    snapshot.current_storage = {
        "metals": 5000.0, "organics": 3000.0, "vapors": 1000.0,
        "radioactives": 500.0, "exotics": 100.0
    }
    snapshot.max_storage = {
        "metals": 10000.0, "organics": 10000.0, "vapors": 10000.0,
        "radioactives": 10000.0, "exotics": 10000.0
    }

    return snapshot


@pytest.fixture
def sample_snapshot() -> EmpireEconomySnapshot:
    """Create a sample EmpireEconomySnapshot with test data.

    Function-scoped: 4 tests in TestPopulationUpkeepRow mutate
    `snapshot.total_population_upkeep` and would otherwise leak across tests.
    """
    return _build_sample_snapshot()


@pytest.fixture(scope="module")
def mock_ui_manager():
    """Mock pygame_gui UIManager. Module-scoped: pure-input MagicMock,
    never mutated nor asserted-on across the file (PROJ-327 Phase 2 Task 2.11)."""
    return MagicMock()


@pytest.fixture(scope="module")
def mock_panel():
    """Mock UIPanel with realistic dimensions. Module-scoped: pure-input
    container, only `.get_relative_rect()` is called (returns the same inner
    MagicMock) and tests verify identity, not call counts (PROJ-327 Phase 2
    Task 2.11)."""
    panel = MagicMock()
    panel.get_relative_rect.return_value = MagicMock(width=800, height=600)
    return panel


@pytest.fixture(scope="module")
def mock_resource_icons():
    """Mock resource icons dict. Module-scoped: pure-input lookup table,
    never mutated nor asserted-on (PROJ-327 Phase 2 Task 2.11)."""
    icons = {}
    for resource in PLANET_RESOURCE_NAMES:
        mock_surface = MagicMock()
        mock_surface.get_size.return_value = (ICON_SIZE, ICON_SIZE)
        icons[resource] = mock_surface
    return icons


# =============================================================================
# Resource Abbreviations Tests
# =============================================================================

class TestResourceAbbreviations:
    """Tests for resource name abbreviations."""

    def test_all_resources_have_abbreviations(self):
        """All planet resources should have abbreviations defined."""
        for resource in PLANET_RESOURCE_NAMES:
            assert resource in RESOURCE_ABBREVIATIONS

    def test_abbreviations_are_short(self):
        """Abbreviations should be 3 characters or less."""
        for abbrev in RESOURCE_ABBREVIATIONS.values():
            assert len(abbrev) <= 3

    def test_expected_abbreviations(self):
        """Check expected abbreviation values."""
        assert RESOURCE_ABBREVIATIONS["metals"] == "Met"
        assert RESOURCE_ABBREVIATIONS["organics"] == "Org"
        assert RESOURCE_ABBREVIATIONS["vapors"] == "Vap"
        assert RESOURCE_ABBREVIATIONS["radioactives"] == "Rad"
        assert RESOURCE_ABBREVIATIONS["exotics"] == "Exo"


# =============================================================================
# Value Formatting Tests
# =============================================================================

class TestValueFormatting:
    """Tests for _format_value method."""

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_format_zero_returns_zero(self, mock_image, mock_label, mock_container, mock_header,
                                       mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Zero values should format as '0'."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        assert panel._format_value(0) == "0"
        assert panel._format_value(0.0) == "0"

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_format_small_integers(self, mock_image, mock_label, mock_container, mock_header,
                                    mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Small integers should format without commas."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        assert panel._format_value(5) == "5"
        assert panel._format_value(100) == "100"
        assert panel._format_value(999) == "999"

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_format_large_integers_with_commas(self, mock_image, mock_label, mock_container, mock_header,
                                                mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Large integers should format with comma separators."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        assert panel._format_value(1000) == "1,000"
        assert panel._format_value(10000) == "10,000"
        assert panel._format_value(1000000) == "1,000,000"

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_format_floats_rounds_to_integer(self, mock_image, mock_label, mock_container, mock_header,
                                              mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Float values should round to nearest integer."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        assert panel._format_value(9.5) == "10"  # Round up
        assert panel._format_value(9.4) == "9"   # Round down
        assert panel._format_value(1234.7) == "1,235"


# =============================================================================
# Row Data Tests
# =============================================================================

class TestRowData:
    """Tests for row data structure methods."""

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_production_rows_structure(self, mock_image, mock_label, mock_container, mock_header,
                                        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Production rows should have correct structure."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_production_rows()

        assert len(rows) == 6  # 5 sources + total
        assert rows[0][0] == "From Colonies"
        assert rows[5][0] == "Total"
        assert rows[5][2] is True  # Total row has is_total=True

        # Non-total rows have is_total=False
        for i in range(5):
            assert rows[i][2] is False

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_expense_rows_structure(self, mock_image, mock_label, mock_container, mock_header,
                                     mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Expense rows should have correct structure."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()

        assert len(rows) == 4  # 3 categories + total
        assert rows[0][0] == "Tributes"
        assert rows[1][0] == "Construction Queues (Ships)"
        assert rows[2][0] == "Construction Queues (Complexes)"
        assert rows[3][0] == "Total"
        assert rows[3][2] is True

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_treasury_rows_structure(self, mock_image, mock_label, mock_container, mock_header,
                                      mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Treasury rows should have correct structure."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_treasury_rows()

        assert len(rows) == 3
        assert rows[0][0] == "Net Resources"
        assert rows[1][0] == "Total In Storage"
        assert rows[2][0] == "Maximum Storage"

        # No total rows in treasury section
        for row in rows:
            assert row[2] is False

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_production_rows_use_snapshot_data(self, mock_image, mock_label, mock_container, mock_header,
                                                mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Production rows should reference snapshot data."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_production_rows()

        # Check that rows contain actual snapshot data
        assert rows[0][1] is sample_snapshot.colony_production
        assert rows[5][1] is sample_snapshot.total_production


# =============================================================================
# PROJ-290 Phase 1: Population Upkeep row
# =============================================================================

class TestPopulationUpkeepRow:
    """Tests for the PROJ-290 "Population Upkeep" expense row.

    Inserted before the "Total" row when
    `snapshot.total_population_upkeep` has any non-zero entries. Hidden
    (row not emitted) when the dict is empty or all-zero — avoids
    visual noise in a fresh game with no populations yet.

    Cell values are rendered as NEGATIVE floats (drain). Only resources
    with upkeep entries produce cells; resources absent from the dict
    render as 0 via the existing per-column default.
    """

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_row_hidden_when_total_population_upkeep_empty(
        self, mock_image, mock_label, mock_container, mock_header,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Fresh-game snapshot with `total_population_upkeep == {}` →
        expense section stays at the legacy 4 rows (no "Population Upkeep")."""
        assert sample_snapshot.total_population_upkeep == {}
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()
        labels = [r[0] for r in rows]
        assert "Population Upkeep" not in labels
        assert len(rows) == 4

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_row_hidden_when_all_values_zero(
        self, mock_image, mock_label, mock_container, mock_header,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Dict populated but every value is 0 → still hidden."""
        sample_snapshot.total_population_upkeep = {
            "organics": 0.0, "metals": 0.0, "radioactives": 0.0,
        }
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()
        labels = [r[0] for r in rows]
        assert "Population Upkeep" not in labels

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_row_visible_with_single_resource_upkeep(
        self, mock_image, mock_label, mock_container, mock_header,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """`{"organics": 5.0}` → row shown, organics cell is -5.0 drain."""
        sample_snapshot.total_population_upkeep = {"organics": 5.0}
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()

        labels = [r[0] for r in rows]
        assert "Population Upkeep" in labels
        upkeep_row = next(r for r in rows if r[0] == "Population Upkeep")
        label, values, is_total = upkeep_row
        assert is_total is False
        # Drain = NEGATIVE
        assert values["organics"] == pytest.approx(-5.0)
        # Unused resources default to 0 (sparse dict).
        assert values.get("metals", 0.0) == 0.0

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_row_visible_with_multi_resource_upkeep(
        self, mock_image, mock_label, mock_container, mock_header,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Multi-resource upkeep: every key becomes a negative cell."""
        sample_snapshot.total_population_upkeep = {
            "organics": 1.5, "metals": 0.15, "radioactives": 0.015,
        }
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()

        upkeep_row = next(r for r in rows if r[0] == "Population Upkeep")
        values = upkeep_row[1]
        assert values["organics"] == pytest.approx(-1.5)
        assert values["metals"] == pytest.approx(-0.15)
        assert values["radioactives"] == pytest.approx(-0.015)

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_upkeep_row_inserted_before_total(
        self, mock_image, mock_label, mock_container, mock_header,
        mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons,
    ):
        """Population Upkeep must appear BEFORE the Total row so the
        running-total visually aggregates below it."""
        sample_snapshot.total_population_upkeep = {"organics": 1.0}
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)
        rows = panel._get_expense_rows()
        labels = [r[0] for r in rows]
        assert labels.index("Population Upkeep") < labels.index("Total")


# =============================================================================
# Panel Construction Tests
# =============================================================================

class TestPanelConstruction:
    """Tests for panel initialization and construction."""

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_panel_stores_references(self, mock_image, mock_label, mock_container, mock_header,
                                      mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Panel should store all constructor arguments."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)

        assert panel.panel is mock_panel
        assert panel.ui_manager is mock_ui_manager
        assert panel.snapshot is sample_snapshot
        assert panel.resource_icons is mock_resource_icons

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_scroll_container_created(self, mock_image, mock_label, mock_container, mock_header,
                                       mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Panel should create a scroll container."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)

        mock_container.assert_called_once()
        assert panel._scroll_container is not None


# =============================================================================
# Refresh Tests
# =============================================================================

class TestRefresh:
    """Tests for panel refresh functionality."""

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_refresh_updates_snapshot(self, mock_image, mock_label, mock_container, mock_header,
                                       mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Refresh should update the stored snapshot."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)

        new_snapshot = EmpireEconomySnapshot()
        new_snapshot.colony_production = {"metals": 999.0}
        panel.refresh(new_snapshot)

        assert panel.snapshot is new_snapshot

    @patch('game.ui.panels.empire_treasury_panel.create_section_header')
    @patch('game.ui.panels.empire_treasury_panel.UIScrollingContainer')
    @patch('game.ui.panels.empire_treasury_panel.UILabel')
    @patch('game.ui.panels.empire_treasury_panel.UIImage')
    def test_refresh_clears_old_elements(self, mock_image, mock_label, mock_container, mock_header,
                                          mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons):
        """Refresh should kill old UI elements."""
        panel = EmpireTreasuryPanel(mock_panel, mock_ui_manager, sample_snapshot, mock_resource_icons)

        # Store reference to old elements
        old_elements = list(panel._elements)
        old_container = panel._scroll_container

        new_snapshot = EmpireEconomySnapshot()
        panel.refresh(new_snapshot)

        # Old container should be killed
        old_container.kill.assert_called_once()

        # Old elements should be killed
        for elem in old_elements:
            elem.kill.assert_called()


