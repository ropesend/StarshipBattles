"""ShipCombatManager -- Combat orchestration for Ship.

PROJ-240 Phase 2: Extracted from Ship god class.
Ship retains facade methods that delegate here.
"""
import logging
from typing import List, Optional, Any, TYPE_CHECKING

from game.core.math import Vector2

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.entities.ship_combat_engine import ShipCombatEngine

logger = logging.getLogger(__name__)


class ShipCombatManager:
    """Manages combat orchestration for a Ship.

    Owns:
    - The per-tick update loop (resources, components, physics, combat, firing)
    - Derelict status computation
    - Death handling
    - Combat engine lazy initialization
    - Firing state (just_fired_projectiles, comp_trigger_pulled, aim_point)

    Args:
        ship: The Ship instance this manager serves.
    """

    def __init__(self, ship: 'Ship') -> None:
        self._ship = ship
        # Combat state (moved from Ship.__init__)
        self.just_fired_projectiles: List[Any] = []
        self.total_shots_fired: int = 0
        self.comp_trigger_pulled: bool = False
        self.aim_point: Optional[Any] = None
        self._combat_engine: Optional['ShipCombatEngine'] = None

    # =========================================================================
    # Combat Engine (lazy initialization)
    # =========================================================================

    @property
    def combat_engine(self) -> 'ShipCombatEngine':
        """Get or create the ShipCombatEngine for this ship.

        Lazy initialization ensures ship is fully initialized before engine creation.
        """
        if self._combat_engine is None:
            from game.simulation.entities.ship_combat_engine import ShipCombatEngine
            self._combat_engine = ShipCombatEngine(self._ship)
        return self._combat_engine

    def set_event_bus(self, bus: Any) -> None:
        """Set the event bus on the combat engine.

        PROJ-240: Facade method to avoid 3-level delegation chain.
        BattleEngine calls ship.set_event_bus(bus) instead of
        ship.combat_engine._event_bus = bus.
        """
        self.combat_engine._event_bus = bus

    # =========================================================================
    # Death
    # =========================================================================

    def die(self) -> None:
        """Handle ship destruction. Sets ship to dead state and resets velocity."""
        logger.info(f"{self._ship.name} EXPLODED!")
        self._ship.is_alive = False
        self._ship.velocity = Vector2(0, 0)
        self._ship.recalculate_stats()

    # =========================================================================
    # Per-Tick Update Loop
    # =========================================================================

    def update(self, dt: float = 0.01, context: Optional[dict] = None) -> None:
        """Update ship state (physics, combat, resources).

        CRITICAL: The ordering of subsystem updates is load-bearing.
        Do not reorder without understanding the full implications.

        Order:
        1. Resources (regeneration) - tick-based
        2. Components (consumption, cooldowns) - tick-based
        2b. Recalculate stats (operational status changes reflected)
        3. Physics movement
        4. Combat cooldowns (shields, repair)
        5. Firing logic (if trigger pulled)
        """
        if not self._ship.is_alive:
            return

        # 1. Update Resources (Regeneration) - Tick-based
        if self._ship.resources:
            self._ship.resources.update()

        # 2. Update Components (Consumption, Cooldowns) - Tick-based
        for comp in self._ship.get_all_components():
            if comp.is_active:
                comp.update()

        # 2b. Recalculate stats after component updates so that operational
        # status changes (e.g., shield losing energy) are reflected in ship
        # stats (max_shields, current_shields) before damage is processed.
        self._ship.recalculate_stats()

        # 3. Physics (Thrust calc handling operational engines)
        # Note: update_physics_movement() handles all arcade physics:
        # - Acceleration/deceleration toward target speed
        # - Setting velocity from current_speed and heading
        # - Updating position
        # We don't call super().update() because it would apply drag and
        # update position a second time, which breaks arcade physics.
        self._ship.update_physics_movement()

        # 4. Combat Cooldowns (Shields/Repair/Custom Logic)
        self.combat_engine.update_combat_cooldowns()

        # 5. Firing Logic (Link AI trigger to Combat System)
        if self.comp_trigger_pulled:
            new_attacks = self.combat_engine.fire_weapons(context)
            if new_attacks:
                self.just_fired_projectiles.extend(new_attacks)

    # =========================================================================
    # Derelict Status
    # =========================================================================

    def update_derelict_status(self) -> None:
        """Update derelict status based on functional capability.

        A ship is derelict when it cannot fight: no operational weapons
        AND no operational engines. This is a derived flag -- the actual
        enforcement happens per-component (e.g., RequiresCommandAndControl
        marks individual components non-operational when C&C is missing).

        The crew check remains as a ship-level requirement.
        """
        ship = self._ship

        # Check 1: Crew capacity requirement (ship-level)
        crew_required = ship.get_total_ability_value('CrewRequired')

        if crew_required > 0:
            crew_capacity = ship.get_total_ability_value('CrewCapacity')

            if crew_required > crew_capacity:
                if not ship.is_derelict:
                    logger.info(
                        f"{ship.name} has become DERELICT "
                        f"(Insufficient crew capacity)"
                    )
                ship.is_derelict = True
                return

        # Check 2: Functional capability -- can the ship fight?
        has_weapons = len(
            ship.get_components_by_ability('WeaponAbility', operational_only=True)
        ) > 0
        has_engines = len(
            ship.get_components_by_ability('CombatPropulsion', operational_only=True)
        ) > 0

        was_derelict = ship.is_derelict
        ship.is_derelict = not has_weapons and not has_engines

        if ship.is_derelict and not was_derelict:
            logger.info(
                f"{ship.name} has become DERELICT "
                f"(no operational weapons or engines)"
            )
        elif not ship.is_derelict and was_derelict:
            logger.info(f"{ship.name} is no longer derelict")

        ship.bridge_destroyed = False
