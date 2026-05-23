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
import random
from typing import Any, FrozenSet, List, Optional, Set, Tuple


class HexCoord:
    """
    Represents a specific hexagon in a flat-topped axial coordinate system (q, r).
    Constraint: q + r + s = 0
    """
    __slots__ = ('q', 'r', 's')

    def __init__(self, q: int, r: int) -> None:
        self.q: int = q
        self.r: int = r
        self.s: int = -q - r

    @property
    def cube(self) -> Tuple[int, int, int]:
        return (self.q, self.r, self.s)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HexCoord):
            return False
        return self.q == other.q and self.r == other.r

    def __hash__(self) -> int:
        return hash((self.q, self.r))

    def __repr__(self) -> str:
        return f"HexCoord({self.q}, {self.r})"

    def __add__(self, other: 'HexCoord') -> 'HexCoord':
        if isinstance(other, HexCoord):
            return HexCoord(self.q + other.q, self.r + other.r)
        return NotImplemented

    def __sub__(self, other: 'HexCoord') -> 'HexCoord':
        if isinstance(other, HexCoord):
            return HexCoord(self.q - other.q, self.r - other.r)
        return NotImplemented

    def neighbors(self) -> List['HexCoord']:
        """Return the 6 direct neighbors."""
        directions = [
            HexCoord(1, 0), HexCoord(1, -1), HexCoord(0, -1),
            HexCoord(-1, 0), HexCoord(-1, 1), HexCoord(0, 1)
        ]
        return [self + d for d in directions]


def hex_distance(a: HexCoord, b: HexCoord) -> int:
    """Calculate grid distance between two hexes."""
    # Convert vectors to cube coords for easy distance
    # distance = max(|dq|, |dr|, |ds|)
    vec = a - b
    return max(abs(vec.q), abs(vec.r), abs(vec.s))


def hex_to_pixel(hex_coord: HexCoord, size: float) -> Tuple[float, float]:
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


def hex_axial_to_cartesian(
    q: float,
    r: float,
    center_q: float = 0.0,
    center_r: float = 0.0
) -> Tuple[float, float]:
    """
    Convert axial hex coordinates to approximate Cartesian (x, y).

    Maps flat-topped hexagonal axial coordinates to a 2D Cartesian plane.
    This is a raw coordinate conversion without pixel scaling - for UI
    rendering, use hex_to_pixel() instead.

    Args:
        q: Axial q coordinate
        r: Axial r coordinate
        center_q: Center q to compute relative offset (default 0.0)
        center_r: Center r to compute relative offset (default 0.0)

    Returns:
        Tuple (x, y) in Cartesian coordinates
    """
    dq = q - center_q
    dr = r - center_r
    x = dq + dr * 0.5
    y = dr * (math.sqrt(3.0) / 2.0)
    return x, y


def pixel_to_hex(x: float, y: float, size: float) -> 'HexCoord':
    """
    Convert pixel coordinates back to axial hex coords.
    Uses rounding to find nearest integer hex.
    """
    q_float = (2./3 * x) / size
    r_float = (-1./3 * x + math.sqrt(3)/3 * y) / size
    s_float = -q_float - r_float
    return _hex_round(q_float, r_float, s_float)


def _hex_round(q: float, r: float, s: float) -> HexCoord:
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


def hex_ring(radius: int) -> List[HexCoord]:
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


def hex_circle_filled(center: HexCoord, radius: int) -> FrozenSet[HexCoord]:
    """
    Return all HexCoords within distance 'radius' from center (inclusive).

    This creates a filled hexagonal area (disc) containing all hexes
    from distance 0 to 'radius'.

    Args:
        center: The center hex coordinate
        radius: Maximum distance from center (inclusive)

    Returns:
        FrozenSet of all HexCoord within the specified radius

    Example:
        radius=0 -> 1 hex (just center)
        radius=1 -> 7 hexes (center + 6 neighbors)
        radius=2 -> 19 hexes
        radius=5 -> 91 hexes (Dyson Sphere zone)
    """
    result = set()
    for r in range(radius + 1):
        for hex_coord in hex_ring(r):
            result.add(center + hex_coord)
    return frozenset(result)


