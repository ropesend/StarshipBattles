"""Fleet battle adapter - extracted from Fleet class.

PROJ-87 Phase 4: Bridges strategy layer Fleet with simulation layer Ship
for battle conversion.

PROJ-90 Phase 4: Uses IPostBattleShip protocol for strategy-simulation boundary.
"""

from typing import List, Optional, Tuple, TYPE_CHECKING

from game.core.protocols import IPostBattleShip

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.simulation.entities.ship import Ship
    from game.core.registry import GameRegistries


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
            registries: Optional GameRegistries for DI. If None, uses global fallback
                        (transitional - will be required in Phase 6).

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

        for i, instance in enumerate(self._fleet.ships):
            if not instance.is_combat_capable():
                continue

            pos = formation_positions[i] if i < len(formation_positions) else (0, 0)
            ship = instance.to_ship(pos, team_id, registries=registries)
            ships.append(ship)

        return ships

    def _default_formation_positions(
        self,
        count: int,
        team_id: int
    ) -> List[Tuple[float, float]]:
        """Generate default formation positions for ships."""
        positions = []

        # Team 0 starts on the left, Team 1 on the right
        base_x = 20000 if team_id == 0 else 80000
        base_y = 50000

        # Simple line formation
        spacing = 2000

        for i in range(count):
            y = base_y + (i - count // 2) * spacing
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
        # Build lookup for surviving ships by name
        survivors_by_name = {s.name: s for s in surviving_ships}

        # Update each ShipInstance - ships not in survivors were destroyed
        new_ships = []
        for s in self._fleet.ships:
            if s.name in survivors_by_name:
                # Update state from battle
                s.update_from_ship(survivors_by_name[s.name])
                new_ships.append(s)
            # else: ship was destroyed, don't include

        self._fleet.ships = new_ships

        # Recalculate speed (ships may have been destroyed or damaged)
        self._fleet._trigger_speed_recalculation()
