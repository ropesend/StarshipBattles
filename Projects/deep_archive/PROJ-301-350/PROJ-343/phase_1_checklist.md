# Phase 1: Failing API tests (TDD)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-343 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Write one public-API failing test per defect (six total). Each test must FAIL for the right reason against current `feat/03c-phase-aware-execution` HEAD before any production fix is applied.

---

## Optional Phase B swarm (recommended for PROJ-343 only)

Per master arc plan, launch 3 parallel Explore agents in a single message before writing the tests. This shortens Phases 6 + 7 (test-locating work) and confirms T1.3 ripple. Skip if confident.

- **Agent 1**: enumerate every test that pins `kill()` on TransferDialog or CargoQuickDialog (`patch.object(dialog, "kill")`, mock_kill assertions, `dialog.kill.assert_*`). Report file:line for each.
- **Agent 2**: list every call site of `collect_sector_effects(..., empire_id=None)` and `collect_sector_effects(..., empire_id=<expr>)`; report whether each is correct or a leak.
- **Agent 3**: list every test that asserts a raw exception (not `EnginePhaseError`) propagates from `process_consumption`, `process_happiness`, `process_population_growth`, `process_quality_improvement`, `process_atmosphere`, `process_water_modification`.

---

## Tasks

### Task 1.1: Write failing API test for T1.1 (fleet-to-fleet transfer) [Medium]
**File:** `tests/unit/strategy/engine/handlers/test_transfer_handler_fleet_to_fleet.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/handlers/test_transfer_handler_fleet_to_fleet.py -x` — must FAIL with "Planet not found"

- [ ] Create test file with imports: `IssueTransferCommand`, `TransferCommandHandler`, `GameSession`, `Empire`, `Fleet`.
- [ ] Build minimal session with two empires (A, B), each owning one fleet at the same hex.
- [ ] Construct `IssueTransferCommand(fleet_id=A_fleet.id, planet_id=None, target_fleet_id=B_fleet.id, cargo_type='passengers', direction='load', amount=10)`.
- [ ] Call `TransferCommandHandler().execute(session, cmd)`.
- [ ] Assert `result.is_valid is True` and a TRANSFER order is appended to `A_fleet.orders` carrying `target_fleet_id=B_fleet.id`.
- [ ] Run; confirm fail message is "Planet not found." (proves the exact bug).

**Notes:** [Filled during implementation]

### Task 1.2: Write failing API test for T1.2-snapshot [Medium]
**File:** `tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py` (NEW)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py -x` — must FAIL

- [ ] Monkeypatch `TurnStateSnapshot.capture` to raise `RuntimeError("simulated capture failure")`.
- [ ] Build minimal session that would otherwise process a turn cleanly.
- [ ] Call `turn_engine.process_turn(...)` with the patched capture.
- [ ] Assert that EITHER the capture failure surfaces (raises) OR a clear error is logged with `EnginePhaseError(phase_name="snapshot_capture")` shape — implementer's chosen contract from Phase 3.
- [ ] Confirm current behavior is "snapshot=None, turn proceeds silently" (proves the bug).

**Notes:**

### Task 1.3: Write failing API test for T1.2-engines [Medium]
**File:** `tests/unit/strategy/turn_engine/test_turn_end_of_turn_engine_rollback.py` (NEW)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_end_of_turn_engine_rollback.py -x` — must FAIL

- [ ] Install a stub `happiness_engine` whose `process_happiness` raises `RuntimeError("forced happiness failure")`.
- [ ] Capture pre-turn state (population, resources) for one empire.
- [ ] Call `turn_engine.process_turn(...)`.
- [ ] Assert that `EnginePhaseError` is raised AND `snapshot.restore` was called (state matches pre-turn).
- [ ] Confirm current behavior is `RuntimeError` propagates without rollback (state changed).

**Notes:**

### Task 1.4: Write failing API test for T1.3 (sector-effect leak) [Medium]
**File:** `tests/unit/strategy/engine/test_owned_sector_effects_filter.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_owned_sector_effects_filter.py -x` — must FAIL

- [ ] Build a star system with one hex containing a planet owned by empire A.
- [ ] Install a facility on the planet projecting `EnvironmentalDamage` ability with non-zero damage.
- [ ] Place an empire-B fleet at the same hex.
- [ ] Tick `EnvironmentalHazardEngine`.
- [ ] Assert empire-B fleet took zero damage (because the hazard is empire-A-owned).
- [ ] Assert empire-A's own fleet at that hex DID take damage (sanity).
- [ ] Confirm current behavior: empire-B fleet damaged (proves the leak).

**Notes:**

### Task 1.5: Write failing API test for T1.4 (TransferDialog stays open on abort) [Simple]
**File:** `tests/unit/ui/screens/test_transfer_dialog_keeps_open_on_abort.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog_keeps_open_on_abort.py -x` — must FAIL

- [ ] Construct `TransferDialog` with `bypass_init` per `tests/fixtures/ui_widget_factory.py`.
- [ ] Set `view_model.current_source = None` (or `current_target = None`); leave pending non-empty.
- [ ] Spy on `dialog.kill`.
- [ ] Call `dialog._on_confirm()`.
- [ ] Assert `dialog.kill` was NOT called.
- [ ] Confirm current behavior: `kill` IS called (try/finally always runs).

**Notes:**

### Task 1.6: Write failing API test for T1.5 (CargoQuickDialog kills on exception) [Simple]
**File:** `tests/unit/ui/screens/test_cargo_quick_dialog_kills_on_dispatch_failure.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_cargo_quick_dialog_kills_on_dispatch_failure.py -x` — must FAIL

- [ ] Construct `CargoQuickDialog` with `bypass_init`.
- [ ] Install a controller stub whose `issue_orders` raises `RuntimeError("forced facade failure")`.
- [ ] Spy on `dialog.kill`.
- [ ] Call `dialog._issue_orders()`. Expect RuntimeError to propagate.
- [ ] Assert `dialog.kill` WAS called despite the exception.
- [ ] Confirm current behavior: `kill` is NOT called (no try/finally).

**Notes:**

### Task 1.7: Run all 6 new tests together
**Tests:** `pytest tests/unit/strategy/engine/handlers/test_transfer_handler_fleet_to_fleet.py tests/unit/strategy/turn_engine/test_turn_snapshot_capture_failure.py tests/unit/strategy/turn_engine/test_turn_end_of_turn_engine_rollback.py tests/unit/strategy/engine/test_owned_sector_effects_filter.py tests/unit/ui/screens/test_transfer_dialog_keeps_open_on_abort.py tests/unit/ui/screens/test_cargo_quick_dialog_kills_on_dispatch_failure.py -x`

- [ ] All 6 fail; each failure message proves the bug.
- [ ] Commit: `test(PROJ-343): add 6 failing API tests for Tier-1 production defects`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 6 new tests fail with messages confirming the bugs
- [ ] Single commit landed with all 6 tests
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2 (T1.1 fix)
