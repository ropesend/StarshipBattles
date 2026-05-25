"""
BattleState - Complete serialization of battle state for save/load and strategy integration.

Provides full state capture for:
- Mid-battle save/load
- Strategy layer battle resolution
- Deterministic replay support
- Debugging and analysis

PROJ-38: Added registries parameter for dependency injection.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING
from datetime import datetime
from enum import Enum
import json
import uuid

import logging
from game.core.constants import LayerType, AttackType
from game.core.exceptions import ValidationException, PersistenceException
from game.core.error_codes import ErrorCode

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.systems.battle_engine import BattleEngine
    from game.simulation.entities.projectile import Projectile
    from game.core.registry import GameRegistries


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
        from game.simulation.battle_state_serde import component_state_to_dict
        return component_state_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentState':
        """Deserialize ComponentState from a dictionary.

        Args:
            data: Dictionary containing component state data

        Returns:
            ComponentState instance

        Raises:
            PersistenceException: If required keys are missing or values are invalid
        """
        from game.simulation.battle_state_serde import component_state_from_dict
        return component_state_from_dict(data)

    @classmethod
    def from_component(cls, component: 'Any') -> 'ComponentState':
        """Create ComponentState from a live Component object."""
        modifiers = []
        # Component.modifiers is always initialized as a list
        for mod in component.modifiers:
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
    movement_policy: str

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

    # Per-ship policies
    targeting_policy: str = "standard"

    # Status flags
    is_alive: bool = True
    is_derelict: bool = False
    retreat_status: Optional[str] = None  # None, "retreating", "escaped"

    # AI state (for resume)
    current_target_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        from game.simulation.battle_state_serde import ship_state_to_dict
        return ship_state_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShipState':
        """Deserialize ShipState from a dictionary.

        Args:
            data: Dictionary containing ship state data

        Returns:
            ShipState instance

        Raises:
            PersistenceException: If required keys are missing or values are invalid
        """
        from game.simulation.battle_state_serde import ship_state_from_dict
        return ship_state_from_dict(data)

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
            for comp in layer_data.components:
                components[layer_name].append(ComponentState.from_component(comp))

        # Capture resource levels
        resource_levels = {}
        resource_max = {}
        if ship.resources:
            for name in ship.resources.get_resource_names():
                resource_levels[name] = ship.resources.get_value(name)
                resource_max[name] = ship.resources.get_max_value(name)

        # Get current target ID if available
        # Ship.current_target is always initialized (None by default). The
        # target may be a Ship OR a Projectile (PDC ships target missiles):
        # ships are resolved by name, projectiles expose only .id.
        current_target_id = None
        if ship.current_target is not None:
            target = ship.current_target
            current_target_id = getattr(target, 'name', None) or getattr(target, 'id', None)

        return cls(
            ship_id=ship_id,
            name=ship.name,
            ship_class=ship.ship_class,
            theme_id=ship.theme_id,
            team_id=ship.team_id,
            color=ship.color if isinstance(ship.color, tuple) else tuple(ship.color),
            movement_policy=ship.movement_policy,
            targeting_policy=ship.targeting_policy,
            position=(ship.x, ship.y),
            velocity=(ship.velocity.x, ship.velocity.y),
            angle=ship.angle,
            current_hp=ship.hp,
            max_hp=ship.max_hp,
            current_shields=ship.current_shields,
            max_shields=ship.max_shields,
            components=components,
            resource_levels=resource_levels,
            resource_max=resource_max,
            is_alive=ship.is_alive,
            is_derelict=ship.is_derelict,
            retreat_status=ship.retreat_status,
            current_target_id=current_target_id,
        )

    def to_ship(self, *, registries: 'GameRegistries') -> 'Ship':
        """
        Create a simulation Ship from this state.

        PROJ-50: Strict DI - registries is required.

        Args:
            registries: GameRegistries for DI (required).

        Returns:
            Ship instance with the stored state applied.

        Raises:
            ValidationException: If registries is None

        Note: This creates a new Ship with the stored state applied.
        Component damage and resource levels are restored.
        """
        if registries is None:
            raise ValidationException(
                "registries is required for ShipState.to_ship",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"class": "ShipState", "method": "to_ship", "parameter": "registries"}
            )
        from game.simulation.entities.ship import Ship
        from game.core.math import Vector2

        # PROJ-50: Use registries directly (strict DI)
        comp_registry = registries.components
        mod_registry = registries.modifiers

        # Create base ship - PROJ-38: Pass registries to Ship constructor
        ship = Ship(
            self.name,
            self.position[0],
            self.position[1],
            self.color,
            self.team_id,
            ship_class=self.ship_class,
            theme_id=self.theme_id,
            registries=registries
        )
        ship.movement_policy = self.movement_policy
        ship.targeting_policy = self.targeting_policy
        ship.angle = self.angle
        ship.velocity = Vector2(self.velocity[0], self.velocity[1])

        for layer_name, comp_states in self.components.items():
            try:
                layer_type = LayerType[layer_name]
            except KeyError:
                # ERR-08/ERR-015: Log missing key with context before skipping
                valid_layers = [lt.name for lt in LayerType]
                logger.warning(
                    f"Unknown layer type '{layer_name}' while rebuilding ship '{self.ship_id}'. "
                    f"Valid layers: {valid_layers}. Skipping this layer."
                )
                continue

            if layer_type not in ship.layers:
                continue

            for comp_state in comp_states:
                if comp_state.component_id in comp_registry:
                    new_comp = comp_registry[comp_state.component_id].clone()

                    # Set ship BEFORE adding modifiers. add_modifier triggers
                    # recalculate_stats, which evaluates ship_class_mass formulas
                    # against component.ship.max_mass_budget.
                    new_comp.ship = ship

                    # PROJ-498: shared save-restore helper (dedupes with
                    # ship_serialization.py). Local import avoids the
                    # Ship -> battle_state -> services cycle.
                    from game.simulation.services.modifier_save_restore import (
                        apply_modifier_with_rejection_logging,
                    )
                    for mod_data in comp_state.modifiers:
                        mid = mod_data['id']
                        mval = mod_data['value']
                        if mid in mod_registry:
                            apply_modifier_with_rejection_logging(
                                modifier_id=mid,
                                modifier_value=mval,
                                component=new_comp,
                                modifier_registry=mod_registry,
                                context_label="BattleState restore",
                                target_label=f"ship '{self.ship_id}'",
                            )

                    ship.add_component(new_comp, layer_type)

                    # Apply damage state AFTER adding (to override default HP)
                    new_comp.current_hp = comp_state.current_hp
                    new_comp.mark_hp_cache_dirty()  # PROJ-49: Mark cache dirty
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
        from game.simulation.battle_state_serde import projectile_state_to_dict
        return projectile_state_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectileState':
        from game.simulation.battle_state_serde import projectile_state_from_dict
        return projectile_state_from_dict(data)

    @classmethod
    def from_projectile(cls, proj: 'Projectile', ship_id_map: Dict[str, str]) -> 'ProjectileState':
        """
        Create ProjectileState from a live Projectile object.

        Args:
            proj: The projectile to capture
            ship_id_map: Mapping from ship.id to battle state ship_id string
        """
        owner_ship_id = None
        if proj.owner:
            owner_ship_id = ship_id_map.get(proj.owner.id)

        # Projectile.target is always initialized (None by default)
        target_ship_id = None
        if proj.target is not None:
            target_ship_id = ship_id_map.get(proj.target.id)

        # Get projectile type as string - AttackType is always an Enum
        proj_type = proj.type
        if isinstance(proj_type, Enum):
            proj_type = proj_type.value

        # All Projectile fields are initialized in __init__
        return cls(
            projectile_id=str(uuid.uuid4()),
            owner_ship_id=owner_ship_id,
            team_id=proj.team_id,
            position=(proj.position.x, proj.position.y),
            velocity=(proj.velocity.x, proj.velocity.y),
            damage=proj.damage,
            max_range=proj.max_range or 0,
            endurance=proj.endurance or 0,
            max_endurance=proj.max_endurance,
            projectile_type=str(proj_type),
            turn_rate=proj.turn_rate,
            max_speed=proj.max_speed,
            target_ship_id=target_ship_id,
            hp=proj.hp,
            max_hp=proj.max_hp,
            distance_traveled=proj.distance_traveled,
            is_alive=proj.is_alive,
        )

    def to_projectile(
        self,
        ship_lookup: Dict[str, 'Ship'],
        event_bus: Any = None,
    ) -> 'Projectile':
        """
        Restore a Projectile from saved state.

        Args:
            ship_lookup: Mapping from ship_id to Ship object for owner/target resolution
            event_bus: Optional session ``EventBus`` (PROJ-405).  When the
                restored projectile resumes ticking inside a battle, it
                must emit lifecycle telemetry (``SEEKER_EXPIRE``) on the
                same bus as freshly-spawned projectiles do.

        Returns:
            Projectile instance with restored state
        """
        from game.simulation.entities.projectile import Projectile
        from game.core.math import Vector2

        # Resolve owner ship reference
        owner = ship_lookup.get(self.owner_ship_id) if self.owner_ship_id else None

        # Resolve target ship reference (for missiles)
        target = ship_lookup.get(self.target_ship_id) if self.target_ship_id else None

        proj_kwargs: Dict[str, Any] = {}
        if event_bus is not None:
            proj_kwargs["event_logger"] = event_bus.log_event

        proj = Projectile(
            owner=owner,
            position=Vector2(self.position[0], self.position[1]),
            velocity=Vector2(self.velocity[0], self.velocity[1]),
            damage=self.damage,
            range_val=self.max_range,
            endurance=self.endurance,
            proj_type=self.projectile_type,
            turn_rate=self.turn_rate,
            max_speed=self.max_speed,
            target=target,
            hp=self.hp,
            **proj_kwargs,
        )

        # Restore additional state
        proj.max_endurance = self.max_endurance
        proj.max_hp = self.max_hp
        proj.distance_traveled = self.distance_traveled
        proj.is_alive = self.is_alive

        return proj


@dataclass
class BattleState:
    """Complete serializable battle state."""
    version: str = "1.0"

    # Identity
    battle_id: str = ""
    seed: Optional[int] = None

    # Timing
    tick_count: int = 0

    # Ships (keyed by ship_id)
    ships: Dict[str, ShipState] = field(default_factory=dict)

    # Projectiles
    projectiles: List[ProjectileState] = field(default_factory=list)

    # Configuration
    end_condition_data: Dict[str, Any] = field(default_factory=lambda: {"type": "team_eliminated"})
    allow_retreat: bool = False
    allow_reinforcements: bool = False

    # Metadata
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        from game.simulation.battle_state_serde import battle_state_to_dict
        return battle_state_to_dict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BattleState':
        from game.simulation.battle_state_serde import battle_state_from_dict
        return battle_state_from_dict(data)

    @classmethod
    def from_json(cls, json_str: str) -> 'BattleState':
        """Deserialize from JSON string.

        PROJ-381 Phase 3 (ERR-01-004): wrap json.JSONDecodeError as a
        chained PersistenceException so corrupt-state failures are
        distinguishable from other deserialization paths.
        """
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise PersistenceException(
                message=f"Corrupt BattleState JSON: {e}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={"json_length": len(json_str)},
            ) from e
        return cls.from_dict(data)

    @classmethod
    def capture_from_engine(
        cls,
        engine: 'BattleEngine',
        seed: Optional[int] = None,
        allow_retreat: bool = False,
        allow_reinforcements: bool = False,
        battle_id: Optional[str] = None,
        ship_id_map: Optional[Dict[str, str]] = None,
    ) -> 'BattleState':
        """
        Capture complete state from a running BattleEngine.

        Args:
            engine: The battle engine to capture from
            seed: Random seed used for this battle
            allow_retreat: Whether retreat is enabled
            allow_reinforcements: Whether reinforcements are enabled
            battle_id: Optional battle ID (generates new UUID if not provided)
            ship_id_map: Optional mapping of ship.id -> battle state id (for consistent IDs across captures)
        """
        if battle_id is None:
            battle_id = str(uuid.uuid4())

        # Build ship ID mapping (ship.id -> battle state id)
        if ship_id_map is None:
            ship_id_map = {}
        ships: Dict[str, ShipState] = {}

        for ship in engine.ships:
            # Use existing mapping or create new ID
            if ship.id in ship_id_map:
                ship_id = ship_id_map[ship.id]
            else:
                ship_id = ship.id
                ship_id_map[ship.id] = ship_id
            ships[ship_id] = ShipState.from_ship(ship, ship_id)

        # Capture projectiles with ship references
        projectiles = []
        for proj in engine.projectiles:
            if proj.is_alive:
                projectiles.append(ProjectileState.from_projectile(proj, ship_id_map))

        # Serialize end condition
        end_condition_data = {"type": "team_eliminated"}
        if engine.end_condition is not None:
            end_condition_data = engine.end_condition.to_dict()

        return cls(
            version="1.0",
            battle_id=battle_id,
            seed=seed,
            tick_count=engine.tick_counter,
            ships=ships,
            projectiles=projectiles,
            end_condition_data=end_condition_data,
            allow_retreat=allow_retreat,
            allow_reinforcements=allow_reinforcements,
            created_at=datetime.now().isoformat(),
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
        from game.simulation.battle_state_serde import battle_results_to_dict
        return battle_results_to_dict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BattleResults':
        from game.simulation.battle_state_serde import battle_results_from_dict
        return battle_results_from_dict(data)

    def get_team_survivors(self, team_id: int) -> List[ShipState]:
        """Get surviving ships for a specific team."""
        return [s for s in self.surviving_ships if s.team_id == team_id]

    def get_team_losses(self, team_id: int) -> List[ShipState]:
        """Get destroyed ships for a specific team."""
        return [s for s in self.destroyed_ships if s.team_id == team_id]
