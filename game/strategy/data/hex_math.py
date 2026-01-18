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
    """
    results = []
    if radius == 0:
        return [HexCoord(0, 0)]
    
    # Start at top-left-ish? (direction 4 scaled by radius)
    # Standard algo: pick a direction, scale by radius, then walk around
    
    # Directions: (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
    # Start at (-radius, radius) which is direction 4 * radius?
    # Let's use standard walk.
    
    curr = HexCoord(-1, 1) # Direction 4
    # Actually, simplistic way:
    # Start at q = -radius, r = 0? No that's direction 3 (Left) * radius?
    # Direction 4 is (-1, 1). Multiplied by radius: (-radius, radius).
    
    # Let's use the neighbors directions list to walk
    directions = [
        HexCoord(1, 0), HexCoord(1, -1), HexCoord(0, -1),
        HexCoord(-1, 0), HexCoord(-1, 1), HexCoord(0, 1)
    ]
    
    # Start at direction 4 scaled
    start_dir = directions[4] # (-1, 1)
    
    # Actually, simpler: Start at direction 4 * radius, walk direction 0, then 1, etc.
    # Start at (-1, 1) * radius ??? No HexCoord doesn't mult.
    
    curr = HexCoord(directions[4].q * radius, directions[4].r * radius)
    
    for i in range(6):
        # Walk 'radius' steps in direction i
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
