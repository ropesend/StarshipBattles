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

2. ``STAT_CONTRIBUTOR_REGISTRY`` — list of registered contributor callables
   keyed by ability name. Each entry says "when component X has ability Y,
   call function Z(ship, comp) during stats aggregation". The acceptance
   test exercises this end-to-end with a fake contributor.

Both registries support runtime registration via ``register_*`` helpers,
which is what the acceptance test uses to add an extension without
editing core code.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, TYPE_CHECKING

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
# ``Callable[[Ship, Component], None]``. It is invoked during the
# stats-aggregation phase for every ACTIVE+OPERATIONAL component that
# satisfies the gating predicate.
StatContributorFn = Callable[["Ship", "Component"], None]


@dataclass(frozen=True)
class StatContributorEntry:
    """One registered stat contributor.

    Fields:
        ability_name: the ability whose presence on a component triggers
            the contributor. ``has_ability`` is the gating check; the
            contributor itself is responsible for any further reads.
        contributor: function that mutates ``ship`` based on ``comp``.
        domain: human-readable tag for diagnostics; not consumed by the
            calculator.
    """

    ability_name: str
    contributor: StatContributorFn
    domain: str = "ext"


STAT_CONTRIBUTOR_REGISTRY: List[StatContributorEntry] = []


def register_stat_contributor(
    ability_name: str,
    contributor: StatContributorFn,
    *,
    domain: str = "ext",
) -> None:
    """Register a runtime stat contributor.

    Raises if the same (ability, domain) pair is already registered to
    catch accidental double-registration.
    """
    for entry in STAT_CONTRIBUTOR_REGISTRY:
        if entry.ability_name == ability_name and entry.domain == domain:
            raise ValueError(
                f"Stat contributor for {ability_name!r} in domain "
                f"{domain!r} already registered."
            )
    STAT_CONTRIBUTOR_REGISTRY.append(
        StatContributorEntry(ability_name, contributor, domain)
    )


def unregister_stat_contributor(ability_name: str, *, domain: str = "ext") -> None:
    """Remove a previously registered stat contributor."""
    global STAT_CONTRIBUTOR_REGISTRY
    STAT_CONTRIBUTOR_REGISTRY = [
        e
        for e in STAT_CONTRIBUTOR_REGISTRY
        if not (e.ability_name == ability_name and e.domain == domain)
    ]


def apply_registered_contributors(
    ship: "Ship", component: "Component"
) -> None:
    """Invoke every registered contributor whose ability the component has.

    Called from ``ShipStatsCalculator._phase_stats_aggregation`` for each
    operational component. Order is registration order; contributors
    should not depend on ordering (consistent with the legacy aggregator
    helpers, which were each independent).
    """
    for entry in STAT_CONTRIBUTOR_REGISTRY:
        if component.has_ability(entry.ability_name):
            entry.contributor(ship, component)


__all__ = [
    "CREW_PRIORITY_REGISTRY",
    "CREW_PRIORITY_DEFAULT",
    "CrewPriorityEntry",
    "register_crew_priority",
    "unregister_crew_priority",
    "lookup_crew_priority",
    "StatContributorEntry",
    "StatContributorFn",
    "STAT_CONTRIBUTOR_REGISTRY",
    "register_stat_contributor",
    "unregister_stat_contributor",
    "apply_registered_contributors",
]
