"""
HarvestingEngine - Planetary Resource Harvesting & Storage Aggregation

PROJ-75 Phase 2-3: Engine for extracting planetary resources to empire pools
and calculating empire-wide storage capacity from storage facilities.
PROJ-161: Now per-tick only (100 ticks per turn, 1/100th harvest rate each).

Responsibilities:
- Scan facilities for ResourceHarvester abilities
- Calculate harvest: (base_rate * planet_quality) / 100 per tick
- Deduct from planet quantity (clamped to zero)
- Add to empire resource pool (respecting storage limits)
- Skip non-operational facilities and missing resource types
- Aggregate EmpireStorage abilities to set empire max_storage
- Recalculate storage each tick for mid-turn facility changes

Called by TurnEngine._process_tick() 100 times per turn.
"""

from typing import List, Optional, TYPE_CHECKING
import logging

from game.core.registry import GameRegistries

logger = logging.getLogger(__name__)
from game.strategy.interfaces.engines import IHarvestingEngine

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet, PlanetaryFacility


def get_harvester_info(comp, registries: Optional[GameRegistries] = None) -> Optional[dict]:
    """Extract ResourceHarvester info from a component entry.

    Supports:
    - Dict with inline abilities: {"id": "x", "abilities": {"ResourceHarvester": {...}}}
    - Plain string ID: resolved via registries

    Args:
        comp: Component entry from design_data layers (dict or str)
        registries: Optional GameRegistries for component lookup

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
        if comp_id and registries is not None:
            return get_harvester_from_registry(comp_id, registries)
    elif isinstance(comp, str) and registries is not None:
        return get_harvester_from_registry(comp, registries)
    return None


def get_harvester_from_registry(comp_id: str, registries: GameRegistries) -> Optional[dict]:
    """Get harvester ability from the component registry.

    Args:
        comp_id: Component identifier to look up
        registries: GameRegistries for component lookup

    Returns:
        Dict with harvester info or None
    """
    comp_def = registries.components.get(comp_id)
    if comp_def is None:
        return None
    # comp_def may be dict (JSON) or Component object
    abilities = getattr(comp_def, 'abilities', {}) or {}
    harvester_data = abilities.get('ResourceHarvester')
    if isinstance(harvester_data, dict):
        return harvester_data
    return None


class HarvestingEngine(IHarvestingEngine):
    """
    Engine for processing planetary resource harvesting.

    PROJ-75 Phase 2: Scans planetary facilities for ResourceHarvester
    abilities and extracts resources from planets into empire pools.
    PROJ-161: Per-tick only (1/100th of harvest rate per tick).

    Harvest formula (per tick):
        harvest = (base_harvest_rate * planet_resource_quality) / 100
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

    def process_harvesting_tick(self, tick: int, empires: List) -> None:
        """
        Process resource harvesting for one tick (1/100th of turn).

        PROJ-161: Per-tick harvesting spreads resource extraction across
        100 ticks. Each call extracts 1/100th of the per-turn harvest rate.

        Storage is recalculated each tick to handle mid-turn facility
        construction/destruction.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
        """
        self.recalculate_storage(empires)
        for empire in empires:
            self._process_empire(empire, tick_fraction=0.01)

    def recalculate_storage(self, empires: List) -> None:
        """
        Recalculate empire-wide storage capacity from storage facilities.

        Scans all colonies' facilities for EmpireStorage abilities and
        sums their capacity per resource type into empire.max_storage.

        Resets max_storage before recalculating so destroyed/removed
        facilities are no longer counted.

        Args:
            empires: List of Empire objects to process
        """
        for empire in empires:
            self._aggregate_empire_storage(empire)

    def _aggregate_empire_storage(self, empire: 'Empire') -> None:
        """Aggregate storage capacity for a single empire."""
        new_storage = {}
        for colony in empire.colonies:
            for facility in colony.facilities:
                if not facility.is_operational:
                    continue
                self._collect_storage_from_facility(facility, new_storage)
        empire.max_storage = new_storage

    def _collect_storage_from_facility(
        self,
        facility: 'PlanetaryFacility',
        storage_totals: dict,
    ) -> None:
        """Scan a facility's components for EmpireStorage abilities."""
        design_data = facility.design_data
        layers = design_data.get('layers', {})

        for layer_data in layers.values():
            if not isinstance(layer_data, list):
                continue
            for comp in layer_data:
                storage_info = self._get_storage_info(comp)
                if storage_info is not None:
                    resource_type = storage_info.get('resource_type', '')
                    capacity = storage_info.get('capacity', 0.0)
                    if resource_type and capacity > 0:
                        storage_totals[resource_type] = (
                            storage_totals.get(resource_type, 0.0) + capacity
                        )

    def _get_storage_info(self, comp) -> Optional[dict]:
        """Extract EmpireStorage info from a component entry.

        Supports:
        - Dict with inline abilities: {"id": "x", "abilities": {"EmpireStorage": {...}}}
        - Plain string ID: resolved via registries

        Args:
            comp: Component entry from design_data layers (dict or str)

        Returns:
            Dict with 'resource_type' and 'capacity', or None
        """
        if isinstance(comp, dict):
            abilities = comp.get('abilities', {})
            storage_data = abilities.get('EmpireStorage')
            if isinstance(storage_data, dict):
                return storage_data
            # Also check by component ID via registry
            comp_id = comp.get('id')
            if comp_id and self._registries is not None:
                return self._get_storage_from_registry(comp_id)
        elif isinstance(comp, str) and self._registries is not None:
            return self._get_storage_from_registry(comp)
        return None

    def _get_storage_from_registry(self, comp_id: str) -> Optional[dict]:
        """Get storage ability from the component registry.

        Args:
            comp_id: Component identifier to look up

        Returns:
            Dict with storage info or None
        """
        comp_def = self._registries.components.get(comp_id)
        if comp_def is None:
            return None
        # comp_def may be dict (JSON) or Component object
        abilities = getattr(comp_def, 'abilities', {}) or {}
        storage_data = abilities.get('EmpireStorage')
        if isinstance(storage_data, dict):
            return storage_data
        return None

    def _process_empire(self, empire: 'Empire', tick_fraction: float = 1.0) -> None:
        """Process harvesting for a single empire.

        Args:
            empire: Empire to process
            tick_fraction: Fraction of per-turn harvest to extract (1.0 = full turn, 0.01 = one tick)
        """
        for colony in empire.colonies:
            self._process_colony(colony, empire, tick_fraction)

    def _process_colony(self, colony: 'Planet', empire: 'Empire', tick_fraction: float = 1.0) -> None:
        """Process harvesting for a single colony.

        Args:
            colony: Colony to process
            empire: Empire receiving resources
            tick_fraction: Fraction of per-turn harvest to extract
        """
        for facility in colony.facilities:
            if not facility.is_operational:
                continue
            self._process_facility(facility, colony, empire, tick_fraction)

    def _process_facility(
        self,
        facility: 'PlanetaryFacility',
        colony: 'Planet',
        empire: 'Empire',
        tick_fraction: float = 1.0,
    ) -> None:
        """Scan a facility's components for ResourceHarvester abilities.

        Args:
            facility: Facility to scan
            colony: Colony containing the facility
            empire: Empire receiving resources
            tick_fraction: Fraction of per-turn harvest to extract
        """
        design_data = facility.design_data
        layers = design_data.get('layers', {})

        for layer_data in layers.values():
            if not isinstance(layer_data, list):
                continue
            for comp in layer_data:
                harvester_info = get_harvester_info(comp, self._registries)
                if harvester_info is not None:
                    self._harvest_resource(
                        harvester_info, colony, empire, tick_fraction
                    )

    def _get_harvester_info(self, comp) -> Optional[dict]:
        """Extract ResourceHarvester info from a component entry.

        Delegates to module-level get_harvester_info() function.

        Args:
            comp: Component entry from design_data layers (dict or str)

        Returns:
            Dict with 'resource_type' and 'base_harvest_rate', or None
        """
        return get_harvester_info(comp, self._registries)

    def _get_harvester_from_registry(self, comp_id: str) -> Optional[dict]:
        """Look up harvester ability from the component registry.

        Delegates to module-level get_harvester_from_registry() function.

        Args:
            comp_id: Component identifier to look up

        Returns:
            Dict with harvester info or None
        """
        if self._registries is None:
            return None
        return get_harvester_from_registry(comp_id, self._registries)

    def _harvest_resource(
        self,
        harvester_info: dict,
        colony: 'Planet',
        empire: 'Empire',
        tick_fraction: float = 1.0,
    ) -> None:
        """Execute one harvester's resource extraction.

        Args:
            harvester_info: Dict with 'resource_type' and 'base_harvest_rate'
            colony: Planet being harvested
            empire: Empire receiving resources
            tick_fraction: Fraction of per-turn harvest to extract (1.0 = full turn, 0.01 = one tick)
        """
        resource_type = harvester_info.get('resource_type', '')
        base_rate = harvester_info.get('base_harvest_rate', 0.0)

        if not resource_type or base_rate <= 0:
            return

        # Check planet has this resource
        resource_data = colony.resources.get(resource_type)
        if resource_data is None:
            return

        quality = resource_data.get('quality', 0.0)
        quantity = resource_data.get('quantity', 0.0)

        if quality <= 0 or quantity <= 0:
            return

        # Calculate harvest amount (scaled by tick_fraction for per-tick operation)
        harvest = base_rate * quality * tick_fraction
        actual_harvest = min(harvest, quantity)

        # Deduct from planet
        resource_data['quantity'] = quantity - actual_harvest

        # Add to empire pool
        empire.add_resources(resource_type, actual_harvest)

        logger.debug(
            f"Harvested {actual_harvest:.1f} {resource_type} from "
            f"{colony.name} (quality={quality:.2f}, "
            f"remaining={resource_data['quantity']:.1f}, tick_fraction={tick_fraction})"
        )
