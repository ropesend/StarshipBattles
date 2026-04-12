"""
TaskForce — mid-level organizational node in the fleet hierarchy.

A TaskForce contains Squadrons and lone ships. It is the middle
organizational level: Fleet -> TaskForce -> Squadron -> Ships.
"""

from typing import List, Optional, Dict, Any, TYPE_CHECKING

from game.core.math import Vector2
from game.simulation.combat.formation import FormationShape, FormationSpec
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
        formation: Optional[FormationSpec] = None,
    ):
        super().__init__(
            name=name,
            node_id=node_id,
            policy=policy,
            battle_role=battle_role,
            flagship_id=flagship_id,
        )
        self._squadrons: List[Squadron] = []
        # PROJ-269 Phase 4: formation authored for this task force.
        # `None` → design-role default resolved by `FormationResolver`.
        self.formation: Optional[FormationSpec] = formation

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

        # PROJ-269 Phase 4: formation (omitted when None for back-compat).
        if self.formation is not None:
            data["formation"] = _formation_to_dict(self.formation)

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskForce':
        """Deserialize from dict."""
        policy = CombatPolicy.from_dict(data.get("policy", {}))

        battle_role = None
        if "battle_role" in data:
            battle_role = BattleRole(data["battle_role"])

        formation = _formation_from_dict(data.get("formation"))

        tf = cls(
            name=data["name"],
            node_id=data.get("node_id"),
            policy=policy,
            battle_role=battle_role,
            flagship_id=data.get("flagship_id"),
            formation=formation,
        )

        for sq_data in data.get("squadrons", []):
            tf.add_squadron(Squadron.from_dict(sq_data))

        return tf


# ---------------------------------------------------------------------------
# FormationSpec (de)serialization helpers — local to TaskForce since it is
# the only strategy-layer holder of FormationSpec today.
# ---------------------------------------------------------------------------


def _formation_to_dict(formation: FormationSpec) -> Dict[str, Any]:
    return {
        "shape": formation.shape.value,
        "spacing": float(formation.spacing),
        "custom_positions": [
            [float(p.x), float(p.y)] for p in formation.custom_positions
        ],
    }


def _formation_from_dict(data: Optional[Dict[str, Any]]) -> Optional[FormationSpec]:
    if data is None:
        return None
    shape = FormationShape(data["shape"])
    spacing = float(data.get("spacing", 100.0))
    raw_positions = data.get("custom_positions", [])
    custom = tuple(Vector2(float(p[0]), float(p[1])) for p in raw_positions)
    return FormationSpec(shape=shape, spacing=spacing, custom_positions=custom)
