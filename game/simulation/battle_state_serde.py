"""Save/load helpers for the simulation BattleState dataclass family.

Free functions for the 5 dataclasses (ComponentState, ShipState,
ProjectileState, BattleState, BattleResults). The dataclass
``to_dict`` / ``from_dict`` methods are 1-line facades that call into
these helpers. Extraction preserves byte-identical dict output.

Modeled on ``game/strategy/data/planet_serde.py`` (PROJ-372). PROJ-460
Phase 1 (F-D-028). Multi-class variant.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, TYPE_CHECKING

from game.core.error_codes import ErrorCode
from game.core.exceptions import PersistenceException
from game.core.validation_helpers import (
    require_keys, validate_non_negative, validate_positive
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.simulation.battle_state import (
        BattleResults,
        BattleState,
        ComponentState,
        ProjectileState,
        ShipState,
    )

__all__ = [
    "component_state_to_dict",
    "component_state_from_dict",
    "ship_state_to_dict",
    "ship_state_from_dict",
    "projectile_state_to_dict",
    "projectile_state_from_dict",
    "battle_state_to_dict",
    "battle_state_from_dict",
    "battle_results_to_dict",
    "battle_results_from_dict",
]


# ---------------------------------------------------------------------------
# ComponentState
# ---------------------------------------------------------------------------
def component_state_to_dict(state: "ComponentState") -> Dict[str, Any]:
    return {
        'component_id': state.component_id,
        'current_hp': state.current_hp,
        'max_hp': state.max_hp,
        'is_active': state.is_active,
        'layer': state.layer,
        'modifiers': state.modifiers,
    }


def component_state_from_dict(data: Dict[str, Any]) -> "ComponentState":
    """Deserialize ComponentState from a dictionary.

    Args:
        data: Dictionary containing component state data

    Returns:
        ComponentState instance

    Raises:
        PersistenceException: If required keys are missing or values are invalid
    """
    from game.simulation.battle_state import ComponentState

    require_keys(
        data,
        ['component_id', 'current_hp', 'max_hp', 'is_active', 'layer'],
        'ComponentState'
    )
    validate_non_negative(data['current_hp'], 'current_hp', 'ComponentState')
    validate_positive(data['max_hp'], 'max_hp', 'ComponentState')

    return ComponentState(
        component_id=data['component_id'],
        current_hp=data['current_hp'],
        max_hp=data['max_hp'],
        is_active=data['is_active'],
        layer=data['layer'],
        modifiers=data.get('modifiers', []),
    )


# ---------------------------------------------------------------------------
# ShipState
# ---------------------------------------------------------------------------
def ship_state_to_dict(state: "ShipState") -> Dict[str, Any]:
    return {
        'ship_id': state.ship_id,
        'name': state.name,
        'ship_class': state.ship_class,
        'theme_id': state.theme_id,
        'team_id': state.team_id,
        'color': list(state.color),
        'movement_policy': state.movement_policy,
        'targeting_policy': state.targeting_policy,
        'position': list(state.position),
        'velocity': list(state.velocity),
        'angle': state.angle,
        'current_hp': state.current_hp,
        'max_hp': state.max_hp,
        'current_shields': state.current_shields,
        'max_shields': state.max_shields,
        'components': {
            layer: [c.to_dict() for c in comps]
            for layer, comps in state.components.items()
        },
        'resource_levels': state.resource_levels,
        'resource_max': state.resource_max,
        'is_alive': state.is_alive,
        'is_derelict': state.is_derelict,
        'retreat_status': state.retreat_status,
        'current_target_id': state.current_target_id,
    }


def ship_state_from_dict(data: Dict[str, Any]) -> "ShipState":
    """Deserialize ShipState from a dictionary.

    Args:
        data: Dictionary containing ship state data

    Returns:
        ShipState instance

    Raises:
        PersistenceException: If required keys are missing or values are invalid
    """
    from game.simulation.battle_state import ComponentState, ShipState

    require_keys(
        data,
        ['ship_id', 'name', 'ship_class', 'theme_id', 'team_id', 'color',
         'movement_policy', 'position', 'velocity', 'angle', 'current_hp',
         'max_hp', 'current_shields', 'max_shields'],
        'ShipState'
    )

    # Validate color format (must be list/tuple with at least 3 elements)
    color = data['color']
    if not isinstance(color, (list, tuple)) or len(color) < 3:
        raise PersistenceException(
            f"ShipState: color must be a list/tuple with at least 3 elements, got {type(color).__name__}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={
                "source": "ShipState",
                "field": "color",
                "value": str(color)[:100],
                "expected": "list or tuple with >= 3 elements"
            }
        )

    # Validate position format
    position = data['position']
    if not isinstance(position, (list, tuple)) or len(position) < 2:
        raise PersistenceException(
            f"ShipState: position must be a list/tuple with at least 2 elements, got {type(position).__name__}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={
                "source": "ShipState",
                "field": "position",
                "value": str(position)[:100],
                "expected": "list or tuple with >= 2 elements"
            }
        )

    # Validate velocity format
    velocity = data['velocity']
    if not isinstance(velocity, (list, tuple)) or len(velocity) < 2:
        raise PersistenceException(
            f"ShipState: velocity must be a list/tuple with at least 2 elements, got {type(velocity).__name__}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={
                "source": "ShipState",
                "field": "velocity",
                "value": str(velocity)[:100],
                "expected": "list or tuple with >= 2 elements"
            }
        )

    # Deserialize components with resilient error handling
    components = {}
    for layer, comps in data.get('components', {}).items():
        components[layer] = []
        for i, c in enumerate(comps):
            try:
                components[layer].append(ComponentState.from_dict(c))
            except (PersistenceException, KeyError, TypeError) as e:
                logger.warning(
                    f"ShipState: skipping corrupt component at {layer}[{i}]: {e}"
                )

    return ShipState(
        ship_id=data['ship_id'],
        name=data['name'],
        ship_class=data['ship_class'],
        theme_id=data['theme_id'],
        team_id=data['team_id'],
        color=tuple(color),
        movement_policy=data['movement_policy'],
        targeting_policy=data.get('targeting_policy', 'standard'),
        position=tuple(position),
        velocity=tuple(velocity),
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


# ---------------------------------------------------------------------------
# ProjectileState
# ---------------------------------------------------------------------------
def projectile_state_to_dict(state: "ProjectileState") -> Dict[str, Any]:
    return {
        'projectile_id': state.projectile_id,
        'owner_ship_id': state.owner_ship_id,
        'team_id': state.team_id,
        'position': list(state.position),
        'velocity': list(state.velocity),
        'damage': state.damage,
        'max_range': state.max_range,
        'endurance': state.endurance,
        'max_endurance': state.max_endurance,
        'projectile_type': state.projectile_type,
        'turn_rate': state.turn_rate,
        'max_speed': state.max_speed,
        'target_ship_id': state.target_ship_id,
        'hp': state.hp,
        'max_hp': state.max_hp,
        'distance_traveled': state.distance_traveled,
        'is_alive': state.is_alive,
    }


def projectile_state_from_dict(data: Dict[str, Any]) -> "ProjectileState":
    from game.simulation.battle_state import ProjectileState

    return ProjectileState(
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


# ---------------------------------------------------------------------------
# BattleState
# ---------------------------------------------------------------------------
def battle_state_to_dict(state: "BattleState") -> Dict[str, Any]:
    return {
        'version': state.version,
        'battle_id': state.battle_id,
        'seed': state.seed,
        'tick_count': state.tick_count,
        'ships': {sid: s.to_dict() for sid, s in state.ships.items()},
        'projectiles': [p.to_dict() for p in state.projectiles],
        'end_condition_data': state.end_condition_data,
        'allow_retreat': state.allow_retreat,
        'allow_reinforcements': state.allow_reinforcements,
        'created_at': state.created_at,
    }


def battle_state_from_dict(data: Dict[str, Any]) -> "BattleState":
    from game.simulation.battle_state import BattleState, ProjectileState, ShipState

    ships = {}
    for sid, sdata in data.get('ships', {}).items():
        ships[sid] = ShipState.from_dict(sdata)

    projectiles = []
    for pdata in data.get('projectiles', []):
        projectiles.append(ProjectileState.from_dict(pdata))

    return BattleState(
        version=data.get('version', '1.0'),
        battle_id=data.get('battle_id', ''),
        seed=data.get('seed'),
        tick_count=data.get('tick_count', 0),
        ships=ships,
        projectiles=projectiles,
        end_condition_data=data.get('end_condition_data', {"type": "team_eliminated"}),
        allow_retreat=data.get('allow_retreat', False),
        allow_reinforcements=data.get('allow_reinforcements', False),
        created_at=data.get('created_at', ''),
    )


# ---------------------------------------------------------------------------
# BattleResults
# ---------------------------------------------------------------------------
def battle_results_to_dict(state: "BattleResults") -> Dict[str, Any]:
    return {
        'winner': state.winner,
        'tick_count': state.tick_count,
        'seed': state.seed,
        'initial_state': state.initial_state.to_dict() if state.initial_state else None,
        'final_state': state.final_state.to_dict() if state.final_state else None,
        'surviving_ships': [s.to_dict() for s in state.surviving_ships],
        'destroyed_ships': [s.to_dict() for s in state.destroyed_ships],
        'escaped_ships': [s.to_dict() for s in state.escaped_ships],
        'captured_ships': [s.to_dict() for s in state.captured_ships],
    }


def battle_results_from_dict(data: Dict[str, Any]) -> "BattleResults":
    from game.simulation.battle_state import BattleResults, BattleState, ShipState

    initial_state = None
    if data.get('initial_state'):
        initial_state = BattleState.from_dict(data['initial_state'])

    final_state = None
    if data.get('final_state'):
        final_state = BattleState.from_dict(data['final_state'])

    return BattleResults(
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
