"""
Tests for game.core.math module.

Tests the Vector2 class and math helper functions.
Following TDD: these tests are written BEFORE implementation.
"""
import pytest
import math


class TestVector2Creation:
    """Tests for Vector2 instantiation."""

    def test_default_constructor_creates_zero_vector(self):
        """Vector2() creates a (0, 0) vector."""
        from game.core.math import Vector2

        v = Vector2()

        assert v.x == 0
        assert v.y == 0

    def test_constructor_with_values(self):
        """Vector2(x, y) stores the values."""
        from game.core.math import Vector2

        v = Vector2(3.5, -2.1)

        assert v.x == 3.5
        assert v.y == -2.1

    def test_constructor_converts_integers_to_float(self):
        """Integer arguments are converted to floats."""
        from game.core.math import Vector2

        v = Vector2(5, 10)

        assert isinstance(v.x, float)
        assert isinstance(v.y, float)
        assert v.x == 5.0
        assert v.y == 10.0


class TestVector2Arithmetic:
    """Tests for Vector2 arithmetic operations."""

    def test_add_vectors(self):
        """Vector addition works correctly."""
        from game.core.math import Vector2

        a = Vector2(1, 2)
        b = Vector2(3, 4)

        result = a + b

        assert result.x == 4
        assert result.y == 6

    def test_subtract_vectors(self):
        """Vector subtraction works correctly."""
        from game.core.math import Vector2

        a = Vector2(5, 8)
        b = Vector2(2, 3)

        result = a - b

        assert result.x == 3
        assert result.y == 5

    def test_multiply_vector_by_scalar(self):
        """Vector * scalar works correctly."""
        from game.core.math import Vector2

        v = Vector2(2, 3)

        result = v * 2.5

        assert result.x == 5.0
        assert result.y == 7.5

    def test_scalar_multiply_vector(self):
        """scalar * Vector works correctly (rmul)."""
        from game.core.math import Vector2

        v = Vector2(2, 3)

        result = 2.5 * v

        assert result.x == 5.0
        assert result.y == 7.5

    def test_divide_vector_by_scalar(self):
        """Vector / scalar works correctly."""
        from game.core.math import Vector2

        v = Vector2(10, 20)

        result = v / 2

        assert result.x == 5.0
        assert result.y == 10.0

    def test_negate_vector(self):
        """Negating a vector returns opposite signs."""
        from game.core.math import Vector2

        v = Vector2(3, -4)

        result = -v

        assert result.x == -3
        assert result.y == 4

    def test_operations_return_new_vector(self):
        """Arithmetic operations don't modify originals."""
        from game.core.math import Vector2

        a = Vector2(1, 2)
        b = Vector2(3, 4)

        _ = a + b
        _ = a - b
        _ = a * 2
        _ = -a

        assert a.x == 1
        assert a.y == 2
        assert b.x == 3
        assert b.y == 4


class TestVector2Comparison:
    """Tests for Vector2 equality and comparison."""

    def test_equal_vectors(self):
        """Equal vectors compare as equal."""
        from game.core.math import Vector2

        a = Vector2(1.5, 2.5)
        b = Vector2(1.5, 2.5)

        assert a == b

    def test_unequal_vectors(self):
        """Unequal vectors compare as not equal."""
        from game.core.math import Vector2

        a = Vector2(1, 2)
        b = Vector2(1, 3)

        assert a != b

    def test_not_equal_to_non_vector(self):
        """Vector2 is not equal to non-Vector2 types."""
        from game.core.math import Vector2

        v = Vector2(1, 2)

        assert v != (1, 2)
        assert v != [1, 2]
        assert v != "Vector2(1, 2)"
        assert v != None


class TestVector2Representation:
    """Tests for Vector2 string representation."""

    def test_repr(self):
        """repr shows Vector2 format."""
        from game.core.math import Vector2

        v = Vector2(3.5, -2.0)

        assert repr(v) == "Vector2(3.5, -2.0)"


