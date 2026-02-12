"""
Tests for ColumnManager - manages column configuration and ordering.

PROJ-44 Phase 7 Task 7.4: FleetReportWindow refactoring.
"""
import pytest


class TestColumnManager:
    """Test ColumnManager column configuration and visibility."""

    @pytest.fixture
    def manager(self):
        """Create ColumnManager instance with default columns."""
        from game.ui.screens.column_manager import ColumnManager
        return ColumnManager()

    @pytest.fixture
    def custom_columns(self):
        """Create custom column configuration."""
        return [
            {'id': 'col_a', 'width': 100, 'title': 'Column A', 'visible': True},
            {'id': 'col_b', 'width': 150, 'title': 'Column B', 'visible': True},
            {'id': 'col_c', 'width': 80, 'title': 'Column C', 'visible': False},
        ]

    def test_default_columns(self, manager):
        """Default columns are set for fleet report."""
        columns = manager.get_columns()
        assert len(columns) >= 5  # At least portrait, topdown, serial, design, name
        # Check required columns exist
        ids = [c['id'] for c in columns]
        assert 'serial' in ids
        assert 'name' in ids
        assert 'hp_pct' in ids

    def test_get_visible_columns(self, manager):
        """get_visible_columns returns only visible columns."""
        visible = manager.get_visible_columns()
        for col in visible:
            assert col.get('visible', True) is True

    def test_toggle_column_visibility(self, manager):
        """Toggle column visibility."""
        # Find a visible column
        columns = manager.get_visible_columns()
        col_id = columns[-1]['id']  # Use last visible column

        # Toggle off
        manager.toggle_column(col_id)
        col = manager.get_column(col_id)
        assert col['visible'] is False

        # Toggle on
        manager.toggle_column(col_id)
        col = manager.get_column(col_id)
        assert col['visible'] is True

    def test_get_column_by_id(self, manager):
        """Get column by ID."""
        col = manager.get_column('serial')
        assert col is not None
        assert col['id'] == 'serial'
        assert 'width' in col
        assert 'title' in col

    def test_get_column_not_found(self, manager):
        """Get column returns None for unknown ID."""
        col = manager.get_column('nonexistent')
        assert col is None

    def test_swap_columns(self, manager):
        """Swap adjacent columns."""
        columns = manager.get_columns()
        first_id = columns[0]['id']
        second_id = columns[1]['id']

        # Swap first with second (direction=1)
        manager.swap_column(columns[0], 1)

        columns = manager.get_columns()
        assert columns[0]['id'] == second_id
        assert columns[1]['id'] == first_id

    def test_swap_column_left(self, manager):
        """Swap column left."""
        columns = manager.get_columns()
        first_id = columns[0]['id']
        second_id = columns[1]['id']

        # Swap second with first (direction=-1)
        manager.swap_column(columns[1], -1)

        columns = manager.get_columns()
        assert columns[0]['id'] == second_id
        assert columns[1]['id'] == first_id

    def test_swap_column_boundary_no_change(self, manager):
        """Swap at boundary does nothing."""
        columns = manager.get_columns()
        first_id = columns[0]['id']

        # Try to swap first column left (invalid)
        manager.swap_column(columns[0], -1)

        columns = manager.get_columns()
        assert columns[0]['id'] == first_id  # Unchanged

    def test_get_total_visible_width(self, manager):
        """Get total width of visible columns."""
        width = manager.get_total_visible_width()
        assert width > 0

        # Should match sum of visible column widths
        expected = sum(c['width'] for c in manager.get_visible_columns())
        assert width == expected

    def test_custom_columns_init(self, custom_columns):
        """Initialize with custom columns."""
        from game.ui.screens.column_manager import ColumnManager
        mgr = ColumnManager(custom_columns)

        columns = mgr.get_columns()
        assert len(columns) == 3
        assert columns[0]['id'] == 'col_a'

    def test_image_columns_always_visible(self, manager):
        """Image columns don't appear in visibility toggles."""
        toggleable = manager.get_toggleable_columns()
        for col in toggleable:
            assert col.get('type') != 'image'

    def test_get_column_value_serial(self):
        """Get display value for serial column."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.get_display_id = Mock(return_value="SN-0001")
        ship.instance_id = "abc123"

        col = mgr.get_column('serial')
        value = mgr.get_column_value(ship, col)
        assert value == "SN-0001"

    def test_get_column_value_hp_pct(self):
        """Get display value for HP percentage column."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.get_hp_percentage = Mock(return_value=0.75)

        col = mgr.get_column('hp_pct')
        value = mgr.get_column_value(ship, col)
        assert value == "75%"

    def test_get_column_value_status_ok(self):
        """Get status column value for healthy ship."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.is_damaged = Mock(return_value=False)

        col = mgr.get_column('status')
        value = mgr.get_column_value(ship, col)
        assert value == "OK"

    def test_get_column_value_status_destroyed(self):
        """Get status column value for destroyed ship."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.is_alive = False

        col = mgr.get_column('status')
        value = mgr.get_column_value(ship, col)
        assert value == "DESTROYED"

    def test_get_column_value_status_derelict(self):
        """Get status column value for derelict ship."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.is_alive = True
        ship.is_derelict = True

        col = mgr.get_column('status')
        value = mgr.get_column_value(ship, col)
        assert value == "DERELICT"

    def test_get_column_value_status_damaged(self):
        """Get status column value for damaged ship."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.is_damaged = Mock(return_value=True)

        col = mgr.get_column('status')
        value = mgr.get_column_value(ship, col)
        assert value == "DAMAGED"


