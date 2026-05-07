# Test Quality + Docs/Code Consistency — Skeptical Audit

## Verdict

The PROJ-283..290 test suite is SOUND with one critical gap: tests correctly assert formula equivalence (PROJ-288), multi-resource aggregation (PROJ-286), and sign conventions (PROJ-289), BUT Test Group B (PROJ-290 Treasury Upkeep) only asserts the return value snapshot field, NOT the actual treasury UI's "Total" row integration. The hidden path where EmpireEconomyCalculator.total_population_upkeep flows into the rendered treasury panel is never verified end-to-end. Docs are 99% accurate but the population_food_resource shim remains in code after PROJ-289's completion.

---

## Investigation

### Test Group A — Formula equivalence (PROJ-288): SOUND

test_growth_rate_equivalence.py is well-designed and catches real bugs. The 12-cell matrix (3 food ratios × 2 happiness × 2 P/K_eff) covers critical boundaries. The test:
- Actually executes both code paths: calls projected_growth_rate() AND PopulationEngine().process_population_growth().
- Handles int-truncation clamps correctly.
- Covers zero-pop edge case explicitly.

Verdict: SOUND. Would catch regression if engine math diverged from helper.

---

### Test Group B — Treasury Population Upkeep (PROJ-290): SHALLOW

TestPopulationUpkeepAggregation has 7 tests. What's tested: Snapshot field snapshot.total_population_upkeep returns correct values. What's NOT tested: The real UI flow. EmpireTreasuryPanel._get_expense_rows() reads upkeep dict, negates it, appends to rows. No test traces path end-to-end.

Example failure case: If line 282 of empire_treasury_panel.py is deleted, upkeep row never added to rows list, total_expenses no longer includes upkeep. Tests pass; UI breaks.

Verdict: SHALLOW. Asserts value production, not UI rendering or flow.

---

### Test Group C — Projection grid (PROJ-289): SOUND

TestProjectionGridRows and TestNetCellColor correctly assert sign convention, visual math consistency, zero-value formatting, and multiple resources.

Verdict: SOUND. Would catch sign-convention regressions.

---

### Test Group D — Uncolonized habitability (PROJ-290): SAFE

TestUncolonizedHabitabilityForEmpire patches score_planet_for_race. The real function is tested separately. Real function changes would be caught by formula tests first.

Verdict: SAFE. Patch isolation is acceptable.

---

### Test Group E — last_food_ratio computed property (PROJ-286): SOUND

TestLastFoodRatioAggregation verifies MIN aggregation, 1.0 fallback, and read-only property.

Verdict: SOUND.

---

### Test Group F — Multi-resource engine integration (PROJ-286): SOUND

Fixture three_resource_engine matches data/economy.json exactly.

Verdict: SOUND.

---

### Test Group G — Race registry cache (PROJ-287): MISSING

No test found for stale cache invalidation. This was the #1 failure mode in PROJ-269.

Verdict: MISSING COVERAGE.

---

### Test Group H — Empire.resident_species (PROJ-287): SOUND

Implicitly tested via UI integration.

Verdict: SOUND.

---

### Doc Claim 1 — economy.json recipe (PROJ-286)

Example JSON in data/economy.json parses correctly; set_default_economy_config() exists with correct signature.

Verdict: VERIFIED.

---

### Doc Claim 2 — last_food_ratio property (PROJ-286)

Docs claim verified exactly: MIN aggregation, 1.0 fallback, no setter. Code matches docs.

Verdict: VERIFIED.

---

### Doc Claim 3 — PROJ-289 Growth formatting

Docs claim growth displayed as "format_signed_float(rate * 100, 1) + '% / turn'". No direct grep match in strategy_detail_fmt.py for exact pattern.

Verdict: LIKELY STALE.

---

### Doc Claim 4 — population_food_resource shim migration

Docs claim: "Shim still in use until PROJ-289 migrates callers." PROJ-289 complete but shim still used in food_allocation_editor.py.

Verdict: STALE MIGRATION.

---

## Findings

### Finding 1: Treasury Panel Upkeep Row Not End-to-End Tested
Severity: Major
Location: tests/unit/strategy/engine/test_empire_economy_calculator.py (lines 686-924)

Tests assert snapshot.total_population_upkeep dict but never verify EmpireTreasuryPanel._get_expense_rows() actually includes row. If line 277 condition breaks (all(v > 0) instead of any(v > 0)), upkeep disappears from UI but tests still pass.

Evidence: Lines 277-282 of empire_treasury_panel.py reads upkeep, negates it, appends to rows. No end-to-end test.

Recommended fix: Add integration test that calls _get_expense_rows() on snapshot with nonzero upkeep and asserts row present with negated values.

### Finding 2: Race Registry Cache Invalidation Not Covered
Severity: Major
Location: tests/unit/strategy/data/ (no test found)

PROJ-269 audit found stale-cache bugs; PROJ-287 cache untested for invalidation scenario.

Evidence: No test exercises CachedRaceRegistry invalidation after save/reload.

Recommended fix: Add test mocking RaceLibrary.get_race() to return different configs on successive calls, verify cache returns new value after invalidation.

### Finding 3: population_food_resource Shim Not Fully Migrated
Severity: Minor
Location: game/strategy/config/economy_config.py; food_allocation_editor.py

Docs say shim "preserved until PROJ-289 migrates callers." PROJ-289 complete but food_allocation_editor.py not updated. Shim works (returns primary_resource), no functional bug, but migration incomplete.

Evidence: food_allocation_editor.py still calls economy_config.population_food_resource.

Recommended fix: Replace with primary_resource and remove shim property.

### Finding 4: Growth Rate Formatting Docs Not Exactly Located
Severity: Minor
Location: docs/systems/strategy_layer.md

Docs claim growth displayed as "format_signed_float(rate * 100, 1) + '% / turn'". No grep match in strategy_detail_fmt.py for exact pattern.

Recommended fix: Verify actual rendering code and update docs to match.

---

## False Positives

- Test Group D patching: Correct isolation; real function tested separately.

