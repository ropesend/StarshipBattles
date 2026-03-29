"""
Protocol definitions for type-safe duck typing replacement.

This module provides @runtime_checkable Protocol classes and TypeGuard
functions to replace hasattr/getattr patterns with proper type checking.

Usage:
    from game.core.protocols import is_fleet, is_planet, is_scene, IFleet, IScene

    if is_fleet(obj):
        # obj is now typed as IFleet
        print(obj.ships)
    elif is_planet(obj):
        # obj is now typed as IPlanet
        print(obj.name)
    elif is_scene(obj):
        # obj is now typed as IScene
        obj.handle_event(event)
"""

from typing import (
    Protocol,
    runtime_checkable,
    Optional,
    List,
    Tuple,
    Dict,
    Any,
    FrozenSet,
    TYPE_CHECKING,
    TypeGuard,
)

from game.core.constants import LayerType

if TYPE_CHECKING:
    from game.core.hex_math import HexCoord
    # Note: LayerData not imported - protocols use Any for cross-layer types


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

    def get_resources(self) -> Dict[str, Any]:
        """Get the resources registry dictionary."""
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

    @property
    def storms(self) -> List[Any]:
        """List of Storm objects in this system."""
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

    # PROJ-193: Extended properties for UI data binding
    @property
    def id(self) -> int:
        """Unique planet ID assigned by Galaxy registry."""
        ...

    @property
    def populations(self) -> List[Any]:
        """List of SpeciesPopulation objects."""
        ...

    @property
    def max_population(self) -> int:
        """Maximum population capacity based on surface area."""
        ...

    @property
    def facilities(self) -> List[Any]:
        """List of PlanetaryFacility objects."""
        ...

    @property
    def atmosphere(self) -> Dict[str, float]:
        """Atmosphere composition: gas name -> partial pressure (Pa)."""
        ...

    @property
    def surface_gravity(self) -> float:
        """Surface gravity in m/s^2."""
        ...

    @property
    def surface_temperature(self) -> float:
        """Surface temperature in Kelvin."""
        ...

    @property
    def orbit_distance(self) -> int:
        """Orbit ring number from system center."""
        ...

    @property
    def radius_hexes(self) -> int:
        """Radius in hexes for multi-hex objects (0 for normal planets)."""
        ...

    @property
    def image_id(self) -> str:
        """Filename for planet image."""
        ...

    @property
    def image_rotation(self) -> float:
        """Rotation angle in degrees (0.0 to 360.0) for visual variety."""
        ...

    # PROJ-237: Energy and shield properties
    @property
    def energy(self) -> float:
        """Current stored energy level."""
        ...

    @property
    def energy_capacity(self) -> float:
        """Maximum energy storage capacity."""
        ...

    @property
    def shield_active(self) -> bool:
        """Whether planetary shield is currently active."""
        ...


@runtime_checkable
class IZoneOccupant(Protocol):
    """
    Protocol for entities that occupy multiple hexes (PROJ-139).

    Zone occupants are game objects that span multiple hexes on the galaxy map.
    Examples include:
    - Stars (based on radius_hexes)
    - Dyson Spheres (multi-hex planets)
    - Future: nebulae, asteroid fields

    The occupied_hexes property returns LOCAL coordinates relative to the
    object's system. The Galaxy zone registry converts these to global
    coordinates for spatial lookups.
    """
    @property
    def occupied_hexes(self) -> FrozenSet:
        """
        Set of LOCAL hex coords this object occupies.

        Returns:
            FrozenSet of HexCoord in LOCAL system coordinates
        """
        ...


@runtime_checkable
class IFleet(Protocol):
    """Protocol for Fleet entities.

    PROJ-210: Delegate properties (capabilities, resources, battle) expose
    the underlying delegate objects directly. Callers use:
    - fleet.capabilities.has_space_shipyard
    - fleet.resources.get_fleet_cargo_capacity(cargo_type)
    - fleet.battle.to_battle_ships(team_id)
    """
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

    # PROJ-193: Extended properties for UI data binding
    @property
    def speed(self) -> float:
        """Fleet movement speed (limited by slowest ship)."""
        ...

    @property
    def path(self) -> List[Any]:
        """Current movement path (list of HexCoord)."""
        ...

    @property
    def construction_queue(self) -> List[Any]:
        """Production queue for fleets with shipyards."""
        ...

    @property
    def name(self) -> str:
        """Display name for the fleet."""
        ...

    @property
    def is_building(self) -> bool:
        """True if fleet is currently executing a BUILD order."""
        ...

    # PROJ-210: Delegate properties for capability/resource/battle queries
    @property
    def capabilities(self) -> Any:
        """FleetCapabilityCalculator delegate for fleet capabilities."""
        ...

    @property
    def resources(self) -> Any:
        """FleetResourceAggregator delegate for resource operations."""
        ...

    @property
    def battle(self) -> Any:
        """FleetBattleAdapter delegate for battle conversion."""
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


