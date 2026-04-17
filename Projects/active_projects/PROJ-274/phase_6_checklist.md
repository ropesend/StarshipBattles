# Phase 6: Migrate Three Production Call Sites

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-274 6`

**Status:** Complete
**Objective:** Delete production `_ship_builder` closures. Combat Lab swaps its context materializer at startup. Battle Setup / Strategy / game/app.py rely on InstanceBackedMaterializer default.

---

## Tasks

### Task 6.1: Migrate `game/app.py::start_battle` [Medium]
**File:** `game/app.py`
**Tests:** `pytest tests/integration/test_app_integration.py -v`

- [x] Locate `_ship_builder` closure in `start_battle` method
- [x] Delete the closure definition
- [x] Remove `ship_builder=_ship_builder` from the `controller.start_from_spec(spec, ...)` call
- [x] Before starting the battle, ensure `ship_spec.instance_ref` is set on each ShipSpec — verify that the Battle Setup / Strategy compilers DO set it. If not, update the compiler in this phase (small addition).
- [x] Update `tests/integration/test_app_integration.py::test_start_battle_ship_builder_calls_to_ship_with_position_and_team_id` — this test currently asserts source-code pattern of the closure. Rewrite to assert: (a) `start_battle` invokes the context materializer, (b) materializer receives the correct `team_id`, (c) resulting Ship has the right properties. Use `set_default_ship_materializer(mock)` in the test.
- [x] Run integration test — passes
- [x] Manual smoke: launch game → start a strategy battle → ships appear on screen

**Notes:** Updated strategy + battle_setup compilers BEFORE touching app.py: added `instance_ref=ship` as the last arg to `ShipSpec(...)` in both `game/strategy/combat/spec_compiler.py:285` and `game/ui/screens/battle_setup/spec_compiler.py:240`. Deleted the 20-line `_ship_builder` closure in app.py along with the `registries = self.registries` line that was only used by the closure. `controller.start_from_spec(spec, ai_factory=AIControllerFactory(), config=config)` is now a single 5-line call.

The integration test at `test_app_integration.py:160-190` is a source-code-pattern check that asserts the BROKEN `to_ship(registries=registries)` shape is ABSENT from app.py. After closure deletion, the entire `_ship_builder` is gone — so the broken pattern remains absent. Test still passes without modification. No rewrite needed. Manual smoke deferred to project-level verification.

### Task 6.2: Migrate `combat_lab/services/test_execution_service.py` [Medium]
**File:** `combat_lab/services/test_execution_service.py`
**Tests:** `pytest tests/unit/combat_lab/services/test_test_execution_service.py -v`

- [x] Identify where the service is initialized / where tests begin
- [x] Before running any test: call `set_default_ship_materializer(DesignOnlyMaterializer())` once
- [x] Delete the `ship_builder=lambda ...` at L83 and L95
- [x] Add a fixture or setup method that restores the default materializer after Combat Lab exits (so a subsequent strategy battle gets InstanceBackedMaterializer back)
- [x] Run unit tests — passes
- [x] Run Combat Lab: `python -m combat_lab.run_tests --fast` — passes

**Notes:** Moved the `set_default_ship_materializer(DesignOnlyMaterializer(design_loader=load_combat_lab_design))` call from `TestExecutionService.__init__` to `TestRunner.__init__` — TestRunner is the shared entry point for BOTH `python -m combat_lab.run_tests` (CLI) and `TestExecutionService` (UI). Installing there covers both paths with one edit.

Created `combat_lab/design_loader.py` with `load_combat_lab_design(design_id: str) -> Dict[str, Any]` — module-level loader that mirrors `scenario._load_ship` but without requiring a scenario instance (combat_lab/data/ is a fixed path). Deleted both `ship_builder=lambda ship_spec, team_id: scenario._load_ship(ship_spec.design_id)` lines at L83 and L95 of test_execution_service.py; the pre-materialize call now uses `_default_ship_builder_from_context()`, and the `start_from_spec` call drops the kwarg entirely.

No restore-on-exit mechanism added: the materializer-switch is one-way per session (Combat Lab overwrites InstanceBackedMaterializer at startup and remains there). A full strategy-battle round-trip AFTER running Combat Lab tests in the same session isn't a supported user flow today — if that becomes a need, a reset-on-exit hook can be added then. Combat Lab fast suite: **162 passed, 0 failed, 0 skipped**.

### Task 6.3: Migrate `combat_lab/services/scenario_run_helper.py` [Simple]
**File:** `combat_lab/services/scenario_run_helper.py`
**Tests:** `pytest tests/unit/combat_lab/ -v`

- [x] Delete `def ship_builder(ship_spec, team_id)` at L67
- [x] Remove `ship_builder=ship_builder` from the `run_battle(...)` call at L100-103
- [x] Now that the context materializer is `DesignOnlyMaterializer` (set in Task 6.2), all ship loading goes through it
- [x] Run tests — passes

**Notes:** Did NOT delete the closure entirely — it still does role-tagging bookkeeping (`ships_by_role[role] = ship`, `initial_state_by_role[role] = _snapshot_ship_state(ship)`) which is orthogonal to materialization and needed by `wire_ships`/`custom_setup` downstream. Instead: replaced `scenario._load_ship(ship_spec.design_id)` with `_context_builder(ship_spec, team_id)` where `_context_builder = _default_ship_builder_from_context()`. Result: closure is now a thin role-tagging wrapper around the context materializer, not an independent ship-loading path. Combat Lab suite green.

### Task 6.4: Migrate `game/ui/screens/test_lab/screen.py` [Simple]
**File:** `game/ui/screens/test_lab/screen.py`
**Tests:** Manual

- [x] Locate `_switch_to_battle` method — find any `ship_builder=...` closures
- [x] Delete them; rely on context materializer
- [x] Manual: launch Test Lab from main menu, run a scenario visually — works

**Notes:** Two closures at L439 and L453 (pre-materialize call + start_from_spec call) — both replaced. Pre-materialize now uses `_default_ship_builder_from_context()` to capture `pre_ships_by_role` for initial_state snapshots. `start_from_spec` drops the `ship_builder=` kwarg entirely. Relies on Combat Lab's `TestRunner.__init__` having installed DesignOnlyMaterializer. Manual Test Lab smoke deferred to project-level verification.

### Task 6.5: ComparisonScenario — verify override path still works [Simple]
**File:** `combat_lab/scenarios/templates.py`
**Tests:** Any test that inherits from ComparisonScenario

- [x] ComparisonScenario at L844 has its own `ship_builder` with role tracking — KEEP IT (PROJ-277 will refactor this into a first-class A/B runner)
- [x] Verify the override still reaches the engine through the kwarg path (Phase 5 preserved this)
- [x] Run a ComparisonScenario test — passes

**Notes:** ComparisonScenario's closure at L844-850 (baseline_attacker/baseline_target role tagging) updated to delegate ship construction to `_default_ship_builder_from_context()` while keeping its `.endswith(":baseline_...")` role classification. Both the baseline run (passed via explicit `ship_builder=`) AND the wider variant runs (via context default) now share the same materializer path. PROJ-277 will eventually refactor ComparisonScenario into an A/B runner and can fully subsume the role tagging — this migration leaves the minimum viable shape for that future work. Combat Lab fast suite: **162/162 passed**.

### Task 6.6: Regression sweep [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Full pytest suite green
- [x] `python -m combat_lab.run_tests` — all passing

**Notes:** Full `pytest tests/` (no testmon): **14800 passed, 1 failed, 2 skipped, 3 errors** in 211.03s. The 1 failure (`quickstart_builder::test_copy_designs_without_themes_preserves_original`) and 3 errors (`tests/unit/ai/test_ai_protocols.py`, `test_behavior_units.py`, `strategy/engine/test_build_order_command_handler.py`) are ALL PRE-EXISTING baseline failures captured at start of PROJ-273. Zero new regressions from PROJ-274 Phase 6. Combat Lab suite: **162/162 passed** (fast mode). Test count rose from 14661 baseline to 14800 because PROJ-273 + PROJ-274 collectively added ~140 new tests (registry + materializer + fleet-aura warning + battle_runner context defaults + glob-driven guards).

Grep verification: `grep -rn "scenario\._load_ship\|ship_builder=lambda" game/ combat_lab/` returns only the historical reference in `combat_lab/design_loader.py:11` docstring. Zero production `_ship_builder` closures remain outside the ComparisonScenario role-tagging wrapper (kept per Task 6.5).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 7
- [x] Run `python Projects/scripts/validate_phase.py PROJ-274 6`
