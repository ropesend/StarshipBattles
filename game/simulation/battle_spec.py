"""BattleSpec and nested DTOs — the single input contract into the simulator.

Introduced by PROJ-269 Phase 1. Every battle (Combat Lab, Battle Setup,
Strategy combat) is described by a `BattleSpec` produced by a context-specific
compiler and handed to `run_battle(spec) -> BattleOutcome`.

All DTOs in this module are frozen dataclasses so specs are trivially
comparable, hashable where possible, and safe to pass across layers.

Layer rule (per `docs/01_ARCHITECTURE.md`): this module lives in
`game/simulation/` so every layer — strategy, UI, combat_lab — can import it.
The simulation layer itself does NOT import from strategy/UI.

Types whose full implementation lands in sibling Phase 1 tasks are imported
under TYPE_CHECKING with string annotations, so Task 1.1 can ship before
Tasks 1.2–1.5. The DTOs accept whatever object the caller passes; the engine
only interprets them in Task 1.6 and later phases.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable, Optional, Tuple

from game.core.math import Vector2

if TYPE_CHECKING:
    # Future sibling Phase 1 modules — imported only for type-checker use.
    from game.simulation.battle_outcome import BattleOutcome
    from game.simulation.combat.boundary import BoundaryRegion
    from game.simulation.combat.formation import FormationSpec
    from game.simulation.combat.modifier_stack import ModifierStack
    from game.simulation.combat.telemetry import TelemetryLevel
    from game.simulation.systems.battle_end_conditions import IEndCondition


# ---------------------------------------------------------------------------
# Post-battle hook type alias
# ---------------------------------------------------------------------------

PostBattleHook = Callable[["BattleOutcome"], None]
"""Closure invoked by `run_battle` after the engine stops.

