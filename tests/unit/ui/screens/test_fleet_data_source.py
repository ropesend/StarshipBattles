"""Tests for FleetDataSource - Provides fleet data for VirtualTable.

PROJ-188 Phase 2: FleetDataSource value extraction tests.
"""

import pytest
from unittest.mock import Mock, patch

import pygame


class TestFleetDataSourceColumns:
    """Test FleetDataSource column configuration."""

    def test_get_columns_returns_19_columns(self):
        """get_columns returns all 19 fleet columns."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[])
        ds = FleetDataSource(view_model)

        columns = ds.get_columns()
        assert len(columns) == 19

    def test_get_columns_includes_required_ids(self):
        """get_columns includes all required column ids."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[])
        ds = FleetDataSource(view_model)

        columns = ds.get_columns()
        col_ids = [c["id"] for c in columns]

        # Core columns
        assert "portrait" in col_ids
        assert "topdown" in col_ids
        assert "serial" in col_ids
        assert "design" in col_ids
        assert "name" in col_ids
        assert "hp_pct" in col_ids
        assert "status" in col_ids

        # Extra columns
        assert "speed" in col_ids
        assert "tonnage" in col_ids
        assert "warp" in col_ids
        assert "spaceyard" in col_ids
        assert "transport" in col_ids
        assert "resources" in col_ids
        assert "cargo" in col_ids

        # Special capability columns
        assert "can_destroy_planet" in col_ids
        assert "can_open_warp" in col_ids
        assert "can_close_warp" in col_ids
        assert "can_destroy_star" in col_ids
        assert "can_create_sphere" in col_ids

    def test_columns_have_required_properties(self):
        """Each column has id, width, title, visible."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[])
        ds = FleetDataSource(view_model)

        for col in ds.get_columns():
            assert "id" in col
            assert "width" in col
            assert "title" in col
            assert "visible" in col


class TestFleetDataSourceRowCount:
    """Test FleetDataSource row count."""

    def test_get_row_count_delegates_to_view_model(self):
        """get_row_count returns len of filtered ships."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[Mock(), Mock(), Mock()])
        ds = FleetDataSource(view_model)

        assert ds.get_row_count() == 3

    def test_get_row_count_empty(self):
        """get_row_count returns 0 when no ships."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[])
        ds = FleetDataSource(view_model)

        assert ds.get_row_count() == 0


class TestFleetDataSourceCellValueSerial:
    """Test FleetDataSource serial column value extraction."""

    def test_serial_returns_display_id(self):
        """Serial column returns ship.get_display_id()."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.get_display_id = Mock(return_value="SN-0001")
        ship.instance_id = "abc123"

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "serial") == "SN-0001"

    def test_serial_fallback_to_instance_id(self):
        """Serial column falls back to instance_id[:8] if no display_id."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.get_display_id = Mock(return_value=None)
        ship.instance_id = "abc123456789"

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "serial") == "abc12345"


class TestFleetDataSourceCellValueDesign:
    """Test FleetDataSource design column."""

    def test_design_returns_name_from_design_data(self):
        """Design column returns design name."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.design_data = {"name": "Cruiser Mk II"}
        ship.design_id = "cruiser_2"

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "design") == "Cruiser Mk II"

    def test_design_fallback_to_design_id(self):
        """Design column falls back to design_id."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.design_data = {}
        ship.design_id = "cruiser_2"

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "design") == "cruiser_2"


class TestFleetDataSourceCellValueName:
    """Test FleetDataSource name column."""

    def test_name_returns_ship_name(self):
        """Name column returns ship.name."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.name = "USS Enterprise"

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "name") == "USS Enterprise"


class TestFleetDataSourceCellValueHpPct:
    """Test FleetDataSource HP percentage column."""

    def test_hp_pct_formats_percentage(self):
        """HP% column returns formatted percentage."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.get_hp_percentage = Mock(return_value=0.75)

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "hp_pct") == "75%"

    def test_hp_pct_full_health(self):
        """HP% column shows 100% for full health."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.get_hp_percentage = Mock(return_value=1.0)

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "hp_pct") == "100%"


class TestFleetDataSourceCellValueStatus:
    """Test FleetDataSource status column."""

    def test_status_ok(self):
        """Status column returns OK for healthy ship."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.is_damaged = Mock(return_value=False)

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "status") == "OK"

    def test_status_destroyed(self):
        """Status column returns DESTROYED for dead ship."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.is_alive = False

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "status") == "DESTROYED"

    def test_status_derelict(self):
        """Status column returns DERELICT for derelict ship."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.is_alive = True
        ship.is_derelict = True

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "status") == "DERELICT"

    def test_status_damaged(self):
        """Status column returns DAMAGED for damaged ship."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.is_alive = True
        ship.is_derelict = False
        ship.is_damaged = Mock(return_value=True)

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "status") == "DAMAGED"


