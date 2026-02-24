"""BattleUIService - Adapter between BattleService and UI layer.

PROJ-43 Phase 12: This service provides a UI-friendly interface to battle state,
converting simulation domain objects to DTOs for safe UI consumption.

The service wraps a BattleService instance and provides read-only
access to battle state through immutable DTOs.

PROJ-113: Added PROJECTILE_COLORS mapping to move visual properties
from simulation layer to UI layer.
"""
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from game.ui.interfaces.battle_ui import (
    ShipDTO,
    ComponentDTO,
    ProjectileDTO,
    BeamDTO,
    ResourceDTO,
)
from game.core.math import Vector2
from game.core.constants import AttackType
from game.ui.colors import PROJECTILE_STANDARD, PROJECTILE_MISSILE, PROJECTILE_BEAM

if TYPE_CHECKING:
    from game.simulation.services import BattleService
    from game.simulation.entities.ship import Ship

# PROJ-113: Projectile color mapping moved from simulation to UI layer
# Maps AttackType to RGB color tuple
PROJECTILE_COLORS: Dict[AttackType, Tuple[int, int, int]] = {
    AttackType.PROJECTILE: PROJECTILE_STANDARD,
    AttackType.MISSILE: PROJECTILE_MISSILE,
    AttackType.BEAM: PROJECTILE_BEAM,
}
DEFAULT_PROJECTILE_COLOR: Tuple[int, int, int] = PROJECTILE_STANDARD


