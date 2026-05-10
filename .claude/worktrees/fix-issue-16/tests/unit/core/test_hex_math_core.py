"""
Unit tests for game/core/hex_math.py

Tests hex coordinate system, distance calculations, pixel conversions,
rings, line drawing, and serialization.
"""
import math
import pytest

from game.core.hex_math import (
    HexCoord,
    hex_distance,
    hex_to_pixel,
    hex_axial_to_cartesian,
    pixel_to_hex,
    hex_ring,
    hex_circle_filled,
    hex_random_cluster,
    hex_lerp,
    hex_linedraw,
    hex_to_dict,
    hex_from_dict,
    hex_from_dict_safe,
)


# =============================================================================
# HexCoord Class Tests
# =============================================================================

class TestHexCoordInit:
    """Tests for HexCoord initialization."""

    def test_init_calculates_s_coordinate(self):
        """Verify s = -q - r for various inputs."""
        coord = HexCoord(3, 2)
        assert coord.s == -3 - 2 == -5

    def test_init_negative_coords(self):
        """HexCoord(-5, -3) should have s=8."""
        coord = HexCoord(-5, -3)
        assert coord.s == 8
        assert coord.q + coord.r + coord.s == 0

    def test_init_large_coords(self):
        """HexCoord(10000, -5000) maintains invariant."""
        coord = HexCoord(10000, -5000)
        assert coord.s == -10000 - (-5000) == -5000
        assert coord.q + coord.r + coord.s == 0

    def test_cube_property(self):
        """Cube property returns (q, r, s) tuple."""
        coord = HexCoord(2, 3)
        assert coord.cube == (2, 3, -5)


class TestHexCoordEquality:
    """Tests for HexCoord equality and hashing."""

    def test_eq_identical_coords(self):
        """HexCoord(1,2) == HexCoord(1,2)."""
        assert HexCoord(1, 2) == HexCoord(1, 2)

    def test_eq_different_coords(self):
        """HexCoord(1,2) != HexCoord(2,1)."""
        assert HexCoord(1, 2) != HexCoord(2, 1)

    def test_eq_non_hexcoord(self):
        """HexCoord(1,2) != (1,2) returns False."""
        coord = HexCoord(1, 2)
        assert coord != (1, 2)
        assert coord != [1, 2]
        assert coord != "HexCoord(1, 2)"

    def test_hash_same_coords(self):
        """Two equal HexCoords have same hash."""
        a = HexCoord(5, -3)
        b = HexCoord(5, -3)
        assert hash(a) == hash(b)

    def test_hash_usable_as_dict_key(self):
        """Can use HexCoord as dict key."""
        d = {}
        coord = HexCoord(1, 2)
        d[coord] = "value"
        assert d[HexCoord(1, 2)] == "value"

    def test_hash_usable_in_set(self):
        """Can add/lookup HexCoord in set."""
        s = set()
        s.add(HexCoord(1, 2))
        s.add(HexCoord(3, 4))
        assert HexCoord(1, 2) in s
        assert HexCoord(3, 4) in s
        assert HexCoord(5, 6) not in s
        # Adding duplicate should not increase size
        s.add(HexCoord(1, 2))
        assert len(s) == 2


class TestHexCoordRepr:
    """Tests for HexCoord string representation."""

    def test_repr_format(self):
        """repr returns 'HexCoord(q, r)'."""
        coord = HexCoord(7, -3)
        assert repr(coord) == "HexCoord(7, -3)"


class TestHexCoordArithmetic:
    """Tests for HexCoord arithmetic operations."""

    def test_add_two_hexcoords(self):
        """(1,0) + (0,1) = (1,1)."""
        a = HexCoord(1, 0)
        b = HexCoord(0, 1)
        result = a + b
        assert result == HexCoord(1, 1)

    def test_add_returns_notimplemented(self):
        """HexCoord + int returns NotImplemented."""
        coord = HexCoord(1, 2)
        result = coord.__add__(5)
        assert result is NotImplemented

    def test_sub_two_hexcoords(self):
        """(3,2) - (1,1) = (2,1)."""
        a = HexCoord(3, 2)
        b = HexCoord(1, 1)
        result = a - b
        assert result == HexCoord(2, 1)

    def test_sub_returns_notimplemented(self):
        """HexCoord - int returns NotImplemented."""
        coord = HexCoord(1, 2)
        result = coord.__sub__(5)
        assert result is NotImplemented