def hex_lerp(a: HexCoord, b: HexCoord, t: float) -> HexCoord:
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

def hex_linedraw(a: HexCoord, b: HexCoord) -> List[HexCoord]:
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
def hex_to_dict(coord: HexCoord) -> dict[str, int]:
    """
    Serialize HexCoord to dict.

    Args:
        coord: HexCoord to serialize

    Returns:
        Dict with 'q' and 'r' keys
    """
    return {'q': coord.q, 'r': coord.r}


def hex_from_dict(data: dict[str, int]) -> HexCoord:
    """
    Deserialize HexCoord from dict.

    Args:
        data: Dict with 'q' and 'r' keys

    Returns:
        Reconstructed HexCoord
    """
    return HexCoord(data['q'], data['r'])


def hex_from_dict_safe(
    data: dict[str, Any],
    key: str = 'location',
    default: Optional[HexCoord] = None
) -> Optional[HexCoord]:
    """
    Deserialize a HexCoord from a nested dict, returning default on failure.

    Safely extracts a HexCoord from ``data[key]``, handling missing keys,
    None values, and malformed dicts without raising exceptions.

    Args:
        data: Outer dict containing the hex coordinate under *key*
        key: Key to look up in *data* (default ``'location'``)
        default: Value to return when deserialization fails

    Returns:
        Deserialized HexCoord, or *default* if the value is missing/invalid
    """
    try:
        raw = data.get(key)
        if raw is None:
            return default
        return HexCoord(raw['q'], raw['r'])
    except (KeyError, TypeError, ValueError):
        return default


def hex_random_cluster(
    center: HexCoord,
    target_size: int,
    rng: random.Random,
    avoid: FrozenSet[HexCoord] = frozenset()
) -> FrozenSet[HexCoord]:
    """
    Generate a random connected cluster of hexes around a center point.

    Uses a frontier expansion algorithm to grow an irregular connected shape.
    Returns the cluster as offsets relative to center (not absolute coordinates).

    Args:
        center: The center hex for the cluster (absolute coordinates)
        target_size: Desired number of hexes in the cluster
        rng: Random number generator for deterministic results
        avoid: Set of absolute hex coordinates to exclude from the cluster

    Returns:
        FrozenSet of HexCoord offsets relative to center (includes (0,0) for center)

    Example:
        rng = random.Random(42)
        offsets = hex_random_cluster(HexCoord(5, 3), target_size=7, rng=rng)
        # offsets might be {HexCoord(0,0), HexCoord(1,0), HexCoord(0,1), ...}
        # To get absolute positions: {center + offset for offset in offsets}
    """
    if target_size <= 0:
        return frozenset()

    # Work in absolute coordinates during generation
    cluster: Set[HexCoord] = {center}

    # Initialize frontier with valid neighbors (not in avoid, not already in cluster)
    frontier: Set[HexCoord] = set()
    for neighbor in center.neighbors():
        if neighbor not in avoid and neighbor not in cluster:
            frontier.add(neighbor)

    # Grow cluster by adding random frontier hexes
    while len(cluster) < target_size and frontier:
        # Pick random hex from frontier
        frontier_list = list(frontier)
        chosen = rng.choice(frontier_list)

        # Add to cluster
        cluster.add(chosen)
        frontier.remove(chosen)

        # Add chosen's neighbors to frontier (if valid)
        for neighbor in chosen.neighbors():
            if neighbor not in avoid and neighbor not in cluster and neighbor not in frontier:
                frontier.add(neighbor)

    # Convert to offsets relative to center
    offsets = frozenset({h - center for h in cluster})
    return offsets
