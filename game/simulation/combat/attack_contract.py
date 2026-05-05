"""PROJ-359: Typed Weapon Execution Contract.

This module defines the typed contract that replaces the dict-shaped attack
carriers and string-class dispatch in the realtime combat layer. Mirrors the
shape of the Ability-Stat Registry pattern (PROJ-273): one mapping per family,
lookup at the dispatch site.

## Why
Pre-refactor (PROJ-359), four files coordinated weapon family behavior via
`comp.has_ability('BeamWeaponAbility' | 'SeekerWeaponAbility' | ...)` string
branches. Adding a new family required edits to:
- `game/simulation/combat/weapon_firing_system.py` (firing dispatch)
- `game/simulation/combat/targeting_system.py` (filter rules)
- `game/engine/collision.py` (beam dict consumer)
- `game/simulation/projectile_manager.py` (projectile hit application)

This contract pulls those decisions behind a single registry and a typed
request/resolution pair.

## Layer note
This module lives in `game/simulation/combat/` because the `AttackResolution`
union encodes simulation-layer semantics. The engine layer
(`game/engine/collision.py`) consumes a `BeamResolution` *value* but does not
own its definition — this preserves the Engine vs Simulation boundary
described in `docs/01_ARCHITECTURE.md`.

## Public surface
- `WeaponFamily` (Enum): BEAM, PROJECTILE, SEEKER, PDC
- `AttackRequest` (frozen dataclass): inputs to a family handler
- `AttackResolution` (Union): one of `BeamResolution`, `ProjectileResolution`,
  `MissileResolution`, `NoAttack`
- `WeaponHandler` (Protocol): `fire(request) -> AttackResolution`
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, Optional, Protocol, Union, runtime_checkable

from game.core.math import Vector2

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.projectile import Projectile


class WeaponFamily(Enum):
    """The four weapon families that route through the registry.

    PDC is a *role* of a Beam weapon — a Beam component with the 'pdc' tag
    on its ability — but the targeting / firing logic differs enough that it
    is registered as a distinct family. The registry's family-detection
    helper resolves it via tags.
    """

    BEAM = "beam"
    PROJECTILE = "projectile"
    SEEKER = "seeker"
    PDC = "pdc"


@dataclass(frozen=True)
class AttackRequest:
    """Inputs supplied by the firing system to a weapon family handler.

    `family` is computed by the registry's family-detection helper before
    dispatch. Handlers should not need to re-detect family.

    `aim_pos` and `aim_vec` come from
    `TargetingSystem.calculate_firing_solution`; for beams these are
    direct-aim, for projectile/seeker these are lead-corrected.
    """

    source: Any  # Ship — Any to avoid runtime import cost; protocol-compat
    component: "Component"
    weapon_ability: Any  # IWeaponAbility — see ability_protocols
    target: Any  # ICombatShip | IProjectile
    aim_pos: Vector2
    aim_vec: Vector2
    family: WeaponFamily


# -----------------------------------------------------------------------------
# Resolution variants
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class BeamResolution:
    """Resolution emitted by the Beam (and PDC) family.

    Mirrors the legacy beam-attack dict 1:1 so the engine layer can consume
    it via attribute access (`resolution.origin` instead of `attack['origin']`).
    The legacy dict path remains during Phase 3 migration; Phase 4 deletes it.
    """

    source: Any
    component: "Component"
    target: Any
    damage: float
    range: float
    origin: Vector2
    direction: Vector2
    hit: bool = True


@dataclass(frozen=True)
class ProjectileResolution:
    """Resolution emitted by the Projectile and Seeker families.

    Carries an already-constructed `Projectile` instance. The simulation
    layer adds it to the `ProjectileManager`. Future damage-event convergence
    (per plan goal) will lift the damage telemetry shape into this resolution.
    """

    projectile: "Projectile"


@dataclass(frozen=True)
class NoAttack:
    """Sentinel for handlers that decide not to fire (e.g., target out of
    arc). Distinct from a missing target — the firing system filters those
    earlier."""

    reason: str = ""


AttackResolution = Union[BeamResolution, ProjectileResolution, NoAttack]


# -----------------------------------------------------------------------------
# Handler protocol
# -----------------------------------------------------------------------------


@runtime_checkable
class WeaponHandler(Protocol):
    """Protocol every family handler implements.

    Handlers are registered in `weapon_registry.WEAPON_REGISTRY`. They take a
    typed `AttackRequest` and return a typed `AttackResolution`. Any per-family
    state (e.g., seeker firing-arc check) lives inside the handler.
    """

    def fire(self, request: AttackRequest) -> AttackResolution:
        ...


@dataclass(frozen=True)
class WeaponFamilyMetadata:
    """Static metadata about a weapon family used by firing/targeting systems
    *outside* the dispatch path.

    Carries the per-family policy decisions that previously lived as `if
    is_pdc:` and `comp.has_ability(...)` branches across firing and targeting.

    Fields:
      - `targets_missiles`: True when this family is allowed to target enemy
        missile-type projectiles. Only PDC is True today; non-PDC weapons
        cannot target missiles.
      - `valid_target_types`: Set of uppercase target-type strings this family
        is restricted to. Empty set means "no type restriction" (default).
        PDC reads `pdc_valid_targets` from its BeamWeaponAbility, but that
        per-component data is consulted at filter time, not metadata time.
      - `consumes_pdc_missile_context`: True when the firing system should
        scan `context['projectiles']` for enemy missiles to add as candidate
        targets. Currently equivalent to `targets_missiles` but kept as a
        separate flag for future flexibility (e.g., a hypothetical missile-
        only sensor weapon that doesn't intercept).
    """

    targets_missiles: bool = False
    consumes_pdc_missile_context: bool = False


# Family metadata lookup. Mirrors ABILITY_STAT_REGISTRY shape.
FAMILY_METADATA: dict[WeaponFamily, WeaponFamilyMetadata] = {
    WeaponFamily.BEAM: WeaponFamilyMetadata(),
    WeaponFamily.PROJECTILE: WeaponFamilyMetadata(),
    WeaponFamily.SEEKER: WeaponFamilyMetadata(),
    WeaponFamily.PDC: WeaponFamilyMetadata(
        targets_missiles=True,
        consumes_pdc_missile_context=True,
    ),
}


class UnregisteredWeaponFamilyError(KeyError):
    """Raised when `WeaponRegistry.dispatch` is called with a request whose
    family has no registered handler. Prefer this over silent fallback —
    a missing handler is a programming error, not a runtime condition."""
