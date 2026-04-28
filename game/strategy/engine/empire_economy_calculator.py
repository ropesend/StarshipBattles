"""
EmpireEconomyCalculator - Aggregates empire-wide production and expense data.

PROJ-99 Phase 1: Pure strategy-layer class that calculates production from
facilities, construction expenses, and provides a snapshot of the empire economy.

This is a read-only calculation - it doesn't modify any game state.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

from game.core.resources import ResourceCatalog
from game.core.patterns.layer_iterator import iter_components

_PLANETARY_IDS = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.strategy.config.economy_config import EconomyConfig
    from game.strategy.data.empire import Empire
from game.core.registry import GameRegistries
from game.strategy.engine.harvesting_engine import get_harvester_info
from game.strategy.engine.construction_forecast import forecast_queue_turn_spend


@dataclass
class EmpireEconomySnapshot:
    """Snapshot of empire economic state.

    Contains aggregated production and expense data for the empire.
    All fields are Dict[str, float] mapping resource type to amount.
    Default factory ensures each can be instantiated empty.
    """

    # Production sources
    colony_production: Dict[str, float] = field(default_factory=dict)
    ship_production: Dict[str, float] = field(default_factory=dict)
    trade_production: Dict[str, float] = field(default_factory=dict)
    tribute_production: Dict[str, float] = field(default_factory=dict)
    mining_production: Dict[str, float] = field(default_factory=dict)
    total_production: Dict[str, float] = field(default_factory=dict)

    # Expense categories
    tribute_expenses: Dict[str, float] = field(default_factory=dict)
    construction_expenses_ships: Dict[str, float] = field(default_factory=dict)
    construction_expenses_complexes: Dict[str, float] = field(default_factory=dict)
    total_expenses: Dict[str, float] = field(default_factory=dict)

    # PROJ-290 Phase 1: empire-wide multi-resource population upkeep.
    # Sparse dict — keys are only resources declared in
    # `EconomyConfig.population_consumption` that have non-zero demand
    # somewhere in the empire. Empty `{}` when the empire has no
    # populations yet, which signals the treasury row to hide.
    total_population_upkeep: Dict[str, float] = field(default_factory=dict)

    # Treasury state
    net_resources: Dict[str, float] = field(default_factory=dict)
    current_storage: Dict[str, float] = field(default_factory=dict)
    max_storage: Dict[str, float] = field(default_factory=dict)


class EmpireEconomyCalculator:
    """Calculator for empire-wide production and expense aggregation.

    PROJ-211: registries parameter is now required (no global fallback).

    Usage:
        # From GameSession context
        calculator = EmpireEconomyCalculator(registries=session.registries)
        snapshot = calculator.calculate(empire)
        # Access snapshot.colony_production, snapshot.total_expenses, etc.

    Replicates formulas from:
    - HarvestingEngine: base_harvest_rate * planet_quality
    """

    def __init__(
        self,
        *,
        registries: GameRegistries,
        economy_config: Optional["EconomyConfig"] = None,
        race_registry: Optional["IRaceRegistry"] = None,
    ) -> None:
        """Initialize the calculator.

        PROJ-211: registries is required (no global fallback).
        PROJ-290: `economy_config` + `race_registry` enable empire-wide
        multi-resource population upkeep aggregation via the shared
        `PlanetEconomyProjector`. When either is omitted the calculator
        still produces a valid snapshot but leaves
        `EmpireEconomySnapshot.total_population_upkeep = {}` — callers
        that want the upkeep row must pass both.

        Args:
            registries: GameRegistries for resolving component
                        abilities from plain component IDs in design_data (required).
            economy_config: Active `EconomyConfig` driving per-resource
                            population upkeep rates. When None, upkeep
                            aggregation is skipped.
            race_registry: Session-scoped `IRaceRegistry` used by the
                           projector's habitability multiplier. When None,
                           upkeep aggregation is skipped.
        """
        self._registries: GameRegistries = registries
        self._economy = economy_config
        self._race_registry = race_registry

    def calculate(self, empire: 'Empire') -> EmpireEconomySnapshot:
        """Calculate complete economic snapshot for an empire.

        Args:
            empire: Empire object with colonies, fleets, resource_pool, max_storage.

        Returns:
            EmpireEconomySnapshot with all production and expense data.
        """
        snapshot = EmpireEconomySnapshot()

        # Production aggregation
        snapshot.colony_production = self._aggregate_colony_production(empire)

        # Placeholder production sources (future implementation)
        zero_resources = {r: 0.0 for r in _PLANETARY_IDS}
        snapshot.ship_production = zero_resources.copy()
        snapshot.trade_production = zero_resources.copy()
        snapshot.tribute_production = zero_resources.copy()
        snapshot.mining_production = zero_resources.copy()

        # Total production = colony production only for now
        snapshot.total_production = snapshot.colony_production.copy()

        # Construction expenses split by type
        ships_exp, complexes_exp = self._aggregate_construction_expenses(empire)
        snapshot.construction_expenses_ships = ships_exp
        snapshot.construction_expenses_complexes = complexes_exp

        # Placeholder expense categories (future implementation)
        snapshot.tribute_expenses = zero_resources.copy()

        # PROJ-290: empire-wide multi-resource population upkeep.
        snapshot.total_population_upkeep = self._aggregate_population_upkeep(empire)

        # Total expenses = sum of all expense categories
        snapshot.total_expenses = {}
        for r in _PLANETARY_IDS:
            snapshot.total_expenses[r] = (
                snapshot.tribute_expenses.get(r, 0.0)
                + snapshot.construction_expenses_ships.get(r, 0.0)
                + snapshot.construction_expenses_complexes.get(r, 0.0)
                + snapshot.total_population_upkeep.get(r, 0.0)   # PROJ-291 C1: include upkeep
            )

        # Net resources per turn
        snapshot.net_resources = {}
        for r in _PLANETARY_IDS:
            prod = snapshot.total_production.get(r, 0.0)
            exp = snapshot.total_expenses.get(r, 0.0)
            snapshot.net_resources[r] = prod - exp

        # Current treasury state
        snapshot.current_storage = empire.resource_pool.copy()
        snapshot.max_storage = empire.max_storage.copy()

        return snapshot

    def _aggregate_population_upkeep(self, empire: 'Empire') -> Dict[str, float]:
        """Sum per-resource population upkeep across every empire colony.

        Delegates to `PlanetEconomyProjector._project_upkeep` via the
        shared `project()` entry point so upkeep math stays in one place
        (see PROJ-288 design.md § 3).

        Returns `{}` when either `economy_config` or `race_registry` was
        not injected at construction time — the treasury panel hides its
        row in that state, preserving backward compat for legacy callers
        that only pass `registries=`.
        """
        if self._economy is None or self._race_registry is None:
            return {}

        from game.strategy.services.planet_economy_projector import (
            PlanetEconomyProjector,
        )

        projector = PlanetEconomyProjector(
            registries=self._registries,
            economy_config=self._economy,
            race_registry=self._race_registry,
        )

        totals: Dict[str, float] = {}
        for colony in empire.colonies:
            projections = projector.project(colony)
            for res_id, projection in projections.items():
                if projection.upkeep <= 0:
                    continue
                totals[res_id] = totals.get(res_id, 0.0) + projection.upkeep
        return totals

    def _aggregate_colony_production(self, empire: 'Empire') -> Dict[str, float]:
        """Calculate total production from all colony facilities.

        Scans colonies -> facilities -> components for ResourceHarvester abilities.
        Checks inline abilities first, then falls back to registry lookup.
        Production = min(base_harvest_rate * quality, remaining_quantity) per harvester.

        Args:
            empire: Empire with colonies attribute.

        Returns:
            Dict mapping resource type to total production per turn.
        """
        totals = {r: 0.0 for r in _PLANETARY_IDS}

        for colony in empire.colonies:
            # Track remaining quantity per resource for this colony
            # (multiple harvesters draw from the same deposit)
            remaining_quantity: Dict[str, float] = {}
            for res in _PLANETARY_IDS:
                resource_data = colony.deposits.get(res, {})
                remaining_quantity[res] = resource_data.get('quantity', 0.0)

            for facility in colony.facilities:
                # Skip non-operational facilities
                if not facility.is_operational:
                    continue

                for comp in iter_components(facility.design_data):
                    harvester = get_harvester_info(comp, self._registries)
                    if harvester is None:
                        continue

                    resource_type = harvester.get('resource_type', '')
                    base_rate = harvester.get('base_harvest_rate', 0.0)

                    if not resource_type or base_rate <= 0:
                        continue

                    # Get planet quality for this resource
                    resource_data = colony.deposits.get(resource_type, {})
                    quality = resource_data.get('quality', 0.0)
                    if quality <= 0:
                        continue

                    # Cap production by remaining planet quantity
                    potential = base_rate * quality
                    available = remaining_quantity.get(resource_type, 0.0)
                    production = min(potential, available)

                    if resource_type in totals:
                        totals[resource_type] += production
                    # Reduce tracked quantity so subsequent harvesters see less
                    remaining_quantity[resource_type] = max(0.0, available - production)

        return totals

    def _aggregate_construction_expenses(
        self, empire: 'Empire'
    ) -> Tuple[Dict[str, float], Dict[str, float]]:
        """Calculate construction expenses split by ships vs complexes.

        Iterates all construction queues (planet base, facility, fleet),
        forecasts per-turn spend using queue-level distribution, and
        classifies by item type.

        Args:
            empire: Empire with colonies and fleets.

        Returns:
            Tuple of (ships_expenses, complexes_expenses), each a dict
            mapping resource type to total per-turn expense.
        """
        from game.strategy.data.build_queue_source import (
            get_default_production_rates,
            _get_facility_production_rates,
        )
        from game.strategy.data.fleet import Fleet

        ships = {r: 0.0 for r in _PLANETARY_IDS}
        complexes = {r: 0.0 for r in _PLANETARY_IDS}

        def _accumulate(queue: List[Dict], build_rate: Dict[str, float]) -> None:
            """Forecast spend for a queue and accumulate into ships/complexes."""
            if not queue:
                return
            per_item_spend = forecast_queue_turn_spend(queue, build_rate)
            for i, item in enumerate(queue):
                item_type = item.get("type", "ship")
                target = complexes if item_type == "complex" else ships
                spend = per_item_spend[i]
                for r, amount in spend.items():
                    if r in target:
                        target[r] += amount

        # Planet base queues (complexes only).
        # FEAT-17: paused queues contribute zero — ProductionEngine will not
        # tick them next turn, so they can't be a Treasury expense.
        for colony in empire.colonies:
            if not getattr(colony, 'construction_queue_paused', False):
                base_rate = get_default_production_rates("planetary_yard")
                _accumulate(colony.construction_queue, base_rate)

            # Facility queues (shipyards) — per-facility pause flag.
            for facility in colony.facilities:
                if (
                    facility.construction_queue
                    and facility.is_shipyard
                    and not getattr(facility, 'construction_queue_paused', False)
                ):
                    fac_rate = _get_facility_production_rates(facility)
                    _accumulate(facility.construction_queue, fac_rate)

        # Fleet queues — per-fleet pause flag.
        for fleet in empire.fleets:
            if not fleet.construction_queue:
                continue
            if not hasattr(fleet, 'capabilities') or not fleet.capabilities.has_space_shipyard:
                continue
            if getattr(fleet, 'construction_queue_paused', False):
                continue
            yard_count = fleet.capabilities.space_shipyard_count
            base_rate = get_default_production_rates("space_shipyard")
            total_rate = {k: v * yard_count for k, v in base_rate.items()}
            _accumulate(fleet.construction_queue, total_rate)

        return ships, complexes
