# Phase 2: Tier-7 polish (test-quality MAJORs)

**Status:** Not Started
**Objective:** Land selected polish items from synthesis lines 105-122. Each is a small targeted fix; per-concern commit.

> **Note:** This phase has many small items. Implementer can roll several into a single commit if they touch the same file/concern, but PREFER per-concern commits for `git blame` clarity. Items can be tackled in any order.

---

## Tasks

### Task 2.1: LLMBackgroundCall `_done_event` race [Medium]
**File:** `game/services/llm/background.py:210, 291-297`

- [ ] Read the race: `wait()` waits on `_done_event` (line 210), `_run()` sets the event at line 291 BEFORE releasing the in-flight slot (lines 293-297).
- [ ] Move the event-set AFTER cleanup so callers observing `wait()` return see consistent state.
- [ ] Consider adding a lock around `_active_workers` mutations (currently mutated by `start`, `_run`, `shutdown_all_calls` without serialization).
- [ ] Commit: `fix(llm-background): set _done_event after worker cleanup (PROJ-349 T7-LLM)`

**Notes:**

### Task 2.2: `production_spawner` dispatch — `assert_called_once_with` [Simple]
**File:** `tests/unit/strategy/engine/test_production_spawner.py`

- [ ] `git grep -n "assert_called_once()" tests/unit/strategy/engine/test_production_spawner.py` — locate every call.
- [ ] For each: replace with `assert_called_once_with(<concrete expected args>)`.
- [ ] Commit: `test(production-spawner): tighten dispatch assertions to concrete args (PROJ-349 T7)`

**Notes:**

### Task 2.3: `_collect_team_modifiers` brittle import patch [Medium]
**File:** locate via `git grep -n "_collect_team_modifiers" tests/`

- [ ] Read the patch — likely depends on production keeping a deferred import that could move.
- [ ] Refactor to either (a) patch a stable seam (the function itself or a registry), or (b) remove the patch and rely on real imports.
- [ ] Commit: `test(team-modifiers): remove brittle import patch (PROJ-349 T7)`

**Notes:**

### Task 2.4: `_apply_damage_to_ship` dead-branch pin annotation [Simple]
**File:** locate via grep

- [ ] Find the test that pins a dead branch. Annotate the assertion with a comment linking to the relevant ticket/observation so future cleanup doesn't look like a regression.
- [ ] Commit: `test(damage): annotate dead-branch pin with observation link (PROJ-349 T7)`

**Notes:**

### Task 2.5: ActionExecutionEngine pin annotation [Simple]
**File:** `tests/unit/strategy/engine/test_action_execution_engine_gaps.py`

- [ ] After T6.3 (Phase 1 task 1.3) lands, the dead-DI test was rewritten. Annotate the now-correct test referencing the T6.3 ticket if any test still references the old behavior.

**Notes:**

### Task 2.6: PROJ-332 lazy-property + factory tests [Medium]
**File:** `tests/unit/strategy/turn_engine/`

- [ ] Add tests for the 5 lazy-property defaults flagged by OpenCode b4.
- [ ] Add a test for `create_default_turn_engine` factory.
- [ ] Commit: `test(turn-engine): cover lazy-property defaults + create_default_turn_engine factory (PROJ-349 T7)`

**Notes:**

### Task 2.7: PROJ-335 from_dict gaps [Medium]
**File:** `tests/unit/strategy/data/`

- [ ] 4 missing-key tests: PlanetaryFacility, Squadron missing required keys; Order missing `type` key; extra-key-tolerance test.
- [ ] Commit: `test(strategy-data): cover from_dict edge cases (PROJ-349 T7)`

**Notes:**

### Task 2.8: PROJ-336 vacuous module-constant tests [Simple]
**File:** locate via grep on test names `test_stabilizers_is_a_tuple_with_three_specs`, `test_system_radius_hexes_is_50`

