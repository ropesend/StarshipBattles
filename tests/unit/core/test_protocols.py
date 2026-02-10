"""
Tests for game.core.protocols module.

Tests the Protocol definitions and TypeGuard functions for type-safe
duck typing replacement.
"""

import pytest


class TestProtocolExistence:
    """Verify that all expected Protocols exist and are importable."""

    def test_import_all_protocols(self):
        """All Protocols should be importable from protocols module."""
        from game.core.protocols import (
            ILocatable,
            INamed,
            IOwnable,
            IStarSystem,
            IStar,
            IPlanet,
            IFleet,
            IWarpPoint,
            ISectorEnvironment,
            ICombatant,
            IDamageable,
        )
        # If we get here, all imports succeeded
        assert IStarSystem is not None
        assert IStar is not None
        assert IPlanet is not None
        assert IFleet is not None
        assert IWarpPoint is not None
        assert ISectorEnvironment is not None
        assert ICombatant is not None

    def test_import_all_typeguards(self):
        """All TypeGuard functions should be importable."""
        from game.core.protocols import (
            is_star_system,
            is_star,
            is_planet,
            is_fleet,
            is_warp_point,
            is_sector_environment,
            is_combatant,
        )
        assert callable(is_star_system)
        assert callable(is_star)
        assert callable(is_planet)
        assert callable(is_fleet)
        assert callable(is_warp_point)
        assert callable(is_sector_environment)
        assert callable(is_combatant)