class BattleUIService:
    """Service that provides UI-friendly access to battle state.

    This service converts simulation domain objects to immutable DTOs
    for safe UI consumption.

    Usage:
        battle_service = BattleService()
        battle_service.create_battle()
        # ... add ships, start battle ...

        ui_service = BattleUIService(battle_service)
        ships = ui_service.get_ships()  # List of ShipDTO
        projectiles = ui_service.get_projectiles()  # List of ProjectileDTO
    """

    def __init__(self, battle_service: 'BattleService'):
        """Initialize with a BattleService instance.

        Args:
            battle_service: The BattleService to wrap
        """
        self._battle_service = battle_service

    def _get_engine_or_none(self):
        """Get the battle engine, or None if not available.

        This helper centralizes engine access to reduce code duplication.
        All public methods that need engine access should use this.

        Returns:
            The battle engine if available, None otherwise.
        """
        return self._battle_service.get_engine()

    def get_ships(self) -> List[ShipDTO]:
        """Get all ships in the battle as DTOs.

        Returns:
            List of ShipDTO objects representing all ships
        """
        engine = self._get_engine_or_none()
        if engine is None:
            return []
        return [self._convert_ship(ship) for ship in engine.ships]

    def get_projectiles(self) -> List[ProjectileDTO]:
        """Get all projectiles in the battle as DTOs.

        Returns:
            List of ProjectileDTO objects representing all projectiles
        """
        engine = self._get_engine_or_none()
        if engine is None:
            return []
        return [self._convert_projectile(proj) for proj in engine.projectiles]

    def get_recent_beams(self) -> List[BeamDTO]:
        """Get recent beam weapon effects as DTOs.

        Returns beams fired since last call. UI manages visual fade.

        Returns:
            List of BeamDTO objects for new beam effects
        """
        engine = self._get_engine_or_none()
        if engine is None:
            return []
        return [self._convert_beam(beam) for beam in engine.recent_beams]

    def is_battle_over(self) -> bool:
        """Check if the battle has ended.

        Returns:
            True if battle is over or no engine, False otherwise
        """
        engine = self._get_engine_or_none()
        if engine is None:
            return True
        return engine.is_battle_over()

    def get_winner(self) -> Optional[int]:
        """Get the winning team ID.

        Returns:
            Winning team ID (0 or 1), -1 for draw, or None if battle ongoing/no engine
        """
        engine = self._get_engine_or_none()
        if engine is None:
            return None
        return engine.get_winner()

    def get_tick_count(self) -> int:
        """Get the current simulation tick count.

        Returns:
            Number of simulation ticks elapsed, 0 if no engine
        """
        engine = self._get_engine_or_none()
        if engine is None:
            return 0
        return engine.tick_counter

    def _convert_ship(self, ship: 'Ship') -> ShipDTO:
        """Convert a Ship domain object to ShipDTO.

        Args:
            ship: The Ship object to convert

        Returns:
            ShipDTO with all ship data
        """
        # Convert resources - Ship.resources is always initialized in __init__
        resources = []
        for res in ship.resources.get_all_resources():
            resources.append(ResourceDTO(
                name=res.name,
                current_value=res.current_value,
                max_value=res.max_value
            ))

        # Convert components
        components = []
        for layer_type, layer_data in ship.layers.items():
            layer_name = layer_type.value  # LayerType is always an enum
            for comp in layer_data.components:
                components.append(self._convert_component(comp, layer_name))

        # Get target name - current_target is always initialized (may be None)
        current_target_name = None
        if ship.current_target and hasattr(ship.current_target, 'name'):
            current_target_name = ship.current_target.name

        # Get secondary target names - secondary_targets is always initialized (may be empty)
        secondary_target_names = []
        for target in ship.secondary_targets:
            if hasattr(target, 'name'):
                secondary_target_names.append(target.name)

        # Get ship id - use object id if no explicit id
        ship_id = str(getattr(ship, 'id', id(ship)))

        # Ship uses 'angle' internally (from PhysicsBody), DTO exposes as 'heading'
        heading = ship.angle

        return ShipDTO(
            id=ship_id,
            name=ship.name,
            team_id=ship.team_id,
            position=Vector2(ship.position.x, ship.position.y),
            velocity=Vector2(ship.velocity.x, ship.velocity.y),
            heading=heading,
            is_alive=ship.is_alive,
            is_derelict=ship.is_derelict,
            hp=ship.hp,
            max_hp=ship.max_hp,
            current_shields=ship.current_shields,
            max_shields=ship.max_shields,
            current_speed=ship.current_speed,
            max_speed=ship.max_speed,
            mass=ship.mass,
            total_thrust=ship.total_thrust,
            turn_speed=ship.turn_speed,
            total_shots_fired=ship.total_shots_fired,
            # crew_onboard/crew_required are dynamically set by ShipStatsCalculator, not in __init__
            crew_onboard=getattr(ship, 'crew_onboard', 0),
            crew_required=getattr(ship, 'crew_required', 0),
            current_target_name=current_target_name,
            secondary_target_names=secondary_target_names,
            max_targets=ship.max_targets,
            ai_strategy=ship.ai_strategy,
            source_file=ship.source_file,
            resources=resources,
            components=components
        )

    def _convert_component(self, comp, layer_name: str) -> ComponentDTO:
        """Convert a component to ComponentDTO.

        Args:
            comp: The component object to convert
            layer_name: The layer this component is in

        Returns:
            ComponentDTO with component data
        """
        # Determine status string
        status = "active"
        if hasattr(comp, 'status') and hasattr(comp.status, 'name'):
            status = comp.status.name.lower()

        # Check if it's a weapon
        has_weapon = False
        if hasattr(comp, 'has_ability'):
            has_weapon = comp.has_ability('WeaponAbility')

        return ComponentDTO(
            name=comp.name,
            layer=layer_name,
            current_hp=comp.current_hp,
            max_hp=comp.max_hp,
            is_active=comp.is_active,
            status=status,
            has_weapon=has_weapon,
            shots_fired=getattr(comp, 'shots_fired', 0),
            shots_hit=getattr(comp, 'shots_hit', 0)
        )

    def _convert_projectile(self, proj) -> ProjectileDTO:
        """Convert a projectile to ProjectileDTO.

        Args:
            proj: The projectile object to convert

        Returns:
            ProjectileDTO with projectile data
        """
        # Get target name
        target_name = None
        target = getattr(proj, 'target', None)
        if target and hasattr(target, 'name'):
            target_name = target.name

        # Get projectile id
        proj_id = str(getattr(proj, 'id', id(proj)))

        # PROJ-113: Get color from type mapping (UI concern, not simulation)
        proj_type = getattr(proj, 'type', None)
        color = PROJECTILE_COLORS.get(proj_type, DEFAULT_PROJECTILE_COLOR)

        return ProjectileDTO(
            id=proj_id,
            position=Vector2(proj.position.x, proj.position.y),
            velocity=Vector2(proj.velocity.x, proj.velocity.y),
            color=color,
            radius=getattr(proj, 'radius', 4.0),
            damage=proj.damage,
            hp=getattr(proj, 'hp', 0.0),
            max_hp=getattr(proj, 'max_hp', 0.0),
            status=getattr(proj, 'status', 'active'),
            endurance=getattr(proj, 'endurance', 0.0),
            max_endurance=getattr(proj, 'max_endurance', 0.0),
            target_name=target_name,
            max_speed=getattr(proj, 'max_speed', 0.0)
        )

    def _convert_beam(self, beam: dict) -> BeamDTO:
        """Convert a beam dict to BeamDTO.

        Args:
            beam: Dictionary with beam data (start, end, color)

        Returns:
            BeamDTO with beam visual data
        """
        start = beam.get('start', Vector2(0, 0))
        end = beam.get('end', Vector2(0, 0))

        return BeamDTO(
            start=Vector2(start.x, start.y),
            end=Vector2(end.x, end.y),
            color=beam.get('color', (255, 255, 255))
        )
