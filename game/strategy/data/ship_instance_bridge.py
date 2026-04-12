"""
ShipInstanceBridge - Simulation bridge for ShipInstance.

Handles conversion between strategy-layer ShipInstance and simulation-layer Ship.
Extracted from ShipInstance to separate cross-layer bridge logic.

Late imports of ShipSerializer are intentional to avoid circular deps across
the strategy/simulation boundary. See docs/01_ARCHITECTURE.md.

PROJ-234: Extracted as part of ShipInstance god object decomposition.
"""
import logging
from typing import Dict, Tuple, TYPE_CHECKING

from game.core.protocols import IPostBattleShip

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance
    from game.simulation.entities.ship import Ship
    from game.core.registry import GameRegistries

logger = logging.getLogger(__name__)


class ShipInstanceBridge:
    """
    Bridges ShipInstance (strategy) with Ship (simulation).

    Handles:
    - to_ship: Create simulation Ship from strategy ShipInstance
    - update_from_ship: Update ShipInstance from post-battle Ship state
    """

    def __init__(self, ship_instance: 'ShipInstance') -> None:
        self._ship = ship_instance

    @staticmethod
    def _capture_resource_levels(ship: IPostBattleShip) -> Dict[str, float]:
        """Extract all resource levels from a post-battle Ship."""
        levels: Dict[str, float] = {}
        if ship.resources:
            for name in ship.resources.get_resource_names():
                levels[name] = ship.resources.get_value(name)
        return levels

    def to_ship(
        self,
        position: Tuple[float, float],
        team_id: int,
        *,
        registries: 'GameRegistries'
    ) -> 'Ship':
        """
        Create a simulation Ship from the owning ShipInstance.

        Applies any existing damage/resource state from strategy layer.

        Args:
            position: (x, y) spawn position for the ship
            team_id: Team assignment for battle (0 or 1)
            registries: GameRegistries for DI (required).
        """
        # INTENTIONAL LATE IMPORT: Cross-layer boundary (strategy -> simulation)
        # See docs/01_ARCHITECTURE.md "Intentional Late Imports" section
        from game.simulation.entities.ship_serialization import ShipSerializer
        from game.strategy.data.component_state import component_state_key

        # Create ship from design data
        ship = ShipSerializer.from_dict(self._ship.design_data, registries=registries)

        # Set position, team, and strategy-layer identity
        ship.x, ship.y = position
        ship.team_id = team_id
        ship.instance_id = self._ship.instance_id  # PROJ-254: Thread ID for battle reconciliation

        # Apply HP damage if tracked
        if self._ship.current_hp is not None:
            damage = ship.max_hp - self._ship.current_hp
            if damage > 0:
                logger.debug(
                    f"Ship {self._ship.name} entering battle with {damage} damage pre-applied"
                )
                ship.combat_engine.take_damage(damage)

        # PROJ-269 Phase 2: prefer per-instance component HP from
        # `ShipInstance.components` when populated — disambiguates
        # identical components by `instance_index`. Falls back to the
        # legacy `component_damage` dict (single-instance granularity)
        # when `components` is empty (legacy saves, pre-Phase-2 code).
        if self._ship.components:
            per_id_index: Dict[str, int] = {}
            for layer_data in ship.layers.values():
                for comp in layer_data.components:
                    idx = per_id_index.get(comp.id, 0)
                    per_id_index[comp.id] = idx + 1
                    key = component_state_key(comp.id, idx)
                    cs = self._ship.components.get(key)
                    if cs is None:
                        continue
                    target_hp = cs.current_hp
                    damage = comp.current_hp - target_hp
                    if damage > 0:
                        comp.take_damage(int(damage))
        else:
            # Apply component-specific damage (legacy path)
            for comp_id, target_hp in self._ship.component_damage.items():
                for layer_type, layer_data in ship.layers.items():
                    for comp in layer_data.components:
                        if comp.id == comp_id:
                            damage = comp.current_hp - target_hp
                            if damage > 0:
                                comp.take_damage(damage)

        # Apply resource levels
        if ship.resources:
            for resource_name, current in self._ship.consumable_levels.items():
                ship.resources.set_value(resource_name, current)

        # Recalculate stats after applying damage
        ship.recalculate_stats()

        return ship

    def update_from_ship(self, ship: IPostBattleShip) -> None:
        """
        Update the owning ShipInstance from post-battle ship state.

        Called after strategy battle resolution to persist damage/resource changes.
        """
        from game.strategy.data.component_state import ComponentState, component_state_key

        # Update HP state
        if ship.is_alive:
            if ship.hp < ship.max_hp:
                self._ship.current_hp = ship.hp
            else:
                self._ship.current_hp = None  # Full health
            self._ship.is_alive = True
        else:
            self._ship.is_alive = False
            self._ship.current_hp = 0

        self._ship.is_derelict = ship.is_derelict

        # Update component damage (legacy — single-instance granularity)
        self._ship.component_damage.clear()
        # PROJ-269 Phase 2: rebuild `components` authoritatively from the
        # engine's per-instance state. Walks ship layers and emits one
        # ComponentState per component instance with the final HP.
        rebuilt_components: Dict[str, ComponentState] = {}
        per_id_index: Dict[str, int] = {}
        for layer_type, layer_data in ship.layers.items():
            for comp in layer_data.components:
                # Legacy `component_damage` mirror (first instance wins,
                # matches pre-Phase-2 behavior).
                if comp.current_hp < comp.max_hp and comp.id not in self._ship.component_damage:
                    self._ship.component_damage[comp.id] = comp.current_hp

                idx = per_id_index.get(comp.id, 0)
                per_id_index[comp.id] = idx + 1
                key = component_state_key(comp.id, idx)
                rebuilt_components[key] = ComponentState(
                    component_id=comp.id,
                    instance_index=idx,
                    current_hp=float(comp.current_hp),
                    is_active=bool(getattr(comp, "is_active", True)),
                )

        self._ship.components = rebuilt_components

        # Update resource levels
        self._ship.consumable_levels = self._capture_resource_levels(ship)

        # Update battle stats
        self._ship.battles_survived += 1

        # Invalidate stats cache (damage changed)
        self._ship.invalidate_stats_cache()
