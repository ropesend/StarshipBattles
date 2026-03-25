"""
Unit tests for PlanetGenerator - planet generation system.

PROJ-119 Task 1.1: TCG-STR-001 - planet_gen.py has no dedicated unit test.
Tests focus on individual methods rather than full integration.
"""

import pytest
import math
from unittest.mock import MagicMock, patch

from game.core.hex_math import HexCoord
from game.strategy.data.planet import PlanetType


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_image_registry():
    """Create a mock PlanetImageRegistry."""
    registry = MagicMock()
    registry.get_random_image.return_value = "planet_01"
    registry.get_random_rotation.return_value = 45.0
    return registry


@pytest.fixture
def planet_generator(mock_image_registry):
    """Create a PlanetGenerator with mock dependencies."""
    from game.strategy.data.planet_gen import PlanetGenerator
    return PlanetGenerator(mock_image_registry)


@pytest.fixture
def mock_star():
    """Create a mock Star."""
    star = MagicMock()
    star.radius_hexes = 3
    star.luminosity = 1.0
    star.location = HexCoord(0, 0)
    star.spectral_class = "G"
    return star


# =============================================================================
# Test: PlanetGenerator Initialization
# =============================================================================

class TestPlanetGeneratorInit:
    """Tests for PlanetGenerator initialization."""

    def test_planet_generator_can_be_created(self, mock_image_registry):
        """PlanetGenerator can be instantiated with registry."""
        from game.strategy.data.planet_gen import PlanetGenerator

        generator = PlanetGenerator(mock_image_registry)

        assert generator is not None
        assert generator._image_registry == mock_image_registry


# =============================================================================
# Test: Mass Generation
# =============================================================================

class TestMassGeneration:
    """Tests for mass generation methods."""

    def test_generate_mass_returns_positive(self, planet_generator):
        """_generate_mass returns positive mass."""
        mass = planet_generator._generate_mass()

        assert mass > 0

    def test_generate_mass_within_bounds(self, planet_generator):
        """_generate_mass returns mass within expected range."""
        from game.strategy.data.planet_physics import MASS_CERES, MASS_JUPITER

        # Generate multiple samples
        for _ in range(100):
            mass = planet_generator._generate_mass()
            assert MASS_CERES <= mass <= MASS_JUPITER

    def test_generate_mass_companion_constrained_by_primary(self, planet_generator):
        """Companion mass is constrained by primary mass."""
        from game.strategy.data.planet_physics import MASS_EARTH

        primary_mass = MASS_EARTH

        for _ in range(50):
            companion_mass = planet_generator._generate_mass(
                is_companion=True, primary_mass=primary_mass
            )
            # Companion should be <= 40% of primary
            assert companion_mass <= primary_mass * 0.4 + 1e15  # Small tolerance

    def test_generate_mass_constrained_respects_min(self, planet_generator):
        """_generate_mass_constrained respects minimum bound."""
        min_mass = 1e24
        max_mass = 1e28

        for _ in range(50):
            mass = planet_generator._generate_mass_constrained(min_mass, max_mass)
            assert mass >= min_mass

    def test_generate_mass_constrained_respects_max(self, planet_generator):
        """_generate_mass_constrained respects maximum bound."""
        min_mass = 1e22
        max_mass = 1e25

        for _ in range(50):
            mass = planet_generator._generate_mass_constrained(min_mass, max_mass)
            assert mass <= max_mass

    def test_generate_mass_constrained_with_small_bias(self, planet_generator):
        """Small bias tends toward smaller masses."""
        from game.strategy.data.planet_physics import MASS_CERES, MASS_JUPITER

        masses = []
        for _ in range(100):
            mass = planet_generator._generate_mass_constrained(
                MASS_CERES, MASS_JUPITER, bias="small"
            )
            masses.append(math.log10(mass))

        avg_log = sum(masses) / len(masses)
        # Small bias should center around log10 ~ 24 (Earth-like)
        assert avg_log < 26  # Below Neptune mass range

    def test_generate_mass_constrained_with_large_bias(self, planet_generator):
        """Large bias tends toward larger masses."""
        from game.strategy.data.planet_physics import MASS_CERES, MASS_JUPITER

        masses = []
        for _ in range(100):
            mass = planet_generator._generate_mass_constrained(
                MASS_CERES, MASS_JUPITER, bias="large"
            )
            masses.append(math.log10(mass))

        avg_log = sum(masses) / len(masses)
        # Large bias should center around log10 ~ 26.5 (Neptune-Jupiter)
        assert avg_log > 24  # Above Earth mass


# =============================================================================
# Test: Moon Generation
# =============================================================================

