"""
ShipCombatMixin - Thin facade for ship combat operations.

This mixin delegates to ShipCombatEngine for actual implementation.
Maintained for backward compatibility during PROJ-12 transition.

PROJ-12: God Class Decomposition - Phase 1
"""
import math
from typing import Optional, List, Any

from game.core.math import Vector2
from game.core.logger import log_info


class ShipCombatMixin:
    """
    Mixin class handling ship combat (firing, taking damage).

    This is now a thin facade that delegates to ShipCombatEngine.
    Kept for backward compatibility - the Ship class inherits this mixin.

    The combat_engine property is lazily initialized on first access.
    """

    @property
    def combat_engine(self):
        """
        Get or create the ShipCombatEngine for this ship.

        Lazy initialization to avoid import cycles and ensure ship
        is fully initialized before engine creation.
        """
        if not hasattr(self, '_combat_engine') or self._combat_engine is None:
            from game.simulation.entities.ship_combat_engine import ShipCombatEngine
            self._combat_engine = ShipCombatEngine(self)
        return self._combat_engine

    def update_combat_cooldowns(self) -> None:
        """
        Update weapon cooldowns and energy regeneration.

        Delegates to ShipCombatEngine.update_combat_cooldowns().
        """
        self.combat_engine.update_combat_cooldowns()

    def fire_weapons(self, context: Optional[dict] = None) -> List[Any]:
        """
        Fire all ready weapons at available targets.

        Delegates to ShipCombatEngine.fire_weapons().

        Args:
            context: Optional context dict with projectiles list for PDC targeting

        Returns:
            List of attack objects (Projectiles or beam attack dicts)
        """
        return self.combat_engine.fire_weapons(context)

    def take_damage(self, damage_amount: float) -> None:
        """
        Apply damage to the ship.

        Delegates to ShipCombatEngine.take_damage().

        Args:
            damage_amount: Amount of damage to apply
        """
        self.combat_engine.take_damage(damage_amount)

    def solve_lead(self, pos, vel, t_pos, t_vel, p_speed) -> float:
        """
        Calculate interception time for a projectile.

        Delegates to ShipCombatEngine.solve_lead().

        Args:
            pos: Shooter position
            vel: Shooter velocity
            t_pos: Target position
            t_vel: Target velocity
            p_speed: Projectile speed

        Returns:
            Interception time t > 0 if solution exists, else 0
        """
        return self.combat_engine.solve_lead(pos, vel, t_pos, t_vel, p_speed)

    def _calculate_firing_solution(self, comp, target):
        """
        Calculate aim position and vector for firing at a target.

        Delegates to ShipCombatEngine.calculate_firing_solution().

        Args:
            comp: The weapon component
            target: The target to fire at

        Returns:
            Tuple of (aim_position, aim_vector)
        """
        return self.combat_engine.calculate_firing_solution(comp, target)

    def _find_pdc_target(self, comp, context):
        """
        Find the best target for a Point Defense Cannon.

        Note: This method is kept for backward compatibility but may
        be deprecated in future versions.

        Args:
            comp: PDC weapon component
            context: Context dict containing projectiles list

        Returns:
            Best PDC target or None
        """
        projectiles = context.get('projectiles', [])
        if not projectiles:
            return None

        # Get weapon ability for range check
        weapon_range = 0
        if hasattr(comp, 'get_ability'):
            weapon_ab = comp.get_ability('WeaponAbility')
            weapon_range = weapon_ab.range if weapon_ab else 0
        else:
            weapon_range = getattr(comp, 'range', 0)

        possible_targets = []
        for p in projectiles:
            if not p.is_alive:
                continue
            if getattr(p, 'team_id', -1) == self.team_id:
                continue

            dist = self.position.distance_to(p.position)
            if dist > weapon_range:
                continue

            possible_targets.append((p, dist))

        if not possible_targets:
            return None

        possible_targets.sort(key=lambda x: x[1])
        return possible_targets[0][0]

    def die(self) -> None:
        """
        Handle ship destruction.

        Sets ship to dead state and resets velocity.
        """
        log_info(f"{self.name} EXPLODED!")
        self.is_alive = False
        self.velocity = Vector2(0, 0)
        self.recalculate_stats()

    def _damage_layer(self, layer_type, damage: float) -> float:
        """
        Apply damage to a specific layer.

        Delegates to ShipCombatEngine._damage_layer().

        Args:
            layer_type: The layer to damage
            damage: Amount of damage to apply

        Returns:
            Remaining damage after layer absorption
        """
        return self.combat_engine._damage_layer(layer_type, damage)

    def _apply_repair(self, repair_amount: float) -> None:
        """
        Apply structural repair to damaged components.

        Delegates to ShipCombatEngine._apply_repair().

        Args:
            repair_amount: Amount of HP to repair per tick
        """
        self.combat_engine._apply_repair(repair_amount)
