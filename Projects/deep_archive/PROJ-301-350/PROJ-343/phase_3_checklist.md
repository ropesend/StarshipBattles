# Phase 3: T1.2-snapshot — surface snapshot-capture failures

**Status:** Not Started
**Objective:** When `TurnStateSnapshot.capture()` raises, the failure must NOT silently disable rollback. Either the exception escapes (preferred) or escalates to `EnginePhaseError(phase_name="snapshot_capture")`.

---

## Tasks

### Task 3.1: Decide contract [Simple]
**File:** none (decision only)

- [ ] Choose between (A) re-raise capture failures verbatim, (B) wrap as `EnginePhaseError(phase_name="snapshot_capture")` so existing rollback path triggers, (C) re-raise but log loudly first.
- [ ] Default recommendation: (A) re-raise. Simplest. Caller already handles arbitrary exceptions and the turn was unsafe regardless.
- [ ] Document choice in [decisions.md](../PROJ-343/decisions.md).

**Notes:**

### Task 3.2: Apply fix to `turn_engine.py:514-524` [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py -x` — must PASS

- [ ] Replace broad `except Exception as e: logger.error(...); # Continue without snapshot` with the chosen contract.
- [ ] If contract (A): `except Exception as e: logger.error("Pre-turn snapshot capture failed; turn aborted to preserve state integrity"); raise`.
- [ ] If contract (B): `except Exception as e: raise EnginePhaseError(...)`.
- [ ] Run Phase 1 task-1.2 test → passes.

**Notes:**

### Task 3.3: Rewrite `test_turn_engine_snapshot_integration.py:130-160` [Medium]
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration.py -x`

- [ ] Read lines 130-160 to confirm what's pinned.
- [ ] Replace the assertion that `snapshot=None, turn proceeds` with the new contract:
  - If contract (A): assert `pytest.raises(<original exception type>)` and that no rollback was attempted.
  - If contract (B): assert `pytest.raises(EnginePhaseError)` with `phase_name == "snapshot_capture"`.
- [ ] Update commit message: include `tests: rewrite snapshot-capture failure pin per new contract (PROJ-343 T1.2-snapshot)` rationale.

**Notes:**

### Task 3.4: Targeted test slice
**Tests:** `pytest tests/unit/strategy/turn_engine/ -x`

- [ ] All pass except possibly the soon-to-be-rewritten end-of-turn-engines test (Phase 4 covers that).

**Notes:**

### Task 3.5: Commit
- [ ] Stage only `turn_engine.py` snapshot-capture change + the rewritten test + the Phase 1 task-1.2 test
- [ ] Commit: `fix(turn-engine): surface snapshot-capture failures instead of silently disabling rollback (PROJ-343 T1.2-snapshot)`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes checked
- [ ] T1.2-snapshot commit landed
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update Current State to point to Phase 4