@runtime_checkable
class IStorm(Protocol):
    """Protocol for Storm entities (PROJ-189)."""
    @property
    def name(self) -> str:
        """Storm display name."""
        ...

    @property
    def storm_type(self) -> str:
        """Storm type ID (e.g., 'ion_storm')."""
        ...

    @property
    def effects(self) -> Any:
        """StormEffect with multipliers and rates."""
        ...

    @property
    def occupied_hexes(self) -> FrozenSet:
        """Hexes occupied by this storm (local coordinates)."""
        ...


# =============================================================================
# Strategy Domain Protocols (PROJ-193)
# =============================================================================

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
    def resource_levels(self) -> Dict[str, float]:
        """Resource levels stored in this facility."""
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


@runtime_checkable
class ICombatShip(Protocol):
    """
    Protocol for simulation Ship entities in combat (PROJ-193).

    NOTE: Do NOT add crew_onboard, crew_required, shots_fired, shots_hit —
    these are dynamically injected by battle tracking systems.
    """
    @property
    def name(self) -> str:
        """Ship name."""
        ...

    @property
    def team_id(self) -> int:
        """Team identifier."""
        ...

    @property
    def is_alive(self) -> bool:
        """True if ship can participate in combat."""
        ...

    @property
    def is_derelict(self) -> bool:
        """True if destroyed but still present on battlefield."""
        ...

    @property
    def hp(self) -> int:
        """Current hull points."""
        ...

    @property
    def max_hp(self) -> int:
        """Maximum hull points."""
        ...

    @property
    def position(self) -> Any:
        """Vector2 position."""
        ...

    @property
    def layers(self) -> Dict[Any, Any]:
        """Ship layers containing components."""
        ...

    @property
    def resources(self) -> Optional[Any]:
        """Resource registry (None for ships without consumables)."""
        ...

    @property
    def current_target(self) -> Optional[Any]:
        """Current combat target."""
        ...

    @property
    def secondary_targets(self) -> List[Any]:
        """List of secondary combat targets."""
        ...

    @property
    def max_targets(self) -> int:
        """Maximum number of targets this ship can engage."""
        ...

    @property
    def total_defense_score(self) -> float:
        """Total defensive score for to-hit calculations."""
        ...

    def get_total_sensor_score(self) -> float:
        """Calculate total targeting/sensor score."""
        ...


# =============================================================================
# TypeGuard Functions (Duck Typing Implementation)
# =============================================================================
#
# These functions use duck typing (hasattr checks) instead of isinstance()
# with @runtime_checkable Protocols. This approach:
#
# 1. Works with test mocks (MagicMock, Mock) without needing full protocol compliance
# 2. Checks only the defining attributes that distinguish each entity type
# 3. Still provides TypeGuard narrowing for static type checkers
# 4. Is consistent with Python's duck typing philosophy
#
# Pattern: Check for the minimal set of attributes that uniquely identify the type.
# =============================================================================


def _has_attrs(obj: Any, *attrs: str) -> bool:
    """Check if obj has all specified attributes (duck typing helper)."""
    return all(hasattr(obj, attr) for attr in attrs)


def is_star_system(obj: Any) -> TypeGuard[IStarSystem]:
    """Check if obj has star system attributes (stars, planets, warp_points)."""
    return _has_attrs(obj, 'stars', 'planets', 'warp_points')


def is_star(obj: Any) -> TypeGuard[IStar]:
    """Check if obj has star attributes (star_type, color, mass)."""
    return _has_attrs(obj, 'star_type', 'color', 'mass')


