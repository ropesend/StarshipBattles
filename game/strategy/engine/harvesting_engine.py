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
- Aggregate LocalStorage abilities to set empire max_storage
- Recalculate storage each tick for mid-turn facility changes

Called by TurnEngine._process_tick() 100 times per turn.
"""

from __future__ import annotations

from typing import Any, List, Optional, TYPE_CHECKING
import logging

from game.core.registry import GameRegistries
from game.core.patterns.layer_iterator import iter_components
from game.strategy.services.component_inspector import get_component_abilities
from game.strategy.services.modifier_resolver import resolve_size_multiplier

logger = logging.getLogger(__name__)
from game.strategy.interfaces.engines import IHarvestingEngine

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.planet import Planet, PlanetaryFacility


def get_harvester_info(comp, registries: Optional[GameRegistries] = None) -> dict | list | None:
    """Extract ResourceHarvester info from a component entry.

    Supports:
    - Dict with inline abilities: {"id": "x", "abilities": {"ResourceHarvester": {...}}}
    - List of dicts: {"id": "x", "abilities": {"ResourceHarvester": [{...}, {...}]}}
    - Plain string ID: resolved via registries

    Args:
        comp: Component entry from design_data layers (dict or str)
        registries: Optional GameRegistries for component lookup

    Returns:
        Dict, list of dicts, or None
    """
    if isinstance(comp, dict):
        abilities = comp.get('abilities', {})
        harvester_data = abilities.get('ResourceHarvester')
        if isinstance(harvester_data, (dict, list)):
            return harvester_data
        # Also check by component ID via registry
        comp_id = comp.get('id')
        if comp_id and registries is not None:
            return get_harvester_from_registry(comp_id, registries)
    elif isinstance(comp, str) and registries is not None:
        return get_harvester_from_registry(comp, registries)
    return None


def get_harvester_from_registry(comp_id: str, registries: GameRegistries) -> dict | list | None:
    """Get harvester ability from the component registry.

    Args:
        comp_id: Component identifier to look up
        registries: GameRegistries for component lookup

    Returns:
        Dict, list of dicts, or None
    """
    comp_def = registries.components.get(comp_id)
    if comp_def is None:
        return None
    abilities = get_component_abilities(comp_def)
    harvester_data = abilities.get('ResourceHarvester')
    if isinstance(harvester_data, (dict, list)):
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

    def __init__(
        self,
        *,
        registries: GameRegistries,
        race_registry: Optional[Any] = None,
    ):
        """Initialize the harvesting engine.

        Args:
            registries: GameRegistries for resolving component abilities.
                       Required — no fallback.
            race_registry: PROJ-285 — optional race-config lookup for the
                population-weighted habitability multiplier on colony harvest.
                Must expose `get_race(race_id) -> Optional[RaceConfig]`.
                When None (legacy callers), the multiplier is 1.0 and
                harvest behaves as it did pre-PROJ-285.

        Raises:
            ValidationException: If registries is None.
        """
        if registries is None:
            from game.core.exceptions import ValidationException
            from game.core.error_codes import ErrorCode
            raise ValidationException(
                "registries is required for HarvestingEngine",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"class": "HarvestingEngine", "parameter": "registries"}
            )
        self._registries = registries
        self._race_registry = race_registry
        # PROJ-285: used to key the per-turn habitability cache on Planet.
        # TurnEngine calls `set_current_turn` before each turn's tick loop.
        self._current_turn: int = 0
        self._galaxy = None

    def set_current_turn(self, turn: int) -> None:
        """PROJ-285: TurnEngine calls this at the start of each turn so the
        per-turn habitability cache invalidates cleanly."""
        self._current_turn = turn

    def _validate_tick_inputs(self, empires: List) -> None:
        """PROJ-251: Validate preconditions before mutating state.

        Raises:
            ValidationException: If any empire has invalid colony references.
        """
        from game.core.exceptions import ValidationException
        for empire in empires:
            for i, colony in enumerate(empire.colonies):
                if colony is None:
                    raise ValidationException(
                        f"Empire {empire.id}: colony at index {i} is None",
                        context={"empire_id": empire.id, "colony_index": i}
                    )

    def process_harvesting_tick(self, tick: int, empires: List, galaxy=None) -> None:
        """
        Process resource harvesting for one tick (1/100th of turn).

        PROJ-161: Per-tick harvesting spreads resource extraction across
        100 ticks. Each call extracts 1/100th of the per-turn harvest rate.

        Storage is recalculated each tick to handle mid-turn facility
        construction/destruction.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process
            galaxy: Optional Galaxy for scoped ability queries (harvest boosters)
        """
        self._validate_tick_inputs(empires)
        self._galaxy = galaxy
        self.recalculate_storage(empires)
        for empire in empires:
            self._process_empire(empire, tick_fraction=0.01)

    def recalculate_storage(self, empires: List) -> None:
        """
        Recalculate empire-wide storage capacity from storage facilities.

        Scans all colonies' facilities for LocalStorage abilities and
        sums their capacity per resource type into empire.max_storage.

        Resets max_storage before recalculating so destroyed/removed
        facilities are no longer counted.

        Args:
            empires: List of Empire objects to process
        """
        for empire in empires:
            self._aggregate_empire_storage(empire)

    def _aggregate_empire_storage(self, empire: 'Empire') -> None:
        """Aggregate storage capacity per colony into local max_stockpile and staging yard."""
        for colony in empire.colonies:
            colony_storage = {}
            staging_mass = 0.0
            for facility in colony.facilities:
                if not facility.is_operational:
                    continue
                self._collect_storage_from_facility(facility, colony_storage)
                staging_mass += self._collect_staging_capacity(facility)
            colony.max_stockpile = colony_storage
            colony.max_staging_mass = staging_mass
        # Keep empire.max_storage as aggregate for read-only UI display
        empire_total = {}
        for colony in empire.colonies:
            for res, cap in colony.max_stockpile.items():
                empire_total[res] = empire_total.get(res, 0.0) + cap
        empire.max_storage = empire_total

    def _collect_staging_capacity(self, facility: 'PlanetaryFacility') -> float:
        """Sum StagingYard capacity from a facility's components."""
        total = 0.0
        for comp in iter_components(facility.design_data):
            staging_info = self._get_staging_info(comp)
            if staging_info is not None:
                # Handle single dict or list of dicts
                if isinstance(staging_info, dict):
                    staging_info = [staging_info]
                for entry in staging_info:
                    total += entry.get('capacity_mass', 0.0)
        return total

    def _get_staging_info(self, comp) -> dict | list | None:
        """Extract StagingYard info from a component entry."""
        if isinstance(comp, dict):
            abilities = comp.get('abilities', {})
            data = abilities.get('StagingYard')
            if isinstance(data, (dict, list)):
                return data
            comp_id = comp.get('id')
            if comp_id and self._registries is not None:
                comp_def = self._registries.components.get(comp_id)
                if comp_def:
                    reg_abilities = get_component_abilities(comp_def)
                    data = reg_abilities.get('StagingYard')
                    if isinstance(data, (dict, list)):
                        return data
        elif isinstance(comp, str) and self._registries is not None:
            comp_def = self._registries.components.get(comp)
            if comp_def:
                reg_abilities = get_component_abilities(comp_def)
                data = reg_abilities.get('StagingYard')
                if isinstance(data, (dict, list)):
                    return data
        return None

    def _collect_storage_from_facility(
        self,
        facility: 'PlanetaryFacility',
        storage_totals: dict,
    ) -> None:
        """Scan a facility's components for LocalStorage abilities."""
        for comp in iter_components(facility.design_data):
            storage_entries = self._get_storage_info(comp)
            if storage_entries is None:
                continue
            # Normalize to list (single dict or list of dicts)
            if isinstance(storage_entries, dict):
                storage_entries = [storage_entries]
            size_mult = resolve_size_multiplier(comp)
            for entry in storage_entries:
                resource_type = entry.get('resource_type', '')
                capacity = entry.get('capacity', 0.0) * size_mult
                if resource_type and capacity > 0:
                    storage_totals[resource_type] = (
                        storage_totals.get(resource_type, 0.0) + capacity
                    )

    def _get_storage_info(self, comp) -> dict | list | None:
        """Extract LocalStorage info from a component entry.

        Supports:
        - Dict with inline abilities: {"id": "x", "abilities": {"LocalStorage": {...}}}
        - List of dicts: {"id": "x", "abilities": {"LocalStorage": [{...}, {...}]}}
        - Plain string ID: resolved via registries

        Args:
            comp: Component entry from design_data layers (dict or str)

        Returns:
            Dict, list of dicts, or None
        """
        if isinstance(comp, dict):
            abilities = comp.get('abilities', {})
            storage_data = abilities.get('LocalStorage')
            if isinstance(storage_data, (dict, list)):
                return storage_data
            # Also check by component ID via registry
            comp_id = comp.get('id')
            if comp_id and self._registries is not None:
                return self._get_storage_from_registry(comp_id)
        elif isinstance(comp, str) and self._registries is not None:
            return self._get_storage_from_registry(comp)
        return None

    def _get_storage_from_registry(self, comp_id: str) -> dict | list | None:
        """Get storage ability from the component registry.

        Args:
            comp_id: Component identifier to look up

        Returns:
            Dict, list of dicts, or None
        """
        comp_def = self._registries.components.get(comp_id)
        if comp_def is None:
            return None
        abilities = get_component_abilities(comp_def)
        storage_data = abilities.get('LocalStorage')
        if isinstance(storage_data, (dict, list)):
            return storage_data
        return None

    def _process_empire(self, empire: 'Empire', tick_fraction: float = 1.0) -> None:
        """Process harvesting for a single empire.

        Args:
            empire: Empire to process
            tick_fraction: Fraction of per-turn harvest to extract (1.0 = full turn, 0.01 = one tick)
        """
        for colony in empire.colonies:
            self._process_colony(colony, tick_fraction, empire=empire)

    def _process_colony(self, colony: 'Planet', tick_fraction: float = 1.0, empire=None) -> None:
        """Process harvesting for a single colony.

        Args:
            colony: Colony to process (resources deposited to colony.stockpile)
            tick_fraction: Fraction of per-turn harvest to extract
            empire: Empire that owns this colony (for scoped booster queries)
        """
        for facility in colony.facilities:
            if not facility.is_operational:
                continue
            self._process_facility(facility, colony, tick_fraction, empire=empire)

    def _process_facility(
        self,
        facility: 'PlanetaryFacility',
        colony: 'Planet',
        tick_fraction: float = 1.0,
        empire=None,
    ) -> None:
        """Scan a facility's components for ResourceHarvester abilities.

        Args:
            facility: Facility to scan
            colony: Colony containing the facility (resources deposited to colony.stockpile)
            tick_fraction: Fraction of per-turn harvest to extract
            empire: Empire that owns this colony (for scoped booster queries)
        """
        for comp in iter_components(facility.design_data):
            harvester_data = get_harvester_info(comp, self._registries)
            if harvester_data is None:
                continue
            # Normalize to list (single dict or list of dicts)
            if isinstance(harvester_data, dict):
                harvester_data = [harvester_data]
            size_mult = resolve_size_multiplier(comp)
            for harvester_info in harvester_data:
                self._harvest_resource(
                    harvester_info, colony, tick_fraction,
                    size_multiplier=size_mult,
                    empire=empire
                )

    def _get_habitability_mult(self, colony) -> float:
        """PROJ-285: Resolve the colony's per-turn habitability multiplier.

        Returns 1.0 when `race_registry` was not injected (legacy call
        pattern) OR when the colony doesn't expose
        `get_cached_habitability_multiplier` (MagicMock spec-shaped
        objects in older tests) — preserves pre-PROJ-285 formula
        values exactly in both cases.
        """
        if self._race_registry is None:
            return 1.0
        get_cached = getattr(colony, "get_cached_habitability_multiplier", None)
        if get_cached is None:
            return 1.0
        return get_cached(self._race_registry, self._current_turn)

    def _get_harvest_booster_mult(self, colony, resource_type, empire) -> float:
        """Aggregate ResourceHarvestBooster multipliers affecting this colony.

        Uses the strategic ability scanner to find all boosters at each scope
        that match the resource type, then aggregates with two-phase stacking.

        Args:
            colony: The colony being harvested.
            resource_type: Resource type to match boosters for.
            empire: Empire owning the colony.

        Returns:
            Combined multiplier (1.0 if no boosters).
        """
        if empire is None or self._galaxy is None:
            return 1.0

        from game.strategy.services.strategic_ability_scanner import (
            find_abilities_in_scope, aggregate_multipliers,
        )

        all_boosters = []
        for scope in ["planet", "sector", "system", "empire"]:
            entries = find_abilities_in_scope(
                "ResourceHarvestBooster", colony, self._galaxy, empire, scope,
                registries=self._registries,
            )
            for entry in entries:
                if entry.get("resource_type") == resource_type:
                    all_boosters.append(entry)

        return aggregate_multipliers(all_boosters)

    def _harvest_resource(
        self,
        harvester_info: dict,
        colony: 'Planet',
        tick_fraction: float = 1.0,
        size_multiplier: float = 1.0,
        empire=None,
    ) -> None:
        """Execute one harvester's resource extraction.

        Args:
            harvester_info: Dict with 'resource_type' and 'base_harvest_rate'
            colony: Planet being harvested (resources deposited to colony.stockpile)
            tick_fraction: Fraction of per-turn harvest to extract (1.0 = full turn, 0.01 = one tick)
            size_multiplier: Size mount scaling factor (e.g., 0.2 for 20% size)
            empire: Empire owning the colony (for scoped booster queries)
        """
        resource_type = harvester_info.get('resource_type', '')
        base_rate = harvester_info.get('base_harvest_rate', 0.0)

        if not resource_type or base_rate <= 0:
            return

        # Check planet has this resource
        resource_data = colony.deposits.get(resource_type)
        if resource_data is None:
            return

        quality = resource_data.get('quality', 0.0)
        quantity = resource_data.get('quantity', 0.0)

        if quality <= 0 or quantity <= 0:
            return

        # Calculate harvest amount (scaled by size, boosters, habitability,
        # and tick_fraction).
        # PROJ-285: habitability multiplier stacks multiplicatively
        # alongside booster aggregation. Cached per-turn on Planet so
        # 100 harvest ticks per turn trigger exactly one multiplier
        # computation per colony.
        booster_mult = self._get_harvest_booster_mult(colony, resource_type, empire)
        habitability_mult = self._get_habitability_mult(colony)
        harvest = (
            base_rate * size_multiplier * booster_mult * quality
            * habitability_mult * tick_fraction
        )
        actual_harvest = min(harvest, quantity)

        # Deduct from planet
        resource_data['quantity'] = quantity - actual_harvest

        # Add to planet local stockpile
        colony.add_to_stockpile(resource_type, actual_harvest)

        logger.debug(
            f"Harvested {actual_harvest:.1f} {resource_type} from "
            f"{colony.name} (quality={quality:.2f}, "
            f"remaining={resource_data['quantity']:.1f}, tick_fraction={tick_fraction})"
        )
