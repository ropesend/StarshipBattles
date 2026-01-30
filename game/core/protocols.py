"""
Protocol definitions for type-safe duck typing replacement.

This module provides @runtime_checkable Protocol classes and TypeGuard
functions to replace hasattr/getattr patterns with proper type checking.

Usage:
    from game.core.protocols import is_fleet, is_planet, IFleet

    if is_fleet(obj):
        # obj is now typed as IFleet
        print(obj.ships)
    elif is_planet(obj):
        # obj is now typed as IPlanet
        print(obj.name)
"""

from typing import (
    Protocol,
    runtime_checkable,
    Optional,
    List,
    Tuple,
    Dict,
    Any,
    TypeVar,
    TYPE_CHECKING,
)

# Python 3.10+ has TypeGuard in typing, but for 3.9 compatibility use typing_extensions
try:
    from typing import TypeGuard
except ImportError:
    from typing_extensions import TypeGuard

if TYPE_CHECKING:
    from game.strategy.data.hex_math import HexCoord


# =============================================================================
# Registry Provider Protocol (PROJ-27)
# =============================================================================

@runtime_checkable
class IRegistryProvider(Protocol):
    """
    Protocol for registry access abstraction.

    PROJ-27/PROJ-50: Enables dependency injection for registry access, allowing
    services to be tested in isolation without relying on the global singleton.

    Implementations:
        - DefaultRegistryProvider: Delegates to RegistryManager singleton (production)
        - TestRegistryProvider: Provides isolated registry data (testing)

    Usage (PROJ-50 strict DI - registry is required):
        def calculate_stats(design: dict, registry: IRegistryProvider):
            # PROJ-50: registry is now required, not optional
            components = registry.get_components()
            ...
    """
    def get_components(self) -> Dict[str, Any]:
        """Get the component registry dictionary."""
        ...

    def get_modifiers(self) -> Dict[str, Any]:
        """Get the modifier registry dictionary."""
        ...

    def get_vehicle_classes(self) -> Dict[str, Any]:
        """Get the vehicle classes dictionary."""
        ...


# =============================================================================
# Base Protocols (Composable)
# =============================================================================

@runtime_checkable
class ILocatable(Protocol):
    """Protocol for objects with a location property."""
    @property
    def location(self) -> Any:
        """Entity's position (HexCoord for strategy, Vector2 for simulation)."""
        ...


@runtime_checkable
class INamed(Protocol):
    """Protocol for objects with a name property."""
    @property
    def name(self) -> str:
        """Human-readable display name, always non-empty."""
        ...


@runtime_checkable
class IOwnable(Protocol):
    """Protocol for objects that can be owned by a player."""
    @property
    def owner_id(self) -> Optional[int]:
        """Player ID of owner, None for unowned/neutral entities."""
        ...


# =============================================================================
# Strategy Entity Protocols
# =============================================================================

@runtime_checkable
class IStarSystem(Protocol):
    """Protocol for StarSystem entities."""
    @property
    def stars(self) -> List[Any]:
        ...

    @property
    def planets(self) -> List[Any]:
        ...

    @property
    def warp_points(self) -> List[Any]:
        ...

    @property
    def global_location(self) -> Any:
        """HexCoord of system on galaxy map."""
        ...

    @property
    def name(self) -> str:
        ...


@runtime_checkable
class IStar(Protocol):
    """Protocol for Star entities."""
    @property
    def color(self) -> Tuple[int, int, int]:
        ...

    @property
    def mass(self) -> float:
        ...

    @property
    def temperature(self) -> float:
        ...

    @property
    def luminosity(self) -> float:
        ...

    @property
    def star_type(self) -> Any:
        """StarType enum."""
        ...

    @property
    def name(self) -> str:
        ...


@runtime_checkable
class IPlanet(Protocol):
    """Protocol for Planet entities."""
    @property
    def planet_type(self) -> Any:
        """PlanetType enum."""
        ...

    @property
    def resources(self) -> Dict[str, Any]:
        ...

    @property
    def owner_id(self) -> Optional[int]:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def location(self) -> Any:
        """HexCoord (local to system)."""
        ...


@runtime_checkable
class IFleet(Protocol):
    """Protocol for Fleet entities."""
    @property
    def ships(self) -> List[Any]:
        ...

    @property
    def orders(self) -> List[Any]:
        ...

    @property
    def location(self) -> Any:
        """HexCoord (global on galaxy map)."""
        ...

    @property
    def owner_id(self) -> int:
        ...

    @property
    def id(self) -> int:
        ...


@runtime_checkable
class IWarpPoint(Protocol):
    """Protocol for WarpPoint entities."""
    @property
    def destination_id(self) -> str:
        ...

    @property
    def location(self) -> Any:
        """HexCoord (local to system)."""
        ...


@runtime_checkable
class ISectorEnvironment(Protocol):
    """Protocol for SectorEnvironment entities."""
    @property
    def local_hex(self) -> Any:
        """HexCoord within the system."""
        ...

    @property
    def system(self) -> Any:
        """Reference to the StarSystem."""
        ...

    def calculate_radiation(self) -> Any:
        """Calculate radiation at this sector."""
        ...


# =============================================================================
# Combat Entity Protocols
# =============================================================================

@runtime_checkable
class ICombatant(Protocol):
    """Protocol for combat-capable entities with team affiliation."""
    @property
    def team_id(self) -> int:
        ...

    @property
    def is_alive(self) -> bool:
        """True if entity can participate in combat (not destroyed/derelict)."""
        ...

    @property
    def position(self) -> Any:
        """Vector2 or similar position type."""
        ...


@runtime_checkable
class IDamageable(Protocol):
    """Protocol for entities that can take damage."""
    @property
    def current_hp(self) -> float:
        ...

    @property
    def max_hp(self) -> float:
        ...

    @property
    def is_derelict(self) -> bool:
        """True if destroyed but still present on battlefield (hulk/wreckage)."""
        ...


# =============================================================================
# TypeGuard Functions
# =============================================================================

def is_star_system(obj: Any) -> TypeGuard[IStarSystem]:
    """Check if obj satisfies the IStarSystem Protocol."""
    return isinstance(obj, IStarSystem)


def is_star(obj: Any) -> TypeGuard[IStar]:
    """Check if obj satisfies the IStar Protocol."""
    return isinstance(obj, IStar)


def is_planet(obj: Any) -> TypeGuard[IPlanet]:
    """Check if obj satisfies the IPlanet Protocol."""
    return isinstance(obj, IPlanet)


def is_fleet(obj: Any) -> TypeGuard[IFleet]:
    """Check if obj satisfies the IFleet Protocol."""
    return isinstance(obj, IFleet)


def is_warp_point(obj: Any) -> TypeGuard[IWarpPoint]:
    """Check if obj satisfies the IWarpPoint Protocol."""
    return isinstance(obj, IWarpPoint)


def is_sector_environment(obj: Any) -> TypeGuard[ISectorEnvironment]:
    """Check if obj satisfies the ISectorEnvironment Protocol."""
    return isinstance(obj, ISectorEnvironment)


def is_combatant(obj: Any) -> TypeGuard[ICombatant]:
    """Check if obj satisfies the ICombatant Protocol."""
    return isinstance(obj, ICombatant)