class TestVector2Length:
    """Tests for Vector2 length calculations."""

    def test_length_of_unit_vector(self):
        """Length of (1, 0) is 1."""
        from game.core.math import Vector2

        v = Vector2(1, 0)

        assert v.length() == 1.0

    def test_length_of_3_4_vector(self):
        """Length of (3, 4) is 5."""
        from game.core.math import Vector2

        v = Vector2(3, 4)

        assert v.length() == 5.0

    def test_length_of_zero_vector(self):
        """Length of (0, 0) is 0."""
        from game.core.math import Vector2

        v = Vector2(0, 0)

        assert v.length() == 0.0

    def test_length_squared(self):
        """length_squared returns length^2 without sqrt."""
        from game.core.math import Vector2

        v = Vector2(3, 4)

        assert v.length_squared() == 25.0


class TestVector2Normalization:
    """Tests for Vector2 normalization."""

    def test_normalize_returns_unit_vector(self):
        """normalize returns a vector of length 1."""
        from game.core.math import Vector2

        v = Vector2(3, 4)

        result = v.normalize()

        assert abs(result.length() - 1.0) < 1e-9

    def test_normalize_preserves_direction(self):
        """normalize preserves the direction."""
        from game.core.math import Vector2

        v = Vector2(3, 4)

        result = v.normalize()

        assert abs(result.x - 0.6) < 1e-9
        assert abs(result.y - 0.8) < 1e-9

    def test_normalize_zero_vector_returns_zero(self):
        """Normalizing zero vector returns zero vector (not error)."""
        from game.core.math import Vector2

        v = Vector2(0, 0)

        result = v.normalize()

        assert result.x == 0
        assert result.y == 0

    def test_normalize_does_not_modify_original(self):
        """normalize returns new vector, doesn't modify original."""
        from game.core.math import Vector2

        v = Vector2(3, 4)

        _ = v.normalize()

        assert v.x == 3
        assert v.y == 4

    def test_normalize_ip_modifies_in_place(self):
        """normalize_ip modifies the vector in place."""
        from game.core.math import Vector2

        v = Vector2(3, 4)

        v.normalize_ip()

        assert abs(v.length() - 1.0) < 1e-9
        assert abs(v.x - 0.6) < 1e-9
        assert abs(v.y - 0.8) < 1e-9

    def test_normalize_ip_zero_vector_stays_zero(self):
        """normalize_ip on zero vector leaves it as zero."""
        from game.core.math import Vector2

        v = Vector2(0, 0)

        v.normalize_ip()  # Should not raise

        assert v.x == 0
        assert v.y == 0


class TestVector2Dot:
    """Tests for Vector2 dot product."""

    def test_dot_product(self):
        """Dot product calculation is correct."""
        from game.core.math import Vector2

        a = Vector2(1, 2)
        b = Vector2(3, 4)

        result = a.dot(b)

        assert result == 11  # 1*3 + 2*4

    def test_dot_orthogonal_is_zero(self):
        """Dot product of orthogonal vectors is 0."""
        from game.core.math import Vector2

        a = Vector2(1, 0)
        b = Vector2(0, 1)

        result = a.dot(b)

        assert result == 0


class TestVector2Distance:
    """Tests for Vector2 distance calculations."""

    def test_distance_to(self):
        """distance_to calculates Euclidean distance."""
        from game.core.math import Vector2

        a = Vector2(0, 0)
        b = Vector2(3, 4)

        result = a.distance_to(b)

        assert result == 5.0

    def test_distance_squared_to(self):
        """distance_squared_to returns distance^2."""
        from game.core.math import Vector2

        a = Vector2(0, 0)
        b = Vector2(3, 4)

        result = a.distance_squared_to(b)

        assert result == 25.0

    def test_distance_to_same_point(self):
        """Distance to same point is 0."""
        from game.core.math import Vector2

        a = Vector2(5, 5)

        assert a.distance_to(a) == 0
        assert a.distance_squared_to(a) == 0


