# PROJ-291 File Manifest

> Used for parallel-execution conflict detection with PROJ-292.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/engine/empire_economy_calculator.py | Production (MODIFY) | C1 fix — add `+ snapshot.total_population_upkeep.get(r, 0.0)` to the `total_expenses` summation at lines 147-150 |
| game/strategy/engine/happiness_engine.py | Production (MODIFY) | C3 fix — accept `race_registry: Optional[IRaceRegistry] = None` kwarg; rewrite `_get_race_config` to consult registry first, fall back to legacy single-race resolver, return None on mismatch (instead of returning the wrong race) |
| game/strategy/engine/population_engine.py | Production (MODIFY) | C3 fix — same pattern as happiness_engine.py |
| game/strategy/engine/turn_engine.py | Production (MODIFY) | C3 wiring — pass `race_registry=...` when constructing HappinessEngine + PopulationEngine. Resolution path mirrors how PROJ-285 already wires registry into HarvestingEngine + ProductionEngine |
| game/ui/screens/food_allocation_editor.py | Production (MODIFY) | C2 fix — rewrite `compute_consumption_preview` to take `population_consumption: Dict[str, float]` and return per-resource dict; update line 258 call site; rewrite UI to render per-resource preview cluster |
| game/strategy/config/economy_config.py | Production (MODIFY, conditional) | After C2 lands, grep for remaining `population_food_resource` callers; if zero, retire the shim; else leave it documented |
| Projects/active_projects/PROJ-287/decisions.md | Documentation (MODIFY) | Add forward-link noting PROJ-291 reverses the line-16 engine-deferral decision |
| docs/systems/strategy_layer.md | Documentation (MODIFY) | § Demographics Loop — note the engine retrofit; engines now consume IRaceRegistry like PROJ-285 already established for HarvestingEngine + ProductionEngine |
| docs/04_SERVICES.md | Documentation (MODIFY) | Race Registry section — add HappinessEngine + PopulationEngine to the consumers list |
| Projects/projects_index.md | Documentation (MODIFY) | After Phase 4 + manual smoke, move PROJ-283..290 from `Awaiting Verification` to `Archived`; add PROJ-291 + PROJ-292 entries |
| tests/unit/strategy/engine/test_empire_economy_calculator.py | Test (MODIFY) | Add `TestTreasuryTotalIncludesUpkeep` class — pins the C1 contract |
| tests/integration/strategy/test_treasury_panel_e2e.py | Test (NEW) | End-to-end test: build snapshot with non-zero upkeep, run `EmpireTreasuryPanel._get_expense_rows`, assert row presence + Total magnitude. Closes prior-audit M3 simultaneously |
| tests/unit/strategy/engine/test_happiness_engine.py | Test (MODIFY) | Add `TestMultiSpeciesViaRegistry` — registry-wired engine grows 2-species colony with each species using its own `base_happiness` |
| tests/unit/strategy/engine/test_population_engine.py | Test (MODIFY) | Add `TestMultiSpeciesViaRegistry` — same pattern, asserts each species' `base_reproduction_rate` is honoured |
| tests/unit/ui/screens/test_food_allocation_editor.py | Test (MODIFY) | Migrate all 13 broken fixtures to `EconomyConfig(population_consumption={...})`. Add new tests for the multi-resource preview rendering |
| Projects/active_projects/PROJ-291/findings/SUMMARY.md | Documentation (NEW — copied) | Move from `Temp Review Docs/SUMMARY.md` |
| Projects/active_projects/PROJ-291/findings/pipeline_reachability_skeptic.md | Documentation (NEW — copied) | Move from `Temp Review Docs/` |
| Projects/active_projects/PROJ-291/findings/state_cache_skeptic.md | Documentation (NEW — copied) | Move from `Temp Review Docs/` |
| Projects/active_projects/PROJ-291/findings/architecture_shims_skeptic.md | Documentation (NEW — copied) | Move from `Temp Review Docs/` |
| Projects/active_projects/PROJ-291/findings/merge_hazards_skeptic.md | Documentation (NEW — copied) | Move from `Temp Review Docs/` |
| Projects/active_projects/PROJ-291/findings/tests_docs_skeptic.md | Documentation (NEW — copied) | Move from `Temp Review Docs/` |

## Cross-project file overlap with PROJ-292

| File | This project | PROJ-292 phase | Sequencing |
|------|--------------|---------------|-----------|
| game/strategy/engine/empire_economy_calculator.py | C1 fix (1 line) | Phase 2 (M1 — wrap with empire_economy_service.py facade; doesn't modify the calculator itself) | Sequential — PROJ-291 lands first; PROJ-292 wraps it |
| docs/systems/strategy_layer.md | C3 doc note | Phase 6 (overall doc sweep) | Sequential — append-only, no conflict if PROJ-291 lands first |
| docs/04_SERVICES.md | C3 doc note | Phase 6 (M1 facade catalogue entry) | Sequential, append-only |
| Projects/projects_index.md | Status updates | Status updates | Sequential — last writer wins; both update different rows |
