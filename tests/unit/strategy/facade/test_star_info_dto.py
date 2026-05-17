"""Tests for StarInfo DTO enrichment and facade star queries (PROJ-231)."""
import pytest
from unittest.mock import MagicMock
from game.core.hex_math import HexCoord
from game.strategy.data.spectrum import Spectrum
from game.strategy.data.stars import Star, StarType
from game.strategy.facade.dto.system_dto import StarInfo, SystemInfo
from game.strategy.facade.strategy_session_facade import StrategySessionFacade


def _make_spectrum(**overrides):
    """Create a Spectrum with default values, optionally overriding specific bands."""
    defaults = dict(
        gamma_ray=0.001, xray=0.01, ultraviolet=0.1, blue=0.3,
        green=0.4, red=0.35, infrared=0.5, microwave=0.02, radio=0.005,
    )
    defaults.update(overrides)
    return Spectrum(**defaults)


def _make_star(name="Sol", star_type=StarType.MAIN_SEQUENCE, mass=1.0,
               temperature=5778.0, luminosity=1.0, age=4.6e9,
               radius_hexes=2, spectrum=None, color=(255, 200, 50),
               location=None):
    """Create a Star domain object with sensible defaults."""
    return Star(
        name=name,
        mass=mass,
        radius_hexes=radius_hexes,
        temperature=temperature,
        luminosity=luminosity,
        spectrum=spectrum or _make_spectrum(),
        star_type=star_type,
        color=color,
        age=age,
        location=location or HexCoord(0, 0),
    )


class TestStarInfoFromStar:
    """Test StarInfo.from_star() with enriched fields."""

    def test_basic_fields_preserved(self):
        """Original fields (name, star_type, color, location) still work."""
        star = _make_star(name="Alpha", color=(100, 200, 255))
        info = StarInfo.from_star(star)

        assert info.name == "Alpha"
        assert info.star_type == "MAIN_SEQUENCE"
        assert info.color == (100, 200, 255)
        assert info.location == HexCoord(0, 0)

    def test_physical_attributes(self):
        """New physical attributes are populated from star domain object."""
        star = _make_star(mass=2.5, temperature=8000.0, luminosity=15.0,
                          age=1.2e9, radius_hexes=4)
        info = StarInfo.from_star(star)

        assert info.mass == 2.5
        assert info.temperature == 8000.0
        assert info.luminosity == 15.0
        assert info.age == 1.2e9
        assert info.radius_hexes == 4

    def test_spectrum_fields_flattened(self):
        """Spectrum bands are flattened into individual StarInfo fields."""
        spectrum = Spectrum(
            gamma_ray=0.001, xray=0.01, ultraviolet=0.1, blue=0.3,
            green=0.4, red=0.35, infrared=0.5, microwave=0.02, radio=0.005,
        )
        star = _make_star(spectrum=spectrum)
        info = StarInfo.from_star(star)

        assert info.spectrum_gamma_ray == 0.001
        assert info.spectrum_xray == 0.01
        assert info.spectrum_ultraviolet == 0.1
        assert info.spectrum_blue == 0.3
        assert info.spectrum_green == 0.4
        assert info.spectrum_red == 0.35
        assert info.spectrum_infrared == 0.5
        assert info.spectrum_microwave == 0.02
        assert info.spectrum_radio == 0.005

    def test_system_context_with_defaults(self):
        """Without system context kwargs, defaults are used."""
        star = _make_star()
        info = StarInfo.from_star(star)

        assert info.system_name == ""
        assert info.system_global_location is None
        assert info.planet_count == 0
        assert info.companion_star_count == 0

    def test_system_context_with_values(self):
        """System context kwargs are populated in the DTO."""
        star = _make_star()
        loc = HexCoord(10, 20)
        info = StarInfo.from_star(
            star,
            system_name="Alpha System",
            system_global_location=loc,
            planet_count=5,
            total_star_count=3,
        )

        assert info.system_name == "Alpha System"
        assert info.system_global_location == loc
        assert info.planet_count == 5
        assert info.companion_star_count == 2  # total_star_count - 1

    def test_single_star_system_companion_count(self):
        """A single-star system has 0 companions."""
        star = _make_star()
        info = StarInfo.from_star(star, total_star_count=1)
        assert info.companion_star_count == 0

    def test_dto_is_frozen(self):
        """StarInfo should be immutable (frozen dataclass)."""
        star = _make_star()
        info = StarInfo.from_star(star)
        with pytest.raises(AttributeError):
            info.name = "Changed"


