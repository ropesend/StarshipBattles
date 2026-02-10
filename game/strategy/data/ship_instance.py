"""
ShipInstance - Strategy layer representation of a ship.

Bridges between:
- Ship designs (templates from Ship Builder)
- Strategy fleet management
- Battle simulation

Each ShipInstance tracks the current state of a ship (damage, resources)
separate from its design template.

PROJ-40/NEW-STRAT-008: Added validation and warning for serial parameter.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List, TYPE_CHECKING
import uuid
import json

from game.core.logger import log_warning, log_debug
from game.strategy.data.ship_resource_manager import ShipResourceManager
from game.strategy.data.ship_cargo_manager import ShipCargoManager
from game.strategy.data.ship_display_formatter import ShipDisplayFormatter

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
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
    resource_levels: Dict[str, float] = field(default_factory=dict)  # resource_name -> current
    component_toggles: Dict[str, bool] = field(default_factory=dict)  # component_id -> enabled

    # Cargo contents (cargo_type -> current amount)
    cargo_contents: Dict[str, int] = field(default_factory=dict)

    # Status
    is_destroyed: bool = False
    is_derelict: bool = False

    # Strategy tracking
    experience: int = 0           # For future crew/veteran system
    kills: int = 0
    battles_survived: int = 0

    # Serial number - unique per design within an empire
    serial: Optional[int] = None

    # Cached calculated stats (invalidated on damage change)
    _cached_stats: Optional[Dict[str, Any]] = field(default=None, repr=False)

    # Delegate managers (initialized in __post_init__)
    _resource_mgr: Optional['ShipResourceManager'] = field(default=None, repr=False, init=False)
    _cargo_mgr: Optional['ShipCargoManager'] = field(default=None, repr=False, init=False)
    _display_fmt: Optional['ShipDisplayFormatter'] = field(default=None, repr=False, init=False)

    def __post_init__(self) -> None:
        """Initialize delegate managers after dataclass init."""
        self._resource_mgr = ShipResourceManager(self)
        self._cargo_mgr = ShipCargoManager(self)
        self._display_fmt = ShipDisplayFormatter(self)

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
            log_warning(f"ShipInstance.create() called without empire - "
                       f"serial will be None for '{actual_design_id}'")

        instance = cls(
            instance_id=str(uuid.uuid4()),
            design_id=actual_design_id,
            name=name or design_name,
            owner_id=owner_id,
            design_data=design_data,
        )
        instance.serial = serial
        return instance

    @classmethod
    def from_ship(cls, ship: 'Ship', owner_id: int) -> 'ShipInstance':
        """
        Create a ShipInstance from a live Ship object.

        Captures the current state of the ship including any damage.
        """
        # INTENTIONAL LATE IMPORT: Cross-layer boundary (strategy -> simulation)
        # See docs/ARCHITECTURE.md "Intentional Late Imports" section
        from game.simulation.entities.ship_serialization import ShipSerializer

        # Serialize the ship design
        design_data = ShipSerializer.to_dict(ship)

        instance = cls(
            instance_id=str(uuid.uuid4()),
            design_id=ship.name,
            name=ship.name,
            owner_id=owner_id,
            design_data=design_data,
        )

        # Capture current state if damaged
        if ship.hp < ship.max_hp:
            instance.current_hp = ship.hp

        # Capture component damage
        for layer_type, layer_data in ship.layers.items():
            for comp in layer_data.components:
                if comp.current_hp < comp.max_hp:
                    instance.component_damage[comp.id] = comp.current_hp

        # Capture resource levels
        if hasattr(ship, 'resources') and ship.resources:
            for name in ['fuel', 'energy', 'ammo']:
                current = ship.resources.get_value(name)
                max_val = ship.resources.get_max_value(name)
                if current < max_val:
                    instance.resource_levels[name] = current

        instance.is_derelict = getattr(ship, 'is_derelict', False)
        instance.is_destroyed = not ship.is_alive

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
        return not self.is_destroyed and not self.is_derelict

    def get_calculated_stats(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get calculated stats from components, respecting damage state.

        Uses ShipStatsCalculator to calculate stats dynamically rather than
        reading from cached expected_stats. Results are cached and invalidated
        when component damage changes.

        Args:
            force_refresh: If True, recalculate even if cached

        Returns:
            Dict with calculated stats (max_hp, mass, max_fuel, etc.)
        """
        if self._cached_stats is None or force_refresh:
            # INTENTIONAL LATE IMPORT: Lazy initialization pattern
            # See docs/ARCHITECTURE.md "Intentional Late Imports" section
            from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
            from game.core.registry import get_default_registries
            registries = get_default_registries()
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
        max_hp = self.get_calculated_stats().get('max_hp', 100)
        if max_hp <= 0:
            return 0.0
        return self.current_hp / max_hp

    def get_resource_percentage(self, resource_name: str) -> float:
        """Get current resource level as percentage of max."""
        return self._display_fmt.get_resource_percentage(resource_name)

    def get_fuel_cost_per_hex(self) -> float:
        """
        Get strategic fuel consumption per hex, accounting for component damage.

        Returns:
            Fuel consumed per hex of strategic movement, or 0 if no consumption.
        """
        return self._resource_mgr.get_fuel_cost_per_hex()

    def get_current_fuel(self) -> float:
        """
        Get current fuel level.

        Returns:
            Current fuel amount. Returns max_fuel if not tracked (assumed full).
        """
        return self._resource_mgr.get_current_fuel()

    def consume_fuel(self, amount: float) -> bool:
        """
        Consume fuel from this ship.

        Args:
            amount: Fuel to consume

        Returns:
            True if fuel was available and consumed, False if insufficient
        """
        return self._resource_mgr.consume_fuel(amount)

    def get_warp_energy_cost(self) -> float:
        """
        Get energy cost per warp jump, accounting for component damage.

        Returns:
            Energy consumed per warp jump, or 0 if no energy cost.
        """
        return self._resource_mgr.get_warp_energy_cost()

    def get_warp_fuel_cost(self) -> float:
        """
        Get fuel cost per warp jump, accounting for component damage.

        Returns:
            Fuel consumed per warp jump, or 0 if no fuel cost.
        """
        return self._resource_mgr.get_warp_fuel_cost()

    def get_current_energy(self) -> float:
        """
        Get current energy level.

        Returns:
            Current energy amount. Returns max_energy if not tracked (assumed full).
        """
        return self._resource_mgr.get_current_energy()

    def consume_energy(self, amount: float) -> bool:
        """
        Consume energy from this ship.

        Args:
            amount: Energy to consume

        Returns:
            True if energy was available and consumed, False if insufficient
        """
        return self._resource_mgr.consume_energy(amount)

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

    def get_component_damage_summary(self) -> Dict[str, int]:
        """
        Get summary of damaged components.

        Returns:
            Dict mapping component_id to current HP for damaged components.
        """
        return dict(self.component_damage)

    def get_damaged_component_count(self) -> int:
        """
        Get count of damaged components.

        Returns:
            Number of components with recorded damage.
        """
        return len(self.component_damage)

    def get_layer_damage_summary(self) -> Dict[str, float]:
        """
        Get damage summary grouped by layer.

        Note: Without converting to a Ship, we can't determine layer membership
        of damaged components. Returns empty dict for ShipInstance.
        Full layer info requires calling to_ship() first.

        Returns:
            Empty dict (layer info requires live Ship object).
        """
        return {}

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
        registries: Optional['GameRegistries'] = None
    ) -> 'Ship':
        """
        Create a simulation Ship from this instance.

        Applies any existing damage/resource state from strategy layer.

        Args:
            position: (x, y) spawn position for the ship
            team_id: Team assignment for battle (0 or 1)
            registries: Optional GameRegistries for DI. If None, uses global fallback
                        (transitional - will be required in Phase 6).
        """
        # INTENTIONAL LATE IMPORT: Cross-layer boundary (strategy -> simulation)
        # See docs/ARCHITECTURE.md "Intentional Late Imports" section
        from game.simulation.entities.ship_serialization import ShipSerializer
        # log_debug imported at module level

        # Create ship from design data
        ship = ShipSerializer.from_dict(self.design_data, registries=registries)

        # Set position and team
        ship.x, ship.y = position
        ship.team_id = team_id

        # Apply HP damage if tracked
        if self.current_hp is not None:
            # Calculate damage to distribute
            damage = ship.max_hp - self.current_hp
            if damage > 0:
                log_debug(f"Ship {self.name} entering battle with {damage} damage pre-applied")
                # Apply damage (this will distribute to components)
                ship.combat_engine.take_damage(damage)

        # Apply component-specific damage
        for comp_id, target_hp in self.component_damage.items():
            for layer_type, layer_data in ship.layers.items():
                for comp in layer_data.components:
                    if comp.id == comp_id:
                        # Set component to specific HP
                        damage = comp.current_hp - target_hp
                        if damage > 0:
                            comp.take_damage(damage)

        # Apply resource levels
        if ship.resources:
            for resource_name, current in self.resource_levels.items():
                ship.resources.set_value(resource_name, current)

        # Recalculate stats after applying damage
        ship.recalculate_stats()

        return ship

    def update_from_ship(self, ship: 'Ship') -> None:
        """
        Update this instance from post-battle ship state.

        Called after strategy battle resolution to persist damage/resource changes.
        """
        # Update HP state
        if ship.is_alive:
            if ship.hp < ship.max_hp:
                self.current_hp = ship.hp
            else:
                self.current_hp = None  # Full health
            self.is_destroyed = False
        else:
            self.is_destroyed = True
            self.current_hp = 0

        self.is_derelict = getattr(ship, 'is_derelict', False)

        # Update component damage
        self.component_damage.clear()
        for layer_type, layer_data in ship.layers.items():
            for comp in layer_data.components:
                if comp.current_hp < comp.max_hp:
                    self.component_damage[comp.id] = comp.current_hp

        # Update resource levels
        self.resource_levels.clear()
        if hasattr(ship, 'resources') and ship.resources:
            for name in ['fuel', 'energy', 'ammo']:
                current = ship.resources.get_value(name)
                max_val = ship.resources.get_max_value(name)
                if current < max_val:
                    self.resource_levels[name] = current

        # Update battle stats
        self.battles_survived += 1

        # Invalidate stats cache (damage changed)
        self.invalidate_stats_cache()

    def repair(self, amount: int) -> int:
        """
        Repair the ship by a certain amount.

        Returns the actual amount repaired.
        """
        if self.current_hp is None:
            return 0  # Already at full health

        max_hp = self.get_calculated_stats().get('max_hp', 100)
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
        data = {
            'instance_id': self.instance_id,
            'design_id': self.design_id,
            'name': self.name,
            'owner_id': self.owner_id,
            'design_data': self.design_data,
            'current_hp': self.current_hp,
            'component_damage': self.component_damage,
            'resource_levels': self.resource_levels,
            'component_toggles': self.component_toggles,
            'is_destroyed': self.is_destroyed,
            'is_derelict': self.is_derelict,
            'experience': self.experience,
            'kills': self.kills,
            'battles_survived': self.battles_survived,
            'serial': self.serial,
        }
        # Only include cargo_contents if non-empty
        if self.cargo_contents:
            data['cargo_contents'] = self.cargo_contents
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShipInstance':
        """Deserialize from save game."""
        return cls(
            instance_id=data['instance_id'],
            design_id=data['design_id'],
            name=data['name'],
            owner_id=data['owner_id'],
            design_data=data.get('design_data', {}),
            current_hp=data.get('current_hp'),
            component_damage=data.get('component_damage', {}),
            resource_levels=data.get('resource_levels', {}),
            component_toggles=data.get('component_toggles', {}),
            cargo_contents=data.get('cargo_contents', {}),
            is_destroyed=data.get('is_destroyed', False),
            is_derelict=data.get('is_derelict', False),
            experience=data.get('experience', 0),
            kills=data.get('kills', 0),
            battles_survived=data.get('battles_survived', 0),
            serial=data.get('serial'),
        )

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, json_str: str) -> 'ShipInstance':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def clone(self) -> 'ShipInstance':
        """Create a deep copy of this instance (for hypothetical battles)."""
        import copy
        return ShipInstance(
            instance_id=str(uuid.uuid4()),  # New ID for clone
            design_id=self.design_id,
            name=self.name,
            owner_id=self.owner_id,
            design_data=copy.deepcopy(self.design_data),
            current_hp=self.current_hp,
            component_damage=copy.deepcopy(self.component_damage),
            resource_levels=copy.deepcopy(self.resource_levels),
            component_toggles=copy.deepcopy(self.component_toggles),
            cargo_contents=copy.deepcopy(self.cargo_contents),
            is_destroyed=self.is_destroyed,
            is_derelict=self.is_derelict,
            experience=self.experience,
            kills=self.kills,
            battles_survived=self.battles_survived,
        )

    def __repr__(self) -> str:
        hp_status = f"{self.current_hp}HP" if self.current_hp is not None else "Full"
        status = "DESTROYED" if self.is_destroyed else ("DERELICT" if self.is_derelict else "OK")
        return f"ShipInstance({self.name}, {hp_status}, {status})"
