# Phase 3: ReplayStore listener API + ReplayResolver sidecar read

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-354B 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add post-persist listener registration to `ReplayStore`; extend `ReplayResolver` to surface sidecar status.

See `plan.md` Phase 3 for full task details.

---

## Tasks

### Task 3.1: Listener API on `ReplayStore` [Medium]
**File:** `game/strategy/services/replay_store.py`
**Tests:** `pytest tests/integration/replay/test_replay_store.py -k listener -v`

- [ ] Add `self._on_record_persisted_listeners: List[Callable[[ReplayRecord, Path], None]] = []` in `__init__` (lines 119-131)
- [ ] Add `add_on_record_persisted_listener(callback)` and `remove_on_record_persisted_listener(callback)` methods (idempotent: don't duplicate, don't error on missing)
- [ ] In `persist` (lines 200-214), after successful write but BEFORE `_evict_excess`, fire listeners (each in own try/except)
- [ ] Tests: subscribe, unsubscribe, multiple listeners, exception isolation, no-listener path (existing behavior preserved)
- [ ] Verify: all tests green

**Notes:**

### Task 3.2: Extend `ReplayResolver.resolve` to read sidecar [Medium]
**File:** `game/strategy/services/replay_resolver.py` (lines 75-113 + ReplayLookup at 27-41)
**Tests:** `pytest tests/unit/strategy/test_replay_resolver.py -v`

- [ ] Add field `verification_status: Optional[str] = None` to `ReplayLookup`
- [ ] After loading record, attempt `read_verification_sidecar(rd, replay_id)`; populate field if sidecar exists
- [ ] Tests: missing sidecar → None; passed sidecar → "PASSED"; failed → "FAILED"; corrupt → None (no exception)
- [ ] Verify: existing resolver tests unaffected; new sidecar field tested

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
