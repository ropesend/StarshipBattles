"""SatelliteAIController — PROJ-FMS-D Phase 1.

Stationary AI controller for tactical satellites. Per the shared design,
satellites are defensive emplacements: they do not move, but acquire
targets and fire when an enemy enters weapon range.

Why a dedicated controller?
    The base :class:`AIController` already short-circuits behavior
    execution for ships whose ``vehicle_type == 'Satellite'`` (see
    ``controller.py:361-363``), but it still pulls the trigger via the
    standard target-acquisition path. We want a tighter contract: zero
    movement throttles, no formation logic, no policy tree, no
    avoidance steering. Pick the nearest enemy, set it as the target,
    pull the trigger; otherwise idle in place.

The controller is registered via
:meth:`AIControllerFactory.create_for_ship` which dispatches on
``ship.vehicle_type == "Satellite"`` (parallel to the Fighter dispatch).
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


class SatelliteAIController(AIController):
    """Lightweight per-tick AI controller for tactical satellite ships.

    Behavior per tick:
        1. Liveness check — dead satellites idle silently.
        2. Force zero throttles so the satellite never accelerates or
           rotates under its own power.
        3. Find nearest live enemy via the spatial grid.
        4. Set it as the current target and pull the trigger; the
           weapon firing system handles range / cooldown / hit-chance.
        5. When no enemies are visible, clear target and release trigger.

    No movement, no avoidance, no formation, no ram support. Satellites
    are passive defensive emplacements.
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
        """Run one satellite-AI cycle. Strictly no movement output."""
        if not self.ship.is_alive():
            return

        # Force zero throttles — satellite is a stationary emplacement.
        # Defensive against base-class state that might leave a non-zero
        # throttle from a prior controller swap.
        try:
            self.ship.set_throttle(0.0)
            self.ship.set_turn_throttle(0.0)
        except AttributeError:
            # Minimal adapters may not expose these methods; the absence
            # of acceleration on those stubs is what we want anyway.
            pass

        target = self._find_nearest_enemy()
        if target is None:
            try:
                self.ship.set_current_target(None)
                self.ship.set_trigger_pulled(False)
            except AttributeError:
                pass
            return

        try:
            self.ship.set_current_target(target)
            self.ship.set_trigger_pulled(True)
        except AttributeError:
            pass

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _find_nearest_enemy(self) -> Optional[Any]:
        """Return the closest live enemy ship, or ``None``.

        Mirrors :class:`FighterAIController._find_nearest_enemy` — uses
        the same ``_find_enemies_in_radius`` surface from the base
        controller so test fixtures and grid stubs work identically.
        """
        enemies = self._find_enemies_in_radius()
        if not enemies:
            return None
        try:
            my_pos = self.ship.get_position()
        except AttributeError:
            return None
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


__all__ = ["SatelliteAIController"]
