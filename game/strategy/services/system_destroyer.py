"""SystemDestroyer — safely tear down an entire star system.

Single entry point for any superweapon that removes a whole system
(STELLERATE_STAR, CREATE_DYSON_SPHERE). Uses a **collect-then-mutate**
pattern: every entity the operation will destroy is listed BEFORE any
mutation happens, so downstream queries aren't affected by half-torn-down
state.

Two categories of affected entities:

- Planets and stars live on the `StarSystem`. Enumerated from the live
  system prior to any removal.
- Fleets are collected by **hex distance**: every fleet whose
  `fleet.location` is within the system's 50-hex radius
  (matching `get_system_at_hex(radius=50)` in
  `game/strategy/data/pathfinding.py`). This is broader than the old
  `GalaxySpatialIndex.get_all_fleets_in_system`, which only checked hexes
  that happened to contain a placed entity — fleets at "open space"
  hexes inside the system would silently survive.

Why not keep doing it inline in the superweapon handler?
- Centralizes the collection rule so adding a new system-destroying
  superweapon is one line ("call `destroy_system`") — there's nowhere
  for the planet-before-fleet ordering bug to re-emerge.
- The PROJ-277 ordering bug (`system.planets` scanned AFTER planets are
  unregistered) can't recur because the collection phase runs first and
  stashes references locally.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, TYPE_CHECKING, Tuple

from game.core.hex_math import hex_distance

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import Galaxy, StarSystem
    from game.strategy.data.planet import Planet
    from game.strategy.data.stars import Star


# Matches the "what hexes are 'in' the system" radius used everywhere else
# (see pathfinding.get_system_at_hex). Keeping this as a module constant
# makes the rule searchable and easy to change in one place.
SYSTEM_RADIUS_HEXES: int = 50


@dataclass(frozen=True)
class SystemDestructionPlan:
    """Immutable snapshot of what a system-destruction pass will remove.

    Captured BEFORE any mutation. Anything added to the system after this
    plan is built will NOT be destroyed — callers that care about in-flight
    fleets should treat this snapshot as authoritative.
    """
    system: "StarSystem"
    planets: Tuple["Planet", ...]
    stars: Tuple["Star", ...]
    fleets: Tuple[Tuple["Empire", "Fleet"], ...]

    @property
    def fleet_count(self) -> int:
        return len(self.fleets)


@dataclass
class SystemDestructionResult:
    """What actually happened after executing a plan."""
    planets_removed: int = 0
    stars_removed: int = 0
    fleets_removed: int = 0
    ship_names: List[str] = field(default_factory=list)


def collect_system_contents(
    system: "StarSystem",
    galaxy: "Galaxy",
    empires,
    *,
    radius: int = SYSTEM_RADIUS_HEXES,
) -> SystemDestructionPlan:
    """Snapshot the entities a system-destroying superweapon will remove.

    A fleet is considered "in the system" if its location is within
    `radius` hexes of the system's `global_location`. This is strictly
    broader than the entity-hex set used by `GalaxySpatialIndex.get_all_fleets_in_system`
    — it catches ships in the empty space between planets.

    Args:
        system: The target system. `system.planets` and `system.stars`
            must still be populated (no removals done yet).
        galaxy: Galaxy (unused today but threaded for future spatial
            index hooks; keeping the signature stable avoids churn
            in callers later).
        empires: Iterable of Empire objects whose fleets are candidates.
        radius: Hex radius defining "in the system" (default 50).

    Returns:
        Immutable `SystemDestructionPlan`.
    """
    center = system.global_location
    planets = tuple(system.planets)
    stars = tuple(system.stars)

    fleets: List[Tuple["Empire", "Fleet"]] = []
    for empire in empires:
        for fleet in list(empire.fleets):
            # `<` matches pathfinding.get_system_at_hex's `dist < radius`.
            if hex_distance(fleet.location, center) < radius:
                fleets.append((empire, fleet))

    return SystemDestructionPlan(
        system=system,
        planets=planets,
        stars=stars,
        fleets=tuple(fleets),
    )


def destroy_system(
    plan: SystemDestructionPlan,
    galaxy: "Galaxy",
    empires,
    *,
    remove_stars: bool = True,
    event_bus: Any = None,
    empire_mutator: Any = None,
) -> SystemDestructionResult:
    """Execute a destruction plan: remove planets, stars, fleets.

    Ordering inside this function is safe because `plan` holds local
    references — queries that once depended on `system.planets` being
    populated (e.g. the pre-PROJ-277 spatial-index fleet lookup) have
    already run during `collect_system_contents`.

    Args:
        plan: Snapshot from `collect_system_contents`.
        galaxy: Galaxy for planet unregistration.
        empires: All empires (planets may be owned by any of them).
        remove_stars: If False, keep stars (e.g. CREATE_DYSON_SPHERE
            replaces the star with a Dyson Sphere planet, so callers
            might want to keep the star removal logic separate).
        event_bus: Optional EventBus. Currently unused — per-entity
            event emission stays with the superweapon handler that
            knows the specific event type (STAR_DESTROYED vs
            DYSON_SPHERE_CREATED) and the message framing.

    Returns:
        `SystemDestructionResult` with counts and ship names.
    """
    result = SystemDestructionResult()

    # PROJ-370 Phase 4: route Empire.colonies removals through IEmpireMutator.
    if empire_mutator is None:
        from game.strategy.services.empire_write_service import (
            EmpireWriteService,
        )
        empire_mutator = EmpireWriteService()

    # Remove planets: drop from owner empire's colonies (if owned) and
    # unregister from galaxy. Iterate all empires because planets may
    # belong to anyone.
    for planet in plan.planets:
        if getattr(planet, "owner_id", None) is not None:
            for emp in empires:
                empire_mutator.remove_colony(emp, planet)
        galaxy.unregister_planet(planet)
        result.planets_removed += 1

    # Remove fleets. `Empire.remove_fleet` auto-unregisters from the
    # galaxy via empire._galaxy.
    for owner_empire, victim_fleet in plan.fleets:
        for ship in getattr(victim_fleet, "ships", []):
            name = getattr(ship, "name", None)
            if name:
                result.ship_names.append(name)
        owner_empire.remove_fleet(victim_fleet, event_bus=event_bus)
        result.fleets_removed += 1

    if remove_stars:
        plan.system.stars = []
        result.stars_removed = len(plan.stars)

    return result
