"""RamTargetResolver — symmetric ramming model (QA 2026-05-16 Obs 1b).

Ramming is a universal tactical action: any moving vehicle can be
assigned a ram target via :meth:`set_ram_target(rammer, target)`.
There is no ``RamTargetAbility`` / ``ram_target_module`` gate — the
component-gated model from PROJ-FMS-B was replaced after user feedback
on 2026-05-16. Kamikaze fighters express ram intent by having the
AI controller call ``set_ram_target`` on spawn.

Flow:

    1. UI / AI calls :meth:`set_ram_target(rammer, target)`.
    2. The rammer's movement code (FighterAIController kamikaze flow,
       or a player tactical override) drives the rammer toward the
       target.
    3. On hull-radius intersection (collision), BOTH ships exchange
       damage simultaneously:

           rammer_delivered = rammer.current_shields + rammer.hp +
                              sum(warhead.damage on rammer)
           target_delivered = target.current_shields + target.hp +
                              sum(warhead.damage on target)

       Values are sampled at collision instant so the rammer's state
       going to zero does not reduce the damage it delivers.
    4. All warheads on both sides are consumed (one-shot, mirroring
       ``consume_on_fire`` for beam laserheads).
    5. The rammer's ``ram_target`` is cleared after collision so a
       survivor does not auto-re-collide on the next tick.

Survival is possible: a heavy target with ample shields/HP ramming a
fighter eats little; a kamikaze fighter ramming a dreadnought is
annihilated but does big damage if it carries warheads.
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class RamTargetResolver:
    """Resolves ramming events with symmetric simultaneous damage."""

    def __init__(self, damage_calculator: Optional[Any] = None) -> None:
        self._damage_calculator = damage_calculator

    # ------------------------------------------------------------------
    # Public actions
    # ------------------------------------------------------------------

    def set_ram_target(self, rammer: Any, target: Any) -> bool:
        """Assign ``target`` as the ram target on ``rammer``.

        Returns False (without mutating state) when either ship is dead
        or when ``rammer is target``. Unlike the pre-2026-05-16 model,
        no component / ability check is performed — any vehicle can be
        assigned a ram target.
        """
        if not getattr(rammer, "is_alive", True):
            return False
        if not getattr(target, "is_alive", True):
            return False
        if rammer is target:
            return False
        rammer.ram_target = target
        rammer.ram_target_id = (
            getattr(target, "instance_id", None) or id(target)
        )
        return True

    def clear_ram_target(self, rammer: Any) -> None:
        if hasattr(rammer, "ram_target"):
            rammer.ram_target = None
        if hasattr(rammer, "ram_target_id"):
            rammer.ram_target_id = None

    # ------------------------------------------------------------------
    # Per-tick processing — called by BattleEngine
    # ------------------------------------------------------------------

    def process_ramming_tick(self, ships: List[Any]) -> List[dict]:
        """Resolve ramming for the current tick.

        Returns:
            List of event dicts describing ``ram_collision`` /
            ``ram_target_cleared`` events.
        """
        events: List[dict] = []
        for rammer in list(ships):
            if not getattr(rammer, "is_alive", True):
                continue
            target = getattr(rammer, "ram_target", None)
            if target is None:
                continue
            if not getattr(target, "is_alive", True):
                self.clear_ram_target(rammer)
                events.append({
                    "type": "ram_target_cleared",
                    "rammer": rammer,
                    "reason": "target_dead",
                })
                continue

            if self._is_collision(rammer, target):
                events.append(self._resolve_collision(rammer, target))
        return events

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _collect_warheads(ship: Any) -> List[Any]:
        """Return the live ``WarheadAbility`` instances on ``ship``
        (skipping any already marked consumed)."""
        warheads: List[Any] = []
        layers = getattr(ship, "layers", {}) or {}
        for _layer_type, layer in layers.items():
            for comp in getattr(layer, "components", []) or []:
                for ability in getattr(comp, "ability_instances", []) or []:
                    if type(ability).__name__ != "WarheadAbility":
                        continue
                    if getattr(ability, "consumed", False):
                        continue
                    warheads.append(ability)
        return warheads

    @staticmethod
    def _delivered_damage(ship: Any, warheads: List[Any]) -> float:
        """Sum kinetic (shields + HP) + warhead-yield contributions."""
        shields = float(getattr(ship, "current_shields", 0.0) or 0.0)
        hp = float(getattr(ship, "hp", 0.0) or 0.0)
        warhead_damage = sum(
            float(getattr(w, "damage", 0.0) or 0.0) for w in warheads
        )
        return shields + hp + warhead_damage

    @staticmethod
    def _is_collision(rammer: Any, target: Any) -> bool:
        """Hull-radius intersection test."""
        if not hasattr(rammer, "position") or not hasattr(target, "position"):
            rx = float(getattr(rammer, "x", 0.0))
            ry = float(getattr(rammer, "y", 0.0))
            tx = float(getattr(target, "x", 0.0))
            ty = float(getattr(target, "y", 0.0))
            rr = float(getattr(rammer, "radius", 1.0))
            tr = float(getattr(target, "radius", 1.0))
            dx, dy = tx - rx, ty - ry
            return (dx * dx + dy * dy) < (rr + tr) ** 2
        return rammer.position.distance_to(target.position) < (
            float(getattr(rammer, "radius", 1.0))
            + float(getattr(target, "radius", 1.0))
        )

    def _apply_damage(self, victim: Any, amount: float) -> None:
        """Route damage through the calculator when present; fall back
        to direct HP decrement (drains current_shields first when the
        attribute exists). Used by both sides of the symmetric
        exchange."""
        if amount <= 0:
            return
        if self._damage_calculator is not None and hasattr(victim, "layers"):
            try:
                self._damage_calculator.apply_damage(victim, amount)
                return
            except Exception as exc:  # Intentional broad catch: damage pipeline can fail on minimal test ships; fall through to direct decrement so the symmetric exchange still resolves.
                logger.warning(
                    "RamTargetResolver: damage pipeline failed (%s); "
                    "falling back to direct HP decrement",
                    exc,
                )
        # Fallback: drain shields first, then HP.
        remaining = amount
        if hasattr(victim, "current_shields"):
            shields = float(getattr(victim, "current_shields", 0.0) or 0.0)
            absorbed = min(shields, remaining)
            victim.current_shields = max(0.0, shields - absorbed)
            remaining -= absorbed
        if remaining <= 0:
            return
        current_hp = float(getattr(victim, "hp", 0.0) or 0.0)
        new_hp = max(0.0, current_hp - remaining)
        if hasattr(victim, "hp"):
            victim.hp = new_hp
        if new_hp <= 0.0 and hasattr(victim, "is_alive"):
            victim.is_alive = False

    def _resolve_collision(self, rammer: Any, target: Any) -> dict:
        """Apply symmetric simultaneous damage; consume warheads on
        both sides; clear the rammer's target."""
        # 1. Snapshot BOTH sides' state before any damage is applied so
        # the rammer's destruction does not reduce its delivered damage
        # and vice versa.
        rammer_warheads = self._collect_warheads(rammer)
        target_warheads = self._collect_warheads(target)
        rammer_delivered = self._delivered_damage(rammer, rammer_warheads)
        target_delivered = self._delivered_damage(target, target_warheads)

        # 2. Apply both deliveries in parallel (sampled-before-applied).
        self._apply_damage(target, rammer_delivered)
        self._apply_damage(rammer, target_delivered)

        # 3. Consume all warheads on both sides (one-shot).
        for wh in rammer_warheads:
            wh.consumed = True
            wh.damage = 0.0
        for wh in target_warheads:
            wh.consumed = True
            wh.damage = 0.0

        # 4. Clear ram_target on the rammer regardless of survival so
        # a survivor does not re-collide next tick.
        self.clear_ram_target(rammer)

        return {
            "type": "ram_collision",
            "rammer": rammer,
            "target": target,
            "rammer_delivered": rammer_delivered,
            "target_delivered": target_delivered,
        }


__all__ = ["RamTargetResolver"]
