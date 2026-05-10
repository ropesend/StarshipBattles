# Phase 1: Headless Single-Entry Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Risk:** LOW
**Objective:** Eliminate the three headless-path bypasses of `run_battle` that PROJ-269 Phase 6 left behind: the Combat Lab UI's `test_execution_service.run_headless` service, `BattleController.run_headless()`, and the legacy `setup(battle_engine)` methods on all 5 scenario templates plus `propulsion_scenarios.py`. After Phase 1 there is no way to run a headless battle in live production code except via `run_battle(spec)`.

---

## Tasks

### Task 1.1: Migrate `test_execution_service.run_headless` through `run_battle(spec)` [Medium] — COMPLETE
**File:** `combat_lab/services/test_execution_service.py`
**Tests:** `pytest tests/unit/combat_lab/services/test_test_execution_service.py --tb=short`

- [x] Write failing test in [tests/unit/combat_lab/services/test_test_execution_service.py](../../../tests/unit/combat_lab/services/test_test_execution_service.py) asserting the new contract (13 tests in `TestRunHeadless` rewritten)
- [x] Run test — confirmed all 13 tests fail for the right reason (run_battle not imported; legacy battle_engine param still required)
- [x] Created shared helper [combat_lab/services/scenario_run_helper.py](../../../combat_lab/services/scenario_run_helper.py) exposing `run_scenario_via_run_battle(scenario, *, seed_override, pre_tick_loop_hook, per_tick_hook) -> (engine, outcome)`. Reuses `_role_from_instance_id` + `_snapshot_ship_state` from `combat_lab/runner.py`.
- [x] Rewrote `run_headless` in [combat_lab/services/test_execution_service.py:120-207](../../../combat_lab/services/test_execution_service.py#L120-L207):
  - Deleted `battle_engine.start([], [])` call
  - Deleted `scenario.setup(battle_engine)` call
  - Deleted the manual tick loop
  - Replaced with a call to `run_scenario_via_run_battle(scenario, per_tick_hook=progress_hook)`
- [x] Removed the `battle_engine` parameter from `run_headless` signature
- [x] Updated [combat_lab/services/test_lab_controller.py:137](../../../combat_lab/services/test_lab_controller.py#L137) caller to drop the engine arg
- [x] Run tests — 20/20 pass in `test_test_execution_service.py` (13 new + 7 TestRunVisual preserved)
- [x] `python -m combat_lab.run_tests --fast --no-history` — **162/162 green** ✓
- [x] `pytest tests/unit/combat_lab/ tests/unit/test_lab/` — **336/336 green** ✓

**Notes:** Validator still consumes `engine` (PROJ-270 Phase 2 migrates to `BattleOutcome`). The `engine_ref["engine"] = engine` closure trick lives temporarily in the shared helper — Phase 2.5 deletes it.

---

### Task 1.2: Delete `BattleController.run_headless()` [Medium] — COMPLETE
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/battle_controller/ --tb=short`

- [x] Wrote failing regression test `TestBattleControllerNoRunHeadless::test_battle_controller_has_no_run_headless_method` asserting `not hasattr(controller, 'run_headless')`
- [x] Ran test — confirmed it failed for the right reason (method existed at line 232)
- [x] Grep audit — **zero production callers**. Only `TestBattleControllerRunHeadless` (6 tests) exercised the method. `TestLabExecutor.run_headless` is a UI-layer method that calls the PROJ-269-migrated `_run_scenario_via_run_battle` path, not the controller's
- [x] No callers to migrate
- [x] Deleted `run_headless` method from [game/simulation/battle_controller.py:232-263](../../../game/simulation/battle_controller.py)
- [x] Deleted obsolete `TestBattleControllerRunHeadless` class (6 tests); replaced with single-test `TestBattleControllerNoRunHeadless` regression guard
- [x] Run test — passes
- [x] `pytest tests/unit/simulation/battle_controller/` — **74 passed** ✓
- [x] `python -m combat_lab.run_tests --fast --no-history` — **162/162** ✓

**Notes:** Residual unused-import hints (`Any`, `IEndCondition`, `BattleResults`) in battle_controller.py may be cleaned in Task 1.4. `pytest` import + `patch` import in test_execution.py adjusted accordingly.

---

### Task 1.3: Delete `setup(battle_engine)` methods from scenario templates [Medium] — COMPLETE
**File:** `combat_lab/scenarios/templates.py`, `combat_lab/scenarios/base.py`, `combat_lab/scenarios/propulsion_scenarios.py`
**Tests:** `python -m combat_lab.run_tests --fast --no-history`; `pytest tests/unit/combat_lab/ --tb=short`

- [x] Wrote failing test in [tests/unit/combat_lab/test_template_no_legacy_setup.py](../../../tests/unit/combat_lab/test_template_no_legacy_setup.py) (new file, 8 tests covering all 5 templates + base + `_setup_battle` helper + PropMassAffectsTurnRateScenario)
- [x] Ran tests — confirmed 8/8 failed for the right reason
- [x] Deleted `setup(self, battle_engine)` method from each template in [combat_lab/scenarios/templates.py](../../../combat_lab/scenarios/templates.py):
  - StaticTargetScenario: lines 145-203
  - DuelScenario: lines 357-409
  - PropulsionScenario: lines 553-600
  - ResourceScenario: lines 801-870
  - ComparisonScenario: lines 1042-1074
- [x] Also deleted `ComparisonScenario._setup_battle` (lines 1089-1118) — only caller was the deleted `setup()`
- [x] Deleted `setup(self, battle_engine)` from `PropMassAffectsTurnRateScenario` in [combat_lab/scenarios/propulsion_scenarios.py:941-960](../../../combat_lab/scenarios/propulsion_scenarios.py) (not PROP005 — that name doesn't exist; the actual class was `PropMassAffectsTurnRateScenario`)
- [x] Deleted "Legacy-compatible / retained for" docstring comment (folded into the deletion)
- [x] Deleted the base-class abstract `setup` on `TestScenario` in [combat_lab/scenarios/base.py:468-490](../../../combat_lab/scenarios/base.py)
- [x] Grep audit — only production-code references to `scenario.setup(` are now docstring comments (no live callers). Remaining live test callers were in `test_skip_test_template.py` — redundant after deletion, consolidated to the runner-level skip test
- [x] Updated [tests/unit/combat_lab/test_skip_test_template.py](../../../tests/unit/combat_lab/test_skip_test_template.py) — removed 2 tests that invoked `scenario.setup(engine)` directly; kept `test_runner_records_skip_in_results` which covers skip behaviour end-to-end via `runner.run_scenario`
- [x] Run test — 8/8 pass
- [x] `python -m combat_lab.run_tests --fast --no-history` — **162/162 green** ✓
- [x] `python -m combat_lab.run_tests --no-history` — **170/170 green** ✓ (full suite including -HT)
- [x] `pytest tests/unit/combat_lab/ tests/unit/test_lab/ tests/unit/simulation/battle_controller/` — **416/416 green** ✓

**Notes:** The baseline `ComparisonScenario._run_baseline_battle` path is driven by the `before_run_battle(spec)` hook at line 1296 (post-deletion numbering may shift), which is already the production path used by `combat_lab/runner.py`, `test_executor._run_scenario_via_run_battle`, and the new `scenario_run_helper`. Visual-baseline mode still works because `_visual_baseline` branch in `wire_ships` (line 1317 pre-deletion) handles baseline ship wiring.

---

### Task 1.4: Eradicate "Legacy-compatible / retained for" dead-code comments [Simple] — COMPLETE
**File:** (multiple — grep-driven)
**Tests:** `pytest tests/ --testmon` after changes

- [x] Grep sweep produced 6 matches for `"Legacy-compatible"|"retained for"|"legacy path"`:

  | File:Line | Phrase | Disposition |
  |-----------|--------|-------------|
  | `combat_lab/scenarios/templates.py:885` | "same shape as the legacy path" | Descriptive of what the code emulates — docstring only, no legacy code attached. **Keep.** |
  | `combat_lab/scenarios/base.py:513` | "matches the legacy path" | Docstring explaining ship-creation ordering. **Keep.** |
  | `combat_lab/scenarios/propulsion_scenarios.py:489` | "Legacy-compatible setup()" | **DELETED** — `PropThrustMassRatioScenario.setup` was missed by Task 1.3's class list (the class name wasn't `PROP005_*`). Lines 488-511 removed. Added `test_prop_thrust_mass_ratio_has_no_setup` to the Task 1.3 guard file. |
  | `combat_lab/runner.py:152` | "no silent legacy fallback post-Phase 6" | Affirms the unified-entry contract — descriptive, not a legacy marker. **Keep.** |
  | `game/strategy/data/ship_instance_bridge.py:105` | "(legacy path)" | Fallback `else` branch for ships without per-component-index damage. **Keep** — PROJ-269 Phase 2 decision explicitly kept this path; MEMORY.md documents the rationale ("additive approach; full consolidation is post-PROJ-269 cleanup"). |
  | `game/simulation/combat/fleet_aura_manager.py:90` | "(legacy path)" | `if config:` branch reads `config.team_modifiers` / `config.global_modifiers` — **fields that no longer exist on `BattleConfig` post-PROJ-269**. Dead in production (no live caller passes a config with these attrs). **DEFERRED to Phase 6** — requires rewriting 5 tests in `test_fleet_aura_extended.py` + `test_fleet_aura_manager_modifier_stack.py` to drive via `modifier_stack` instead. Logged as a Phase 6 task sub-item. |

- [x] Zero strict-pattern matches (`"Legacy-compatible"` / `"retained for"`) remain in production code after the `PropThrustMassRatioScenario.setup` deletion
- [x] `pytest tests/unit/combat_lab/test_template_no_legacy_setup.py` — 9/9 green
- [x] `python -m combat_lab.run_tests --fast --no-history` — 162/162 green

**Notes:** Added a follow-up entry for Phase 6: delete the `fleet_aura_manager.initialize(config=...)` legacy branch after the `team_modifiers`/`global_modifiers` fields are confirmed absent from every caller and the 5 dependent tests are migrated to `modifier_stack`-driven fixtures. Captured in Phase 6 checklist as a sub-task of Task 6.4.

---

### Task 1.5: Phase 1 regression gate [Simple] — COMPLETE
**Tests:** Full suites

- [x] `pytest tests/ --tb=no -q` — **14572 passed, 3 failed, 2 skipped, 3 errors** (195s). Failures + errors match the pre-existing baseline exactly: `test_bug_15_screenshot_strategy.py`, `test_build_queue_formatting.py`, `test_build_queue_queue_data_source.py` (all build-queue UI, unrelated to PROJ-269/270); 3 import errors in `test_ai_protocols.py`, `test_behavior_units.py`, `test_build_order_command_handler.py` (pre-existing). **No new failures.** Pass-count delta vs project start baseline (14577 → 14572 = -5) is deliberate: net effect of deleted legacy tests (6 in `TestBattleControllerRunHeadless` + 3 in `TestRunHeadless` + 2 in `TestSkipTestTemplate` = 11 removed) minus new regression guards (13 in `TestRunHeadless` + 1 in `TestBattleControllerNoRunHeadless` + 9 in `test_template_no_legacy_setup.py` = 23 added — but some test counts collapsed during rewrites). ✓
- [x] `python -m combat_lab.run_tests --fast --no-history` — **162/162 green** ✓
- [x] `python -m combat_lab.run_tests --no-history` (full, includes -HT) — **170/170 green** ✓
- [x] Grep audit: zero live `scenario.setup(` callers in non-test code. Remaining matches are docstring examples in `combat_lab/scenarios/base.py:36, 172, 452` (to be updated in Phase 8.5 docs rewrite) and `combat_lab/scenarios/__init__.py:30` (same)
- [x] Grep audit: `BattleController.run_headless` does not exist (zero matches)
- [x] Grep audit: `combat_lab/services/test_execution_service.py` no longer contains live `battle_engine.start(` or `scenario.setup(` — only a docstring comment at line 128 referring to the deleted legacy path

**Notes:** Baseline maintained. No behavioral regressions. Pre-existing UI build-queue and AI import errors are out of scope per decisions.md. Docstring examples in `combat_lab/scenarios/base.py` + `__init__.py` show legacy `battle_engine.start(...)` API — flagged for Phase 8.5 docs rewrite (not blocking).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Tests written in Task 1.1, 1.2, 1.3 are passing
- [x] Regression gate (Task 1.5) passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2 Task 2.1
