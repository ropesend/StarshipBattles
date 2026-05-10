"""
Stat contributor registry — unified extension surface for ship-stat calculation.

PROJ-360 Phase 3 introduced the registry as a parallel, second-tier extension
mechanism alongside hardcoded built-in domain contributors. PROJ-367 Phase 2
collapses the two-tier model: built-in Phase-3 contributors are now seeded
into ``STAT_CONTRIBUTOR_REGISTRY`` at module import, and modders register the
same way. The single iteration in
``ShipStatsCalculator._phase_stats_aggregation`` walks the registry once per
component.

Two registries:

1. ``CREW_PRIORITY_REGISTRY`` — list of (ability_name, priority) pairs.
   ``command.allocate_crew_and_life_support`` consults this via
   ``lookup_crew_priority`` to decide crew-allocation order. Lower priority
   value = served first. Default fallback = 3.

2. ``STAT_CONTRIBUTOR_REGISTRY`` — the unified Phase-3 pipeline. Each entry
   binds an ``ability_name`` to a callable
   ``contributor(ship, comp, acc) -> None`` invoked when ``comp.has_ability``
   reports the ability present. Built-ins are seeded as ``is_default=True``
   entries with ``phase_order`` in 10..50 (movement=10, defense=20,
   hangar=40, command=50). Modder entries default to ``phase_order=99`` so
   they fire after non-replaced built-ins.

Conflict semantics (``RegistrationConflictPolicy``):

- ``REPLACE_WARN`` (default): a new registration for an existing ability
  REPLACES the active entry; a warning is logged. The replacement inherits
  ``phase_order=99`` unless explicitly overridden, so it fires after
  non-replaced built-ins (mirrors the legacy "skip-built-in-then-modder"
  semantics from PROJ-360 ``is_builtin_suppressed_for``).
- ``REPLACE_SILENT``: same as ``REPLACE_WARN`` but no log.
- ``APPEND``: the new entry is appended; both default + appended fire.
- ``ERROR``: raises ``RegistrationConflictError`` on any conflict.

Replacement entries that ``REPLACE_*`` a default *suppress* the default while
they live; ``unregister_stat_contributor(handle)`` restores it. Default
entries cannot be unregistered by handle (raises
``CannotUnregisterDefaultError``); they are managed via the seed/reset
cycle.

PROJ-367 retirements (Phase 2):

- ``BUILTIN_HANDLED_ABILITIES`` frozenset → DELETED.
- ``is_builtin_suppressed_for()`` → DELETED.
- ``apply_registered_contributors()`` → DELETED (folded into
  ``iter_for(comp)`` + the single ``_phase_stats_aggregation`` loop).
- The four Phase-3 ``aggregate_*`` wrappers (``aggregate_propulsion`` /
  ``aggregate_defense`` / ``aggregate_hangar`` / ``track_multiplex``) →
  DELETED. Per-ability ``contribute_*`` functions live in the same domain
  modules.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from itertools import count
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Crew-allocation priority registry (unchanged from PROJ-360)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CrewPriorityEntry:
    """One row of the crew-priority registry."""

    ability_name: str
    priority: int  # 0 highest, larger = lower priority


CREW_PRIORITY_REGISTRY: List[CrewPriorityEntry] = [
    CrewPriorityEntry("CommandAndControl", 0),
    CrewPriorityEntry("CombatPropulsion", 1),
    CrewPriorityEntry("ManeuveringThruster", 1),
    CrewPriorityEntry("WeaponAbility", 2),
]

CREW_PRIORITY_DEFAULT: int = 3


def register_crew_priority(ability_name: str, priority: int) -> None:
    """Add a crew-priority binding at runtime (registries are append-only)."""
    for entry in CREW_PRIORITY_REGISTRY:
        if entry.ability_name == ability_name:
            raise ValueError(
                f"Crew priority for ability {ability_name!r} already registered "
                f"with priority {entry.priority}; remove it first or use a "
                f"different ability name."
            )
    CREW_PRIORITY_REGISTRY.append(CrewPriorityEntry(ability_name, priority))


def unregister_crew_priority(ability_name: str) -> None:
    """Remove a previously registered crew-priority binding (no-op if absent)."""
    global CREW_PRIORITY_REGISTRY
    CREW_PRIORITY_REGISTRY = [
        e for e in CREW_PRIORITY_REGISTRY if e.ability_name != ability_name
    ]


def lookup_crew_priority(component: "Component") -> int:
    """Return the lowest priority value across the abilities the component has."""
    best = CREW_PRIORITY_DEFAULT
    for entry in CREW_PRIORITY_REGISTRY:
        if entry.priority < best and component.has_ability(entry.ability_name):
            best = entry.priority
            if best == 0:
                return 0
    return best


# ---------------------------------------------------------------------------
# Stat contributor registry — PROJ-367 Phase 2 unified pipeline
# ---------------------------------------------------------------------------


# Contributor signature: ``(ship, comp, acc) -> None``. ``acc`` is the
# Phase-3 accumulator (Phase 2: still a Dict; Phase 3: typed
# ``StatAccumulator`` dataclass). Built-in defaults and modder entries
# share the same contract.
StatContributorFn = Callable[["Ship", "Component", Any], None]


class RegistrationConflictPolicy(Enum):
    """How to handle registering for an ability that already has an entry.

    See module docstring for full semantics.
    """

    REPLACE_WARN = "replace_warn"  # default — log + replace
    REPLACE_SILENT = "replace_silent"
    APPEND = "append"
    ERROR = "error"


class RegistrationConflictError(Exception):
    """Raised when ``policy=ERROR`` and the ability already has an entry."""


class CannotUnregisterDefaultError(Exception):
    """Raised when attempting to unregister a default entry by handle.

    Defaults are managed via the seed/reset cycle, not direct unregister.
    """


@dataclass(frozen=True)
class RegistrationHandle:
    """Identifies a registered entry for unambiguous unregister.

    The ``entry_id`` is monotonic across the process and unique per entry,
    so APPEND entries (which share an ability_name with the default) can
    be individually addressed.
    """

    ability_name: str
    entry_id: int


@dataclass
class StatContributorEntry:
    """One registered stat contributor.

    ``is_default`` marks built-in seed entries. ``phase_order`` controls
    iteration order across the registry — built-ins use 10..50, modders
    default to 99.
    """

    ability_name: str
    contributor: StatContributorFn
    entry_id: int
    is_default: bool = False
    phase_order: int = 99

    def as_handle(self) -> RegistrationHandle:
        return RegistrationHandle(self.ability_name, self.entry_id)


class _StatContributorRegistry:
    """Container for stat-contributor entries with phase-ordered iteration.

    The container holds a list per ability_name (to support APPEND policy),
    plus an "active" entry per ability_name that takes precedence after a
    REPLACE_*. ``iter_for(comp)`` yields all relevant entries in
    ``phase_order`` ascending (then registration order as tie-breaker).
    """

    __slots__ = ("_entries", "_replacements")

    def __init__(self) -> None:
        # ability_name -> list of entries (ordered: default first if any,
        # then APPEND entries in registration order). REPLACE_* entries are
        # NOT stored here — they live in ``_replacements`` so unregistering
        # naturally restores the default.
        self._entries: Dict[str, List[StatContributorEntry]] = {}
        # ability_name -> the currently-active replacement entry (if any).
        # When set, the replacement entry is the "active" entry for that
        # ability; the default in ``_entries`` is suppressed.
        self._replacements: Dict[str, StatContributorEntry] = {}

    # -- mutation -----------------------------------------------------

    def add_default(self, entry: StatContributorEntry) -> None:
        """Add a default-seeded entry. There is exactly one default per ability."""
        if not entry.is_default:
            raise ValueError("add_default requires entry.is_default=True")
        existing = self._entries.get(entry.ability_name, [])
        if any(e.is_default for e in existing):
            raise ValueError(
                f"Default already seeded for ability {entry.ability_name!r}"
            )
        self._entries.setdefault(entry.ability_name, []).insert(0, entry)

    def add_replacement(self, entry: StatContributorEntry) -> None:
        """Install a REPLACE_* entry (suppresses the default while live)."""
        self._replacements[entry.ability_name] = entry

    def add_appended(self, entry: StatContributorEntry) -> None:
        """Append a non-replacing entry (coexists with the default)."""
        self._entries.setdefault(entry.ability_name, []).append(entry)

    def remove_handle(self, handle: RegistrationHandle) -> None:
        """Remove the entry matching ``handle``.

        Replacement entries: removed; the underlying default (if any) becomes
        active again. Appended entries: removed in place. Defaults: raise.
        """
        # Replacement?
        repl = self._replacements.get(handle.ability_name)
        if repl is not None and repl.entry_id == handle.entry_id:
            del self._replacements[handle.ability_name]
            return
        # Appended (or default)?
        entries = self._entries.get(handle.ability_name, [])
        for i, e in enumerate(entries):
            if e.entry_id == handle.entry_id:
                if e.is_default:
                    raise CannotUnregisterDefaultError(
                        f"Cannot unregister default contributor for "
                        f"{handle.ability_name!r}; defaults are managed "
                        f"via seed/reset."
                    )
                del entries[i]
                if not entries:
                    del self._entries[handle.ability_name]
                return
        # Silent if not found — matches old `pop(name, None)` semantics
        # for unknown handles.

    def clear(self) -> None:
        self._entries.clear()
        self._replacements.clear()

    # -- queries ------------------------------------------------------

    def get_active_entry(self, ability_name: str) -> Optional[StatContributorEntry]:
        """The single 'active' entry for an ability — replacement (if any) else default."""
        repl = self._replacements.get(ability_name)
        if repl is not None:
            return repl
        entries = self._entries.get(ability_name, [])
        # If there's a replacement absent but appends without a default,
        # the first entry is the active one.
        return entries[0] if entries else None

    def get_entries(self, ability_name: str) -> List[StatContributorEntry]:
        """All entries for an ability (replacement first if any, then default + appends)."""
        result: List[StatContributorEntry] = []
        repl = self._replacements.get(ability_name)
        if repl is not None:
            result.append(repl)
            # When a replacement is active, the default is suppressed; only
            # appends fire alongside the replacement.
            for e in self._entries.get(ability_name, []):
                if not e.is_default:
                    result.append(e)
        else:
            result.extend(self._entries.get(ability_name, []))
        return result

    def get(self, ability_name: str) -> Optional[StatContributorEntry]:
        """Backward-compat: dict-like ``.get(name)`` returns the active entry."""
        return self.get_active_entry(ability_name)

    def iter_for(self, comp: "Component"):
        """Yield every entry whose ability the component has, in phase_order ascending.

        Replacement entries inherit ``phase_order=99`` unless explicitly
        overridden, so they fire after non-replaced built-ins (mirroring the
        legacy "skip-built-in-then-modder-runs-last" semantics).
        """
        candidates: List[StatContributorEntry] = []
        # Iterate over every known ability_name (default + replacement +
        # append). Use a set union of keys.
        names = set(self._entries.keys()) | set(self._replacements.keys())
        for name in names:
            if not comp.has_ability(name):
                continue
            for entry in self.get_entries(name):
                candidates.append(entry)
        # Stable sort by (phase_order, entry_id) — entry_id is monotonic so
        # ties resolve in registration order.
        candidates.sort(key=lambda e: (e.phase_order, e.entry_id))
        for entry in candidates:
            yield entry

    # -- introspection (used by tests) --------------------------------

    def __contains__(self, ability_name: str) -> bool:
        return self.get_active_entry(ability_name) is not None

    def __len__(self) -> int:
        return len(self._replacements) + sum(
            len(v) for v in self._entries.values()
        )


STAT_CONTRIBUTOR_REGISTRY = _StatContributorRegistry()


# ---------------------------------------------------------------------------
# Public registration API
# ---------------------------------------------------------------------------


_entry_id_counter = count(start=1)


def _next_entry_id() -> int:
    return next(_entry_id_counter)


# Default phase-order map for built-ins. Domain modules register through
# ``_seed_builtin_contributors`` and pass an explicit phase_order; this
# constant is the canonical source for the four built-in domains.
DEFAULT_PHASE_ORDER: Dict[str, int] = {
    "movement": 10,
    "defense": 20,
    "hangar": 40,
    "command": 50,
}


def register_stat_contributor(
    ability_name: str,
    contributor: StatContributorFn,
    *,
    policy: RegistrationConflictPolicy = RegistrationConflictPolicy.REPLACE_WARN,
    phase_order: int = 99,
    default: bool = False,
) -> RegistrationHandle:
    """Register a Phase-3 stat contributor.

    ``policy`` controls how conflicts with an existing entry for the same
    ``ability_name`` are resolved (see module docstring).

    ``default=True`` is reserved for ``_seed_builtin_contributors``. Modder
    code must NOT pass ``default=True`` — it would create a parallel
    "default" without going through the seed cycle and would not be
    re-seeded by ``reset_stat_contributor_registry``.

    Returns a ``RegistrationHandle`` for unambiguous unregister.
    """
    eid = _next_entry_id()
    entry = StatContributorEntry(
        ability_name=ability_name,
        contributor=contributor,
        entry_id=eid,
        is_default=default,
        phase_order=phase_order,
    )

    if default:
        STAT_CONTRIBUTOR_REGISTRY.add_default(entry)
        return entry.as_handle()

    # Non-default registration — check for conflicts.
    active = STAT_CONTRIBUTOR_REGISTRY.get_active_entry(ability_name)
    if active is None:
        # No conflict — install as a fresh entry.
        STAT_CONTRIBUTOR_REGISTRY.add_appended(entry)
        return entry.as_handle()

    # There IS an existing active entry. Apply policy.
    if policy == RegistrationConflictPolicy.ERROR:
        raise RegistrationConflictError(
            f"Stat contributor for {ability_name!r} already registered; "
            f"policy=ERROR. Unregister first or use a different policy."
        )
    if policy == RegistrationConflictPolicy.APPEND:
        STAT_CONTRIBUTOR_REGISTRY.add_appended(entry)
        return entry.as_handle()
    if policy in (
        RegistrationConflictPolicy.REPLACE_WARN,
        RegistrationConflictPolicy.REPLACE_SILENT,
    ):
        if policy == RegistrationConflictPolicy.REPLACE_WARN:
            logger.warning(
                "register_stat_contributor: replacing existing entry for "
                "ability %r (phase_order=%d). Pass policy=REPLACE_SILENT to "
                "suppress this warning, APPEND to coexist with the default, "
                "or ERROR to raise instead.",
                ability_name,
                phase_order,
            )
        STAT_CONTRIBUTOR_REGISTRY.add_replacement(entry)
        return entry.as_handle()

    raise ValueError(f"Unknown RegistrationConflictPolicy: {policy!r}")


def unregister_stat_contributor(handle: RegistrationHandle) -> None:
    """Remove the entry matching ``handle``.

    Replacement entries: removed; the underlying default (if any) becomes
    active again. Appended entries: removed in place. Defaults: raise
    ``CannotUnregisterDefaultError`` (defaults are managed via seed/reset).
    """
    if not isinstance(handle, RegistrationHandle):
        raise TypeError(
            f"unregister_stat_contributor takes a RegistrationHandle, got "
            f"{type(handle).__name__}. Capture the handle returned from "
            f"register_stat_contributor."
        )
    STAT_CONTRIBUTOR_REGISTRY.remove_handle(handle)


def reset_stat_contributor_registry() -> None:
    """Test-support hook: clear AND re-seed default contributors (idempotent).

    Called by the root ``conftest.py`` reset_game_state fixture before/after
    every test. Built-in defaults are restored via ``_seed_builtin_contributors``
    so each test starts with the canonical default-seeded registry.
    """
    STAT_CONTRIBUTOR_REGISTRY.clear()
    _seed_builtin_contributors()


def _seed_builtin_contributors() -> None:
    """Register the built-in Phase-3 contributors as default entries.

    Imports the per-ability ``contribute_*`` functions from the domain
    modules. Idempotent: safe to call after ``clear()``. Phase ordering
    (movement=10, defense=20, hangar=40, command=50) preserves the legacy
    call order for non-replaced built-ins so the golden snapshot stays
    bit-identical.
    """
    # Imports are local to avoid circular-import storms at module load.
    from game.simulation.entities.stat_contributors import (
        command as _cmd,
        defense as _def,
        launch as _launch,
        movement as _mov,
    )

    p_mov = DEFAULT_PHASE_ORDER["movement"]
    p_def = DEFAULT_PHASE_ORDER["defense"]
    p_hangar = DEFAULT_PHASE_ORDER["hangar"]
    p_cmd = DEFAULT_PHASE_ORDER["command"]

    # Movement domain (phase_order=10) — split from aggregate_propulsion.
    register_stat_contributor(
        "CombatPropulsion", _mov.contribute_combat_propulsion,
        default=True, phase_order=p_mov,
    )
    register_stat_contributor(
        "StrategicMovement", _mov.contribute_strategic_movement,
        default=True, phase_order=p_mov,
    )
    register_stat_contributor(
        "WarpJump", _mov.contribute_warp_jump,
        default=True, phase_order=p_mov,
    )
    register_stat_contributor(
        "ManeuveringThruster", _mov.contribute_maneuvering_thruster,
        default=True, phase_order=p_mov,
    )

    # Defense domain (phase_order=20) — split from aggregate_defense.
    # Decision (Task 2.4): Armor stays a separate `contribute_armor` entry
    # (clean per-ability split). Shield energy cost stays merged into
    # `contribute_shield_regeneration` (the energy-cost extraction is
    # tightly coupled to the regen-component idiom and splitting it would
    # require a separate `RequiresShieldRegen` predicate that doesn't exist).
    register_stat_contributor(
        "Armor", _def.contribute_armor,
        default=True, phase_order=p_def,
    )
    register_stat_contributor(
        "ShieldProjection", _def.contribute_shield_projection,
        default=True, phase_order=p_def,
    )
    register_stat_contributor(
        "ShieldRegeneration", _def.contribute_shield_regeneration,
        default=True, phase_order=p_def,
    )

    # Hangar domain (phase_order=40) — split from aggregate_hangar.
    # Decision (Task 2.4): VehicleStorage stays gated under VehicleLaunch
    # (the legacy semantics required a launch bay to count storage; storage
    # without a launch ability is meaningless). The single contributor
    # `contribute_vehicle_launch` reads both abilities.
    register_stat_contributor(
        "VehicleLaunch", _launch.contribute_vehicle_launch,
        default=True, phase_order=p_hangar,
    )

    # Command domain (phase_order=50) — split from track_multiplex.
    register_stat_contributor(
        "MultiplexTracking", _cmd.contribute_multiplex_tracking,
        default=True, phase_order=p_cmd,
    )


# NOTE: seeding is performed by ``stat_contributors/__init__.py`` AFTER the
# four domain modules (command, defense, launch, movement) finish loading.
# Calling ``_seed_builtin_contributors()`` from inside this module's body
# would create a circular import (command/defense/launch/movement all
# import names from this module).


__all__ = [
    "CREW_PRIORITY_REGISTRY",
    "CREW_PRIORITY_DEFAULT",
    "CrewPriorityEntry",
    "register_crew_priority",
    "unregister_crew_priority",
    "lookup_crew_priority",
    "STAT_CONTRIBUTOR_REGISTRY",
    "StatContributorEntry",
    "StatContributorFn",
    "RegistrationConflictPolicy",
    "RegistrationConflictError",
    "RegistrationHandle",
    "CannotUnregisterDefaultError",
    "DEFAULT_PHASE_ORDER",
    "register_stat_contributor",
    "unregister_stat_contributor",
    "reset_stat_contributor_registry",
]