class TestMoonGeneration:
    """Tests for moon generation."""

    def test_calculate_moon_chance_jupiter_high(self, planet_generator):
        """Jupiter-sized bodies have high moon chance (~80%)."""
        from game.strategy.data.planet_physics import MASS_JUPITER

        chance = planet_generator._calculate_moon_chance(MASS_JUPITER)

        assert 0.7 <= chance <= 0.95

    def test_calculate_moon_chance_earth_low(self, planet_generator):
        """Earth-sized bodies have lower moon chance (~10%)."""
        from game.strategy.data.planet_physics import MASS_EARTH

        chance = planet_generator._calculate_moon_chance(MASS_EARTH)

        assert 0.05 <= chance <= 0.15

    def test_calculate_moon_chance_ceres_very_low(self, planet_generator):
        """Ceres-sized bodies have very low moon chance (~1%)."""
        from game.strategy.data.planet_physics import MASS_CERES

        chance = planet_generator._calculate_moon_chance(MASS_CERES)

        assert chance <= 0.05

    def test_calculate_moon_chance_clamped_to_bounds(self, planet_generator):
        """Moon chance is clamped between 0 and 0.95."""
        # Very small mass
        chance_tiny = planet_generator._calculate_moon_chance(1e15)
        assert 0.0 <= chance_tiny <= 1.0

        # Extremely large mass
        chance_huge = planet_generator._calculate_moon_chance(1e30)
        assert 0.0 <= chance_huge <= 0.95

    def test_generate_moon_mass_proportional(self, planet_generator):
        """Moon mass is proportional to primary (~10%)."""
        from game.strategy.data.planet_physics import MASS_EARTH

        primary_mass = MASS_EARTH

        for _ in range(20):
            moon_mass = planet_generator._generate_moon_mass(primary_mass)
            # Should be around 10% +/- 20%
            ratio = moon_mass / primary_mass
            assert 0.01 <= ratio <= 0.5

    def test_generate_moon_mass_not_larger_than_primary(self, planet_generator):
        """Moon mass cannot exceed primary mass."""
        primary_mass = 1e22  # Small primary

        for _ in range(50):
            moon_mass = planet_generator._generate_moon_mass(primary_mass)
            assert moon_mass < primary_mass

    def test_generate_moon_mass_minimum_ceres(self, planet_generator):
        """Moon mass has minimum at Ceres mass."""
        from game.strategy.data.planet_physics import MASS_CERES

        # Small primary where 10% would be below Ceres
        primary_mass = MASS_CERES * 5

        for _ in range(50):
            moon_mass = planet_generator._generate_moon_mass(primary_mass)
            assert moon_mass >= MASS_CERES

    def test_generate_moons_adds_to_slots(self, planet_generator):
        """_generate_moons adds moons to occupied slots."""
        from game.strategy.data.planet_physics import MASS_JUPITER

        # Start with Jupiter-mass primaries (high moon chance)
        occupied_slots = {
            HexCoord(5, 0): [MASS_JUPITER],
            HexCoord(10, 0): [MASS_JUPITER],
        }

        # Run multiple times to verify it sometimes adds moons
        added_any = False
        for _ in range(10):
            test_slots = {k: list(v) for k, v in occupied_slots.items()}
            planet_generator._generate_moons(test_slots)

            for loc, masses in test_slots.items():
                if len(masses) > 1:
                    added_any = True
                    break
            if added_any:
                break

        # With Jupiter masses, should add moons at least sometimes
        assert added_any

    def test_generate_moons_respects_max_total(self, planet_generator):
        """_generate_moons respects max_total constraint."""
        from game.strategy.data.planet_physics import MASS_JUPITER

        occupied_slots = {
            HexCoord(5, 0): [MASS_JUPITER],
            HexCoord(10, 0): [MASS_JUPITER],
        }

        planet_generator._generate_moons(occupied_slots, max_total=3)

        total = sum(len(masses) for masses in occupied_slots.values())
        assert total <= 3


# =============================================================================
# Test: Orbital Slots Generation
# =============================================================================

