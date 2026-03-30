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
    RESOURCE_ABBREVIATIONS,
    LABEL_COL_WIDTH,
    RESOURCE_COL_WIDTH,
    ICON_SIZE,
    ROW_HEIGHT,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_snapshot():
    """Create a sample EmpireEconomySnapshot with test data."""
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
    snapshot.maintenance_expenses = {
        "metals": 10.0, "organics": 5.0, "vapors": 2.0,
        "radioactives": 1.0, "exotics": 0.5
    }
    snapshot.construction_expenses_ships = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.construction_expenses_complexes = {r: 0.0 for r in PLANET_RESOURCE_NAMES}
    snapshot.total_expenses = snapshot.maintenance_expenses.copy()

    # Treasury
    snapshot.net_resources = {
        "metals": 90.0, "organics": 195.0, "vapors": 48.0,
        "radioactives": 24.0, "exotics": 9.5
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
def mock_ui_manager():
    """Create a mock pygame_gui UIManager."""
    return MagicMock()


@pytest.fixture
def mock_panel():
    """Create a mock UIPanel with realistic dimensions."""
    panel = MagicMock()
    panel.get_relative_rect.return_value = MagicMock(width=800, height=600)
    return panel


@pytest.fixture
def mock_resource_icons():
    """Create mock resource icons dict."""
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

        assert len(rows) == 5  # 4 categories + total
        assert rows[0][0] == "Tributes"
        assert rows[1][0] == "Maintenance Costs"
        assert rows[2][0] == "Construction Queues (Ships)"
        assert rows[3][0] == "Construction Queues (Complexes)"
        assert rows[4][0] == "Total"
        assert rows[4][2] is True

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


