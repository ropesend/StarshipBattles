# PROJ-286: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### PROJ-284 baseline (what we're evolving)

- `data/economy.json` currently:
  ```json
  {"population_food_resource": "organics", "food_per_pop_per_turn": 0.001}
  ```
- `EconomyConfig` at `game/strategy/config/economy_config.py`:
  ```python
  @dataclass(frozen=True)
  class EconomyConfig:
      population_food_resource: str
      food_per_pop_per_turn: float
  ```
- `OrganicsConsumptionEngine.process_consumption(empires)` reads one resource id + one rate, drains colony stockpile, writes `cfg.last_food_ratio = supplied / needed`.
- `ColonySpeciesConfig`:
  ```python
  @dataclass
  class ColonySpeciesConfig:
      food_allocation: float = 1.0
      last_food_ratio: float = 1.0  # TRANSIENT — not serialized
  ```
- HappinessEngine: `happiness = clamp(base_happiness * cfg.last_food_ratio * habitability, 0, 3)`
- PopulationEngine: `effective_r = base_reproduction_rate * cfg.last_food_ratio`; `decline_term = -0.02 * P * (1 - last_food_ratio)` when ratio < 1.

### What changes

**Config schema** — dict instead of single-resource fields:
```json
{
    "population_consumption": {
        "organics": 0.001,
        "metals": 0.0001,
        "radioactives": 0.00001
    }
}
```

**EconomyConfig**:
```python
@dataclass(frozen=True)
class EconomyConfig:
    population_consumption: Dict[str, float]

    @property
    def primary_resource(self) -> str:
        """First resource in the dict (dict preserves insertion order in
        Python 3.7+). Used by UI titles that name the primary food
        resource — e.g. the FoodAllocationEditor window title. Returns
        "organics" as a safe fallback when the dict is empty."""
        return next(iter(self.population_consumption), "organics")
```

**ColonySpeciesConfig**:
```python
@dataclass
class ColonySpeciesConfig:
    food_allocation: float = 1.0
    # TRANSIENT — not serialized. Written per-resource by OrganicsConsumptionEngine.
    last_consumption_ratios: Dict[str, float] = field(default_factory=dict)

    @property
    def last_food_ratio(self) -> float:
        """Aggregate supply ratio for happiness / population formulas.

        Defined as the MINIMUM across all declared resource ratios — the
        colony is 'as well-fed as its worst-supplied resource'. If a
        colony has 100% organics but 0% metals, the aggregate ratio is 0
        and HappinessEngine/PopulationEngine treat the species as starving.

        Returns 1.0 when `last_consumption_ratios` is empty (uncolonized /
        pre-first-turn / zero-pop edge cases), preserving PROJ-284's
        default-1.0 contract.
        """
        if not self.last_consumption_ratios:
            return 1.0
        return min(self.last_consumption_ratios.values())
```

**OrganicsConsumptionEngine** — iterate every resource in `economy.population_consumption`:
```python
def process_consumption(self, empires):
    for empire in empires:
        for colony in empire.colonies:
            for pop in colony.populations:
                cfg = colony.get_species_config(pop.race_id)
                cfg.last_consumption_ratios.clear()  # overwrite every turn
                for resource_id, per_pop_rate in self._economy.population_consumption.items():
                    needed = pop.count * cfg.food_allocation * per_pop_rate
                    if needed <= 0:
                        cfg.last_consumption_ratios[resource_id] = 1.0
                        continue
                    available = colony.stockpile.get(resource_id, 0.0)
                    supplied = min(available, needed)
                    colony.stockpile[resource_id] = available - supplied
                    cfg.last_consumption_ratios[resource_id] = supplied / needed
```

## Architecture

### Aggregation choice: MIN

We aggregate `last_consumption_ratios` → `last_food_ratio` via `min()`. Three aggregation options were considered:

