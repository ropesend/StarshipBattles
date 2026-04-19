"""Per-planet per-resource projection service (PROJ-288 Phase 2).

`PlanetEconomyProjector` returns a snapshot dict of `ResourceProjection`
entries keyed by `resource_id`. Each entry breaks the planet's projected
next-turn flux into three components — **harvest**, **upkeep**, **yard
drain** — and a derived **net** (harvest − upkeep − yard).

The projector is stateless and read-only. It does NOT mutate `Planet`,
`SpeciesPopulation`, `EconomyConfig`, `IRaceRegistry`, or any queue. UI
panels call `project(planet)` once per render to source consistent
demographic + economic data without rolling their own formulas.

Three sub-projections, each independent:

* **harvest** = `compute_planet_production(planet, registries) * habitability`
  — scans operational facilities for `ResourceHarvester` abilities, sums
  `base_harvest_rate * deposit_quality`, then applies the colony
  habitability multiplier (PROJ-285 stacking rule).

* **upkeep** = `Σ_species pop.count * cfg.food_allocation * per_pop_rate`
  for each `(resource_id, per_pop_rate)` in
  `EconomyConfig.population_consumption`. Mirrors
  `OrganicsConsumptionEngine._process_colony` exactly. Upkeep is NOT
  habitability-scaled — population needs are independent of planet
  conditions.

* **yard drain** = `Σ_active_queue build_rate[res] * habitability` for the
  planet's base queue (PlanetaryYard) and each operational shipyard
  facility queue. Mirrors `ProductionEngine._process_queue_tick_dynamic`
  per-turn rate calculation. Empty queues contribute zero. Build-rate
  boosters (system-wide / sector-wide) are NOT factored in — the
  projector views the planet in isolation; boosters require galaxy +
  empire context the v1 contract doesn't carry.

The previously UI-only `compute_planet_production` lives here now: it's
strategy-layer math, not UI logic. The old `game/ui/panels/planet_report_panel.py`
location was a layer violation — non-UI callers cannot import from UI
per `docs/01_ARCHITECTURE.md § Dependency Rules`. Existing UI callers
(`planet_report_panel`, `build_queue_panel_factory`, `planet_list_window`,
`strategy_detail_formatter`) are migrated to import from this module in
Task 2.3.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from game.strategy.formulas.colony_output import planet_habitability_multiplier
from game.strategy.services.component_inspector import get_component_abilities

if TYPE_CHECKING:
    from game.core.protocols import IPlanet, IFacility, IRaceRegistry
    from game.core.registry import GameRegistries
    from game.strategy.config.economy_config import EconomyConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResourceProjection:
    """Per-resource per-planet next-turn flux snapshot.

    `net = harvest - upkeep - yard`. Frozen so UI consumers can treat it
    as a value type and cache freely.
    """
    resource_id: str
    harvest: float
    upkeep: float
    yard: float
    net: float


class PlanetEconomyProjector:
    """Per-planet per-resource projection service. See module docstring."""

    def __init__(
        self,
        *,
        registries: "GameRegistries",
        economy_config: "EconomyConfig",
        race_registry: "IRaceRegistry",
    ) -> None:
        self._registries = registries
        self._economy = economy_config
        self._race_registry = race_registry

    def project(self, planet: "IPlanet") -> Dict[str, ResourceProjection]:
        """Return per-resource flux for `planet` as the union of its
        harvest, upkeep, and yard sub-projections."""
        habitability = planet_habitability_multiplier(planet, self._race_registry)

        harvest = self._project_harvest(planet, habitability)
        upkeep = self._project_upkeep(planet)
        yard = self._project_yard_drain(planet, habitability)

        resource_ids = set(harvest) | set(upkeep) | set(yard)
        return {
            rid: ResourceProjection(
                resource_id=rid,
                harvest=harvest.get(rid, 0.0),
                upkeep=upkeep.get(rid, 0.0),
                yard=yard.get(rid, 0.0),
                net=harvest.get(rid, 0.0) - upkeep.get(rid, 0.0) - yard.get(rid, 0.0),
            )
            for rid in resource_ids
        }

    def _project_harvest(self, planet: "IPlanet", habitability: float) -> Dict[str, float]:
        """Per-resource harvest scaled by colony habitability (PROJ-285)."""
        base = compute_planet_production(planet, self._registries)
        return {res: rate * habitability for res, rate in base.items()}

    def _project_upkeep(self, planet: "IPlanet") -> Dict[str, float]:
        """Per-resource upkeep summed across species. Matches
        `OrganicsConsumptionEngine._process_colony` exactly."""
        upkeep: Dict[str, float] = {}
        consumption = self._economy.population_consumption
        for pop in planet.populations:
            count = getattr(pop, "count", 0)
            if count <= 0:
                continue
            cfg = planet.get_species_config(pop.race_id)
            allocation = cfg.food_allocation
            for resource_id, per_pop_rate in consumption.items():
                upkeep[resource_id] = (
                    upkeep.get(resource_id, 0.0) + count * allocation * per_pop_rate
                )
        return upkeep

    def _project_yard_drain(
        self, planet: "IPlanet", habitability: float
    ) -> Dict[str, float]:
        """Per-resource yard drain summed across non-empty active queues
        (planetary base + shipyard facilities), then scaled by habitability
        to mirror `ProductionEngine._process_queue_tick_dynamic`."""
        # `_collect_planet_sources` is strategy-internal (`_` prefix denotes
        # non-public-API but inside the same layer); calling it directly is
        # cheaper than reimplementing the queue-discovery + rate-resolution
        # logic. Pass galaxy=None and empire=None so the build-rate booster
        # math short-circuits to 1.0 — boosters require external context
        # the v1 projector contract doesn't carry (see module docstring).
        from game.strategy.data.build_queue_source import _collect_planet_sources

        sources: list = []
        _collect_planet_sources(planet, sources, registries=self._registries)

        drain: Dict[str, float] = {}
        for source in sources:
            if not source.construction_queue:
                continue
            for resource_id, rate in source.build_rate.items():
                drain[resource_id] = (
                    drain.get(resource_id, 0.0) + rate * habitability
                )
        return drain


# ---------------------------------------------------------------------------
# Module-level helpers (moved from `game/ui/panels/planet_report_panel.py`
# in PROJ-288 Task 2.3 — UI layer must not host strategy math)
# ---------------------------------------------------------------------------

def compute_planet_production(
    planet: "IPlanet",
    registries: "GameRegistries",
) -> Dict[str, float]:
    """Compute per-resource base production rates for a colony planet.

    Scans the planet's operational facilities for `ResourceHarvester`
    abilities and returns `base_harvest_rate * deposit_quality` per
    resource. Used by the projector's harvest sub-projection AND by UI
    panels that display production rates directly.

    Returns an empty dict for unowned planets (no harvest on rocks no one
    has claimed).

    Args:
        planet: Planet object with `facilities` and `deposits`.
        registries: GameRegistries for component-by-id lookups.

    Returns:
        Dict mapping resource id to per-turn base rate (pre-habitability).
    """
    if planet.owner_id is None:
        return {}

    rates: Dict[str, float] = {}
    facility: "IFacility"
    for facility in planet.facilities:
        if not facility.is_operational:
            continue
        design_data = facility.design_data
        for layer_data in design_data.get("layers", {}).values():
            if not isinstance(layer_data, list):
                continue
            for comp in layer_data:
                harvester = _get_harvester_info(comp, registries)
                if harvester:
                    res_type = harvester.get("resource_type", "")
                    base_rate = harvester.get("base_harvest_rate", 0.0)
                    if res_type and base_rate > 0:
                        quality = planet.deposits.get(res_type, {}).get("quality", 0.0)
                        rates[res_type] = rates.get(res_type, 0.0) + base_rate * quality
    return rates


def _get_harvester_info(comp: Any, registries: Optional["GameRegistries"]) -> Optional[dict]:
    """Extract `ResourceHarvester` ability dict from a component entry.

    Checks inline abilities first; falls back to registry lookup when
    the component is referenced only by id.
    """
    if isinstance(comp, dict):
        harvester = comp.get("abilities", {}).get("ResourceHarvester")
        if isinstance(harvester, dict):
            return harvester
        comp_id = comp.get("id")
        if comp_id and registries is not None:
            comp_def = registries.components.get(comp_id)
            if comp_def is not None:
                abilities = get_component_abilities(comp_def)
                harvester = abilities.get("ResourceHarvester")
                if isinstance(harvester, dict):
                    return harvester
    return None


__all__ = [
    "ResourceProjection",
    "PlanetEconomyProjector",
    "compute_planet_production",
]