class TestVector2Rotation:
    """Tests for Vector2 rotation."""

    def test_rotate_90_degrees(self):
        """Rotating (1, 0) by 90 degrees gives (0, 1)."""
        from game.core.math import Vector2

        v = Vector2(1, 0)

        result = v.rotate(90)

        assert abs(result.x - 0) < 1e-9
        assert abs(result.y - 1) < 1e-9

    def test_rotate_180_degrees(self):
        """Rotating (1, 0) by 180 degrees gives (-1, 0)."""
        from game.core.math import Vector2

        v = Vector2(1, 0)

        result = v.rotate(180)

        assert abs(result.x - (-1)) < 1e-9
        assert abs(result.y - 0) < 1e-9

    def test_rotate_negative_angle(self):
        """Rotating by negative angle works."""
        from game.core.math import Vector2

        v = Vector2(1, 0)

        result = v.rotate(-90)

        assert abs(result.x - 0) < 1e-9
        assert abs(result.y - (-1)) < 1e-9

    def test_rotate_preserves_length(self):
        """Rotation preserves vector length."""
        from game.core.math import Vector2

        v = Vector2(3, 4)
        original_length = v.length()

        result = v.rotate(45)

        assert abs(result.length() - original_length) < 1e-9

    def test_rotate_does_not_modify_original(self):
        """rotate returns new vector, doesn't modify original."""
        from game.core.math import Vector2

        v = Vector2(1, 0)

        _ = v.rotate(90)

        assert v.x == 1
        assert v.y == 0


class TestVector2AngleTo:
    """Tests for Vector2 angle_to method."""

    def test_angle_to_east(self):
        """Angle from origin to east is 0."""
        from game.core.math import Vector2

        origin = Vector2(0, 0)
        east = Vector2(1, 0)

        result = origin.angle_to(east)

        assert abs(result - 0) < 1e-9

    def test_angle_to_north(self):
        """Angle from origin to north is 90."""
        from game.core.math import Vector2

        origin = Vector2(0, 0)
        north = Vector2(0, 1)

        result = origin.angle_to(north)

        assert abs(result - 90) < 1e-9

    def test_angle_to_west(self):
        """Angle from origin to west is 180 or -180."""
        from game.core.math import Vector2

        origin = Vector2(0, 0)
        west = Vector2(-1, 0)

        result = origin.angle_to(west)

        assert abs(abs(result) - 180) < 1e-9

    def test_angle_to_south(self):
        """Angle from origin to south is -90."""
        from game.core.math import Vector2

        origin = Vector2(0, 0)
        south = Vector2(0, -1)

        result = origin.angle_to(south)

        assert abs(result - (-90)) < 1e-9


class TestVector2Copy:
    """Tests for Vector2 copy method."""

    def test_copy_returns_equal_vector(self):
        """copy returns an equal vector."""
        from game.core.math import Vector2

        v = Vector2(3.5, -2.1)

        result = v.copy()

        assert result == v

    def test_copy_returns_independent_vector(self):
        """copy returns a new object, not the same."""
        from game.core.math import Vector2

        v = Vector2(3.5, -2.1)

        result = v.copy()
        result.x = 99

        assert v.x == 3.5  # Original unchanged


class TestVector2Conversion:
    """Tests for Vector2 tuple conversion methods."""

    def test_as_tuple(self):
        """as_tuple returns (x, y) as floats."""
        from game.core.math import Vector2

        v = Vector2(3.5, -2.1)

        result = v.as_tuple()

        assert result == (3.5, -2.1)
        assert isinstance(result[0], float)
        assert isinstance(result[1], float)

    def test_as_int_tuple(self):
        """as_int_tuple returns (int(x), int(y))."""
        from game.core.math import Vector2

        v = Vector2(3.7, -2.9)

        result = v.as_int_tuple()

        assert result == (3, -2)
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)


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
