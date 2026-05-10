"""Tests for math helper functions and edge cases."""
import pytest


class TestVector2EdgeCases:
    """Tests for edge cases and error handling."""

    def test_divide_by_zero_raises(self):
        """Division by zero raises ZeroDivisionError."""
        from game.core.math import Vector2

        v = Vector2(1, 2)

        with pytest.raises(ZeroDivisionError):
            _ = v / 0

    def test_very_small_vector_normalization(self):
        """Very small vectors can be normalized."""
        from game.core.math import Vector2

        v = Vector2(1e-10, 1e-10)

        result = v.normalize()

        assert abs(result.length() - 1.0) < 1e-6

    def test_very_large_vector(self):
        """Very large vectors work correctly."""
        from game.core.math import Vector2

        v = Vector2(1e10, 1e10)

        result = v.normalize()

        assert abs(result.length() - 1.0) < 1e-6


class TestHelperFunctions:
    """Tests for math helper functions."""

    def test_clamp_within_range(self):
        """clamp returns value when within range."""
        from game.core.math import clamp

        assert clamp(5, 0, 10) == 5

    def test_clamp_below_minimum(self):
        """clamp returns min when value below min."""
        from game.core.math import clamp

        assert clamp(-5, 0, 10) == 0

    def test_clamp_above_maximum(self):
        """clamp returns max when value above max."""
        from game.core.math import clamp

        assert clamp(15, 0, 10) == 10

    def test_clamp_at_boundary(self):
        """clamp returns value at exact boundaries."""
        from game.core.math import clamp

        assert clamp(0, 0, 10) == 0
        assert clamp(10, 0, 10) == 10

    def test_lerp_at_zero(self):
        """lerp(a, b, 0) returns a."""
        from game.core.math import lerp

        assert lerp(10, 20, 0) == 10

    def test_lerp_at_one(self):
        """lerp(a, b, 1) returns b."""
        from game.core.math import lerp

        assert lerp(10, 20, 1) == 20

    def test_lerp_at_half(self):
        """lerp(a, b, 0.5) returns midpoint."""
        from game.core.math import lerp

        assert lerp(10, 20, 0.5) == 15

    def test_lerp_beyond_range(self):
        """lerp works with t outside [0, 1]."""
        from game.core.math import lerp

        assert lerp(10, 20, 2) == 30  # Extrapolation
        assert lerp(10, 20, -1) == 0  # Extrapolation

    def test_angle_diff_same_angle(self):
        """angle_diff of same angles is 0."""
        from game.core.math import angle_diff

        assert angle_diff(45, 45) == 0

    def test_angle_diff_small_difference(self):
        """angle_diff returns shortest path."""
        from game.core.math import angle_diff

        assert abs(angle_diff(10, 20) - 10) < 1e-9

    def test_angle_diff_wrapping(self):
        """angle_diff wraps around 360."""
        from game.core.math import angle_diff

        # 350 to 10 is 20 degrees the short way
        result = angle_diff(350, 10)
        assert abs(result - 20) < 1e-9

    def test_angle_diff_negative(self):
        """angle_diff can return negative for shortest path."""
        from game.core.math import angle_diff

        # 10 to 350 is -20 degrees the short way
        result = angle_diff(10, 350)
        assert abs(result - (-20)) < 1e-9

    def test_angle_diff_opposite_directions(self):
        """angle_diff for opposite angles is 180 or -180."""
        from game.core.math import angle_diff

        result = angle_diff(0, 180)
        assert abs(abs(result) - 180) < 1e-9


class TestPygameCompatibility:
    """Tests to verify compatibility with pygame.math.Vector2 API."""

    def test_vector2_has_expected_attributes(self):
        """Vector2 has x and y attributes."""
        from game.core.math import Vector2

        v = Vector2(1, 2)

        assert hasattr(v, 'x')
        assert hasattr(v, 'y')

    def test_vector2_has_expected_methods(self):
        """Vector2 has all expected methods."""
        from game.core.math import Vector2

        v = Vector2(1, 2)

        expected_methods = [
            'length', 'length_squared', 'normalize', 'normalize_ip',
            'dot', 'distance_to', 'distance_squared_to', 'rotate',
            'angle_to', 'copy', 'as_tuple', 'as_int_tuple'
        ]

        for method_name in expected_methods:
            assert hasattr(v, method_name), f"Missing method: {method_name}"
            assert callable(getattr(v, method_name)), f"Not callable: {method_name}"