class TestProtocolsWithRealClasses:
    """Test that real game classes satisfy the Protocols."""

    def test_fleet_satisfies_ifleet(self):
        """Fleet class should satisfy IFleet Protocol."""
        from game.core.protocols import IFleet
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        assert isinstance(fleet, IFleet)

    def test_planet_satisfies_iplanet(self):
        """Planet class should satisfy IPlanet Protocol."""
        from game.core.protocols import IPlanet
        from game.strategy.data.planet import Planet, PlanetType
        from game.core.hex_math import HexCoord

        planet = Planet(
            name="Test Planet",
            location=HexCoord(1, 1),
            orbit_distance=3,
            mass=5.972e24,
            radius=6371000,
            surface_area=5.1e14,
            density=5515,
            surface_gravity=9.8,
            surface_pressure=101325,
            surface_temperature=288,
            surface_water=0.71,
            tectonic_activity=0.5,
            magnetic_field=1.0,
            planet_type=PlanetType.CONTINENTAL,
        )
        assert isinstance(planet, IPlanet)

    def test_star_system_satisfies_istarsystem(self):
        """StarSystem class should satisfy IStarSystem Protocol."""
        from game.core.protocols import IStarSystem
        from game.strategy.data.galaxy import StarSystem
        from game.core.hex_math import HexCoord

        system = StarSystem(name="Sol", global_location=HexCoord(0, 0))
        assert isinstance(system, IStarSystem)

    def test_star_satisfies_istar(self):
        """Star class should satisfy IStar Protocol."""
        from game.core.protocols import IStar
        from game.strategy.data.stars import Star, StarType, Spectrum
        from game.core.hex_math import HexCoord

        spectrum = Spectrum(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
        star = Star(
            name="Sun",
            mass=1.0,
            diameter_hexes=1.0,
            temperature=5778,
            luminosity=1.0,
            spectrum=spectrum,
            star_type=StarType.MAIN_SEQUENCE,
            color=(255, 255, 200),
            age=4.6e9,
            location=HexCoord(0, 0),
        )
        assert isinstance(star, IStar)

    def test_warp_point_satisfies_iwarppoint(self):
        """WarpPoint class should satisfy IWarpPoint Protocol."""
        from game.core.protocols import IWarpPoint
        from game.strategy.data.galaxy import WarpPoint
        from game.core.hex_math import HexCoord

        wp = WarpPoint(destination_id="Alpha Centauri", location=HexCoord(5, 3))
        assert isinstance(wp, IWarpPoint)

    def test_sector_environment_satisfies_isectorenvironment(self):
        """SectorEnvironment class should satisfy ISectorEnvironment Protocol."""
        from game.core.protocols import ISectorEnvironment
        from game.strategy.data.physics import SectorEnvironment
        from game.strategy.data.galaxy import StarSystem
        from game.core.hex_math import HexCoord

        system = StarSystem(name="Sol", global_location=HexCoord(0, 0))
        sector = SectorEnvironment(local_hex=HexCoord(3, 2), system=system)
        assert isinstance(sector, ISectorEnvironment)


class TestTypeGuardFunctions:
    """Test TypeGuard functions return correct boolean values."""

    def test_is_fleet_returns_true_for_fleet(self):
        """is_fleet should return True for Fleet instances."""
        from game.core.protocols import is_fleet
        from game.strategy.data.fleet import Fleet
        from game.core.hex_math import HexCoord

        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        assert is_fleet(fleet) is True

    def test_is_fleet_returns_false_for_non_fleet(self):
        """is_fleet should return False for non-Fleet objects."""
        from game.core.protocols import is_fleet

        assert is_fleet("not a fleet") is False
        assert is_fleet(123) is False
        assert is_fleet({"ships": []}) is False

    def test_is_planet_returns_true_for_planet(self):
        """is_planet should return True for Planet instances."""
        from game.core.protocols import is_planet
        from game.strategy.data.planet import Planet, PlanetType
        from game.core.hex_math import HexCoord

        planet = Planet(
            name="Test",
            location=HexCoord(0, 0),
            orbit_distance=1,
            mass=1e24,
            radius=6e6,
            surface_area=5e14,
            density=5000,
            surface_gravity=10,
            surface_pressure=100000,
            surface_temperature=290,
            surface_water=0.5,
            tectonic_activity=0.3,
            magnetic_field=0.8,
        )
        assert is_planet(planet) is True

    def test_is_planet_returns_false_for_non_planet(self):
        """is_planet should return False for non-Planet objects."""
        from game.core.protocols import is_planet

        assert is_planet("not a planet") is False
        assert is_planet(None) is False

    def test_is_star_system_returns_true_for_system(self):
        """is_star_system should return True for StarSystem instances."""
        from game.core.protocols import is_star_system
        from game.strategy.data.galaxy import StarSystem
        from game.core.hex_math import HexCoord

        system = StarSystem(name="Sol", global_location=HexCoord(0, 0))
        assert is_star_system(system) is True

    def test_is_star_system_returns_false_for_non_system(self):
        """is_star_system should return False for non-StarSystem objects."""
        from game.core.protocols import is_star_system

        assert is_star_system("Sol") is False
        assert is_star_system(None) is False

    def test_is_star_returns_true_for_star(self):
        """is_star should return True for Star instances."""
        from game.core.protocols import is_star
        from game.strategy.data.stars import Star, StarType, Spectrum
        from game.core.hex_math import HexCoord

        spectrum = Spectrum(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
        star = Star(
            name="Sun",
            mass=1.0,
            diameter_hexes=1.0,
            temperature=5778,
            luminosity=1.0,
            spectrum=spectrum,
            star_type=StarType.MAIN_SEQUENCE,
            color=(255, 255, 200),
            age=4.6e9,
        )
        assert is_star(star) is True

    def test_is_star_returns_false_for_non_star(self):
        """is_star should return False for non-Star objects."""
        from game.core.protocols import is_star

        assert is_star("Sun") is False

    def test_is_warp_point_returns_true_for_warppoint(self):
        """is_warp_point should return True for WarpPoint instances."""
        from game.core.protocols import is_warp_point
        from game.strategy.data.galaxy import WarpPoint
        from game.core.hex_math import HexCoord

        wp = WarpPoint(destination_id="Alpha", location=HexCoord(1, 1))
        assert is_warp_point(wp) is True

    def test_is_warp_point_returns_false_for_non_warppoint(self):
        """is_warp_point should return False for non-WarpPoint objects."""
        from game.core.protocols import is_warp_point

        assert is_warp_point("Alpha") is False

    def test_is_sector_environment_returns_true_for_sector(self):
        """is_sector_environment should return True for SectorEnvironment."""
        from game.core.protocols import is_sector_environment
        from game.strategy.data.physics import SectorEnvironment
        from game.strategy.data.galaxy import StarSystem
        from game.core.hex_math import HexCoord

        system = StarSystem(name="Sol", global_location=HexCoord(0, 0))
        sector = SectorEnvironment(local_hex=HexCoord(1, 1), system=system)
        assert is_sector_environment(sector) is True

    def test_is_sector_environment_returns_false_for_non_sector(self):
        """is_sector_environment should return False for non-SectorEnvironment."""
        from game.core.protocols import is_sector_environment

        assert is_sector_environment({}) is False


class TestNoneSafety:
    """Test that Protocols and TypeGuards handle None safely."""

    def test_none_does_not_satisfy_any_protocol(self):
        """None should not satisfy any Protocol."""
        from game.core.protocols import (
            IFleet, IPlanet, IStarSystem, IStar, IWarpPoint, ISectorEnvironment
        )

        assert not isinstance(None, IFleet)
        assert not isinstance(None, IPlanet)
        assert not isinstance(None, IStarSystem)
        assert not isinstance(None, IStar)
        assert not isinstance(None, IWarpPoint)
        assert not isinstance(None, ISectorEnvironment)

    def test_typeguards_return_false_for_none(self):
        """All TypeGuard functions should return False for None."""
        from game.core.protocols import (
            is_fleet,
            is_planet,
            is_star_system,
            is_star,
            is_warp_point,
            is_sector_environment,
            is_combatant,
        )

        assert is_fleet(None) is False
        assert is_planet(None) is False
        assert is_star_system(None) is False
        assert is_star(None) is False
        assert is_warp_point(None) is False
        assert is_sector_environment(None) is False
        assert is_combatant(None) is False


class TestRuntimeCheckable:
    """Verify that Protocols are runtime_checkable."""

    def test_protocols_are_runtime_checkable(self):
        """All Protocols should have @runtime_checkable decorator."""
        from typing import runtime_checkable
        from game.core.protocols import (
            IFleet, IPlanet, IStarSystem, IStar, IWarpPoint,
            ISectorEnvironment, ICombatant
        )

        # If Protocol is runtime_checkable, isinstance() should work without error
        # Just calling isinstance with a non-matching object should not raise
        try:
            isinstance("test", IFleet)
            isinstance("test", IPlanet)
            isinstance("test", IStarSystem)
            isinstance("test", IStar)
            isinstance("test", IWarpPoint)
            isinstance("test", ISectorEnvironment)
            isinstance("test", ICombatant)
        except TypeError as e:
            pytest.fail(f"Protocol is not runtime_checkable: {e}")
