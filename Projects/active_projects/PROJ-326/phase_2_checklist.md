# Phase 2: SystemTreePanel coverage check + StrategySessionFacade contract guard

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-326 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Address two PROJ-321 review follow-ups: (a) verify SystemTreePanel has integration coverage now that the 664-LOC unit test was deleted (MAJ-001); (b) restore the StrategySessionFacade public-API contract guard test (MIN-002).

**Required reading:**
- [`design.md`](design.md) — Phase 2 SystemTreePanel + Facade Contract sections
- [`Reviews/results/2026-05-04_015902_consistency_proj-321-p0-dead-trivial-test-cleanup-completion-c_req-req_20260504_015901_0ba42a/report.md`](Reviews/results/2026-05-04_015902_consistency_proj-321-p0-dead-trivial-test-cleanup-completion-c_req-req_20260504_015901_0ba42a/report.md) — MAJ-001 + MIN-002

**Parallelism:** Fully parallel-safe with PROJ-324, PROJ-325 (all phases), Phase 1 of this project, and Phase 3 of this project. No cross-file conflicts.

---

## Tasks

### Task 2.1: SystemTreePanel coverage audit [Medium]

**Files (audit only):** `tests/integration/`, `tests/regression/`, `tests/unit/ui/`

- [ ] Search for any existing exercise of `SystemTreePanel`: `grep -rn 'SystemTreePanel' tests/`.
- [ ] For each hit, evaluate: does it test construction? Refresh? Click events? Tree expansion?
- [ ] Build a coverage scorecard: which behaviors are exercised by integration / regression tests?
- [ ] **GO criterion (no new test needed):** existing tests cover construction + at least one substantive behavior (refresh, click, render).
- [ ] **NO-GO criterion (smoke test needed):** no existing integration/regression coverage. Proceed to Task 2.2.

**Notes:** [Filled during implementation. Document existing coverage findings.]

---

### Task 2.2: SystemTreePanel integration smoke test (CONDITIONAL on Task 2.1) [Medium]

**File:** [`tests/integration/ui/test_system_tree_panel_smoke.py`](tests/integration/ui/test_system_tree_panel_smoke.py) (NEW)
**Tests:** Whichever this file contains.

**Skip this task if Task 2.1 found adequate existing coverage.**

- [ ] Mirror the `tests/integration/ui/build_queue_screen/` headless pygame_gui pattern.
- [ ] Test: SystemTreePanel constructs against a real (test-mode) StrategySession.
- [ ] Test: `panel.refresh()` runs without error after a session state change.
- [ ] Test: simulated click event on a tree node produces the expected callback / state change.
- [ ] Verify: tests pass headless: `pytest tests/integration/ui/test_system_tree_panel_smoke.py`.
- [ ] Document in PROJ-321 review (MAJ-001 follow-up): annotate the OpenCode review report (or a follow-up note) that MAJ-001 was addressed.

**Notes:** [Filled during implementation. Skip explanation if not needed.]

---

### Task 2.3: Restore StrategySessionFacade public-API contract guard [Medium]

**File:** [`tests/unit/strategy/facade/test_strategy_session_facade_contract.py`](tests/unit/strategy/facade/test_strategy_session_facade_contract.py) (NEW)
**Tests:** Whichever this file contains.

- [ ] Read [`game/strategy/facade/strategy_session_facade.py`](game/strategy/facade/strategy_session_facade.py) (or wherever StrategySessionFacade lives — verify path).
- [ ] Identify the canonical public-API surface — methods that callers MUST be able to invoke. Aim for 3-5 representative methods.
- [ ] Write a `TestStrategySessionFacadeContract` class that exercises each, with **assertions on observable behavior** — NOT `assert facade.method() is not None` style trivial-pass tests (the original deletion was correct on those).
- [ ] Use the design.md Phase 2 example as the template structure.
- [ ] Add a docstring at file top: "Public-API contract guard for StrategySessionFacade. Originally part of test_strategy_session_facade_public_api.py (deleted by PROJ-321). Restored per OpenCode review MIN-002."
- [ ] Verify: tests pass.
- [ ] Verify: file size ~30 LOC (lightweight).

**Notes:** [Filled during implementation. Document which methods exercised + why.]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] SystemTreePanel coverage gap closed (either confirmed adequate OR new smoke test added)
- [ ] StrategySessionFacade contract guard restored
- [ ] Sharded test suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State accordingly
