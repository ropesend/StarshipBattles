"""
ShipInstance - Strategy layer representation of a ship.

Bridges between:
- Ship designs (templates from Ship Builder)
- Strategy fleet management
- Battle simulation

Each ShipInstance tracks the current state of a ship (damage, resources)
separate from its design template.

Delegates:
- ShipConsumableManager: resource tracking (fuel, energy, ammo)
- ShipCargoManager: cargo loading/unloading
- ShipDisplayFormatter: display string formatting
- ShipInstanceBridge: simulation bridge (to_ship, update_from_ship)
- ShipInstanceSerializer: serialization (to_dict, from_dict, clone)
"""
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List, TYPE_CHECKING
import uuid

from game.core.protocols import IPostBattleShip
from game.strategy.data.ship_consumable_manager import ShipConsumableManager
from game.strategy.data.ship_cargo_manager import ShipCargoManager
from game.strategy.data.ship_display_formatter import ShipDisplayFormatter
from game.strategy.data.ship_instance_bridge import ShipInstanceBridge

logger = logging.getLogger(__name__)

# Fallback if stats dict lacks max_hp (should not happen with proper DI)
_DEFAULT_MAX_HP = 100

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.core.registry import GameRegistries


@dataclass
class ShipInstance:
    """
    Represents a ship in the strategy layer.

    Bridges between:
    - Ship designs (templates from Ship Builder)
    - Strategy fleet management
    - Battle simulation
    """

    instance_id: str  # Unique across game
    design_id: str    # Reference to ship design file/name
    name: str         # Instance name (may differ from design)
    owner_id: int     # Empire that owns this ship

    # Design data (full serialized ship template)
    design_data: Dict[str, Any] = field(default_factory=dict)

    # Current state (may differ from design defaults)
    # None values mean "use design default"
    current_hp: Optional[int] = None
    component_damage: Dict[str, int] = field(default_factory=dict)  # component_id -> current_hp
    consumable_levels: Dict[str, float] = field(default_factory=dict)  # resource_name -> current
    component_toggles: Dict[str, bool] = field(default_factory=dict)  # component_id -> enabled

    # Cargo contents (cargo_type -> current amount)
    cargo_contents: Dict[str, int] = field(default_factory=dict)

    # Carried constructed items (drop pods, etc.) — full design data preserved
    carried_items: List[Dict[str, Any]] = field(default_factory=list)

    # Status
    is_alive: bool = True
    is_derelict: bool = False
    is_operational: bool = True

    # Strategy tracking
    experience: int = 0           # For future crew/veteran system
    kills: int = 0
    battles_survived: int = 0

    # Serial number - unique per design within an empire
    serial: Optional[int] = None

    # Cached calculated stats (invalidated on damage change)
    _cached_stats: Optional[Dict[str, Any]] = field(default=None, repr=False)

    # PROJ-211: Injected registries for stats calculation (no global fallback)
    _registries: Optional['GameRegistries'] = field(default=None, repr=False, init=False)

    # Delegate managers (initialized in __post_init__)
    _resource_mgr: Optional['ShipConsumableManager'] = field(default=None, repr=False, init=False)
    _cargo_mgr: Optional['ShipCargoManager'] = field(default=None, repr=False, init=False)
    _display_fmt: Optional['ShipDisplayFormatter'] = field(default=None, repr=False, init=False)
    _bridge: Optional['ShipInstanceBridge'] = field(default=None, repr=False, init=False)

    def __post_init__(self) -> None:
        """Initialize delegate managers after dataclass init."""
        self._resource_mgr = ShipConsumableManager(self)
        self._cargo_mgr = ShipCargoManager(self)
        self._display_fmt = ShipDisplayFormatter(self)
        self._bridge = ShipInstanceBridge(self)

    def set_registries(self, registries: 'GameRegistries') -> None:
        """
        Set the registries for stats calculation.

        PROJ-211: Allows setting registries after construction for objects
        created without registries (e.g., deserialization).

        Args:
            registries: GameRegistries instance for stats calculation.
        """
        self._registries = registries
        self.invalidate_stats_cache()

    # PROJ-193: Property aliases for IShipInstance Protocol compliance
    @property
    def design_name(self) -> str:
        """Design name from design_data (IShipInstance Protocol)."""
        return self.design_data.get('name', self.design_id)

    @property
    def hull_class(self) -> str:
        """Ship's hull class from design_data (IShipInstance Protocol)."""
        return self.design_data.get('ship_class', 'Unknown')

    @property
    def ship_name(self) -> str:
        """Instance name alias (IShipInstance Protocol)."""
        return self.name

    @property
    def serial_number(self) -> Optional[int]:
        """Serial number alias (IShipInstance Protocol)."""
        return self.serial

    def __hash__(self) -> int:
        return hash(self.instance_id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ShipInstance):
            return NotImplemented
        return self.instance_id == other.instance_id

    @classmethod
    def create(
        cls,
        design_data: Dict[str, Any],
        owner_id: int,
        name: Optional[str] = None,
        design_id: Optional[str] = None,
        empire: Optional['Empire'] = None,
        registries: Optional['GameRegistries'] = None,
    ) -> 'ShipInstance':
        """
        Create a new ship instance from a design.

        Args:
            design_data: Full ship design dictionary (from ShipSerializer.to_dict())
            owner_id: Empire that owns this ship
            name: Instance name (defaults to design name)
            design_id: Design identifier (defaults to design name)
            empire: Empire to get serial number from. If None, no serial will be
                    assigned and a warning will be logged. Provide empire for proper
                    tracking of ships by serial number within empire fleets.
            registries: GameRegistries for stats calculation. Required for proper
                       DI. If None, get_calculated_stats() will raise an error.

        Returns:
            New ShipInstance with unique instance_id.

        Note:
            Serial numbers are unique per design_id within an empire, allowing
            identification like "USS Enterprise (NCC-1701)". Without an empire,
            the ship will have serial=None which may affect fleet tracking.
        """
        design_name = design_data.get('name', 'Unknown Ship')
        actual_design_id = design_id or design_name

        # Get serial number from empire if provided
        serial = None
        if empire is not None:
            serial = empire.get_next_serial(actual_design_id)
        else:
            # PROJ-40/NEW-STRAT-008: Log warning when empire not provided
            logger.warning(f"ShipInstance.create() called without empire - "
                       f"serial will be None for '{actual_design_id}'")

        instance = cls(
            instance_id=str(uuid.uuid4()),
            design_id=actual_design_id,
            name=name or design_name,
            owner_id=owner_id,
            design_data=design_data,
        )
        instance.serial = serial
        instance._registries = registries

        # Initialize all resources to full capacity
        stats = instance.get_calculated_stats()
        storage = stats.get('resource_storage', {})
        instance.consumable_levels = {name: float(val) for name, val in storage.items()}

        # Initialize cargo from design data (Phase 2: colony pods as cargo)
        initial_cargo = design_data.get('cargo', {})
        for cargo_type, amount in initial_cargo.items():
            instance.cargo_contents[cargo_type] = int(amount)

        return instance

    def is_damaged(self) -> bool:
        """Check if ship has any damage."""
        return (
            self.current_hp is not None or
            bool(self.component_damage) or
            self.is_derelict
        )

    def is_combat_capable(self) -> bool:
        """Check if ship can participate in combat."""
        return self.is_alive and not self.is_derelict

    def get_calculated_stats(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get calculated stats from components, respecting damage state.

        Uses ShipStatsCalculator to calculate stats dynamically rather than
        reading from cached expected_stats. Results are cached and invalidated
        when component damage changes.

        PROJ-211: Uses _registries if set, otherwise falls back to global
        registry provider temporarily. The fallback will be removed after
        all test fixtures are updated to use DI.

        Args:
            force_refresh: If True, recalculate even if cached

        Returns:
            Dict with calculated stats (max_hp, mass, max_fuel, etc.)
        """
        if self._cached_stats is None or force_refresh:
            # INTENTIONAL LATE IMPORT: Lazy initialization pattern
            # See docs/ARCHITECTURE.md "Intentional Late Imports" section
            from game.strategy.services.ship_stats_calculator import ShipStatsCalculator

            registries = self._registries
            if registries is None:
                raise ValueError(
                    "ShipInstance requires registries for stats calculation. "
                    "Use ShipInstance.create() or from_dict() with registries parameter, "
                    "or set ship._registries after construction."
                )

            service = ShipStatsCalculator(registries=registries)
            self._cached_stats = service.calculate_stats(
                self.design_data,
                self.component_damage,
                self.component_toggles
            )
        return self._cached_stats

    def invalidate_stats_cache(self) -> None:
        """
        Invalidate cached stats.

        Call this when component damage changes, after battle,
        or after repair operations.
        """
        self._cached_stats = None

    def get_hp_percentage(self) -> float:
        """Get current HP as percentage of max."""
        if self.current_hp is None:
            return 1.0
        max_hp = self.get_calculated_stats().get('max_hp', _DEFAULT_MAX_HP)
        if max_hp <= 0:
            return 0.0
        return self.current_hp / max_hp

    def get_resource_percentage(self, resource_name: str) -> float:
        """Get current resource level as percentage of max."""
        return self._display_fmt.get_resource_percentage(resource_name)

    # --- Generic Resource Methods ---

    def get_resource_capacity(self, resource_type: str) -> float:
        """
        Get maximum capacity for any resource type.

        Args:
            resource_type: Resource type (e.g., 'fuel', 'energy', 'ammo')

        Returns:
            Maximum capacity for the resource, or 0 if not available.
        """
        return self._resource_mgr.get_resource_capacity(resource_type)

    def get_current_resource(self, resource_type: str) -> float:
        """
        Get current level of any resource type.

        Args:
            resource_type: Resource type (e.g., 'fuel', 'energy', 'ammo')

        Returns:
            Current resource level. Returns max capacity if not tracked (assumed full).
        """
        return self._resource_mgr.get_current_resource(resource_type)

    def consume_resource(self, resource_type: str, amount: float) -> bool:
        """
        Consume a specified amount of any resource type.

        Args:
            resource_type: Resource type to consume
            amount: Amount to consume (must be >= 0)

        Returns:
            True if resource was available and consumed, False if insufficient
            or if amount is negative.
        """
        return self._resource_mgr.consume_resource(resource_type, amount)

    def get_all_resource_costs_per_hex(self) -> Dict[str, float]:
        """
        Get all per-hex consumption costs.

        Returns:
            Dict mapping resource type to cost per hex of movement.
        """
        return self._resource_mgr.get_all_resource_costs_per_hex()

    def get_all_resource_costs_per_turn(self) -> Dict[str, float]:
        """
        Get all per-turn consumption costs.

        Returns:
            Dict mapping resource type to cost per turn.
        """
        return self._resource_mgr.get_all_resource_costs_per_turn()

    # --- Cargo Methods (delegated to ShipCargoManager) ---

    def get_cargo_capacity(self, cargo_type: str) -> int:
        """Get maximum cargo capacity for a specific cargo type."""
        return self._cargo_mgr.get_cargo_capacity(cargo_type)

    def get_current_cargo(self, cargo_type: str) -> int:
        """Get current amount of cargo loaded for a specific type."""
        return self._cargo_mgr.get_current_cargo(cargo_type)

    def get_cargo_space_available(self, cargo_type: str) -> int:
        """Get available space for a specific cargo type."""
        return self._cargo_mgr.get_cargo_space_available(cargo_type)

    def load_cargo(self, cargo_type: str, amount: int) -> int:
        """Load cargo onto this ship."""
        return self._cargo_mgr.load_cargo(cargo_type, amount)

    def unload_cargo(self, cargo_type: str, amount: int) -> int:
        """Unload cargo from this ship."""
        return self._cargo_mgr.unload_cargo(cargo_type, amount)

    # --- Pod Storage (mass-based carried_items capacity) ---

    def get_pod_storage_capacity(self) -> float:
        """Get maximum mass capacity for carried items (drop pods)."""
        stats = self.get_calculated_stats()
        return float(stats.get('pod_storage_mass', 0))

    def get_pod_storage_used(self) -> float:
        """Get total mass of items currently in carried_items."""
        return sum(item.get('mass', 0.0) for item in self.carried_items)

    def can_carry_pod(self, pod_mass: float) -> bool:
        """Check if this ship can carry an additional pod of the given mass."""
        capacity = self.get_pod_storage_capacity()
        if capacity <= 0:
            return False
        return self.get_pod_storage_used() + pod_mass <= capacity

    def get_warp_resource_costs(self) -> Dict[str, float]:
        """
        Get all resource costs for a warp jump.

        Returns:
            Dict mapping resource type to cost per warp jump.
        """
        return self._resource_mgr.get_warp_resource_costs()

    # --- Component Toggle Methods ---

    def set_component_enabled(self, component_id: str, enabled: bool) -> None:
        """
        Enable or disable a component manually.

        Disabled components don't contribute abilities to stats but still
        contribute their mass. Useful for conserving resources or managing
        damage states.

        Args:
            component_id: ID of the component to toggle
            enabled: True to enable, False to disable
        """
        self.component_toggles[component_id] = enabled
        self.invalidate_stats_cache()

    def is_component_enabled(self, component_id: str) -> bool:
        """
        Check if a component is enabled.

        Args:
            component_id: ID of the component to check

        Returns:
            True if component is enabled (or not in toggles dict), False if disabled.
        """
        return self.component_toggles.get(component_id, True)

    def get_display_id(self) -> Optional[str]:
        """Get human-readable display ID in format "DesignName-000001"."""
        return self._display_fmt.get_display_id()

    def get_damaged_component_count(self) -> int:
        """
        Get count of damaged components.

        Returns:
            Number of components with recorded damage.
        """
        return len(self.component_damage)

    def get_status_text(self) -> str:
        """Get human-readable status text."""
        return self._display_fmt.get_status_text()

    def get_hp_display(self) -> str:
        """Get HP as display string "current/max"."""
        return self._display_fmt.get_hp_display()

    def get_resource_display(self, resource_name: str) -> str:
        """Get resource as display string "current/max"."""
        return self._display_fmt.get_resource_display(resource_name)

    def get_components_by_layer(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get components grouped by layer from design data.

        Returns:
            Dict mapping layer name (CORE, INNER, etc.) to list of component entries.
        """
        layers = self.design_data.get('layers', {})
        return {layer_name: list(comps) for layer_name, comps in layers.items()}

    def get_damaged_components_by_layer(self) -> Dict[str, List[Tuple[str, int]]]:
        """
        Get damaged components grouped by layer.

        Matches damaged component IDs against the design's layer structure
        to determine which layer each damaged component belongs to.

        Returns:
            Dict mapping layer name to list of (component_id, current_hp) tuples
            for damaged components in that layer.
        """
        if not self.component_damage:
            return {}

        # Build lookup from component base ID to layer
        layers = self.design_data.get('layers', {})
        comp_to_layer: Dict[str, str] = {}

        for layer_name, components in layers.items():
            for i, comp_entry in enumerate(components):
                # Component IDs in damage dict are typically "base_id_index"
                comp_id = comp_entry.get('id') if isinstance(comp_entry, dict) else comp_entry
                # Map both the base ID and indexed versions
                comp_to_layer[comp_id] = layer_name
                comp_to_layer[f"{comp_id}_{i}"] = layer_name

        # Group damaged components by layer
        result: Dict[str, List[Tuple[str, int]]] = {}

        for comp_id, current_hp in self.component_damage.items():
            # Try to find layer for this component
            layer_name = comp_to_layer.get(comp_id)

            if layer_name is None:
                # Try matching by base ID (strip trailing _N)
                base_id = '_'.join(comp_id.rsplit('_', 1)[:-1]) if '_' in comp_id else comp_id
                layer_name = comp_to_layer.get(base_id, 'UNKNOWN')

            if layer_name not in result:
                result[layer_name] = []
            result[layer_name].append((comp_id, current_hp))

        return result

    def to_ship(
        self,
        position: Tuple[float, float],
        team_id: int,
        *,
        registries: 'GameRegistries'
    ) -> 'Ship':
        """
        Create a simulation Ship from this instance.

        Applies any existing damage/resource state from strategy layer.

        Args:
            position: (x, y) spawn position for the ship
            team_id: Team assignment for battle (0 or 1)
            registries: GameRegistries for DI (required).
        """
        return self._bridge.to_ship(position, team_id, registries=registries)

    def update_from_ship(self, ship: IPostBattleShip) -> None:
        """
        Update this instance from post-battle ship state.

        Called after strategy battle resolution to persist damage/resource changes.
        """
        self._bridge.update_from_ship(ship)

    def repair(self, amount: int) -> int:
        """
        Repair the ship by a certain amount.

        Returns the actual amount repaired.
        """
        if self.current_hp is None:
            return 0  # Already at full health

        max_hp = self.get_calculated_stats().get('max_hp', _DEFAULT_MAX_HP)
        old_hp = self.current_hp
        self.current_hp = min(max_hp, self.current_hp + amount)

        # If fully repaired, clear damage tracking
        if self.current_hp >= max_hp:
            self.current_hp = None
            self.component_damage.clear()

        # Invalidate stats cache (damage changed)
        self.invalidate_stats_cache()

        return self.current_hp - old_hp if self.current_hp else max_hp - old_hp

    def resupply(self, resource_name: str, amount: float) -> float:
        """
        Resupply a resource.

        Returns the actual amount resupplied.
        """
        return self._resource_mgr.resupply(resource_name, amount)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save game."""
        from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
        return ShipInstanceSerializer.to_dict(self)

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        registries: Optional['GameRegistries'] = None,
    ) -> 'ShipInstance':
        """
        Deserialize from save game.

        Args:
            data: Dict with ship instance data
            registries: GameRegistries for stats calculation. Optional during
                       deserialization but must be set before calling
                       get_calculated_stats().

        Returns:
            Reconstructed ShipInstance

        Raises:
            PersistenceException: If required keys missing or values invalid
        """
        from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
        return ShipInstanceSerializer.from_dict(data, registries=registries)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
        return ShipInstanceSerializer.to_json(self, indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> 'ShipInstance':
        """Deserialize from JSON string."""
        from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
        return ShipInstanceSerializer.from_json(json_str)

    def clone(self) -> 'ShipInstance':
        """Create a deep copy of this instance (for hypothetical battles)."""
        from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer
        return ShipInstanceSerializer.clone(self)

    def __repr__(self) -> str:
        hp_status = f"{self.current_hp}HP" if self.current_hp is not None else "Full"
        status = "DESTROYED" if not self.is_alive else ("DERELICT" if self.is_derelict else "OK")
        return f"ShipInstance({self.name}, {hp_status}, {status})"
