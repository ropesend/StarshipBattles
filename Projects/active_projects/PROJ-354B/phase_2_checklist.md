# Phase 2: Sidecar persistence + lifecycle

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-354B 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Atomic sidecar JSON file at `replay_<id>.verification.json`. ReplayStore lifecycle (delete + evict) extended.

See `plan.md` Phase 2 for full task details.

---

## Tasks

### Task 2.1: Sidecar schema + atomic writer module [Medium]
**File:** `game/strategy/services/replay_verification_sidecar.py` (NEW)
**Tests:** `tests/unit/strategy/services/test_replay_verification_sidecar.py` (NEW)

- [ ] `REPLAY_VERIFICATION_SCHEMA_VERSION = "1.0.0"` constant
- [ ] `VerificationStatus` enum: `PENDING`, `PASSED`, `FAILED`, `ERROR`, `SKIPPED_QUEUE_FULL`, `SKIPPED_DISABLED`
- [ ] `VerificationSource` enum: `BACKGROUND`, `VISUAL_REPLAY` (reserved)
- [ ] `VerificationSidecar` frozen dataclass (replay_id, schema_version, status, source, verified_at, duration_ms, diff, error)
- [ ] `write_verification_sidecar(replay_dir, sidecar) -> Optional[Path]` (uses `save_json` atomic)
- [ ] `read_verification_sidecar(replay_dir, replay_id) -> Optional[VerificationSidecar]`
- [ ] `sidecar_path_for_replay(replay_dir, replay_id) -> Path`
- [ ] Tests: round-trip, atomic, missing returns None, corrupt returns None, path format
- [ ] Verify: tests green

**Notes:**

### Task 2.2: Update `ReplayStore.delete` to unlink sidecar [Simple]
**File:** `game/strategy/services/replay_store.py` (lines 250-262)
**Tests:** `pytest tests/integration/replay/test_replay_store.py -k delete -v`

- [ ] After existing `path.unlink()`, also unlink sidecar via `sidecar_path_for_replay(rd, replay_id)`
- [ ] Try/except OSError with logging
- [ ] New test `test_delete_removes_sidecar`
- [ ] Verify: existing delete tests still pass; new test green

**Notes:**

### Task 2.3: Update `_evict_excess` to unlink sidecars [Simple]
**File:** `game/strategy/services/replay_store.py` (lines 280-299)
**Tests:** `pytest tests/integration/replay/test_replay_store.py -k evict -v`

- [ ] Parse replay_id from each evicted file's name; unlink matching sidecar
- [ ] New test `test_evict_removes_sidecars_alongside_records` (cap=3, persist 5+sidecars, assert 2 oldest of each gone)
- [ ] Verify: existing eviction tests still green; new sidecar test passes

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