- [ ] Decide: either delete (constants are self-evident) or rewrite to pin a behavioral consequence (e.g., "system_radius_hexes is what `is_in_system_radius` uses").
- [ ] Commit: `test(strategy-services): replace vacuous module-constant tests with behavioral pins (PROJ-349 T7)`

**Notes:**

### Task 2.9: `test_get_font_enforces_minimum_size_8` quantize-to-2 step [Simple]
**File:** locate via grep

- [ ] Add an assertion pinning the quantize-to-2 step (currently only the floor is pinned).
- [ ] Commit: `test(font): pin quantize-to-2 step in get_font minimum-size enforcement (PROJ-349 T7)`

**Notes:**

### Task 2.10: PROJ-326 misc [Simple]
**Files:** `Tools/lint_test_files.py` and friends

- [ ] Allowlist header lie: `pathlib.PurePosixPath.match` claim — verify and fix.
- [ ] AST linter blind spot: `importlib.import_module("game.foo")` — decide whether to extend linter or document gap.
- [ ] Python version comment (says 3.11; codebase is 3.13+) — fix.
- [ ] Per-fix commit if substantive; bundle if trivial.

**Notes:**

### Task 2.11: PROJ-321 deleted test recovery [Medium]
**File:** locate deletion via `git log --diff-filter=D --all -- 'tests/unit/**/test_start_battle_ship_builder*'`

- [ ] Find the deletion commit. Read the deleted test body via `git show <commit> -- <path>`.
- [ ] Per Stream 2 finding: PROJ-321 Phase 2 task said REWRITE not delete; no replacement exists; the `[x]` was wrong.
- [ ] Recover the test, either verbatim or rewritten to match current production.
- [ ] Update the PROJ-321 phase checklist to mark the task as actually-complete.
- [ ] Commit: `test: recover and rewrite test_start_battle_ship_builder_calls_to_ship_with_position_and_team_id (PROJ-349 T7)`

**Notes:**

### Task 2.12: `TestRegisterOnConstruction` retrofit [Medium]
**File:** locate via grep

- [ ] After PROJ-328 A.5 retrofit, this test no longer tests construction-registration — the helper manually calls `register_modal` AFTER bypass.
- [ ] Rewrite to actually exercise construction-time registration (i.e., do NOT call register_modal manually; assert it was called as a side effect of construction).
- [ ] Commit: `test: actually test construction-time modal registration in TestRegisterOnConstruction (PROJ-349 T7)`

**Notes:**

### Task 2.13: `bypass_init` MRO leak risk [Medium]
**File:** `tests/fixtures/ui_widget_factory.py` (or wherever `bypass_init` lives)

- [ ] Read the context-manager. Identify the MRO leak risk under pytest-xdist parallel (likely a class-level attribute mutation that persists across worker boundaries).
- [ ] Refactor to use instance-level state, or document the constraint.
- [ ] Commit: `fix(test-fixtures): isolate bypass_init MRO state per worker (PROJ-349 T7)`

**Notes:**

### Task 2.14: §2.4 LOC ceiling — DEFER decision [Simple]
**File:** `game/ui/screens/race_setup/screen.py` (484 LOC), `game/ui/screens/new_game_setup_screen.py` (733 LOC)

- [ ] Surface to user: "Two screens exceed the §2.4 500-LOC ceiling: `race_setup/screen.py` (484 LOC, near-miss) and `new_game_setup_screen.py` (733 LOC, real violation). PROJ-347 T4.7 may have already touched the latter. Splitting either is a non-trivial refactor — open a follow-up project, or scope into PROJ-349 if small?"
- [ ] Document direction in [decisions.md](decisions.md). If deferred: skip task.

**Notes:**

### Task 2.15: Phase 2 verification
- [ ] `pytest tests/unit/ -q` — all pass.
- [ ] `python Tools/lint_test_files.py` — 0 violations.
- [ ] Update Current State to Phase 3.

---

## Phase Completion Checklist
- [ ] All tasks (or user-deferred ones noted) checked
- [ ] Per-concern commits landed
- [ ] plan.md phase row → `Complete`
