"""Fleet battle adapter - extracted from Fleet class.

PROJ-87 Phase 4: Bridges strategy layer Fleet with simulation layer Ship
for battle conversion.

PROJ-90 Phase 4: Uses IPostBattleShip protocol for strategy-simulation boundary.
"""

import logging
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from game.core.protocols import IPostBattleShip

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.fleet_hierarchy import CombatPolicy
    from game.strategy.data.group_policy_registry import GroupPolicyRegistry
    from game.strategy.data.ship_instance import ShipInstance
    from game.simulation.entities.ship import Ship
    from game.core.registry import GameRegistries

logger = logging.getLogger(__name__)

# Default battle formation positions (in simulation coordinates)
FORMATION_BASE_X_TEAM_0 = 20000  # Left side of battlefield
FORMATION_BASE_X_TEAM_1 = 80000  # Right side of battlefield
FORMATION_BASE_Y = 50000         # Vertical center of battlefield
FORMATION_SHIP_SPACING = 2000    # Vertical spacing between ships


class FleetBattleAdapter:
    """
    Handles conversion between strategy Fleet and simulation Ship objects.

    Bridges the strategy/simulation layer boundary for combat:
    - Converts FleetShipInstances to simulation Ships for battle
    - Updates FleetShipInstances from battle results
    - Generates default formation positions
    """

    def __init__(self, fleet: 'Fleet'):
        """
        Initialize adapter with fleet reference.

        Args:
            fleet: The Fleet instance to adapt for battle.
        """
        self._fleet = fleet

    def to_battle_ships(
        self,
        team_id: int,
        formation_positions: Optional[List[Tuple[float, float]]] = None,
        registries: Optional['GameRegistries'] = None
    ) -> List['Ship']:
        """
        Convert fleet ships to simulation Ship objects for battle.

        Only works with ShipInstance objects - legacy strings cannot be converted.

        Args:
            team_id: Team assignment for battle (0 or 1)
            formation_positions: Optional list of (x, y) positions for ships
            registries: Optional GameRegistries for DI. If None, uses global provider.

        Returns:
            List of Ship objects ready for battle
        """
        ships = []

        if not self._fleet.ships:
            return []

        # Generate default positions if not provided
        if formation_positions is None:
            formation_positions = self._default_formation_positions(
                len(self._fleet.ships), team_id
            )

        # Resolve fleet hierarchy policies per ship
        policy_overrides = self._resolve_ship_policies()

        for i, instance in enumerate(self._fleet.ships):
            if not instance.is_combat_capable():
                continue

            pos = formation_positions[i] if i < len(formation_positions) else (0, 0)
            ship = instance.to_ship(pos, team_id, registries=registries)

            # Apply hierarchy policy overrides
            override = policy_overrides.get(instance.instance_id)
            if override:
                mov, tgt = override
                if mov:
                    ship.movement_policy = mov
                if tgt:
                    ship.targeting_policy = tgt

            ships.append(ship)

        return ships

    def _resolve_ship_policies(self) -> Dict[str, Optional[Tuple[Optional[str], Optional[str]]]]:
        """Resolve effective movement/targeting policy for each ship from hierarchy.

        Walks Fleet → TaskForce → Squadron → per-ship override, mapping group
        policy keys to per-ship policy IDs via group_policies.json.

        Returns:
            Dict mapping instance_id to (movement_policy_id, targeting_policy_id).
            Values are None when no hierarchy override applies (ship keeps its design default).
        """
        from game.strategy.data.group_policy_registry import GroupPolicyRegistry

        registry = GroupPolicyRegistry()
        registry.load()

        result: Dict[str, Optional[Tuple[Optional[str], Optional[str]]]] = {}
        fleet_policy = self._fleet.fleet_policy

        for tf in self._fleet.task_forces:
            tf_effective = tf.resolve_effective_policy(fleet_policy)

            for sq in tf.squadrons:
                sq_effective = sq.resolve_effective_policy(tf_effective)
                for ship in sq.all_ships:
                    self._apply_policy_override(result, ship, sq_effective, registry)

            for ship in tf.lone_ships:
                self._apply_policy_override(result, ship, tf_effective, registry)

        # Unassigned ships get fleet-level policy
        assigned_ids = set(result.keys())
        for ship in self._fleet.ships:
            if ship.instance_id not in assigned_ids:
                self._apply_policy_override(result, ship, fleet_policy, registry)

        return result

    @staticmethod
    def _apply_policy_override(
        result: Dict,
        ship: 'ShipInstance',
        group_policy: 'CombatPolicy',
        registry: 'GroupPolicyRegistry',
    ) -> None:
        """Map a resolved group CombatPolicy to per-ship policy IDs."""
        mov_override = None
        tgt_override = None

        # Per-ship override from battle setup (stored in design_data)
        ship_mov_group = ship.design_data.get('_movement_policy')

        # Use per-ship override if set, otherwise use group hierarchy
        mov_group_key = ship_mov_group or group_policy.movement

        # Map group movement key → per_ship_policy via registry
        if mov_group_key:
            group_def = registry.get_movement(mov_group_key)
            if group_def and 'per_ship_policy' in group_def:
                mov_override = group_def['per_ship_policy']

        # Per-ship targeting override from battle setup is a direct policy ID
        ship_tgt = ship.design_data.get('_targeting_policy')
        if ship_tgt:
            tgt_override = ship_tgt

        if mov_override or tgt_override:
            result[ship.instance_id] = (mov_override, tgt_override)

    def _default_formation_positions(
        self,
        count: int,
        team_id: int
    ) -> List[Tuple[float, float]]:
        """Generate default formation positions for ships."""
        positions = []

        # Team 0 starts on the left, Team 1 on the right
        base_x = FORMATION_BASE_X_TEAM_0 if team_id == 0 else FORMATION_BASE_X_TEAM_1

        for i in range(count):
            y = FORMATION_BASE_Y + (i - count // 2) * FORMATION_SHIP_SPACING
            positions.append((base_x, y))

        return positions

    def update_from_battle_results(
        self,
        surviving_ships: List[IPostBattleShip],
    ) -> None:
        """
        Update fleet ships from battle results.

        Args:
            surviving_ships: Ships that survived the battle (IPostBattleShip protocol)
        """
        # PROJ-254: Match by instance_id (unique), not name (may have duplicates)
        survivors_by_id = {s.instance_id: s for s in surviving_ships if s.instance_id}

        # Update each ShipInstance - ships not in survivors were destroyed
        new_ships = []
        for s in self._fleet.ships:
            if s.instance_id in survivors_by_id:
                s.update_from_ship(survivors_by_id[s.instance_id])
                new_ships.append(s)
            # else: ship was destroyed, don't include

        self._fleet.ships = new_ships

        # Recalculate speed (ships may have been destroyed or damaged)
        self._fleet.trigger_speed_recalculation()
