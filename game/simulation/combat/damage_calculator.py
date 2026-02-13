"""
DamageCalculator - Extracted damage logic from ShipCombatEngine.

This class handles all damage-related operations:
- Emissive armor reduction
- Crystalline armor absorption and shield recharge
- Shield absorption
- Hull layer damage distribution

Part of PROJ-44 Phase 5: ShipCombatEngine Decomposition.
"""
import random
from typing import TYPE_CHECKING

from game.core.constants import LayerType

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship


class DamageCalculator:
    """
    Handles all damage-related logic for combat.

    Extracted from ShipCombatEngine to focus on single responsibility:
    applying damage to ships through various defensive layers.
    """

    def apply_damage(self, ship: 'Ship', damage_amount: float) -> None:
        """
        Apply damage to the ship.

        Processes damage through:
        1. Emissive armor (flat reduction)
        2. Crystalline armor (absorption + shield recharge)
        3. Shields
        4. Hull layers (outer to inner)

        Args:
            ship: The ship to apply damage to
            damage_amount: Amount of damage to apply
        """
        if not ship.is_alive:
            return

        # Apply Emissive Armor Reduction (Flat reduction per hit)
        ea = ship.emissive_armor
        if ea > 0:
            damage_amount = max(0, damage_amount - ea)
            if damage_amount <= 0:
                return

        # Apply Crystalline Armor (Absorb and Recharge Shields)
        ca = ship.crystalline_armor
        if ca > 0 and damage_amount > 0:
            absorption = min(ca, damage_amount)
            damage_amount -= absorption

            # Recharge shields
            if ship.max_shields > 0:
                ship.current_shields = min(
                    ship.max_shields,
                    ship.current_shields + absorption
                )

            if damage_amount <= 0:
                return

        remaining_damage = damage_amount

        # Shield Absorption
        if ship.current_shields > 0:
            absorbed = min(ship.current_shields, remaining_damage)
            ship.current_shields -= absorbed
            remaining_damage -= absorbed

        # Dynamic Layer Order: Sort by radius_pct descending (Outermost first)
        sorted_layers = sorted(
            ship.layers.items(),
            key=lambda x: x[1].radius_pct,
            reverse=True
        )

        for ltype, layer_data in sorted_layers:
            if remaining_damage <= 0:
                break
            remaining_damage = self._damage_layer(ship, ltype, remaining_damage)

        if remaining_damage < damage_amount:
            ship.recalculate_stats()
            ship.update_derelict_status()

    def _damage_layer(
        self,
        ship: 'Ship',
        layer_type: LayerType,
        damage: float
    ) -> float:
        """
        Apply damage to a specific layer.

        Uses weighted random selection based on component HP.

        Args:
            ship: The ship being damaged
            layer_type: The layer to damage
            damage: Amount of damage to apply

        Returns:
            Remaining damage after layer absorption
        """
        layer = ship.layers[layer_type]

        while damage > 0:
            # Filter for components with HP > 0
            targets = [c for c in layer.components if c.current_hp > 0]

            if not targets:
                break

            # Weighted random selection based on current HP
            weights = [c.current_hp for c in targets]
            target = random.choices(targets, weights=weights, k=1)[0]

            damage_absorbed = min(target.current_hp, damage)
            target.take_damage(damage_absorbed)
            damage -= damage_absorbed

        return damage
