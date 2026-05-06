"""``InterceptCalculator`` — chase / intercept point calculation.

PROJ-372 Phase 4: extracted from ``game/strategy/data/pathfinding.py``.
Holds a reference to a ``GalaxyPathfindingService`` for path queries.

Supports both ``Fleet`` and ``NavigationState`` chasers via duck-typing
(see ``_extract_chaser_info``).
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, List, Optional, Union

from game.core.hex_math import HexCoord

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.services.fleet_navigation_service import NavigationState
    from game.strategy.services.galaxy_pathfinding_service import (
        GalaxyPathfindingService,
    )


__all__ = ["InterceptCalculator", "project_fleet_path"]


logger = logging.getLogger(__name__)


class _ChaserProxyCapabilities:
    """Minimal capabilities adapter for _ChaserProxy."""

    def __init__(self, can_warp: bool):
        self._can_warp = can_warp

    def can_use_warp(self) -> bool:
        return self._can_warp


class _ChaserProxy:
    """Adapter that gives NavigationState a Fleet-like interface for
    ``find_hybrid_path``. Intentional adapter — not a legacy compat shim
    (PROJ-42)."""

    def __init__(self, can_warp: bool, fleet_id):
        self._capabilities = _ChaserProxyCapabilities(can_warp)
        self.id = fleet_id

    @property
    def capabilities(self) -> _ChaserProxyCapabilities:
        return self._capabilities


def _extract_chaser_info(chaser: Union["Fleet", "NavigationState"]) -> tuple:
    """Return (location, speed, id, can_warp) — duck-typed across both inputs."""
    from game.strategy.services.fleet_navigation_service import NavigationState

    if isinstance(chaser, NavigationState):
        return (chaser.location, chaser.speed, -1, chaser.can_warp)
    return (
        chaser.location,
        chaser.speed,
        chaser.id,
        chaser.capabilities.can_use_warp(),
    )


def project_fleet_path(fleet, galaxy, max_turns: int = 10) -> List[dict]:
    """Project a fleet's future path. Delegates to FleetNavigationService.

    Kept as a top-level function (rather than a method on the calculator)
    because callers don't need an InterceptCalculator instance for this
    pure-projection workflow.
    """
    from game.strategy.services.fleet_navigation_service import (
        FleetNavigationService,
    )

    service = FleetNavigationService()
    return service.project_path_as_dicts(fleet, galaxy, max_turns)


class InterceptCalculator:
    """Find an optimal intercept hex for a chaser pursuing a target fleet.

    Uses real path lengths (via ``GalaxyPathfindingService.find_hybrid_path``)
    rather than straight-line distance so the chaser routes through warp
    lanes correctly.
    """

    def __init__(self, pathfinding: "GalaxyPathfindingService"):
        self._pathfinding = pathfinding

    def calculate_intercept_point(
        self,
        chaser: Union["Fleet", "NavigationState"],
        target_fleet,
        galaxy: "Galaxy",
    ) -> Optional[HexCoord]:
        """Optimal interception hex, or target's current location if impossible.

        Algorithm:
          1. Project target's future path over 50 turns.
          2. For each candidate, compute chaser's travel time via hybrid pathfinding.
          3. Return the earliest point where the chaser arrives before the target leaves.
        """
        chaser_location, chaser_speed, chaser_id, chaser_can_warp = _extract_chaser_info(chaser)
        chaser_proxy = _ChaserProxy(chaser_can_warp, chaser_id)

        logger.debug(
            f"Intercept: chaser={chaser_id} @ {chaser_location} (speed={chaser_speed}) -> "
            f"target={target_fleet.id} @ {target_fleet.location}",
        )

        if chaser_speed <= 0:
            return target_fleet.location

        # Route through the shim so tests patching
        # `pathfinding.project_fleet_path` still take effect.
        from game.strategy.data import pathfinding as _pf_shim
        target_path = _pf_shim.project_fleet_path(target_fleet, galaxy, max_turns=50)
        points_to_check = target_path or [{"hex": target_fleet.location, "turn": 0}]

        best_intercept, best_time, best_turn, fallback = self._evaluate_intercept_candidates(
            points_to_check, chaser_location, chaser_speed, chaser_proxy, galaxy,
        )

        if best_intercept is not None:
            logger.debug(
                f"Intercept selected: {best_intercept} (chaser arrives turn {best_time:.1f}, "
                f"target at hex turn {best_turn})",
            )
            return best_intercept
        if target_path:
            result = target_path[-1]["hex"]
            logger.debug(f"No intercept possible - chasing endpoint: {result}")
            return result
        result = fallback if fallback else target_fleet.location
        logger.debug(f"Intercept fallback: {result}")
        return result

    def _evaluate_intercept_candidates(
        self,
        points_to_check: list,
        chaser_location: HexCoord,
        chaser_speed: float,
        chaser_proxy: _ChaserProxy,
        galaxy=None,
    ) -> tuple:
        """Score each candidate; return (best_hex, best_time, best_turn, fallback_hex).

        ``galaxy`` is passed when callers want test-patches of
        ``pathfinding.find_hybrid_path`` to take effect — we route via
        the shim. When ``galaxy`` is None, we use ``self._pathfinding``
        directly (faster, no extra layer of indirection)."""
        best_intercept = None
        best_intercept_time = float("inf")
        best_target_turn = None
        fallback_hex = None

        for pt in points_to_check:
            target_turn = pt["turn"]
            target_hex = pt["hex"]

            if galaxy is not None:
                # Route through the shim so test patches of
                # ``pathfinding.find_hybrid_path`` still apply.
                from game.strategy.data import pathfinding as _pf_shim
                path_to_target = _pf_shim.find_hybrid_path(
                    galaxy, chaser_location, target_hex, fleet=chaser_proxy,
                )
            else:
                path_to_target = self._pathfinding.find_hybrid_path(
                    chaser_location, target_hex, fleet=chaser_proxy,
                )
            if not path_to_target:
                continue

            path_length = max(0, len(path_to_target) - 1)
            chaser_turns = path_length / chaser_speed

            if chaser_turns < target_turn + 1:
                if chaser_turns < best_intercept_time:
                    best_intercept_time = chaser_turns
                    best_intercept = target_hex
                    best_target_turn = target_turn
                    if abs(chaser_turns - target_turn) < 0.1:
                        break
            else:
                if fallback_hex is None:
                    fallback_hex = target_hex

            if best_intercept is not None and target_turn > best_intercept_time + 3:
                break

        return (best_intercept, best_intercept_time, best_target_turn, fallback_hex)
