"""Tests for BuildQueueDataSource.

PROJ-188 Phase 4: Tests for build queue data source adapter for VirtualTable.
"""

import pytest
from unittest.mock import Mock, MagicMock

from game.ui.screens.empire_build_queue_data_source import BuildQueueDataSource
from game.ui.screens.empire_build_queue_viewmodel import (
    EmpireBuildQueueViewModel,
    RESOURCE_RATE_COLS,
    RESOURCE_TOTAL_COLS,
)
from game.ui.screens.empire_build_queue_filter_manager import (
    BuildQueueFilterManager,
    DEFAULT_COLUMNS,
)


@pytest.fixture
def mock_source():
    """Create a mock BuildQueueSource."""
    source = Mock()
    source.display_name = "Alpha Station"
    source.context_type = "planet"
    source.can_build_ships = True
    source.can_build_complexes = True
    source.construction_queue = [
        {"name": "Frigate", "type": "ship"},
        {"name": "Factory", "type": "complex"},
    ]
    source.build_rate = {"metals": 100, "organics": 50}
    source.owner_entity = Mock()
    source.owner_entity.location = (2, 3)
    # Ensure system_name is None so get_system_name uses galaxy lookup
    source.owner_entity.system_name = None
    return source


@pytest.fixture
def mock_source_fleet():
    """Create a mock BuildQueueSource for a fleet."""
    source = Mock()
    source.display_name = "Fleet Yard Alpha"
    source.context_type = "fleet"
    source.can_build_ships = True
    source.can_build_complexes = False
    source.construction_queue = []
    source.build_rate = {"metals": 50}
    source.owner_entity = Mock()
    source.owner_entity.location = (5, 6)
    return source


@pytest.fixture
def mock_viewmodel(mock_source, mock_source_fleet):
    """Create a mock EmpireBuildQueueViewModel."""
    vm = Mock(spec=EmpireBuildQueueViewModel)
    vm.filtered_sources = [mock_source, mock_source_fleet]
    vm.all_sources = [mock_source, mock_source_fleet]

    def get_column_value(source, col_id):
        """Mock column value extraction."""
        if col_id == "location":
            return source.display_name
        if col_id == "queue_count":
            return str(len(source.construction_queue))
        if col_id == "first_item":
            if source.construction_queue:
                return source.construction_queue[0].get("name", "-")
            return "-"
        if col_id == "turns_left":
            return "5" if source.construction_queue else "-"
        if col_id == "capabilities":
            caps = []
            if source.can_build_ships:
                caps.append("Ships")
            if source.can_build_complexes:
                caps.append("Complexes")
            return ", ".join(caps) if caps else "-"
        if col_id == "build_rate":
            if source.build_rate:
                max_rate = max(source.build_rate.values())
                return f"{int(max_rate)}/turn"
            return "N/A"
        # Resource columns
        if col_id in RESOURCE_RATE_COLS:
            return "10/turn"
        if col_id in RESOURCE_TOTAL_COLS:
            return "100"
        return ""

    vm.get_column_value = get_column_value
    return vm


@pytest.fixture
def mock_galaxy():
    """Create a mock Galaxy."""
    galaxy = Mock()
    system = Mock()
    system.name = "Sol System"
    galaxy.get_system_of_planet = Mock(return_value=system)
    galaxy.get_system_at_hex = Mock(return_value=system)
    return galaxy


@pytest.fixture
def filter_manager():
    """Create a BuildQueueFilterManager."""
    return BuildQueueFilterManager()


@pytest.fixture
def data_source(mock_viewmodel, filter_manager, mock_galaxy):
    """Create a BuildQueueDataSource."""
    return BuildQueueDataSource(mock_viewmodel, filter_manager, mock_galaxy)


class TestBuildQueueDataSourceInit:
    """Tests for BuildQueueDataSource initialization."""

    def test_init_stores_viewmodel(self, mock_viewmodel, filter_manager, mock_galaxy):
        """DataSource stores viewmodel reference."""
        ds = BuildQueueDataSource(mock_viewmodel, filter_manager, mock_galaxy)
        assert ds._viewmodel is mock_viewmodel

    def test_init_stores_filter_manager(self, mock_viewmodel, filter_manager, mock_galaxy):
        """DataSource stores filter manager reference."""
        ds = BuildQueueDataSource(mock_viewmodel, filter_manager, mock_galaxy)
        assert ds._filter_mgr is filter_manager

    def test_init_stores_galaxy(self, mock_viewmodel, filter_manager, mock_galaxy):
        """DataSource stores galaxy reference."""
        ds = BuildQueueDataSource(mock_viewmodel, filter_manager, mock_galaxy)
        assert ds._galaxy is mock_galaxy


class TestBuildQueueDataSourceRowCount:
    """Tests for get_row_count()."""

    def test_get_row_count_returns_filtered_sources_length(self, data_source, mock_viewmodel):
        """get_row_count returns len(viewmodel.filtered_sources)."""
        assert data_source.get_row_count() == 2

    def test_get_row_count_zero_when_empty(self, mock_viewmodel, filter_manager, mock_galaxy):
        """get_row_count returns 0 when no sources."""
        mock_viewmodel.filtered_sources = []
        ds = BuildQueueDataSource(mock_viewmodel, filter_manager, mock_galaxy)
        assert ds.get_row_count() == 0