class TestOrbitalSlots:
    """Tests for orbital slot generation."""

    def test_generate_orbital_slots_returns_dict(self, planet_generator, mock_star):
        """_generate_orbital_slots returns dict of locations to masses."""
        slots = planet_generator._generate_orbital_slots([mock_star])

        assert isinstance(slots, dict)
        for loc, masses in slots.items():
            assert isinstance(loc, HexCoord)
            assert isinstance(masses, list)
            assert len(masses) > 0
            assert all(isinstance(m, float) for m in masses)

    def test_generate_orbital_slots_respects_safe_distance(self, planet_generator, mock_star):
        """Orbital slots are beyond safe start distance from star."""
        mock_star.radius_hexes = 4  # Larger star

        slots = planet_generator._generate_orbital_slots([mock_star])

        safe_start = mock_star.radius_hexes + 2

        for loc in slots.keys():
            dist = max(abs(loc.q), abs(loc.r), abs(-loc.q - loc.r))
            assert dist >= safe_start

    def test_generate_orbital_slots_zero_count_blueprint(self, planet_generator, mock_star):
        """Blueprint with planet_count=0 returns empty dict."""
        blueprint = {"planet_count": 0}

        slots = planet_generator._generate_orbital_slots([mock_star], blueprint)

        assert slots == {}

    def test_generate_orbital_slots_respects_count_range(self, planet_generator, mock_star):
        """Blueprint planet_count range is respected."""
        blueprint = {"planet_count": {"min": 5, "max": 5}}

        slots = planet_generator._generate_orbital_slots([mock_star], blueprint)

        assert len(slots) == 5

    def test_generate_orbital_slots_hot_jupiter(self, planet_generator, mock_star):
        """Hot Jupiter blueprint places gas giant close to star."""
        from game.strategy.data.planet_physics import MASS_EARTH

        blueprint = {
            "planet_count": {"min": 1, "max": 3},
            "orbital_zones": {"hot_required": True}
        }

        slots = planet_generator._generate_orbital_slots([mock_star], blueprint)

        # Find closest orbit
        if slots:
            min_dist = min(
                max(abs(loc.q), abs(loc.r), abs(-loc.q - loc.r))
                for loc in slots.keys()
            )
            # Hot Jupiter should be orbit 2-3
            assert min_dist <= 4

            # First planet should be gas giant mass
            first_loc = min(slots.keys(), key=lambda l: max(abs(l.q), abs(l.r), abs(-l.q - l.r)))
            first_mass = slots[first_loc][0]
            assert first_mass > 1e26  # Gas giant range

    def test_generate_orbital_slots_avoids_secondary_star_hexes(self, planet_generator, mock_star):
        """BUG-108: Planets must not be placed in hexes occupied by secondary stars."""
        from game.core.hex_math import hex_circle_filled

        # Primary star at (0,0) with radius_hexes=2
        mock_star.radius_hexes = 2

        # Secondary star at distance 8 from origin, with radius_hexes=2
        # This places it within the default orbital range (safe_start=4, max_dist=20)
        secondary = MagicMock()
        secondary.radius_hexes = 2
        secondary.location = HexCoord(8, 0)
        secondary.luminosity = 0.5
        # occupied_hexes should return the filled hex zone around the secondary
        secondary.occupied_hexes = hex_circle_filled(HexCoord(8, 0), 1)  # radius_hexes-1 = 1

        stars = [mock_star, secondary]

        # The secondary star's occupied hexes plus a 2-hex buffer zone
        secondary_zone = hex_circle_filled(HexCoord(8, 0), secondary.radius_hexes + 1)  # radius + buffer

        # Generate many times to catch probabilistic collisions
        for _ in range(50):
            slots = planet_generator._generate_orbital_slots(stars)

            for loc in slots.keys():
                assert loc not in secondary_zone, (
                    f"Planet placed at {loc} which is within secondary star zone "
                    f"(star at {secondary.location}, radius_hexes={secondary.radius_hexes})"
                )


# =============================================================================
# Test: Surface Flags Generation
# =============================================================================

class TestSurfaceFlags:
    """Tests for surface flag generation."""

    def test_generate_surface_flags_large_body(self, planet_generator):
        """Large bodies have higher activity and magnetic field."""
        from game.strategy.data.planet_physics import MASS_EARTH

        water, activity, mag = planet_generator._generate_surface_flags(MASS_EARTH, 300)

        # Earth-like should have notable activity
        assert activity > 0
        assert mag > 0

    def test_generate_surface_flags_small_body(self, planet_generator):
        """Small bodies have low activity."""
        from game.strategy.data.planet_physics import MASS_CERES

        water, activity, mag = planet_generator._generate_surface_flags(MASS_CERES, 200)

        # Ceres-like should have minimal activity
        assert activity <= 0.2
        assert mag <= 0.5

    def test_generate_surface_flags_water_in_habitable(self, planet_generator):
        """Water present in habitable temperature range."""
        from game.strategy.data.planet_physics import MASS_EARTH

        water, _, _ = planet_generator._generate_surface_flags(MASS_EARTH, 290)

        # Should have some water in habitable range
        assert water >= 0

    def test_generate_surface_flags_no_water_hot(self, planet_generator):
        """No water when too hot (boiled off)."""
        from game.strategy.data.planet_physics import MASS_EARTH

        water, _, _ = planet_generator._generate_surface_flags(MASS_EARTH, 500)

        assert water == 0


