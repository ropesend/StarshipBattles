"""
Unit tests for strategy_detail_fmt.py - pure formatting functions.

Tests format_spectrum_html, format_atmosphere_raw, get_label_for_object,
format_fleet_info, and related helper functions.
"""
import pytest
from unittest.mock import Mock, MagicMock
from collections import namedtuple

from game.ui.screens.strategy_detail_fmt import (
    format_spectrum_html,
    format_atmosphere_raw,
    format_planet_info,
    format_star_system_info,
    format_star_info,
    format_fleet_info,
    format_uncolonized_habitability_for_empire,
    get_label_for_object,
    _format_ship_groups,
    _format_cargo_summary,
    _format_orders,
)
from game.strategy.data.order_types import OrderType


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def mock_spectrum():
    """Create mock spectrum with all 9 bands."""
    spectrum = Mock()
    spectrum.gamma_ray = 1.5e-10
    spectrum.xray = 2.3e-8
    spectrum.ultraviolet = 4.2e-5
    spectrum.blue = 1.8e-3
    spectrum.green = 2.1e-3
    spectrum.red = 1.9e-3
    spectrum.infrared = 5.5e-4
    spectrum.microwave = 1.2e-6
    spectrum.radio = 3.4e-9
    return spectrum


@pytest.fixture
def mock_star(mock_spectrum):
    """Create mock star with spectrum."""
    star = Mock()
    star.name = "Sol"
    star.spectrum = mock_spectrum
    star.star_type = Mock(name="G2V")
    star.star_type.name = "G2V"
    star.mass = 1.0
    star.temperature = 5778
    star.radius_hexes = 2
    return star


@pytest.fixture
def mock_planet():
    """Create mock planet with various attributes."""
    planet = Mock()
    planet.name = "Earth"
    planet.planet_type = Mock()
    planet.planet_type.name = "Terran"
    planet.orbit_distance = 3
    planet.mass = 5.97e24
    planet.radius = 6371000
    planet.surface_gravity = 9.81
    planet.surface_temperature = 288
    planet.surface_water = 0.71
    planet.total_pressure_atm = 1.0
    planet.atmosphere = {"N2": 78400.0, "O2": 20900.0, "Ar": 934.0, "CO2": 40.0}
    planet.owner_id = None
    return planet


@pytest.fixture
def mock_fleet():
    """Create mock fleet with ships and orders."""
    fleet = Mock()
    fleet.id = "F-001"
    fleet.name = "Fleet F-001"
    fleet.owner_id = 1
    fleet.location = (10, 20)
    fleet.speed = 5
    # PROJ-210: fuel_endurance accessed via fleet.resources property
    fleet.resources = Mock()
    fleet.resources.fuel_endurance = Mock(return_value=25)
    fleet.orders = []
    fleet.ships = []
    return fleet


@pytest.fixture
def mock_star_system(mock_star):
    """Create mock star system."""
    system = Mock()
    system.name = "Sol System"
    system.primary_star = mock_star
    system.stars = [mock_star]
    return system


# =============================================================================
# format_spectrum_html Tests
# =============================================================================

class TestFormatSpectrumHtml:
    """Tests for format_spectrum_html()."""

    def test_formats_all_nine_bands(self, mock_star):
        """Test returns HTML with all 9 spectrum bands."""
        result = format_spectrum_html(mock_star)

        assert "Gamma:" in result
        assert "X-Ray:" in result
        assert "UV:" in result
        assert "Blue:" in result
        assert "Green:" in result
        assert "Red:" in result
        assert "IR:" in result
        assert "Micro:" in result
        assert "Radio:" in result

    def test_uses_scientific_notation(self, mock_star):
        """Test spectrum values use .2e format."""
        result = format_spectrum_html(mock_star)

        # Check scientific notation format (e.g., 1.50e-10)
        assert "e-" in result or "e+" in result
        # Verify specific formatted values
        assert "1.50e-10" in result  # gamma_ray
        assert "2.30e-08" in result  # xray

    def test_includes_header(self, mock_star):
        """Test includes spectrum header."""
        result = format_spectrum_html(mock_star)

        assert "Spectrum Intensity" in result
        assert "W/m^2" in result


# =============================================================================
# format_atmosphere_raw Tests
# =============================================================================

class TestFormatAtmosphereRaw:
    """Tests for format_atmosphere_raw()."""

    def test_formats_atmosphere_dict(self, mock_planet):
        """Test with planet having atmosphere dict."""
        result = format_atmosphere_raw(mock_planet)

        assert "Atmosphere" in result
        assert "1.00 atm" in result
        assert "N2:" in result
        assert "O2:" in result

    def test_formats_pressure_values(self, mock_planet):
        """Test atmosphere values formatted in Pa."""
        result = format_atmosphere_raw(mock_planet)

        assert "78400.0 Pa" in result  # N2
        assert "20900.0 Pa" in result  # O2

    def test_handles_empty_atmosphere(self, mock_planet):
        """Test with planet having empty atmosphere."""
        mock_planet.atmosphere = {}
        mock_planet.total_pressure_atm = 0.0

        result = format_atmosphere_raw(mock_planet)

        assert "Atmosphere" in result
        assert "0.00 atm" in result


# =============================================================================
# get_label_for_object Tests
# =============================================================================