class TestHexCoordNeighbors:
    """Tests for HexCoord.neighbors() method."""

    def test_neighbors_returns_6(self):
        """center.neighbors() has exactly 6 elements."""
        center = HexCoord(0, 0)
        neighbors = center.neighbors()
        assert len(neighbors) == 6

    def test_neighbors_are_adjacent(self):
        """All neighbors are distance 1 from center."""
        center = HexCoord(0, 0)
        neighbors = center.neighbors()
        for neighbor in neighbors:
            assert hex_distance(center, neighbor) == 1

    def test_neighbors_off_center(self):
        """Neighbors of (5,3) are correct."""
        center = HexCoord(5, 3)
        neighbors = center.neighbors()
        expected = [
            HexCoord(6, 3),   # +q
            HexCoord(6, 2),   # +q, -r
            HexCoord(5, 2),   # -r
            HexCoord(4, 3),   # -q
            HexCoord(4, 4),   # -q, +r
            HexCoord(5, 4),   # +r
        ]
        assert len(neighbors) == 6
        for n in neighbors:
            assert n in expected

    def test_neighbors_all_unique(self):
        """All neighbors are distinct."""
        center = HexCoord(0, 0)
        neighbors = center.neighbors()
        assert len(set(neighbors)) == 6


# =============================================================================
# hex_distance Tests
# =============================================================================

class TestHexDistance:
    """Tests for hex_distance function."""

    def test_distance_same_coord(self):
        """distance(a, a) == 0."""
        a = HexCoord(3, -2)
        assert hex_distance(a, a) == 0

    def test_distance_adjacent(self):
        """distance to neighbor == 1."""
        center = HexCoord(0, 0)
        neighbor = HexCoord(1, 0)
        assert hex_distance(center, neighbor) == 1

    def test_distance_symmetric(self):
        """distance(a,b) == distance(b,a)."""
        a = HexCoord(3, -2)
        b = HexCoord(-1, 4)
        assert hex_distance(a, b) == hex_distance(b, a)

    def test_distance_known_value(self):
        """distance((0,0), (2,3)) == 5."""
        a = HexCoord(0, 0)
        b = HexCoord(2, 3)
        # s for a = 0, s for b = -2 - 3 = -5
        # dq = 2, dr = 3, ds = 5
        # max(2, 3, 5) = 5
        assert hex_distance(a, b) == 5

    def test_distance_negative_coords(self):
        """distance((-3,2), (3,-2)) works correctly."""
        a = HexCoord(-3, 2)  # s = 1
        b = HexCoord(3, -2)  # s = -1
        # dq = 6, dr = 4, ds = 2
        # max(6, 4, 2) = 6
        assert hex_distance(a, b) == 6


# =============================================================================
# hex_ring Tests
# =============================================================================

class TestHexRing:
    """Tests for hex_ring function."""

    def test_ring_radius_0(self):
        """Returns [HexCoord(0,0)]."""
        result = hex_ring(0)
        assert result == [HexCoord(0, 0)]

    def test_ring_radius_1(self):
        """Returns exactly 6 hexes, all at distance 1."""
        result = hex_ring(1)
        assert len(result) == 6
        origin = HexCoord(0, 0)
        for coord in result:
            assert hex_distance(origin, coord) == 1

    def test_ring_radius_3(self):
        """Returns exactly 18 hexes (6*3), all at distance 3."""
        result = hex_ring(3)
        assert len(result) == 18
        origin = HexCoord(0, 0)
        for coord in result:
            assert hex_distance(origin, coord) == 3

    def test_ring_no_duplicates(self):
        """No duplicate coordinates in ring."""
        for radius in [1, 2, 5]:
            result = hex_ring(radius)
            assert len(result) == len(set(result))


