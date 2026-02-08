"""
HarvestingEngine - Planetary Resource Harvesting

PROJ-75 Phase 2: Engine for extracting planetary resources to empire pools.

Responsibilities:
- Scan facilities for ResourceHarvester abilities
- Calculate harvest: base_rate * planet_quality
- Deduct from planet quantity (clamped to zero)
- Add to empire resource pool (respecting storage limits)
- Skip non-operational facilities and missing resource types

Fits into TurnEngine's process_turn() as a turn-start phase
(before the subturn loop).
"""

import logging
from typing import List, Optional, TYPE_CHECKING

from game.core.registry import GameRegistries
from game.strategy.interfaces.engines import IHarvestingEngine

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet, PlanetaryFacility

logger = logging.getLogger(__name__)


class HarvestingEngine(IHarvestingEngine):
    """
    Engine for processing planetary resource harvesting.

    PROJ-75 Phase 2: Scans planetary facilities for ResourceHarvester
    abilities and extracts resources from planets into empire pools.

    Harvest formula:
        harvest = base_harvest_rate * planet_resource_quality
        actual = min(harvest, planet_quantity)

    Supports two design_data formats:
    - Inline abilities: {"id": "comp", "abilities": {"ResourceHarvester": {...}}}
    - Registry lookup: plain string component ID resolved via registries
    """

    def __init__(self, *, registries: Optional[GameRegistries] = None):
        """Initialize the harvesting engine.

        Args:
            registries: Optional GameRegistries for resolving component
                       abilities from plain string IDs in design_data.
        """
        self._registries = registries

    def process_harvesting(self, empires: List) -> None:
        """
        Process resource harvesting for all empires.

        Iterates: empire -> colonies -> facilities -> components.
        For each ResourceHarvester ability found, extracts resources
        from the planet and adds them to the empire pool.

        Args:
            empires: List of Empire objects to process
        """
        for empire in empires:
            self._process_empire(empire)

    def _process_empire(self, empire: 'Empire') -> None:
        """Process harvesting for a single empire."""
        colonies = getattr(empire, 'colonies', [])
        for colony in colonies:
            self._process_colony(colony, empire)

    def _process_colony(self, colony: 'Planet', empire: 'Empire') -> None:
        """Process harvesting for a single colony."""
        facilities = getattr(colony, 'facilities', [])
        for facility in facilities:
            if not getattr(facility, 'is_operational', True):
                continue
            self._process_facility(facility, colony, empire)

    def _process_facility(
        self,
        facility: 'PlanetaryFacility',
        colony: 'Planet',
        empire: 'Empire',
    ) -> None:
        """Scan a facility's components for ResourceHarvester abilities."""
        design_data = getattr(facility, 'design_data', {})
        layers = design_data.get('layers', {})

        for layer_data in layers.values():
            if not isinstance(layer_data, list):
                continue
            for comp in layer_data:
                harvester_info = self._get_harvester_info(comp)
                if harvester_info is not None:
                    self._harvest_resource(
                        harvester_info, colony, empire
                    )

    def _get_harvester_info(self, comp) -> Optional[dict]:
        """Extract ResourceHarvester info from a component entry.

        Supports:
        - Dict with inline abilities: {"id": "x", "abilities": {"ResourceHarvester": {...}}}
        - Plain string ID: resolved via registries

        Args:
            comp: Component entry from design_data layers (dict or str)

        Returns:
            Dict with 'resource_type' and 'base_harvest_rate', or None
        """
        if isinstance(comp, dict):
            abilities = comp.get('abilities', {})
            harvester_data = abilities.get('ResourceHarvester')
            if isinstance(harvester_data, dict):
                return harvester_data
            # Also check by component ID via registry
            comp_id = comp.get('id')
            if comp_id and self._registries is not None:
                return self._lookup_harvester_in_registry(comp_id)
        elif isinstance(comp, str) and self._registries is not None:
            return self._lookup_harvester_in_registry(comp)
        return None

    def _lookup_harvester_in_registry(self, comp_id: str) -> Optional[dict]:
        """Look up harvester ability from the component registry.

        Args:
            comp_id: Component identifier to look up

        Returns:
            Dict with harvester info or None
        """
        comp_def = self._registries.components.get(comp_id)
        if comp_def is None:
            return None
        abilities = getattr(comp_def, 'abilities', {}) or {}
        harvester_data = abilities.get('ResourceHarvester')
        if isinstance(harvester_data, dict):
            return harvester_data
        return None

    def _harvest_resource(
        self,
        harvester_info: dict,
        colony: 'Planet',
        empire: 'Empire',
    ) -> None:
        """Execute one harvester's resource extraction.

        Args:
            harvester_info: Dict with 'resource_type' and 'base_harvest_rate'
            colony: Planet being harvested
            empire: Empire receiving resources
        """
        resource_type = harvester_info.get('resource_type', '')
        base_rate = harvester_info.get('base_harvest_rate', 0.0)

        if not resource_type or base_rate <= 0:
            return

        # Check planet has this resource
        planet_resources = getattr(colony, 'resources', {})
        resource_data = planet_resources.get(resource_type)
        if resource_data is None:
            return

        quality = resource_data.get('quality', 0.0)
        quantity = resource_data.get('quantity', 0.0)

        if quality <= 0 or quantity <= 0:
            return

        # Calculate harvest amount
        harvest = base_rate * quality
        actual_harvest = min(harvest, quantity)

        # Deduct from planet
        resource_data['quantity'] = quantity - actual_harvest

        # Add to empire pool
        empire.add_resources(resource_type, actual_harvest)

        logger.debug(
            "Harvested %.1f %s from %s (quality=%.2f, remaining=%.1f)",
            actual_harvest,
            resource_type,
            getattr(colony, 'name', 'unknown'),
            quality,
            resource_data['quantity'],
        )
