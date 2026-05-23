# Phase 5: CAT-12 Logic-Heavy

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-480 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace ~18 verified CAT-12 logic-heavy test bodies from review `2026-05-20_210550_test-review`. Each test reimplements production logic with for-loops, conditional branches, or derived assertions. Replace with pre-computed reference values or extracted helpers so tests can't drift along with production formula changes.

---

## Tasks

### Task 5.1: test_ship_loading.py — logic-heavy ship validation body
**File:** `tests/unit/builder/test_ship_loading.py`
**Tests:** `pytest tests/unit/builder/test_ship_loading.py`

- [ ] Extract per-ship validation into a helper and parametrize by design file. Current 42-LOC body (lines 88-129) has nested loops + 4 stat-type if/else + broad except.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 5.2: test_empire_economy_caching.py — repeated scenario unpack
**File:** `tests/unit/strategy/services/test_empire_economy_caching.py`
**Tests:** `pytest tests/unit/strategy/services/test_empire_economy_caching.py`

- [ ] Extract `session, galaxy, empires = smoke_turn1_scenario` + `_build_service(fresh_registries)` (repeated 4×, lines 32-83) into a fixture yielding `(service, session, galaxy, empires)`.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 5.3: test_build_queue_panel_factory.py — 5-level os.path.dirname
**File:** `tests/unit/ui/screens/test_build_queue_panel_factory.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_panel_factory.py`

- [ ] Replace 5-level `os.path.dirname` chain to reach `data/builder_theme.json` (lines 208-234) with `Paths` module for repo-root resolution. Move to integration tests.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 5.4: test_battle_engine_tick.py — for-loop with hardcoded counts
**File:** `tests/unit/simulation/systems/test_battle_engine_tick.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py`

- [ ] Consolidate the 2 loop-with-hardcoded-count tests (lines 610-617, 740-748) into `@pytest.mark.parametrize("n", [1, 10, 100])`.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 5.5: test_battle_engine_tick.py — strict AI-before-ship invariant
**File:** `tests/unit/simulation/systems/test_battle_engine_tick.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_tick.py`