def is_planet(obj: Any) -> TypeGuard[IPlanet]:
    """Check if obj has planet attributes (planet_type)."""
    return _has_attrs(obj, 'planet_type')


def is_fleet(obj: Any) -> TypeGuard[IFleet]:
    """Check if obj has fleet attributes (ships, orders)."""
    return _has_attrs(obj, 'ships', 'orders')


def is_warp_point(obj: Any) -> TypeGuard[IWarpPoint]:
    """Check if obj has warp point attributes (destination_id)."""
    return _has_attrs(obj, 'destination_id')


def is_sector_environment(obj: Any) -> TypeGuard[ISectorEnvironment]:
    """Check if obj has sector environment attributes (local_hex, system)."""
    return _has_attrs(obj, 'local_hex', 'system')


def is_storm(obj: Any) -> TypeGuard[IStorm]:
    """Check if obj has storm attributes (storm_type, effects)."""
    return _has_attrs(obj, 'storm_type', 'effects')


def is_zone_occupant(obj: Any) -> TypeGuard[IZoneOccupant]:
    """Check if obj has zone occupant attributes (occupied_hexes)."""
    return _has_attrs(obj, 'occupied_hexes')


def is_combatant(obj: Any) -> TypeGuard[ICombatant]:
    """Check if obj has combatant attributes (team_id, is_alive)."""
    return _has_attrs(obj, 'team_id', 'is_alive')


def is_empire(obj: Any) -> TypeGuard[IEmpire]:
    """Check if obj has empire attributes (id, fleets)."""
    return _has_attrs(obj, 'id', 'fleets')


def is_facility(obj: Any) -> TypeGuard[IFacility]:
    """Check if obj has facility attributes (instance_id, design_id)."""
    return _has_attrs(obj, 'instance_id', 'design_id')


def is_ship_instance(obj: Any) -> TypeGuard[IShipInstance]:
    """Check if obj has ship instance attributes (design_id, design_data)."""
    return _has_attrs(obj, 'design_id', 'design_data')


def is_combat_ship(obj: Any) -> TypeGuard[ICombatShip]:
    """Check if obj has combat ship attributes (team_id, hp, is_derelict)."""
    return _has_attrs(obj, 'team_id', 'hp', 'is_derelict')


# =============================================================================
# Scene Protocol (PROJ-65)
# =============================================================================

@runtime_checkable
class IScene(Protocol):
    """
    Protocol for game scenes (PROJ-65).

    Scenes are the main UI states (menu, battle, workshop, etc.) that
    handle events, update logic, and render to the screen.
    """
    def handle_event(self, event: Any) -> None:
        """Handle a pygame event."""
        ...

    def update(self, dt: float) -> None:
        """Update scene logic. dt is time since last frame in seconds."""
        ...

    def draw(self, screen: Any) -> None:
        """Draw the scene to the screen surface."""
        ...

    def handle_resize(self, width: int, height: int) -> None:
        """Handle window resize to new dimensions."""
        ...



# =============================================================================
# Strategy-Simulation Boundary Protocols (PROJ-90)
# =============================================================================

@runtime_checkable
class IResourceReader(Protocol):
    """
    Read-only interface for resource values.

    Used to access resource state without depending on concrete ResourceRegistry.
    """
    def get_value(self, name: str) -> float:
        """Get current value of a resource."""
        ...

    def get_max_value(self, name: str) -> float:
        """Get maximum value of a resource."""
        ...

    def get_resource_names(self) -> List[str]:
        """Return list of all registered resource names."""
        ...


@runtime_checkable
class IPostBattleShip(Protocol):
    """
    Minimal interface for reading post-battle ship state.

    Used by ShipInstance.update_from_ship() and Fleet.update_from_battle_results()
    to extract results without depending on the concrete Ship class.
    Defines the Strategy <-> Simulation boundary for post-battle state transfer.
    """
    @property
    def name(self) -> str:
        """Ship name for identification."""
        ...

    @property
    def hp(self) -> int:
        """Current hull points."""
        ...

    @property
    def max_hp(self) -> int:
        """Maximum hull points."""
        ...

    @property
    def is_alive(self) -> bool:
        """True if ship is still operational (not destroyed)."""
        ...

    @property
    def is_derelict(self) -> bool:
        """True if ship is a derelict hulk."""
        ...

    @property
    def layers(self) -> Dict['LayerType', Any]:
        """Ship layers containing components (LayerData instances)."""
        ...

    @property
    def resources(self) -> Optional['IResourceReader']:
        """Resource registry (None for ships without consumables)."""
        ...