The strategy layer attaches a hook that writes `ShipOutcome.components` back
to `ShipInstance.components`, removes dead ships, and applies empire-level
effects. Battle Setup and Combat Lab typically pass `None` — their outcome
handling happens in the caller.
"""


# ---------------------------------------------------------------------------
# Leaf DTOs
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class EntryVector:
    """Where a team enters the arena.

    `origin` is the focal point for the team's starting formation; `facing`
    is the heading (degrees) for ships produced by the formation resolver.
    """

    origin: Vector2
    facing: float


@dataclass(frozen=True)
class CombatPolicies:
    """Three-axis combat policy bag (targeting / movement / retreat).

    Mirrors the shape of `game.strategy.data.fleet_hierarchy.CombatPolicy`
    but lives in the simulation layer so specs can carry it without a
    simulation→strategy import (which the layer rules forbid).

    Each axis is either a preset-id string (looked up in
    `data/targeting_policies.json` / `data/movement_policies.json` /
    `data/group_policies.json`) or `None` meaning "inherit from parent".
    """

    targeting: Optional[str] = None
    movement: Optional[str] = None
    retreat: Optional[str] = None


@dataclass(frozen=True)
class ComponentStateSpec:
    """Persisted per-component HP, max_hp, status, and active-toggle state.

    Populated by the strategy compiler from `ShipInstance.components` so
    per-component damage carries across battles. Combat Lab and Battle Setup
    normally emit ships with no persistent component state (empty tuple on
    `ShipSpec.components`), in which case the engine initializes HP from
    the design.

    `max_hp` and `status` (PROJ-354A) capture battle-end fidelity for the
    PROJ-354B replay end-state verifier — the live capture extractor in
    `battle_runner._extract_component_states` populates them from the
    engine `Component`. `status` carries the `ComponentStatus.name` string
    (e.g., "ACTIVE", "DAMAGED", "NO_CREW", "NO_POWER", "NO_FUEL", "NO_AMMO");
    the enum uses `auto()` numeric values which are not stable across
    Python versions, so we serialize the name.
    """

    component_id: str
    instance_index: int
    current_hp: float
    max_hp: float
    status: str  # ComponentStatus.name (ACTIVE/DAMAGED/NO_CREW/NO_POWER/NO_FUEL/NO_AMMO)
    is_active: bool


@dataclass(frozen=True)
class ShipSpec:
    """A single ship, fully specified at battle start.

    `instance_id` is the stable identifier that the outcome uses to match
    ships back to their spec. Pose fields (`position`, `angle`, `velocity`)
    are produced by `FormationResolver` during compilation.

    `instance_ref` (PROJ-274): optional opaque reference to a strategy-
    layer `ShipInstance` for instance-backed materialization. Typed
    `Optional[Any]` because the simulation layer cannot import
    `ShipInstance` from the strategy layer (layer violation per
    `docs/01_ARCHITECTURE.md`). `InstanceBackedMaterializer` uses duck
    typing to invoke `instance.to_ship(...)`. Design-only callers
    (Combat Lab) leave this `None` and use `DesignOnlyMaterializer`.

    `scenario_role` (PROJ-278 Phase 4): optional positional wiring label
    used by Combat Lab scenarios to route ships into the
    `ships_by_role` dict consumed by `scenario.wire_ships(...)`. Replaces
    the deleted `_role_from_instance_id` substring parser. Battle Setup
    and Strategy callers leave this `None`. Values must match an entry
    in `combat_lab_role_registry` — see
    `combat_lab/data/scenario_roles.json`.
    """

    instance_id: str
    design_id: str
    theme_id: str
    name: str
    position: Vector2
    angle: float
    velocity: Vector2
    components: Tuple[ComponentStateSpec, ...]
    instance_ref: Optional[Any] = None
    scenario_role: Optional[str] = None


@dataclass(frozen=True)
class SquadronSpec:
    """Squadron — sibling of TaskForce, contains ships directly."""

    squadron_id: str
    policies: CombatPolicies
    ships: Tuple[ShipSpec, ...]


@dataclass(frozen=True)
class TaskForceSpec:
    """Task force — top-level tactical grouping under a team.

    `formation` is an opaque slot in Phase 1 (typed as FormationSpec when
    Task 1.4 lands). Annotated as `object` to avoid forcing Phase 1
    callers to import the not-yet-built type.
    """

    task_force_id: str
    formation: object  # FormationSpec — real type lands in Task 1.4
    policies: CombatPolicies
    squadrons: Tuple[SquadronSpec, ...]


@dataclass(frozen=True)
class TeamSpec:
    """One combatant side in a battle.

    `team_id` mirrors the engine's per-ship `team_id`. Order of
    `BattleSpec.teams` determines engine team_id assignment.
    """

    team_id: int
    name: str
    entry_vector: EntryVector
    fleet_hierarchy: Tuple[TaskForceSpec, ...]


# ---------------------------------------------------------------------------
# Root DTO
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BattleSpec:
    """The fully specified initial conditions of a battle.

    Consumed by `run_battle(spec)`. The engine reads every field directly
    — no mode switch, no side-channel mutation, no factory variants.

    Field types that land in sibling Phase 1 tasks:
      - `boundary`: `Optional[BoundaryRegion]` (Task 1.2) — None = unbounded
      - `telemetry_level`: `TelemetryLevel` (Task 1.5)
      - `modifier_stack`: `ModifierStack` (Task 1.3)
      - `end_condition`: `IEndCondition` (already exists)
      - `post_battle_hook`: `Optional[PostBattleHook]` (this module)

    Annotated as `object` / forward-ref strings to keep Task 1.1 shippable
    before those tasks complete. Field discipline is enforced by the tests
    against design.md §2.1.
    """

    # Identity
    seed: int
    telemetry_level: object  # TelemetryLevel — real type lands in Task 1.5

    # Arena — None = unbounded combat
    boundary: Optional[object]  # BoundaryRegion — real type lands in Task 1.2

    # Termination
    end_condition: object  # IEndCondition — already exists in simulation
    absolute_max_ticks: int

    # Teams (N supported — order defines engine team_id assignment)
    teams: Tuple[TeamSpec, ...]

    # Modifier stack (species / empire / system / sector)
    modifier_stack: object  # ModifierStack — real type lands in Task 1.3

    # Post-battle hook (Strategy attaches one; Combat Lab / Setup pass None)
    post_battle_hook: Optional[PostBattleHook]


__all__ = [
    "BattleSpec",
    "CombatPolicies",
    "ComponentStateSpec",
    "EntryVector",
    "PostBattleHook",
    "ShipSpec",
    "SquadronSpec",
    "TaskForceSpec",
    "TeamSpec",
]
