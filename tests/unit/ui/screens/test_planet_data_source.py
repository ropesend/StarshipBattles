"""Tests for PlanetDataSource - Provides planet data for VirtualTable.

PROJ-188 Phase 3: PlanetDataSource value extraction tests.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

import pygame


class TestPlanetDataSourceColumns:
    """Test PlanetDataSource column configuration."""

    def test_get_columns_returns_columns_list(self):
        """get_columns returns the column definitions passed at init."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        columns = [
            {"id": "icon", "width": 50, "title": "", "type": "image", "visible": True},
            {"id": "name", "width": 150, "title": "Name", "attr": "name", "visible": True},
        ]
        galaxy = Mock()
        empire = Mock()
        ds = PlanetDataSource(columns, galaxy, empire)

        result = ds.get_columns()
        assert len(result) == 2
        assert result[0]["id"] == "icon"
        assert result[1]["id"] == "name"

    def test_columns_have_required_properties(self):
        """Each column has id, width, title, visible."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        columns = [
            {"id": "icon", "width": 50, "title": "", "type": "image", "visible": True},
            {"id": "name", "width": 150, "title": "Name", "attr": "name", "visible": True},
            {"id": "type", "width": 100, "title": "Type", "attr": "planet_type.name", "visible": True},
        ]
        galaxy = Mock()
        empire = Mock()
        ds = PlanetDataSource(columns, galaxy, empire)

        for col in ds.get_columns():
            assert "id" in col
            assert "width" in col
            assert "title" in col
            assert "visible" in col


class TestPlanetDataSourceRowCount:
    """Test PlanetDataSource row count."""

    def test_get_row_count_empty(self):
        """get_row_count returns 0 before update_data called."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        columns = []
        ds = PlanetDataSource(columns, Mock(), Mock())

        assert ds.get_row_count() == 0

    def test_get_row_count_after_update(self):
        """get_row_count returns len of filtered planets."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        columns = []
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([Mock(), Mock(), Mock()])

        assert ds.get_row_count() == 3


class TestPlanetDataSourceUpdateData:
    """Test PlanetDataSource update_data method."""

    def test_update_data_stores_reference(self):
        """update_data stores the planet list."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        columns = []
        ds = PlanetDataSource(columns, Mock(), Mock())

        planets = [Mock(name="Planet1"), Mock(name="Planet2")]
        ds.update_data(planets)

        assert ds.get_row_count() == 2

    def test_update_data_replaces_previous(self):
        """update_data replaces previous data."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        columns = []
        ds = PlanetDataSource(columns, Mock(), Mock())

        ds.update_data([Mock()])
        assert ds.get_row_count() == 1

        ds.update_data([Mock(), Mock(), Mock()])
        assert ds.get_row_count() == 3


class TestPlanetDataSourceCellValueFunc:
    """Test PlanetDataSource with func column type."""

    def test_func_column_calls_function(self):
        """get_cell_value calls func for func columns."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        func = Mock(return_value="System Alpha")
        columns = [
            {"id": "system", "width": 120, "title": "System", "func": func, "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_value(0, "system")

        assert result == "System Alpha"
        func.assert_called_once_with(planet)

    def test_func_column_with_planet_reference(self):
        """get_cell_value passes planet to func."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.surface_gravity = 9.81

        columns = [
            {
                "id": "grav",
                "width": 90,
                "title": "Grav (g)",
                "func": lambda p: f"{p.surface_gravity/9.81:.2f}",
                "visible": True,
            },
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_value(0, "grav")
        assert result == "1.00"


class TestPlanetDataSourceCellValueAttr:
    """Test PlanetDataSource with attr column type."""

    def test_attr_simple_attribute(self):
        """get_cell_value extracts simple attribute."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.name = "Terra Nova"
        columns = [
            {"id": "name", "width": 150, "title": "Name", "attr": "name", "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_value(0, "name")
        assert result == "Terra Nova"

    def test_attr_dotted_path(self):
        """get_cell_value extracts dotted attribute path."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.planet_type = Mock()
        planet.planet_type.name = "Continental"
        columns = [
            {"id": "type", "width": 100, "title": "Type", "attr": "planet_type.name", "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_value(0, "type")
        assert result == "Continental"

    def test_attr_missing_returns_question_mark(self):
        """get_cell_value returns '?' for missing attributes."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock(spec=[])  # No attributes
        columns = [
            {"id": "missing", "width": 100, "title": "Missing", "attr": "nonexistent", "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_value(0, "missing")
        assert result == "?"

    def test_attr_dotted_path_missing_intermediate(self):
        """get_cell_value returns '?' for missing intermediate attributes."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock(spec=[])  # No attributes
        columns = [
            {"id": "type", "width": 100, "title": "Type", "attr": "planet_type.name", "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_value(0, "type")
        assert result == "?"


class TestPlanetDataSourceCellValueFmt:
    """Test PlanetDataSource with fmt format string."""

    def test_fmt_float_formatting(self):
        """get_cell_value applies fmt to float values."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.surface_temperature = 298.7
        columns = [
            {"id": "temp", "width": 90, "title": "Temp (K)", "attr": "surface_temperature", "fmt": "{:.0f}", "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_value(0, "temp")
        assert result == "299"  # Rounded

    def test_fmt_percent_formatting(self):
        """get_cell_value applies percentage fmt."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.surface_water = 0.75
        columns = [
            {"id": "water", "width": 90, "title": "Water %", "attr": "surface_water", "fmt": "{:.0%}", "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_value(0, "water")
        assert result == "75%"

    def test_fmt_decimal_places(self):
        """get_cell_value applies decimal fmt."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.total_pressure_atm = 1.0132
        columns = [
            {"id": "pressure", "width": 100, "title": "Press (atm)", "attr": "total_pressure_atm", "fmt": "{:.2f}", "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_value(0, "pressure")
        assert result == "1.01"

    def test_fmt_only_applies_to_numbers(self):
        """get_cell_value only applies fmt to int/float."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.name = "Test Planet"
        columns = [
            {"id": "name", "width": 150, "title": "Name", "attr": "name", "fmt": "{:.2f}", "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_value(0, "name")
        assert result == "Test Planet"  # Not formatted


class TestPlanetDataSourceCellValueOutOfBounds:
    """Test PlanetDataSource with out-of-bounds indices."""

    def test_cell_value_out_of_bounds(self):
        """get_cell_value returns empty string for invalid index."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        columns = [
            {"id": "name", "width": 150, "title": "Name", "attr": "name", "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([Mock(name="Test")])

        result = ds.get_cell_value(5, "name")
        assert result == ""

    def test_cell_value_negative_index(self):
        """get_cell_value returns empty string for negative index."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        columns = [
            {"id": "name", "width": 150, "title": "Name", "attr": "name", "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([Mock(name="Test")])

        result = ds.get_cell_value(-1, "name")
        assert result == ""

    def test_cell_value_unknown_column(self):
        """get_cell_value returns empty string for unknown column."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        columns = [
            {"id": "name", "width": 150, "title": "Name", "attr": "name", "visible": True},
        ]
        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([Mock(name="Test")])

        result = ds.get_cell_value(0, "nonexistent_column")
        assert result == ""


class TestPlanetDataSourceCellImage:
    """Test PlanetDataSource get_cell_image for icon column."""

    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        """Initialize pygame for surface tests."""
        pygame.init()
        yield
        pygame.quit()

    def test_get_cell_image_icon_column(self):
        """get_cell_image returns cached surface for icon column."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.image_id = "earth_like_01"
        planet.image_rotation = 0

        columns = [
            {"id": "icon", "width": 50, "title": "", "type": "image", "visible": True},
        ]

        # Mock AssetManager
        mock_surface = pygame.Surface((128, 128))
        with patch("game.ui.screens.planet_data_source.AssetManager") as MockAM:
            mock_instance = Mock()
            mock_instance.load_planet_image = Mock(return_value=mock_surface)
            mock_instance.get_missing_texture = Mock(return_value=None)
            MockAM.instance = Mock(return_value=mock_instance)

            ds = PlanetDataSource(columns, Mock(), Mock())
            ds.update_data([planet])

            result = ds.get_cell_image(0, "icon")

            assert result is not None
            assert isinstance(result, pygame.Surface)
            # Should be scaled to 40x40
            assert result.get_width() == 40
            assert result.get_height() == 40

    def test_get_cell_image_caches_by_image_id_and_rotation(self):
        """get_cell_image uses cache key with image_id and rotation."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.image_id = "earth_like_01"
        planet.image_rotation = 45

        columns = [
            {"id": "icon", "width": 50, "title": "", "type": "image", "visible": True},
        ]

        mock_surface = pygame.Surface((128, 128))
        with patch("game.ui.screens.planet_data_source.AssetManager") as MockAM:
            mock_instance = Mock()
            mock_instance.load_planet_image = Mock(return_value=mock_surface)
            mock_instance.get_missing_texture = Mock(return_value=None)
            MockAM.instance = Mock(return_value=mock_instance)

            ds = PlanetDataSource(columns, Mock(), Mock())
            ds.update_data([planet])

            # First call
            result1 = ds.get_cell_image(0, "icon")
            # Second call (should use cache)
            result2 = ds.get_cell_image(0, "icon")

            assert result1 is result2
            # AssetManager should only be called once
            assert mock_instance.load_planet_image.call_count == 1

    def test_get_cell_image_applies_rotation(self):
        """get_cell_image applies planet rotation."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.image_id = "earth_like_01"
        planet.image_rotation = 90  # Non-zero rotation

        columns = [
            {"id": "icon", "width": 50, "title": "", "type": "image", "visible": True},
        ]

        mock_surface = pygame.Surface((128, 128))
        with patch("game.ui.screens.planet_data_source.AssetManager") as MockAM:
            mock_instance = Mock()
            mock_instance.load_planet_image = Mock(return_value=mock_surface)
            mock_instance.get_missing_texture = Mock(return_value=None)
            MockAM.instance = Mock(return_value=mock_instance)

            ds = PlanetDataSource(columns, Mock(), Mock())
            ds.update_data([planet])

            result = ds.get_cell_image(0, "icon")

            # Should still return a surface (rotation applied internally)
            assert result is not None
            assert isinstance(result, pygame.Surface)

    def test_get_cell_image_no_image_id_returns_blank(self):
        """get_cell_image returns blank surface when no image_id."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock(spec=["name"])  # No image_id attribute

        columns = [
            {"id": "icon", "width": 50, "title": "", "type": "image", "visible": True},
        ]

        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_image(0, "icon")

        assert result is not None
        assert isinstance(result, pygame.Surface)
        assert result.get_width() == 40
        assert result.get_height() == 40

    def test_get_cell_image_missing_texture_returns_blank(self):
        """get_cell_image returns blank surface for missing texture."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.image_id = "nonexistent"
        planet.image_rotation = 0

        columns = [
            {"id": "icon", "width": 50, "title": "", "type": "image", "visible": True},
        ]

        missing_texture = pygame.Surface((32, 32))
        with patch("game.ui.screens.planet_data_source.AssetManager") as MockAM:
            mock_instance = Mock()
            mock_instance.load_planet_image = Mock(return_value=missing_texture)
            mock_instance.get_missing_texture = Mock(return_value=missing_texture)
            MockAM.instance = Mock(return_value=mock_instance)

            ds = PlanetDataSource(columns, Mock(), Mock())
            ds.update_data([planet])

            result = ds.get_cell_image(0, "icon")

            # Should return blank surface (fallback)
            assert result is not None
            assert isinstance(result, pygame.Surface)

    def test_get_cell_image_non_image_column_returns_none(self):
        """get_cell_image returns None for non-image columns."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet = Mock()
        planet.name = "Test"

        columns = [
            {"id": "name", "width": 150, "title": "Name", "attr": "name", "visible": True},
        ]

        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        result = ds.get_cell_image(0, "name")
        assert result is None

    def test_get_cell_image_out_of_bounds_returns_none(self):
        """get_cell_image returns None for out of bounds index."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        columns = [
            {"id": "icon", "width": 50, "title": "", "type": "image", "visible": True},
        ]

        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([Mock(image_id="test", image_rotation=0)])

        result = ds.get_cell_image(5, "icon")
        assert result is None


class TestPlanetDataSourceGetPlanetAtIndex:
    """Test PlanetDataSource get_planet_at_index helper."""

    def test_get_planet_at_index_valid(self):
        """get_planet_at_index returns planet at index."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        planet1 = Mock(name="Planet1")
        planet2 = Mock(name="Planet2")

        ds = PlanetDataSource([], Mock(), Mock())
        ds.update_data([planet1, planet2])

        assert ds.get_planet_at_index(0) is planet1
        assert ds.get_planet_at_index(1) is planet2

    def test_get_planet_at_index_out_of_bounds(self):
        """get_planet_at_index returns None for invalid index."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        ds = PlanetDataSource([], Mock(), Mock())
        ds.update_data([Mock()])

        assert ds.get_planet_at_index(-1) is None
        assert ds.get_planet_at_index(5) is None


class TestPlanetDataSourceIntegration:
    """Integration tests for PlanetDataSource with real column configs."""

    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        """Initialize pygame for surface tests."""
        pygame.init()
        yield
        pygame.quit()

    def test_full_column_extraction(self):
        """Test extraction across multiple column types."""
        from game.ui.screens.planet_data_source import PlanetDataSource

        # Create a realistic planet mock
        planet = Mock()
        planet.name = "Terra Nova"
        planet.planet_type = Mock()
        planet.planet_type.name = "Continental"
        planet.surface_temperature = 288.7
        planet.surface_water = 0.7
        planet.total_pressure_atm = 1.01

        # Lambda for gravity
        def get_gravity(p):
            return f"{p.surface_gravity / 9.81:.2f}"

        planet.surface_gravity = 9.81  # 1g

        columns = [
            {"id": "name", "width": 150, "title": "Name", "attr": "name", "visible": True},
            {"id": "type", "width": 100, "title": "Type", "attr": "planet_type.name", "visible": True},
            {"id": "temp", "width": 90, "title": "Temp (K)", "attr": "surface_temperature", "fmt": "{:.0f}", "visible": True},
            {"id": "water", "width": 90, "title": "Water %", "attr": "surface_water", "fmt": "{:.0%}", "visible": True},
            {"id": "grav", "width": 90, "title": "Grav (g)", "func": get_gravity, "visible": True},
        ]

        ds = PlanetDataSource(columns, Mock(), Mock())
        ds.update_data([planet])

        assert ds.get_cell_value(0, "name") == "Terra Nova"
        assert ds.get_cell_value(0, "type") == "Continental"
        assert ds.get_cell_value(0, "temp") == "289"  # Rounded
        assert ds.get_cell_value(0, "water") == "70%"
        assert ds.get_cell_value(0, "grav") == "1.00"