class TestNewColumns:
    """Tests for new columns added in PROJ-101 Phase 2."""

    def test_new_columns_exist_in_defaults(self):
        """All 7 new columns exist in DEFAULT_FLEET_COLUMNS."""
        from game.ui.screens.column_manager import DEFAULT_FLEET_COLUMNS

        new_column_ids = ['speed', 'tonnage', 'warp', 'spaceyard', 'transport', 'resources', 'cargo']
        existing_ids = [c['id'] for c in DEFAULT_FLEET_COLUMNS]

        for col_id in new_column_ids:
            assert col_id in existing_ids, f"Column {col_id} not found in defaults"

    def test_new_columns_hidden_by_default(self):
        """All 7 new columns are hidden by default."""
        from game.ui.screens.column_manager import DEFAULT_FLEET_COLUMNS

        new_column_ids = ['speed', 'tonnage', 'warp', 'spaceyard', 'transport', 'resources', 'cargo']

        for col in DEFAULT_FLEET_COLUMNS:
            if col['id'] in new_column_ids:
                assert col.get('visible') is False, f"Column {col['id']} should be hidden by default"

    def test_new_columns_have_required_properties(self):
        """New columns have id, width, title, and visible properties."""
        from game.ui.screens.column_manager import DEFAULT_FLEET_COLUMNS

        new_column_ids = ['speed', 'tonnage', 'warp', 'spaceyard', 'transport', 'resources', 'cargo']

        for col in DEFAULT_FLEET_COLUMNS:
            if col['id'] in new_column_ids:
                assert 'width' in col, f"Column {col['id']} missing width"
                assert 'title' in col, f"Column {col['id']} missing title"
                assert 'visible' in col, f"Column {col['id']} missing visible"
                assert col['width'] > 0, f"Column {col['id']} has invalid width"