# =============================================================================
# hex_lerp Tests
# =============================================================================

class TestHexLerp:
    """Tests for hex_lerp function."""

    def test_lerp_t0_returns_start(self):
        """hex_lerp(a, b, 0) == a."""
        a = HexCoord(1, 2)
        b = HexCoord(5, -3)
        assert hex_lerp(a, b, 0) == a

    def test_lerp_t1_returns_end(self):
        """hex_lerp(a, b, 1) == b."""
        a = HexCoord(1, 2)
        b = HexCoord(5, -3)
        assert hex_lerp(a, b, 1) == b

    def test_lerp_t05_returns_midpoint(self):
        """hex_lerp((0,0), (4,0), 0.5) == (2,0)."""
        a = HexCoord(0, 0)
        b = HexCoord(4, 0)
        result = hex_lerp(a, b, 0.5)
        assert result == HexCoord(2, 0)

    def test_lerp_same_start_end(self):
        """hex_lerp(a, a, 0.5) == a."""
        a = HexCoord(3, -1)
        assert hex_lerp(a, a, 0.5) == a


# =============================================================================
# hex_linedraw Tests
# =============================================================================

class TestHexLinedraw:
    """Tests for hex_linedraw function."""

    def test_linedraw_same_point(self):
        """Returns [a] when a == b."""
        a = HexCoord(2, 3)
        result = hex_linedraw(a, a)
        assert result == [a]

    def test_linedraw_adjacent(self):
        """Returns [a, b] for adjacent hexes."""
        a = HexCoord(0, 0)
        b = HexCoord(1, 0)
        result = hex_linedraw(a, b)
        assert len(result) == 2
        assert result[0] == a
        assert result[-1] == b

    def test_linedraw_length(self):
        """Line from (0,0) to (3,0) has 4 points (N+1)."""
        a = HexCoord(0, 0)
        b = HexCoord(3, 0)
        result = hex_linedraw(a, b)
        # Distance is 3, so N+1 = 4 points
        assert len(result) == 4

    def test_linedraw_all_adjacent(self):
        """Each consecutive pair is adjacent."""
        a = HexCoord(0, 0)
        b = HexCoord(4, -2)
        result = hex_linedraw(a, b)
        for i in range(len(result) - 1):
            dist = hex_distance(result[i], result[i + 1])
            assert dist == 1, f"Hexes {result[i]} and {result[i+1]} not adjacent"


# =============================================================================
# hex_to_pixel / pixel_to_hex Tests
# =============================================================================

class TestHexToPixel:
    """Tests for hex_to_pixel function."""

    def test_to_pixel_origin(self):
        """(0,0) -> (0, 0)."""
        coord = HexCoord(0, 0)
        x, y = hex_to_pixel(coord, size=10)
        assert x == 0
        assert y == 0

    def test_to_pixel_known_value(self):
        """(1,0) with size=10 -> (15, 8.66...)."""
        coord = HexCoord(1, 0)
        x, y = hex_to_pixel(coord, size=10)
        # x = 10 * (3/2 * 1) = 15
        assert x == 15
        # y = 10 * (sqrt(3)/2 * 1 + sqrt(3) * 0) = 10 * sqrt(3)/2
        expected_y = 10 * (math.sqrt(3) / 2)
        assert abs(y - expected_y) < 0.001