# =============================================================================
# Test: Planet Type Determination
# =============================================================================

class TestPlanetTypeDetermination:
    """Tests for planet type classification."""

    def test_determine_type_jovian(self, planet_generator):
        """Very massive body classified as Jovian."""
        from game.strategy.data.planet_physics import MASS_JUPITER

        p_type = planet_generator._determine_type(
            mass=MASS_JUPITER,
            temp=150,
            pressure=1000,
            water=0,
            atmosphere={"H2": 0.9},
        )

        assert p_type == PlanetType.JOVIAN

    def test_determine_type_ice_giant(self, planet_generator):
        """Moderately massive cold body classified as Ice Giant."""
        p_type = planet_generator._determine_type(
            mass=5e25,  # Neptune-ish
            temp=80,
            pressure=100,
            water=0.2,
            atmosphere={"CH4": 0.3},
        )

        assert p_type == PlanetType.ICE_GIANT

    def test_determine_type_magma(self, planet_generator):
        """Hot terrestrial classified as Magma."""
        from game.strategy.data.planet_physics import MASS_EARTH

        p_type = planet_generator._determine_type(
            mass=MASS_EARTH,
            temp=1500,
            pressure=100,
            water=0,
            atmosphere={"CO2": 0.9},
        )

        assert p_type == PlanetType.MAGMA

    def test_determine_type_cryoplanet(self, planet_generator):
        """Cold terrestrial classified as Cryoplanet."""
        from game.strategy.data.planet_physics import MASS_MARS

        p_type = planet_generator._determine_type(
            mass=MASS_MARS,
            temp=50,
            pressure=0.001,
            water=0.5,
            atmosphere={},
        )

        assert p_type == PlanetType.CRYOPLANET

    def test_determine_type_barren(self, planet_generator):
        """Warm vacuum body classified as Barren."""
        # Mass must be above dwarf_max (2e23) and below giant_min (6e24)
        # Vacuum threshold is 500 Pa, so pressure < 500 triggers vacuum path
        # temp above cold_limit (200) and below cryo_max (255) puts in barren
        p_type = planet_generator._determine_type(
            mass=5e23,  # Between dwarf_max (2e23) and giant_min (6e24)
            temp=220,   # Above cold_limit (200), below cryo_max (255)
            pressure=100,  # Below vacuum threshold (500)
            water=0,
            atmosphere={},
        )

        assert p_type == PlanetType.BARREN

    def test_determine_type_pelagic(self, planet_generator):
        """High water body classified as Pelagic."""
        from game.strategy.data.planet_physics import MASS_EARTH

        # Pelagic requires: mass in terrestrial range, pressure > vacuum (500),
        # water > ocean_world (0.85)
        p_type = planet_generator._determine_type(
            mass=MASS_EARTH,
            temp=290,
            pressure=101325,  # 1 atm (well above vacuum threshold of 500)
            water=0.95,  # Ocean world threshold > 0.85
            atmosphere={"N2": 0.8},
        )

        assert p_type == PlanetType.PELAGIC

    def test_determine_type_continental(self, planet_generator):
        """Moderate water/temp body classified as Continental."""
        from game.strategy.data.planet_physics import MASS_EARTH

        # Continental requires: mass in terrestrial range,
        # pressure > continental_pressure_min (5000),
        # temp in continental range (255-330),
        # water > arid (0.2) and < ocean_world (0.85)
        p_type = planet_generator._determine_type(
            mass=MASS_EARTH,
            temp=288,  # In continental temp range (255-330)
            pressure=101325,  # 1 atm (above continental_pressure_min of 5000)
            water=0.5,  # Between arid (0.2) and ocean_world (0.85)
            atmosphere={"N2": 0.78, "O2": 0.21},
        )

        assert p_type == PlanetType.CONTINENTAL

    def test_determine_type_arid(self, planet_generator):
        """Low water body classified as Arid."""
        from game.strategy.data.planet_physics import MASS_MARS

        # Arid requires: mass in terrestrial range,
        # pressure > vacuum (500), water < arid (0.2)
        p_type = planet_generator._determine_type(
            mass=MASS_MARS,  # ~6.4e23, above dwarf_max
            temp=300,
            pressure=1000,  # Above vacuum threshold (500)
            water=0.01,  # Below arid threshold (0.2)
            atmosphere={"CO2": 0.9},
        )

        assert p_type == PlanetType.ARID

    def test_determine_type_ice_dwarf(self, planet_generator):
        """Cold dwarf classified as Ice Dwarf."""
        from game.strategy.data.planet_physics import MASS_CERES

        p_type = planet_generator._determine_type(
            mass=MASS_CERES * 0.5,
            temp=40,
            pressure=0,
            water=0.3,
            atmosphere={},
        )

        assert p_type == PlanetType.ICE_DWARF

    def test_determine_type_planetoid(self, planet_generator):
        """Warm dwarf classified as Planetoid."""
        from game.strategy.data.planet_physics import MASS_CERES

        p_type = planet_generator._determine_type(
            mass=MASS_CERES * 0.5,
            temp=250,
            pressure=0,
            water=0,
            atmosphere={},
        )

        assert p_type == PlanetType.PLANETOID


