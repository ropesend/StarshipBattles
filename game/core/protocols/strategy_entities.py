"""Strategy-layer entity protocols (concrete galaxy-map objects) and TypeGuards.

These are the things that occupy a star system: stars, planets, fleets,
warp points, sector environments, storms. Domain-scoped types (empires,
facilities, races, ship instances) live in `strategy_domain.py`.
"""

from typing import Any, Dict, FrozenSet, List, Optional, Protocol, Tuple, TypeGuard, runtime_checkable

from game.core.protocols.common import _has_attrs


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
    def deposits(self) -> Dict[str, Any]:
        ...

    @property
    def stockpile(self) -> Dict[str, float]:
        """Local resource stockpile (harvested/stored resources)."""
        ...

    @property
    def max_stockpile(self) -> Dict[str, float]:
        """Maximum local stockpile capacity per resource type."""
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


@runtime_checkable
class IOrderable(Protocol):
    """Protocol for entities with an order queue (Fleet, Planet).

    PROJ-238: Unified interface for any entity that can receive orders.
    """

    @property
    def orders(self) -> List[Any]:
        """The entity's order queue."""
        ...

    def get_current_order(self) -> Optional[Any]:
        """Peek at the first order in the queue."""
        ...

    def add_order(self, order: Any, index: Optional[int] = None) -> None:
        """Add an order to the queue."""
        ...

    def pop_order(self) -> Optional[Any]:
        """Remove and return the first order."""
        ...

    def clear_orders(self) -> None:
        """Remove all orders."""
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
        """FleetConsumableAggregator delegate for resource operations."""
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


@runtime_checkable
class IAbilitySource(Protocol):
    """Protocol for any entity that contributes abilities to the unified collector (PROJ-300).

    Sources expose their abilities as a `{ability_name: ability_data | [data,...]}`
    dict matching the components.json shape. Each ability_data dict carries
    `scope` plus multiplier/rate/etc. Sources also describe where they apply via
    `affects_hex` (hex-scoped) and `affects_system` (system-scoped), and provide
    identity for UI rendering.

    Source-kind idiosyncrasies (facility activation states, owner filtering)
    live inside source-specific adapters so the collector remains uniform.
    """
    @property
    def source_kind(self) -> str:
        """Discriminator: 'facility' | 'storm' | 'planet' | 'star' | 'warp_point' | 'system' | 'fleet'."""
        ...

    @property
    def source_label(self) -> str:
        """Human-readable: 'Ion Storm Alpha', 'Geologic Stabilizer (Tarsis IV)'."""
        ...

    @property
    def source_id(self) -> str:
        """Stable unique id for dedup."""
        ...

    @property
    def owner_id(self) -> Optional[int]:
        """None = ownerless (storms; later: stars, warp points, system itself)."""
        ...

    def get_abilities(self) -> Dict[str, Any]:
        """Return abilities dict in components.json shape."""
        ...

    def affects_hex(self, hex_coord: Any) -> bool:
        """True iff this source's abilities apply at the given hex."""
        ...

    def affects_system(self, system: Any) -> bool:
        """True iff this source's abilities apply within the given star system."""
        ...

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        """None = always active. Used for activatable abilities on facilities."""
        ...


# =============================================================================
# TypeGuards
# =============================================================================


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


def is_ability_source(obj: Any) -> TypeGuard[IAbilitySource]:
    """Check if obj satisfies the IAbilitySource protocol (PROJ-300)."""
    return _has_attrs(obj, 'source_kind', 'source_label', 'get_abilities', 'affects_hex')


def is_zone_occupant(obj: Any) -> TypeGuard[IZoneOccupant]:
    """Check if obj has zone occupant attributes (occupied_hexes)."""
    return _has_attrs(obj, 'occupied_hexes')
