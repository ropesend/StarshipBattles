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
    pixel_to_hex,
    hex_ring,
    hex_lerp,
    hex_linedraw,
    hex_to_dict,
    hex_from_dict,
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
