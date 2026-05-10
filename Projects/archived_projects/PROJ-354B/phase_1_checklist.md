# Phase 1: Settings + pure verifier

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-354B 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extend `ReplaySettings`; add the pure verifier module. No coordinator, no sidecar, no integration.

See `plan.md` Phase 1 for full task details.

---

## Tasks

### Task 1.1: Extend `ReplaySettings` with verification fields [Simple]
**File:** `game/strategy/services/replay_store.py` (lines 56-86)
**Tests:** `pytest tests/unit/strategy/services/test_replay_settings.py -v`

- [ ] Add `verification_enabled: bool = True`, `verification_queue_cap: int = 16`
- [ ] Update `load_replay_settings` to read both new keys
- [ ] Tests: defaults, override via JSON, malformed → defaults, type coercion
- [ ] Verify: settings tests green; existing tests unaffected

**Notes:**

### Task 1.2: Failing tests for pure verifier (TDD) [Medium]
**File:** `tests/unit/simulation/replay/test_replay_verifier.py` (NEW)

- [ ] Pass case (identical outcomes), single-field fail, multi-field fail, capped diff (30→25), team_survivor mismatch, round-trip identity (see plan.md Task 1.2 for exact list)
- [ ] Verify: all fail with import error

**Notes:**

### Task 1.3: Implement pure verifier module [Medium]
**File:** `game/simulation/replay/replay_verifier.py` (NEW)

- [ ] Imports limited to stdlib + simulation/replay (NO Strategy/UI/AI)
- [ ] `Difference`, `ReplayVerificationResult` frozen dataclasses
- [ ] `compute_outcome_diff(expected, actual, max_diffs=25)`
- [ ] `verify_replay_outcome(record, replayed_outcome) -> ReplayVerificationResult`
- [ ] Verify: all Phase 1.2 tests pass

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
