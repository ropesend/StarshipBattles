"""Tests for System and Planet DTOs."""
import pytest
from dataclasses import FrozenInstanceError
from game.core.hex_math import HexCoord


# PROJ-323 Task 3.31: 4 is_frozen tests across StarInfo/WarpPointInfo/SystemInfo/PlanetInfo
# consolidated into one parametrized test.
def _star_info():
    from game.strategy.facade.dto.system_dto import StarInfo
    return StarInfo(
        name="Sol", star_type="MAIN_SEQUENCE",
        color=(255, 255, 200), location=HexCoord(0, 0),
    )


def _warp_point_info():
    from game.strategy.facade.dto.system_dto import WarpPointInfo
    return WarpPointInfo(
        destination_system_name="Proxima", location=HexCoord(5, 5),
    )


def _system_info():
    from game.strategy.facade.dto.system_dto import SystemInfo
    return SystemInfo(
        name="Alpha Centauri", global_location=HexCoord(0, 0),
    )


def _planet_info():
    from game.strategy.facade.dto.planet_dto import PlanetInfo
    return PlanetInfo(
        planet_id=1,
        name="Venus",
        planet_type="CONTINENTAL",
        location=HexCoord(2, 0),
        orbit_distance=2,
    )


@pytest.mark.parametrize("dto_factory,attr,new_value", [
    pytest.param(_star_info, "name", "Proxima", id="StarInfo"),
    pytest.param(_warp_point_info, "destination_system_name", "Sirius", id="WarpPointInfo"),
    pytest.param(_system_info, "name", "Beta Centauri", id="SystemInfo"),
    pytest.param(_planet_info, "name", "Mercury", id="PlanetInfo"),
])
def test_dto_is_frozen(dto_factory, attr, new_value):
    """All DTO frozen dataclasses raise FrozenInstanceError on field mutation."""
    dto = dto_factory()
    with pytest.raises(FrozenInstanceError):
        setattr(dto, attr, new_value)


class TestStarInfo:
    """Tests for StarInfo frozen dataclass."""

    def test_create_star_info(self):
        """StarInfo stores star data correctly."""
        from game.strategy.facade.dto.system_dto import StarInfo

        star = StarInfo(
            name="Alpha Centauri A",
            star_type="MAIN_SEQUENCE",
            color=(255, 200, 150),
            location=HexCoord(0, 0),
        )

        assert star.name == "Alpha Centauri A"
        assert star.star_type == "MAIN_SEQUENCE"
        assert star.color == (255, 200, 150)
        assert star.location == HexCoord(0, 0)


class TestWarpPointInfo:
    """Tests for WarpPointInfo frozen dataclass."""

    def test_create_warp_point_info(self):
        """WarpPointInfo stores warp point data correctly."""
        from game.strategy.facade.dto.system_dto import WarpPointInfo

        warp = WarpPointInfo(
            destination_system_name="Beta Cygni",
            location=HexCoord(15, -8),
        )

        assert warp.destination_system_name == "Beta Cygni"
        assert warp.location == HexCoord(15, -8)


class TestSystemInfo:
    """Tests for SystemInfo frozen dataclass."""

    def test_create_basic_system_info(self):
        """SystemInfo stores system data correctly."""
        from game.strategy.facade.dto.system_dto import SystemInfo

        system = SystemInfo(
            name="Sol",
            global_location=HexCoord(50, 25),
        )

        assert system.name == "Sol"
        assert system.global_location == HexCoord(50, 25)
        assert system.primary_star is None
        assert system.planet_count == 0
        assert system.warp_point_count == 0
        assert system.colony_count == 0

    def test_create_full_system_info(self):
        """SystemInfo can include full star data."""
        from game.strategy.facade.dto.system_dto import SystemInfo, StarInfo

        star = StarInfo(
            name="Sol",
            star_type="MAIN_SEQUENCE",
            color=(255, 255, 200),
            location=HexCoord(0, 0),
        )

        system = SystemInfo(
            name="Sol System",
            global_location=HexCoord(50, 25),
            primary_star=star,
            planet_count=8,
            warp_point_count=2,
            colony_count=1,
        )

        assert system.primary_star is not None
        assert system.primary_star.name == "Sol"
        assert system.planet_count == 8
        assert system.warp_point_count == 2
        assert system.colony_count == 1

