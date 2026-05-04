# Phase 4: `strategy_screen` 50-test refactor (PROJ-322 Task 3.25) — CONDITIONAL

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-327 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

> **⚠️ PHASE 4 IS CONDITIONAL.** Skip entirely if Phases 1-3 cumulative runtime delta meets the user's target set in Phase 0 Task 0.6. If skipped, mark this phase Complete with a single Note: "Skipped — Phases 1-3 met target." and update PROJ-322 Task 3.25 annotation to `**RE-CONFIRMED DEFERRED IN PROJ-327 — Phases 1-3 deltas sufficient; refactor not warranted at this time. Audit at <commit SHA>**`.

**Status:** Not Started (CONDITIONAL on Phases 1-3 outcome + user target)
**Objective:** Production-side refactor of `strategy_screen.py` to extract sub-object construction to a `StrategyScreenComposition` factory, then migrate 50 tests to use a `MockComposition`. Closes PROJ-322 Task 3.25.

**Required reading:**
- [`design.md`](design.md) — Phase 4 section
- PROJ-322 phase_3_checklist.md Task 3.25 deferral annotation
- OpenCode 322-review Section 7 — strategy-screen analysis (described as "multi-day production refactor")
- [`game/ui/screens/strategy_screen.py`](game/ui/screens/strategy_screen.py) (verify path) — the production class
- [`tests/unit/ui/screens/test_strategy_screen.py`](tests/unit/ui/screens/test_strategy_screen.py) (verify path) — the 50-test cluster

**Parallelism:** Sequential after Phases 1-3. The Composition pattern may overlap PROJ-325's PanelRegistry pattern (if PROJ-325 NO-GO landed) — coordinate documentation in `docs/02_PATTERNS.md` to avoid duplicate pattern entries.

**Hard time budget:** 3 LLM-paced sessions. If estimate balloons past that, STOP and surface to user (Decision D-005).

---

## Tasks

### Task 4.0: Confirm Phase 4 trigger [Simple]

- [ ] Read Phase 0 Task 0.6 outcome (user-set target).
- [ ] Compute Phases 1-3 cumulative delta against baseline.
- [ ] If cumulative delta meets target: skip Phase 4 (mark Complete with note above). Done.
- [ ] If cumulative delta does NOT meet target: proceed to Task 4.1.

**Notes:** [Filled during implementation. Record cumulative delta + decision.]

---

### Task 4.1: Audit current `strategy_screen` test brittleness [Medium]

**File:** [`tests/unit/ui/screens/test_strategy_screen.py`](tests/unit/ui/screens/test_strategy_screen.py)

- [ ] Read the file. Catalog all private-method patches (e.g., `patch.object(screen, '_init_layout')`).
- [ ] Catalog all sub-object dependencies of `StrategyScreen.__init__` (the 8 sub-objects per OpenCode review).
- [ ] Identify the boundary: what's the minimal public surface a test needs to drive?

**Notes:** [Filled during implementation. Record sub-object list + private-method patch count.]

---

### Task 4.2: Define `StrategyScreenComposition` protocol [Medium]

**File:** [`game/ui/screens/strategy_screen_composition.py`](game/ui/screens/strategy_screen_composition.py) (NEW)
**Tests:** Smoke test in `tests/unit/ui/screens/test_strategy_screen_composition.py` (NEW)

- [ ] Define a `StrategyScreenComposition` Protocol with one method per sub-object construction (e.g., `make_command_bar(...)`, `make_galaxy_map(...)`, etc.). Match existing inline construction signatures.
- [ ] Define default `StrategyScreenCompositionFactory` that implements the protocol with the existing construction logic moved verbatim.
- [ ] Add smoke test.

**Notes:** [Filled during implementation]

---

### Task 4.3: Wire Composition into `StrategyScreen.__init__` [Medium]

**File:** [`game/ui/screens/strategy_screen.py`](game/ui/screens/strategy_screen.py)

- [ ] Add `composition: StrategyScreenComposition | None = None` to `__init__` signature.
- [ ] Default to `StrategyScreenCompositionFactory()` when None.
- [ ] Replace inline sub-object constructions with `composition.make_<thing>(...)` calls.
- [ ] Verify: production behavior unchanged. Run the existing tests against the default Composition — should still pass (after Task 4.4 migrates them).

**Notes:** [Filled during implementation]

---

### Task 4.4: Add `MockComposition` test fixture [Simple]

**File:** [`tests/fixtures/strategy_screen_composition.py`](tests/fixtures/strategy_screen_composition.py) (NEW)
**Tests:** Smoke test.

- [ ] Implement `MockComposition` returning Mock objects for every method.
- [ ] Add smoke test.

**Notes:** [Filled during implementation]

---

### Task 4.5: Migrate 50 tests to use MockComposition [Complex]

**File:** [`tests/unit/ui/screens/test_strategy_screen.py`](tests/unit/ui/screens/test_strategy_screen.py)
**Tests:** Whichever this file contains.

- [ ] Replace private-method patches with construction-via-MockComposition.
- [ ] For each test: identify which sub-object the test cares about, customize that one Mock from MockComposition.
- [ ] Verify: all 50 tests pass.
- [ ] Verify: no private-method patches remain.
- [ ] Measure runtime delta for the file.
- [ ] Update PROJ-322 Task 3.25 annotation: `**RESOLVED IN PROJ-327 Phase 4 (commit <SHA>)**`.

**Notes:** [Filled during implementation. Record per-test pass count + runtime delta.]

---

### Task 4.6: Document "Compositional Construction" pattern [Simple]

**File:** [`docs/02_PATTERNS.md`](docs/02_PATTERNS.md)

- [ ] Add a pattern entry for "Compositional Construction" — extract sub-object factory, default in production, mock in tests.
- [ ] Cross-reference: the StrategyScreenComposition (this phase), the RaceSetupScreen PanelRegistry (if PROJ-325 NO-GO landed), and the make_ui_widget factory (PROJ-322 / PROJ-324).
- [ ] Note: this pattern is preferred over `bypass_init` for new code; `bypass_init` is the retrofit pattern for code that wasn't built compositionally.

**Notes:** [Filled during implementation]

---

### Task 4.7: Final cumulative measurement [Simple]

- [ ] Run sharded suite + median of 3 wall-clocks.
- [ ] Compare to Phase 0 baseline.
- [ ] Verify target hit (or document overshoot / undershoot).
- [ ] Record final delta in `findings/phase_4_runtime_delta.md`.

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] StrategyScreenComposition pattern landed in production + docs
- [ ] 50 tests migrated, no private-method patches remain
- [ ] PROJ-322 Task 3.25 annotation updated
- [ ] Sharded suite passes
- [ ] User-set target met (or shortfall documented)
- [ ] Update status at top of this file to `Complete`
- [ ] Update `plan.md` phase table row to `Complete`
- [ ] Update `plan.md` Current State to point to Phase 5
