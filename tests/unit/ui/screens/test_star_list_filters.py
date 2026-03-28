"""Tests for star list filtering and sorting logic (PROJ-231)."""
import pytest
from unittest.mock import MagicMock
from game.core.hex_math import HexCoord
from game.strategy.data.stars import Star, StarType, Spectrum
from game.ui.screens.star_list_filters import (
    gather_stars, filter_stars, sort_stars, compute_star_ranges,
    get_system_name, get_star_type_display,
)


def _make_spectrum(**overrides):
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
    return Star(
        name=name, mass=mass, radius_hexes=radius_hexes,
        temperature=temperature, luminosity=luminosity,
        spectrum=spectrum or _make_spectrum(), star_type=star_type,
        color=color, age=age, location=location or HexCoord(0, 0),
    )


def _make_galaxy(systems_dict):
    """Create a mock galaxy with the given systems dict."""
    galaxy = MagicMock()
    galaxy.systems = systems_dict
    return galaxy


def _make_system(name, stars, planets=None, location=None):
    """Create a StarSystem with given attributes."""
    from game.strategy.data.galaxy import StarSystem
    system = StarSystem(name, location or HexCoord(0, 0), stars=stars)
    if planets:
        system.planets = planets
    return system


class TestGatherStars:
    def test_empty_galaxy(self):
        galaxy = _make_galaxy({})
        result = gather_stars(galaxy)
        assert result == []

    def test_single_star(self):
        star = _make_star(name="Sol")
        system = _make_system("Solar", [star])
        galaxy = _make_galaxy({"Solar": system})

        result = gather_stars(galaxy)
        assert len(result) == 1
        assert result[0].name == "Sol"

    def test_cached_values_attached(self):
        star = _make_star(name="Sol", star_type=StarType.MAIN_SEQUENCE)
        planet = MagicMock()
        system = _make_system("Solar", [star], planets=[planet], location=HexCoord(10, 20))
        galaxy = _make_galaxy({"Solar": system})

        result = gather_stars(galaxy)
        s = result[0]
        assert s._cached_name_lower == "sol"
        assert s._cached_type_category == "MAIN_SEQUENCE"
        assert s._cached_system_name == "Solar"
        assert s._cached_system_global_location == HexCoord(10, 20)
        assert s._cached_planet_count == 1
        assert s._cached_companion_count == 0

    def test_binary_system_companion_count(self):
        star_a = _make_star(name="A")
        star_b = _make_star(name="B")
        system = _make_system("Binary", [star_a, star_b])
        galaxy = _make_galaxy({"Binary": system})

        result = gather_stars(galaxy)
        assert len(result) == 2
        assert result[0]._cached_companion_count == 1
        assert result[1]._cached_companion_count == 1

    def test_none_galaxy(self):
        result = gather_stars(None)
        assert result == []


