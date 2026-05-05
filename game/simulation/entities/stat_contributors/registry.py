"""
Stat contributor registry — extension points for ship-stat calculation.

PROJ-360 Phase 3: replaces hardcoded ability-name string checks inside the
contributor modules with declarative registry entries. Adding a new
stat-affecting ability now means *registering* it; no edits to
``ship_stats.py`` or the contributor modules are required for the
extension points covered here.

Two registries are provided, intentionally separate from the existing
``game.simulation.combat.ability_stat_registry.ABILITY_STAT_REGISTRY`` —
that one shapes the modifier-emission pipeline (compiler → ModifierEntry
→ external_stats), which has different semantics than per-component stat
aggregation. Mixing them would warp both registries' contracts.

Registries:

1. ``CREW_PRIORITY_REGISTRY`` — list of (ability_name, priority) pairs.
   The `command.priority_sort_key` consults this to decide crew-allocation
   order. Lower priority value = served first. Default fallback = 3.

2. ``STAT_CONTRIBUTOR_REGISTRY`` — dict (keyed by ability name) of
   registered contributor callables. Each entry says "when component X has
   ability Y, call function Z(ship, comp, acc) during stats aggregation".
   Per-ability dedup is enforced (PROJ-360 audit EXT-01): registering the
   same ability twice raises. Registering a contributor for an ability
   *already handled by a built-in domain* (see ``BUILTIN_HANDLED_ABILITIES``)
   *suppresses* the built-in handler for that ability — accumulate-then-commit
   stays consistent and double-counting is impossible.

Both registries support runtime registration via ``register_*`` helpers,
which is what the acceptance test uses to add an extension without
editing core code.

PROJ-360 audit fixes (2026-05-05):

- EXT-01 (CRIT): per-ability dedup (the ``domain`` field is now an opt-in
  diagnostic tag, no longer part of the dedup or apply key).
- EXT-02 (MAJ) / EXT-11: registering an ability listed in
  ``BUILTIN_HANDLED_ABILITIES`` suppresses the built-in domain handler
  for that ability inside ``ShipStatsCalculator._phase_stats_aggregation``.
  See ``is_builtin_suppressed_for(ability_name)``.
- EXT-12 (CRIT): registered contributors receive the same ``acc`` dict the
  built-in contributors mutate, so the accumulate-then-commit invariant is
  preserved across both tiers.
- C1 (MAJ): dict-backed registry for O(1) registration / lookup, replacing
  the linear-scan list.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


# ---------------------------------------------------------------------------
# Crew-allocation priority registry
# ---------------------------------------------------------------------------


# Lower number = higher priority during crew/life-support allocation.
# A component matching MULTIPLE entries gets the lowest (highest-priority)
# match, mirroring legacy behavior (CommandAndControl beats WeaponAbility).
@dataclass(frozen=True)
class CrewPriorityEntry:
    """One row of the crew-priority registry."""

    ability_name: str
    priority: int  # 0 highest, larger = lower priority


CREW_PRIORITY_REGISTRY: List[CrewPriorityEntry] = [
    # 0 — Command first.
    CrewPriorityEntry("CommandAndControl", 0),
    # 1 — Movement (engines + thrusters).
    CrewPriorityEntry("CombatPropulsion", 1),
    CrewPriorityEntry("ManeuveringThruster", 1),
    # 2 — Weapons.
    CrewPriorityEntry("WeaponAbility", 2),
]

# Default priority for components matching no registered ability.
CREW_PRIORITY_DEFAULT: int = 3


def register_crew_priority(ability_name: str, priority: int) -> None:
    """Add a crew-priority binding at runtime.

    Used by the extension acceptance test to demonstrate a new
    component class joining the priority order without editing
    ``command.py``. Raises if the same ability is already registered
    (registries are append-only; collisions are programmer error).
    """
    for entry in CREW_PRIORITY_REGISTRY:
        if entry.ability_name == ability_name:
            raise ValueError(
                f"Crew priority for ability {ability_name!r} already registered "
                f"with priority {entry.priority}; remove it first or use a "
                f"different ability name."
            )
    CREW_PRIORITY_REGISTRY.append(CrewPriorityEntry(ability_name, priority))


def unregister_crew_priority(ability_name: str) -> None:
    """Remove a previously registered crew-priority binding.

    No-op if the ability is not registered. Used primarily by tests to
    keep the global registry clean across cases.
    """
    global CREW_PRIORITY_REGISTRY
    CREW_PRIORITY_REGISTRY = [
        e for e in CREW_PRIORITY_REGISTRY if e.ability_name != ability_name
    ]


def lookup_crew_priority(component: "Component") -> int:
    """Return the lowest priority value among the abilities the component has.

    Mirrors the legacy hardcoded ``priority_sort_key`` semantics: a component
    with both `CommandAndControl` and `WeaponAbility` returns 0.
    """
    best = CREW_PRIORITY_DEFAULT
    for entry in CREW_PRIORITY_REGISTRY:
        if entry.priority < best and component.has_ability(entry.ability_name):
            best = entry.priority
            if best == 0:
                return 0  # already as good as it gets
    return best


# ---------------------------------------------------------------------------
# Generic stat contributor registry (the extension point)
# ---------------------------------------------------------------------------


# A contributor is any callable matching the signature
# ``Callable[[Ship, Component, Dict[str, Any]], None]``. It is invoked during
# the stats-aggregation phase for every ACTIVE+OPERATIONAL component that
# satisfies the gating predicate. ``acc`` is the same accumulator dict
# built-in contributors mutate — registered contributors fully participate
# in the accumulate-then-commit pattern (PROJ-360 audit EXT-12).
StatContributorFn = Callable[["Ship", "Component", Dict[str, Any]], None]

# Abilities handled by built-in domain contributors inside
# ``ShipStatsCalculator._phase_stats_aggregation``. Registering a contributor
# for any of these ability names *suppresses* the built-in handler for that
# component-pass (PROJ-360 audit EXT-02). Used by
# ``is_builtin_suppressed_for`` so the calculator can skip its own dispatch
# when an extension owns the ability.
#
# Order matches the call sites in ``ship_stats.py``. Keep this list in sync
# whenever a new built-in domain handler is added.
BUILTIN_HANDLED_ABILITIES: frozenset[str] = frozenset({
    # movement.aggregate_propulsion
    "CombatPropulsion",
    "StrategicMovement",
    "WarpJump",
    "ManeuveringThruster",
    # defense.aggregate_defense
    "ShieldProjection",
    "ShieldRegeneration",
    # launch.aggregate_hangar
    "VehicleLaunch",
    # command.track_multiplex
    "MultiplexTracking",
})


@dataclass(frozen=True)
class StatContributorEntry:
    """One registered stat contributor.

    Fields:
        ability_name: the ability whose presence on a component triggers
            the contributor. ``has_ability`` is the gating check; the
            contributor itself is responsible for any further reads.
        contributor: function that mutates the shared ``acc`` dict (and
            optionally ``ship``) based on ``comp``.
        domain: optional human-readable diagnostic tag. Not part of the
            registration key — registration is per-ability — but useful
            in error messages and tracing.
    """

    ability_name: str
    contributor: StatContributorFn
    domain: str = "ext"


# PROJ-360 audit C1: dict-backed registry — O(1) registration and lookup.
# Key is the ability name; values are StatContributorEntry. Per-ability
# dedup (EXT-01) is naturally enforced by dict semantics.
STAT_CONTRIBUTOR_REGISTRY: Dict[str, StatContributorEntry] = {}


def register_stat_contributor(
    ability_name: str,
    contributor: StatContributorFn,
    *,
    domain: str = "ext",
) -> None:
    """Register a runtime stat contributor (one per ability name).

    PROJ-360 audit EXT-01: dedup is per-ability. Registering the same
    ``ability_name`` twice — with any domain tag — raises. The ``domain``
    field remains as a diagnostic label only.

    A contributor registered for an ability listed in
    ``BUILTIN_HANDLED_ABILITIES`` suppresses the built-in handler for that
    ability so double-counting is impossible (PROJ-360 audit EXT-02).
    """
    existing = STAT_CONTRIBUTOR_REGISTRY.get(ability_name)
    if existing is not None:
        raise ValueError(
            f"Stat contributor for {ability_name!r} already registered "
            f"(existing domain: {existing.domain!r}). Per-ability dedup is "
            f"enforced — unregister first or use a different ability name."
        )
    STAT_CONTRIBUTOR_REGISTRY[ability_name] = StatContributorEntry(
        ability_name, contributor, domain
    )


def unregister_stat_contributor(ability_name: str, *, domain: str = "ext") -> None:
    """Remove a previously registered stat contributor.

    The ``domain`` parameter is accepted for backward-compat but is no
    longer part of the registration key (PROJ-360 audit EXT-01). Removal
    is keyed solely on ``ability_name``; passing a non-matching ``domain``
    still removes the entry, since per-ability dedup means there can only
    be one.
    """
    STAT_CONTRIBUTOR_REGISTRY.pop(ability_name, None)


def is_builtin_suppressed_for(ability_name: str) -> bool:
    """Return True if a registered contributor should suppress the built-in.

    The calculator consults this before invoking its built-in domain handlers
    so that a registered contributor takes over fully — same component, same
    ability, single execution. Both halves of the test (registered contributor
    runs; built-in does not) are covered by the audit-remediation tests.
    """
    return (
        ability_name in BUILTIN_HANDLED_ABILITIES
        and ability_name in STAT_CONTRIBUTOR_REGISTRY
    )


def apply_registered_contributors(
    ship: "Ship",
    component: "Component",
    acc: Dict[str, Any],
) -> None:
    """Invoke every registered contributor whose ability the component has.

    Called from ``ShipStatsCalculator._phase_stats_aggregation`` for each
    operational component. Iteration is over the dict's values so the
    relative cost is proportional to registered entries (not all known
    abilities). Registered contributors mutate the same ``acc`` dict the
    built-in contributors use (PROJ-360 audit EXT-12).
    """
    if not STAT_CONTRIBUTOR_REGISTRY:
        return
    for ability_name, entry in STAT_CONTRIBUTOR_REGISTRY.items():
        if component.has_ability(ability_name):
            entry.contributor(ship, component, acc)


def reset_stat_contributor_registry() -> None:
    """Test-support hook: clear all registered stat contributors.

    PROJ-360 audit A1: used by the root conftest to guarantee a clean
    registry between tests, even if a test crashes before its cleanup
    fixture runs. Built-in registries (``CREW_PRIORITY_REGISTRY``) are
    not touched — they are seeded with default entries on import.
    """
    STAT_CONTRIBUTOR_REGISTRY.clear()


__all__ = [
    "CREW_PRIORITY_REGISTRY",
    "CREW_PRIORITY_DEFAULT",
    "CrewPriorityEntry",
    "register_crew_priority",
    "unregister_crew_priority",
    "lookup_crew_priority",
    "BUILTIN_HANDLED_ABILITIES",
    "StatContributorEntry",
    "StatContributorFn",
    "STAT_CONTRIBUTOR_REGISTRY",
    "register_stat_contributor",
    "unregister_stat_contributor",
    "is_builtin_suppressed_for",
    "apply_registered_contributors",
    "reset_stat_contributor_registry",
]
