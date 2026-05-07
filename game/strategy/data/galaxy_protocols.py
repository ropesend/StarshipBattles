"""Read + read+write surface protocols for galaxy/planet/star. PROJ-372.

Five protocols, two surface shapes:

- **Pure-read:** ``IGalaxySystemGraph``, ``IGalaxySpatialQuery``,
  ``IHabitabilityCalculator``. These describe query surfaces with no
  state mutation.
- **Read+write:** ``IStockpileHolder``, ``IStagingYardHolder``. These
  describe the per-item add/consume/remove surface that ``Planet``
  exposes today. Capacity / conservation invariants belong to PROJ-370.
  PROJ-370's higher-level batch-mutation surface (`IPlanetMutator`'s
  ``set_max_stockpile`` / ``add_staging_item`` / ``pop_staging_item``)
  composes with these per-item protocols rather than replacing them.

Goals (G4, G5 in PROJ-372 plan.md):

- `IHabitabilityCalculator` lets modders inject a custom habitability
  calculator via `ApplicationContext` without monkey-patching.
- `IGalaxySystemGraph` + `IGalaxySpatialQuery` let services and tests
  stub the galaxy with a 3-system graph instead of constructing a real
  100-system universe.
- `IStockpileHolder` + `IStagingYardHolder` describe the typed surface
  for planet write paths so future contract tests (PROJ-370) can layer
  on top.

PROJ-372 only DEFINES these protocols and asserts existing classes
satisfy them structurally. Capacity / conservation invariants belong
to PROJ-370.
"""
from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
    Protocol,
    runtime_checkable,
)

if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
    from game.strategy.data.galaxy import StarSystem
    from game.strategy.data.planet import Planet


__all__ = [
    "IHabitabilityCalculator",
    "IGalaxySystemGraph",
    "IGalaxySpatialQuery",
    "IStockpileHolder",
    "IStagingYardHolder",
]


@runtime_checkable
class IHabitabilityCalculator(Protocol):
    """Computes the population-weighted habitability multiplier for a colony.

    Implementations: `PlanetHabitabilityService` (Phase 2). Modders may
    inject alternates via `set_default_planet_habitability_service`.

    The standard implementation caches per-turn on the planet's transient
    cache fields (`_cached_habitability_multiplier`,
    `_cached_multiplier_turn`); custom implementations may use any cache
    strategy or none.
    """

    def get_cached(
        self, planet: "Planet", race_registry: Any, turn: int
    ) -> float:
        """Return the habitability multiplier in [0, 1].

        Uncolonized / degenerate cases should return 1.0 (additive
        neutral, matches the legacy default).
        """
        ...


@runtime_checkable
class IGalaxySystemGraph(Protocol):
    """Read protocol for the galaxy's system topology.

    Pathfinding (Phase 4) consumes this so tests can stub a 3-system
    graph rather than constructing a full Galaxy.
    """

    @property
    def systems(self) -> Dict["HexCoord", "StarSystem"]:
        """Hex-coord-keyed map of all systems."""
        ...

    def get_system_by_name(self, name: str) -> Optional["StarSystem"]:
        """Return the system with this name, or None."""
        ...


@runtime_checkable
class IGalaxySpatialQuery(Protocol):
    """Read protocol for spatial lookups against the galaxy.

    Mirrors `GalaxySpatialIndex` public methods. Services and tests
    can stub or wrap this surface independently of a full Galaxy.
    """

    def get_system_at_location(
        self, location: "HexCoord"
    ) -> Optional["StarSystem"]:
        """Return the system at this global hex, or None for deep space."""
        ...

    def get_planets_at_global_hex(
        self, global_hex: "HexCoord"
    ) -> List["Planet"]:
        """Return planets at this global hex (empty list if none)."""
        ...

    def get_zones_at_global_hex(self, global_hex: "HexCoord") -> list:
        """Return zone occupants (stars, Dyson Spheres) at this hex."""
        ...

    def get_planet_global_hex(
        self, planet: "Planet"
    ) -> Optional["HexCoord"]:
        """Return planet's global hex, or None if unregistered."""
        ...


@runtime_checkable
class IStockpileHolder(Protocol):
    """Read+write surface for planet-side resource stockpiles.

    Planet currently satisfies this structurally. Capacity / conservation
    contract tests are PROJ-370's responsibility, not PROJ-372's.
    """

    def add_to_stockpile(self, resource_type: str, amount: float) -> float:
        """Add `amount` of `resource_type`; return overflow."""
        ...

    def consume_from_stockpile(
        self, resource_type: str, amount: float
    ) -> bool:
        """All-or-nothing consume; return True on success."""
        ...

    def has_stockpile(self, costs: dict) -> bool:
        """True iff every resource->amount in `costs` is satisfied."""
        ...

    def get_stockpile(self, resource_type: str) -> float:
        """Current stockpiled amount, 0.0 if absent."""
        ...


@runtime_checkable
class IStagingYardHolder(Protocol):
    """Read+write surface for planet-side staging-yard storage.

    Planet currently satisfies this structurally. Mass-cap contract
    tests are PROJ-370's responsibility.
    """

    def get_staging_mass(self) -> float:
        """Total mass of items currently in the staging yard."""
        ...

    def add_to_staging_yard(self, item: Dict[str, Any]) -> bool:
        """Add `item`; return False on insufficient capacity."""
        ...

    def remove_from_staging_yard(
        self, index: int
    ) -> Optional[Dict[str, Any]]:
        """Remove by index; return removed item or None."""
        ...

    @property
    def max_staging_mass(self) -> float:
        """Maximum cumulative mass allowed (0.0 = unlimited)."""
        ...
