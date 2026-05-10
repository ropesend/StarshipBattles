"""Tests for Vector2 geometric operations: length, normalization, dot, distance, rotation, angle."""
import pytest


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
