"""
TaskForce — mid-level organizational node in the fleet hierarchy.

A TaskForce contains Squadrons and lone ships. It is the middle
organizational level: Fleet -> TaskForce -> Squadron -> Ships.
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING

from game.strategy.data.fleet_hierarchy import (
    FleetHierarchyNode,
    CombatPolicy,
    BattleRole,
)
from game.strategy.data.squadron import Squadron

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


class TaskForce(FleetHierarchyNode):
    """A task force — mid-level organizational node.

    Contains:
    - Squadrons (child groups)
    - Lone ships (ships not in any squadron)
    - Policy overrides (inherited)
    """

    def __init__(
        self,
        name: str,
        node_id: Optional[str] = None,
        policy: Optional[CombatPolicy] = None,
        battle_role: Optional[BattleRole] = None,
        flagship_id: Optional[str] = None,
    ):
        super().__init__(
            name=name,
            node_id=node_id,
            policy=policy,
            battle_role=battle_role,
            flagship_id=flagship_id,
        )
        self._squadrons: List[Squadron] = []

    @property
    def squadrons(self) -> List[Squadron]:
        """Child squadrons of this task force."""
        return self._squadrons

    def add_squadron(self, squadron: Squadron) -> None:
        """Add a squadron to this task force."""
        if squadron not in self._squadrons:
            self._squadrons.append(squadron)

    def remove_squadron(self, squadron: Squadron) -> bool:
        """Remove a squadron. Returns True if found and removed."""
        if squadron in self._squadrons:
            self._squadrons.remove(squadron)
            return True
        return False

    @property
    def all_ships(self) -> List['ShipInstance']:
        """All ships: from all squadrons + lone ships at TF level."""
        ships: List['ShipInstance'] = []
        for sq in self._squadrons:
            ships.extend(sq.all_ships)
        ships.extend(self._lone_ships)
        return ships

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        data = super().to_dict()
        data["type"] = "task_force"

        if self._squadrons:
            data["squadrons"] = [sq.to_dict() for sq in self._squadrons]

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskForce':
        """Deserialize from dict."""
        policy = CombatPolicy.from_dict(data.get("policy", {}))

        battle_role = None
        if "battle_role" in data:
            battle_role = BattleRole(data["battle_role"])

        tf = cls(
            name=data["name"],
            node_id=data.get("node_id"),
            policy=policy,
            battle_role=battle_role,
            flagship_id=data.get("flagship_id"),
        )

        for sq_data in data.get("squadrons", []):
            tf.add_squadron(Squadron.from_dict(sq_data))

        return tf
