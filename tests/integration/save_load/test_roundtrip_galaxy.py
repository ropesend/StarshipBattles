"""Round-trip tests for WarpPoint, StarSystem, and Galaxy serialization (PROJ-223 Phase 2+3)."""

import pytest

from game.strategy.data.galaxy import Galaxy
from game.strategy.data.star_system import WarpPoint, StarSystem
from game.core.hex_math import HexCoord
from tests.fixtures.strategy_entities import (
    create_test_warp_point,
    create_test_star_system,
    create_test_storm,
)
from tests.integration.save_load.conftest import assert_round_trip_fidelity


class TestWarpPointRoundTrip:
    """WarpPoint round-trip serialization tests."""

    def test_to_dict_includes_destination_and_location(self):
        wp = create_test_warp_point()
        d = wp.to_dict()
        assert 'destination_id' in d
        assert 'location' in d

    def test_from_dict_restores_both_fields(self):
        original = create_test_warp_point(destination_id="SystemX", location=HexCoord(7, -4))
        d = original.to_dict()
        restored = WarpPoint.from_dict(d)
        assert restored.destination_id == "SystemX"
        assert restored.location == HexCoord(7, -4)

    def test_round_trip_preserves_hex_coord_location(self):
        wp = create_test_warp_point(location=HexCoord(-3, 8))
        d = wp.to_dict()
        restored = WarpPoint.from_dict(d)
        assert restored.location == wp.location
        assert restored.destination_id == wp.destination_id


# =============================================================================
# Phase 3: StarSystem compound round-trip tests
# =============================================================================

class TestStarSystemRoundTrip:
    """StarSystem compound round-trip serialization tests."""

    def test_round_trip_with_all_children(self):
        ss = create_test_star_system(num_planets=2, num_stars=1)
        ss.storms.append(create_test_storm())
        # Storm hex_offsets are frozenset → list (non-deterministic order),
        # so ignore that field in deep compare and check manually
        restored = assert_round_trip_fidelity(
            ss, StarSystem,
            ignore_fields={"storms[0].hex_offsets"},
        )
        assert restored.name == ss.name
        assert len(restored.stars) == 1
        assert len(restored.planets) == 2
        assert len(restored.warp_points) == 1
        assert len(restored.storms) == 1
        assert restored.storms[0].hex_offsets == ss.storms[0].hex_offsets

    def test_region_id_present(self):
        ss = create_test_star_system(region_id=5)
        d = ss.to_dict()
        assert d['region_id'] == 5
        restored = StarSystem.from_dict(d)
        assert restored.region_id == 5

    def test_region_id_null(self):
        ss = create_test_star_system(region_id=None)
        restored = assert_round_trip_fidelity(ss, StarSystem)
        assert restored.region_id is None

    def test_global_location_preserved(self):
        ss = create_test_star_system(global_location=HexCoord(42, -17))
        restored = assert_round_trip_fidelity(ss, StarSystem)
        assert restored.global_location == HexCoord(42, -17)

    def test_nested_stars_preserved(self):
        ss = create_test_star_system(num_stars=2)
        restored = assert_round_trip_fidelity(ss, StarSystem)
        assert len(restored.stars) == 2
        for orig, rest in zip(ss.stars, restored.stars):
            assert rest.name == orig.name
            assert rest.mass == orig.mass

    def test_nested_planets_preserved(self):
        ss = create_test_star_system(num_planets=3)
        restored = assert_round_trip_fidelity(ss, StarSystem)
        assert len(restored.planets) == 3
        for orig, rest in zip(ss.planets, restored.planets):
            assert rest.name == orig.name
            assert rest.id == orig.id


# =============================================================================
# Phase 3: Galaxy compound round-trip tests
# =============================================================================

class TestGalaxyRoundTrip:
    """Galaxy compound round-trip serialization tests."""

    def test_radius_preserved(self):
        galaxy = Galaxy(radius=5000)
        d = galaxy.to_dict()
        restored = Galaxy.from_dict(d)
        assert restored.radius == 5000

    def test_next_planet_id_preserved(self):
        galaxy = Galaxy(radius=100)
        galaxy._next_planet_id = 42
        d = galaxy.to_dict()
        restored = Galaxy.from_dict(d)
        assert restored._next_planet_id == 42

    def test_systems_round_trip(self):
        galaxy = Galaxy(radius=100)
        ss = create_test_star_system(name="Alpha", global_location=HexCoord(10, -5), num_planets=1)
        galaxy.systems[ss.global_location] = ss
        galaxy.name_map[ss.name] = ss

        d = galaxy.to_dict()
        restored = Galaxy.from_dict(d)
        assert len(restored.systems) == 1
        coord = HexCoord(10, -5)
        assert coord in restored.systems
        assert restored.systems[coord].name == "Alpha"

    def test_spatial_indexes_rebuilt(self):
        """After from_dict, planet registry should be populated."""
        galaxy = Galaxy(radius=100)
        ss = create_test_star_system(name="Beta", num_planets=2)
        galaxy.systems[ss.global_location] = ss
        galaxy.name_map[ss.name] = ss
        # Register planets
        for planet in ss.planets:
            galaxy._registry.restore_planet(ss, planet)

        d = galaxy.to_dict()
        restored = Galaxy.from_dict(d)
        # Planets should be registered after from_dict
        for planet in restored.systems[ss.global_location].planets:
            found = restored.get_planet_by_id(planet.id)
            assert found is not None
            assert found.name == planet.name

    def test_multiple_systems(self):
        galaxy = Galaxy(radius=200)
        for i in range(3):
            ss = create_test_star_system(
                name=f"System_{i}",
                global_location=HexCoord(i * 10, 0),
                num_planets=1,
            )
            galaxy.systems[ss.global_location] = ss
            galaxy.name_map[ss.name] = ss

        d = galaxy.to_dict()
        restored = Galaxy.from_dict(d)
        assert len(restored.systems) == 3
