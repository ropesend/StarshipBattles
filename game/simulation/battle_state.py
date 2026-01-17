"""
BattleState - Complete serialization of battle state for save/load and strategy integration.

Provides full state capture for:
- Mid-battle save/load
- Strategy layer battle resolution
- Deterministic replay support
- Debugging and analysis
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING
from datetime import datetime
import json
import uuid

from game.simulation.components.component import LayerType
from game.core.logger import log_debug, log_warning

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.systems.battle_engine import BattleEngine
    from game.simulation.entities.projectile import Projectile


@dataclass
class ComponentState:
    """Serializable state for a single component."""
    component_id: str
    current_hp: int
    max_hp: int
    is_active: bool
    layer: str  # LayerType name

    # Modifiers applied to this component
    modifiers: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'component_id': self.component_id,
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'is_active': self.is_active,
            'layer': self.layer,
            'modifiers': self.modifiers,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentState':
        return cls(
            component_id=data['component_id'],
            current_hp=data['current_hp'],
            max_hp=data['max_hp'],
            is_active=data['is_active'],
            layer=data['layer'],
            modifiers=data.get('modifiers', []),
        )

    @classmethod
    def from_component(cls, component: 'Any') -> 'ComponentState':
        """Create ComponentState from a live Component object."""
        modifiers = []
        for mod in getattr(component, 'modifiers', []):
            modifiers.append({
                'id': mod.definition.id,
                'value': mod.value
            })

        return cls(
            component_id=component.id,
            current_hp=component.current_hp,
            max_hp=component.max_hp,
            is_active=component.is_active,
            layer=component.layer_assigned.name if component.layer_assigned else 'UNKNOWN',
            modifiers=modifiers,
        )


@dataclass
class ShipState:
    """Complete serializable state for a ship."""
    ship_id: str  # Unique ID for this battle instance
    name: str
    ship_class: str
    theme_id: str
    team_id: int
    color: Tuple[int, int, int]
    ai_strategy: str

    # Position and physics
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    angle: float

    # Health state
    current_hp: int
    max_hp: int
    current_shields: float
    max_shields: float

    # Component states (keyed by layer, then list of components)
    components: Dict[str, List[ComponentState]] = field(default_factory=dict)

    # Resource levels
    resource_levels: Dict[str, float] = field(default_factory=dict)
    resource_max: Dict[str, float] = field(default_factory=dict)

    # Status flags
    is_alive: bool = True
    is_derelict: bool = False
    retreat_status: Optional[str] = None  # None, "retreating", "escaped"

    # AI state (for resume)
    current_target_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'ship_id': self.ship_id,
            'name': self.name,
            'ship_class': self.ship_class,
            'theme_id': self.theme_id,
            'team_id': self.team_id,
            'color': list(self.color),
            'ai_strategy': self.ai_strategy,
            'position': list(self.position),
            'velocity': list(self.velocity),
            'angle': self.angle,
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'current_shields': self.current_shields,
            'max_shields': self.max_shields,
            'components': {
                layer: [c.to_dict() for c in comps]
                for layer, comps in self.components.items()
            },
            'resource_levels': self.resource_levels,
            'resource_max': self.resource_max,
            'is_alive': self.is_alive,
            'is_derelict': self.is_derelict,
            'retreat_status': self.retreat_status,
            'current_target_id': self.current_target_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShipState':
        components = {}
        for layer, comps in data.get('components', {}).items():
            components[layer] = [ComponentState.from_dict(c) for c in comps]

        return cls(
            ship_id=data['ship_id'],
            name=data['name'],
            ship_class=data['ship_class'],
            theme_id=data['theme_id'],
            team_id=data['team_id'],
            color=tuple(data['color']),
            ai_strategy=data['ai_strategy'],
            position=tuple(data['position']),
            velocity=tuple(data['velocity']),
            angle=data['angle'],
            current_hp=data['current_hp'],
            max_hp=data['max_hp'],
            current_shields=data['current_shields'],
            max_shields=data['max_shields'],
            components=components,
            resource_levels=data.get('resource_levels', {}),
            resource_max=data.get('resource_max', {}),
            is_alive=data.get('is_alive', True),
            is_derelict=data.get('is_derelict', False),
            retreat_status=data.get('retreat_status'),
            current_target_id=data.get('current_target_id'),
        )

    @classmethod
    def from_ship(cls, ship: 'Ship', ship_id: Optional[str] = None) -> 'ShipState':
        """Create ShipState from a live Ship object."""
        # Generate ID if not provided
        if ship_id is None:
            ship_id = str(uuid.uuid4())

        # Capture component states by layer
        components: Dict[str, List[ComponentState]] = {}
        for layer_type, layer_data in ship.layers.items():
            layer_name = layer_type.name
            components[layer_name] = []
            for comp in layer_data.get('components', []):
                components[layer_name].append(ComponentState.from_component(comp))

        # Capture resource levels
        resource_levels = {}
        resource_max = {}
        if hasattr(ship, 'resources') and ship.resources:
            for name in ['fuel', 'energy', 'ammo']:
                resource_levels[name] = ship.resources.get_value(name)
                resource_max[name] = ship.resources.get_max_value(name)

        # Get current target ID if available
        current_target_id = None
        if hasattr(ship, 'current_target') and ship.current_target:
            # We'll resolve this by ship name for now (should use proper IDs)
            current_target_id = getattr(ship.current_target, 'name', None)

        return cls(
            ship_id=ship_id,
            name=ship.name,
            ship_class=ship.ship_class,
            theme_id=ship.theme_id,
            team_id=ship.team_id,
            color=ship.color if isinstance(ship.color, tuple) else tuple(ship.color),
            ai_strategy=getattr(ship, 'ai_strategy', 'standard_ranged'),
            position=(ship.x, ship.y),
            velocity=(ship.velocity.x, ship.velocity.y) if hasattr(ship.velocity, 'x') else (0, 0),
            angle=getattr(ship, 'angle', 0),
            current_hp=ship.hp,
            max_hp=ship.max_hp,
            current_shields=getattr(ship, 'current_shields', 0),
            max_shields=getattr(ship, 'max_shields', 0),
            components=components,
            resource_levels=resource_levels,
            resource_max=resource_max,
            is_alive=ship.is_alive,
            is_derelict=getattr(ship, 'is_derelict', False),
            retreat_status=getattr(ship, 'retreat_status', None),
            current_target_id=current_target_id,
        )

    def to_ship(self) -> 'Ship':
        """
        Create a simulation Ship from this state.

        Note: This creates a new Ship with the stored state applied.
        Component damage and resource levels are restored.
        """
        from game.simulation.entities.ship import Ship
        from game.core.registry import get_component_registry, get_modifier_registry
        import pygame

        # Create base ship
        ship = Ship(
            self.name,
            self.position[0],
            self.position[1],
            self.color,
            self.team_id,
            ship_class=self.ship_class,
            theme_id=self.theme_id
        )
        ship.ai_strategy = self.ai_strategy
        ship.angle = self.angle
        ship.velocity = pygame.math.Vector2(self.velocity[0], self.velocity[1])

        # Add components with proper state
        comp_registry = get_component_registry()
        mod_registry = get_modifier_registry()

        for layer_name, comp_states in self.components.items():
            try:
                layer_type = LayerType[layer_name]
            except KeyError:
                log_warning(f"Unknown layer type: {layer_name}")
                continue

            if layer_type not in ship.layers:
                continue

            for comp_state in comp_states:
                if comp_state.component_id in comp_registry:
                    new_comp = comp_registry[comp_state.component_id].clone()

                    # Apply modifiers
                    for mod_data in comp_state.modifiers:
                        mid = mod_data['id']
                        mval = mod_data['value']
                        if mid in mod_registry:
                            new_comp.add_modifier(mid, mval)

                    ship.add_component(new_comp, layer_type)

                    # Apply damage state AFTER adding (to override default HP)
                    new_comp.current_hp = comp_state.current_hp
                    new_comp.is_active = comp_state.is_active

        ship.recalculate_stats()

        # Restore resource levels
        if ship.resources:
            for name, value in self.resource_levels.items():
                ship.resources.set_value(name, value)

        # Restore combat state
        ship.current_shields = self.current_shields
        ship.is_alive = self.is_alive
        ship.is_derelict = self.is_derelict

        # Store retreat status if we add it to Ship
        if hasattr(ship, 'retreat_status'):
            ship.retreat_status = self.retreat_status

        return ship


@dataclass
class ProjectileState:
    """Serializable state for a projectile."""
    projectile_id: str
    owner_ship_id: Optional[str]
    team_id: int
    position: Tuple[float, float]
    velocity: Tuple[float, float]
    damage: float
    max_range: float
    endurance: float
    max_endurance: float
    projectile_type: str  # 'projectile', 'missile'

    # Missile-specific
    turn_rate: float = 0
    max_speed: float = 0
    target_ship_id: Optional[str] = None
    hp: int = 1
    max_hp: int = 1

    distance_traveled: float = 0
    is_alive: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'projectile_id': self.projectile_id,
            'owner_ship_id': self.owner_ship_id,
            'team_id': self.team_id,
            'position': list(self.position),
            'velocity': list(self.velocity),
            'damage': self.damage,
            'max_range': self.max_range,
            'endurance': self.endurance,
            'max_endurance': self.max_endurance,
            'projectile_type': self.projectile_type,
            'turn_rate': self.turn_rate,
            'max_speed': self.max_speed,
            'target_ship_id': self.target_ship_id,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'distance_traveled': self.distance_traveled,
            'is_alive': self.is_alive,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectileState':
        return cls(
            projectile_id=data['projectile_id'],
            owner_ship_id=data.get('owner_ship_id'),
            team_id=data['team_id'],
            position=tuple(data['position']),
            velocity=tuple(data['velocity']),
            damage=data['damage'],
            max_range=data['max_range'],
            endurance=data['endurance'],
            max_endurance=data['max_endurance'],
            projectile_type=data['projectile_type'],
            turn_rate=data.get('turn_rate', 0),
            max_speed=data.get('max_speed', 0),
            target_ship_id=data.get('target_ship_id'),
            hp=data.get('hp', 1),
            max_hp=data.get('max_hp', 1),
            distance_traveled=data.get('distance_traveled', 0),
            is_alive=data.get('is_alive', True),
        )

    @classmethod
    def from_projectile(cls, proj: 'Projectile', ship_id_map: Dict[int, str]) -> 'ProjectileState':
        """
        Create ProjectileState from a live Projectile object.

        Args:
            proj: The projectile to capture
            ship_id_map: Mapping from ship object id() to ship_id string
        """
        owner_ship_id = None
        if proj.owner:
            owner_ship_id = ship_id_map.get(id(proj.owner))

        target_ship_id = None
        if hasattr(proj, 'target') and proj.target:
            target_ship_id = ship_id_map.get(id(proj.target))

        # Get projectile type as string
        proj_type = proj.type
        if hasattr(proj_type, 'value'):
            proj_type = proj_type.value

        return cls(
            projectile_id=str(uuid.uuid4()),
            owner_ship_id=owner_ship_id,
            team_id=proj.team_id,
            position=(proj.position.x, proj.position.y),
            velocity=(proj.velocity.x, proj.velocity.y),
            damage=proj.damage,
            max_range=proj.max_range or 0,
            endurance=proj.endurance or 0,
            max_endurance=getattr(proj, 'max_endurance', proj.endurance or 0),
            projectile_type=str(proj_type),
            turn_rate=getattr(proj, 'turn_rate', 0),
            max_speed=getattr(proj, 'max_speed', 0),
            target_ship_id=target_ship_id,
            hp=getattr(proj, 'hp', 1),
            max_hp=getattr(proj, 'max_hp', 1),
            distance_traveled=getattr(proj, 'distance_traveled', 0),
            is_alive=proj.is_alive,
        )


@dataclass
class BattleState:
    """Complete serializable battle state."""
    version: str = "1.0"

    # Identity
    battle_id: str = ""
    seed: Optional[int] = None

    # Timing
    tick_count: int = 0
    max_ticks: Optional[int] = None

    # Ships (keyed by ship_id)
    ships: Dict[str, ShipState] = field(default_factory=dict)

    # Projectiles
    projectiles: List[ProjectileState] = field(default_factory=list)

    # Configuration
    end_mode: str = "HP_BASED"
    allow_retreat: bool = False
    allow_reinforcements: bool = False

    # Metadata
    created_at: str = ""
    mode: str = "manual"  # manual, test, strategy, hypothetical

    def to_dict(self) -> Dict[str, Any]:
        return {
            'version': self.version,
            'battle_id': self.battle_id,
            'seed': self.seed,
            'tick_count': self.tick_count,
            'max_ticks': self.max_ticks,
            'ships': {sid: s.to_dict() for sid, s in self.ships.items()},
            'projectiles': [p.to_dict() for p in self.projectiles],
            'end_mode': self.end_mode,
            'allow_retreat': self.allow_retreat,
            'allow_reinforcements': self.allow_reinforcements,
            'created_at': self.created_at,
            'mode': self.mode,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BattleState':
        ships = {}
        for sid, sdata in data.get('ships', {}).items():
            ships[sid] = ShipState.from_dict(sdata)

        projectiles = []
        for pdata in data.get('projectiles', []):
            projectiles.append(ProjectileState.from_dict(pdata))

        return cls(
            version=data.get('version', '1.0'),
            battle_id=data.get('battle_id', ''),
            seed=data.get('seed'),
            tick_count=data.get('tick_count', 0),
            max_ticks=data.get('max_ticks'),
            ships=ships,
            projectiles=projectiles,
            end_mode=data.get('end_mode', 'HP_BASED'),
            allow_retreat=data.get('allow_retreat', False),
            allow_reinforcements=data.get('allow_reinforcements', False),
            created_at=data.get('created_at', ''),
            mode=data.get('mode', 'manual'),
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'BattleState':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def capture_from_engine(
        cls,
        engine: 'BattleEngine',
        mode: str = "manual",
        seed: Optional[int] = None,
        allow_retreat: bool = False,
        allow_reinforcements: bool = False,
        battle_id: Optional[str] = None,
        ship_id_map: Optional[Dict[int, str]] = None,
    ) -> 'BattleState':
        """
        Capture complete state from a running BattleEngine.

        Args:
            engine: The battle engine to capture from
            mode: Battle mode string
            seed: Random seed used for this battle
            allow_retreat: Whether retreat is enabled
            allow_reinforcements: Whether reinforcements are enabled
            battle_id: Optional battle ID (generates new UUID if not provided)
            ship_id_map: Optional mapping of ship object id -> string id (for consistent IDs across captures)
        """
        if battle_id is None:
            battle_id = str(uuid.uuid4())

        # Build ship ID mapping (object id -> string id)
        if ship_id_map is None:
            ship_id_map = {}
        ships: Dict[str, ShipState] = {}

        for ship in engine.ships:
            # Use existing mapping or create new ID
            if id(ship) in ship_id_map:
                ship_id = ship_id_map[id(ship)]
            else:
                ship_id = str(uuid.uuid4())
                ship_id_map[id(ship)] = ship_id
            ships[ship_id] = ShipState.from_ship(ship, ship_id)

        # Capture projectiles with ship references
        projectiles = []
        for proj in engine.projectiles:
            if proj.is_alive:
                projectiles.append(ProjectileState.from_projectile(proj, ship_id_map))

        # Get end mode
        end_mode = "HP_BASED"
        if hasattr(engine, 'end_condition') and engine.end_condition:
            end_mode = engine.end_condition.mode.name

        max_ticks = None
        if hasattr(engine, 'end_condition') and engine.end_condition:
            max_ticks = engine.end_condition.max_ticks

        return cls(
            version="1.0",
            battle_id=battle_id,
            seed=seed,
            tick_count=engine.tick_counter,
            max_ticks=max_ticks,
            ships=ships,
            projectiles=projectiles,
            end_mode=end_mode,
            allow_retreat=allow_retreat,
            allow_reinforcements=allow_reinforcements,
            created_at=datetime.now().isoformat(),
            mode=mode,
        )

    def get_ships_by_team(self, team_id: int) -> List[ShipState]:
        """Get all ships for a specific team."""
        return [s for s in self.ships.values() if s.team_id == team_id]

    def get_alive_ships(self) -> List[ShipState]:
        """Get all living ships."""
        return [s for s in self.ships.values() if s.is_alive]

    def get_surviving_ships(self) -> List[ShipState]:
        """Get ships that survived (alive and not escaped)."""
        return [s for s in self.ships.values() if s.is_alive and s.retreat_status != "escaped"]

    def get_escaped_ships(self) -> List[ShipState]:
        """Get ships that escaped via retreat."""
        return [s for s in self.ships.values() if s.retreat_status == "escaped"]

    def get_destroyed_ships(self) -> List[ShipState]:
        """Get ships that were destroyed."""
        return [s for s in self.ships.values() if not s.is_alive and s.retreat_status != "escaped"]


@dataclass
class BattleResults:
    """Results of a completed battle."""
    winner: Optional[int]  # Team ID (0 or 1), -1 for draw, None if incomplete
    tick_count: int
    seed: Optional[int]

    # State snapshots
    initial_state: Optional[BattleState] = None
    final_state: Optional[BattleState] = None

    # Categorized ships (from final state)
    surviving_ships: List[ShipState] = field(default_factory=list)
    destroyed_ships: List[ShipState] = field(default_factory=list)
    escaped_ships: List[ShipState] = field(default_factory=list)
    captured_ships: List[ShipState] = field(default_factory=list)  # Future: derelicts captured by winner

    def to_dict(self) -> Dict[str, Any]:
        return {
            'winner': self.winner,
            'tick_count': self.tick_count,
            'seed': self.seed,
            'initial_state': self.initial_state.to_dict() if self.initial_state else None,
            'final_state': self.final_state.to_dict() if self.final_state else None,
            'surviving_ships': [s.to_dict() for s in self.surviving_ships],
            'destroyed_ships': [s.to_dict() for s in self.destroyed_ships],
            'escaped_ships': [s.to_dict() for s in self.escaped_ships],
            'captured_ships': [s.to_dict() for s in self.captured_ships],
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BattleResults':
        initial_state = None
        if data.get('initial_state'):
            initial_state = BattleState.from_dict(data['initial_state'])

        final_state = None
        if data.get('final_state'):
            final_state = BattleState.from_dict(data['final_state'])

        return cls(
            winner=data.get('winner'),
            tick_count=data.get('tick_count', 0),
            seed=data.get('seed'),
            initial_state=initial_state,
            final_state=final_state,
            surviving_ships=[ShipState.from_dict(s) for s in data.get('surviving_ships', [])],
            destroyed_ships=[ShipState.from_dict(s) for s in data.get('destroyed_ships', [])],
            escaped_ships=[ShipState.from_dict(s) for s in data.get('escaped_ships', [])],
            captured_ships=[ShipState.from_dict(s) for s in data.get('captured_ships', [])],
        )

    def get_team_survivors(self, team_id: int) -> List[ShipState]:
        """Get surviving ships for a specific team."""
        return [s for s in self.surviving_ships if s.team_id == team_id]

    def get_team_losses(self, team_id: int) -> List[ShipState]:
        """Get destroyed ships for a specific team."""
        return [s for s in self.destroyed_ships if s.team_id == team_id]
