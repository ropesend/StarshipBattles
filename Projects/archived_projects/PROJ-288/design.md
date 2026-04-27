# PROJ-288: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### What lives where today

- **`PopulationEngine._grow_species`** at `game/strategy/engine/population_engine.py` — computes logistic + decline for a single species in-place, mutating `pop.count`. The UI can't call this without side effects.
- **`HappinessEngine.process_happiness`** at `game/strategy/engine/happiness_engine.py` — same pattern, mutates `pop.happiness`.
- **`score_planet_for_race`** at `game/strategy/formulas/habitability.py` (PROJ-283) — pure, reusable. UI already calls it.
- **`planet_habitability_multiplier`** at `game/strategy/formulas/colony_output.py` (PROJ-285) — pure, cached per-turn on Planet. UI already has an access path.
- **`compute_planet_production`** at `game/ui/panels/planet_report_panel.py:498` — function-level, projects per-turn harvest per-resource. CURRENTLY lives in a UI file; should migrate into a service for reuse by other UIs.
- **No yard-consumption aggregator** — `_process_queue_tick_dynamic` in ProductionEngine consumes resources per-tick-per-queue; there's no "what would this planet's queues consume next turn" projector.
- **No population-upkeep projector** — `OrganicsConsumptionEngine.process_consumption` drains live; no projector.

### What this project extracts

Three pure primitives in order of complexity:

**1. `projected_growth_rate` (simple)**

```python
# game/strategy/formulas/colony_output.py
def projected_growth_rate(
    planet: 'Planet',
    pop: 'SpeciesPopulation',
    race_config: 'RaceConfig',
    cfg: 'ColonySpeciesConfig',
) -> float:
    """Return the % growth rate this species would experience next turn on
    this planet, given current inputs. Replicates PopulationEngine._grow_species
    math (PROJ-284 Phase 3) but returns the rate — does NOT mutate anything.

    Rate is returned as a fraction: +0.03 = 3%/turn growth, -0.02 = 2%/turn decline.
    Can be deeply negative under starvation (decline_term dominates) or deeply
    positive under ideal conditions (over-food + happiness > 1).
    """
    from game.strategy.formulas.habitability import score_planet_for_race
    from game.strategy.engine.population_engine import DECLINE_RATE

    if pop.count <= 0:
        return 0.0

    last_food_ratio = cfg.last_food_ratio  # multi-resource MIN after PROJ-286
    habitability = score_planet_for_race(planet, race_config)
    K_eff = max(1.0, planet.max_population * habitability)

    effective_r = race_config.base_reproduction_rate * last_food_ratio
    logistic_factor = 1.0 - (pop.count / K_eff)
    happiness = max(0.0, pop.happiness)
    logistic_term = effective_r * logistic_factor * happiness  # per-capita

    decline_term = 0.0
    if last_food_ratio < 1.0:
        decline_term = -DECLINE_RATE * (1.0 - last_food_ratio)  # per-capita

    return logistic_term + decline_term
```

Note the per-capita vs absolute distinction — `PopulationEngine._grow_species` returns absolute delta (`rate * pop.count`); the UI helper returns the rate (delta per unit of pop). UI then multiplies to get Δpop if needed.

**2. `PlanetEconomyProjector` (medium)**

```python
# game/strategy/services/planet_economy_projector.py
@dataclass(frozen=True)
class ResourceProjection:
    resource_id: str
    harvest: float       # Projected per-turn harvest from planet harvesters
    upkeep: float        # Population consumption (sum across species)
    yard: float          # Projected per-turn drain from active construction queues
    net: float           # harvest - upkeep - yard

class PlanetEconomyProjector:
    def __init__(
        self,
        *,
        registries: GameRegistries,
        economy_config: EconomyConfig,
        race_registry: IRaceRegistry,
    ):
        self._registries = registries
        self._economy = economy_config
        self._race_registry = race_registry

    def project(self, planet: 'Planet') -> Dict[str, ResourceProjection]:
        harvest = self._project_harvest(planet)       # reuses compute_planet_production
        upkeep  = self._project_upkeep(planet)        # iterates population_consumption dict
        yard    = self._project_yard_drain(planet)    # iterates construction_queue + facility queues
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
```

Three sub-computations:
- **Harvest**: extract + relocate `compute_planet_production` from `planet_report_panel.py:498` to this service. Applies habitability multiplier per PROJ-285.
- **Upkeep**: iterate `planet.populations`, resolve `cfg = planet.get_species_config(race_id)`, sum `pop.count * cfg.food_allocation * per_pop_rate` for each `resource_id, per_pop_rate` in `economy.population_consumption.items()`.
- **Yard**: iterate planet's `construction_queue` (planetary yard) + each operational shipyard facility's `construction_queue`. For the CURRENT head item in each queue, compute `per_turn_drain[res] = production_rate[res]` scaled by habitability. Sum across queues per resource.

