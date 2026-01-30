import pytest
import math
from game.strategy.data.hex_math import HexCoord, hex_distance, hex_to_pixel, pixel_to_hex

class TestHexCoord:
    def test_init(self):
        """Test axial initialization and cubic property."""
        h = HexCoord(1, 2)
        assert h.q == 1
        assert h.r == 2
        assert h.s == -3  # s = -q - r
        assert h.cube == (1, 2, -3)

    def test_equality(self):
        """Test value equality."""
        h1 = HexCoord(1, 2)
        h2 = HexCoord(1, 2)
        h3 = HexCoord(0, 0)
        assert h1 == h2
        assert h1 != h3
        assert h1 != (1, 2) # Strict object comparison to prevent ambiguity

    def test_hash(self):
        """Test hashing for dictionary keys."""
        h1 = HexCoord(1, 2)
        h2 = HexCoord(1, 2)
        d = {h1: "System A"}
        assert d[h2] == "System A"

    def test_addition(self):
        """Test vector addition."""
        h1 = HexCoord(1, 0)
        h2 = HexCoord(2, 3)
        h3 = h1 + h2
        assert h3.q == 3
        assert h3.r == 3

    def test_subtraction(self):
        """Test vector subtraction."""
        h1 = HexCoord(5, 5)
        h2 = HexCoord(2, 3)
        h3 = h1 - h2
        assert h3.q == 3
        assert h3.r == 2

    def test_neighbors(self):
        """Test neighbor generation."""
        center = HexCoord(0, 0)
        neighbors = center.neighbors()
        assert len(neighbors) == 6
        assert HexCoord(1, 0) in neighbors
        assert HexCoord(1, -1) in neighbors
        assert HexCoord(0, -1) in neighbors
        assert HexCoord(-1, 0) in neighbors
        assert HexCoord(-1, 1) in neighbors
        assert HexCoord(0, 1) in neighbors

    def test_distance(self):
        """Test grid distance."""
        h1 = HexCoord(0, 0)
        h2 = HexCoord(1, 0)
        assert hex_distance(h1, h2) == 1

        h3 = HexCoord(2, 3)
        # Distance is max(|dq|, |dr|, |ds|)
        # h1(0,0,0) -> h3(2,3,-5)
        # d = max(2, 3, 5) = 5
        assert hex_distance(h1, h3) == 5
        
        # Test specific "101 hexes" scenario
        h_far = HexCoord(100, 0)
        assert hex_distance(h1, h_far) == 100

    def test_pixel_conversion(self):
        """Test to/from pixel conversion (Flat topped)."""
        # Flat top: width = 2 * size, height = sqrt(3) * size
        # spacing_w = 3/2 * size, spacing_h = sqrt(3) * size
        size = 10
        origin = HexCoord(0, 0)
        x, y = hex_to_pixel(origin, size)
        assert x == 0
        assert y == 0
        
        # Neighbor at (1, 0) -> +3/2 width, +sqrt(3)/2 height? 
        # Standard flat top conversion:
        # x = size * (3/2 * q)
        # y = size * (sqrt(3)/2 * q + sqrt(3) * r)
        
        h1 = HexCoord(1, 0) 
        x1, y1 = hex_to_pixel(h1, size)
        assert x1 == 15.0 # 10 * 1.5 * 1
        assert abs(y1 - 8.66) < 0.01 # 10 * 0.866 * 1
        
        # Round trip
        h_back = pixel_to_hex(x1, y1, size)
        assert h_back == h1

