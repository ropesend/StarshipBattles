# Phase 10 (DEFERRED): Behavioral E2E test for ActionExecutionEngine planet-FMS tick

> **STATUS: DEFERRED** — Created from end-of-project Codex consult Finding 6c + Risk 3. Not blocking PROJ-438 completion. May be picked up as a standalone follow-up by a future contributor.

**Status:** Deferred (created 2026-05-18; not started)
**Depends on:** PROJ-438 Phases 0–9 complete on `main`.
**Objective:** Add a behavioral end-to-end test that drives a planet FMS order (recovery or launch) through `ActionExecutionEngine._process_planet_action_tick()` and asserts the planet's order queue + side-effects after the tick. This closes the strongest uncovered runtime seam in PROJ-438's scope: today the engine-mediated dispatch path is protected by structural / inspect-based tests + unit-level handler tests, but no behavioral test runs the full engine tick path.

**Why deferred:**
- PROJ-438 ships strict-green at 23,268 passed tests; the existing unit + structural coverage protects against the specific regressions Phase 6 was designed to prevent.
- The integration fixture work is non-trivial — needs a real planet with an operational facility, a queued recovery or launch order, and an engine tick driver. Plausibly 100-200 LOC of test scaffold.
- Phase 9 was already a bundle of four small follow-ups; adding a medium-sized integration test would have broken that "small bundle" shape.
- A future contributor can pick this up as a clean standalone task using this checklist as the briefing.

---

## Tasks (TO BE EXECUTED LATER)

### Task 10.1: Failing behavioral E2E test
**Files:** `tests/integration/strategy/test_action_execution_planet_fms.py` (new)

- [ ] Build a fixture: 1 empire, 1 owned planet with 1 operational facility carrying a fighter or satellite bay; queue a `RECOVER_FIGHTERS` (or `RECOVER_SATELLITES`) order on the planet via the typed command path; ensure deployed groups exist for the recovery target.
- [ ] Run one tick of `ActionExecutionEngine._process_planet_action_tick()` (or the parent `tick` if the private method is not directly callable).
- [ ] Assert: the planet's order queue advanced, the recovery handler was invoked with all 5 kwargs of the unified `execute_for_issuer` contract, the deployed group transitioned correctly, and no exceptions propagated.
- [ ] Confirm test fails (or is not present) before adding it. Then implement / confirm the engine path makes it pass.

### Task 10.2: Optional — add a sibling test for the launch direction
**Files:** Same test file

- [ ] If 10.1's fixture is reusable, add a parametrized variant for `LAUNCH_FIGHTERS` / `LAUNCH_SATELLITES` that asserts the launch direction (planet → deployed group) round-trips through the engine.

---

## Phase Completion Checklist (when work happens)
- [ ] Failing test written first
- [ ] `python Tools/test_sharded/test_sharded.py` green (no NEW failures vs. baseline)
- [ ] Game still runnable / savable / loadable
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] `python Projects/scripts/validate_phase.py PROJ-438 10` passes