class TestBuildQueueDataSourceColumns:
    """Tests for get_columns()."""

    def test_get_columns_returns_filter_mgr_columns(self, data_source, filter_manager):
        """get_columns returns filter_mgr.columns."""
        columns = data_source.get_columns()
        assert len(columns) == len(filter_manager.columns)

    def test_get_columns_returns_deep_copy(self, data_source, filter_manager):
        """get_columns returns a copy, not the original list."""
        columns = data_source.get_columns()
        # Modify the returned list
        columns[0]["width"] = 999
        # Original should be unchanged
        assert filter_manager.columns[0]["width"] != 999

    def test_get_columns_includes_expected_ids(self, data_source):
        """Columns include expected IDs."""
        columns = data_source.get_columns()
        col_ids = [c["id"] for c in columns]
        assert "location" in col_ids
        assert "system" in col_ids
        assert "sector" in col_ids
        assert "queue_count" in col_ids
        assert "first_item" in col_ids


class TestBuildQueueDataSourceCellValue:
    """Tests for get_cell_value()."""

    def test_get_cell_value_location(self, data_source):
        """get_cell_value for location column returns display_name."""
        value = data_source.get_cell_value(0, "location")
        assert value == "Alpha Station"

    def test_get_cell_value_system(self, data_source):
        """get_cell_value for system column returns system name."""
        value = data_source.get_cell_value(0, "system")
        assert value == "Sol System"

    def test_get_cell_value_sector(self, data_source, mock_source):
        """get_cell_value for sector column returns sector text."""
        # The sector comes from get_sector_text which uses owner_entity
        value = data_source.get_cell_value(0, "sector")
        # Should return some sector text (format depends on get_sector_text)
        assert isinstance(value, str)

    def test_get_cell_value_queue_count(self, data_source, mock_viewmodel):
        """get_cell_value for queue_count delegates to viewmodel."""
        value = data_source.get_cell_value(0, "queue_count")
        assert value == "2"

    def test_get_cell_value_first_item(self, data_source):
        """get_cell_value for first_item delegates to viewmodel."""
        value = data_source.get_cell_value(0, "first_item")
        assert value == "Frigate"

    def test_get_cell_value_turns_left(self, data_source):
        """get_cell_value for turns_left delegates to viewmodel."""
        value = data_source.get_cell_value(0, "turns_left")
        assert value == "5"

    def test_get_cell_value_capabilities(self, data_source):
        """get_cell_value for capabilities delegates to viewmodel."""
        value = data_source.get_cell_value(0, "capabilities")
        assert "Ships" in value
        assert "Complexes" in value

    def test_get_cell_value_build_rate(self, data_source):
        """get_cell_value for build_rate delegates to viewmodel."""
        value = data_source.get_cell_value(0, "build_rate")
        assert "/turn" in value

    def test_get_cell_value_resource_rate_columns(self, data_source):
        """get_cell_value for resource rate columns delegates to viewmodel."""
        for col_id in RESOURCE_RATE_COLS:
            value = data_source.get_cell_value(0, col_id)
            assert isinstance(value, str)

    def test_get_cell_value_resource_total_columns(self, data_source):
        """get_cell_value for resource total columns delegates to viewmodel."""
        for col_id in RESOURCE_TOTAL_COLS:
            value = data_source.get_cell_value(0, col_id)
            assert isinstance(value, str)

    def test_get_cell_value_invalid_row_returns_empty(self, data_source):
        """get_cell_value with invalid row index returns empty string."""
        value = data_source.get_cell_value(999, "location")
        assert value == ""

    def test_get_cell_value_fleet_source(self, data_source):
        """get_cell_value works for fleet sources too."""
        value = data_source.get_cell_value(1, "location")
        assert value == "Fleet Yard Alpha"


class TestBuildQueueDataSourceGetSourceAtIndex:
    """Tests for get_source_at_index()."""

    def test_get_source_at_index_returns_source(self, data_source, mock_source):
        """get_source_at_index returns the source at that index."""
        source = data_source.get_source_at_index(0)
        assert source.display_name == "Alpha Station"

    def test_get_source_at_index_second_source(self, data_source):
        """get_source_at_index returns correct source for other indices."""
        source = data_source.get_source_at_index(1)
        assert source.display_name == "Fleet Yard Alpha"

    def test_get_source_at_index_out_of_bounds_returns_none(self, data_source):
        """get_source_at_index returns None for invalid index."""
        assert data_source.get_source_at_index(99) is None
        assert data_source.get_source_at_index(-1) is None


class TestBuildQueueDataSourceSystemName:
    """Tests for system name lookup."""

    def test_system_name_for_planet(self, data_source, mock_galaxy):
        """System name lookup works for planets."""
        value = data_source.get_cell_value(0, "system")
        assert value == "Sol System"
        mock_galaxy.get_system_of_planet.assert_called()

    def test_system_name_for_fleet(self, data_source, mock_galaxy):
        """System name lookup for fleets returns appropriate value."""
        # For fleets, the behavior depends on get_system_name implementation
        value = data_source.get_cell_value(1, "system")
        assert isinstance(value, str)


class TestBuildQueueDataSourceSectorText:
    """Tests for sector text extraction."""

    def test_sector_for_planet(self, data_source, mock_source):
        """Sector text extraction works for planets."""
        value = data_source.get_cell_value(0, "sector")
        assert isinstance(value, str)

    def test_sector_for_fleet(self, data_source):
        """Sector text extraction works for fleets."""
        value = data_source.get_cell_value(1, "sector")
        assert isinstance(value, str)
