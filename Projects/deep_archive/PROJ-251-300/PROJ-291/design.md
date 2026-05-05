# PROJ-291: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Audit provenance

This project resolves the 3 Critical findings from a dual cross-project audit of PROJ-283..290:

1. The first review (mine, single session) used 3 skeptical-reviewer Explore agents organized by layer (math/engines, infrastructure/contracts, UI/tests). It identified 1 Critical (the FoodAllocationEditor crash) + 5 High + 11 Medium + 8 Low.
2. The second review (the user's pre-existing 5-skeptic audit in `c:/Developer/StarshipBattles/Temp Review Docs/`) used 5 Explore agents organized by audit lens (pipeline reachability, architecture/shims, state/cache, merge hazards, tests/docs). It identified 3 Critical + 4 Major + 5 Minor + 12 cleared false-positives.
3. Two impartial Explore agents adjudicated disagreements between the two reviews. Outcomes:
   - The PROJ-289 view-kwarg threading IS a real UX regression (HIGH severity, my call upheld). Owner = PROJ-292 Phase 1.
   - The cache-rollback concern (`Planet._cached_habitability_multiplier` survival across `TurnStateSnapshot.restore()`) is CLEARED — `restore()` does `session.galaxy = Galaxy.from_dict(...)` which creates fresh Planet objects, so the `init=False` cache fields can never carry stale data across rollback.

The 3 Critical findings (C1, C2, C3) are confirmed by both reviews and are the scope of this project.

### What the audits found

**C1 — Treasury Total excludes Population Upkeep ([empire_economy_calculator.py:144-151](game/strategy/engine/empire_economy_calculator.py#L144-L151))**

`EmpireEconomyCalculator.calculate(empire)` sets `snapshot.total_population_upkeep = self._aggregate_population_upkeep(empire)` correctly on line 142, but then computes:

```python
snapshot.total_expenses = {}
for r in _PLANETARY_IDS:
    snapshot.total_expenses[r] = (
        snapshot.tribute_expenses.get(r, 0.0)
        + snapshot.construction_expenses_ships.get(r, 0.0)
        + snapshot.construction_expenses_complexes.get(r, 0.0)
    )
```

The `total_population_upkeep` term is **omitted** from the sum. The Treasury panel correctly displays a "Population Upkeep" row but its "Total" row reads `snapshot.total_expenses` — so the user sees a mathematically inconsistent total (e.g. `Tributes 0 + Ships 2 + Complexes 3 + Upkeep -10 = Total -5` displayed, but the correct total is -15). This is shape-identical to the PROJ-269/270 `_team_bonuses` / `_apply_bonuses` bug from a prior audit cycle.

**Why undetected:** `TestPopulationUpkeepAggregation` (7 tests) asserts `snapshot.total_population_upkeep` is correct, but no test asserts `snapshot.total_expenses` includes upkeep. There's also no end-to-end test from `_get_expense_rows` rendering — the audit's M3 (test gap).

**C2 — FoodAllocationEditor crashes at runtime ([food_allocation_editor.py:258](game/ui/screens/food_allocation_editor.py#L258))**

```python
consumption = compute_consumption_preview(
    pop, allocation, self._economy.food_per_pop_per_turn
)
```

`food_per_pop_per_turn` was deleted from `EconomyConfig` in PROJ-286. The replacement is `population_consumption: Dict[str, float]`. PROJ-286's plan.md explicitly deferred the editor migration to "PROJ-289's UI migration", but PROJ-289's manifest never picked it up — orphaned handoff.

**Symptom:** the editor opens cleanly, but the first slider adjustment that triggers the preview update raises `AttributeError: 'EconomyConfig' object has no attribute 'food_per_pop_per_turn'`. The cluster of 13 broken tests in `tests/unit/ui/screens/test_food_allocation_editor.py` is collateral damage from the same schema migration.

**C3 — Multi-species engines silently use the wrong race_config ([happiness_engine.py:90-95](game/strategy/engine/happiness_engine.py#L90-L95) and [population_engine.py:165-175](game/strategy/engine/population_engine.py#L165-L175))**

```python
def _get_race_config(self, race_id, empire):
    race_config = empire.race_config
    if race_config is None:
        return None
    if race_config.race_id == race_id:
        return race_config
    return race_config  # Phase 4 wires multi-species registry
```

The dual-return is the bug: when `race_id != empire.race_config.race_id`, the function returns the empire's PRIMARY race anyway. On a multi-species colony (humans + voidari, both in one empire), the engine computes both species' happiness/growth using the human `base_happiness` / `base_reproduction_rate`. PROJ-287's decisions.md line 16 deferred wiring `IRaceRegistry` here on the basis that "the engines' existing resolvers work" — they didn't, but the bug was invisible in single-species games. Post-PROJ-284 + PROJ-286 + PROJ-289, multi-species colonies are now real gameplay state, so the bug is reachable.

## Architecture

### C1 fix shape

One-line addition to the `total_expenses` sum at lines 147-150 of `empire_economy_calculator.py`:

```python
for r in _PLANETARY_IDS:
    snapshot.total_expenses[r] = (
        snapshot.tribute_expenses.get(r, 0.0)
        + snapshot.construction_expenses_ships.get(r, 0.0)
        + snapshot.construction_expenses_complexes.get(r, 0.0)
        + snapshot.total_population_upkeep.get(r, 0.0)   # PROJ-291 C1 fix
    )
```

Pinned by:

1. Unit test `TestTreasuryTotalIncludesUpkeep` in `tests/unit/strategy/engine/test_empire_economy_calculator.py` — constructs an empire with non-zero upkeep, calls `.calculate(empire)`, asserts the equation.
2. End-to-end integration test `tests/integration/strategy/test_treasury_panel_e2e.py` — builds a snapshot with non-zero upkeep, runs `EmpireTreasuryPanel._get_expense_rows(snapshot)`, asserts the "Population Upkeep" row appears AND the "Total" row magnitude equals the sum across all expense categories. **Closes prior-audit M3 simultaneously** (the e2e test that should have caught C1 in the first place).

### C3 fix shape: mirror PROJ-285's pattern

PROJ-285 already established the canonical optional-registry pattern on `HarvestingEngine` and `ProductionEngine`:

```python
def __init__(self, registries, race_registry=None, ...):
    self._registries = registries
    self._race_registry = race_registry
    ...

def _get_habitability_mult(self, colony) -> float:
    if self._race_registry is None:
        return 1.0  # legacy fallback — preserves pre-PROJ-285 tests
    ...
```

PROJ-291 applies the same shape to `HappinessEngine` and `PopulationEngine`:

```python
class HappinessEngine(IHappinessEngine):
    def __init__(self, race_registry: Optional['IRaceRegistry'] = None):
        self._race_registry = race_registry

    def _get_race_config(self, race_id: str, empire: 'Empire') -> Optional['RaceConfig']:
        # PROJ-291 C3: when registry is wired, resolve every race correctly.
        if self._race_registry is not None:
            race_config = self._race_registry.get_race(race_id)
            if race_config is not None:
                return race_config
            # registry wired but race_id unknown → fall through to legacy fallback
        # Legacy single-race fallback (preserves pre-PROJ-291 tests)
        race_config = empire.race_config
        if race_config is None:
            return None
        if race_config.race_id == race_id:
            return race_config
        return None  # PROJ-291 C3: stop returning the wrong race silently
```

`PopulationEngine` gets the identical treatment. Note the **third behaviour change**: when registry is None AND race_id doesn't match the empire's primary race, we now return `None` (the species is gracefully skipped) instead of returning the wrong `race_config`. The dual-return bug is fixed even on the legacy path.

`turn_engine.py` passes the registry through when constructing the engines:

```python
self.happiness_engine = HappinessEngine(race_registry=self._race_registry)
self.population_engine = PopulationEngine(race_registry=self._race_registry)
```

The `_race_registry` source on `turn_engine` is whatever PROJ-285 already wired. If PROJ-285 lazily resolves it from the session, do the same here.

### C2 fix shape: editor migrated to multi-resource preview

`compute_consumption_preview(pop, allocation, food_per_pop_per_turn) -> float` becomes `compute_consumption_preview(pop, allocation, population_consumption: Dict[str, float]) -> Dict[str, float]` returning per-resource consumption.

The editor's row UI gains a per-resource preview cluster. For a single-resource `economy.json` (default), the visual is essentially unchanged (one row of preview). For a multi-resource `economy.json`, the player sees one preview line per resource consumed.

The 13 broken test fixtures rewrite from `EconomyConfig(population_food_resource=..., food_per_pop_per_turn=...)` to `EconomyConfig(population_consumption={"organics": 0.001, ...})`. Some tests will need additional assertions for the multi-resource branches.

### `population_food_resource` shim retirement

After C2 lands, grep for any remaining callers of `EconomyConfig.population_food_resource`. If none, delete the shim from `economy_config.py`. If any callers remain (e.g. in label/title resolution that legitimately wants "the primary resource"), leave the shim and document. Either way, `food_per_pop_per_turn` should be removed from any compatibility surface — it was deleted by PROJ-286 and stays deleted.

## Key Patterns to Reuse

- **Optional `race_registry: Optional[Any] = None` kwarg + None-fallback** ([game/strategy/engine/harvesting_engine.py](game/strategy/engine/harvesting_engine.py), [production_engine.py](game/strategy/engine/production_engine.py)) — the canonical PROJ-285 pattern. C3 mirrors this exactly.
- **Strict TDD per CLAUDE.md Rule 1** — every task in this project's phase checklists has a "write the failing test FIRST" subtask before the implementation subtask.
- **Equivalence integration test pattern** ([tests/integration/strategy/test_growth_rate_equivalence.py](tests/integration/strategy/test_growth_rate_equivalence.py), PROJ-288) — for C3 multi-species verification, build a similar matrix: 2 species × 2 P/K_eff × 2 happiness baselines, assert each species grows at its own race's rate.

## Dependencies & Risks

1. **C3 is the largest piece — touches the demographics hot path.** Mitigation: keep the legacy fallback path so 850+ pre-PROJ-285 MagicMock tests continue to work. Don't make `race_registry` mandatory.

2. **C2 may surface secondary editor bugs once the schema migration lands.** Mitigation: the manual-smoke step in Phase 4 is non-optional; user must open a 2-species colony and walk through the food slider before sign-off.

3. **`Temp Review Docs/` is the user's working directory and may have files I haven't read.** Mitigation: copy (not move) during Phase 4. The user can delete the temp dir after they verify the archive.

4. **PROJ-292 file overlaps:** PROJ-292 Phase 1 (view threading) modifies `planet_list_window.py` and `build_queue_panel_factory.py`. PROJ-291 doesn't touch those, so parallel-safe. PROJ-292 Phase 2 (`empire_economy_service.py` facade) wraps `EmpireEconomyCalculator` which PROJ-291 modifies — sequential preferred; PROJ-291 lands first, then PROJ-292 wraps it.

5. **Reversal of PROJ-287 deferral.** PROJ-287's decisions.md line 16 explicitly chose NOT to migrate the engines. PROJ-291 reverses that. Document the reversal in PROJ-287/decisions.md as a forward-link.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
