"""
Squadron — leaf organizational node in the fleet hierarchy.

A Squadron contains ships and optional lone ships. It is the lowest
organizational level: Fleet -> TaskForce -> Squadron -> Ships.
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING

from game.strategy.data.fleet_hierarchy import (
    FleetHierarchyNode,
    CombatPolicy,
    BattleRole,
)

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


class Squadron(FleetHierarchyNode):
    """A squadron of ships — the leaf organizational node.

    Contains:
    - Member ships (the primary ship list)
    - Lone ships (inherited from FleetHierarchyNode)
    - Spatial behavior configuration
    - Policy overrides (inherited)
    """

    def __init__(
        self,
        name: str,
        node_id: Optional[str] = None,
        policy: Optional[CombatPolicy] = None,
        battle_role: Optional[BattleRole] = None,
        flagship_id: Optional[str] = None,
        spatial_behavior: Optional[str] = None,
        spatial_behavior_params: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            name=name,
            node_id=node_id,
            policy=policy,
            battle_role=battle_role,
            flagship_id=flagship_id,
        )
        self._ships: List['ShipInstance'] = []
        self.spatial_behavior = spatial_behavior
        self.spatial_behavior_params = spatial_behavior_params or {}

    @property
    def ships(self) -> List['ShipInstance']:
        """Member ships of this squadron."""
        return self._ships

    def add_ship(self, ship: 'ShipInstance') -> None:
        """Add a ship to this squadron."""
        if ship not in self._ships:
            self._ships.append(ship)

    def remove_ship(self, ship: 'ShipInstance') -> bool:
        """Remove a ship from this squadron. Returns True if found."""
        if ship in self._ships:
            self._ships.remove(ship)
            return True
        return False

    @property
    def all_ships(self) -> List['ShipInstance']:
        """All ships: squadron members + lone ships."""
        return list(self._ships) + list(self._lone_ships)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict."""
        data = super().to_dict()
        data["type"] = "squadron"

        if self.spatial_behavior is not None:
            data["spatial_behavior"] = self.spatial_behavior
        if self.spatial_behavior_params:
            data["spatial_behavior_params"] = self.spatial_behavior_params

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Squadron':
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
            spatial_behavior=data.get("spatial_behavior"),
            spatial_behavior_params=data.get("spatial_behavior_params"),
        )
