"""
Fleet hierarchy foundational types.

Provides BattleRole, CombatPolicy, and FleetHierarchyNode — the shared
base for TaskForce and Squadron in the Fleet -> TaskForce -> Squadron
hierarchy.
"""

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


class BattleRole(Enum):
    """Deployment zone on the battlefield.

    Determines where a group is placed when combat begins.
    """
    VANGUARD = "vanguard"
    SCREEN = "screen"
    MAIN_BODY = "main_body"
    FLANKER_LEFT = "flanker_left"
    FLANKER_RIGHT = "flanker_right"
    RESERVE = "reserve"


@dataclass
class CombatPolicy:
    """Three independent policy axes for combat behavior.

    Each axis can be None (inherit from parent) or a string preset ID.
    """
    targeting: Optional[str] = None
    movement: Optional[str] = None
    retreat: Optional[str] = None

    @property
    def is_empty(self) -> bool:
        """True when all axes are None (fully inherits from parent)."""
        return (
            self.targeting is None
            and self.movement is None
            and self.retreat is None
        )

    def resolve(self, parent: Optional['CombatPolicy']) -> 'CombatPolicy':
        """Resolve effective policy by filling None axes from parent.

        Args:
            parent: Parent policy to inherit from, or None.

        Returns:
            New CombatPolicy with None axes filled from parent.
        """
        if parent is None:
            return CombatPolicy(
                targeting=self.targeting,
                movement=self.movement,
                retreat=self.retreat,
            )
        return CombatPolicy(
            targeting=self.targeting if self.targeting is not None else parent.targeting,
            movement=self.movement if self.movement is not None else parent.movement,
            retreat=self.retreat if self.retreat is not None else parent.retreat,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict, omitting None values."""
        data: Dict[str, Any] = {}
        if self.targeting is not None:
            data["targeting"] = self.targeting
        if self.movement is not None:
            data["movement"] = self.movement
        if self.retreat is not None:
            data["retreat"] = self.retreat
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CombatPolicy':
        """Deserialize from dict."""
        return cls(
            targeting=data.get("targeting"),
            movement=data.get("movement"),
            retreat=data.get("retreat"),
        )


class FleetHierarchyNode:
    """Base class for organizational nodes in the fleet hierarchy.

    Both TaskForce and Squadron inherit from this. Provides:
    - Name and unique ID
    - CombatPolicy (3 axes: targeting, movement, retreat)
    - BattleRole (deployment zone)
    - Lone ships (ships directly in this node, not in a sub-group)
    - Flagship designation
    """

    def __init__(
        self,
        name: str,
        node_id: Optional[str] = None,
        policy: Optional[CombatPolicy] = None,
        battle_role: Optional[BattleRole] = None,
        flagship_id: Optional[str] = None,
    ):
        self.name = name
        self.node_id = node_id or str(uuid.uuid4())
        self.policy = policy or CombatPolicy()
        self.battle_role = battle_role
        self.flagship_id = flagship_id
        self._lone_ships: List['ShipInstance'] = []

    @property
    def lone_ships(self) -> List['ShipInstance']:
        """Ships directly in this node, not in any sub-group."""
        return self._lone_ships

    def add_lone_ship(self, ship: 'ShipInstance') -> None:
        """Add a ship directly to this node (not in a sub-group)."""
        if ship not in self._lone_ships:
            self._lone_ships.append(ship)

    def remove_lone_ship(self, ship: 'ShipInstance') -> bool:
        """Remove a lone ship. Returns True if found and removed."""
        if ship in self._lone_ships:
            self._lone_ships.remove(ship)
            return True
        return False

    @property
    def all_ships(self) -> List['ShipInstance']:
        """All ships in this node and its children.

        Subclasses override to include ships from sub-groups.
        Order: sub-group ships first (in sub-group order), then lone ships.
        """
        return list(self._lone_ships)

    def resolve_effective_policy(
        self,
        parent_policy: Optional[CombatPolicy] = None
    ) -> CombatPolicy:
        """Resolve this node's effective policy given a parent policy."""
        return self.policy.resolve(parent_policy)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        data: Dict[str, Any] = {
            "name": self.name,
            "node_id": self.node_id,
        }

        policy_data = self.policy.to_dict()
        if policy_data:
            data["policy"] = policy_data

        if self.battle_role is not None:
            data["battle_role"] = self.battle_role.value

        if self.flagship_id is not None:
            data["flagship_id"] = self.flagship_id

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FleetHierarchyNode':
        """Deserialize from dict."""
        policy = CombatPolicy.from_dict(data.get("policy", {}))

        battle_role = None
        if "battle_role" in data:
            battle_role = BattleRole(data["battle_role"])

        return cls(
            name=data["name"],
            node_id=data.get("node_id"),
            policy=policy,
            battle_role=battle_role,
            flagship_id=data.get("flagship_id"),
        )