class TestFilterStars:
    def _gathered_stars(self):
        """Create a set of gathered stars with cached values."""
        star_ms = _make_star(name="Sol", star_type=StarType.MAIN_SEQUENCE,
                             mass=1.0, temperature=5778, luminosity=1.0,
                             age=4.6e9, radius_hexes=2)
        star_rg = _make_star(name="Betelgeuse", star_type=StarType.RED_GIANT,
                             mass=12.0, temperature=3500, luminosity=100.0,
                             age=8e6, radius_hexes=5)
        star_wd = _make_star(name="Sirius B", star_type=StarType.WHITE_DWARF,
                             mass=1.0, temperature=25000, luminosity=0.03,
                             age=2.3e8, radius_hexes=1)

        system1 = _make_system("Solar", [star_ms])
        system2 = _make_system("Orion", [star_rg])
        system3 = _make_system("Sirius", [star_wd])
        galaxy = _make_galaxy({
            "Solar": system1, "Orion": system2, "Sirius": system3
        })
        return gather_stars(galaxy)

    def _all_types_enabled(self):
        return {t.name: True for t in StarType}

    def test_no_filters(self):
        stars = self._gathered_stars()
        types = self._all_types_enabled()
        result = filter_stars(stars, "", types,
                              0, 100, 0, 1e6, 0, 1e6, 0, 1.5e10, 1, 6)
        assert len(result) == 3

    def test_name_search(self):
        stars = self._gathered_stars()
        types = self._all_types_enabled()
        result = filter_stars(stars, "sol", types,
                              0, 100, 0, 1e6, 0, 1e6, 0, 1.5e10, 1, 6)
        assert len(result) == 1
        assert result[0].name == "Sol"

    def test_type_filter(self):
        stars = self._gathered_stars()
        types = self._all_types_enabled()
        types["RED_GIANT"] = False
        result = filter_stars(stars, "", types,
                              0, 100, 0, 1e6, 0, 1e6, 0, 1.5e10, 1, 6)
        assert len(result) == 2
        assert all(s.name != "Betelgeuse" for s in result)

    def test_mass_range(self):
        stars = self._gathered_stars()
        types = self._all_types_enabled()
        result = filter_stars(stars, "", types,
                              5.0, 100, 0, 1e6, 0, 1e6, 0, 1.5e10, 1, 6)
        assert len(result) == 1
        assert result[0].name == "Betelgeuse"

    def test_temperature_range(self):
        stars = self._gathered_stars()
        types = self._all_types_enabled()
        result = filter_stars(stars, "", types,
                              0, 100, 20000, 1e6, 0, 1e6, 0, 1.5e10, 1, 6)
        assert len(result) == 1
        assert result[0].name == "Sirius B"

    def test_radius_range(self):
        stars = self._gathered_stars()
        types = self._all_types_enabled()
        result = filter_stars(stars, "", types,
                              0, 100, 0, 1e6, 0, 1e6, 0, 1.5e10, 4, 6)
        assert len(result) == 1
        assert result[0].name == "Betelgeuse"


class TestSortStars:
    def _make_sortable_stars(self):
        """Create gathered stars for sorting tests."""
        s1 = _make_star(name="Beta", mass=2.0, temperature=8000)
        s2 = _make_star(name="Alpha", mass=0.5, temperature=3000)
        s3 = _make_star(name="Gamma", mass=5.0, temperature=15000)
        system = _make_system("Sys", [s1, s2, s3])
        galaxy = _make_galaxy({"Sys": system})
        return gather_stars(galaxy)

    def _columns(self):
        return [
            {'id': 'name', 'title': 'Name', 'attr': 'name'},
            {'id': 'mass', 'title': 'Mass', 'attr': 'mass'},
            {'id': 'temp', 'title': 'Temp', 'attr': 'temperature'},
        ]

    def test_sort_by_name_ascending(self):
        stars = self._make_sortable_stars()
        result = sort_stars(stars, 'name', False, self._columns())
        assert [s.name for s in result] == ["Alpha", "Beta", "Gamma"]

    def test_sort_by_mass_descending(self):
        stars = self._make_sortable_stars()
        result = sort_stars(stars, 'mass', True, self._columns())
        assert [s.mass for s in result] == [5.0, 2.0, 0.5]

    def test_sort_no_column(self):
        stars = self._make_sortable_stars()
        original_order = [s.name for s in stars]
        result = sort_stars(stars, None, False, self._columns())
        assert [s.name for s in result] == original_order


class TestComputeStarRanges:
    def test_empty_list(self):
        ranges = compute_star_ranges([])
        assert 'mass' in ranges
        assert 'temperature' in ranges
        assert 'luminosity' in ranges
        assert 'age' in ranges
        assert 'radius_hexes' in ranges

    def test_single_star(self):
        star = _make_star(mass=1.0, temperature=5778, luminosity=1.0,
                          age=4.6e9, radius_hexes=2)
        ranges = compute_star_ranges([star])
        assert ranges['mass'][0] <= 1.0 <= ranges['mass'][1]
        assert ranges['temperature'][0] <= 5778 <= ranges['temperature'][1]


class TestHelperFunctions:
    def test_get_system_name(self):
        star = _make_star()
        star._cached_system_name = "Solar"
        assert get_system_name(star) == "Solar"

    def test_get_system_name_no_cache(self):
        star = _make_star()
        assert get_system_name(star) == "?"

    def test_get_star_type_display(self):
        star = _make_star(star_type=StarType.MAIN_SEQUENCE)
        assert get_star_type_display(star) == "Main Sequence"

    def test_get_star_type_display_black_hole(self):
        star = _make_star(star_type=StarType.BLACK_HOLE)
        assert get_star_type_display(star) == "Black Hole"