class TestHexAxialToCartesian:
    """Tests for hex_axial_to_cartesian function."""

    def test_origin_returns_zero(self):
        """(0, 0) with default center returns (0.0, 0.0)."""
        x, y = hex_axial_to_cartesian(0, 0)
        assert x == 0.0
        assert y == 0.0

    def test_q_only_offset(self):
        """(1, 0) maps to (1.0, 0.0) — pure q movement."""
        x, y = hex_axial_to_cartesian(1, 0)
        assert x == 1.0
        assert y == 0.0

    def test_r_only_offset(self):
        """(0, 1) maps to (0.5, sqrt(3)/2)."""
        x, y = hex_axial_to_cartesian(0, 1)
        assert abs(x - 0.5) < 1e-10
        assert abs(y - math.sqrt(3.0) / 2.0) < 1e-10

    def test_with_center_offset(self):
        """center_q=5, center_r=3 produces correct delta."""
        x, y = hex_axial_to_cartesian(5, 3, center_q=5, center_r=3)
        assert x == 0.0
        assert y == 0.0

    def test_matches_hardcoded_constant(self):
        """Result matches the hardcoded 0.8660254037844386 constant."""
        _, y = hex_axial_to_cartesian(0, 1)
        assert abs(y - 0.8660254037844386) < 1e-15

    def test_negative_coords(self):
        """Negative coordinates produce correct signs."""
        x, y = hex_axial_to_cartesian(-2, -3)
        expected_x = -2 + (-3) * 0.5  # -3.5
        expected_y = -3 * math.sqrt(3.0) / 2.0
        assert abs(x - expected_x) < 1e-10
        assert abs(y - expected_y) < 1e-10

    def test_float_inputs(self):
        """Float q, r inputs work correctly."""
        x, y = hex_axial_to_cartesian(1.5, 2.5)
        expected_x = 1.5 + 2.5 * 0.5  # 2.75
        expected_y = 2.5 * math.sqrt(3.0) / 2.0
        assert abs(x - expected_x) < 1e-10
        assert abs(y - expected_y) < 1e-10


class TestPixelToHex:
    """Tests for pixel_to_hex function."""

    def test_pixel_roundtrip(self):
        """pixel_to_hex(hex_to_pixel(h, s), s) == h for various h."""
        test_coords = [
            HexCoord(0, 0),
            HexCoord(1, 0),
            HexCoord(0, 1),
            HexCoord(-1, 1),
            HexCoord(5, -3),
            HexCoord(-10, 7),
        ]
        size = 50
        for original in test_coords:
            px, py = hex_to_pixel(original, size)
            result = pixel_to_hex(px, py, size)
            assert result == original, f"Roundtrip failed for {original}"

    def test_pixel_to_hex_rounding(self):
        """Fractional pixels round to nearest hex."""
        # Convert (0,0) to pixel, then offset slightly
        size = 10
        px, py = hex_to_pixel(HexCoord(0, 0), size)
        # Small offset should still round to origin
        result = pixel_to_hex(px + 0.1, py + 0.1, size)
        assert result == HexCoord(0, 0)


# =============================================================================
# Serialization Tests
# =============================================================================

class TestHexSerialization:
    """Tests for hex_to_dict and hex_from_dict."""

    def test_to_dict_format(self):
        """Returns {'q': q, 'r': r}."""
        coord = HexCoord(3, -5)
        d = hex_to_dict(coord)
        assert d == {'q': 3, 'r': -5}

    def test_from_dict_creates_hexcoord(self):
        """Creates correct HexCoord."""
        d = {'q': 7, 'r': -2}
        coord = hex_from_dict(d)
        assert coord.q == 7
        assert coord.r == -2
        assert coord.s == -5

    def test_serialization_roundtrip(self):
        """hex_from_dict(hex_to_dict(h)) == h."""
        test_coords = [
            HexCoord(0, 0),
            HexCoord(100, -50),
            HexCoord(-30, -40),
        ]
        for original in test_coords:
            d = hex_to_dict(original)
            result = hex_from_dict(d)
            assert result == original


# =============================================================================
# TCG-FND-014: HexCoord Arithmetic TypeError Tests
# =============================================================================

