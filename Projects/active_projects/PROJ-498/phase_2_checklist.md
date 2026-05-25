# Phase 2: Save-restore path rejection logging (TDD)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-498 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Emit `logger.warning` with reason at the two save-restore boundaries when `Component.add_modifier()` returns False. Today both paths silently drop.

**Precondition:** Phase 1 complete (`check_allowance()` available).

---

## Tasks

### Task 2.1: Failing test for `battle_state.py` rejection log [Medium]
**File:** `tests/unit/simulation/test_battle_state.py` (or nearest existing module covering battle_state restoration)
**Tests:** `pytest tests/unit/simulation/test_battle_state.py -k rejection`

- [x] Construct a battle-state save dict where a modifier exists in the registry but is `allow_abilities`-rejected for a given component
- [x] Use `caplog` to assert `logger.warning` fires with component id, modifier id, and reason
- [x] Confirm test fails (no log emitted today — `battle_state.py:274-280` silently drops)

**Notes:** Test lives at `tests/unit/simulation/test_battle_state_live_object_bridges.py::TestShipStateToShipRejectionLogging::test_to_ship_logs_rejection_with_reason`. Pre-implementation: assertion `Expected save-restore rejection warning ... got []` (RED).

### Task 2.2: Implement log at `battle_state.py:279` [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** same as 2.1

- [x] Call `check_allowance()` before `add_modifier()` (or check `add_modifier()`'s False return) and emit `logger.warning(f"BattleState restore: modifier '{mid}' rejected for component '{new_comp.id}': {reason}")`
- [x] Verify test passes

**Notes:** Live message format: `BattleState restore: Modifier '{mid}' rejected for component '{new_comp.id}' on ship '{self.ship_id}': {AllowanceReason.name}; skipping`. Post-implementation: GREEN.

### Task 2.3: Failing test for `ship_serialization.py` rejection log [Medium]
**File:** `tests/unit/simulation/entities/test_ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_serialization.py -k rejection`

- [x] Construct a ship JSON dict where a modifier exists in the registry but is `allow_abilities`-rejected
- [x] Use `caplog` to assert a NEW warning fires (distinct from the existing unknown-id warning at `ship_serialization.py:228`)
- [x] Confirm test fails

**Notes:** Added two tests in `TestLoadComponentsRejectionLogging`: one asserts the warning fires with reason, the other asserts the message wording is distinct from the unknown-id one. Pre-implementation: assertion-with-reason RED; distinct-wording test vacuously GREEN (no warning at all).

### Task 2.4: Implement log at `ship_serialization.py:226` [Simple]
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** same as 2.3

- [x] Add a check-and-warn branch before/after `new_comp.add_modifier(mid, ...)` that logs reason on rejection
- [x] Keep existing unknown-id warning intact
- [x] Verify test passes

**Notes:** Live message format: `ShipSerializer: Modifier '{mid}' rejected for component '{new_comp.id}' on ship '{ship.name}': {AllowanceReason.name}; skipping`. The pre-existing unknown-id wording (`not found in registry, skipping`) is preserved, so the two log lines are reliably distinguishable.

### Task 2.5: Spot-check no new log noise in builder/UI tests [Simple]
**File:** N/A
**Tests:** `pytest tests/regression/modifier_ability_snapshots/ tests/unit/ui/`

- [x] Run the snapshot suite + UI tests with default log level
- [x] Confirm no new warnings appear (builder rejections are intentional and should NOT log)

**Notes:** 70 snapshot tests + 5297 UI tests green. The new warning text (`"rejected for"`) appears only in `battle_state.py` and `ship_serialization.py` per repo-wide grep; no other production module emits it. Builder/UI paths never reach the save-restore log site.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Both save-restore paths log on rejection with reason
- [x] UI/builder paths do NOT log on rejection
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
