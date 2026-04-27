"""Strategy-layer domain protocols (organisational/empire-scoped types) and TypeGuards.

These are the abstract organisational types: empires, facilities, races,
ship instances. Concrete galaxy-map entities (stars, planets, fleets, etc.)
live in `strategy_entities.py`.
"""

from typing import Any, Dict, List, Optional, Protocol, TYPE_CHECKING, TypeGuard, runtime_checkable

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
    def race_config(self) -> Optional[Any]:
        """Full race configuration (RaceConfig or None)."""
        ...

    @property
    def colonies(self) -> List[Any]:
        """List of owned Planet objects."""
        ...

    @property
    def fleets(self) -> List[Any]:
        """List of Fleet objects."""
        ...

    @property
    def resource_pool(self) -> Dict[str, float]:
        """Current resource amounts by type."""
        ...

    @property
    def max_storage(self) -> Dict[str, float]:
        """Storage capacity per resource type."""
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
    def design_data(self) -> Dict[str, Any]:
        """Full complex design (from JSON)."""
        ...

    @property
    def is_operational(self) -> bool:
        """True if facility is operational."""
        ...

    @property
    def construction_queue(self) -> List[Any]:
        """Facility's construction queue."""
        ...

    @property
    def consumable_levels(self) -> Dict[str, float]:
        """Consumable levels stored in this facility."""
        ...


@runtime_checkable
class IRaceRegistry(Protocol):
    """Read-only registry for resolving race_id -> RaceConfig (PROJ-287).

    Decouples consumers (UI panels, formulas, engines) from the file-backed
    RaceLibrary. Implementations are free to cache, lazy-load, or proxy.
    Returns None when the race_id is unknown — callers must handle missing
    races gracefully (extinct species, save drift, typos).
    """

    def get_race(self, race_id: str) -> Optional['RaceConfig']:
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
    def design_data(self) -> Dict[str, Any]:
        """Full serialized ship template."""
        ...

    @property
    def hull_class(self) -> str:
        """Ship's hull class (from design_data)."""
        ...

    @property
    def cargo_contents(self) -> Dict[str, int]:
        """Cargo contents (cargo_type -> current amount)."""
        ...

    @property
    def ship_name(self) -> str:
        """Instance name (alias for name property)."""
        ...

    @property
    def serial_number(self) -> Optional[int]:
        """Serial number unique per design within empire."""
        ...

    def get_calculated_stats(self, force_refresh: bool = False) -> Dict[str, Any]:
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
