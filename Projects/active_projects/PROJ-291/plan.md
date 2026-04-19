# PROJ-291: Audit Critical Fixes (PROJ-283..290 Sign-off Blocker)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-291` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-291 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. C1 — Treasury Total includes Population Upkeep + e2e test | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. C3 — Retrofit Happiness/PopulationEngine to consume IRaceRegistry | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. C2 — Migrate FoodAllocationEditor to multi-resource preview | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Docs + final suite + PROJ-283..290 sign-off handoff | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Phase 1 complete; ready to begin Phase 2
**Last Action:** Phase 1 (C1) complete. Added `TestTreasuryTotalIncludesUpkeep` (2 tests) at the end of `tests/unit/strategy/engine/test_empire_economy_calculator.py` — confirmed FAILING against the pre-fix code (`total_expenses[metals] = 0.0` vs expected `0.4`). Applied the one-line fix at `game/strategy/engine/empire_economy_calculator.py:151` adding `+ snapshot.total_population_upkeep.get(r, 0.0)` to the `total_expenses` summation. Added new e2e integration test `tests/integration/strategy/test_treasury_panel_e2e.py::TestTreasuryPanelTotalRowEndToEnd` (2 tests) that round-trips calculator → snapshot → `EmpireTreasuryPanel._get_expense_rows()` and pins both the upkeep-row presence + Total-row magnitude (closes prior-audit M3). All 26 tests in `test_empire_economy_calculator.py` pass; targeted strategy engine + integration suite is 1072 passed, 1 skipped. The lone collection error (`test_build_order_command_handler.py` ImportError on `create_auto_load_population_order`) is pre-existing (verified by stashing PROJ-291 changes and re-running) — unrelated to PROJ-291 scope.
**Next Action:** Phase 2 Task 2.1 — read `game/strategy/engine/harvesting_engine.py` for the canonical `race_registry: Optional[Any] = None` kwarg + None-fallback pattern (PROJ-285's reference pattern). Then Task 2.2 — write failing tests in `tests/unit/strategy/engine/test_happiness_engine.py::TestMultiSpeciesViaRegistry` proving the wrong-race fallback bug. Then Task 2.3 — same for `PopulationEngine`. Then Task 2.4-2.5 — implement the registry consult on both engines (return None on mismatch when registry is absent, instead of returning the wrong race_config). Then Task 2.6 — wire the registry through `turn_engine.py` (mirror how PROJ-285 already wires `HarvestingEngine` + `ProductionEngine`; grep for `HappinessEngine(` to find the construction site).
**Blockers:** None. PROJ-292 may begin its Phase 2 (the empire_economy_service.py facade that wraps EmpireEconomyCalculator) since PROJ-291 Phase 1 has now landed.
**Context for Next Agent:** Read `findings/SUMMARY.md` first if not already loaded. Phase 2 reverses PROJ-287's decisions.md line 16 deferral — that's a forward-link for Phase 4 Task 4.2 to add to PROJ-287/decisions.md. The third behaviour change matters: when `race_registry is None` AND `race_id != empire.race_config.race_id`, the legacy fallback now returns `None` instead of returning the wrong `race_config`. The empire's `process_*` loops already have `if race_config is None: return` early-outs, so the species is gracefully skipped. Pin this with Test 3 in Tasks 2.2 + 2.3.

## Overview

Resolve the three Critical findings from the dual cross-project audit of PROJ-283..290 so those 8 projects can move from `Awaiting Verification` → `Archived`. The Critical findings are: (C1) Treasury Total silently excludes Population Upkeep — user sees mathematically wrong totals; (C2) FoodAllocationEditor crashes at runtime because PROJ-286 deleted the `food_per_pop_per_turn` field the editor still reads; (C3) HappinessEngine + PopulationEngine return the empire's primary `race_config` for ANY species race_id, so multi-species colonies (now reachable post-PROJ-284/286/289) compute happiness/growth using the wrong base values.

## Goals

- **C1 fix**: `EmpireEconomyCalculator.calculate()` includes `total_population_upkeep` in `total_expenses`. New e2e test pins the contract so this can't recur (closes prior-audit M3 simultaneously).
- **C2 fix**: `FoodAllocationEditor` rewritten to iterate `economy.population_consumption` and show per-resource preview. All 13 broken test fixtures migrated to the post-PROJ-286 `EconomyConfig(population_consumption={...})` schema. The `population_food_resource` shim is retired (auto-fix for prior-audit m4).
- **C3 fix**: `HappinessEngine` + `PopulationEngine` accept an optional `race_registry: IRaceRegistry` kwarg (mirrors PROJ-285's pattern on `HarvestingEngine`/`ProductionEngine`). When supplied, the engines resolve `pop.race_id` via `registry.get_race(race_id)` and grow each species correctly. When None, fall back to the existing single-race resolver (preserves pre-PROJ-291 test fixtures). New multi-species growth + happiness tests pin the registry path.
- Full sharded suite green except the long-standing `test_copy_designs_without_themes_preserves_original` flake. Net new tests: ~30. Net failing tests dropped: ~13 (the food editor cluster).
- PROJ-283..290 documented as ready for sign-off; durable archive of the audit reports under `Projects/active_projects/PROJ-291/findings/`.

## Scope

**In:**
- `game/strategy/engine/empire_economy_calculator.py` (1-line fix to `total_expenses` aggregation).
- `game/strategy/engine/happiness_engine.py` + `population_engine.py` + `turn_engine.py` (registry threading; mirror PROJ-285 pattern).
- `game/ui/screens/food_allocation_editor.py` + `tests/unit/ui/screens/test_food_allocation_editor.py` (editor migration + 13 fixture rewrites).
- `game/strategy/config/economy_config.py` (retire `population_food_resource` shim if no remaining callers; verify with grep first).
- New tests: `tests/unit/strategy/engine/test_empire_economy_calculator.py::TestTreasuryTotalIncludesUpkeep`, `tests/integration/strategy/test_treasury_panel_e2e.py`, `tests/unit/strategy/engine/test_happiness_engine.py::TestMultiSpeciesViaRegistry`, `tests/unit/strategy/engine/test_population_engine.py::TestMultiSpeciesViaRegistry`.
- Docs updates: `docs/systems/strategy_layer.md` § Demographics Loop notes the retrofit; `docs/04_SERVICES.md` Race Registry section adds the engine consumers; PROJ-287/decisions.md notes the deferral was reversed.
- Move `c:/Developer/StarshipBattles/Temp Review Docs/*.md` → `Projects/active_projects/PROJ-291/findings/` for durable storage.

**Out:**
- All Major + High + Minor findings from the dual audit — those go to PROJ-292.
- The PROJ-289 `view`-kwarg UX regression (PROJ-292 Phase 1).
- The UI→engine layer violation (PROJ-292 Phase 2).
- The CachedRaceRegistry mtime/invalidation work (PROJ-292 Phase 3).

## Key Files

| Component | File Path |
|-----------|-----------|
| C1 fix site | [game/strategy/engine/empire_economy_calculator.py:144-151](game/strategy/engine/empire_economy_calculator.py#L144-L151) |
| C3 fix sites | [game/strategy/engine/happiness_engine.py:77-95](game/strategy/engine/happiness_engine.py#L77-L95), [game/strategy/engine/population_engine.py:146-180](game/strategy/engine/population_engine.py#L146-L180) |
| C3 wiring | [game/strategy/engine/turn_engine.py](game/strategy/engine/turn_engine.py) (sub-engine instantiation site — find by grep `HappinessEngine(`) |
| C3 pattern reference | [game/strategy/engine/harvesting_engine.py](game/strategy/engine/harvesting_engine.py) — already accepts `race_registry: Optional[Any] = None` |
| C2 fix site | [game/ui/screens/food_allocation_editor.py:258](game/ui/screens/food_allocation_editor.py#L258) |
| C2 broken fixtures | [tests/unit/ui/screens/test_food_allocation_editor.py](tests/unit/ui/screens/test_food_allocation_editor.py) (13 failures, all on `EconomyConfig(population_food_resource=..., food_per_pop_per_turn=...)`) |

## Related Documents
- [design.md](design.md) — Architectural rationale (engine retrofit shape, editor migration approach)
- [decisions.md](decisions.md) — Decisions log
- [manifest.md](manifest.md) — File manifest for parallel-work safety
- [findings/SUMMARY.md](findings/SUMMARY.md) — Dual-audit summary (move-in copied from `Temp Review Docs/SUMMARY.md` during Phase 4)

## Related Projects

| PROJ | Relationship |
|------|--------------|
| PROJ-283..290 | Gated by this project — `Awaiting Verification` → `Archived` after PROJ-291 + manual smoke |
| PROJ-287 | This project REVERSES PROJ-287's decisions.md line 16 deferral (engines now consume IRaceRegistry) — log the reversal in `Projects/active_projects/PROJ-287/decisions.md` |
| PROJ-292 | Sibling — High/Major/Minor cleanups, runs in parallel after Phase 2 of this project lands (file overlaps are minimal) |
| PROJ-285 | Pattern source — the `race_registry: Optional[Any] = None` kwarg shape on HarvestingEngine/ProductionEngine is what C3 mirrors |
| PROJ-286 | Schema source — the broken `food_per_pop_per_turn` reference in the editor is C2's root cause |

## Verification
- [ ] All phase checklists complete
- [ ] `python -m pytest tests/unit/ui/screens/test_food_allocation_editor.py -v` shows 0 failures (was 13)
- [ ] `python -m pytest tests/integration/strategy/test_treasury_panel_e2e.py -v` green
- [ ] `python -m pytest tests/unit/strategy/engine/test_empire_economy_calculator.py::TestTreasuryTotalIncludesUpkeep -v` green
- [ ] `python -m pytest tests/unit/strategy/engine/test_happiness_engine.py tests/unit/strategy/engine/test_population_engine.py -v` green (including new multi-species tests)
- [ ] `python Tools/test_sharded/test_sharded.py` — expect ~15080 tests, ~1 known failure (the long-standing theme-bleed flake; net 13 fewer failures than baseline)
- [ ] Manual scenarios:
  - [ ] Open the FoodAllocationEditor on a 2-species colony — no `AttributeError`; per-resource preview rows display.
  - [ ] Treasury panel on an empire with population — Total row equals Tributes + Ships + Complexes + Upkeep.
  - [ ] 2-species colony with humans + voidari — both species visibly grow at independent rates after a turn passes (verified via per-species sub-block in PROJ-289 panel).
- [ ] User verified end-to-end.
- [ ] PROJ-283..290 statuses moved Awaiting Verification → Archived in `Projects/projects_index.md`.
- [ ] `Temp Review Docs/` directory deleted after the move to `findings/` is confirmed.
