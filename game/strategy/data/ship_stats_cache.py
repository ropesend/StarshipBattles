"""ShipStatsCache - Stats calculation + cache management for ShipInstance.

PROJ-425 Phase 1 (TD-06): extracted from ``ShipInstance.get_calculated_stats``
and ``invalidate_stats_cache`` so the entity no longer owns the registry-DI
calculation path and the cache invalidation rule.

Per TD-06 Weak-LLM Guardrail #2, storage (``ShipInstance._cached_stats``)
stays on the entity for this phase — only the *logic* moves. A later phase
may move the storage off the entity once this helper is proven.

The helper is stateless; methods operate on the supplied ``ShipInstance``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from game.strategy.data.ship_instance import ShipInstance


__all__ = ["ShipStatsCache"]


class ShipStatsCache:
    """Stateless helper that owns the stats calculation + cache rule."""

    @staticmethod
    def calculate(ship: "ShipInstance") -> Dict[str, Any]:
        """Recalculate stats from the ship's design + state.

        Uses ``calculate_design_stats`` as the single source of truth.
        Raises ``ValidationException`` (``MISSING_DEPENDENCY``) when no
        registries are wired.
        """
        # INTENTIONAL LATE IMPORT: cross-layer boundary (strategy -> simulation).
        # Same pattern as ``ShipInstanceBridge.to_ship``.
        from game.simulation.entities.ship_design_stats import calculate_design_stats

        from game.core.error_codes import ErrorCode
        from game.core.exceptions import ValidationException

        registries = ship._registries
        if registries is None:
            raise ValidationException(
                "ShipInstance requires registries for stats calculation. "
                "Use ShipInstance.create() or from_dict() with registries parameter, "
                "or set ship._registries after construction.",
                code=ErrorCode.MISSING_DEPENDENCY.value,
            )

        return calculate_design_stats(
            ship.design_data,
            registries,
            components=ship.components,
            component_toggles=ship.component_toggles,
        )

    @staticmethod
    def get_or_compute(
        ship: "ShipInstance", force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Return cached stats; recompute + cache on miss or force_refresh."""
        if ship._cached_stats is None or force_refresh:
            ship._cached_stats = ShipStatsCache.calculate(ship)
        return ship._cached_stats

    @staticmethod
    def invalidate(ship: "ShipInstance") -> None:
        """Clear the cached stats on the entity."""
        ship._cached_stats = None
