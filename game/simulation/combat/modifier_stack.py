"""ModifierStack — source-tagged modifier bundle carried on BattleSpec.

Introduced by PROJ-269 Phase 1 Task 1.3. Replaces the current habit of
pre-mutating ship attributes before the engine sees them (see
`SimulationBattleResolver` and `FleetBattleSetupScreen._apply_complex_modifiers`).

Each `ModifierEntry` wraps an existing
`game.simulation.components.modifier_effects.ModifierEffect` with two extra
fields used for provenance and aggregation:
  - `source`: human-readable origin ("species:Terran", "system:nebula",
    "sector:ion_storm", "empire:research_xyz"). Surfaced on
    `HitRecord.modifiers_applied` for forensic UI.
  - `stack_group`: the existing `Ability.stack_group` key used by the
    two-phase aggregator (intra-group MAX, inter-group SUM). `None`
    means "this entry stands alone" (unique group).

The engine applies the stack at init (Task 1.6 + full wiring at end of
Phase 1 / Phase 5). Phase 1 Task 1.3 ships only the type shape.

`ModifierStack.empty()` is provided for compilers that need a non-None
default without constructing zero-length collections by hand.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Optional, Tuple

from game.simulation.components.modifier_effects import ModifierEffect


@dataclass(frozen=True)
class ModifierEntry:
    """One entry in a ModifierStack — a ModifierEffect plus provenance.

    `stack_group` feeds into the existing two-phase aggregator
    (`game/simulation/entities/ability_aggregator.py`): same-group entries
    take MAX, different-group entries SUM.
    """

    source: str
    stack_group: Optional[str]
    effect: ModifierEffect


# Frozen, shared empty mapping reused by `ModifierStack.empty()` — avoids
# reallocating a dict every call and sidesteps dataclass mutable-default
# footguns.
_EMPTY_PER_TEAM: Mapping[int, Tuple[ModifierEntry, ...]] = MappingProxyType({})


@dataclass(frozen=True)
class ModifierStack:
    """Per-team + global modifier bundle carried on `BattleSpec`.

    Fields:
      - `per_team`: `team_id -> tuple of ModifierEntry` applied to that team
      - `global_`: tuple of entries applied to every team (environmental /
        system-wide effects)
    """

    per_team: Mapping[int, Tuple[ModifierEntry, ...]]
    global_: Tuple[ModifierEntry, ...]

    @classmethod
    def empty(cls) -> "ModifierStack":
        """Return an empty stack — no team or global modifiers."""
        return cls(per_team=_EMPTY_PER_TEAM, global_=())


__all__ = [
    "ModifierEntry",
    "ModifierStack",
]
