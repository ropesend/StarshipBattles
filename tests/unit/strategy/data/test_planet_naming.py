"""
Unit tests for planet naming utilities.
"""
from game.core.hex_math import HexCoord
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.planet_naming import assign_body_names


def _make_planet(location: HexCoord, mass: float, name: str = "") -> Planet:
    """Helper to create a minimal Planet for testing."""
    return Planet(
        name=name,
        location=location,
        orbit_distance=max(abs(location.q), abs(location.r), abs(-location.q - location.r)),
        mass=mass,
        radius=6.37e6,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.8,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        atmosphere={"N2": 78000, "O2": 21000},
        planet_type=PlanetType.CONTINENTAL
    )


class TestAssignBodyNames:
    """Tests for the assign_body_names function."""

    def test_single_planet(self):
        """Single planet at a location gets Roman numeral I."""
        bodies = [_make_planet(HexCoord(1, 0), mass=5e24)]
        assign_body_names(bodies, "Alpha Centauri")
        assert bodies[0].name == "Alpha Centauri I"

    def test_multiple_planets_different_locations(self):
        """Multiple planets at different distances get sequential Roman numerals."""
        bodies = [
            _make_planet(HexCoord(1, 0), mass=5e24),  # Distance 1
            _make_planet(HexCoord(2, 0), mass=4e24),  # Distance 2
            _make_planet(HexCoord(3, 0), mass=3e24),  # Distance 3
        ]
        assign_body_names(bodies, "Sol")
        assert bodies[0].name == "Sol I"
        assert bodies[1].name == "Sol II"
        assert bodies[2].name == "Sol III"

    def test_moons_at_same_location_get_suffixes(self):
        """Multiple bodies at same location: largest is primary, others get letter suffixes."""
        loc = HexCoord(2, 0)
        bodies = [
            _make_planet(loc, mass=5e24),   # Primary (largest)
            _make_planet(loc, mass=1e22),   # Moon a
            _make_planet(loc, mass=5e21),   # Moon b
        ]
        assign_body_names(bodies, "Kepler")
        assert bodies[0].name == "Kepler I"
        assert bodies[1].name == "Kepler Ia"
        assert bodies[2].name == "Kepler Ib"

    def test_sorts_same_location_by_mass_descending(self):
        """Bodies at same location should be sorted by mass (largest first)."""
        loc = HexCoord(1, 0)
        # Create bodies with masses out of order
        small = _make_planet(loc, mass=1e21)
        large = _make_planet(loc, mass=5e24)
        medium = _make_planet(loc, mass=1e23)
        bodies = [small, large, medium]

        assign_body_names(bodies, "Proxima")
        # After sorting, large should be primary, medium and small should be moons
        assert large.name == "Proxima I"
        assert medium.name == "Proxima Ia"
        assert small.name == "Proxima Ib"

    def test_sorts_locations_by_distance_from_center(self):
        """Locations should be sorted by distance from center (0,0)."""
        # Create planets at different distances (unsorted input)
        far = _make_planet(HexCoord(3, 0), mass=5e24)      # Distance 3
        close = _make_planet(HexCoord(1, 0), mass=5e24)    # Distance 1
        mid = _make_planet(HexCoord(2, 0), mass=5e24)      # Distance 2
        bodies = [far, close, mid]

        assign_body_names(bodies, "Tau Ceti")
        # Should be numbered by distance, not input order
        assert close.name == "Tau Ceti I"
        assert mid.name == "Tau Ceti II"
        assert far.name == "Tau Ceti III"

    def test_empty_bodies_list(self):
        """Empty bodies list should not raise an error."""
        bodies = []
        assign_body_names(bodies, "Empty System")
        assert bodies == []
