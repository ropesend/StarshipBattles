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

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.strategy.data.empire import Empire


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
            for comp in layer_data.get('components', []):
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

        Uses ShipStatsService to calculate stats dynamically rather than
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
            from game.strategy.services.ship_stats_service import ShipStatsService
            # PROJ-42: Use instance pattern (no more static calling)
            service = ShipStatsService()
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
        if resource_name not in self.resource_levels:
            return 1.0  # Full by default

        current = self.resource_levels[resource_name]
        max_key = f'max_{resource_name}'
        max_val = self.get_calculated_stats().get(max_key, 100)

        if max_val <= 0:
            return 0.0
        return current / max_val

    def get_fuel_cost_per_hex(self) -> float:
        """
        Get strategic fuel consumption per hex, accounting for component damage.

        Returns:
            Fuel consumed per hex of strategic movement, or 0 if no consumption.
        """
        stats = self.get_calculated_stats()
        return stats.get('resource_consumption_per_hex', {}).get('fuel', 0)

    def get_current_fuel(self) -> float:
        """
        Get current fuel level.

        Returns:
            Current fuel amount. Returns max_fuel if not tracked (assumed full).
        """
        stats = self.get_calculated_stats()
        max_fuel = stats.get('resource_storage', {}).get('fuel', 0)
        return self.resource_levels.get('fuel', max_fuel)

    def consume_fuel(self, amount: float) -> bool:
        """
        Consume fuel from this ship.

        Args:
            amount: Fuel to consume

        Returns:
            True if fuel was available and consumed, False if insufficient
        """
        stats = self.get_calculated_stats()
        max_fuel = stats.get('resource_storage', {}).get('fuel', 0)
        current = self.resource_levels.get('fuel', max_fuel)

        if current < amount:
            return False

        new_level = current - amount
        self.resource_levels['fuel'] = new_level
        return True

    def get_warp_energy_cost(self) -> float:
        """
        Get energy cost per warp jump, accounting for component damage.

        Returns:
            Energy consumed per warp jump, or 0 if no energy cost.
        """
        stats = self.get_calculated_stats()
        return stats.get('warp_resource_costs', {}).get('energy', 0)

    def get_warp_fuel_cost(self) -> float:
        """
        Get fuel cost per warp jump, accounting for component damage.

        Returns:
            Fuel consumed per warp jump, or 0 if no fuel cost.
        """
        stats = self.get_calculated_stats()
        return stats.get('warp_resource_costs', {}).get('fuel', 0)

    def get_current_energy(self) -> float:
        """
        Get current energy level.

        Returns:
            Current energy amount. Returns max_energy if not tracked (assumed full).
        """
        stats = self.get_calculated_stats()
        max_energy = stats.get('resource_storage', {}).get('energy', 0)
        return self.resource_levels.get('energy', max_energy)

    def consume_energy(self, amount: float) -> bool:
        """
        Consume energy from this ship.

        Args:
            amount: Energy to consume

        Returns:
            True if energy was available and consumed, False if insufficient
        """
        stats = self.get_calculated_stats()
        max_energy = stats.get('resource_storage', {}).get('energy', 0)
        current = self.resource_levels.get('energy', max_energy)

        if current < amount:
            return False

        new_level = current - amount
        self.resource_levels['energy'] = new_level
        return True

    # --- Generic Resource Methods ---

    def get_resource_capacity(self, resource_type: str) -> float:
        """
        Get maximum capacity for any resource type.

        Args:
            resource_type: Resource type (e.g., 'fuel', 'energy', 'ammo')

        Returns:
            Maximum capacity for the resource, or 0 if not available.
        """
        stats = self.get_calculated_stats()
        resource_storage = stats.get('resource_storage', {})
        return resource_storage.get(resource_type, 0)

    def get_current_resource(self, resource_type: str) -> float:
        """
        Get current level of any resource type.

        Args:
            resource_type: Resource type (e.g., 'fuel', 'energy', 'ammo')

        Returns:
            Current resource level. Returns max capacity if not tracked (assumed full).
        """
        max_val = self.get_resource_capacity(resource_type)
        return self.resource_levels.get(resource_type, max_val)

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
        # Reject negative amounts - cannot "consume" a negative amount
        if amount < 0:
            return False

        max_val = self.get_resource_capacity(resource_type)
        current = self.resource_levels.get(resource_type, max_val)

        if current < amount:
            return False

        self.resource_levels[resource_type] = current - amount
        return True

    def get_all_resource_costs_per_hex(self) -> Dict[str, float]:
        """
        Get all per-hex consumption costs.

        Returns:
            Dict mapping resource type to cost per hex of movement.
        """
        stats = self.get_calculated_stats()
        return stats.get('resource_consumption_per_hex', {})

    def get_all_resource_costs_per_turn(self) -> Dict[str, float]:
        """
        Get all per-turn consumption costs.

        Returns:
            Dict mapping resource type to cost per turn.
        """
        stats = self.get_calculated_stats()
        return stats.get('resource_consumption_per_turn', {})

    def get_warp_resource_costs(self) -> Dict[str, float]:
        """
        Get all resource costs for a warp jump.

        Returns:
            Dict mapping resource type to cost per warp jump.
        """
        stats = self.get_calculated_stats()
        return stats.get('warp_resource_costs', {})

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
        """
        Get human-readable display ID in format "DesignName-000001".

        Returns:
            Display ID string if serial is set, None otherwise.
        """
        if self.serial is None:
            return None
        # Use design name from design_data for display
        design_name = self.design_data.get('name', self.design_id)
        return f"{design_name}-{self.serial:06d}"

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
        """
        Get human-readable status text.

        Returns:
            One of: "OK", "DAMAGED", "DERELICT", "DESTROYED"
        """
        if self.is_destroyed:
            return "DESTROYED"
        elif self.is_derelict:
            return "DERELICT"
        elif self.is_damaged():
            return "DAMAGED"
        else:
            return "OK"

    def get_hp_display(self) -> str:
        """
        Get HP as display string "current/max".

        Returns:
            HP display string like "150/200"
        """
        max_hp = self.get_calculated_stats().get('max_hp', 100)

        if self.current_hp is None:
            return f"{max_hp}/{max_hp}"
        else:
            return f"{self.current_hp}/{max_hp}"

    def get_resource_display(self, resource_name: str) -> str:
        """
        Get resource as display string "current/max".

        Args:
            resource_name: Name of resource (fuel, energy, ammo)

        Returns:
            Resource display string like "250/500", or "N/A" if not tracked
        """
        stats = self.get_calculated_stats()
        resource_storage = stats.get('resource_storage', {})
        max_val = resource_storage.get(resource_name)

        if max_val is None or max_val <= 0:
            return "N/A"

        if resource_name in self.resource_levels:
            current = int(self.resource_levels[resource_name])
        else:
            current = int(max_val)  # Full if not tracked

        return f"{current}/{int(max_val)}"

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

    def to_ship(self, position: Tuple[float, float], team_id: int) -> 'Ship':
        """
        Create a simulation Ship from this instance.

        Applies any existing damage/resource state from strategy layer.

        Args:
            position: (x, y) spawn position for the ship
            team_id: Team assignment for battle (0 or 1)
        """
        # INTENTIONAL LATE IMPORT: Cross-layer boundary (strategy -> simulation)
        # See docs/ARCHITECTURE.md "Intentional Late Imports" section
        from game.simulation.entities.ship_serialization import ShipSerializer
        # log_debug imported at module level

        # Create ship from design data
        ship = ShipSerializer.from_dict(self.design_data)

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
                ship.take_damage(damage)

        # Apply component-specific damage
        for comp_id, target_hp in self.component_damage.items():
            for layer_type, layer_data in ship.layers.items():
                for comp in layer_data.get('components', []):
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
            for comp in layer_data.get('components', []):
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
        if resource_name not in self.resource_levels:
            return 0  # Already at full

        max_key = f'max_{resource_name}'
        max_val = self.get_calculated_stats().get(max_key, 100)

        old_val = self.resource_levels[resource_name]
        new_val = min(max_val, old_val + amount)

        # If fully resupplied, remove from tracking
        if new_val >= max_val:
            del self.resource_levels[resource_name]
            return max_val - old_val
        else:
            self.resource_levels[resource_name] = new_val
            return new_val - old_val

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save game."""
        return {
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
