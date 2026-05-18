"""Planet query slice (PROJ-309 sub-phase 3.7).

Owns planet-shaped reads. The lazy `_planet_index` lives on
`FacadeSessionState` so multiple slices (planet + economy validation) share
the same cache.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from game.core.hex_math import HexCoord
from game.core.validation import ValidationResult
from game.strategy.data.containable import (
    ContainableKind,
    ItemContainable,
    ItemRef,
    ResourceContainable,
)
from game.strategy.data.container import Container, ContainerPolicy
from game.strategy.facade.dto import ContainerSnapshotInfo, PlanetInfo

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet
    from game.strategy.facade.slices._facade_state import FacadeSessionState


class PlanetSlice:
    """Planet reads + planet-shaped validation."""

    __slots__ = ("_state",)

    def __init__(self, state: "FacadeSessionState") -> None:
        self._state = state

    # ------------------------------------------------------------------
    # ID helpers (forwarded for tests asserting on the cached lookup)
    # ------------------------------------------------------------------

    def build_planet_index(self) -> dict:
        """Build planet-id -> Planet lookup dict (PROJ-254)."""
        return self._state.build_planet_index()

    def get_planet_by_id(self, planet_id: int) -> Optional["Planet"]:
        """Internal helper to get a planet by ID using index (PROJ-254)."""
        return self._state.get_planet_by_id(planet_id)

    # ------------------------------------------------------------------
    # Public reads
    # ------------------------------------------------------------------

    def get_planet(self, planet_id: int) -> Optional[PlanetInfo]:
        """Get planet information by ID."""
        planet = self._state.get_planet_by_id(planet_id)
        if planet is None:
            return None
        return PlanetInfo.from_planet(planet)

    def get_planets_at_hex(self, hex_coord: HexCoord) -> List[PlanetInfo]:
        """Get planets whose global position exactly matches the given hex coordinate.

        Only returns planets at the specific hex — not all planets in the
        system. A planet's global position is
        ``system.global_location + planet.location``. Uses radius search to
        resolve which system owns the hex when a strict lookup misses (e.g.
        clicking an inner hex that isn't the system center).
        """
        # 1. Try strict lookup first (fast & correct for exact hits)
        system = self._state.session.galaxy.get_system_at_location(hex_coord)

        # 2. If strict failed, try radius/ownership lookup (robust for area clicks)
        if system is None:
            from game.strategy.services.galaxy_pathfinding_service import (
                GalaxyPathfindingService,
            )
            system = GalaxyPathfindingService(
                self._state.session.galaxy,
            ).get_system_at_hex(hex_coord, radius=50)

        if system is None:
            return []

        target_planets = []
        for p in system.planets:
            p_global = system.global_location + p.location
            if p_global == hex_coord:
                target_planets.append(p)

        return [PlanetInfo.from_planet(planet) for planet in target_planets]

    # ------------------------------------------------------------------
    # Container snapshots (PROJ-437 Phase 1a)
    # ------------------------------------------------------------------

    def get_planet_containers(
        self, planet_id: int,
    ) -> Tuple[ContainerSnapshotInfo, ...]:
        """Return container snapshots for a planet.

        PROJ-437 Phase 1a substrate. Emits two snapshots — the
        resource stockpile and the staging-yard items — projected from
        the planet's legacy storage shapes. The mutable Container is
        not constructed; the snapshot is built directly from the
        underlying dicts / list so per-resource caps do not reject
        existing contents at projection time.

        Returns an empty tuple when the planet ID is unknown.
        """
        planet = self._state.get_planet_by_id(planet_id)
        if planet is None:
            return ()
        return (
            _planet_stockpile_snapshot(planet),
            _planet_staging_yard_snapshot(planet),
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def can_colonize(
        self, fleet_id: int, planet_id: Optional[int]
    ) -> ValidationResult:
        """Check if a fleet can colonize a planet (without executing).

        Cross-domain query: needs both fleet AND planet lookup. Both go
        through `FacadeSessionState`, so this slice never reaches into
        `FleetSlice`.
        """
        fleet = self._state.get_fleet_by_id(fleet_id)
        if fleet is None:
            return ValidationResult.error("Fleet not found.")

        planet = None
        if planet_id is not None:
            planet = self._state.get_planet_by_id(planet_id)
            if planet is None:
                return ValidationResult.error("Planet not found.")

        return self._state.session.turn_engine.validate_colonize_order(
            self._state.session.galaxy, fleet, planet
        )


_RESOURCE_POLICY = ContainerPolicy(
    allowed_kinds=frozenset({ContainableKind.RESOURCE}),
    allowed_type_ids=None,
)
_ITEM_POLICY = ContainerPolicy(
    allowed_kinds=frozenset({ContainableKind.ITEM}),
    allowed_type_ids=None,
)


def _planet_stockpile_snapshot(planet: "Planet") -> ContainerSnapshotInfo:
    stockpile = getattr(planet, "stockpile", None) or {}
    max_stockpile = getattr(planet, "max_stockpile", None) or {}
    if max_stockpile:
        # F-A-014: ``max_stockpile`` values are per-resource caps in
        # resource units, not mass. Convert each cap through
        # ``ResourceCatalog.get_mass_per_unit`` before summing — the
        # bare ``sum(...)`` was implicitly treating every resource as
        # mass_per_unit == 1.0, which is wrong for vapors/fuel/exotics
        # whose mass_per_unit is ≪ 1.
        from game.core.resources import ResourceCatalog
        _catalog = ResourceCatalog.from_json()
        capacity_mass = float(sum(
            float(amount) * _catalog.get_mass_per_unit(rid)
            for rid, amount in max_stockpile.items()
        ))
    else:
        capacity_mass = float("inf")

    # Project at infinite capacity so existing contents are never
    # rejected even if the per-resource max sum is below the running
    # total. The snapshot reports the real cap so the UI can flag
    # over-capacity explicitly.
    container = Container(capacity_mass=float("inf"), policy=_RESOURCE_POLICY)
    for resource_id, amount in stockpile.items():
        container.add(ResourceContainable(resource_id), float(amount))

    return ContainerSnapshotInfo(
        container_id=f"planet:{planet.id}:stockpile",
        owner_kind="planet",
        owner_id=planet.id,
        label=f"{planet.name} — Stockpile",
        capacity_mass=capacity_mass,
        mass_used=container.mass_used,
        allowed_kinds=_RESOURCE_POLICY.allowed_kinds,
        entries=tuple(container.contents()),
    )


def _planet_staging_yard_snapshot(planet: "Planet") -> ContainerSnapshotInfo:
    items_raw = getattr(planet, "staging_yard", None) or []
    capacity_mass = float(getattr(planet, "max_staging_mass", 0.0) or 0.0)
    if capacity_mass <= 0.0:
        capacity_mass = float("inf")

    container = Container(capacity_mass=float("inf"), policy=_ITEM_POLICY)
    for idx, item in enumerate(items_raw):
        design_id = item.get("design_id") or item.get("name", "unknown")
        instance_id = item.get("instance_id") or f"staging-{idx}"
        mass = float(item.get("mass", 0.0))
        container.add(
            ItemContainable(ItemRef(
                design_id=design_id,
                instance_id=instance_id,
                mass=mass,
                state={},
            )),
            1,
        )

    return ContainerSnapshotInfo(
        container_id=f"planet:{planet.id}:staging_yard",
        owner_kind="planet",
        owner_id=planet.id,
        label=f"{planet.name} — Staging Yard",
        capacity_mass=capacity_mass,
        mass_used=container.mass_used,
        allowed_kinds=_ITEM_POLICY.allowed_kinds,
        entries=tuple(container.contents()),
    )
