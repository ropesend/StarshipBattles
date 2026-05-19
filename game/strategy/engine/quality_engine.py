"""QualityEngine — Permanent resource quality improvement per turn.

Scans colonies for QualityImprovement abilities on operational facilities
and increases the quality value of the target resource each turn.

Changes are permanent — they persist even if the facility is later removed.
Quality caps at 100.0.
"""
from __future__ import annotations

import logging
from typing import List, TYPE_CHECKING

from game.strategy.services.component_abilities import iter_facility_ability_entries

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire

logger = logging.getLogger(__name__)

QUALITY_CAP = 100.0


class QualityEngine:
    """Engine for processing per-turn resource quality improvement."""

    def __init__(self, registries=None):
        self._registries = registries

    def _validate_tick_inputs(self, empires) -> None:
        """PROJ-251: Validate preconditions before mutating state."""
        from game.core.exceptions import ValidationException
        for empire in empires:
            for colony in empire.colonies:
                if colony is None:
                    raise ValidationException(
                        f"Empire {empire.id}: colony list contains None entry",
                        context={"empire_id": empire.id}
                    )

    def process_quality_improvement(self, empires: List) -> None:
        """Process quality improvement for all empires.

        Called once per turn (not per tick) by TurnEngine.

        Args:
            empires: List of Empire objects to process.
        """
        self._validate_tick_inputs(empires)
        for empire in empires:
            for colony in empire.colonies:
                self._process_colony(colony)

    def _process_colony(self, colony) -> None:
        """Process quality improvement for a single colony."""
        # Aggregate improvement rates per resource from all facilities
        improvements = {}  # resource_type -> total rate

        for facility in colony.facilities:
            if not getattr(facility, 'is_operational', True):
                continue
            for _comp, entry in iter_facility_ability_entries(
                facility, 'QualityImprovement', self._registries
            ):
                res = entry.get('resource_type', '')
                rate = entry.get('improvement_rate', 0.0)
                if res and rate > 0:
                    improvements[res] = improvements.get(res, 0.0) + rate

        # Apply improvements
        deposits = getattr(colony, 'deposits', {})
        for resource_type, total_rate in improvements.items():
            if resource_type not in deposits:
                continue
            resource_data = deposits[resource_type]
            current_quality = resource_data.get('quality', 0.0)
            new_quality = min(QUALITY_CAP, current_quality + total_rate)
            resource_data['quality'] = new_quality

            if new_quality > current_quality:
                logger.debug(
                    f"{colony.name}: {resource_type} quality {current_quality:.1f} -> {new_quality:.1f}"
                )
