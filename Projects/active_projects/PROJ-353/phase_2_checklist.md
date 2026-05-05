# Phase 2: Tier-7 polish bundle

**Status:** Not Started
**Objective:** Land the test-quality polish items from synthesis lines 105-122. Per-concern commits. None of these are merge-blocking; tackle in priority order.

> **Discipline:** This is test-quality work + small targeted production fixes only. Apparent bugs found mid-task are documented as Observations in [decisions.md](decisions.md), NOT auto-fixed.

---

## Priority 1 — production fix (small but real)

### Task 2.1: LLMBackgroundCall `_done_event` race [Medium]
**File:** `game/services/llm/background.py:210, 291-297`
**Tests:** `pytest tests/unit/services/llm/test_background.py -x` (note: one test in this file is a known-flaky LLM-timing test on Windows per MEMORY.md)

- [ ] Read the race: `wait()` waits on `_done_event` (line 210); `_run()` sets the event at line 291 BEFORE releasing the in-flight slot at lines 293-297.
- [ ] Move event-set to AFTER cleanup so callers observing `wait()` return see consistent state.
- [ ] Consider lock around `_active_workers` (currently mutated by `start`, `_run`, `shutdown_all_calls` without serialization).
- [ ] Run targeted tests; ignore the known-flaky timing test (documented in MEMORY.md `project_flaky_llm_background_test`).
- [ ] Commit: `fix(llm-background): set _done_event after worker cleanup (PROJ-353 Tier-7)`

**Notes:**

---

## Priority 2 — pin tightening + test annotations

### Task 2.2: production_spawner `assert_called_once` → `assert_called_once_with` [Simple]
**File:** `tests/unit/strategy/engine/test_production_spawner.py`

- [ ] `git grep -n "assert_called_once()" tests/unit/strategy/engine/test_production_spawner.py` — locate every call.
- [ ] For each: replace with `assert_called_once_with(<concrete expected args>)`.
- [ ] Commit: `test(production-spawner): tighten dispatch assertions to concrete args (PROJ-353 Tier-7)`

**Notes:**

### Task 2.3: `_collect_team_modifiers` brittle import patch refactor [Medium]
**File:** locate via `git grep -n "_collect_team_modifiers" tests/`

- [ ] Read the patch — depends on production keeping a deferred import.
- [ ] Refactor: patch a stable seam (the function itself or the registry) instead.
- [ ] Commit: `test(team-modifiers): remove brittle import patch (PROJ-353 Tier-7)`

**Notes:**

### Task 2.4: `_apply_damage_to_ship` dead-branch pin annotation [Simple]
**File:** locate via grep

- [ ] Find the test pinning a dead branch.
- [ ] Add a comment linking to the relevant Observation or ticket so future cleanup doesn't look like a regression.
- [ ] Commit: `test(damage): annotate dead-branch pin with observation link (PROJ-353 Tier-7)`

**Notes:**

### Task 2.5: ActionExecutionEngine pin annotation [Simple]
**Dependency:** PROJ-351 T6.3 must land first.
**File:** `tests/unit/strategy/engine/test_action_execution_engine_gaps.py`

- [ ] After PROJ-351 T6.3 lands, the dead-DI test was rewritten. Annotate the now-correct test with a forward reference if it still pins anything subtle.

**Notes:**

---

## Priority 3 — coverage gaps

### Task 2.6: PROJ-332 lazy-property + factory tests [Medium]
**File:** `tests/unit/strategy/turn_engine/`

- [ ] Add tests for the 5 lazy-property defaults flagged by OpenCode b4.
- [ ] Add a test for `create_default_turn_engine` factory.
- [ ] Commit: `test(turn-engine): cover lazy-property defaults + create_default_turn_engine factory (PROJ-353 Tier-7)`

**Notes:**

### Task 2.7: PROJ-335 from_dict gaps [Medium]
**File:** `tests/unit/strategy/data/`