class TestHexCoordArithmeticTypeError:
    """TCG-FND-014: Tests for HexCoord arithmetic with non-HexCoord types.

    Verifies that adding/subtracting non-HexCoord types raises TypeError,
    documenting the explicit contract for type safety.
    """

    def test_add_int_raises_typeerror(self):
        """HexCoord(1,0) + 5 raises TypeError."""
        coord = HexCoord(1, 0)
        with pytest.raises(TypeError):
            _ = coord + 5

    def test_add_tuple_raises_typeerror(self):
        """HexCoord(1,0) + (1, 0) raises TypeError."""
        coord = HexCoord(1, 0)
        with pytest.raises(TypeError):
            _ = coord + (1, 0)

    def test_add_list_raises_typeerror(self):
        """HexCoord(1,0) + [1, 0] raises TypeError."""
        coord = HexCoord(1, 0)
        with pytest.raises(TypeError):
            _ = coord + [1, 0]

    def test_add_string_raises_typeerror(self):
        """HexCoord(1,0) + 'hex' raises TypeError."""
        coord = HexCoord(1, 0)
        with pytest.raises(TypeError):
            _ = coord + "hex"

    def test_sub_int_raises_typeerror(self):
        """HexCoord(1,0) - 5 raises TypeError."""
        coord = HexCoord(1, 0)
        with pytest.raises(TypeError):
            _ = coord - 5

    def test_sub_tuple_raises_typeerror(self):
        """HexCoord(1,0) - (1, 0) raises TypeError."""
        coord = HexCoord(1, 0)
        with pytest.raises(TypeError):
            _ = coord - (1, 0)

    def test_sub_none_raises_typeerror(self):
        """HexCoord(1,0) - None raises TypeError."""
        coord = HexCoord(1, 0)
        with pytest.raises(TypeError):
            _ = coord - None

    def test_add_none_raises_typeerror(self):
        """HexCoord(1,0) + None raises TypeError."""
        coord = HexCoord(1, 0)
        with pytest.raises(TypeError):
            _ = coord + None

    def test_radd_not_supported(self):
        """5 + HexCoord(1,0) raises TypeError (no __radd__)."""
        coord = HexCoord(1, 0)
        with pytest.raises(TypeError):
            _ = 5 + coord

    def test_rsub_not_supported(self):
        """5 - HexCoord(1,0) raises TypeError (no __rsub__)."""
        coord = HexCoord(1, 0)
        with pytest.raises(TypeError):
            _ = 5 - coord


# =============================================================================
# TCG-FND-015: pixel_to_hex Rounding Edge Cases
# =============================================================================

