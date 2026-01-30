"""
ShipCombatEngine - Combat coordinator for Ship class.

This class coordinates all combat-related operations for a ship by
delegating to focused subsystems:
- TargetingSystem: Target selection and firing solutions
- DamageCalculator: Damage application and absorption
- WeaponFiringSystem: Weapon firing and projectile creation

The engine itself handles only:
- Combat cooldown management (shield regen, repair)
- Coordination between subsystems

Part of PROJ-12 God Class Decomposition.
Refactored in PROJ-44 Phase 5: ShipCombatEngine Decomposition.
"""
from typing import TYPE_CHECKING, List, Optional, Any

from game.core.constants import CombatConstants
from game.simulation.combat.targeting_system import TargetingSystem
from game.simulation.combat.damage_calculator import DamageCalculator
from game.simulation.combat.weapon_firing_system import WeaponFiringSystem
from game.simulation.components.component_constants import ComponentStatus

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


class ShipCombatEngine:
    """
    Coordinates all combat-related logic for a ship.

    Delegates targeting, damage, and weapon firing to focused subsystems
    while maintaining combat cooldown management.
    """

    # Shared instances for subsystems (stateless, can be shared)
    _targeting_system: Optional[TargetingSystem] = None
    _damage_calculator: Optional[DamageCalculator] = None
    _weapon_firing_system: Optional[WeaponFiringSystem] = None

    def __init__(self, ship: 'Ship'):
        """
        Initialize combat engine for a ship.

        Args:
            ship: The ship this engine controls combat for
        """
        self._ship = ship

        # Initialize shared subsystems on first use
        if ShipCombatEngine._targeting_system is None:
            ShipCombatEngine._targeting_system = TargetingSystem()
        if ShipCombatEngine._damage_calculator is None:
            ShipCombatEngine._damage_calculator = DamageCalculator()
        if ShipCombatEngine._weapon_firing_system is None:
            ShipCombatEngine._weapon_firing_system = WeaponFiringSystem(
                ShipCombatEngine._targeting_system
            )

    # =========================================================================
    # Delegated Methods - Targeting
    # =========================================================================

    def solve_lead(self, pos, vel, t_pos, t_vel, p_speed) -> float:
        """
        Calculate interception time for a projectile.

        Delegates to TargetingSystem.

        Args:
            pos: Shooter position
            vel: Shooter velocity
            t_pos: Target position
            t_vel: Target velocity
            p_speed: Projectile speed

        Returns:
            Interception time t > 0 if solution exists, else 0
        """
        return self._targeting_system.solve_lead(pos, vel, t_pos, t_vel, p_speed)

    def select_target(self, candidates: List[Any]) -> Optional[Any]:
        """
        Select the best target from a list of candidates.

        Delegates to TargetingSystem.

        Args:
            candidates: List of potential targets

        Returns:
            Best target or None if no valid targets
        """
        return self._targeting_system.select_target(self._ship, candidates)

    def calculate_firing_solution(self, comp, target):
        """
        Calculate aim position and vector for firing at a target.

        Delegates to TargetingSystem.

        Args:
            comp: The weapon component
            target: The target to fire at

        Returns:
            Tuple of (aim_position, aim_vector)
        """
        return self._targeting_system.calculate_firing_solution(self._ship, comp, target)

    # =========================================================================
    # Delegated Methods - Weapon Firing
    # =========================================================================

    def fire_weapons(self, context: Optional[dict] = None) -> List[Any]:
        """
        Fire all ready weapons at available targets.

        Delegates to WeaponFiringSystem.

        Args:
            context: Optional context dict with projectiles list for PDC targeting

        Returns:
            List of attack objects (Projectiles or beam attack dicts)
        """
        return self._weapon_firing_system.fire_weapons(self._ship, context)

    # =========================================================================
    # Delegated Methods - Damage
    # =========================================================================

    def take_damage(self, damage_amount: float) -> None:
        """
        Apply damage to the ship.

        Delegates to DamageCalculator.

        Args:
            damage_amount: Amount of damage to apply
        """
        self._damage_calculator.apply_damage(self._ship, damage_amount)

    # =========================================================================
    # Combat Cooldowns (kept in engine as ship-specific state management)
    # =========================================================================

    def update_combat_cooldowns(self) -> None:
        """
        Update weapon cooldowns and shield/energy regeneration.

        Called each tick to handle:
        - Shield regeneration
        - Repair application
        """
        ship = self._ship

        if not ship.is_alive:
            return

        # Regenerate Shield
        if ship.current_shields < ship.max_shields and ship.shield_regen_rate > 0:
            regen_amount = ship.shield_regen_rate / 100.0
            cost_amount = ship.shield_regen_cost / 100.0

            has_energy = True
            if cost_amount > 0 and hasattr(ship, 'resources'):
                energy_res = ship.resources.get_resource('energy')
                if energy_res:
                    if energy_res.current_value >= cost_amount:
                        energy_res.consume(cost_amount)
                    else:
                        has_energy = False

            if has_energy:
                ship.current_shields += regen_amount
                if ship.current_shields > ship.max_shields:
                    ship.current_shields = ship.max_shields

        # Apply Ship Repair
        if getattr(ship, 'repair_rate', 0) > 0:
            self._apply_repair(ship.repair_rate / 100.0)

    def _apply_repair(self, repair_amount: float) -> None:
        """
        Apply structural repair to damaged components.

        Args:
            repair_amount: Amount of HP to repair per tick
        """
        ship = self._ship

        if repair_amount <= 0:
            return

        damaged_candidates = [
            c for c in ship.get_all_components()
            if 0 < c.current_hp < c.max_hp
        ]

        if not damaged_candidates:
            return

        # Repair the most damaged (relative) component
        damaged_candidates.sort(key=lambda c: c.current_hp / c.max_hp)
        target = damaged_candidates[0]

        missing = target.max_hp - target.current_hp
        amount_to_apply = min(missing, repair_amount)
        target.current_hp += amount_to_apply

        # Restore status if HP above threshold
        if not target.is_active:
            if target.current_hp > (target.max_hp * CombatConstants.DEFAULT_DAMAGE_THRESHOLD):
                target.is_active = True
                target.status = ComponentStatus.ACTIVE