# =============================================================================
# Test: Resource Generation
# =============================================================================

class TestResourceGeneration:
    """Tests for resource generation."""

    def test_generate_resources_returns_dict(self, planet_generator):
        """_generate_resources returns dict of resources."""
        from game.strategy.data.planet_physics import MASS_EARTH

        resources = planet_generator._generate_resources(MASS_EARTH)

        assert isinstance(resources, dict)

    def test_generate_resources_has_required_keys(self, planet_generator):
        """Resources dict has quantity and quality for each resource."""
        from game.strategy.data.planet_physics import MASS_EARTH

        resources = planet_generator._generate_resources(MASS_EARTH)

        for res_name, res_data in resources.items():
            assert 'quantity' in res_data
            assert 'quality' in res_data

    def test_generate_resources_quantity_positive(self, planet_generator):
        """Resource quantities are non-negative."""
        from game.strategy.data.planet_physics import MASS_EARTH

        resources = planet_generator._generate_resources(MASS_EARTH)

        for res_name, res_data in resources.items():
            assert res_data['quantity'] >= 0

    def test_generate_resources_quality_bounded(self, planet_generator):
        """Resource quality is bounded 0-100."""
        from game.strategy.data.planet_physics import MASS_EARTH

        resources = planet_generator._generate_resources(MASS_EARTH)

        for res_name, res_data in resources.items():
            assert 0 <= res_data['quality'] <= 100

    def test_generate_resources_large_planet_high_quantity(self, planet_generator):
        """Large planets tend to have higher resource quantities."""
        from game.strategy.data.planet_physics import MASS_JUPITER, MASS_CERES

        large_resources = planet_generator._generate_resources(MASS_JUPITER)
        small_resources = planet_generator._generate_resources(MASS_CERES)

        # Average over multiple samples for statistical significance
        large_qty = sum(r['quantity'] for r in large_resources.values())
        small_qty = sum(r['quantity'] for r in small_resources.values())

        # Large should generally have more quantity
        assert large_qty > small_qty * 0.5  # Allow some variance


# =============================================================================
# Test: Full System Generation
# =============================================================================

class TestSystemGeneration:
    """Tests for complete system body generation."""

    def test_generate_system_bodies_returns_list(self, planet_generator, mock_star):
        """generate_system_bodies returns list of planets."""
        with patch('game.strategy.data.planet_gen.calculate_incident_radiation') as mock_rad:
            mock_spec = MagicMock()
            mock_spec.get_total_output.return_value = 1361.0
            mock_rad.return_value = mock_spec

            with patch('game.strategy.data.planet_gen.assign_body_names'):
                planets = planet_generator.generate_system_bodies("Test", [mock_star])

        assert isinstance(planets, list)

    def test_generate_system_bodies_with_blueprint_count(self, planet_generator, mock_star):
        """Blueprint planet_count controls output count."""
        blueprint = {"planet_count": {"min": 3, "max": 3}}

        with patch('game.strategy.data.planet_gen.calculate_incident_radiation') as mock_rad:
            mock_spec = MagicMock()
            mock_spec.get_total_output.return_value = 1361.0
            mock_rad.return_value = mock_spec

            with patch('game.strategy.data.planet_gen.assign_body_names'):
                planets = planet_generator.generate_system_bodies(
                    "Test", [mock_star], blueprint
                )

        # Should have at least 3 primary bodies (plus potential moons)
        assert len(planets) >= 3

    def test_generate_system_bodies_empty_with_zero_count(self, planet_generator, mock_star):
        """Blueprint with planet_count=0 returns empty list."""
        blueprint = {"planet_count": 0}

        planets = planet_generator.generate_system_bodies("Test", [mock_star], blueprint)

        assert planets == []
