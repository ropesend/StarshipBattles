"""
DamageCalculator - Extracted damage logic from ShipCombatEngine.

This class handles all damage-related operations:
- Shield absorption
- Emissive armor reduction
- Shield Regenerating Armor absorption and shield recharge
- Hull layer damage distribution

Emits combat events at each pipeline stage when an event bus is provided.

Part of PROJ-44 Phase 5: ShipCombatEngine Decomposition.
"""
import random
from typing import Optional, TYPE_CHECKING

from game.core.constants import LayerType
from game.simulation.combat.combat_events import (
    CombatEvent,
    CombatEventType,
)

if TYPE_CHECKING:
    from game.simulation.entities.ship import Ship
    from game.simulation.combat.combat_events import CombatEventBus
    from game.core.combat_types import DamageContext


class DamageCalculator:
    """
    Handles all damage-related logic for combat.

    Extracted from ShipCombatEngine to focus on single responsibility:
    applying damage to ships through various defensive layers.

    Accepts an optional RNG instance for deterministic damage distribution (PROJ-252).
    """

    def __init__(self, rng: 'random.Random' = None):
        self.rng: random.Random = rng if rng is not None else random.Random()

    def apply_damage(
        self,
        ship: 'Ship',
        damage_amount: float,
        context: Optional['DamageContext'] = None,
        event_bus: Optional['CombatEventBus'] = None
    ) -> None:
        """
        Apply damage to the ship.

        Damage pipeline:
        1. Shields (absorb from shield pool)
        2. Emissive armor (flat reduction on overflow)
        3. Shield Regenerating Armor (absorb overflow + recharge shields)
        4. Hull layers (outer to inner)

        Args:
            ship: The ship to apply damage to
            damage_amount: Amount of damage to apply
            context: Attacker identity for event emission
            event_bus: Event bus for combat events
        """
        if not ship.is_alive or damage_amount <= 0:
            return

        was_derelict = ship.is_derelict
        remaining = damage_amount

        remaining = self._absorb_shields(ship, remaining, context, event_bus)
        if remaining <= 0:
            return
        remaining = self._reduce_emissive_armor(ship, remaining, context, event_bus)
        if remaining <= 0:
            return
        remaining = self._absorb_regenerating_armor(ship, remaining, context, event_bus)
        if remaining <= 0:
            return
        remaining = self._distribute_hull_damage(ship, remaining, context, event_bus)

        self._finalize_damage(ship, damage_amount, remaining, was_derelict, context, event_bus)

    # -- pipeline stages --------------------------------------------------

    @staticmethod
    def _absorb_shields(ship, damage, context, event_bus):
        """Stage 1: Absorb damage from shield pool."""
        if ship.current_shields <= 0:
            return damage
        absorbed = min(ship.current_shields, damage)
        ship.current_shields -= absorbed
        damage -= absorbed
        if event_bus and absorbed > 0:
            event_bus.emit(CombatEvent(
                event_type=CombatEventType.SHIELD_HIT,
                target_ship=ship,
                damage_amount=absorbed,
                context=context,
                shield_remaining=ship.current_shields,
            ))
        return damage

    @staticmethod
    def _reduce_emissive_armor(ship, damage, context, event_bus):
        """Stage 2: Flat damage reduction from emissive armor."""
        ea = ship.emissive_armor
        if ea <= 0:
            return damage
        ea_absorbed = min(ea, damage)
        damage = max(0, damage - ea)
        if event_bus and ea_absorbed > 0:
            event_bus.emit(CombatEvent(
                event_type=CombatEventType.ARMOR_ABSORBED,
                target_ship=ship,
                damage_amount=ea_absorbed,
                context=context,
            ))
        return damage

    @staticmethod
    def _absorb_regenerating_armor(ship, damage, context, event_bus):
        """Stage 3: SRA absorbs overflow and recharges shields."""
        sra = ship.shield_regenerating_armor
        if sra <= 0:
            return damage
        absorption = min(sra, damage)
        damage -= absorption
        if ship.max_shields > 0:
            ship.current_shields = min(ship.max_shields, ship.current_shields + absorption)
        if event_bus and absorption > 0:
            event_bus.emit(CombatEvent(
                event_type=CombatEventType.ARMOR_ABSORBED,
                target_ship=ship,
                damage_amount=absorption,
                context=context,
            ))
        return damage

    def _distribute_hull_damage(self, ship, damage, context, event_bus):
        """Stage 4: Distribute remaining damage across hull layers (outer first)."""
        sorted_layers = sorted(
            ship.layers.items(),
            key=lambda x: x[1].radius_pct,
            reverse=True,
        )
        for ltype, layer_data in sorted_layers:
            if damage <= 0:
                break
            damage = self._damage_layer(ship, ltype, damage, context, event_bus)
        return damage

    @staticmethod
    def _finalize_damage(ship, original_damage, remaining, was_derelict, context, event_bus):
        """Stage 5: Recalculate stats and emit derelict event if needed.

        PROJ-253: Uses recalculate_stats_if_dirty() — the dirty flag is already
        set by component_health_manager.take_damage() when hull components are hit.
        Shield-only damage doesn't change component state, so the pipeline is skipped.
        """
        if remaining >= original_damage:
            return  # No damage was actually applied
        ship.recalculate_stats_if_dirty()
        ship.update_derelict_status()
        if event_bus and not was_derelict and ship.is_derelict:
            event_bus.emit(CombatEvent(
                event_type=CombatEventType.SHIP_DERELICT,
                target_ship=ship,
                context=context,
            ))

        # HP death check — ship at 0 HP is destroyed and removed from combat
        ship_hp = getattr(ship, 'hp', None)
        if isinstance(ship_hp, (int, float)) and ship_hp <= 0 and ship.is_alive:
            ship.is_alive = False
            if event_bus:
                event_bus.emit(CombatEvent(
                    event_type=CombatEventType.SHIP_DESTROYED,
                    target_ship=ship,
                    context=context,
                ))

    def _damage_layer(
        self,
        ship: 'Ship',
        layer_type: LayerType,
        damage: float,
        context: Optional['DamageContext'] = None,
        event_bus: Optional['CombatEventBus'] = None
    ) -> float:
        """
        Apply damage to a specific layer.

        Uses weighted random selection based on component HP.

        Args:
            ship: The ship being damaged
            layer_type: The layer to damage
            damage: Amount of damage to apply
            context: Attacker identity for events
            event_bus: Event bus for combat events

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
            target = self.rng.choices(targets, weights=weights, k=1)[0]

            damage_absorbed = min(target.current_hp, damage)
            target.take_damage(damage_absorbed)
            damage -= damage_absorbed

            if event_bus:
                if target.current_hp <= 0:
                    event_bus.emit(CombatEvent(
                        event_type=CombatEventType.COMPONENT_DESTROYED,
                        target_ship=ship,
                        damage_amount=damage_absorbed,
                        context=context,
                        component=target,
                        layer_type=layer_type,
                    ))
                else:
                    event_bus.emit(CombatEvent(
                        event_type=CombatEventType.COMPONENT_HIT,
                        target_ship=ship,
                        damage_amount=damage_absorbed,
                        context=context,
                        component=target,
                        layer_type=layer_type,
                    ))

        return damage