class TestFleetDataSourceCellValueSpeed:
    """Test FleetDataSource speed column."""

    def test_speed_uses_calculator(self):
        """Speed column uses FleetSpeedCalculator."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        with patch(
            "game.strategy.services.fleet_speed_calculator.FleetSpeedCalculator.calculate_ship_speed",
            return_value=5,
        ):
            assert ds.get_cell_value(0, "speed") == "5"


class TestFleetDataSourceCellValueTonnage:
    """Test FleetDataSource tonnage column."""

    def test_tonnage_formats_with_comma(self):
        """Tonnage column formats mass with comma separator."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.get_calculated_stats = Mock(return_value={"mass": 12500})

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "tonnage") == "12,500"

    def test_tonnage_zero(self):
        """Tonnage column handles zero mass."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.get_calculated_stats = Mock(return_value={"mass": 0})

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "tonnage") == "0"


class TestFleetDataSourceCellValueWarp:
    """Test FleetDataSource warp column."""

    def test_warp_yes(self):
        """Warp column returns Yes when ship has warp."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        with patch(
            "game.strategy.services.component_inspector.has_warp_capability",
            return_value=True,
        ):
            assert ds.get_cell_value(0, "warp") == "Yes"

    def test_warp_no(self):
        """Warp column returns No when ship has no warp."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        with patch(
            "game.strategy.services.component_inspector.has_warp_capability",
            return_value=False,
        ):
            assert ds.get_cell_value(0, "warp") == "No"


class TestFleetDataSourceCellValueSpaceyard:
    """Test FleetDataSource spaceyard column."""

    def test_spaceyard_yes(self):
        """Spaceyard column returns Yes when ship has spaceyard."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        with patch(
            "game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator.ship_has_spaceyard",
            return_value=True,
        ):
            assert ds.get_cell_value(0, "spaceyard") == "Yes"

    def test_spaceyard_no(self):
        """Spaceyard column returns No when ship has no spaceyard."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        with patch(
            "game.strategy.data.fleet_capability_calculator.FleetCapabilityCalculator.ship_has_spaceyard",
            return_value=False,
        ):
            assert ds.get_cell_value(0, "spaceyard") == "No"


class TestFleetDataSourceCellValueTransport:
    """Test FleetDataSource transport column."""

    def test_transport_with_capacity(self):
        """Transport column returns current/capacity."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.get_cargo_capacity = Mock(return_value=100)
        ship.get_current_cargo = Mock(return_value=50)

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "transport") == "50/100"

    def test_transport_no_capacity(self):
        """Transport column returns -- when no capacity."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.get_cargo_capacity = Mock(return_value=0)
        ship.get_current_cargo = Mock(return_value=0)

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "transport") == "--"


class TestFleetDataSourceCellValueResources:
    """Test FleetDataSource resources column."""

    def test_resources_with_values(self):
        """Resources column shows E:xx F:xx A:xx format."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()

        def mock_get_resource_pct(res_type):
            if res_type == "energy":
                return 0.8
            elif res_type == "fuel":
                return 0.9
            elif res_type == "ammo":
                return 1.0
            return None

        ship.get_resource_percentage = mock_get_resource_pct

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        value = ds.get_cell_value(0, "resources")
        assert "E:80" in value
        assert "F:90" in value
        assert "A:100" in value

    def test_resources_empty(self):
        """Resources column returns -- when no resources."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.get_resource_percentage = Mock(return_value=None)

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "resources") == "--"


class TestFleetDataSourceCellValueCargo:
    """Test FleetDataSource cargo column."""

    def test_cargo_with_contents(self):
        """Cargo column returns total cargo."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.cargo_contents = {"minerals": 50, "food": 30}

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "cargo") == "80"

    def test_cargo_empty(self):
        """Cargo column returns -- when empty."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.cargo_contents = {}

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "cargo") == "--"

    def test_cargo_none(self):
        """Cargo column returns -- when cargo_contents is None."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.cargo_contents = None

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "cargo") == "--"


