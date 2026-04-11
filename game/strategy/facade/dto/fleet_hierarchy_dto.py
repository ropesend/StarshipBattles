"""Fleet hierarchy Data Transfer Objects.

Immutable DTOs for fleet hierarchy (TaskForce, Squadron) UI display.
Follows the same pattern as fleet_dto.py.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.task_force import TaskForce
    from game.strategy.data.squadron import Squadron


@dataclass(frozen=True)
class ShipInfoExtended:
    """Ship info with design role for hierarchy display."""

    instance_id: str
    name: str
    design_id: str
    ship_class: str
    is_combat_capable: bool
    current_hp_percent: float
    effective_role: Optional[str] = None

    @classmethod
    def from_ship_instance(cls, ship) -> 'ShipInfoExtended':
        """Create from a ShipInstance."""
        return cls(
            instance_id=ship.instance_id,
            name=ship.name,
            design_id=ship.design_id,
            ship_class=ship.design_data.get("ship_class", "Unknown"),
            is_combat_capable=ship.is_combat_capable(),
            current_hp_percent=ship.get_hp_percentage(),
            effective_role=getattr(ship, 'effective_role', None),
        )


@dataclass(frozen=True)
class SquadronInfo:
    """Immutable DTO representing a Squadron for UI display."""

    node_id: str
    name: str
    ship_count: int
    battle_role: Optional[str] = None
    targeting: Optional[str] = None
    movement: Optional[str] = None
    retreat: Optional[str] = None
    spatial_behavior: Optional[str] = None
    flagship_id: Optional[str] = None

    @classmethod
    def from_squadron(cls, sq: 'Squadron') -> 'SquadronInfo':
        """Create from a Squadron domain object."""
        return cls(
            node_id=sq.node_id,
            name=sq.name,
            ship_count=len(sq.all_ships),
            battle_role=sq.battle_role.value if sq.battle_role else None,
            targeting=sq.policy.targeting,
            movement=sq.policy.movement,
            retreat=sq.policy.retreat,
            spatial_behavior=sq.spatial_behavior,
            flagship_id=sq.flagship_id,
        )


@dataclass(frozen=True)
class TaskForceInfo:
    """Immutable DTO representing a TaskForce for UI display."""

    node_id: str
    name: str
    total_ship_count: int
    lone_ship_count: int
    battle_role: Optional[str] = None
    targeting: Optional[str] = None
    movement: Optional[str] = None
    retreat: Optional[str] = None
    flagship_id: Optional[str] = None
    squadrons: Tuple[SquadronInfo, ...] = field(default_factory=tuple)

    @classmethod
    def from_task_force(cls, tf: 'TaskForce') -> 'TaskForceInfo':
        """Create from a TaskForce domain object."""
        sq_infos = tuple(
            SquadronInfo.from_squadron(sq) for sq in tf.squadrons
        )

        return cls(
            node_id=tf.node_id,
            name=tf.name,
            total_ship_count=len(tf.all_ships),
            lone_ship_count=len(tf.lone_ships),
            battle_role=tf.battle_role.value if tf.battle_role else None,
            targeting=tf.policy.targeting,
            movement=tf.policy.movement,
            retreat=tf.policy.retreat,
            flagship_id=tf.flagship_id,
            squadrons=sq_infos,
        )
