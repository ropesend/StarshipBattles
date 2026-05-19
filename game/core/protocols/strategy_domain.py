"""Strategy-layer domain protocols (organisational/empire-scoped types) and TypeGuards.

These are the abstract organisational types: empires, facilities, races,
ship instances. Concrete galaxy-map entities (stars, planets, fleets, etc.)
live in `strategy_entities.py`.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol, TYPE_CHECKING, TypeGuard, runtime_checkable

from game.core.protocols.common import _has_attrs

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig


@runtime_checkable
class IEmpire(Protocol):
    """Protocol for Empire entities (PROJ-193)."""
    @property
    def id(self) -> int:
        """Unique empire identifier."""
        ...

    @property
    def name(self) -> str:
        """Empire name."""
        ...

    @property
    def color(self) -> Any:
        """Empire color (RGB tuple)."""
        ...

    @property
    def flag_id(self) -> str:
        """Custom flag directory."""
        ...

    @property
    def portrait_id(self) -> str:
        """Race portrait filename."""
        ...

    @property
    def empire_theme_id(self) -> str:
        """Ship theme for this empire's designs."""
        ...

    @property
    def race_config(self) -> Any | None:
        """Full race configuration (RaceConfig or None)."""
        ...

    @property
    def colonies(self) -> list[Any]:
        """List of owned Planet objects."""
        ...

    @property
    def fleets(self) -> list[Any]:
        """List of Fleet objects."""
        ...

    @property
    def resource_pool(self) -> dict[str, float]:
        """Read-only aggregate of resource amounts across the empire.

        PROJ-436 Phase 5: pure aggregation over the empire's colony
        stockpiles. The concrete ``Empire.resource_pool`` walks
        ``self.colonies[*].stockpile`` and sums by ``resource_id``;
        the legacy ``Empire._fleet_resource_pool`` durable summand
        was deleted in Phase 5 and fleet construction now draws
        directly from the build-location's container.

        Per PROJ-436 Phase 0 D2: uncached pure query. If profiling
        ever shows the aggregation is hot at large-empire scale,
        caching with explicit invalidation (PROJ-293 pattern) can
        land as a sibling sub-phase.

        Used for UI display and economy reporting. **Not** a write
        surface — protocols never expose write paths against the
        aggregate; per-colony writes route through
        ``IPlanetMutator``.
        """
        ...

    @property
    def max_storage(self) -> dict[str, float]:
        """Storage capacity per resource type.

        Set by ``HarvestingEngine`` each turn (routed through
        ``EmpireWriteService.replace_max_storage``) by summing the
        capacity contribution of every operational storage component
        across the empire's planets. Read by the treasury panel,
        empire-economy snapshot, build-queue affordability helpers,
        and the strategy-UI resource bar.

        **Not** a write surface — protocols never expose write paths
        against the aggregate; storage capacity flows from per-
        component contributions through ``EmpireWriteService``.
        """
        ...

    @property
    def built_ship_designs(self) -> Any:
        """Set of design_ids that were ever built."""
        ...


@runtime_checkable
class IFacility(Protocol):
    """Protocol for PlanetaryFacility entities (PROJ-193)."""
    @property
    def instance_id(self) -> str:
        """Unique facility ID (uuid)."""
        ...

    @property
    def design_id(self) -> str:
        """Reference to design file."""
        ...

    @property
    def name(self) -> str:
        """Facility name."""
        ...

    @property
    def design_data(self) -> dict[str, Any]:
        """Full complex design (from JSON)."""
        ...

    @property
    def is_operational(self) -> bool:
        """True if facility is operational."""
        ...

    @property
    def construction_queue(self) -> list[Any]:
        """Facility's construction queue."""
        ...

    @property
    def consumable_levels(self) -> dict[str, float]:
        """Consumable levels stored in this facility.

        PROJ-436 Phase 0 D1 / PROJ-446 Phase 2 (F-C-013): the
        annotation is intentionally a writable ``dict[str, float]``
        rather than the read-only ``Mapping[str, float]`` used for
        ship cargo / planet stockpile. The Phase-6 audit chose to
        leave this as-is because no transfer-UI / mutator use case
        had materialised, so promoting consumables to a write-service
        + ``Mapping`` view would have been speculative work.

        The deliberate inconsistency is also pinned at the static-
        guard layer by
        ``tests/static_guards/test_no_legacy_protocol_names.py``
        (``test_ifacility_still_declares_consumable_levels``).

        If a transfer-UI / mutator use case lands later, this
        annotation should be narrowed to ``Mapping[str, float]`` and
        a sibling ``IFacilityMutator`` should land alongside.
        """
        ...


@runtime_checkable
class IRaceRegistry(Protocol):
    """Read-only registry for resolving race_id -> RaceConfig (PROJ-287).

    Decouples consumers (UI panels, formulas, engines) from the file-backed
    RaceLibrary. Implementations are free to cache, lazy-load, or proxy.
    Returns None when the race_id is unknown — callers must handle missing
    races gracefully (extinct species, save drift, typos).
    """

    def get_race(self, race_id: str) -> 'RaceConfig | None':
        """Resolve a race_id to its RaceConfig, or None if unknown."""
        ...


@runtime_checkable
class IShipInstance(Protocol):
    """Protocol for ShipInstance entities (PROJ-193)."""
    @property
    def design_id(self) -> str:
        """Reference to ship design file/name."""
        ...

    @property
    def design_name(self) -> str:
        """Design name (may be same as design_id)."""
        ...

    @property
    def design_data(self) -> dict[str, Any]:
        """Full serialized ship template."""
        ...

    @property
    def hull_class(self) -> str:
        """Ship's hull class (from design_data)."""
        ...

    @property
    def cargo_contents(self) -> Mapping[str, int]:
        """Cargo contents (cargo_type -> current amount), read-only view.

        PROJ-449 Phase 5 (F-C-014 closure): the concrete-class
        ``@cargo_contents.setter`` was retired in Phase 4 alongside the
        legacy-kwarg constructor wrapper, so this property is now
        read-only end-to-end. The protocol annotation has been
        ``Mapping[str, int]`` since PROJ-446 Phase 2.

        Writers must route through the cargo manager API on the
        concrete class: ``ship._cargo_mgr.set_cargo`` /
        ``add_to_cargo`` / ``remove_from_cargo`` / ``get_all_cargo`` /
        ``total_cargo_units`` / ``has_cargo``.
        """
        ...

    @property
    def ship_name(self) -> str:
        """Instance name (alias for name property)."""
        ...

    @property
    def serial_number(self) -> int | None:
        """Serial number unique per design within empire."""
        ...

    def get_calculated_stats(self, force_refresh: bool = False) -> dict[str, Any]:
        """Get calculated stats from components, respecting damage state."""
        ...


# =============================================================================
# TypeGuards
# =============================================================================


def is_empire(obj: Any) -> TypeGuard[IEmpire]:
    """Check if obj has empire attributes (id, fleets)."""
    return _has_attrs(obj, 'id', 'fleets')


def is_facility(obj: Any) -> TypeGuard[IFacility]:
    """Check if obj has facility attributes (instance_id, design_id)."""
    return _has_attrs(obj, 'instance_id', 'design_id')


def is_ship_instance(obj: Any) -> TypeGuard[IShipInstance]:
    """Check if obj has ship instance attributes (design_id, design_data)."""
    return _has_attrs(obj, 'design_id', 'design_data')
