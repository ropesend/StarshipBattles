# Phase 4: Background coordinator (single-worker FIFO queue)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-354B 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Implement `ReplayVerificationCoordinator`. Subscribe to `ReplayStore` listener; queue records; process FIFO with single worker; run headless; verify; write sidecar.

See `plan.md` Phase 4 for full task details. **Reference template:** `LLMBackgroundCall` at `game/services/llm/background.py:65-368` and `RaceDescriptionLLMController` at `game/strategy/services/race_description_llm_controller.py:84-310`.

---

## Tasks

### Task 4.1: Failing tests for coordinator (TDD) [Medium]
**File:** `tests/unit/strategy/services/test_replay_verification_coordinator.py` (NEW)

- [ ] Tests: passes through verifier, failed verification, disabled toggle, queue cap full, single worker, exception isolation, shutdown, no recursion (see plan.md Task 4.1 for full list)
- [ ] Verify: all fail with import error

**Notes:**

### Task 4.2: Coordinator skeleton + queue + threading primitives [Complex]
**File:** `game/strategy/services/replay_verification_coordinator.py` (NEW)

- [ ] Imports: stdlib + simulation/replay verifier + replay_store + sidecar (NO ui/ai/app imports; AI factory must be DI-injected)
- [ ] Module-level `_coordinator_lock`, `_active_coordinators: Set` (mirror `_in_flight_calls` pattern at `game/services/llm/background.py:56-62`)
- [ ] `ReplayVerificationCoordinator` class with `__init__` taking `replay_store, ai_factory, registry_provider, settings, fallback_ship_builder, clock, logger` via DI
- [ ] Internal state: `_queue, _state_lock, _worker, _shutdown_event, _in_flight`
- [ ] `start()`, `_on_record_persisted(record, path)`, `_worker_loop()`, `shutdown(timeout)`
- [ ] Verify: subset of Phase 4.1 tests pass (queueing, cap enforcement, shutdown)

**Notes:**

### Task 4.3: Worker `_verify_one` implementation [Complex]
**File:** `game/strategy/services/replay_verification_coordinator.py`

- [ ] `_verify_one(record)`: replay_dir guard → settings toggle check → `build_replay_ship_builder` (with fallback) → `run_replay_headless` → `verify_replay_outcome` → `_write_sidecar` (see plan.md Task 4.3 for full pseudocode)
- [ ] `_write_sidecar(record, *, status, duration_ms=None, diff=None, error=None)`: defensive replay_dir check + atomic write
- [ ] Verify: "passes through verifier", "failed verification", "exception isolation" tests pass

**Notes:**

### Task 4.4: Listener registration + shutdown integration [Medium]
**File:** `game/strategy/services/replay_verification_coordinator.py`

- [ ] `start()` registers listener via `replay_store.add_on_record_persisted_listener(self._on_record_persisted)`; adds to `_active_coordinators`
- [ ] `shutdown(timeout)`: set event, wake worker, join with bounded timeout, deregister listener, idempotent
- [ ] Module-level `shutdown_all_coordinators(timeout=5.0)` (mirror `shutdown_all_calls` at `background.py:345-368`)
- [ ] Verify: all Phase 4.1 tests green

**Notes:**

### Task 4.5: No-recursion regression test [Simple]
**File:** `tests/unit/strategy/services/test_replay_verification_coordinator.py` (extended)

- [ ] `test_verification_replay_does_not_recursively_create_replay_record`: trigger verification, count files in replay_dir, assert no extra `replay_<other_id>_*.json` records
- [ ] Verify: passes

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
