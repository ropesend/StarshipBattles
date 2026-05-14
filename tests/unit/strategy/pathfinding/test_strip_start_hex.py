"""
Unit tests for strip_start_hex utility function.

PROJ-204 Phase 2: Consolidate path stripping logic (CQ-42).
"""

import pytest
from game.core.hex_math import HexCoord
from game.strategy.services.galaxy_pathfinding_service import GalaxyPathfindingService

strip_start_hex = GalaxyPathfindingService.strip_start_hex


class TestStripStartHex:
    """Tests for strip_start_hex function."""

    def test_strips_matching_start_hex(self):
        """Should remove first hex when it matches current location."""
        current_location = HexCoord(0, 0)
        path = [HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0)]

        result = strip_start_hex(current_location, path)

        assert result == [HexCoord(1, 0), HexCoord(2, 0)]

    def test_preserves_path_when_start_differs(self):
        """Should preserve path when first hex doesn't match."""
        current_location = HexCoord(0, 0)
        path = [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]

        result = strip_start_hex(current_location, path)

        assert result == [HexCoord(1, 0), HexCoord(2, 0), HexCoord(3, 0)]

    def test_empty_path_returns_empty(self):
        """Should return empty list for empty path."""
        current_location = HexCoord(0, 0)
        path = []

        result = strip_start_hex(current_location, path)

        assert result == []

    def test_none_path_returns_none(self):
        """Should return None for None path."""
        current_location = HexCoord(0, 0)

        result = strip_start_hex(current_location, None)

        assert result is None

    def test_single_element_matching_returns_empty(self):
        """Should return empty list when single-element path matches."""
        current_location = HexCoord(5, 5)
        path = [HexCoord(5, 5)]

        result = strip_start_hex(current_location, path)

        assert result == []

    def test_single_element_not_matching_preserves(self):
        """Should preserve single-element path when it doesn't match."""
        current_location = HexCoord(0, 0)
        path = [HexCoord(5, 5)]

        result = strip_start_hex(current_location, path)

        assert result == [HexCoord(5, 5)]

    def test_works_with_tuple_path(self):
        """Should work with tuple input and return same type."""
        current_location = HexCoord(0, 0)
        path = (HexCoord(0, 0), HexCoord(1, 0), HexCoord(2, 0))

        result = strip_start_hex(current_location, path)

        assert result == (HexCoord(1, 0), HexCoord(2, 0))
        assert isinstance(result, tuple)

    def test_preserves_list_type(self):
        """Should preserve list type on return."""
        current_location = HexCoord(0, 0)
        path = [HexCoord(0, 0), HexCoord(1, 0)]

        result = strip_start_hex(current_location, path)

        assert isinstance(result, list)
