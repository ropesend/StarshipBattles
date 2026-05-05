"""
Unit tests for Vector2 class edge cases.

Tests edge cases for __getitem__, __len__, normalize, rotate,
angle_to, and as_int_tuple methods.
"""
import math
import pytest

from game.core.math import Vector2, angle_from_vector, normalize_angle, signed_angle_between


class TestVector2Indexing:
    """Tests for __getitem__ and __len__ methods."""

    def test_getitem_index_0_returns_x(self):
        """v[0] returns the x component."""
        v = Vector2(5.0, 10.0)
        assert v[0] == 5.0

    def test_getitem_index_1_returns_y(self):
        """v[1] returns the y component."""
        v = Vector2(5.0, 10.0)
        assert v[1] == 10.0

    def test_getitem_index_2_raises_index_error(self):
        """v[2] raises IndexError."""
        v = Vector2(5.0, 10.0)
        with pytest.raises(IndexError, match="Vector2 index out of range"):
            _ = v[2]

    def test_getitem_negative_index_raises_index_error(self):
        """v[-1] raises IndexError (no Python-style negative indexing)."""
        v = Vector2(5.0, 10.0)
        with pytest.raises(IndexError):
            _ = v[-1]

    def test_len_returns_2(self):
        """len(v) returns 2."""
        v = Vector2(100.0, 200.0)
        assert len(v) == 2


class TestVector2Normalize:
    """Tests for normalize method edge cases."""

    def test_normalize_zero_vector_returns_zero(self):
        """Zero vector normalizes to zero vector (avoid division by zero)."""
        v = Vector2(0, 0)
        result = v.normalize()
        assert result.x == 0
        assert result.y == 0

    def test_normalize_unit_vector_unchanged(self):
        """Already-normalized vector remains unchanged."""
        v = Vector2(1, 0)  # Already unit length
        result = v.normalize()
        assert abs(result.x - 1.0) < 1e-10
        assert abs(result.y - 0.0) < 1e-10

    def test_normalize_returns_unit_length(self):
        """Normalized vector has length 1."""
        v = Vector2(3.0, 4.0)  # length = 5
        result = v.normalize()
        assert abs(result.length() - 1.0) < 1e-10


class TestVector2Rotate:
    """Tests for rotate method edge cases."""

    def test_rotate_negative_angle(self):
        """Rotation by -90 degrees works correctly."""
        v = Vector2(1, 0)
        result = v.rotate(-90)
        # -90 degrees: (1, 0) -> (0, -1)
        assert abs(result.x - 0.0) < 1e-10
        assert abs(result.y - (-1.0)) < 1e-10

    def test_rotate_360_returns_original(self):
        """Rotation by 360 degrees returns approximately original."""
        v = Vector2(3.0, 4.0)
        result = v.rotate(360)
        assert abs(result.x - 3.0) < 1e-10
        assert abs(result.y - 4.0) < 1e-10

    def test_rotate_720_returns_original(self):
        """Rotation by 720 degrees returns approximately original."""
        v = Vector2(5.0, 12.0)
        result = v.rotate(720)
        assert abs(result.x - 5.0) < 1e-10
        assert abs(result.y - 12.0) < 1e-10

    def test_rotate_90_degrees(self):
        """Rotation by 90 degrees: (1, 0) -> (0, 1)."""
        v = Vector2(1, 0)
        result = v.rotate(90)
        assert abs(result.x - 0.0) < 1e-10
        assert abs(result.y - 1.0) < 1e-10


class TestVector2AngleTo:
    """Tests for angle_to method edge cases."""

    def test_angle_to_right(self):
        """Angle from origin to (1, 0) is 0 degrees."""
        origin = Vector2(0, 0)
        target = Vector2(1, 0)
        angle = origin.angle_to(target)
        assert abs(angle - 0.0) < 1e-10

    def test_angle_to_up(self):
        """Angle from origin to (0, 1) is 90 degrees (standard math coords)."""
        origin = Vector2(0, 0)
        target = Vector2(0, 1)
        angle = origin.angle_to(target)
        assert abs(angle - 90.0) < 1e-10

    def test_angle_to_down(self):
        """Angle from origin to (0, -1) is -90 degrees."""
        origin = Vector2(0, 0)
        target = Vector2(0, -1)
        angle = origin.angle_to(target)
        assert abs(angle - (-90.0)) < 1e-10

    def test_angle_to_same_point(self):
        """Angle to same point is 0 degrees."""
        v = Vector2(5, 5)
        angle = v.angle_to(v)
        assert abs(angle - 0.0) < 1e-10

    def test_angle_to_left(self):
        """Angle from origin to (-1, 0) is 180 degrees."""
        origin = Vector2(0, 0)
        target = Vector2(-1, 0)
        angle = origin.angle_to(target)
        assert abs(abs(angle) - 180.0) < 1e-10  # Could be +180 or -180