def is_post_battle_ship(obj: Any) -> TypeGuard[IPostBattleShip]:
    """Check if obj has post-battle ship attributes (hp, max_hp, is_alive)."""
    return _has_attrs(obj, 'hp', 'max_hp', 'is_alive')


def is_resource_reader(obj: Any) -> TypeGuard[IResourceReader]:
    """Check if obj has resource reader methods (get_value, get_max_value)."""
    return _has_attrs(obj, 'get_value', 'get_max_value')


@runtime_checkable
class IResourceHolder(Protocol):
    """Protocol for objects that hold resources accessible via ResourceRegistry.

    Used by ShipInstance bridge methods (to_ship, update_from_ship)
    to access Ship resource state without hasattr checks.
    """
    @property
    def resources(self) -> Any: ...  # ResourceRegistry (typed as Any to avoid cross-layer import)

    @property
    def hp(self) -> int: ...

    @property
    def max_hp(self) -> int: ...

    @property
    def is_alive(self) -> bool: ...

    @property
    def is_derelict(self) -> bool: ...

    @property
    def layers(self) -> Dict['LayerType', Any]: ...


def is_resource_holder(obj: Any) -> TypeGuard[IResourceHolder]:
    """Check if obj has resource holder attributes (resources, hp, max_hp)."""
    return _has_attrs(obj, 'resources', 'hp', 'max_hp')


# =============================================================================
# Camera Protocol (PROJ-106)
# =============================================================================

@runtime_checkable
class ICamera(Protocol):
    """
    Protocol for camera/viewport abstraction (PROJ-106).

    Enables the research layer to depend on a camera interface without
    importing the concrete Camera class from game.ui.renderer.

    The camera handles:
    - Coordinate transformations between world and screen space
    - Viewport dimensions
    - Zoom level for scaling
    """
    @property
    def width(self) -> int:
        """Viewport width in pixels."""
        ...

    @property
    def height(self) -> int:
        """Viewport height in pixels."""
        ...

    @property
    def zoom(self) -> float:
        """Current zoom level (1.0 = 100%)."""
        ...

    @property
    def position(self) -> Any:
        """Camera world position (center of viewport). Returns Vector2-like object."""
        ...

    def world_to_screen(self, world_pos: Any) -> Any:
        """
        Convert world coordinates to screen coordinates.

        Args:
            world_pos: Position in world space (tuple or Vector2-like)

        Returns:
            Position in screen space (Vector2-like)
        """
        ...

    def screen_to_world(self, screen_pos: Any) -> Any:
        """
        Convert screen coordinates to world coordinates.

        Args:
            screen_pos: Position in screen space (tuple or Vector2-like)

        Returns:
            Position in world space (Vector2-like)
        """
        ...

    def update(self, dt: float) -> None:
        """
        Update camera state (smooth zoom, target following, etc).

        Args:
            dt: Delta time in seconds
        """
        ...

    def update_input(self, dt: float, events: list) -> None:
        """
        Process input events for camera control.

        Args:
            dt: Delta time in seconds
            events: List of input events
        """
        ...


def is_camera(obj: Any) -> TypeGuard[ICamera]:
    """Check if obj has camera attributes (width, height, zoom, world_to_screen)."""
    return _has_attrs(obj, 'width', 'height', 'zoom', 'world_to_screen')


# =============================================================================
# Serializable Protocol (PROJ-228)
# =============================================================================

@runtime_checkable
class ISerializable(Protocol):
    """
    Protocol for objects that can be serialized to/from dictionaries.

    Used by battle state dataclasses (ComponentState, ShipState,
    ProjectileState, BattleState, BattleResults) for persistence
    and JSON serialization.

    This is a type-checking-only protocol. Do NOT create a mixin —
    each implementor provides its own to_dict/from_dict with
    domain-specific serialization logic.
    """

    def to_dict(self) -> Dict[str, Any]:
        """Serialize this object to a dictionary."""
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ISerializable':
        """Deserialize an instance from a dictionary."""
        ...