class TestSystemInfoFactory:
    """Tests for SystemInfo.from_star_system factory method."""

    def test_from_star_system_basic(self):
        """from_star_system creates DTO from basic StarSystem."""
        from game.strategy.facade.dto.system_dto import SystemInfo
        from game.strategy.data.galaxy import StarSystem

        system = StarSystem(
            name="Test System",
            global_location=HexCoord(10, 5),
        )

        info = SystemInfo.from_star_system(system)

        assert info.name == "Test System"
        assert info.global_location == HexCoord(10, 5)
        assert info.primary_star is None
        assert info.planet_count == 0
        assert info.warp_point_count == 0

    def test_from_star_system_with_star(self):
        """from_star_system includes primary star info."""
        from game.strategy.facade.dto.system_dto import SystemInfo
        from game.strategy.data.galaxy import StarSystem
        from game.strategy.data.stars import Star, StarType, Spectrum

        star = Star(
            name="Alpha",
            mass=1.0,
            radius_hexes=2,
            temperature=5778,
            luminosity=1.0,
            spectrum=Spectrum(0, 0, 0, 0.3, 0.4, 0.3, 0, 0, 0),
            star_type=StarType.MAIN_SEQUENCE,
            color=(255, 255, 200),
            age=4.6e9,
            location=HexCoord(0, 0),
        )

        system = StarSystem(
            name="Alpha System",
            global_location=HexCoord(10, 5),
            stars=[star],
        )

        info = SystemInfo.from_star_system(system)

        assert info.primary_star is not None
        assert info.primary_star.name == "Alpha"
        assert info.primary_star.star_type == "MAIN_SEQUENCE"
        assert info.primary_star.color == (255, 255, 200)

    def test_from_star_system_with_planets(self):
        """from_star_system counts planets correctly."""
        from game.strategy.facade.dto.system_dto import SystemInfo
        from game.strategy.data.galaxy import StarSystem
        from game.strategy.data.planet import Planet, PlanetType

        system = StarSystem(
            name="Test System",
            global_location=HexCoord(10, 5),
        )

        # Add planets
        for i in range(3):
            planet = Planet(
                name=f"Planet {i}",
                location=HexCoord(i + 2, 0),
                orbit_distance=i + 2,
                mass=5.972e24,
                radius=6.371e6,
                surface_area=5.1e14,
                density=5515,
                surface_gravity=9.8,
                surface_pressure=101325,
                surface_temperature=288,
                surface_water=0.7,
                tectonic_activity=0.5,
                magnetic_field=1.0,
                planet_type=PlanetType.CONTINENTAL,
            )
            system.planets.append(planet)

        info = SystemInfo.from_star_system(system)

        assert info.planet_count == 3

    def test_from_star_system_counts_colonies(self):
        """from_star_system counts colonized planets."""
        from game.strategy.facade.dto.system_dto import SystemInfo
        from game.strategy.data.galaxy import StarSystem
        from game.strategy.data.planet import Planet, PlanetType

        system = StarSystem(
            name="Test System",
            global_location=HexCoord(10, 5),
        )

        # Add colonized and uncolonized planets
        for i in range(3):
            planet = Planet(
                name=f"Planet {i}",
                location=HexCoord(i + 2, 0),
                orbit_distance=i + 2,
                mass=5.972e24,
                radius=6.371e6,
                surface_area=5.1e14,
                density=5515,
                surface_gravity=9.8,
                surface_pressure=101325,
                surface_temperature=288,
                surface_water=0.7,
                tectonic_activity=0.5,
                magnetic_field=1.0,
                planet_type=PlanetType.CONTINENTAL,
            )
            if i < 2:  # First two colonized
                planet.owner_id = 0
            system.planets.append(planet)

        info = SystemInfo.from_star_system(system)

        assert info.colony_count == 2

    def test_from_star_system_counts_warp_points(self):
        """from_star_system counts warp points."""
        from game.strategy.facade.dto.system_dto import SystemInfo
        from game.strategy.data.galaxy import StarSystem

        system = StarSystem(
            name="Test System",
            global_location=HexCoord(10, 5),
        )
        system.add_warp_point(1, HexCoord(5, 5))
        system.add_warp_point(2, HexCoord(-5, 5))

        info = SystemInfo.from_star_system(system)

        assert info.warp_point_count == 2


