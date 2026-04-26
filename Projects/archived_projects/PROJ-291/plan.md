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
| 2. C3 — Retrofit Happiness/PopulationEngine to consume IRaceRegistry | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. C2 — Migrate FoodAllocationEditor to multi-resource preview | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Docs + final suite + PROJ-283..290 sign-off handoff | Awaiting User Verification | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-19
**Active Phase:** ALL 4 PHASES CODE WORK COMPLETE — awaiting user manual smoke (Task 4.5) + Archive sign-off (Task 4.6)
**Last Action:** Phase 4 Tasks 4.1–4.4 complete.
- 4.1 Findings archive verified complete (6 audit reports + INDEX.md already present under findings/).
- 4.2 PROJ-287 decisions.md: appended a `2026-04-19 (PROJ-291 reversal)` row documenting the engine retrofit + link to PROJ-291/design.md.
- 4.3 docs/systems/strategy_layer.md § Demographics Loop: new `### Multi-species engine resolution (PROJ-291 Phase 2)` subsection; updated FoodAllocationEditor paragraph for the multi-resource preview; updated EconomyConfig paragraph for the shim retirement. docs/04_SERVICES.md Race Registry section: new "Consumers" subsection listing HappinessEngine, PopulationEngine, TurnEngine, GameSession.race_registry alongside the existing consumers.
- 4.4 Full sharded suite: **15113 tests | 15112 passed | 1 failed** (the expected long-standing `test_copy_designs_without_themes_preserves_original` theme-bleed flake — NOT a PROJ-291 regression). 13 food-editor failures gone (migrated by Phase 3). Net +13 from baseline.

**Previous Action:** Phase 3 (C2) complete. FoodAllocationEditor migrated to multi-resource preview. `compute_consumption_preview` signature changed from `(pop, allocation, food_per_pop_per_turn) -> float` to `(pop, allocation, population_consumption: Dict[str, float]) -> Dict[str, float]`. Editor's `_preview_text` now renders one segment per resource (single-resource economies look identical to the pre-migration UI). All 13 broken test fixtures migrated from `EconomyConfig(population_food_resource=..., food_per_pop_per_turn=...)` to `EconomyConfig(population_consumption={...})`. Added `TestMultiResourcePreview` class (5 tests) covering per-resource preview behavior. `population_food_resource` legacy shim retired — the only production consumer (editor line 104) now reads `economy_config.primary_resource` directly; the shim-test class in `test_economy_config.py` was deleted with a comment explaining the retirement. Targeted suite: `pytest tests/unit/ui/ tests/unit/strategy/ --ignore=tests/unit/quickstart/ --ignore=tests/unit/strategy/engine/test_build_order_command_handler.py` → 6380 passed, 0 regressions (auto-fixes prior-audit m4 alongside the retirement).

**Previous Action:** Phase 2 (C3) complete. Engines retrofitted to consume IRaceRegistry. `HappinessEngine.__init__` and `PopulationEngine.__init__` now accept optional `race_registry: Optional['IRaceRegistry'] = None` kwarg. Both `_get_race_config` resolvers now consult the registry first, then fall back to `empire.race_config` ONLY when the race_id matches the empire's primary race — returning None for non-primary species (instead of the pre-PROJ-291 silent wrong-race fallback). Added `TestMultiSpeciesViaRegistry` test classes (3 tests each) in `test_happiness_engine.py` and `test_population_engine.py` — all confirmed FAILING against pre-fix code. TurnEngine gained a `race_registry` kwarg that threads into its HappinessEngine + PopulationEngine lazy-init. GameSession owns a `race_registry` lazy property (creates `CachedRaceRegistry(RaceLibrary())` on first access) and passes it to TurnEngine in both `__init__` and `from_dict`. Two pre-existing PopulationEngine tests had `pop.race_id="human"` but `empire.race_config.race_id="human_happy"` / `"human_sad"` — they were implicitly relying on the wrong-race bug. Fixed their fixtures to use matching race_ids. Full strategy engine + integration suite: 1078 passed, 1 skipped (same pre-existing `test_build_order_command_handler.py` import error unrelated to PROJ-291).
**Next Action:** Tasks 4.5–4.7 are user-gated:
- **User manual smoke (Task 4.5):** (1) open FoodAllocationEditor on a 2-species colony — confirm no AttributeError, per-resource preview rows render, sliders respond; (2) open the Treasury panel on an empire with population — confirm Total row equals Tributes + Ships + Complexes + Population Upkeep; (3) run a turn on a 2-species colony (humans + voidari) with distinct race configs — confirm per-species growth rates and happiness values differ between species (PROJ-289 sub-block).
- **Archive sign-off (Task 4.6):** after user confirms smoke, update `Projects/projects_index.md` — move PROJ-283..290 from `Awaiting Verification` → `Archived`, mark PROJ-291 → `Awaiting Verification`, fix the line-1 `w# Projects Index` typo (prior-audit m17), then run `python Projects/scripts/validate_phase.py PROJ-291 4` for Task 4.7.
- After Task 4.7 passes, delete `Temp Review Docs/` (user confirmation required per decisions.md).

**Blockers:** User must perform manual-smoke pass before Archive sign-off. PROJ-292 Phase 2 can proceed immediately (no dependency on 4.5–4.7).

**Context for Next Agent:** All three Critical findings resolved in code + tests + docs. The remaining gate is the user's manual-smoke verification — do not close PROJ-283..290 without it. If new issues surface during manual smoke, open a new Phase 5 in this project (or a follow-up PROJ ticket) rather than scope-creeping Phase 4.

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