class TestVector2AsIntTuple:
    """Tests for as_int_tuple method edge cases."""

    def test_as_int_tuple_truncates(self):
        """Positive fractional values truncate toward zero."""
        v = Vector2(1.9, 2.1)
        result = v.as_int_tuple()
        assert result == (1, 2)

    def test_as_int_tuple_negative(self):
        """Negative fractional values truncate toward zero."""
        v = Vector2(-0.5, -1.7)
        result = v.as_int_tuple()
        # int(-0.5) = 0, int(-1.7) = -1
        assert result == (0, -1)

    def test_as_int_tuple_whole_numbers(self):
        """Whole float numbers convert cleanly."""
        v = Vector2(5.0, 10.0)
        result = v.as_int_tuple()
        assert result == (5, 10)

    def test_as_int_tuple_large_values(self):
        """Large values convert correctly."""
        v = Vector2(1000000.9, -999999.1)
        result = v.as_int_tuple()
        assert result == (1000000, -999999)


class TestAngleFromVector:
    """Tests for angle_from_vector utility."""

    def test_right_is_zero(self):
        assert angle_from_vector(1, 0) == pytest.approx(0.0)

    def test_down_is_90(self):
        assert angle_from_vector(0, 1) == pytest.approx(90.0)

    def test_left_is_180(self):
        assert angle_from_vector(-1, 0) == pytest.approx(180.0)

    def test_up_is_270(self):
        assert angle_from_vector(0, -1) == pytest.approx(270.0)

    def test_always_positive(self):
        """Result should always be in [0, 360)."""
        result = angle_from_vector(-1, -0.001)
        assert 0 <= result < 360


class TestNormalizeAngle:
    """Tests for normalize_angle utility edge cases."""

    @pytest.mark.parametrize(
        ("raw_angle", "expected"),
        [
            (0, 0),
            (180, 180),
            (-180, 180),
            (360, 0),
            (-360, 0),
            (540, 180),
            (-540, 180),
            (181, -179),
            (-181, 179),
            (1081, 1),
            (-1081, -1),
        ],
    )
    def test_normalizes_to_negative_180_exclusive_positive_180_inclusive(
        self,
        raw_angle,
        expected,
    ):
        assert normalize_angle(raw_angle) == pytest.approx(expected)


class TestSignedAngleBetween:
    """Tests for signed_angle_between() — signed angle from direction A to B."""

    def test_parallel_vectors_zero(self):
        """Same direction → 0°."""
        assert signed_angle_between(Vector2(1, 0), Vector2(1, 0)) == pytest.approx(0.0)

    def test_antiparallel_right_to_left(self):
        """(1,0) to (-1,0) → 180°."""
        result = signed_angle_between(Vector2(1, 0), Vector2(-1, 0))
        assert abs(result) == pytest.approx(180.0)

    def test_antiparallel_left_to_right(self):
        """(-1,0) to (1,0) → 180° (the SEEKER-TURN-002 case)."""
        result = signed_angle_between(Vector2(-1, 0), Vector2(1, 0))
        assert abs(result) == pytest.approx(180.0)

    def test_90_degrees_counterclockwise(self):
        """(1,0) to (0,1) → +90°."""
        assert signed_angle_between(Vector2(1, 0), Vector2(0, 1)) == pytest.approx(90.0)

    def test_90_degrees_clockwise(self):
        """(1,0) to (0,-1) → -90°."""
        assert signed_angle_between(Vector2(1, 0), Vector2(0, -1)) == pytest.approx(-90.0)

    def test_45_degrees(self):
        """(1,0) to (1,1) normalized → +45°."""
        b = Vector2(1, 1).normalize()
        assert signed_angle_between(Vector2(1, 0), b) == pytest.approx(45.0, abs=0.01)

    def test_small_angle(self):
        """Nearly parallel → small positive angle."""
        b = Vector2(1, 0.01).normalize()
        result = signed_angle_between(Vector2(1, 0), b)
        assert 0 < result < 2  # Small positive
