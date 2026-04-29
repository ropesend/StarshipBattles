"""BattleOutcome and nested DTOs — the single output contract from the simulator.

Introduced by PROJ-269 Phase 1. Returned by `run_battle(spec) -> BattleOutcome`.
Callers analyze the outcome for their own purposes:
  - Strategy: `post_battle_hook` writes outcome back to `ShipInstance.components`
  - Battle Setup: results screen renders weapon summaries + ship stats
  - Combat Lab: `_run_validation` turns the outcome into pass/fail checks

All DTOs are frozen dataclasses. Per `docs/01_ARCHITECTURE.md` they live in
the simulation layer so every other layer can import them.

Key invariants (enforced by `run_battle` / `extract_outcome` in Task 1.6):
  - `BattleOutcome.teams[i].team_id == BattleSpec.teams[i].team_id`
  - Every `ShipSpec.instance_id` has exactly one matching `ShipOutcome`
  - `ComponentStateSpec` round-trips: input HP → outcome HP
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional, Tuple

from game.core.math import Vector2
from game.simulation.battle_spec import ComponentStateSpec

if TYPE_CHECKING:
    from game.simulation.combat.telemetry import TelemetryLevel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ShipStatus(Enum):
    """Final status of a ship at battle end."""

    SURVIVED = "survived"       # alive, operational
    DESTROYED = "destroyed"     # hull = 0
    DERELICT = "derelict"       # alive but no weapons + no engines
    RETREATED = "retreated"     # crossed boundary with RETREAT policy


class EndReason(Enum):
    """Which end condition fired to stop the battle.

    Discriminators mirror the existing
    `game.simulation.systems.battle_end_conditions._CONDITION_TYPES`
    plus `ABSOLUTE_MAX` for the engine safety ceiling.
    """

    TICK_LIMIT = "tick_limit"
    TEAM_ELIMINATED = "team_eliminated"
    TEAM_INCAPACITATED = "team_incapacitated"
    ESCAPE = "escape"
    SHIP_DESTROYED = "ship_destroyed"
    NEVER = "never"
    MASS_RATIO = "mass_ratio"
    ANY = "any"
    ALL = "all"
    ABSOLUTE_MAX = "absolute_max"  # engine safety ceiling hit before any condition


# ---------------------------------------------------------------------------
# Leaf DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ModifierApplication:
    """One modifier entry applied to a hit, annotated with its source.

    Enables forensic UI: the Combat Lab hit-log can show where each
    damage-shaping modifier came from ("system:nebula", "empire:research_xyz").
    """

    source: str
    effect_name: str
    value: float


@dataclass(frozen=True)
class HitRecord:
    """A single damage event — populated only at DETAILED telemetry level.

    `NORMAL` and `MINIMAL` outcomes leave `ShipOutcome.hits_taken` empty.
    """

    tick: int
    attacker_ship_id: str
    weapon_component_id: str
    weapon_ability_class: str  # BeamWeaponAbility / ProjectileWeaponAbility / SeekerWeaponAbility
    damage: float
    modifiers_applied: Tuple[ModifierApplication, ...]


@dataclass(frozen=True)
class WeaponSummary:
    """Per-weapon totals — always populated at NORMAL+ telemetry."""

    component_id: str
    component_name: str
    shots_fired: int
    shots_hit: int


@dataclass(frozen=True)
class ShipStats:
    """Per-ship aggregate stats — always populated at NORMAL+ telemetry."""

    total_damage_taken: float
    peak_speed: float
    ticks_derelict: int
    ticks_alive: int


# ---------------------------------------------------------------------------
# Hierarchical outcome DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ShipOutcome:
    """Final state of one ship after the battle.

    `instance_id` matches the originating `ShipSpec.instance_id`.
    `components` reports final per-component HP — fed back into
    `ShipInstance.components` by the strategy post-battle hook.

    PROJ-270 Phase 4.5: added `name` / `ship_class` / `hp` / `max_hp` /
    `current_shields` / `max_shields` display fields so `BattleResultsScreen`
    and other outcome consumers can render results without a live engine
    reference. All default to None/0 for backwards compat with direct
    construction (e.g. tests); `extract_outcome` populates real values.
    """

    instance_id: str
    status: ShipStatus
    final_position: Vector2
    final_angle: float
    final_velocity: Vector2
    components: Tuple[ComponentStateSpec, ...]
    weapons: Tuple[WeaponSummary, ...]
    hits_taken: Tuple[HitRecord, ...]
    stats: ShipStats
    # PROJ-270 Phase 4.5: display fields (None/0 means "not populated").
    name: Optional[str] = None
    ship_class: Optional[str] = None
    hp: float = 0.0
    max_hp: float = 0.0
    current_shields: float = 0.0
    max_shields: float = 0.0


@dataclass(frozen=True)
class TeamOutcome:
    """Per-team outcome — mirrors the team order of `BattleSpec.teams`."""

    team_id: int
    name: str
    ships: Tuple[ShipOutcome, ...]


# ---------------------------------------------------------------------------
# Root DTO
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BattleOutcome:
    """The full, context-blind result of a battle.

    `telemetry_level` is echoed from the input spec so downstream code can
    branch on detail availability (e.g. "hit log is empty because level was
    MINIMAL" vs. "hit log is empty because no one fired").

    FEAT-26: `replay_id` is the uuid string assigned by the
    `IReplayCaptureSink` for the captured replay sidecar, or `None` when
    no real replay was written (NullCaptureSink, replay-of-replay paths,
    capture failures). This is the upstream source of truth — every
    other layer (`BattleResult.replay_id`, the `COMBAT_RESOLVED` event's
    `details["replay_id"]`) carries the same string verbatim.
    """

    end_reason: EndReason
    duration_ticks: int
    seed: int
    teams: Tuple[TeamOutcome, ...]
    telemetry_level: object  # TelemetryLevel — real type lands in Task 1.5
    replay_id: Optional[str] = None


__all__ = [
    "BattleOutcome",
    "EndReason",
    "HitRecord",
    "ModifierApplication",
    "ShipOutcome",
    "ShipStats",
    "ShipStatus",
    "TeamOutcome",
    "WeaponSummary",
]
