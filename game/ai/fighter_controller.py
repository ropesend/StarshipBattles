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

Kamikaze fighters follow the engine's :class:`RamTargetResolver`
instead — when ``BattleEngine.set_ram_target`` has been called on the
fighter, ``ship.ram_target`` is set and this controller short-circuits
its movement update so the resolver's intercept-and-pursue path can
run without interference. QA 2026-05-16 Obs 1b: ramming is no longer
gated on a ``RamTargetAbility`` component; the controller checks the
ship-level ``ram_target`` attribute that ``set_ram_target`` sets.
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
          - Kamikaze short-circuit: if a ram target is set on the
            ship (``ship.ram_target``), defer to the engine's
            RamTargetResolver.
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

        # Kamikaze: when ``ship.ram_target`` is set (via
        # ``BattleEngine.set_ram_target``), defer movement to
        # ``RamTargetResolver`` and just keep the trigger pulled so
        # non-ram weapons fire en-route. QA 2026-05-16 Obs 1b: the
        # ram-intent check is now the ship-level attribute, not an
        # ability lookup.
        ram_target = getattr(self.ship, "ram_target", None)
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



__all__ = ["FighterAIController"]
