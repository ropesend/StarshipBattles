"""RamTargetResolver — PROJ-FMS-B Phase 4.

Explicit-action ramming for ships / fighters carrying ``RamTargetAbility``
and one or more ``Warhead`` components.

Flow:

    1. UI / AI calls :meth:`set_ram_target(rammer, target)` to designate.
    2. Movement AI overrides normal pathing with intercept-and-collide
       pursuit toward the target.
    3. On hull-radius intersection (collision), every ``Warhead``
       component on the rammer detonates against the target via the
       damage pipeline; the rammer is destroyed regardless of outcome.
    4. If the target dies / leaves combat before collision, the
       rammer's ``ram_target_id`` clears and it reverts to default AI.

Designs without ``RamTargetAbility`` cannot ram. ``Warhead`` components
on such ships are inert payload (still cargo).
"""
from __future__ import annotations

import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class RamTargetResolver:
    """Resolves ramming for ships carrying ``RamTargetAbility``."""

    def __init__(self, damage_calculator: Optional[Any] = None) -> None:
        self._damage_calculator = damage_calculator

    # ------------------------------------------------------------------
    # Public actions
    # ------------------------------------------------------------------

    def set_ram_target(self, rammer: Any, target: Any) -> bool:
        """Assign ``target`` as the ram target on ``rammer``.

        Returns False (without mutating state) if the rammer does not
        carry ``RamTargetAbility`` or if either ship is dead.
        """
        if not self._has_ram_ability(rammer):
            logger.debug(
                "RamTargetResolver: %s has no RamTargetAbility — cannot set target",
                getattr(rammer, "name", "?"),
            )
            return False
        if not getattr(rammer, "is_alive", True):
            return False
        if not getattr(target, "is_alive", True):
            return False
        if rammer is target:
            return False
        # Stash target id on the ability and on a top-level convenience attr.
        ability = self._get_ram_ability(rammer)
        if ability is not None:
            ability.target_id = getattr(target, "instance_id", None) or id(target)
        rammer.ram_target = target
        rammer.ram_target_id = ability.target_id if ability else None
        return True

    def clear_ram_target(self, rammer: Any) -> None:
        ability = self._get_ram_ability(rammer)
        if ability is not None:
            ability.target_id = None
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
            List of event dicts describing collisions / target-clear
            events. (Plain dicts for ergonomics; the battle engine
            wraps them into CombatEvents when present.)
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

            # Collision check.
            if self._is_collision(rammer, target):
                events.append(self._resolve_collision(rammer, target))
        return events

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _has_ram_ability(ship: Any) -> bool:
        """Walk the ship's layers looking for a RamTargetAbility instance."""
        layers = getattr(ship, "layers", {}) or {}
        for _layer_type, layer in layers.items():
            for comp in getattr(layer, "components", []) or []:
                for ability in getattr(comp, "ability_instances", []) or []:
                    if type(ability).__name__ == "RamTargetAbility":
                        return True
        return False

    @staticmethod
    def _get_ram_ability(ship: Any) -> Optional[Any]:
        layers = getattr(ship, "layers", {}) or {}
        for _layer_type, layer in layers.items():
            for comp in getattr(layer, "components", []) or []:
                for ability in getattr(comp, "ability_instances", []) or []:
                    if type(ability).__name__ == "RamTargetAbility":
                        return ability
        return None

    @staticmethod
    def _collect_warhead_damages(ship: Any) -> List[float]:
        """Sum each Warhead's damage on the rammer (one entry per warhead)."""
        damages: List[float] = []
        layers = getattr(ship, "layers", {}) or {}
        for _layer_type, layer in layers.items():
            for comp in getattr(layer, "components", []) or []:
                for ability in getattr(comp, "ability_instances", []) or []:
                    if type(ability).__name__ == "WarheadAbility":
                        damages.append(float(getattr(ability, "damage", 0.0)))
        return damages

    @staticmethod
    def _is_collision(rammer: Any, target: Any) -> bool:
        """Hull-radius intersection test."""
        if not hasattr(rammer, "position") or not hasattr(target, "position"):
            # Fall back to (x, y) coords.
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

    def _resolve_collision(self, rammer: Any, target: Any) -> dict:
        """Apply all warhead damages to ``target``; destroy ``rammer``."""
        damages = self._collect_warhead_damages(rammer)
        applied: List[float] = []
        for d in damages:
            if d <= 0:
                continue
            if self._damage_calculator is not None and hasattr(target, "layers"):
                try:
                    self._damage_calculator.apply_damage(target, d)
                    applied.append(d)
                    continue
                except Exception as exc:  # Intentional broad catch: damage pipeline can fail on minimal test ships; fall through to direct decrement so ramming still resolves.
                    logger.warning(
                        "RamTargetResolver: damage pipeline failed (%s); "
                        "falling back to direct HP decrement",
                        exc,
                    )
            # Fallback: direct HP decrement on the target.
            current = float(getattr(target, "hp", 0.0) or 0.0)
            new_hp = max(0.0, current - d)
            if hasattr(target, "hp"):
                target.hp = new_hp
            applied.append(current - new_hp)
            if new_hp <= 0.0 and hasattr(target, "is_alive"):
                target.is_alive = False

        # Destroy the rammer regardless of damage outcome.
        if hasattr(rammer, "hp"):
            rammer.hp = 0.0
        if hasattr(rammer, "is_alive"):
            rammer.is_alive = False
        self.clear_ram_target(rammer)

        return {
            "type": "ram_collision",
            "rammer": rammer,
            "target": target,
            "warheads_applied": applied,
            "total_damage": sum(applied),
        }


__all__ = ["RamTargetResolver"]
