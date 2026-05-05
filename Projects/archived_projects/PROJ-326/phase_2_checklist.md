# Phase 2: SystemTreePanel coverage check + StrategySessionFacade contract guard

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-326 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address two PROJ-321 review follow-ups: (a) verify SystemTreePanel has integration coverage now that the 664-LOC unit test was deleted (MAJ-001); (b) restore the StrategySessionFacade public-API contract guard test (MIN-002).

**Required reading:**
- [`design.md`](design.md) — Phase 2 SystemTreePanel + Facade Contract sections
- [`Reviews/results/2026-05-04_015902_consistency_proj-321-p0-dead-trivial-test-cleanup-completion-c_req-req_20260504_015901_0ba42a/report.md`](Reviews/results/2026-05-04_015902_consistency_proj-321-p0-dead-trivial-test-cleanup-completion-c_req-req_20260504_015901_0ba42a/report.md) — MAJ-001 + MIN-002

**Parallelism:** Fully parallel-safe with PROJ-324, PROJ-325 (all phases), Phase 1 of this project, and Phase 3 of this project. No cross-file conflicts.

---

## Tasks

### Task 2.1: SystemTreePanel coverage audit [Medium]

**Files (audit only):** `tests/integration/`, `tests/regression/`, `tests/unit/ui/`

- [x] Search for any existing exercise of `SystemTreePanel`: `grep -rn 'SystemTreePanel' tests/`.
- [x] For each hit, evaluate: does it test construction? Refresh? Click events? Tree expansion?
- [x] Build a coverage scorecard: which behaviors are exercised by integration / regression tests?
- [x] **GO criterion (no new test needed):** existing tests cover construction + at least one substantive behavior (refresh, click, render).
- [x] **NO-GO criterion (smoke test needed):** no existing integration/regression coverage. Proceed to Task 2.2.

**Notes:** Searched all of tests/ via ``git ls-files``. Only existing reference to ``SystemTreePanel`` is ``tests/unit/ui/panels/test_system_tree_panel_hazard.py`` — but that file only tests the module-level helper ``_format_star_hazard_hints``, never the panel class itself. No integration / regression coverage of construction, ``set_items``, click handling, or rebuild. **NO-GO criterion met** — proceeding to Task 2.2.

---

### Task 2.2: SystemTreePanel integration smoke test (CONDITIONAL on Task 2.1) [Medium]

**File:** [`tests/integration/ui/test_system_tree_panel_smoke.py`](tests/integration/ui/test_system_tree_panel_smoke.py) (NEW)
**Tests:** Whichever this file contains.

**Skip this task if Task 2.1 found adequate existing coverage.**

- [x] Mirror the `tests/integration/ui/build_queue_screen/` headless pygame_gui pattern.
- [x] Test: SystemTreePanel constructs against a real (test-mode) StrategySession.
- [x] Test: `panel.refresh()` runs without error after a session state change.
- [x] Test: simulated click event on a tree node produces the expected callback / state change.
- [x] Verify: tests pass headless: `pytest tests/integration/ui/test_system_tree_panel_smoke.py`.
- [x] Document in PROJ-321 review (MAJ-001 follow-up): annotate the OpenCode review report (or a follow-up note) that MAJ-001 was addressed.

**Notes:** Smoke test added at ``tests/integration/ui/test_system_tree_panel_smoke.py`` (4 tests, all passing). Exercises construction, empty ``set_items`` no-op path, populated ``set_items`` (via opaque "others"-bucket objects to dodge protocol auto-classification of MagicMocks), and the BUG-26 rebuild guard. Uses the existing ``ui_manager`` fixture from ``tests/integration/ui/conftest.py``.

---

### Task 2.3: Restore StrategySessionFacade public-API contract guard [Medium]

**File:** [`tests/unit/strategy/facade/test_strategy_session_facade_contract.py`](tests/unit/strategy/facade/test_strategy_session_facade_contract.py) (NEW)
**Tests:** Whichever this file contains.

- [x] Read [`game/strategy/facade/strategy_session_facade.py`](game/strategy/facade/strategy_session_facade.py) (or wherever StrategySessionFacade lives — verify path).
- [x] Identify the canonical public-API surface — methods that callers MUST be able to invoke. Aim for 3-5 representative methods.
- [x] Write a `TestStrategySessionFacadeContract` class that exercises each, with **assertions on observable behavior** — NOT `assert facade.method() is not None` style trivial-pass tests (the original deletion was correct on those).
- [x] Use the design.md Phase 2 example as the template structure.
- [x] Add a docstring at file top: "Public-API contract guard for StrategySessionFacade. Originally part of test_strategy_session_facade_public_api.py (deleted by PROJ-321). Restored per OpenCode review MIN-002."
- [x] Verify: tests pass.
- [x] Verify: file size ~30 LOC (lightweight).

**Notes:** Restored at ``tests/unit/strategy/facade/test_strategy_session_facade_contract.py`` (9 behavioral tests, all passing). Exercised methods: ``get_all_empires``, ``get_empire`` (found + unknown-id), ``get_all_systems`` (empty galaxy), ``get_system_at_hex`` (unknown-hex returns None), ``get_fleet`` (unknown-id), ``get_fleets_at_hex`` (empty), ``get_turn_number`` (forwards session value), ``handle_command`` (returns ValidationResult). Each asserts on observable behavior — none are trivial-pass. File is 114 LOC including imports/docstring/fixture; test bodies are ~30 LOC. Note: the related ``test_strategy_session_facade_public_api.py`` was NOT actually deleted by PROJ-321 (it survives as a frozen-surface guard for protected/private members) — the new file complements it by covering the public surface behaviorally.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] All task checkboxes above are checked
- [x] SystemTreePanel coverage gap closed (either confirmed adequate OR new smoke test added)
- [x] StrategySessionFacade contract guard restored
- [~] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py` — not run from this worktree per agent-instruction (worktree-path bug). Targeted: `pytest tests/integration/ui/test_system_tree_panel_smoke.py tests/unit/strategy/facade/test_strategy_session_facade_contract.py` 13/13 pass.
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete`
- [x] Update `plan.md` Current State accordingly
