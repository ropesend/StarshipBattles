# Architecture, Shim Lifecycle & Layer Integrity — Skeptical Audit

## Verdict

CLEAN-SHEET ADHERENT with ONE CRITICAL RUNTIME DEFECT. The eight projects (PROJ-283..290) respect layer boundaries and the registry pattern, but PROJ-286's FoodAllocationEditor shim remains live and broken: line 258 reads `self._economy.food_per_pop_per_turn`, which was deleted in PROJ-286, causing an AttributeError at runtime if the editor opens. This is not a mere shim — it is a deferred showstopper. Three other shims (view=None, empire=None, race_registry=None) are lightweight fallback paths, intentional, and documented. The parallel `projected_growth_rate` duplication is well-defended by a 12-cell equivalence matrix test.

---

## Investigation

### Q1: Layer violations

FINDING: ONE ARCHITECTURAL VIOLATION — UI directly imports from `game.strategy.engine`.

`game/ui/panels/empire_treasury_panel.py:19` and `game/ui/screens/empire_panel_window.py:18` both import:
```
from game.strategy.engine.empire_economy_calculator import EmpireEconomySnapshot / EmpireEconomyCalculator
```

Per `docs/01_ARCHITECTURE.md`, UI may read Strategy (read-only DTOs, facades), but direct engine imports are a layer violation. The appropriate fix: expose `EmpireEconomySnapshot` / `EmpireEconomyCalculator` via a strategy-layer service facade (`game/strategy/services/empire_economy_service.py`), not a raw engine class. This is NOT blamed on PROJ-283..290 — `empire_economy_calculator.py` pre-dates these projects — but auditing the new projects reveals the violation persists unchallenged.

No new violations introduced by PROJ-283..290. All new UI→strategy calls (e.g. `PlanetReportPanel.update_planet(view=None)`, `format_planet_info(view=None)`) respect the fallback-to-None pattern rather than hard-wiring direct engine access.

---

### Q2: Shim lifecycle audit

| Shim | Location | Owned By | Retirement | Documented | Status |
|------|----------|----------|------|---|---|
| **`EconomyConfig.population_food_resource`** | economy_config.py:72-76 | PROJ-286 | PROJ-289 callers | PROJ-286/decisions.md | LIVE & BROKEN |
| **`FoodAllocationEditor` line 258 broken read** | food_allocation_editor.py:258 | PROJ-286 deferred | PROJ-289 migration | PROJ-286/plan.md:38 | LIVE & BROKEN |
| **`format_planet_info(view=None)` fallback** | strategy_detail_fmt.py:139+ | PROJ-289 | Retire when callers migrate | PROJ-289/decisions.md:19 | LIVE & SAFE |
| **`PlanetReportPanel(view=None, empire=None, race_registry=None)`** | planet_report_panel.py:100-102 | PROJ-289 | Same as above | PROJ-289/decisions.md | LIVE & SAFE |
| **`PopulationEngine._get_race_config` not migrated** | population_engine.py:146-160 | PROJ-287 skipped | Deferred | PROJ-287/decisions.md:16 | WORKING |
| **`HappinessEngine._get_race_config` not migrated** | happiness_engine.py:77-95 | PROJ-287 skipped | Deferred | PROJ-287/decisions.md:16 | WORKING |

CRITICAL: FoodAllocationEditor broken at runtime. Line 258 reads `self._economy.food_per_pop_per_turn`, which does not exist (PROJ-286 deleted it). The read-only shim is `population_food_resource` (a string), not the float property the editor needs. PROJ-286/plan.md defers fix to PROJ-289; PROJ-289/decisions.md does not list it in scope. Orphaned.

SAFE: view/empire/race_registry shims are intentional fallbacks with documented retirement. _get_race_config skips are deliberate per PROJ-287 decisions.

---

### Q3: Equivalence test coverage

Test: `tests/integration/strategy/test_growth_rate_equivalence.py` (158 lines, 14 cases)

Matrix: food_ratio ∈ {0.0, 0.5, 1.0}, happiness ∈ {0.5, 1.5}, P/K_eff ∈ {under_pop, over_pop}. Total: 3 × 2 × 2 = 12 scenarios + 1 edge case.

Verdict: EXCELLENT. Both `PopulationEngine._grow_species()` and `projected_growth_rate()` exercised per scenario. Starvation, underfeeding, ideal, unhappy, content, under and over population covered. A sign flip on decline_term would be caught (over-population growth would reverse).

Duplication is well-defended. No drift risk.

---

### Q4: Hardcoded factor lists

Finding: NO HARDCODED LISTS. Registry is correctly used.

`game/strategy/formulas/habitability.py:75` iterates `FACTOR_REGISTRY.items()` dynamically. No hardcoded "gravity", "temperature", "pressure" in calculations. Adding a new factor requires only `habitability_factors.py:FACTOR_REGISTRY` update.

PROJ-283's factor registry is the real abstraction, not a facade bandaid.

---

## Findings

### Finding 1: FoodAllocationEditor Runtime Defect

**Severity:** Critical

**Location:** `game/ui/screens/food_allocation_editor.py:258`

**What's wrong:** Calls `compute_consumption_preview(pop, allocation, self._economy.food_per_pop_per_turn)`, but `EconomyConfig` no longer has `food_per_pop_per_turn` attribute (deleted PROJ-286). The shim at line 72-76 is `population_food_resource` (string), not the float property needed. Runtime AttributeError if editor opens.

**Evidence:** PROJ-286/plan.md:38 defers to "PROJ-289's UI migration". PROJ-289/decisions.md does not list FoodAllocationEditor.

**Recommended fix:** PROJ-289 must migrate editor to iterate `economy.population_consumption` dict and show per-resource previews, or add temporary `food_per_pop_per_turn` shim (violates CLAUDE.md Rule 3).

---

### Finding 2: Direct UI Import of Engine Class

**Severity:** Major

**Location:** `game/ui/panels/empire_treasury_panel.py:19`, `game/ui/screens/empire_panel_window.py:18`

**What's wrong:** UI directly imports `EmpireEconomyCalculator` from `game.strategy.engine.*`. Should import from strategy **services** facade per CLAUDE.md Rule 3 and `docs/01_ARCHITECTURE.md`. Not a new violation, but unchallenged.

**Recommended fix:** Create `game/strategy/services/empire_economy_service.py` facade and import from there.

---

### Finding 3: Shim Ownership Ambiguity

**Severity:** Minor

**Location:** PROJ-289 scope boundary

**What's wrong:** PROJ-286 defers FoodAllocationEditor to "PROJ-289 UI migration", but PROJ-289/decisions.md does not mention it. Handoff documentation incomplete.

**Recommended fix:** Add explicit acceptance or deferral to PROJ-289/decisions.md.

---

## False Positives

- `empire.race_config` direct read in engine resolvers: Deliberate per PROJ-287/decisions.md.
- `EconomyConfig.population_food_resource` shim: By design; working; safe.
- `view=None`/`empire=None`/`race_registry=None`: Intentional; documented; safe.
- Equivalence test matrix: 12 cells sufficient; duplication well-defended.
