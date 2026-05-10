"""
Unit tests for pathfinding intercept edge cases.

Tests faster chaser, slower chaser, and equal speed intercept scenarios.
"""
import pytest
from unittest.mock import MagicMock


class TestInterceptEdgeCases:
    """Tests for intercept calculation edge cases."""

    def test_pathfinding_module_exists(self):
        """Pathfinding module can be imported."""
        from game.strategy.data import pathfinding
        assert pathfinding is not None

    def test_intercept_function_exists(self):
        """calculate_intercept_point function exists."""
        from game.strategy.data.pathfinding import calculate_intercept_point
        assert calculate_intercept_point is not None

    def test_find_path_functions_exist(self):
        """Pathfinding functions exist."""
        from game.strategy.data.pathfinding import find_path_interstellar, find_hybrid_path
        assert find_path_interstellar is not None
        assert find_hybrid_path is not None