class TestFleetDataSourceCellValueSpecialCapabilities:
    """Test FleetDataSource special capability columns."""

    def test_destroy_planet_yes(self):
        """DestroyPlanet column returns Yes."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        with patch(
            "game.strategy.services.component_inspector.ship_has_ability",
            return_value=True,
        ):
            assert ds.get_cell_value(0, "can_destroy_planet") == "Yes"

    def test_destroy_planet_no(self):
        """DestroyPlanet column returns No."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        with patch(
            "game.strategy.services.component_inspector.ship_has_ability",
            return_value=False,
        ):
            assert ds.get_cell_value(0, "can_destroy_planet") == "No"

    def test_all_special_columns(self):
        """All 5 special capability columns return Yes/No."""
        from game.ui.screens.fleet_data_source import (
            FleetDataSource,
            SPECIAL_CAPABILITY_COLUMNS,
        )

        ship = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        for col_id in SPECIAL_CAPABILITY_COLUMNS:
            with patch(
                "game.strategy.services.component_inspector.ship_has_ability",
                return_value=True,
            ):
                assert ds.get_cell_value(0, col_id) == "Yes"


class TestFleetDataSourceCellValueImageColumns:
    """Test FleetDataSource image column handling."""

    def test_portrait_returns_empty_string(self):
        """Portrait column returns empty string for text value."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "portrait") == ""

    def test_topdown_returns_empty_string(self):
        """Topdown column returns empty string for text value."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_value(0, "topdown") == ""


class TestFleetDataSourceGetCellImage:
    """Test FleetDataSource get_cell_image for image columns."""

    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        """Initialize pygame for surface tests."""
        pygame.init()
        yield
        pygame.quit()

    def test_get_cell_image_portrait(self):
        """get_cell_image returns surface for portrait column."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.instance_id = "ship123"
        ship.design_data = {"theme_id": "Federation", "ship_class": "Cruiser"}

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        # Mock the theme manager
        mock_surface = pygame.Surface((40, 40))
        with patch(
            "game.ui.assets.ShipThemeManager.instance"
        ) as mock_theme_mgr_cls:
            mock_theme_mgr = Mock()
            mock_theme_mgr.get_portrait_image = Mock(return_value=mock_surface)
            mock_theme_mgr_cls.return_value = mock_theme_mgr

            result = ds.get_cell_image(0, "portrait")

            # Should return a surface (potentially scaled)
            assert result is not None
            assert isinstance(result, pygame.Surface)

    def test_get_cell_image_topdown(self):
        """get_cell_image returns surface for topdown column."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.instance_id = "ship123"
        ship.design_data = {"theme_id": "Federation", "ship_class": "Cruiser"}

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        mock_surface = pygame.Surface((60, 60))
        with patch(
            "game.ui.assets.ShipThemeManager.instance"
        ) as mock_theme_mgr_cls:
            mock_theme_mgr = Mock()
            mock_theme_mgr.load_image = Mock(return_value=mock_surface)
            mock_theme_mgr_cls.return_value = mock_theme_mgr

            result = ds.get_cell_image(0, "topdown")

            assert result is not None
            assert isinstance(result, pygame.Surface)

    def test_get_cell_image_non_image_column_returns_none(self):
        """get_cell_image returns None for non-image columns."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        assert ds.get_cell_image(0, "serial") is None
        assert ds.get_cell_image(0, "name") is None

    def test_get_cell_image_caches_results(self):
        """get_cell_image caches image results."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship = Mock()
        ship.instance_id = "ship123"
        ship.design_data = {"theme_id": "Federation", "ship_class": "Cruiser"}

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship])
        ds = FleetDataSource(view_model)

        mock_surface = pygame.Surface((40, 40))
        with patch(
            "game.ui.assets.ShipThemeManager.instance"
        ) as mock_theme_mgr_cls:
            mock_theme_mgr = Mock()
            mock_theme_mgr.get_portrait_image = Mock(return_value=mock_surface)
            mock_theme_mgr_cls.return_value = mock_theme_mgr

            # First call
            result1 = ds.get_cell_image(0, "portrait")
            # Second call
            result2 = ds.get_cell_image(0, "portrait")

            # Should return same cached result
            assert result1 is result2
            # Theme manager should only be called once
            assert mock_theme_mgr.get_portrait_image.call_count == 1


class TestFleetDataSourceGetShipAtIndex:
    """Test FleetDataSource get_ship_at_index helper."""

    def test_get_ship_at_index_valid(self):
        """get_ship_at_index returns ship at index."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        ship1 = Mock()
        ship2 = Mock()
        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[ship1, ship2])
        ds = FleetDataSource(view_model)

        assert ds.get_ship_at_index(0) is ship1
        assert ds.get_ship_at_index(1) is ship2

    def test_get_ship_at_index_out_of_bounds(self):
        """get_ship_at_index returns None for invalid index."""
        from game.ui.screens.fleet_data_source import FleetDataSource

        view_model = Mock()
        view_model.get_filtered_ships = Mock(return_value=[Mock()])
        ds = FleetDataSource(view_model)

        assert ds.get_ship_at_index(-1) is None
        assert ds.get_ship_at_index(5) is None
