"""
ShipInstance - Strategy layer representation of a ship.

Bridges between:
- Ship designs (templates from Ship Builder)
- Strategy fleet management
- Battle simulation

Each ShipInstance tracks the current state of a ship (damage, resources)
separate from its design template.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List, TYPE_CHECKING
import uuid
import json

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


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

    # Status
    is_destroyed: bool = False
    is_derelict: bool = False

    # Strategy tracking
    experience: int = 0           # For future crew/veteran system
    kills: int = 0
    battles_survived: int = 0

    @classmethod
    def create(
        cls,
        design_data: Dict[str, Any],
        owner_id: int,
        name: Optional[str] = None,
        design_id: Optional[str] = None,
    ) -> 'ShipInstance':
        """
        Create a new ship instance from a design.

        Args:
            design_data: Full ship design dictionary (from ShipSerializer.to_dict())
            owner_id: Empire that owns this ship
            name: Instance name (defaults to design name)
            design_id: Design identifier (defaults to design name)
        """
        design_name = design_data.get('name', 'Unknown Ship')

        return cls(
            instance_id=str(uuid.uuid4()),
            design_id=design_id or design_name,
            name=name or design_name,
            owner_id=owner_id,
            design_data=design_data,
        )

    @classmethod
    def from_ship(cls, ship: 'Ship', owner_id: int) -> 'ShipInstance':
        """
        Create a ShipInstance from a live Ship object.

        Captures the current state of the ship including any damage.
        """
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

    def get_hp_percentage(self) -> float:
        """Get current HP as percentage of max."""
        if self.current_hp is None:
            return 1.0
        max_hp = self.design_data.get('expected_stats', {}).get('max_hp', 100)
        if max_hp <= 0:
            return 0.0
        return self.current_hp / max_hp

    def get_resource_percentage(self, resource_name: str) -> float:
        """Get current resource level as percentage of max."""
        if resource_name not in self.resource_levels:
            return 1.0  # Full by default

        current = self.resource_levels[resource_name]
        max_key = f'max_{resource_name}'
        max_val = self.design_data.get('expected_stats', {}).get(max_key, 100)

        if max_val <= 0:
            return 0.0
        return current / max_val

    def to_ship(self, position: Tuple[float, float], team_id: int) -> 'Ship':
        """
        Create a simulation Ship from this instance.

        Applies any existing damage/resource state from strategy layer.

        Args:
            position: (x, y) spawn position for the ship
            team_id: Team assignment for battle (0 or 1)
        """
        from game.simulation.entities.ship_serialization import ShipSerializer
        from game.core.logger import log_debug

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

    def repair(self, amount: int) -> int:
        """
        Repair the ship by a certain amount.

        Returns the actual amount repaired.
        """
        if self.current_hp is None:
            return 0  # Already at full health

        max_hp = self.design_data.get('expected_stats', {}).get('max_hp', 100)
        old_hp = self.current_hp
        self.current_hp = min(max_hp, self.current_hp + amount)

        # If fully repaired, clear damage tracking
        if self.current_hp >= max_hp:
            self.current_hp = None
            self.component_damage.clear()

        return self.current_hp - old_hp if self.current_hp else max_hp - old_hp

    def resupply(self, resource_name: str, amount: float) -> float:
        """
        Resupply a resource.

        Returns the actual amount resupplied.
        """
        if resource_name not in self.resource_levels:
            return 0  # Already at full

        max_key = f'max_{resource_name}'
        max_val = self.design_data.get('expected_stats', {}).get(max_key, 100)

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
            'is_destroyed': self.is_destroyed,
            'is_derelict': self.is_derelict,
            'experience': self.experience,
            'kills': self.kills,
            'battles_survived': self.battles_survived,
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
            is_destroyed=data.get('is_destroyed', False),
            is_derelict=data.get('is_derelict', False),
            experience=data.get('experience', 0),
            kills=data.get('kills', 0),
            battles_survived=data.get('battles_survived', 0),
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
        return cls(
            instance_id=str(uuid.uuid4()),  # New ID for clone
            design_id=self.design_id,
            name=self.name,
            owner_id=self.owner_id,
            design_data=copy.deepcopy(self.design_data),
            current_hp=self.current_hp,
            component_damage=copy.deepcopy(self.component_damage),
            resource_levels=copy.deepcopy(self.resource_levels),
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