class TestPixelToHexRoundingEdgeCases:
    """TCG-FND-015: Tests for pixel_to_hex() rounding edge cases.

    Verifies round-trip property for a wide range of hexes and tests
    behavior at positions near hex boundaries.
    """

    def test_roundtrip_property_wide_range(self):
        """Round-trip property holds for a wide range of coordinates."""
        size = 50
        # Test a grid of hex coordinates
        for q in range(-20, 21, 5):
            for r in range(-20, 21, 5):
                original = HexCoord(q, r)
                px, py = hex_to_pixel(original, size)
                result = pixel_to_hex(px, py, size)
                assert result == original, f"Roundtrip failed for {original}"

    def test_roundtrip_at_various_sizes(self):
        """Round-trip works correctly at various hex sizes."""
        test_coords = [HexCoord(3, -2), HexCoord(-5, 7), HexCoord(0, 0)]

        for size in [10, 25, 50, 100, 200]:
            for original in test_coords:
                px, py = hex_to_pixel(original, size)
                result = pixel_to_hex(px, py, size)
                assert result == original, f"Roundtrip failed for {original} at size {size}"

    def test_pixel_near_hex_center_returns_that_hex(self):
        """Pixel position near hex center rounds to that hex."""
        size = 50
        coord = HexCoord(3, -1)
        center_x, center_y = hex_to_pixel(coord, size)

        # Test small offsets around center
        for dx in [-1.0, 0.0, 1.0]:
            for dy in [-1.0, 0.0, 1.0]:
                result = pixel_to_hex(center_x + dx, center_y + dy, size)
                assert result == coord, f"Failed for offset ({dx}, {dy})"

    def test_pixel_halfway_between_two_hexes(self):
        """Pixel halfway between two hexes rounds to one of them consistently."""
        size = 50
        hex_a = HexCoord(0, 0)
        hex_b = HexCoord(1, 0)

        px_a, py_a = hex_to_pixel(hex_a, size)
        px_b, py_b = hex_to_pixel(hex_b, size)

        # Midpoint between the two hex centers
        mid_x = (px_a + px_b) / 2
        mid_y = (py_a + py_b) / 2

        # The result should be one of the two adjacent hexes
        result = pixel_to_hex(mid_x, mid_y, size)
        assert result in [hex_a, hex_b], f"Midpoint rounded to unexpected hex: {result}"

    def test_roundtrip_negative_coordinates(self):
        """Round-trip works for negative q and r coordinates."""
        size = 50
        test_coords = [
            HexCoord(-1, 0),
            HexCoord(0, -1),
            HexCoord(-5, -5),
            HexCoord(-10, 3),
            HexCoord(7, -12),
        ]

        for original in test_coords:
            px, py = hex_to_pixel(original, size)
            result = pixel_to_hex(px, py, size)
            assert result == original, f"Roundtrip failed for {original}"

    def test_roundtrip_origin(self):
        """Round-trip at origin works correctly."""
        size = 50
        original = HexCoord(0, 0)
        px, py = hex_to_pixel(original, size)

        assert px == 0
        assert py == 0

        result = pixel_to_hex(px, py, size)
        assert result == original

    def test_pixel_to_hex_returns_hexcoord(self):
        """pixel_to_hex returns a HexCoord instance."""
        result = pixel_to_hex(100, 100, 50)
        assert isinstance(result, HexCoord)

    def test_roundtrip_stress_many_coordinates(self):
        """Round-trip property tested on many coordinates (stress test)."""
        size = 30
        failures = []

        for q in range(-50, 51):
            for r in range(-50, 51):
                original = HexCoord(q, r)
                px, py = hex_to_pixel(original, size)
                result = pixel_to_hex(px, py, size)
                if result != original:
                    failures.append((original, result))

        assert len(failures) == 0, f"Round-trip failures: {failures[:10]}..."


# =============================================================================
# hex_circle_filled Tests
# =============================================================================

class TestHexCircleFilled:
    """Tests for hex_circle_filled function."""

    def test_hex_circle_filled_radius_0(self):
        """radius=0 returns just the center hex."""
        center = HexCoord(0, 0)
        result = hex_circle_filled(center, 0)
        assert result == frozenset({center})

    def test_hex_circle_filled_radius_1(self):
        """radius=1 returns 7 hexes (center + 6 neighbors)."""
        center = HexCoord(0, 0)
        result = hex_circle_filled(center, 1)
        assert len(result) == 7
        assert center in result
        # All neighbors should be included
        for neighbor in center.neighbors():
            assert neighbor in result

    def test_hex_circle_filled_radius_2(self):
        """radius=2 returns 19 hexes (1 + 6 + 12)."""
        center = HexCoord(0, 0)
        result = hex_circle_filled(center, 2)
        assert len(result) == 19
        # Verify all hexes are within distance 2
        for h in result:
            assert hex_distance(center, h) <= 2

    def test_hex_circle_filled_radius_5(self):
        """radius=5 returns 91 hexes (Dyson Sphere zone size)."""
        center = HexCoord(0, 0)
        result = hex_circle_filled(center, 5)
        # Formula: 1 + 6 * (1 + 2 + 3 + 4 + 5) = 1 + 6 * 15 = 91
        assert len(result) == 91
        # Verify all hexes are within distance 5
        for h in result:
            assert hex_distance(center, h) <= 5

    def test_hex_circle_filled_with_offset_center(self):
        """Circle with offset center returns correct hexes."""
        center = HexCoord(5, -3)
        result = hex_circle_filled(center, 2)
        assert len(result) == 19
        assert center in result
        # Verify all hexes are within distance 2 from center
        for h in result:
            assert hex_distance(center, h) <= 2

    def test_hex_circle_filled_returns_frozenset(self):
        """hex_circle_filled returns a frozenset (immutable)."""
        result = hex_circle_filled(HexCoord(0, 0), 1)
        assert isinstance(result, frozenset)

    def test_hex_circle_filled_no_duplicates(self):
        """No duplicate hexes in result."""
        for radius in [1, 2, 3, 5]:
            result = hex_circle_filled(HexCoord(0, 0), radius)
            # frozenset already guarantees no duplicates, but verify count
            result_list = list(result)
            assert len(result_list) == len(set(result_list))