class TestNewColumnValues:
    """Tests for new column value extraction in PROJ-101 Phase 2."""

    def test_get_column_value_speed(self):
        """Get speed column value."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock, patch

        mgr = ColumnManager()
        ship = Mock()

        with patch('game.strategy.services.fleet_speed_calculator.FleetSpeedCalculator.calculate_ship_speed', return_value=5):
            col = mgr.get_column('speed')
            value = mgr.get_column_value(ship, col)
            assert value == "5"

    def test_get_column_value_tonnage(self):
        """Get tonnage column value with comma formatting."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.get_calculated_stats = Mock(return_value={'mass': 12500})

        col = mgr.get_column('tonnage')
        value = mgr.get_column_value(ship, col)
        assert value == "12,500"

    def test_get_column_value_tonnage_zero(self):
        """Get tonnage column value when mass is zero."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.get_calculated_stats = Mock(return_value={'mass': 0})

        col = mgr.get_column('tonnage')
        value = mgr.get_column_value(ship, col)
        assert value == "0"

    def test_get_column_value_warp_yes(self):
        """Get warp column value when ship has warp capability."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock, patch

        mgr = ColumnManager()
        ship = Mock()

        with patch('game.strategy.services.ship_stats_calculator.ShipStatsCalculator.has_warp_capability', return_value=True):
            col = mgr.get_column('warp')
            value = mgr.get_column_value(ship, col)
            assert value == "Yes"

    def test_get_column_value_warp_no(self):
        """Get warp column value when ship has no warp capability."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock, patch

        mgr = ColumnManager()
        ship = Mock()

        with patch('game.strategy.services.ship_stats_calculator.ShipStatsCalculator.has_warp_capability', return_value=False):
            col = mgr.get_column('warp')
            value = mgr.get_column_value(ship, col)
            assert value == "No"

    def test_get_column_value_spaceyard_yes(self):
        """Get spaceyard column value when ship has spaceyard."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock, patch

        mgr = ColumnManager()
        ship = Mock()

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator.ship_has_spaceyard', return_value=True):
            col = mgr.get_column('spaceyard')
            value = mgr.get_column_value(ship, col)
            assert value == "Yes"

    def test_get_column_value_spaceyard_no(self):
        """Get spaceyard column value when ship has no spaceyard."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock, patch

        mgr = ColumnManager()
        ship = Mock()

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator.ship_has_spaceyard', return_value=False):
            col = mgr.get_column('spaceyard')
            value = mgr.get_column_value(ship, col)
            assert value == "No"

    def test_get_column_value_transport_yes(self):
        """Get transport column value when ship has passenger capacity."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.get_calculated_stats = Mock(return_value={'cargo_storage': {'passengers': 100}})

        col = mgr.get_column('transport')
        value = mgr.get_column_value(ship, col)
        assert value == "Yes"

    def test_get_column_value_transport_no(self):
        """Get transport column value when ship has no passenger capacity."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.get_calculated_stats = Mock(return_value={'cargo_storage': {}})

        col = mgr.get_column('transport')
        value = mgr.get_column_value(ship, col)
        assert value == "No"

    def test_get_column_value_resources_with_values(self):
        """Get resources column value with resource percentages."""
        from game.ui.screens.column_manager import ColumnManager
        from game.core.constants import ResourceType
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()

        def mock_get_resource_pct(res_type):
            if res_type == ResourceType.ENERGY:
                return 0.8
            elif res_type == ResourceType.FUEL:
                return 0.9
            elif res_type == ResourceType.AMMO:
                return 1.0
            return None

        ship.get_resource_percentage = mock_get_resource_pct

        col = mgr.get_column('resources')
        value = mgr.get_column_value(ship, col)
        assert "E:80" in value
        assert "F:90" in value
        assert "A:100" in value

    def test_get_column_value_resources_empty(self):
        """Get resources column value when ship has no resources."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.get_resource_percentage = Mock(return_value=None)

        col = mgr.get_column('resources')
        value = mgr.get_column_value(ship, col)
        assert value == "--"

    def test_get_column_value_cargo_with_contents(self):
        """Get cargo column value when ship has cargo."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.cargo_contents = {'minerals': 50, 'food': 30}

        col = mgr.get_column('cargo')
        value = mgr.get_column_value(ship, col)
        assert value == "80"

    def test_get_column_value_cargo_empty(self):
        """Get cargo column value when ship has no cargo."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.cargo_contents = {}

        col = mgr.get_column('cargo')
        value = mgr.get_column_value(ship, col)
        assert value == "--"

    def test_get_column_value_cargo_none(self):
        """Get cargo column value when cargo_contents is None."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock

        mgr = ColumnManager()
        ship = Mock()
        ship.cargo_contents = None

        col = mgr.get_column('cargo')
        value = mgr.get_column_value(ship, col)
        assert value == "--"


class TestSpecialCapabilityColumns:
    """Tests for special capability columns (BUG-83)."""

    def test_special_capability_columns_exist_in_defaults(self):
        """All 5 special capability columns exist in DEFAULT_FLEET_COLUMNS."""
        from game.ui.screens.column_manager import DEFAULT_FLEET_COLUMNS

        expected_ids = ['can_destroy_planet', 'can_open_warp', 'can_close_warp',
                        'can_destroy_star', 'can_create_sphere']
        existing_ids = [c['id'] for c in DEFAULT_FLEET_COLUMNS]

        for col_id in expected_ids:
            assert col_id in existing_ids, f"Column {col_id} not found in defaults"

    def test_special_capability_columns_hidden_by_default(self):
        """All 5 special capability columns are hidden by default."""
        from game.ui.screens.column_manager import DEFAULT_FLEET_COLUMNS

        special_ids = ['can_destroy_planet', 'can_open_warp', 'can_close_warp',
                       'can_destroy_star', 'can_create_sphere']

        for col in DEFAULT_FLEET_COLUMNS:
            if col['id'] in special_ids:
                assert col.get('visible') is False, f"Column {col['id']} should be hidden"

    def test_special_capability_mapping_complete(self):
        """SPECIAL_CAPABILITY_COLUMNS maps all 5 columns to ability names."""
        from game.ui.screens.column_manager import SPECIAL_CAPABILITY_COLUMNS

        assert 'can_destroy_planet' in SPECIAL_CAPABILITY_COLUMNS
        assert SPECIAL_CAPABILITY_COLUMNS['can_destroy_planet'] == 'DestroyPlanet'
        assert SPECIAL_CAPABILITY_COLUMNS['can_open_warp'] == 'OpenWarpPoint'
        assert SPECIAL_CAPABILITY_COLUMNS['can_close_warp'] == 'CloseWarpPoint'
        assert SPECIAL_CAPABILITY_COLUMNS['can_destroy_star'] == 'DestroyStar'
        assert SPECIAL_CAPABILITY_COLUMNS['can_create_sphere'] == 'CreateSphereWorld'

    def test_get_column_value_destroy_planet_yes(self):
        """Ship with DestroyPlanet ability shows 'Yes'."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock, patch

        mgr = ColumnManager()
        ship = Mock()

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator._ship_has_ability',
                   return_value=True):
            col = mgr.get_column('can_destroy_planet')
            value = mgr.get_column_value(ship, col)
            assert value == "Yes"

    def test_get_column_value_destroy_planet_no(self):
        """Ship without DestroyPlanet ability shows 'No'."""
        from game.ui.screens.column_manager import ColumnManager
        from unittest.mock import Mock, patch

        mgr = ColumnManager()
        ship = Mock()

        with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator._ship_has_ability',
                   return_value=False):
            col = mgr.get_column('can_destroy_planet')
            value = mgr.get_column_value(ship, col)
            assert value == "No"

    def test_get_column_value_all_special_columns(self):
        """All 5 special columns return 'Yes'/'No' based on ability check."""
        from game.ui.screens.column_manager import ColumnManager, SPECIAL_CAPABILITY_COLUMNS
        from unittest.mock import Mock, patch

        mgr = ColumnManager()
        ship = Mock()

        for col_id in SPECIAL_CAPABILITY_COLUMNS:
            with patch('game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator._ship_has_ability',
                       return_value=True):
                col = mgr.get_column(col_id)
                assert col is not None, f"Column {col_id} not found"
                value = mgr.get_column_value(ship, col)
                assert value == "Yes", f"Column {col_id} should return 'Yes'"