class TestStarInfoBackwardCompatibility:
    """Verify existing code that calls from_star(star) without new kwargs still works."""

    def test_system_info_from_star_system_still_works(self):
        """SystemInfo.from_star_system() calls StarInfo.from_star(star) with no extra args.
        This must not break."""
        from game.strategy.data.star_system import StarSystem
        star = _make_star(name="TestStar")
        system = StarSystem(
            name="TestSystem",
            global_location=HexCoord(5, 5),
            stars=[star],
        )

        system_info = SystemInfo.from_star_system(system)
        assert system_info.primary_star is not None
        assert system_info.primary_star.name == "TestStar"
        # Physical fields populated from star, system context fields have defaults
        assert system_info.primary_star.mass == 1.0  # from star
        assert system_info.primary_star.system_name == ""  # default (no system context passed)
        assert system_info.primary_star.planet_count == 0  # default


class TestFacadeGetAllStars:
    """Test StrategySessionFacade.get_all_stars() query method."""

    def _make_facade_with_systems(self, systems_dict):
        """Create a facade with a mock session containing the given systems."""
        galaxy = MagicMock()
        galaxy.systems = systems_dict

        session = MagicMock()
        session.galaxy = galaxy

        return StrategySessionFacade(session)

    def test_empty_galaxy(self):
        """No systems means no stars."""
        facade = self._make_facade_with_systems({})
        stars = facade.systems.all_stars()
        assert stars == []

    def test_single_system_single_star(self):
        """One system with one star returns one StarInfo."""
        from game.strategy.data.star_system import StarSystem
        star = _make_star(name="Sol", mass=1.0)
        system = StarSystem("Solar", HexCoord(10, 20), stars=[star])
        # Add a mock planet
        system.planets = [MagicMock()]

        facade = self._make_facade_with_systems({"Solar": system})
        stars = facade.systems.all_stars()

        assert len(stars) == 1
        info = stars[0]
        assert info.name == "Sol"
        assert info.system_name == "Solar"
        assert info.system_global_location == HexCoord(10, 20)
        assert info.planet_count == 1
        assert info.companion_star_count == 0

    def test_binary_system(self):
        """Binary system: each star has companion_star_count == 1."""
        from game.strategy.data.star_system import StarSystem
        star_a = _make_star(name="Alpha A", mass=1.1)
        star_b = _make_star(name="Alpha B", mass=0.9, star_type=StarType.RED_DWARF)
        system = StarSystem("Alpha", HexCoord(5, 5), stars=[star_a, star_b])

        facade = self._make_facade_with_systems({"Alpha": system})
        stars = facade.systems.all_stars()

        assert len(stars) == 2
        assert all(s.companion_star_count == 1 for s in stars)
        assert stars[0].name == "Alpha A"
        assert stars[1].name == "Alpha B"

    def test_multiple_systems(self):
        """Stars from all systems are collected."""
        from game.strategy.data.star_system import StarSystem
        s1 = StarSystem("Sys1", HexCoord(0, 0), stars=[_make_star(name="Star1")])
        s2 = StarSystem("Sys2", HexCoord(100, 100), stars=[
            _make_star(name="Star2A"),
            _make_star(name="Star2B"),
        ])

        facade = self._make_facade_with_systems({"Sys1": s1, "Sys2": s2})
        stars = facade.systems.all_stars()

        assert len(stars) == 3
        names = {s.name for s in stars}
        assert names == {"Star1", "Star2A", "Star2B"}