- [ ] Preserve the strict `max(ai_indices) < min(ship_indices)` invariant with `assert all(i < j for i in ai_indices for j in ship_indices)` (lines 363-388). _(verification adjusted from review's weaker first-element-only suggestion. See verification_report.md.)_
- [ ] Verify: passes; LOC delta ≈ +2.

### Task 5.6: test_new_game_setup.py — for-loop with manual delta calc
**File:** `tests/unit/ui/test_new_game_setup.py`
**Tests:** `pytest tests/unit/ui/test_new_game_setup.py`

- [ ] Replace loop-with-runtime-max_jump-computation (lines 154-165) with `all(system_count_slider_curve(t+1) - system_count_slider_curve(t) <= 1 for t in range(0, 99))`.
- [ ] Replace loop-with-manual-accumulator (lines 185-191) with `all(curve(t) >= curve(t-1) for t in range(1, 1001))`.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 5.7: test_camera_zoom.py — inline derivation comments
**File:** `tests/integration/ui/test_camera_zoom.py`
**Tests:** `pytest tests/integration/ui/test_camera_zoom.py`

- [ ] Replace 29-line derivation comments + inline expected-value computation (lines 51-97) with pre-computed expected constants from engineering notes; assert on the constant.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 5.8: test_generator_crew_requirement_design.py — defensive branches
**File:** `tests/regression/test_generator_crew_requirement_design.py`
**Tests:** `pytest tests/regression/test_generator_crew_requirement_design.py`

- [ ] Remove defensive `if layer_key is None` branches + debug print (lines 32-106). Failing fast on real bugs is better than silently skipping.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 5.9: test_atmosphere/test_generation.py — stochastic conditional
**File:** `tests/unit/strategy/planet_atmosphere/test_generation.py`
**Tests:** `pytest tests/unit/strategy/planet_atmosphere/test_generation.py`

- [ ] Replace `for _ in range(20) + if "CO2" in composition` stochastic branching (lines 146-167) with seeded RNG + deterministic assertion.
- [ ] Verify: passes; LOC delta ≈ +5 (with seed).

### Task 5.10: test_fleet_transfer_extended.py — transfer-cap formula in test
**File:** `tests/unit/strategy/engine/test_fleet_transfer_extended.py`
**Tests:** `pytest tests/unit/strategy/engine/test_fleet_transfer_extended.py`

- [x] Documented as acceptable per Phase 1 — keep as-is. _(verification: VERIFIED but tests document the transfer formula through assertions, valid integration-level pattern.)_

### Task 5.11: test_workflow.py (research) — conditional branch on RNG outcome
**File:** `tests/integration/research_workflow/test_workflow.py`
**Tests:** `pytest tests/integration/research_workflow/test_workflow.py`

- [ ] Replace `if any(e['event'] == 'breakthrough' ...) → assert ... else assert ...` (lines 36-50) with seeded RNG forcing one path; assert the expected outcome.
- [ ] Replace `if len(chances) >= 3: assert chances[-1] > chances[0]` (lines 111-129) similarly; no silent passes on early breakthrough.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 5.12: test_commands_colonization.py — manual retry loop
**File:** `tests/integration/gameplay_loop/test_commands_colonization.py`
**Tests:** `pytest tests/integration/gameplay_loop/test_commands_colonization.py`

- [ ] Replace `for _ in range(5): ... if break` (lines 127-147) with a deterministic computation of expected completion ticks (speed=100, 1-hex move → 1 tick).
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 5.13: test_complex_workflow.py — multiple retry guards
**File:** `tests/integration/test_complex_workflow.py`
**Tests:** `pytest tests/integration/test_complex_workflow.py`

- [ ] Replace 2+ explicit `if len(planet.construction_queue) > 0` retry guards (lines 315-361) with deterministic setup that doesn't require retry.
- [ ] Verify: passes; LOC delta ≈ -10.

### Task 5.14: test_turn_engine_lazy_properties.py — AST parsing in tests
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`

- [ ] _(coordination note: PROJ-480 originally expected Task 3.21 in PROJ-479 Phase 3 CAT-6 to split this into tests/static_guards/. That PROJ-479 task was NOT completed — it's in the NEEDS_REWORK list per PROJ-479/phase_3_checklist.md:156-162. Both the inspect.getsource() guard (lines 219-251) and the AST-parsing guard (lines 262-288) are still present in test_turn_engine_lazy_properties.py. Re-pending.)_

### Task 5.15: test_order_processor_facade.py — meta-test imports
**File:** `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py`

- [ ] Remove the meta-test that imports gate_no_legacy / gate_completeness then asserts hasattr (lines 60-75). Pytest discovery already fails naturally if those tests are renamed/deleted.
- [ ] Verify: passes; LOC delta ≈ -15.

### Task 5.16: test_spec_compiler.py — nested ship-tuple capture loops
**File:** `tests/unit/ui/screens/battle_setup/test_spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py`

- [ ] Extract snapshot-capture logic (39-LOC nested loops, lines 297-335) into a helper function so the assertion stays compact.
- [ ] Verify: passes; LOC delta ≈ -25.

### Task 5.17: test_colony_output.py — happiness rate re-derivation
**File:** `tests/unit/strategy/formulas/test_colony_output.py`
**Tests:** `pytest tests/unit/strategy/formulas/test_colony_output.py`

- [ ] Replace internal re-derivation of `happiness 2.0 → 2× rate` (lines 436-451, `rel=1e-9` tolerance) with pre-computed expected value from formula documentation. Test external value, not re-derived logic.
- [ ] Verify: passes; LOC delta ≈ +2.

### Task 5.18: test_action_execution_engine.py — for-loop hides per-tick
**File:** `tests/unit/strategy/engine/test_action_execution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_action_execution_engine.py`

- [x] _(coordination note: addressed via Task 1.28 in PROJ-480 Phase 1 — parametrize on tick.)_ — Phase 1 Task 1.28 done.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate PROJ-480 complete

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