class TestGetLabelForObject:
    """Tests for get_label_for_object()."""

    def test_star_system_label(self, mock_star_system):
        """Test with star system object."""
        mock_star_system.systems = None  # Mark as system via protocol check

        # Mock the protocol check
        with pytest.MonkeyPatch().context() as m:
            from game.ui.screens import strategy_detail_fmt
            m.setattr(strategy_detail_fmt, 'is_star_system', lambda x: True)
            m.setattr(strategy_detail_fmt, 'is_star', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_planet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_fleet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_warp_point', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_sector_environment', lambda x: False)

            result = get_label_for_object(mock_star_system)
            assert "System:" in result
            assert "Sol System" in result

    def test_star_label(self, mock_star):
        """Test with star object."""
        with pytest.MonkeyPatch().context() as m:
            from game.ui.screens import strategy_detail_fmt
            m.setattr(strategy_detail_fmt, 'is_star_system', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_star', lambda x: True)
            m.setattr(strategy_detail_fmt, 'is_planet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_fleet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_warp_point', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_sector_environment', lambda x: False)

            result = get_label_for_object(mock_star)
            assert "Star:" in result
            assert "Sol" in result

    def test_planet_label(self, mock_planet):
        """Test with planet object."""
        with pytest.MonkeyPatch().context() as m:
            from game.ui.screens import strategy_detail_fmt
            m.setattr(strategy_detail_fmt, 'is_star_system', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_star', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_planet', lambda x: True)
            m.setattr(strategy_detail_fmt, 'is_fleet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_warp_point', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_sector_environment', lambda x: False)

            result = get_label_for_object(mock_planet)
            assert "Planet:" in result
            assert "Earth" in result

    def test_fleet_label(self, mock_fleet):
        """Test with fleet object."""
        mock_fleet.ships = [Mock(), Mock(), Mock()]  # 3 ships

        with pytest.MonkeyPatch().context() as m:
            from game.ui.screens import strategy_detail_fmt
            m.setattr(strategy_detail_fmt, 'is_star_system', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_star', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_planet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_fleet', lambda x: True)
            m.setattr(strategy_detail_fmt, 'is_warp_point', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_sector_environment', lambda x: False)

            result = get_label_for_object(mock_fleet)
            assert "Fleet" in result
            assert "F-001" in result
            assert "(3)" in result

    def test_warp_point_label(self):
        """Test with warp point object."""
        warp_point = Mock()
        warp_point.destination_id = "Alpha Centauri"

        with pytest.MonkeyPatch().context() as m:
            from game.ui.screens import strategy_detail_fmt
            m.setattr(strategy_detail_fmt, 'is_star_system', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_star', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_planet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_fleet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_warp_point', lambda x: True)
            m.setattr(strategy_detail_fmt, 'is_sector_environment', lambda x: False)

            result = get_label_for_object(warp_point)
            assert "Warp Point" in result
            assert "Alpha Centauri" in result

    def test_unknown_object_fallback(self):
        """Test with unknown object type."""
        unknown = Mock()

        with pytest.MonkeyPatch().context() as m:
            from game.ui.screens import strategy_detail_fmt
            m.setattr(strategy_detail_fmt, 'is_star_system', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_star', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_planet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_fleet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_warp_point', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_sector_environment', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_storm', lambda x: False)

            result = get_label_for_object(unknown)
            assert result == "Unknown Object"

    def test_sector_environment_label(self):
        """Test with sector environment object."""
        env = Mock()

        with pytest.MonkeyPatch().context() as m:
            from game.ui.screens import strategy_detail_fmt
            m.setattr(strategy_detail_fmt, 'is_star_system', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_star', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_planet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_fleet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_warp_point', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_sector_environment', lambda x: True)
            m.setattr(strategy_detail_fmt, 'is_storm', lambda x: False)

            result = get_label_for_object(env)
            assert "Radiation Analysis" in result

    def test_storm_label(self):
        """Test with storm object."""
        storm = Mock()
        storm.name = "Ion Storm Alpha"

        with pytest.MonkeyPatch().context() as m:
            from game.ui.screens import strategy_detail_fmt
            m.setattr(strategy_detail_fmt, 'is_star_system', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_star', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_planet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_fleet', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_warp_point', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_sector_environment', lambda x: False)
            m.setattr(strategy_detail_fmt, 'is_storm', lambda x: True)

            result = get_label_for_object(storm)
            assert "Storm:" in result
            assert "Ion Storm Alpha" in result


# =============================================================================
# format_fleet_info Tests
# =============================================================================

class TestFormatFleetInfo:
    """Tests for format_fleet_info()."""

    def test_formats_fleet_header(self, mock_fleet):
        """Test fleet header information."""
        result = format_fleet_info(mock_fleet)

        assert "Fleet:" in result
        assert "F-001" in result
        assert "Owner:" in result
        assert "Location:" in result

    def test_formats_travel_range(self, mock_fleet):
        """Test fleet travel range display."""
        result = format_fleet_info(mock_fleet)

        assert "Range:" in result
        assert "5 hex/turn" in result
        assert "25 hex fuel" in result

    def test_unlimited_fuel_display(self, mock_fleet):
        """Test unlimited fuel display."""
        # PROJ-210: fuel_endurance accessed via fleet.resources property
        mock_fleet.resources.fuel_endurance = Mock(return_value=-1)

        result = format_fleet_info(mock_fleet)

        assert "unlimited fuel" in result

    def test_fleet_with_no_ships(self, mock_fleet):
        """Test fleet with no ships."""
        mock_fleet.ships = []

        result = format_fleet_info(mock_fleet)

        assert "Ships: None" in result

    def test_fleet_with_ships(self, mock_fleet):
        """Test fleet with ships."""
        ship1 = Mock()
        ship1.design_id = "cruiser"
        ship1.design_data = {"name": "Battle Cruiser"}
        ship1.get_calculated_stats = Mock(return_value={"mass": 1000})
        ship1.cargo_contents = {}

        ship2 = Mock()
        ship2.design_id = "cruiser"
        ship2.design_data = {"name": "Battle Cruiser"}
        ship2.get_calculated_stats = Mock(return_value={"mass": 1000})
        ship2.cargo_contents = {}

        mock_fleet.ships = [ship1, ship2]

        result = format_fleet_info(mock_fleet)

        assert "Ships (2):" in result
        assert "Battle Cruiser x 2" in result

    def test_fleet_with_no_orders(self, mock_fleet):
        """Test fleet with no orders."""
        mock_fleet.orders = []

        result = format_fleet_info(mock_fleet)

        assert "Orders:" in result
        assert "(No Orders)" in result

    def test_fleet_with_move_order(self, mock_fleet):
        """Test fleet with move order."""
        order = Mock()
        order.type = OrderType.MOVE
        order.target = (15, 25)
        mock_fleet.orders = [order]

        result = format_fleet_info(mock_fleet)

        assert "1. MOVE" in result


# =============================================================================
# _format_ship_groups Tests
# =============================================================================

class TestFormatShipGroups:
    """Tests for _format_ship_groups()."""

    def test_empty_fleet(self, mock_fleet):
        """Test with no ships."""
        mock_fleet.ships = []

        result = _format_ship_groups(mock_fleet)

        assert "Ships: None" in result

    def test_single_ship(self, mock_fleet):
        """Test with single ship."""
        ship = Mock()
        ship.design_id = "scout"
        ship.design_data = {"name": "Scout Ship"}
        ship.get_calculated_stats = Mock(return_value={"mass": 100})
        mock_fleet.ships = [ship]

        result = _format_ship_groups(mock_fleet)

        assert "Ships (1):" in result
        assert "Scout Ship" in result
        assert "x" not in result  # No multiplier for single ship

    def test_multiple_same_design(self, mock_fleet):
        """Test multiple ships of same design."""
        ships = []
        for _ in range(5):
            ship = Mock()
            ship.design_id = "fighter"
            ship.design_data = {"name": "Fighter"}
            ship.get_calculated_stats = Mock(return_value={"mass": 50})
            ships.append(ship)
        mock_fleet.ships = ships

        result = _format_ship_groups(mock_fleet)

        assert "Ships (5):" in result
        assert "Fighter x 5" in result

    def test_sorted_by_mass_descending(self, mock_fleet):
        """Test ships sorted by mass descending."""
        ship_heavy = Mock()
        ship_heavy.design_id = "battleship"
        ship_heavy.design_data = {"name": "Battleship"}
        ship_heavy.get_calculated_stats = Mock(return_value={"mass": 5000})

        ship_light = Mock()
        ship_light.design_id = "scout"
        ship_light.design_data = {"name": "Scout"}
        ship_light.get_calculated_stats = Mock(return_value={"mass": 100})

        mock_fleet.ships = [ship_light, ship_heavy]  # Light first

        result = _format_ship_groups(mock_fleet)

        # Battleship should appear before Scout
        battleship_pos = result.find("Battleship")
        scout_pos = result.find("Scout")
        assert battleship_pos < scout_pos


# =============================================================================
# _format_cargo_summary Tests
# =============================================================================

class TestFormatCargoSummary:
    """Tests for _format_cargo_summary()."""

    def test_no_cargo(self, mock_fleet):
        """Test fleet with no cargo."""
        ship = Mock()
        ship.cargo_contents = {}
        mock_fleet.ships = [ship]

        result = _format_cargo_summary(mock_fleet)

        assert result == ""

    def test_cargo_aggregation(self, mock_fleet):
        """Test cargo aggregated across ships."""
        ship1 = Mock()
        ship1.cargo_contents = {"colonists": 100, "food": 50}

        ship2 = Mock()
        ship2.cargo_contents = {"colonists": 150, "ore": 200}

        mock_fleet.ships = [ship1, ship2]

        result = _format_cargo_summary(mock_fleet)

        assert "Cargo:" in result
        assert "Colonists: 250" in result
        assert "Food: 50" in result
        assert "Ore: 200" in result

    def test_cargo_name_formatting(self, mock_fleet):
        """Test cargo names formatted with title case."""
        ship = Mock()
        ship.cargo_contents = {"rare_minerals": 100}
        mock_fleet.ships = [ship]

        result = _format_cargo_summary(mock_fleet)

        assert "Rare Minerals:" in result


# =============================================================================
# _format_orders Tests
# =============================================================================

class TestFormatOrders:
    """Tests for _format_orders()."""

    def test_no_orders(self, mock_fleet):
        """Test with no orders."""
        mock_fleet.orders = []

        result = _format_orders(mock_fleet)

        assert "Orders:" in result
        assert "(No Orders)" in result

    def test_move_order(self, mock_fleet):
        """Test MOVE order formatting."""
        order = Mock()
        order.type = OrderType.MOVE
        order.target = (10, 20)
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. MOVE (10, 20)" in result

    def test_colonize_order(self, mock_fleet):
        """Test COLONIZE order formatting."""
        planet = Mock()
        planet.name = "New Eden"

        order = Mock()
        order.type = OrderType.COLONIZE
        order.target = planet
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. COLONIZE New Eden" in result

    def test_build_order(self, mock_fleet):
        """Test BUILD order formatting."""
        order = Mock()
        order.type = OrderType.BUILD
        mock_fleet.orders = [order]
        mock_fleet.construction_queue = [Mock(), Mock(), Mock()]

        result = _format_orders(mock_fleet)

        assert "1. BUILDING (3 items)" in result

    def test_transfer_order_dict_target(self, mock_fleet):
        """Test TRANSFER order with dict target."""
        order = Mock()
        order.type = OrderType.TRANSFER
        order.target = {"direction": "load", "cargo_type": "colonists", "amount": 100}
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. LOAD 100 colonists" in result

    def test_transfer_order_all_amount(self, mock_fleet):
        """Test TRANSFER order with amount 0 means 'All'."""
        order = Mock()
        order.type = OrderType.TRANSFER
        order.target = {"direction": "unload", "cargo_type": "ore", "amount": 0}
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. UNLOAD All ore" in result

    def test_move_to_fleet_order(self, mock_fleet):
        """Test MOVE_TO_FLEET order formatting shows 'Intercept Fleet {id}'."""
        target_fleet = Mock()
        target_fleet.ships = []
        target_fleet.orders = []
        target_fleet.id = 10042

        order = Mock()
        order.type = OrderType.MOVE_TO_FLEET
        order.target = target_fleet
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. Intercept Fleet 10042" in result

    def test_move_to_fleet_order_invalid_target(self, mock_fleet):
        """Test MOVE_TO_FLEET order with non-fleet target shows '?'."""
        order = Mock(spec=[])  # no attributes — fails is_fleet check
        order.type = OrderType.MOVE_TO_FLEET
        order.target = "not_a_fleet"
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. Intercept Fleet ?" in result

    def test_join_fleet_order(self, mock_fleet):
        """Test JOIN_FLEET order formatting shows 'Join Fleet {id}'."""
        target_fleet = Mock()
        target_fleet.ships = []
        target_fleet.orders = []
        target_fleet.id = 10099

        order = Mock()
        order.type = OrderType.JOIN_FLEET
        order.target = target_fleet
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. Join Fleet 10099" in result

    def test_join_fleet_order_invalid_target(self, mock_fleet):
        """Test JOIN_FLEET order with non-fleet target shows '?'."""
        order = Mock(spec=[])
        order.type = OrderType.JOIN_FLEET
        order.target = "not_a_fleet"
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. Join Fleet ?" in result

    def test_load_population_order(self, mock_fleet):
        """Test LOAD_POPULATION order formatting."""
        order = Mock()
        order.type = OrderType.LOAD_POPULATION
        order.target = {"direction": "load"}
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. Load Cargo" in result

    def test_unload_population_order(self, mock_fleet):
        """Test UNLOAD_POPULATION order formatting."""
        order = Mock()
        order.type = OrderType.UNLOAD_POPULATION
        order.target = {"direction": "unload"}
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. Drop Cargo" in result

    def test_implode_planet_order(self, mock_fleet):
        """Test IMPLODE_PLANET order formatting with planet name."""
        planet = Mock()
        planet.name = "Doomed World"
        planet.population = 0  # has planet attrs for is_planet

        order = Mock()
        order.type = OrderType.IMPLODE_PLANET
        order.target = planet
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. Implode Doomed World" in result

    def test_stellerate_star_order(self, mock_fleet):
        """Test STELLERATE_STAR order formatting."""
        order = Mock()
        order.type = OrderType.STELLERATE_STAR
        order.target = None
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. Stellerate Star" in result

    def test_create_dyson_sphere_order(self, mock_fleet):
        """Test CREATE_DYSON_SPHERE order formatting."""
        order = Mock()
        order.type = OrderType.CREATE_DYSON_SPHERE
        order.target = None
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. Create Dyson Sphere" in result

    def test_generic_order_type(self, mock_fleet):
        """Test generic order type fallback for truly unknown order types."""
        order = Mock()
        order.type = OrderType.SELF_DESTRUCT
        order.target = None
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. SELF_DESTRUCT" in result

    def test_multiple_orders_numbered(self, mock_fleet):
        """Test multiple orders are numbered."""
        order1 = Mock()
        order1.type = OrderType.MOVE
        order1.target = (5, 5)

        order2 = Mock()
        order2.type = OrderType.MOVE
        order2.target = (10, 10)

        mock_fleet.orders = [order1, order2]

        result = _format_orders(mock_fleet)

        assert "1. MOVE" in result
        assert "2. MOVE" in result


# =============================================================================
# format_planet_info Tests
# =============================================================================

class TestFormatPlanetInfo:
    """Tests for format_planet_info()."""

    def test_basic_planet_info(self, mock_planet):
        """Test basic planet formatting."""
        result = format_planet_info(mock_planet)

        assert "Planet:" in result
        assert "Earth" in result
        assert "Type:" in result
        assert "Terran" in result
        assert "Orbit:" in result
        assert "Ring 3" in result

    def test_mass_formatting_earth_mass(self, mock_planet):
        """Test mass formatted in Earth masses."""
        mock_planet.mass = 5.97e24  # 1 Earth mass

        result = format_planet_info(mock_planet)

        assert "Mass:" in result
        assert "M_Earth" in result

    def test_mass_formatting_jupiter_mass(self, mock_planet):
        """Test mass formatted in Jupiter masses for large planets."""
        mock_planet.mass = 1.89e27  # 1 Jupiter mass

        result = format_planet_info(mock_planet)

        assert "M_Jup" in result

    def test_radius_in_km(self, mock_planet):
        """Test radius displayed in km."""
        result = format_planet_info(mock_planet)

        assert "Radius:" in result
        assert "6371 km" in result

    def test_gravity_in_g(self, mock_planet):
        """Test gravity displayed in g."""
        result = format_planet_info(mock_planet)

        assert "Gravity:" in result
        assert "1.00 g" in result

    def test_owned_planet_shows_colony_status(self, mock_planet):
        """Test owned planet shows colony status."""
        mock_planet.owner_id = 1
        mock_planet.populations = []
        mock_planet.max_population = 0
        mock_planet.facilities = []

        result = format_planet_info(mock_planet)

        assert "Colony Status:" in result
        assert "Owned" in result

    def test_population_formatting_millions(self, mock_planet):
        """Test population formatted with M suffix."""
        mock_planet.owner_id = 1
        pop = Mock()
        pop.count = 5_500_000
        pop.happiness = 0.9
        pop.race_id = "Humans"
        mock_planet.populations = [pop]
        mock_planet.max_population = 10_000_000
        mock_planet.facilities = []

        result = format_planet_info(mock_planet)

        assert "5.5M" in result
        assert "10.0M" in result

    def test_population_formatting_thousands(self, mock_planet):
        """Test population formatted with K suffix."""
        mock_planet.owner_id = 1
        pop = Mock()
        pop.count = 5_500
        pop.happiness = 0.5
        pop.race_id = "Humans"
        mock_planet.populations = [pop]
        mock_planet.max_population = 10_000
        mock_planet.facilities = []

        result = format_planet_info(mock_planet)

        assert "5k" in result or "6k" in result  # Rounding

    def test_happiness_indicators(self, mock_planet):
        """Test happiness indicators display."""
        mock_planet.owner_id = 1

        pop_happy = Mock()
        pop_happy.count = 1000
        pop_happy.happiness = 0.9
        pop_happy.race_id = "Happy"

        pop_neutral = Mock()
        pop_neutral.count = 1000
        pop_neutral.happiness = 0.5
        pop_neutral.race_id = "Neutral"

        pop_unhappy = Mock()
        pop_unhappy.count = 1000
        pop_unhappy.happiness = 0.2
        pop_unhappy.race_id = "Unhappy"

        mock_planet.populations = [pop_happy, pop_neutral, pop_unhappy]
        mock_planet.max_population = 10000
        mock_planet.facilities = []

        result = format_planet_info(mock_planet)

        assert "[+]" in result  # Happy
        assert "[~]" in result  # Neutral
        assert "[-]" in result  # Unhappy

    def test_facilities_display(self, mock_planet):
        """Test facilities list display."""
        mock_planet.owner_id = 1
        mock_planet.populations = []
        mock_planet.max_population = 0

        # Facility with proper name and operational status
        facility1 = Mock()
        facility1.name = "Mining Complex"
        facility1.design_id = "mining_01"
        facility1.is_operational = True

        # Facility with empty name (falls back to design_id) and offline status
        facility2 = Mock()
        facility2.name = ""  # Empty name triggers fallback to design_id
        facility2.design_id = "factory_01"
        facility2.is_operational = False  # Offline

        mock_planet.facilities = [facility1, facility2]

        result = format_planet_info(mock_planet)

        assert "Complexes:" in result
        assert "Mining Complex" in result
        assert "(Active)" in result
        assert "factory_01" in result
        assert "(Offline)" in result


# =============================================================================
# format_star_system_info Tests
# =============================================================================

class TestFormatStarSystemInfo:
    """Tests for format_star_system_info()."""

    def test_system_with_primary_star(self, mock_star_system):
        """Test system with primary star."""
        result = format_star_system_info(mock_star_system)

        assert "System:" in result
        assert "Sol System" in result
        assert "Primary:" in result
        assert "Sol" in result
        assert "Type:" in result
        assert "Stars:" in result

    def test_empty_system(self, mock_star_system):
        """Test system with no primary star."""
        mock_star_system.primary_star = None

        result = format_star_system_info(mock_star_system)

        assert "System:" in result
        assert "(Empty System)" in result

    def test_system_shows_active_stellar_stabilizer(self, mock_star_system):
        """System with active stellar stabilizer should show it in output."""
        from game.strategy.data.component_activation_state import (
            ActivationPhase, ComponentActivationState,
        )
        planet = Mock()
        planet.name = "Earth"
        planet.active_abilities = {'StellarStabilizer': True}
        planet.orders = []

        facility = Mock()
        facility.design_data = {
            'layers': {
                'OUTER': [{'id': 'stellar_stabilizer', 'abilities': {
                    'StellarStabilizer': {'scope': 'system'}
                }}]
            }
        }
        facility.component_states = {
            "OUTER:0:stellar_stabilizer": ComponentActivationState(
                phase=ActivationPhase.ACTIVE,
                ability_name="StellarStabilizer",
            ).to_dict()
        }
        planet.facilities = [facility]
        mock_star_system.planets = [planet]

        result = format_star_system_info(mock_star_system)

        assert "Stellar Stabilizer" in result
        assert "Active" in result

    def test_system_shows_inactive_stabilizer(self, mock_star_system):
        """System with inactive stabilizer should show Inactive status."""
        planet = Mock()
        planet.name = "Mars"
        planet.active_abilities = {'WarpFieldStabilizer': False}
        planet.orders = []

        facility = Mock()
        facility.design_data = {
            'layers': {
                'OUTER': [{'id': 'warp_field_stabilizer', 'abilities': {
                    'WarpFieldStabilizer': {'scope': 'system'}
                }}]
            }
        }
        facility.component_states = {}
        planet.facilities = [facility]
        mock_star_system.planets = [planet]

        result = format_star_system_info(mock_star_system)

        assert "Warp Field Stabilizer" in result
        assert "Inactive" in result

    def test_system_shows_activation_progress(self, mock_star_system):
        """System panel should show tick progress for activating abilities."""
        from game.strategy.data.component_activation_state import (
            ActivationPhase, ComponentActivationState,
        )

        planet = Mock()
        planet.name = "Venus"
        planet.active_abilities = {'StellarStabilizer': False}
        planet.orders = []

        facility = Mock()
        facility.design_data = {
            'layers': {
                'OUTER': [{'id': 'stellar_stabilizer', 'abilities': {
                    'StellarStabilizer': {'scope': 'system'}
                }}]
            }
        }
        facility.component_states = {
            "OUTER:0:stellar_stabilizer": ComponentActivationState(
                phase=ActivationPhase.ACTIVATING,
                progress_ticks=50,
                required_ticks=250,
                ability_name="StellarStabilizer",
                energy_drain_rate=250.0,
            ).to_dict()
        }
        planet.facilities = [facility]
        mock_star_system.planets = [planet]

        result = format_star_system_info(mock_star_system)

        assert "Stellar Stabilizer" in result
        assert "Activating" in result
        assert "50/250 ticks" in result

    def test_system_without_stabilizers_shows_none(self, mock_star_system):
        """System without stabilizer facilities should not show ability lines."""
        mock_star_system.planets = []

        result = format_star_system_info(mock_star_system)

        assert "Stellar Stabilizer" not in result
        assert "Warp Field Stabilizer" not in result
        assert "Geologic Stabilizer" not in result


# =============================================================================
# format_star_info Tests
# =============================================================================

class TestFormatStarInfo:
    """Tests for format_star_info()."""

    def test_star_formatting(self, mock_star):
        """Test star information formatting."""
        result = format_star_info(mock_star)

        assert "Star:" in result
        assert "Sol" in result
        assert "Type:" in result
        assert "Mass:" in result
        assert "1.00 Sol" in result
        assert "Temp:" in result
        assert "5778 K" in result
        assert "Radius:" in result
        assert "2 Hex" in result


# ---------------------------------------------------------------------------
# PROJ-290 Phase 2: format_uncolonized_habitability_for_empire
# ---------------------------------------------------------------------------

class TestUncolonizedHabitabilityForEmpire:
    """Tests for the uncolonized-planet-habitability helper + its
    integration into `format_planet_info`.

    Section contract:
    - Shown only when the planet is unowned AND an empire + registry are
      provided.
    - One line per `empire.resident_species()` entry: ` - {name}: {score}/100`.
    - Sorted DESCENDING by score (best-fit first).
    - Score = `int(round(score_planet_for_race(planet, race_config) * 100))`.
    - race_id with `registry.get_race(id) == None` is silently skipped.
    - Empty resident_species set → returns `""` (section omitted).
    """

    def _mock_race(self, race_name: str):
        """Race config stub with `.race_name` as the primary display field
        (matches `strategy_session_facade` display-name resolution)."""
        race = Mock()
        race.race_name = race_name
        race.name = race_name  # legacy fallback on some race configs
        return race

    def _mock_empire(self, resident_species_set):
        empire = Mock()
        empire.resident_species.return_value = set(resident_species_set)
        return empire

    def test_empty_resident_species_returns_empty_string(self, mock_planet):
        from unittest.mock import patch
        empire = self._mock_empire(set())
        registry = Mock()
        with patch(
            "game.ui.screens.strategy_detail_fmt.score_planet_for_race",
            return_value=0.5,
        ):
            result = format_uncolonized_habitability_for_empire(mock_planet, empire, registry)
        assert result == ""

    def test_single_resident_species_renders_one_line(self, mock_planet):
        from unittest.mock import patch
        empire = self._mock_empire({"human"})
        registry = Mock()
        registry.get_race.return_value = self._mock_race("Humans")
        with patch(
            "game.ui.screens.strategy_detail_fmt.score_planet_for_race",
            return_value=0.94,
        ):
            result = format_uncolonized_habitability_for_empire(mock_planet, empire, registry)
        assert "Habitability for your species" in result
        assert "Humans: 94/100" in result

    def test_three_species_sorted_descending(self, mock_planet):
        from unittest.mock import patch
        empire = self._mock_empire({"human", "voidari", "ghost"})
        registry = Mock()

        races = {
            "human": self._mock_race("Humans"),
            "voidari": self._mock_race("Voidari"),
            "ghost": self._mock_race("Ghosts"),
        }
        registry.get_race.side_effect = lambda rid: races.get(rid)

        scores = {"human": 0.80, "voidari": 0.30, "ghost": 0.55}
        with patch(
            "game.ui.screens.strategy_detail_fmt.score_planet_for_race",
            side_effect=lambda planet, race: scores[
                next(rid for rid, r in races.items() if r is race)
            ],
        ):
            result = format_uncolonized_habitability_for_empire(mock_planet, empire, registry)

        # Extract the order of appearance.
        humans_idx = result.index("Humans:")
        ghosts_idx = result.index("Ghosts:")
        voidari_idx = result.index("Voidari:")
        assert humans_idx < ghosts_idx < voidari_idx  # 80 > 55 > 30

    def test_missing_race_config_silently_skipped(self, mock_planet):
        from unittest.mock import patch
        empire = self._mock_empire({"human", "extinct_race"})
        registry = Mock()

        def _resolve(race_id):
            if race_id == "human":
                return self._mock_race("Humans")
            return None  # save drift — race file no longer exists

        registry.get_race.side_effect = _resolve
        with patch(
            "game.ui.screens.strategy_detail_fmt.score_planet_for_race",
            return_value=0.5,
        ):
            result = format_uncolonized_habitability_for_empire(mock_planet, empire, registry)

        assert "Humans: 50/100" in result
        assert "extinct_race" not in result
        assert "None" not in result  # never emit the raw None

    def test_score_rounded_to_int(self, mock_planet):
        """0.945 → 94 (banker's round may land 94 or 95 depending on
        exact float; use a clearly-rounded value)."""
        from unittest.mock import patch
        empire = self._mock_empire({"human"})
        registry = Mock()
        registry.get_race.return_value = self._mock_race("Humans")

        with patch(
            "game.ui.screens.strategy_detail_fmt.score_planet_for_race",
            return_value=0.047,  # rounds to 5
        ):
            result = format_uncolonized_habitability_for_empire(mock_planet, empire, registry)
        assert "Humans: 5/100" in result

    def test_zero_score_for_uninhabitable_planet(self, mock_planet):
        from unittest.mock import patch
        empire = self._mock_empire({"human"})
        registry = Mock()
        registry.get_race.return_value = self._mock_race("Humans")
        with patch(
            "game.ui.screens.strategy_detail_fmt.score_planet_for_race",
            return_value=0.0,
        ):
            result = format_uncolonized_habitability_for_empire(mock_planet, empire, registry)
        assert "Humans: 0/100" in result


class TestFormatPlanetInfoUncolonizedHabitabilitySection:
    """Tests for how `format_planet_info` integrates the uncolonized
    habitability section. Pin the conditional: only rendered when
    unowned AND empire + registry provided."""

    def test_legacy_call_without_empire_has_no_habitability_section(self, mock_planet):
        mock_planet.owner_id = None
        result = format_planet_info(mock_planet)
        assert "Habitability for your species" not in result

    def test_uncolonized_with_empire_and_registry_appends_section(self, mock_planet):
        from unittest.mock import patch
        mock_planet.owner_id = None
        empire = Mock()
        empire.resident_species.return_value = {"human"}
        race = Mock()
        race.race_name = "Humans"
        race.name = "Humans"
        registry = Mock()
        registry.get_race.return_value = race

        with patch(
            "game.ui.screens.strategy_detail_fmt.score_planet_for_race",
            return_value=0.73,
        ):
            result = format_planet_info(mock_planet, empire=empire, race_registry=registry)
        assert "Habitability for your species" in result
        assert "Humans: 73/100" in result

    def test_colonized_planet_does_not_render_uncolonized_section(self, mock_planet):
        from unittest.mock import patch
        mock_planet.owner_id = 1
        mock_planet.populations = []
        mock_planet.max_population = 0
        mock_planet.facilities = []
        empire = Mock()
        empire.resident_species.return_value = {"human"}
        race = Mock()
        race.race_name = "Humans"
        race.name = "Humans"
        registry = Mock()
        registry.get_race.return_value = race

        with patch(
            "game.ui.screens.strategy_detail_fmt.score_planet_for_race",
            return_value=0.73,
        ):
            result = format_planet_info(mock_planet, empire=empire, race_registry=registry)
        assert "Habitability for your species" not in result

    def test_uncolonized_with_empire_but_no_registry_skips_section(self, mock_planet):
        """Partial deps — missing `race_registry` kwarg → safe no-op, not crash."""
        mock_planet.owner_id = None
        empire = Mock()
        empire.resident_species.return_value = {"human"}
        result = format_planet_info(mock_planet, empire=empire, race_registry=None)
        assert "Habitability for your species" not in result
# ===========================================================================
# PROJ-289 Phase 1: _happiness_category helper
# ===========================================================================

class TestHappinessCategory:
    """Thresholds: happiness >= 1.5 → Content; >= 0.5 → Settled; else Unhappy.

    Boundary test pinned at the inclusive >= cutoff. PROJ-283 base_happiness
    default = 0.5 → "Settled" at baseline. Tunable.
    """

    def test_content_at_threshold(self):
        from game.ui.screens.strategy_detail_fmt import _happiness_category
        assert _happiness_category(1.5) == "Content"

    def test_content_above(self):
        from game.ui.screens.strategy_detail_fmt import _happiness_category
        assert _happiness_category(2.5) == "Content"

    def test_settled_at_baseline(self):
        from game.ui.screens.strategy_detail_fmt import _happiness_category
        assert _happiness_category(0.5) == "Settled"

    def test_settled_just_below_content(self):
        from game.ui.screens.strategy_detail_fmt import _happiness_category
        assert _happiness_category(1.49) == "Settled"

    def test_unhappy_just_below_settled(self):
        from game.ui.screens.strategy_detail_fmt import _happiness_category
        assert _happiness_category(0.49) == "Unhappy"

    def test_unhappy_zero(self):
        from game.ui.screens.strategy_detail_fmt import _happiness_category
        assert _happiness_category(0.0) == "Unhappy"

    def test_unhappy_negative(self):
        from game.ui.screens.strategy_detail_fmt import _happiness_category
        assert _happiness_category(-0.5) == "Unhappy"

    def test_extreme_high(self):
        """HappinessEngine produces [0, 3] so 3.0 must be Content."""
        from game.ui.screens.strategy_detail_fmt import _happiness_category
        assert _happiness_category(3.0) == "Content"


# ===========================================================================
# PROJ-289 Phase 1: per-species sub-block in format_planet_info
# ===========================================================================
#
# When `view: ColonyDemographicView` is passed, `format_planet_info`
# replaces the single-line per-species line with an indented sub-block:
#
#   <b>Humans</b>: 10k [Content]
#       Habitability: 0.94  Happiness: 1.47
#       Growth: +1.2% / turn  Food ratio: 1.00
#       Allocation: 1.00×
#
# When `view is None`, the legacy single-line layout is preserved
# (uncolonized planets, snapshot tests, callers without a facade).

def _make_basic_planet():
    """Minimal mock IPlanet for format_planet_info — only the fields it
    actually reads. Owner_id non-None so we hit the colony branch."""
    p = MagicMock()
    p.name = "Earth"
    p.planet_type = MagicMock()
    p.planet_type.name = "CONTINENTAL"
    p.orbit_distance = 3
    p.mass = 5.97e24
    p.radius = 6.371e6
    p.surface_gravity = 9.81
    p.surface_temperature = 288.0
    p.surface_water = 0.71
    p.total_pressure_atm = 1.0
    p.owner_id = 1
    p.populations = []
    p.max_population = 51_000_000
    p.facilities = []
    p.atmosphere = {}
    p.energy_capacity = 0
    return p


def _make_species_view(race_id, race_name, count, *, habitability=0.9,
                       happiness=1.0, growth_rate=0.02,
                       food_ratio=1.0, food_allocation=1.0,
                       food_surplus=1.0, food_surplus_bonus=0.0):
    from game.strategy.facade.dto.colony_demographic_view import (
        SpeciesDemographicView,
    )
    return SpeciesDemographicView(
        race_id=race_id, race_name=race_name, count=count,
        habitability=habitability, happiness=happiness,
        growth_rate=growth_rate, food_ratio=food_ratio,
        food_allocation=food_allocation,
        food_surplus=food_surplus, food_surplus_bonus=food_surplus_bonus,
    )


def _make_view(species_views, *, planet_id=42, planet_name="Earth"):
    from game.strategy.facade.dto.colony_demographic_view import (
        ColonyDemographicView,
    )
    return ColonyDemographicView(
        planet_id=planet_id,
        planet_name=planet_name,
        species=tuple(species_views),
        resource_projections=(),
        total_upkeep={},
    )


class TestPerSpeciesSubBlock:

    def test_view_none_preserves_legacy_single_line(self):
        """`view=None` (default) keeps the existing single-line per-species
        rendering — backward compat for legacy call sites and tests."""
        from game.ui.screens.strategy_detail_fmt import format_planet_info
        planet = _make_basic_planet()
        pop = MagicMock()
        pop.race_id = "human"
        pop.count = 1000
        pop.happiness = 0.5
        planet.populations = [pop]

        out = format_planet_info(planet)

        # Legacy line uses ` - {race_id}: {count} [...]` pattern.
        assert " - human:" in out
        # Sub-block markers from the new layout must NOT appear.
        assert "Habitability:" not in out
        assert "Growth:" not in out

    def test_view_single_species_renders_sub_block(self):
        from game.ui.screens.strategy_detail_fmt import format_planet_info
        planet = _make_basic_planet()
        pop = MagicMock()
        pop.race_id = "human"; pop.count = 10000; pop.happiness = 1.47
        planet.populations = [pop]
        view = _make_view([_make_species_view(
            "human", "Humans", 10000,
            habitability=0.94, happiness=1.47,
            growth_rate=0.012, food_ratio=1.0, food_allocation=1.0,
        )])

        out = format_planet_info(planet, view=view)

        # Header line: name, count, category
        assert "Humans" in out
        # happiness 1.47 is below the 1.5 "Content" threshold → "Settled".
        assert "[Settled]" in out

    def test_view_single_species_metric_lines(self):
        """Metrics shown to 2 decimals; growth as signed percentage with
        `% / turn` suffix; allocation with `×` suffix."""
        from game.ui.screens.strategy_detail_fmt import format_planet_info
        planet = _make_basic_planet()
        pop = MagicMock()
        pop.race_id = "human"; pop.count = 10000; pop.happiness = 1.47
        planet.populations = [pop]
        view = _make_view([_make_species_view(
            "human", "Humans", 10000,
            habitability=0.94, happiness=1.47,
            growth_rate=0.012, food_ratio=1.00, food_allocation=1.00,
        )])

        out = format_planet_info(planet, view=view)

        assert "Habitability: 0.94" in out
        assert "Happiness: 1.47" in out
        assert "Growth: +1.2% / turn" in out
        assert "Food ratio: 1.00" in out
        assert "Allocation: 1.00×" in out

    def test_view_negative_growth_rendered_with_minus(self):
        from game.ui.screens.strategy_detail_fmt import format_planet_info
        planet = _make_basic_planet()
        pop = MagicMock()
        pop.race_id = "voidari"; pop.count = 3000; pop.happiness = 0.21
        planet.populations = [pop]
        view = _make_view([_make_species_view(
            "voidari", "Voidari", 3000,
            growth_rate=-0.008, happiness=0.21,
        )])

        out = format_planet_info(planet, view=view)

        assert "Growth: -0.8% / turn" in out

    def test_view_multi_species_each_has_sub_block(self):
        from game.ui.screens.strategy_detail_fmt import format_planet_info
        planet = _make_basic_planet()
        # populations on the planet are not used when view is provided —
        # the view's species tuple is the source of truth.
        view = _make_view([
            _make_species_view("human", "Humans", 10000),
            _make_species_view("voidari", "Voidari", 3000),
        ])

        out = format_planet_info(planet, view=view)

        assert "Humans" in out
        assert "Voidari" in out
        # Habitability appears once per species in the sub-block.
        assert out.count("Habitability:") == 2

    def test_view_preserves_ordering_from_species_tuple(self):
        """The DTO is already largest-first per PROJ-288. The renderer
        must NOT re-sort — it iterates `view.species` in tuple order."""
        from game.ui.screens.strategy_detail_fmt import format_planet_info
        planet = _make_basic_planet()
        view = _make_view([
            _make_species_view("big", "BigOnes", 10000),
            _make_species_view("small", "SmallOnes", 50),
        ])

        out = format_planet_info(planet, view=view)

        big_pos = out.index("BigOnes")
        small_pos = out.index("SmallOnes")
        assert big_pos < small_pos

    def test_view_category_label_settled_at_baseline(self):
        """happiness=0.5 → "Settled" per PROJ-283 baseline."""
        from game.ui.screens.strategy_detail_fmt import format_planet_info
        planet = _make_basic_planet()
        view = _make_view([_make_species_view(
            "human", "Humans", 1000, happiness=0.5,
        )])

        out = format_planet_info(planet, view=view)

        assert "[Settled]" in out

    def test_view_category_label_unhappy_when_low(self):
        from game.ui.screens.strategy_detail_fmt import format_planet_info
        planet = _make_basic_planet()
        view = _make_view([_make_species_view(
            "voidari", "Voidari", 1000, happiness=0.2,
        )])

        out = format_planet_info(planet, view=view)

        assert "[Unhappy]" in out

    def test_view_category_label_content_when_high(self):
        from game.ui.screens.strategy_detail_fmt import format_planet_info
        planet = _make_basic_planet()
        view = _make_view([_make_species_view(
            "human", "Humans", 1000, happiness=2.0,
        )])

        out = format_planet_info(planet, view=view)

        assert "[Content]" in out


# ===========================================================================
# FEAT-19: surplus-food line is conditional — only shown when surplus > 1.0
# ===========================================================================

class TestSurplusFoodLine:
    """The "Food surplus: X.XX× → +Y.YY happiness" line is rendered only
    when `food_surplus > 1.0`. At allocation = 1.0× (the default) the
    surplus equals 1.0 and the line is suppressed so single-resource /
    fully-fed-at-1× colonies don't gain a noisy zero-bonus row."""

    def test_no_surplus_line_when_surplus_equals_one(self):
        from game.ui.screens.strategy_detail_fmt import format_planet_info
        planet = _make_basic_planet()
        view = _make_view([_make_species_view(
            "human", "Humans", 1000,
            food_surplus=1.0, food_surplus_bonus=0.0,
        )])

        out = format_planet_info(planet, view=view)

        assert "Food surplus" not in out

    def test_surplus_line_shown_when_surplus_above_one(self):
        """FEAT-19 QA repro values: surplus 1.35× → +0.07 happiness."""
        from game.ui.screens.strategy_detail_fmt import format_planet_info
        planet = _make_basic_planet()
        view = _make_view([_make_species_view(
            "human", "Humans", 1000,
            food_surplus=1.35, food_surplus_bonus=0.07,
        )])

        out = format_planet_info(planet, view=view)

        assert "Food surplus: 1.35×" in out
        assert "+0.07 happiness" in out