- [ ] 4 missing tests: PlanetaryFacility/Squadron missing required keys; Order missing `type`; extra-key tolerance.
- [ ] Commit: `test(strategy-data): cover from_dict edge cases (PROJ-353 Tier-7)`

**Notes:**

### Task 2.8: PROJ-336 vacuous module-constant tests [Simple]
**File:** locate via grep on test names `test_stabilizers_is_a_tuple_with_three_specs`, `test_system_radius_hexes_is_50`

- [ ] Decide: delete (constants are self-evident) OR rewrite as behavioral pin.
- [ ] Commit: `test(strategy-services): replace vacuous module-constant tests with behavioral pins (PROJ-353 Tier-7)`

**Notes:**

### Task 2.9: `test_get_font_enforces_minimum_size_8` quantize-to-2 step [Simple]
**File:** locate via grep

- [ ] Add an assertion pinning the quantize-to-2 step (currently only the floor is pinned).
- [ ] Commit: `test(font): pin quantize-to-2 step in get_font minimum-size enforcement (PROJ-353 Tier-7)`

**Notes:**

---

## Priority 4 — tooling fixes

### Task 2.10: PROJ-326 misc tooling [Simple]
**Files:** `Tools/lint_test_files.py` and friends

- [ ] Allowlist header lie (`pathlib.PurePosixPath.match` claim) — verify and fix.
- [ ] AST linter blind spot (`importlib.import_module("game.foo")`) — extend linter or document gap.
- [ ] Python version comment (says 3.11; codebase is 3.13+) — fix.
- [ ] Per-fix commit if substantive; bundle if trivial.

**Notes:**

---

## Priority 5 — recovery + retrofit

### Task 2.11: PROJ-321 deleted test recovery [Medium]
**File:** locate via `git log --diff-filter=D --all -- 'tests/unit/**/test_start_battle_ship_builder*'`

- [ ] Find the deletion commit; read the deleted body.
- [ ] Per Stream 2: PROJ-321 task said REWRITE not delete; no replacement exists.
- [ ] Recover; rewrite to match current production.
- [ ] Update PROJ-321 phase checklist to reflect the actual state.
- [ ] Commit: `test: recover and rewrite test_start_battle_ship_builder_calls_to_ship_with_position_and_team_id (PROJ-353 Tier-7)`

**Notes:**

### Task 2.12: `TestRegisterOnConstruction` retrofit [Medium]
**File:** locate via grep

- [ ] After PROJ-328 A.5 retrofit, this test no longer tests construction registration.
- [ ] Rewrite to actually exercise construction-time registration (do NOT call `register_modal` manually; assert it's called as a construction side-effect).
- [ ] Commit: `test: actually test construction-time modal registration in TestRegisterOnConstruction (PROJ-353 Tier-7)`

**Notes:**

### Task 2.13: `bypass_init` MRO leak risk [Medium]
**File:** `tests/fixtures/ui_widget_factory.py` (or wherever `bypass_init` lives)

- [ ] Read the context-manager. Identify the MRO leak risk under pytest-xdist parallel.
- [ ] Refactor to instance-level state OR document the constraint.
- [ ] Commit: `fix(test-fixtures): isolate bypass_init MRO state per worker (PROJ-353 Tier-7)`

**Notes:**

---

## Final verification

### Task 2.14: Suite + lint + index update

- [ ] `pytest tests/unit/ -q -p no:cacheprovider` — full suite green.
- [ ] `python Tools/lint_test_files.py` — 0 violations.
- [ ] Update `Projects/projects_index.md` PROJ-353 → `Awaiting Verification`. Commit: `chore(PROJ-353): mark closeout follow-up awaiting verification`.

**Notes:**

---

## Phase Completion Checklist
- [ ] All tasks checked (or any deferred items explicitly noted)
- [ ] Per-concern commits + chore commit landed
- [ ] plan.md phase table → `Complete`; Current State final
- [ ] Surface to user