# =============================================================================
# hex_random_cluster Tests
# =============================================================================

class TestHexRandomCluster:
    """Tests for hex_random_cluster function."""

    def test_cluster_returns_target_size(self):
        """Cluster returns target_size hexes when space available."""
        from game.core.hex_math import hex_random_cluster
        import random

        rng = random.Random(42)
        center = HexCoord(0, 0)
        result = hex_random_cluster(center, target_size=5, rng=rng)

        assert len(result) == 5
        # Result should be offsets relative to center
        assert HexCoord(0, 0) in result  # Center is always included

    def test_cluster_contains_center(self):
        """Cluster always contains the center hex (as offset 0,0)."""
        from game.core.hex_math import hex_random_cluster
        import random

        rng = random.Random(123)
        center = HexCoord(5, -3)
        result = hex_random_cluster(center, target_size=7, rng=rng)

        # Returns offsets, so (0, 0) should be present
        assert HexCoord(0, 0) in result

    def test_single_hex_cluster(self):
        """target_size=1 returns just {HexCoord(0,0)}."""
        from game.core.hex_math import hex_random_cluster
        import random

        rng = random.Random(0)
        result = hex_random_cluster(HexCoord(0, 0), target_size=1, rng=rng)

        assert result == frozenset({HexCoord(0, 0)})

    def test_cluster_is_connected(self):
        """All hexes in cluster are connected (form contiguous region)."""
        from game.core.hex_math import hex_random_cluster, hex_distance
        import random

        rng = random.Random(999)
        center = HexCoord(0, 0)
        offsets = hex_random_cluster(center, target_size=10, rng=rng)

        # Convert offsets to absolute positions for connectivity check
        absolute_hexes = {center + offset for offset in offsets}

        # Connectivity check: BFS from any hex should reach all others
        start = next(iter(absolute_hexes))
        visited = {start}
        frontier = [start]

        while frontier:
            current = frontier.pop()
            for neighbor in current.neighbors():
                if neighbor in absolute_hexes and neighbor not in visited:
                    visited.add(neighbor)
                    frontier.append(neighbor)

        assert visited == absolute_hexes, "Cluster is not connected"

    def test_cluster_avoids_excluded_hexes(self):
        """Cluster does not include hexes in avoid set."""
        from game.core.hex_math import hex_random_cluster
        import random

        rng = random.Random(42)
        center = HexCoord(0, 0)
        # Avoid all neighbors of the center
        avoid = frozenset({HexCoord(1, 0), HexCoord(0, 1), HexCoord(-1, 1),
                          HexCoord(-1, 0), HexCoord(0, -1), HexCoord(1, -1)})

        result = hex_random_cluster(center, target_size=5, rng=rng, avoid=avoid)

        # Result is offsets - convert to absolute to check
        absolute_hexes = {center + offset for offset in result}

        # Should not overlap with avoid set
        assert absolute_hexes.isdisjoint(avoid)
        # Can only return center since all neighbors blocked
        assert result == frozenset({HexCoord(0, 0)})

    def test_cluster_deterministic_with_seeded_rng(self):
        """Same seed produces same cluster."""
        from game.core.hex_math import hex_random_cluster
        import random

        center = HexCoord(0, 0)

        rng1 = random.Random(12345)
        result1 = hex_random_cluster(center, target_size=8, rng=rng1)

        rng2 = random.Random(12345)
        result2 = hex_random_cluster(center, target_size=8, rng=rng2)

        assert result1 == result2

    def test_cluster_returns_smaller_when_constrained(self):
        """When frontier runs out, returns smaller cluster than requested."""
        from game.core.hex_math import hex_random_cluster, hex_circle_filled
        import random

        rng = random.Random(42)
        center = HexCoord(0, 0)
        # Block everything except a small pocket - only allow hexes within radius 2
        # But mark radius 1 as the "allowed" area and everything else as blocked
        allowed = hex_circle_filled(center, 1)  # 7 hexes total

        # Avoid everything NOT in allowed (block outside the pocket)
        # Create a large ring of blocked hexes around the allowed area
        avoid = hex_circle_filled(center, 10) - allowed

        # Request 50 hexes but only 7 are available
        result = hex_random_cluster(center, target_size=50, rng=rng, avoid=avoid)

        # Should get exactly 7 (all of allowed area)
        assert len(result) == 7
        assert len(result) < 50  # Less than requested

    def test_cluster_returns_frozenset(self):
        """hex_random_cluster returns a frozenset."""
        from game.core.hex_math import hex_random_cluster
        import random

        rng = random.Random(0)
        result = hex_random_cluster(HexCoord(0, 0), target_size=3, rng=rng)

        assert isinstance(result, frozenset)

    def test_cluster_with_offset_center(self):
        """Cluster works correctly with non-origin center."""
        from game.core.hex_math import hex_random_cluster
        import random

        rng = random.Random(42)
        center = HexCoord(10, -5)
        result = hex_random_cluster(center, target_size=5, rng=rng)

        assert len(result) == 5
        # Result should be offsets relative to center, so (0,0) is included
        assert HexCoord(0, 0) in result

        # Converting back to absolute should give hexes near center
        absolute_hexes = {center + offset for offset in result}
        for h in absolute_hexes:
            # All should be within reasonable distance of center
            assert hex_distance(center, h) <= 5  # Can't be farther than cluster size