| Option | Semantics | Verdict |
|--------|-----------|---------|
| MIN | "as well-fed as the worst-supplied resource" | **Chosen** — matches Liebig's Law of the Minimum; harshest but most intuitive for gameplay |
| AVG | "average supply across resources" | Rejected — halving metals supply would only halve ratio by 1/3 on a 3-resource system; dilutes starvation signal |
| WEIGHTED | "weighted by per-pop rate" | Rejected — adds complexity without improving the happiness/population-decline signal |

MIN is also the cheapest mentally: "if the colony is at 50% on any needed resource, treat the species as 50% fed."

### Backward compat via computed property

`ColonySpeciesConfig.last_food_ratio` stays as a public API but becomes a `@property` computed from `last_consumption_ratios`. This means HappinessEngine + PopulationEngine continue to read `cfg.last_food_ratio` with zero code change — PROJ-284's formulas are preserved byte-for-byte.

Tests that pre-set `cfg.last_food_ratio = X` directly won't work anymore (can't set a property). Those tests migrate to `cfg.last_consumption_ratios = {"organics": X}` which is equivalent via MIN aggregation.

### Why NOT rename OrganicsConsumptionEngine

The name becomes misleading after this project (it now consumes any resources declared in economy.json, not just organics). Renaming to `PopulationUpkeepEngine` would be cleaner, but:

- Renames ripple into `IOrganicsConsumptionEngine`, `TurnEngineConfig.organics_consumption_engine`, `TurnEngine.organics_consumption_engine` property, `test_organics_consumption_engine.py`, docs cross-references.
- The rename is cosmetic, not functional.
- Combining a rename with a behavior change obscures the behavioral change in git history.

Deferred to a dedicated cleanup project. The class docstring will note the misnomer.

### Non-negotiables

- PROJ-284 tests must continue to pass after test migration (shape change from float to dict).
- PROJ-285 tests must not be touched (they don't depend on the ratio shape).
- HappinessEngine + PopulationEngine source files must not change.

## Key Patterns to Reuse

- **`get_default_* / set_default_*` module-accessor pattern** (CLAUDE.md, already used by `EconomyConfig`). Schema change preserves this.
- **Transient field on `ColonySpeciesConfig` via `field(default_factory=dict)` with `to_dict`/`from_dict` exclusion** — parallels PROJ-284's handling of `last_food_ratio`.
- **Engine iterates resources, writes per-resource ratio, zero behavior change downstream via computed property** — similar in spirit to PROJ-285's per-turn cache on Planet.

## Dependencies & Risks

1. **Test migration scope** — `tests/unit/strategy/engine/test_organics_consumption_engine.py` has 12 tests that seed/assert `last_food_ratio` directly. Each will need the new-dict shape. Risk: low (mechanical), but needs careful review to ensure semantic equivalence.

2. **Seed values on fresh `ColonySpeciesConfig`** — `last_consumption_ratios` defaults to `{}`; the computed `last_food_ratio` returns 1.0 from empty dict. This preserves PROJ-284's "default 1.0" contract.

3. **Zero-population edge case** — when `pop.count == 0`, PROJ-284 writes `last_food_ratio = 1.0` explicitly. Multi-resource version writes `{res_id: 1.0 for res_id in economy.population_consumption}` so the min still aggregates to 1.0.

4. **Resource-not-in-stockpile** — when a colony has never harvested a resource, `colony.stockpile.get(resource_id, 0.0)` returns 0, the ratio goes to 0, the aggregate min goes to 0, the species starves. Correct gameplay behavior but may surprise players. Document in `docs/systems/strategy_layer.md §8`.

5. **UI knock-on** — the `FoodAllocationEditor` title currently reads `{resource.name} Allocation — {planet.name}` using `economy.population_food_resource`. After this project, the title should use `economy.primary_resource`. PROJ-289 will update this properly; PROJ-286 just needs to not break the current UI. Minimum fix: keep a `population_food_resource` read-only property on EconomyConfig that returns `primary_resource` so existing UI keeps working.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
