"""Tests for hex_math module - hexagonal coordinate calculations."""
import pytest
import math

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


class TestHexCoord:
    """Test cases for HexCoord class."""

    def test_initialization(self):
        """Test HexCoord creation with q, r coordinates."""
        h = HexCoord(3, -2)
        assert h.q == 3
        assert h.r == -2
        assert h.s == -1  # s = -q - r

    def test_cube_constraint(self):
        """Test that q + r + s = 0 is maintained."""
        h = HexCoord(5, -3)
        assert h.q + h.r + h.s == 0

    def test_cube_property(self):
        """Test the cube property returns (q, r, s) tuple."""
        h = HexCoord(2, 4)
        assert h.cube == (2, 4, -6)

    def test_equality(self):
        """Test HexCoord equality comparison."""
        a = HexCoord(1, 2)
        b = HexCoord(1, 2)
        c = HexCoord(2, 1)
        assert a == b
        assert a != c

    def test_equality_with_non_hex(self):
        """Test equality returns False for non-HexCoord."""
        h = HexCoord(1, 2)
        assert h != (1, 2)
        assert h != "HexCoord(1, 2)"
        assert h != None

    def test_hash(self):
        """Test HexCoord can be used in sets and as dict keys."""
        a = HexCoord(1, 2)
        b = HexCoord(1, 2)
        c = HexCoord(2, 1)

        s = {a, b, c}
        assert len(s) == 2  # a and b are equal, should be deduplicated

        d = {a: "value"}
        assert d[b] == "value"

    def test_repr(self):
        """Test string representation."""
        h = HexCoord(3, -1)
        assert repr(h) == "HexCoord(3, -1)"

    def test_addition(self):
        """Test HexCoord addition."""
        a = HexCoord(2, 3)
        b = HexCoord(-1, 5)
        result = a + b
        assert result == HexCoord(1, 8)

    def test_subtraction(self):
        """Test HexCoord subtraction."""
        a = HexCoord(5, 2)
        b = HexCoord(3, -1)
        result = a - b
        assert result == HexCoord(2, 3)

    def test_addition_type_error(self):
        """Test addition with non-HexCoord returns NotImplemented."""
        h = HexCoord(1, 2)
        result = h.__add__((1, 2))
        assert result == NotImplemented

    def test_neighbors(self):
        """Test getting the 6 neighbors of a hex."""
        center = HexCoord(0, 0)
        neighbors = center.neighbors()

        assert len(neighbors) == 6
        # All neighbors should be at distance 1
        for n in neighbors:
            assert hex_distance(center, n) == 1

        # Neighbors should be unique
        assert len(set(neighbors)) == 6


class TestHexDistance:
    """Test cases for hex_distance function."""

    def test_same_hex(self):
        """Test distance to self is 0."""
        a = HexCoord(5, -3)
        assert hex_distance(a, a) == 0

    def test_adjacent_hex(self):
        """Test distance to adjacent hex is 1."""
        a = HexCoord(0, 0)
        b = HexCoord(1, 0)
        assert hex_distance(a, b) == 1

    def test_diagonal_distance(self):
        """Test distance in diagonal direction."""
        a = HexCoord(0, 0)
        b = HexCoord(3, 3)
        # In hex coordinates, moving diagonally (q+1, r+1) doesn't move in a straight line
        assert hex_distance(a, b) == 6

    def test_straight_line_distance(self):
        """Test distance along a straight axis."""
        a = HexCoord(0, 0)
        b = HexCoord(5, 0)
        assert hex_distance(a, b) == 5

    def test_symmetry(self):
        """Test that distance is symmetric."""
        a = HexCoord(3, -2)
        b = HexCoord(-1, 5)
        assert hex_distance(a, b) == hex_distance(b, a)


class TestHexPixelConversion:
    """Test cases for hex-to-pixel and pixel-to-hex conversion."""

    def test_origin_to_pixel(self):
        """Test origin hex converts to origin pixel."""
        h = HexCoord(0, 0)
        x, y = hex_to_pixel(h, 10)
        assert x == 0
        assert y == 0

    def test_pixel_to_hex_origin(self):
        """Test origin pixel converts to origin hex."""
        h = pixel_to_hex(0, 0, 10)
        assert h == HexCoord(0, 0)

    def test_roundtrip_conversion(self):
        """Test that hex -> pixel -> hex roundtrip preserves coordinates."""
        original = HexCoord(3, -2)
        size = 20

        x, y = hex_to_pixel(original, size)
        recovered = pixel_to_hex(x, y, size)

        assert recovered == original

    def test_pixel_to_hex_near_center(self):
        """Test pixel near hex center converts correctly."""
        size = 10
        # Get pixel coords of hex (2, 1)
        target = HexCoord(2, 1)
        x, y = hex_to_pixel(target, size)

        # Add small offset (should still round to same hex)
        h = pixel_to_hex(x + 1, y + 1, size)
        assert h == target


