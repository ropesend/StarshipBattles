"""FormationSpec and FormationShape — formation types carried on TaskForceSpec.

Introduced by PROJ-269 Phase 1 Task 1.4. Phase 1 ships the type shape so
`TaskForceSpec.formation` is well-typed; the `FormationResolver` that
converts (formation, entry_vector, boundary, ship_list, design_roles)
into per-ship (position, angle) lands in Phase 4.

`FormationShape.CUSTOM` lets Combat Lab scenarios specify explicit ship
positions (useful for edge-case tests like "ships stacked at (0, 0)").
Other shapes are parametric — the resolver in Phase 4 generates positions
from `shape`, `spacing`, and the team's `entry_vector`.

Defaults by dominant design_role (resolved at spec-compile time in Phase 4):
  - Strike         → WEDGE
  - Carrier        → CARRIER_PROTECTED
  - Defender       → LINE_ABREAST
  - Scout/Skirmisher → LINE_ASTERN
  - Mixed          → LINE_ABREAST
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple

from game.core.math import Vector2


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


__all__ = [
    "FormationShape",
    "FormationSpec",
]
