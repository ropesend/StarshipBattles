"""Tests for Vector2 basic operations: creation, arithmetic, comparison, representation."""
import pytest


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
