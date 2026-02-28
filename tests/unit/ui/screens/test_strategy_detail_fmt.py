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
    star.diameter_hexes = 2.5
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

    def test_generic_order_type(self, mock_fleet):
        """Test generic order type fallback (superweapon orders)."""
        order = Mock()
        order.type = OrderType.IMPLODE_PLANET
        order.target = (10, 20)  # target hex
        mock_fleet.orders = [order]

        result = _format_orders(mock_fleet)

        assert "1. IMPLODE_PLANET" in result

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

        assert "5K" in result or "6K" in result  # Rounding

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
        assert "Diam:" in result
        assert "2.5 Hex" in result
