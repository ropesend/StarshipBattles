"""
Core math utilities for Starship Battles.

Provides framework-agnostic Vector2 implementation and math helpers.
No pygame or other framework dependencies.
"""
from __future__ import annotations
import math as _math
from typing import Tuple, Union


class Vector2:
    """
    2D vector class compatible with pygame.math.Vector2 API.

    Provides all common vector operations for game physics and rendering.
    Uses __slots__ for memory efficiency.
    """

    __slots__ = ('x', 'y')

    def __init__(self, x: float = 0, y: float = None):
        """
        Create a new Vector2.

        Args:
            x: X component, or a sequence/vector-like object with x,y attributes
            y: Y component (optional if x is a vector-like object)
        """
        if y is None:
            # x might be a sequence or vector-like object
            if hasattr(x, 'x') and hasattr(x, 'y'):
                # Another Vector2 or pygame.math.Vector2
                self.x = float(x.x)
                self.y = float(x.y)
            elif hasattr(x, '__iter__'):
                # Tuple, list, or other sequence
                vals = list(x)
                self.x = float(vals[0])
                self.y = float(vals[1])
            else:
                # Single value - assume both x and y are this value (like pygame)
                self.x = float(x)
                self.y = float(x)
        else:
            self.x = float(x)
            self.y = float(y)

    def __add__(self, other) -> 'Vector2':
        """Add two vectors (supports any object with x, y attributes)."""
        return Vector2(self.x + other.x, self.y + other.y)

    def __radd__(self, other) -> 'Vector2':
        """Reverse add (supports any object with x, y attributes)."""
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> 'Vector2':
        """Subtract two vectors (supports any object with x, y attributes)."""
        return Vector2(self.x - other.x, self.y - other.y)

    def __rsub__(self, other) -> 'Vector2':
        """Reverse subtract (supports any object with x, y attributes)."""
        return Vector2(other.x - self.x, other.y - self.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        """Multiply vector by scalar."""
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> 'Vector2':
        """Multiply scalar by vector (reverse)."""
        return Vector2(self.x * scalar, self.y * scalar)

    def __truediv__(self, scalar: float) -> 'Vector2':
        """Divide vector by scalar."""
        return Vector2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> 'Vector2':
        """Negate vector."""
        return Vector2(-self.x, -self.y)

    def __eq__(self, other: object) -> bool:
        """Check equality with another vector-like object (supports pygame.math.Vector2)."""
        if not hasattr(other, 'x') or not hasattr(other, 'y'):
            return False
        return self.x == other.x and self.y == other.y

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Vector2({self.x}, {self.y})"

    def __iter__(self):
        """Allow iteration over x, y for sequence compatibility."""
        yield self.x
        yield self.y

    def __getitem__(self, index: int) -> float:
        """Allow indexing [0] for x, [1] for y for sequence compatibility."""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Vector2 index out of range")

    def __len__(self) -> int:
        """Return length 2 for sequence compatibility."""
        return 2

    def length(self) -> float:
        """Return the length (magnitude) of the vector."""
        return _math.sqrt(self.x * self.x + self.y * self.y)

    def length_squared(self) -> float:
        """Return the squared length (avoids sqrt for comparisons)."""
        return self.x * self.x + self.y * self.y

    def normalize(self) -> 'Vector2':
        """
        Return a normalized (unit length) copy of this vector.

        Returns zero vector if this vector has zero length.
        """
        length = self.length()
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)

    def normalize_ip(self) -> None:
        """
        Normalize this vector in place.

        Does nothing if vector has zero length.
        """
        length = self.length()
        if length != 0:
            self.x /= length
            self.y /= length

    def dot(self, other) -> float:
        """Return the dot product with another vector (supports any object with x, y)."""
        return self.x * other.x + self.y * other.y

    def distance_to(self, other) -> float:
        """Return the distance to another vector (supports any object with x, y)."""
        return (self - other).length()

    def distance_squared_to(self, other) -> float:
        """Return the squared distance to another vector (supports any object with x, y)."""
        return (self - other).length_squared()

    def rotate(self, angle_degrees: float) -> 'Vector2':
        """
        Return a copy of this vector rotated by the given angle.

        Args:
            angle_degrees: Angle in degrees (counter-clockwise positive)
        """
        angle_rad = _math.radians(angle_degrees)
        cos_a = _math.cos(angle_rad)
        sin_a = _math.sin(angle_rad)
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a
        )

    def angle_to(self, other: 'Vector2') -> float:
        """
        Return the angle from this point to another point in degrees.

        Uses standard math convention: 0 = right, 90 = up.
        """
        return _math.degrees(_math.atan2(other.y - self.y, other.x - self.x))

    def copy(self) -> 'Vector2':
        """Return a copy of this vector."""
        return Vector2(self.x, self.y)

    def as_tuple(self) -> Tuple[float, float]:
        """Return vector as (x, y) tuple of floats."""
        return (self.x, self.y)

    def as_int_tuple(self) -> Tuple[int, int]:
        """Return vector as (x, y) tuple of integers."""
        return (int(self.x), int(self.y))


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp a value to a range.

    Args:
        value: The value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        The clamped value
    """
    if value < min_val:
        return min_val
    if value > max_val:
        return max_val
    return value


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between two values.

    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0 = a, 1 = b)

    Returns:
        Interpolated value (can extrapolate if t outside [0, 1])
    """
    return a + (b - a) * t


def angle_from_vector(dx: float, dy: float) -> float:
    """
    Convert a direction vector to an angle in degrees, normalized to [0, 360).

    Args:
        dx: X component of direction
        dy: Y component of direction

    Returns:
        Angle in degrees, 0 = right, 90 = down, normalized to [0, 360)
    """
    return _math.degrees(_math.atan2(dy, dx)) % 360


def normalize_angle(angle: float) -> float:
    """
    Normalize an angle to the range (-180, 180].

    Args:
        angle: Angle in degrees (any value)

    Returns:
        Equivalent angle in the range (-180, 180]
    """
    angle = angle % 360
    if angle > 180:
        angle -= 360
    return angle


def angle_diff(from_angle: float, to_angle: float) -> float:
    """
    Calculate the shortest angular difference between two angles.

    Args:
        from_angle: Starting angle in degrees
        to_angle: Target angle in degrees

    Returns:
        Signed angle difference in degrees (-180 to 180)
    """
    diff = (to_angle - from_angle) % 360
    if diff > 180:
        diff -= 360
    return diff