# =============================================================================
# hex_from_dict_safe Tests
# =============================================================================

class TestHexFromDictSafe:
    """Tests for hex_from_dict_safe utility."""

    def test_valid_location_key(self):
        """Should deserialize from default 'location' key."""
        data = {'location': {'q': 3, 'r': -1}}
        result = hex_from_dict_safe(data)
        assert result == HexCoord(3, -1)

    def test_custom_key(self):
        """Should deserialize from a custom key."""
        data = {'coord': {'q': 5, 'r': 2}}
        result = hex_from_dict_safe(data, key='coord')
        assert result == HexCoord(5, 2)

    def test_missing_key_returns_default(self):
        """Should return default when key is missing."""
        data = {'other': 'value'}
        result = hex_from_dict_safe(data)
        assert result is None

    def test_missing_key_returns_custom_default(self):
        """Should return custom default when key is missing."""
        default = HexCoord(0, 0)
        data = {'other': 'value'}
        result = hex_from_dict_safe(data, default=default)
        assert result == default

    def test_none_value_returns_default(self):
        """Should return default when value is None."""
        data = {'location': None}
        result = hex_from_dict_safe(data)
        assert result is None

    def test_invalid_dict_returns_default(self):
        """Should return default for invalid dict (missing q/r)."""
        data = {'location': {'x': 1, 'y': 2}}
        result = hex_from_dict_safe(data)
        assert result is None

    def test_non_dict_value_returns_default(self):
        """Should return default when value is not a dict."""
        data = {'location': 'not_a_dict'}
        result = hex_from_dict_safe(data)
        assert result is None

    def test_empty_dict_returns_default(self):
        """Should return default for empty nested dict."""
        data = {'location': {}}
        result = hex_from_dict_safe(data)
        assert result is None
