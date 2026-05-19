"""WaterEngine — Per-turn water level modification toward target.

Scans colonies for WaterModifier abilities and gradually changes the
planet's surface_water toward the player-set water_target. Changes are
permanent — they persist even if the facility is later removed.

Processed once per turn (not per tick), alongside AtmosphereEngine.
"""
from __future__ import annotations

import logging
from typing import List, TYPE_CHECKING

from game.strategy.services.component_abilities import iter_facility_ability_entries

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire

logger = logging.getLogger(__name__)


class WaterEngine:
    """Engine for processing per-turn water level modification."""

    def __init__(self, registries=None):
        self._registries = registries

    def process_water_modification(self, empires: List) -> None:
        """Process water modification for all empires.

        Called once per turn (not per tick) by TurnEngine.

        Args:
            empires: List of Empire objects to process.
        """
        for empire in empires:
            for colony in empire.colonies:
                self._process_colony(colony)

    def _process_colony(self, colony) -> None:
        """Process water modification for a single colony."""
        target = getattr(colony, 'water_target', None)
        if target is None:
            return

        current = getattr(colony, 'surface_water', 0.0)

        # Sum modification rate from all operational facilities
        total_rate = 0.0
        for facility in getattr(colony, 'facilities', []):
            if not getattr(facility, 'is_operational', True):
                continue
            for _comp, entry in iter_facility_ability_entries(
                facility, 'WaterModifier', self._registries
            ):
                total_rate += entry.get('modification_rate', 0.0)

        if total_rate <= 0:
            return

        # Calculate change toward target
        delta = target - current
        if abs(delta) < 0.0001:
            return

        # Apply change without overshooting
        if abs(delta) <= total_rate:
            actual_change = delta
        else:
            actual_change = total_rate if delta > 0 else -total_rate

        new_water = max(0.0, min(1.0, current + actual_change))
        colony.surface_water = new_water
