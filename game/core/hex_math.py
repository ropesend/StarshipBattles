r"""
Hex Math - Hexagonal Grid Mathematics

This module provides utilities for working with hexagonal grids in the
core layer. Used for galaxy maps, fleet positions, and pathfinding.

Coordinate System:
    Uses AXIAL coordinates (q, r) for storage efficiency.
    Internally tracks cube coordinates (q, r, s) where q + r + s = 0.

    Flat-topped hexes (pointy sides on left/right):

             ___
            /   \
           /     \
           \     /
            \___/

    Axis orientation:
        +q: Right/down-right
        +r: Down
        +s: Up-left (derived: s = -q - r)

    The origin hex (0, 0) is at the center of the galaxy.

Distance Calculation:
    Grid distance (number of hex steps) uses cube coordinates:
        distance = max(|dq|, |dr|, |ds|)

    This gives the minimum number of hexes to traverse.

Pixel Conversion:
    hex_to_pixel(hex, size): Convert hex coord to screen position
        x = size * (3/2 * q)
        y = size * (sqrt(3)/2 * q + sqrt(3) * r)

    pixel_to_hex(x, y, size): Convert screen position to nearest hex
        Uses rounding with constraint preservation (q + r + s = 0)

Utility Functions:
    - hex_distance(a, b): Grid distance between hexes
    - hex_ring(radius): All hexes at distance 'radius' from origin
    - hex_lerp(a, b, t): Interpolate between hexes
    - hex_linedraw(a, b): All hexes along a line
    - neighbors(): Get 6 adjacent hexes

Serialization:
    hex_to_dict(coord): Serialize to {'q': q, 'r': r}
    hex_from_dict(data): Deserialize from dict

Example:
    # Create coordinates
    start = HexCoord(0, 0)
    dest = HexCoord(3, -1)

    # Get distance
    dist = hex_distance(start, dest)  # Returns 3

    # Get neighbors
    adjacent = start.neighbors()  # 6 HexCoord objects

    # Convert to pixels
    px, py = hex_to_pixel(dest, size=50)
"""
import math


class HexCoord:
    """
    Represents a specific hexagon in a flat-topped axial coordinate system (q, r).
    Constraint: q + r + s = 0
    """
    __slots__ = ('q', 'r', 's')

    def __init__(self, q, r):
        self.q = q
        self.r = r
        self.s = -q - r

    @property
    def cube(self):
        return (self.q, self.r, self.s)

    def __eq__(self, other):
        if not isinstance(other, HexCoord):
            return False
        return self.q == other.q and self.r == other.r

    def __hash__(self):
        return hash((self.q, self.r))

    def __repr__(self):
        return f"HexCoord({self.q}, {self.r})"

    def __add__(self, other):
        if isinstance(other, HexCoord):
            return HexCoord(self.q + other.q, self.r + other.r)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, HexCoord):
            return HexCoord(self.q - other.q, self.r - other.r)
        return NotImplemented

    def neighbors(self):
        """Return the 6 direct neighbors."""
        directions = [
            HexCoord(1, 0), HexCoord(1, -1), HexCoord(0, -1),
            HexCoord(-1, 0), HexCoord(-1, 1), HexCoord(0, 1)
        ]
        return [self + d for d in directions]


def hex_distance(a, b):
    """Calculate grid distance between two hexes."""
    # Convert vectors to cube coords for easy distance
    # distance = max(|dq|, |dr|, |ds|)
    vec = a - b
    return max(abs(vec.q), abs(vec.r), abs(vec.s))


def hex_to_pixel(hex_coord, size):
    """
    Convert axial hex coords to flat-topped pixel coordinates.
    size: radius of the hex (center to corner)
    Returns (x, y)
    """
    q = hex_coord.q
    r = hex_coord.r
    x = size * (3./2 * q)
    y = size * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
    return x, y


def pixel_to_hex(x, y, size):
    """
    Convert pixel coordinates back to axial hex coords.
    Uses rounding to find nearest integer hex.
    """
    q_float = (2./3 * x) / size
    r_float = (-1./3 * x + math.sqrt(3)/3 * y) / size
    s_float = -q_float - r_float
    return _hex_round(q_float, r_float, s_float)


def _hex_round(q, r, s):
    """Round partial cube coordinates to nearest valid integer hex."""
    qi = round(q)
    ri = round(r)
    si = round(s)

    q_diff = abs(qi - q)
    r_diff = abs(ri - r)
    s_diff = abs(si - s)

    if q_diff > r_diff and q_diff > s_diff:
        qi = -ri - si
    elif r_diff > s_diff:
        ri = -qi - si
    else:
        si = -qi - ri

    return HexCoord(qi, ri)


def hex_ring(radius):
    """
    Return all HexCoords at distance 'radius' from (0,0).

    Uses the standard hex ring algorithm:
    1. Start at direction[4] * radius (the -q, +r corner)
    2. Walk around the ring, taking 'radius' steps in each of 6 directions
    3. Each full circuit visits exactly 6*radius hexes
    """
    results = []
    if radius == 0:
        return [HexCoord(0, 0)]

    directions = [
        HexCoord(1, 0), HexCoord(1, -1), HexCoord(0, -1),
        HexCoord(-1, 0), HexCoord(-1, 1), HexCoord(0, 1)
    ]

    # Start at direction[4] scaled by radius
    curr = HexCoord(directions[4].q * radius, directions[4].r * radius)

    for i in range(6):
        walk_dir = directions[i]
        for _ in range(radius):
            results.append(curr)
            curr = curr + walk_dir

    return results


def hex_lerp(a, b, t):
    """Linear interpolation between two HexCoords."""
    # We need floating point lerp on the cube coords
    # HexCoord only stores q, r. s is derived.
    # But lerp needs to work on floats.
    # Let's do q, r lerp and then round?
    # But for strict correctness we should lerp q, r, s.

    # Simple lerp:
    q = a.q + (b.q - a.q) * t
    r = a.r + (b.r - a.r) * t
    s = a.s + (b.s - a.s) * t # s is needed for rounding

    return _hex_round(q, r, s)

def hex_linedraw(a, b):
    """Return list of hexes forming a line from a to b."""
    N = hex_distance(a, b)
    results = []
    if N == 0:
        return [a]

    # We explicitly calculate t steps
    step = 1.0 / max(N, 1)
    for i in range(N + 1):
        results.append(hex_lerp(a, b, step * i))
    return results


# Serialization helpers for save/load system
def hex_to_dict(coord: HexCoord) -> dict:
    """
    Serialize HexCoord to dict.

    Args:
        coord: HexCoord to serialize

    Returns:
        Dict with 'q' and 'r' keys
    """
    return {'q': coord.q, 'r': coord.r}


def hex_from_dict(data: dict) -> HexCoord:
    """
    Deserialize HexCoord from dict.

    Args:
        data: Dict with 'q' and 'r' keys

    Returns:
        Reconstructed HexCoord
    """
    return HexCoord(data['q'], data['r'])
