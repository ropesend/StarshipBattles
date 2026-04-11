"""
Deployment zone calculator — maps BattleRole to battlefield positions.

Computes deployment positions for fleet hierarchy groups based on their
battle role. Each role maps to a zone on the 100000x100000 battlefield.

Team 0 deploys on the left, Team 1 on the right (mirrored).
"""

from typing import List, Optional, Tuple

from game.core.math import Vector2
from game.strategy.data.fleet_hierarchy import BattleRole

# Battlefield dimensions
BATTLEFIELD_WIDTH = 100000
BATTLEFIELD_CENTER_X = 50000
BATTLEFIELD_CENTER_Y = 50000

# Ship spacing within a zone
SHIP_SPACING = 2000

# Zone X positions for team 0 (team 1 mirrors around center)
_ZONE_X_TEAM_0 = {
    BattleRole.RESERVE: 10000,
    BattleRole.MAIN_BODY: 25000,
    BattleRole.SCREEN: 35000,
    BattleRole.VANGUARD: 42000,
    BattleRole.FLANKER_LEFT: 25000,
    BattleRole.FLANKER_RIGHT: 25000,
}

# Zone Y offsets from center (0 = centered)
_ZONE_Y_OFFSET = {
    BattleRole.RESERVE: 0,
    BattleRole.MAIN_BODY: 0,
    BattleRole.SCREEN: 0,
    BattleRole.VANGUARD: 0,
    BattleRole.FLANKER_LEFT: -15000,
    BattleRole.FLANKER_RIGHT: 15000,
}


class DeploymentZoneCalculator:
    """Computes deployment positions from BattleRole assignments.

    Static methods — no instance state needed.
    """

    @staticmethod
    def get_zone_center(
        battle_role: BattleRole,
        team_id: int,
    ) -> Vector2:
        """Get the center position of a deployment zone.

        Args:
            battle_role: The deployment role.
            team_id: 0 for left side, 1 for right side.

        Returns:
            Zone center as Vector2.
        """
        x_team_0 = _ZONE_X_TEAM_0.get(battle_role, _ZONE_X_TEAM_0[BattleRole.MAIN_BODY])
        y_offset = _ZONE_Y_OFFSET.get(battle_role, 0)

        if team_id == 0:
            x = x_team_0
        else:
            # Mirror: team 1 position = battlefield_width - team 0 position
            x = BATTLEFIELD_WIDTH - x_team_0

        y = BATTLEFIELD_CENTER_Y + y_offset

        return Vector2(x, y)

    @staticmethod
    def compute_positions(
        ship_count: int,
        battle_role: Optional[BattleRole],
        team_id: int,
        spacing: float = SHIP_SPACING,
    ) -> List[Tuple[float, float]]:
        """Compute ship positions within a deployment zone.

        Ships are arranged in a vertical line centered on the zone.

        Args:
            ship_count: Number of ships to position.
            battle_role: Deployment role (None defaults to MAIN_BODY).
            team_id: 0 or 1.
            spacing: Vertical distance between ships.

        Returns:
            List of (x, y) position tuples.
        """
        if battle_role is None:
            battle_role = BattleRole.MAIN_BODY

        center = DeploymentZoneCalculator.get_zone_center(battle_role, team_id)

        positions = []
        for i in range(ship_count):
            y = center.y + (i - (ship_count - 1) / 2.0) * spacing
            positions.append((center.x, y))

        return positions
