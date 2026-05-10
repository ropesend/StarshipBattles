"""FormationSpec, FormationShape, and FormationResolver.

Introduced by PROJ-269 Phase 1 Task 1.4 (types) and Phase 4 Task 4.2
(resolver).

`FormationShape.CUSTOM` lets Combat Lab scenarios specify explicit ship
positions. Other shapes are parametric — `FormationResolver.resolve`
generates world-space positions from `shape`, `spacing`, and the team's
`entry_vector`.

Defaults by dominant design_role (see Task 4.3 `resolve_default_for_task_force`):
  - Strike         → WEDGE
  - Carrier        → CARRIER_PROTECTED
  - Defender       → LINE_ABREAST
  - Scout/Skirmisher → LINE_ASTERN
  - Mixed          → LINE_ABREAST
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple

from game.core.math import Vector2

if TYPE_CHECKING:
    from game.simulation.battle_spec import EntryVector


class FormationShape(Enum):
    """All formation shapes understood by the (Phase 4) FormationResolver."""

    LINE_ABREAST = "line_abreast"              # perpendicular to facing
    LINE_ASTERN = "line_astern"                # single file along facing
    WEDGE = "wedge"                            # arrowhead pointing in facing
    ECHELON_LEFT = "echelon_left"              # diagonal left
    ECHELON_RIGHT = "echelon_right"            # diagonal right
    SCREEN = "screen"                          # heavy ships behind light screen
    CARRIER_PROTECTED = "carrier_protected"    # carriers center, escorts around
    CUSTOM = "custom"                          # explicit `custom_positions`


@dataclass(frozen=True)
class FormationSpec:
    """Formation authored per TaskForce.

    Fields:
      - `shape`: one of `FormationShape`
      - `spacing`: inter-ship distance in world-space pixels
      - `custom_positions`: used only when `shape == FormationShape.CUSTOM`;
        ignored for all other shapes. Positions are in the formation's
        local frame — the resolver rotates them by `entry_vector.facing`.
    """

    shape: FormationShape
    spacing: float
    custom_positions: Tuple[Vector2, ...] = field(default_factory=tuple)

    # ------------------------------------------------------------------
    # Serializable Protocol (Pattern #17 — `docs/02_PATTERNS.md §17`)
    # ------------------------------------------------------------------
    # PROJ-391 Task 1.3: canonical (de)serialization lives on the type
    # itself rather than as duplicated free functions in
    # `task_force.py` and `replay_serialization.py`. Both legacy
    # implementations produced identical output (`float(p.x)`/`float(p.y)`
    # is the same as `_vec_to_list(v)`). The replay-layer fallback for
    # non-FormationSpec inputs is dropped — every spec compiler in the
    # codebase produces a real `FormationSpec`.

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this formation to a JSON-safe dict (Pattern #17)."""
        return {
            "shape": self.shape.value,
            "spacing": float(self.spacing),
            "custom_positions": [
                [float(p.x), float(p.y)] for p in self.custom_positions
            ],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FormationSpec":
        """Reconstruct a `FormationSpec` from its `to_dict` form (Pattern #17)."""
        return cls(
            shape=FormationShape(data["shape"]),
            spacing=float(data.get("spacing", FormationResolver.DEFAULT_SPACING)),
            custom_positions=tuple(
                Vector2(float(p[0]), float(p[1]))
                for p in data.get("custom_positions", [])
            ),
        )


class FormationResolver:
    """Deterministic (formation, entry_vector, boundary, ships) → per-ship pose.

    PROJ-269 Phase 4 Task 4.2. Stateless — the public API is a single
    static `resolve` method. Callers (the three spec compilers) use
    the output to populate `ShipSpec.position` / `ShipSpec.angle`.

    Algorithm:
      1. Compute formation-local positions (facing=0 = +x).
      2. Rotate each position by `entry_vector.facing` (degrees, CCW).
      3. Translate by `entry_vector.origin`.
      4. Clamp to `boundary.closest_inside_point` if the boundary is
         supplied AND the position is outside.
      5. Every ship's angle is set to `entry_vector.facing`.

    Ship ordering: positions are assigned in the input ship-list order
    so callers can use list order to choose who is leader / wingman.
    """

    DEFAULT_SPACING = 100.0

    @staticmethod
    def resolve(
        formation: "FormationSpec",
        entry_vector: "EntryVector",
        boundary: Optional[Any],
        ships: Sequence[Any],
    ) -> Dict[str, Tuple[Vector2, float]]:
        """Compute per-ship (position, angle) keyed by `ship.instance_id`.

        Args:
            formation: Shape + spacing (+ optional custom positions).
            entry_vector: `origin` and `facing` (degrees) — origin is
                the anchor point; facing rotates the formation.
            boundary: Optional `BoundaryRegion`. If a computed position
                is outside, it's clamped via `boundary.closest_inside_point`.
            ships: Input ship list; order determines assignment.

        Returns:
            `{ship.instance_id: (world_position, angle_degrees)}`
        """
        n = len(ships)
        if n == 0:
            return {}

        local_positions = _compute_local_positions(formation, n)
        facing_rad = math.radians(entry_vector.facing)
        cos_f = math.cos(facing_rad)
        sin_f = math.sin(facing_rad)
        origin = entry_vector.origin

        poses: Dict[str, Tuple[Vector2, float]] = {}
        for ship, local in zip(ships, local_positions):
            # Rotate local by facing, translate by origin.
            rx = local.x * cos_f - local.y * sin_f
            ry = local.x * sin_f + local.y * cos_f
            world = Vector2(origin.x + rx, origin.y + ry)

            # Clamp to boundary if supplied + outside.
            if boundary is not None and hasattr(boundary, "contains"):
                if not boundary.contains(world):
                    world = boundary.closest_inside_point(world)

            poses[ship.instance_id] = (world, float(entry_vector.facing))
        return poses


def _compute_local_positions(
    formation: "FormationSpec", n: int
) -> List[Vector2]:
    """Produce `n` formation-local positions for the given shape.

    Local coordinates assume facing=0 = +x axis.
    """
    shape = formation.shape
    spacing = float(formation.spacing) or FormationResolver.DEFAULT_SPACING

    if shape == FormationShape.CUSTOM:
        # Use verbatim, clip to n positions. If shorter than n, pad by
        # repeating the last entry — callers should match list lengths.
        if not formation.custom_positions:
            return [Vector2(0.0, 0.0) for _ in range(n)]
        positions = list(formation.custom_positions)[:n]
        while len(positions) < n:
            positions.append(positions[-1])
        return positions

    if shape == FormationShape.LINE_ABREAST:
        # Perpendicular to facing (along local Y axis), symmetric around origin.
        # For even counts, positions straddle Y=0 at half-spacing offsets.
        return [_symmetric_y(i, n, spacing) for i in range(n)]

    if shape == FormationShape.LINE_ASTERN:
        # Single file along +x: (0, 0), (spacing, 0), (2s, 0), ...
        return [Vector2(i * spacing, 0.0) for i in range(n)]

    if shape == FormationShape.WEDGE:
        # Leader at (0, 0); ships [1..] placed as wingmen behind.
        # Row k > 0 has 2 ships at (-k*s, ±k*s).
        positions: List[Vector2] = []
        positions.append(Vector2(0.0, 0.0))  # leader
        row = 1
        while len(positions) < n:
            positions.append(Vector2(-row * spacing, row * spacing))
            if len(positions) < n:
                positions.append(Vector2(-row * spacing, -row * spacing))
            row += 1
        return positions[:n]

    if shape == FormationShape.ECHELON_LEFT:
        # Diagonal up-left: each ship at (-i*s, +i*s).
        return [Vector2(-i * spacing, i * spacing) for i in range(n)]

    if shape == FormationShape.ECHELON_RIGHT:
        # Diagonal down-left: each ship at (-i*s, -i*s).
        return [Vector2(-i * spacing, -i * spacing) for i in range(n)]

    if shape == FormationShape.SCREEN:
        # Half the ships at x=0 (main line), half at x=+spacing (screen ahead),
        # each column spread symmetrically in Y.
        main = n // 2 + (n % 2)  # main line gets the extra ship if odd
        screen_count = n - main
        positions = []
        # Main line (behind)
        for i in range(main):
            positions.append(Vector2(0.0, _symmetric_y(i, main, spacing).y))
        # Screen (ahead of main line)
        for i in range(screen_count):
            positions.append(
                Vector2(spacing, _symmetric_y(i, screen_count, spacing).y)
            )
        return positions

    if shape == FormationShape.CARRIER_PROTECTED:
        # First ~1/3 of ships are carriers at origin; rest on a ring of
        # radius `spacing` around them, evenly distributed.
        carrier_count = max(1, n // 3)
        escort_count = n - carrier_count
        positions = [Vector2(0.0, 0.0)] * carrier_count
        if escort_count > 0:
            for i in range(escort_count):
                theta = 2.0 * math.pi * i / escort_count
                positions.append(
                    Vector2(
                        spacing * math.cos(theta),
                        spacing * math.sin(theta),
                    )
                )
        return positions

    # Unknown shape — line astern as a safe default.
    return [Vector2(i * spacing, 0.0) for i in range(n)]


def _symmetric_y(index: int, count: int, spacing: float) -> Vector2:
    """Return a Vector2 at (0, offset) where offset places the `index`-th
    ship of `count` total symmetrically around y=0 with `spacing` between
    adjacent pairs.

    Odd count: middle ship at 0, others at ±spacing, ±2*spacing, ...
    Even count: all ships offset by ±(spacing/2), ±(3*spacing/2), ...
    """
    if count == 1:
        return Vector2(0.0, 0.0)
    # Center index = (count - 1) / 2; odd count has integer center, even
    # count has half-integer center (yields half-spacing offsets).
    center = (count - 1) / 2.0
    y = (index - center) * spacing
    return Vector2(0.0, y)


# ---------------------------------------------------------------------------
# Design-role → default formation (Task 4.3)
# ---------------------------------------------------------------------------

# Mapping from design_role id (see `data/design_roles.json`) to one of 4
# archetype buckets. Each bucket has a canonical default formation per
# PROJ-269 decisions.md.
_DESIGN_ROLE_TO_ARCHETYPE: Dict[str, str] = {
    # Carrier archetype
    "carrier": "carrier",
    # Strike archetype (fast attack / heavy alpha-strike)
    "interceptor": "strike",
    "assault_ship": "strike",
    "raider": "strike",
    "missile_platform": "strike",
    # Defender archetype (line / support)
    "line_combatant": "defender",
    "fleet_escort": "defender",
    "defensive_platform": "defender",
    "shield_projector": "defender",
    # Scout/Skirmisher archetype
    "scout": "scout",
    "command_ship": "scout",
    "sensor_platform": "scout",
    # Everything else is "other" → line abreast fallback.
}

_ARCHETYPE_TO_SHAPE: Dict[str, FormationShape] = {
    "carrier": FormationShape.CARRIER_PROTECTED,
    "strike": FormationShape.WEDGE,
    "defender": FormationShape.LINE_ABREAST,
    "scout": FormationShape.LINE_ASTERN,
}


def resolve_default_for_task_force(ships: Sequence[Any]) -> FormationSpec:
    """Pick a `FormationSpec` based on the dominant `design_role` in
    the ship list.

    Ties and unknown roles fall back to `LINE_ABREAST`.

    Args:
        ships: Iterable of ship-like objects. Each must expose a
            `design_role: str` attribute (or `None`).
    """
    if not ships:
        return FormationSpec(
            shape=FormationShape.LINE_ABREAST,
            spacing=FormationResolver.DEFAULT_SPACING,
        )

    # Count each ship's archetype.
    archetype_counts: Dict[str, int] = {}
    for ship in ships:
        role = getattr(ship, "design_role", None)
        archetype = _DESIGN_ROLE_TO_ARCHETYPE.get(role or "", "other")
        archetype_counts[archetype] = archetype_counts.get(archetype, 0) + 1

    # Sorted by count descending; pick first, but require strict majority.
    sorted_buckets = sorted(
        archetype_counts.items(), key=lambda kv: (-kv[1], kv[0])
    )
    top_archetype, top_count = sorted_buckets[0]
    # Tie detection: if there's another archetype with the same count,
    # fall back to LINE_ABREAST (mixed).
    tied = sum(1 for _, c in sorted_buckets if c == top_count) > 1

    if tied or top_archetype == "other":
        shape = FormationShape.LINE_ABREAST
    else:
        shape = _ARCHETYPE_TO_SHAPE.get(top_archetype, FormationShape.LINE_ABREAST)

    return FormationSpec(shape=shape, spacing=FormationResolver.DEFAULT_SPACING)


# ---------------------------------------------------------------------------
# N-team entry vector resolution (PROJ-275 Phase 2)
# ---------------------------------------------------------------------------


DEFAULT_ARENA_RADIUS = 500.0
"""Default radius for `resolve_team_entry_vectors`. Matches the historical
Battle Setup constant `_SIDE_ENTRY_VECTORS` radius (500 units)."""


def resolve_team_entry_vectors(
    team_count: int,
    arena_radius: float = DEFAULT_ARENA_RADIUS,
) -> Dict[int, "EntryVector"]:
    """Assign `EntryVector` origins + facings for N teams on a ring.

    Convention:
    - `team_count == 2`: team 0 at `(-arena_radius, 0)` facing east (0°);
      team 1 at `(+arena_radius, 0)` facing west (180°). Preserves the
      legacy Battle Setup `_SIDE_ENTRY_VECTORS` layout byte-for-byte.
    - `team_count >= 3`: team i at angle `(180 + i * (360 / N))°` on a
      circle of radius `arena_radius`. Equally spaced; all face inward
      toward the origin.

    The "angle 180° start" is chosen so team 0 always sits at west
    `(-r, 0)` regardless of N — preserving player expectations from the
    2-team case.

    Args:
        team_count: Number of teams. Must be in `[2, 8]`.
        arena_radius: Ring radius. Positive float.

    Returns:
        `Dict[int, EntryVector]` keyed by team_id (0..team_count-1).

    Raises:
        ValueError: if `team_count < 2` or `team_count > 8`.
    """
    if team_count < 2 or team_count > 8:
        raise ValueError(
            f"resolve_team_entry_vectors: team_count must be in [2, 8], "
            f"got {team_count}"
        )
    # Late import avoids circular dep: EntryVector is in battle_spec which
    # may import other formation types at load time.
    from game.simulation.battle_spec import EntryVector

    step_deg = 360.0 / team_count
    vectors: Dict[int, "EntryVector"] = {}
    # Snap floating-point noise near zero to exact zero so 2-team layouts
    # report `(-500, 0)` / `(+500, 0)` byte-identically instead of
    # `(-500, 6e-14)`. Threshold is small relative to any sensible arena
    # radius.
    _eps = 1e-9 * max(1.0, arena_radius)
    for i in range(team_count):
        angle_deg = (180.0 + i * step_deg) % 360.0
        angle_rad = math.radians(angle_deg)
        x = arena_radius * math.cos(angle_rad)
        y = arena_radius * math.sin(angle_rad)
        if abs(x) < _eps:
            x = 0.0
        if abs(y) < _eps:
            y = 0.0
        # Face inward toward the origin (angle + 180° mod 360°).
        facing = (angle_deg + 180.0) % 360.0
        vectors[i] = EntryVector(origin=Vector2(x, y), facing=facing)
    return vectors


__all__ = [
    "DEFAULT_ARENA_RADIUS",
    "FormationResolver",
    "FormationShape",
    "FormationSpec",
    "resolve_default_for_task_force",
    "resolve_team_entry_vectors",
]
