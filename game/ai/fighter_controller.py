"""FighterAIController — PROJ-FMS-C Phase 2.

Minimal "target nearest enemy" AI controller for tactical fighters.

Why a dedicated controller?
    Fighters launched into a battle via :meth:`BattleEngine.launch_fighters_in_battle`
    (PROJ-FMS-C Phase 1) and fighters spawned from a participating
    ``fighter_group`` Fleet (Phase 2) are small, fragile, fire-and-forget
    combat entities. The full :class:`AIController` policy machinery
    (retreat thresholds, formation logic, sniper/brawler/anti-fighter
    policy trees) is overkill — a wing of three Talons that hide behind
    cover when they hit 10% HP feels wrong. Fighters want one
    behavior: pick the nearest enemy, turn toward it, thrust, fire
    when in range / cooldown allows.

Kamikaze fighters with :class:`RamTargetAbility` follow the engine's
:class:`RamTargetResolver` (PROJ-FMS-B audit Fix 3) instead — when
``set_ram_target`` has been called, this controller short-circuits its
movement update so the resolver's intercept-and-pursue path can run
without interference.
"""
from __future__ import annotations

import logging
import random
from typing import Any, Optional, TYPE_CHECKING

from game.ai.controller import AIController

if TYPE_CHECKING:
    from game.ai.interfaces.controllable import ShipControllableAdapter
    from game.engine.spatial import SpatialGrid

logger = logging.getLogger(__name__)


class FighterAIController(AIController):
    """Lightweight per-tick AI controller for tactical fighter ships.

    Behavior:
        1. Find the nearest live enemy via the spatial grid.
        2. Set it as the current target so the ship's weapon firing
           system fires on it via the existing pipeline.
        3. Turn toward it.
        4. Thrust forward when reasonably aligned.
        5. When a :class:`RamTargetAbility` has its ``target_id`` set,
           defer movement to the engine's :class:`RamTargetResolver`
           (the resolver handles intercept-and-pursue).
        6. When no enemies are visible, idle in place.
    """

    def __init__(
        self,
        ship: 'ShipControllableAdapter',
        grid: 'SpatialGrid',
        enemy_team_id: int,
        *,
        rng: Optional[random.Random] = None,
    ) -> None:
        super().__init__(ship, grid, enemy_team_id, rng=rng)

    def update(self) -> None:
        """Run one fighter-AI cycle.

        Stages (in order):
          - Liveness check.
          - Default throttle setup.
          - Kamikaze short-circuit: if a ram target is set, defer to
            the engine's RamTargetResolver.
          - Nearest-enemy acquisition; idle when none.
          - Navigate toward the target (turn + thrust) via the base
            class's ``navigate_to`` helper.
          - Pull the trigger (the weapon firing system handles range,
            cooldown, hit-chance internally).
        """
        if not self.ship.is_alive():
            return

        self.ship.set_turn_throttle(1.0)
        self.ship.set_throttle(1.0)

        # Kamikaze: when RamTargetAbility has an active target, defer
        # to BattleEngine._run_ramming_tick / RamTargetResolver. We
        # still pull the trigger so any non-ram weapons can fire on
        # the ram target en-route.
        if self._has_active_ram_target():
            ram_target = self._get_ram_target_entity()
            if ram_target is not None:
                self.ship.set_current_target(ram_target)
                self.ship.set_trigger_pulled(True)
            return

        # Standard target acquisition: nearest enemy from spatial grid.
        target = self._find_nearest_enemy()
        if target is None:
            self.ship.set_current_target(None)
            self.ship.set_trigger_pulled(False)
            return

        self.ship.set_current_target(target)
        self.ship.set_trigger_pulled(True)
        # Navigate toward the target — stop_dist=0 means "always thrust
        # if facing roughly right". The weapon firing system handles
        # actual firing range internally.
        self.navigate_to(target.position, stop_dist=0.0)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _find_nearest_enemy(self) -> Optional[Any]:
        """Return the closest live enemy ship, or None.

        Bypasses the targeting-policy weighting in
        :meth:`AIController.find_target` — fighters always want the
        nearest enemy.
        """
        enemies = self._find_enemies_in_radius()
        if not enemies:
            return None
        my_pos = self.ship.get_position()
        nearest: Optional[Any] = None
        nearest_d: float = float("inf")
        for e in enemies:
            try:
                d = my_pos.distance_to(e.position)
            except (AttributeError, TypeError):
                continue
            if d < nearest_d:
                nearest_d = d
                nearest = e
        return nearest

    def _has_active_ram_target(self) -> bool:
        """True iff the fighter ship mounts an active RamTargetAbility.

        Uses class-name lookup so this controller doesn't need to
        import :class:`RamTargetAbility` (mirrors
        :class:`RamTargetResolver`'s pattern from PROJ-FMS-B Phase 4).
        """
        try:
            comps = self.ship.get_all_components()
        except (AttributeError, TypeError):
            return False
        for comp in comps:
            if not getattr(comp, "is_active", True):
                continue
            abilities = getattr(comp, "ability_instances", None) or []
            for ab in abilities:
                if type(ab).__name__ != "RamTargetAbility":
                    continue
                target_id = getattr(ab, "target_id", None)
                if target_id is not None:
                    return True
        return False

    def _get_ram_target_entity(self) -> Optional[Any]:
        """Resolve the ram target's entity object from the spatial grid."""
        try:
            comps = self.ship.get_all_components()
        except (AttributeError, TypeError):
            return None
        target_id: Optional[Any] = None
        for comp in comps:
            if not getattr(comp, "is_active", True):
                continue
            for ab in getattr(comp, "ability_instances", None) or []:
                if type(ab).__name__ != "RamTargetAbility":
                    continue
                target_id = getattr(ab, "target_id", None)
                if target_id is not None:
                    break
            if target_id is not None:
                break
        if target_id is None:
            return None
        # Look up the entity object via the spatial grid contents.
        enemies = self._find_enemies_in_radius()
        for e in enemies:
            if getattr(e, "id", None) == target_id:
                return e
            if id(e) == target_id:
                return e
        return None


__all__ = ["FighterAIController"]