class TestPlanetInfo:
    """Tests for PlanetInfo frozen dataclass."""

    def test_create_planet_info(self):
        """PlanetInfo stores planet data correctly."""
        from game.strategy.facade.dto.planet_dto import PlanetInfo

        planet = PlanetInfo(
            planet_id=42,
            name="Earth",
            planet_type="CONTINENTAL",
            location=HexCoord(3, 0),
            orbit_distance=3,
        )

        assert planet.planet_id == 42
        assert planet.name == "Earth"
        assert planet.planet_type == "CONTINENTAL"
        assert planet.location == HexCoord(3, 0)
        assert planet.orbit_distance == 3
        assert planet.owner_id is None
        assert planet.is_colonized is False
        assert planet.has_space_shipyard is False

    def test_create_colonized_planet(self):
        """PlanetInfo can represent colonized planets."""
        from game.strategy.facade.dto.planet_dto import PlanetInfo

        planet = PlanetInfo(
            planet_id=1,
            name="Mars Colony",
            planet_type="CONTINENTAL",
            location=HexCoord(4, 0),
            orbit_distance=4,
            owner_id=0,
            is_colonized=True,
            has_space_shipyard=True,
        )

        assert planet.owner_id == 0
        assert planet.is_colonized is True
        assert planet.has_space_shipyard is True

class TestPlanetInfoFactory:
    """Tests for PlanetInfo.from_planet factory method."""

    def test_from_planet_basic(self):
        """from_planet creates DTO from basic Planet."""
        from game.strategy.facade.dto.planet_dto import PlanetInfo
        from game.strategy.data.planet import Planet, PlanetType

        planet = Planet(
            name="Test Planet",
            location=HexCoord(5, 0),
            orbit_distance=5,
            mass=5.972e24,
            radius=6.371e6,
            surface_area=5.1e14,
            density=5515,
            surface_gravity=9.8,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.7,
            tectonic_activity=0.5,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL,
        )
        planet.id = 42

        info = PlanetInfo.from_planet(planet)

        assert info.planet_id == 42
        assert info.name == "Test Planet"
        assert info.planet_type == "CONTINENTAL"
        assert info.location == HexCoord(5, 0)
        assert info.orbit_distance == 5
        assert info.owner_id is None
        assert info.is_colonized is False

    def test_from_planet_colonized(self):
        """from_planet handles colonized planets."""
        from game.strategy.facade.dto.planet_dto import PlanetInfo
        from game.strategy.data.planet import Planet, PlanetType

        planet = Planet(
            name="Colony World",
            location=HexCoord(3, 0),
            orbit_distance=3,
            mass=5.972e24,
            radius=6.371e6,
            surface_area=5.1e14,
            density=5515,
            surface_gravity=9.8,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.7,
            tectonic_activity=0.5,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL,
        )
        planet.id = 1
        planet.owner_id = 0

        info = PlanetInfo.from_planet(planet)

        assert info.owner_id == 0
        assert info.is_colonized is True

    def test_from_planet_with_shipyard(self):
        """from_planet detects space shipyard."""
        from game.strategy.facade.dto.planet_dto import PlanetInfo
        from game.strategy.data.planet import Planet, PlanetType
        from game.strategy.data.planetary_facility import PlanetaryFacility

        planet = Planet(
            name="Shipyard World",
            location=HexCoord(3, 0),
            orbit_distance=3,
            mass=5.972e24,
            radius=6.371e6,
            surface_area=5.1e14,
            density=5515,
            surface_gravity=9.8,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.7,
            tectonic_activity=0.5,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL,
        )
        planet.id = 1
        planet.owner_id = 0

        # Add facility with space shipyard
        facility = PlanetaryFacility(
            instance_id="facility-001",
            design_id="orbital_shipyard",
            name="Orbital Shipyard",
            design_data={
                "layers": {
                    "OUTER": [{"id": "space_shipyard"}]
                }
            },
        )
        planet.facilities.append(facility)

        info = PlanetInfo.from_planet(planet)

        assert info.has_space_shipyard is True