class TestHexRing:
    """Test cases for hex_ring function."""

    def test_radius_zero(self):
        """Test ring at radius 0 returns just the center."""
        ring = hex_ring(0)
        assert len(ring) == 1
        assert ring[0] == HexCoord(0, 0)

    def test_radius_one(self):
        """Test ring at radius 1 returns 6 hexes."""
        ring = hex_ring(1)
        assert len(ring) == 6

        # All should be at distance 1 from origin
        origin = HexCoord(0, 0)
        for h in ring:
            assert hex_distance(origin, h) == 1

    def test_radius_two(self):
        """Test ring at radius 2 returns 12 hexes."""
        ring = hex_ring(2)
        assert len(ring) == 12

        # All should be at distance 2 from origin
        origin = HexCoord(0, 0)
        for h in ring:
            assert hex_distance(origin, h) == 2

    def test_ring_size_formula(self):
        """Test that ring size follows formula: 6*radius for radius > 0."""
        for radius in range(1, 5):
            ring = hex_ring(radius)
            assert len(ring) == 6 * radius


class TestHexLerp:
    """Test cases for hex_lerp (linear interpolation)."""

    def test_lerp_at_zero(self):
        """Test lerp at t=0 returns start hex."""
        a = HexCoord(0, 0)
        b = HexCoord(4, 2)
        result = hex_lerp(a, b, 0)
        assert result == a

    def test_lerp_at_one(self):
        """Test lerp at t=1 returns end hex."""
        a = HexCoord(0, 0)
        b = HexCoord(4, 2)
        result = hex_lerp(a, b, 1)
        assert result == b

    def test_lerp_midpoint(self):
        """Test lerp at t=0.5 returns midpoint hex."""
        a = HexCoord(0, 0)
        b = HexCoord(4, 0)
        result = hex_lerp(a, b, 0.5)
        assert result == HexCoord(2, 0)


class TestHexLinedraw:
    """Test cases for hex_linedraw function."""

    def test_linedraw_same_hex(self):
        """Test line from hex to itself."""
        a = HexCoord(3, 2)
        line = hex_linedraw(a, a)
        assert len(line) == 1
        assert line[0] == a

    def test_linedraw_adjacent(self):
        """Test line to adjacent hex has 2 points."""
        a = HexCoord(0, 0)
        b = HexCoord(1, 0)
        line = hex_linedraw(a, b)
        assert len(line) == 2
        assert line[0] == a
        assert line[1] == b

    def test_linedraw_length(self):
        """Test line has correct number of hexes."""
        a = HexCoord(0, 0)
        b = HexCoord(5, 0)
        line = hex_linedraw(a, b)
        # Should have distance + 1 hexes
        assert len(line) == 6

    def test_linedraw_connectivity(self):
        """Test that consecutive hexes in line are adjacent."""
        a = HexCoord(0, 0)
        b = HexCoord(3, -2)
        line = hex_linedraw(a, b)

        for i in range(len(line) - 1):
            dist = hex_distance(line[i], line[i + 1])
            assert dist <= 1, f"Gap found between {line[i]} and {line[i+1]}"


class TestHexSerialization:
    """Test cases for hex serialization functions."""

    def test_hex_to_dict(self):
        """Test serializing HexCoord to dict."""
        h = HexCoord(5, -3)
        d = hex_to_dict(h)
        assert d == {'q': 5, 'r': -3}

    def test_hex_from_dict(self):
        """Test deserializing HexCoord from dict."""
        d = {'q': 2, 'r': 7}
        h = hex_from_dict(d)
        assert h == HexCoord(2, 7)

    def test_roundtrip_serialization(self):
        """Test serialization roundtrip preserves data."""
        original = HexCoord(-4, 8)
        d = hex_to_dict(original)
        recovered = hex_from_dict(d)
        assert recovered == original


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