**3. `ColonyDemographicView` (simple DTO, aggregates 1 + 2)**

```python
# game/strategy/facade/dto/colony_demographic_view.py
@dataclass(frozen=True)
class SpeciesDemographicView:
    race_id: str
    race_name: str       # display name from race_config
    count: int
    habitability: float  # [0,1] from score_planet_for_race
    happiness: float     # [0,3] current value on pop
    growth_rate: float   # from projected_growth_rate
    food_ratio: float    # cfg.last_food_ratio (MIN across resources)
    food_allocation: float  # slider value

@dataclass(frozen=True)
class ColonyDemographicView:
    planet_id: int
    planet_name: str
    species: Tuple[SpeciesDemographicView, ...]   # ordered largest-first
    resource_projections: Tuple[ResourceProjection, ...]  # all resources on this planet
    total_upkeep: Dict[str, float]  # sum of upkeep across species (for Treasury aggregation)
```

Facade method:
```python
def get_colony_demographic_view(self, planet_id: int) -> Optional[ColonyDemographicView]:
    """Materialize one read with all per-species + per-resource demographics
    data for this colony. UI panels consume this — no per-frame re-projection."""
    planet = self._resolve_planet(planet_id)
    if planet is None or planet.owner_id is None:
        return None
    # ... build via projector + race_registry
```

## Architecture

### Duplication vs migration

The `projected_growth_rate` helper duplicates the math in `PopulationEngine._grow_species`. Rationale: the engine mutates, the helper doesn't. Migrating the engine to call the helper + apply the delta is possible but:
- Adds a function-call layer in the engine's hot path (100 ticks × colonies × species).
- Risk: subtle type changes (int truncation, clamping) if not reviewed carefully.
- Test suite would need expansion.

For THIS project, duplicate the math and pin equivalence via an integration test (Phase 1 Task). A follow-up cleanup project can consolidate if the duplication cost becomes real.

### Where `compute_planet_production` should live

Currently at `game/ui/panels/planet_report_panel.py:498` — a UI file. Non-UI callers shouldn't import UI. Move to `game/strategy/services/planet_economy_projector.py` as a module-level function or static method on `PlanetEconomyProjector`. Update the one UI caller to import from the service.

### Yard projection semantics

For a queue with one item being built, per-turn drain = `cost_per_tick * 100` (where cost_per_tick is what `_calculate_tick_expenditure` would compute for the current capacity). But if the item will COMPLETE this turn, the actual drain is less. Edge case: for the UI "projection" we show the MAXIMUM per-turn drain (i.e. the item continues for the full turn). This is slightly pessimistic but consistent with "what does this planet project to consume next turn assuming no disruption".

Alternative: scale by `min(1.0, remaining_cost / per_turn_rate)`. More accurate but flickers as queues empty/fill. Decision: use MAX per-turn drain; document the decision.

### Multi-queue aggregation

A colony with PlanetaryYard + N space shipyards has N+1 queues. Each queue runs independently. Per-turn drain = SUM across queues per resource. Empty queues contribute 0. Fleet queues (on fleets docked here) are NOT counted — they're fleet-owned, not colony-owned.

### Caching scope

Projections are READ-ONLY and computed on demand. No cache in this project — the cost is O(species + resources + queues) per call, and UIs typically request one per frame per opened panel. If profiling shows this as a hotspot, add per-turn caching on `Planet` similar to PROJ-285's habitability cache. Out of scope for v1.

## Key Patterns to Reuse

- **`game/strategy/formulas/colony_output.py`** is the established location for pure colony-output formulas (PROJ-285). Grow this file.
- **Service injected via DI** (PROJ-284/285 pattern) — `PlanetEconomyProjector` takes `registries`, `economy_config`, `race_registry` via constructor.
- **Frozen dataclass DTOs on facade** (CQRS-lite pattern in docs/02_PATTERNS.md §6) — `ColonyDemographicView` joins the existing `FleetInfo`, `SystemInfo`, `PlanetInfo` DTO family.

## Dependencies & Risks

1. **PROJ-286 contract** — the projector reads `economy.population_consumption` dict. If PROJ-286 delivers a different shape, Phase 2 needs adjustment.

2. **PROJ-287 contract** — the facade method resolves `race_registry = self.get_race_registry()`. Must exist and return `IRaceRegistry`.

3. **Formula equivalence drift** — if PROJ-284's PopulationEngine formula changes (e.g. someone tweaks `DECLINE_RATE`), `projected_growth_rate` must track. The equivalence integration test (Phase 1) catches this on CI.

4. **Yard projection edge case** — if a queue has NO items, yard drain is 0 for every resource. Not a bug, but UI displaying "0 / 0 / 0 / X" rows may confuse players. Out of scope to hide them; UI (PROJ-289) decides.

5. **Moving `compute_planet_production`** — breaks the current import in `planet_report_panel.py`. Update the one call site; PROJ-289 will further refactor that panel.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
