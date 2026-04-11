"""WaterEngine — Per-turn water level modification toward target.

Scans colonies for WaterModifier abilities and gradually changes the
planet's surface_water toward the player-set water_target. Changes are
permanent — they persist even if the facility is later removed.

Processed once per turn (not per tick), alongside AtmosphereEngine.
"""
import logging
from typing import List, TYPE_CHECKING

from game.core.patterns.layer_iterator import iter_components

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
            for comp in iter_components(facility.design_data):
                wm_data = self._extract_water_modifier(comp)
                if wm_data is None:
                    continue
                if isinstance(wm_data, list):
                    for entry in wm_data:
                        total_rate += entry.get('modification_rate', 0.0)
                else:
                    total_rate += wm_data.get('modification_rate', 0.0)

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

    def _extract_water_modifier(self, comp):
        """Extract WaterModifier ability data from a component entry."""
        from game.strategy.services.component_inspector import extract_abilities_from_component
        abilities = extract_abilities_from_component(comp, self._registries)
        data = abilities.get('WaterModifier')
        if isinstance(data, (dict, list)):
            return data
        return None
