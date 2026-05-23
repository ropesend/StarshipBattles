# Phase 2: Save-restore path rejection logging (TDD)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-498 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Emit `logger.warning` with reason at the two save-restore boundaries when `Component.add_modifier()` returns False. Today both paths silently drop.

**Precondition:** Phase 1 complete (`check_allowance()` available).

---

## Tasks

### Task 2.1: Failing test for `battle_state.py` rejection log [Medium]
**File:** `tests/unit/simulation/test_battle_state.py` (or nearest existing module covering battle_state restoration)
**Tests:** `pytest tests/unit/simulation/test_battle_state.py -k rejection`

- [ ] Construct a battle-state save dict where a modifier exists in the registry but is `allow_abilities`-rejected for a given component
- [ ] Use `caplog` to assert `logger.warning` fires with component id, modifier id, and reason
- [ ] Confirm test fails (no log emitted today — `battle_state.py:274-280` silently drops)

**Notes:** [Filled during implementation]

### Task 2.2: Implement log at `battle_state.py:279` [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** same as 2.1

- [ ] Call `check_allowance()` before `add_modifier()` (or check `add_modifier()`'s False return) and emit `logger.warning(f"BattleState restore: modifier '{mid}' rejected for component '{new_comp.id}': {reason}")`
- [ ] Verify test passes

**Notes:** [Filled during implementation]

### Task 2.3: Failing test for `ship_serialization.py` rejection log [Medium]
**File:** `tests/unit/simulation/entities/test_ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_serialization.py -k rejection`

- [ ] Construct a ship JSON dict where a modifier exists in the registry but is `allow_abilities`-rejected
- [ ] Use `caplog` to assert a NEW warning fires (distinct from the existing unknown-id warning at `ship_serialization.py:228`)
- [ ] Confirm test fails

**Notes:** [Filled during implementation]

### Task 2.4: Implement log at `ship_serialization.py:226` [Simple]
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** same as 2.3

- [ ] Add a check-and-warn branch before/after `new_comp.add_modifier(mid, ...)` that logs reason on rejection
- [ ] Keep existing unknown-id warning intact
- [ ] Verify test passes

**Notes:** [Filled during implementation]

### Task 2.5: Spot-check no new log noise in builder/UI tests [Simple]
**File:** N/A
**Tests:** `pytest tests/regression/modifier_ability_snapshots/ tests/unit/ui/`

- [ ] Run the snapshot suite + UI tests with default log level
- [ ] Confirm no new warnings appear (builder rejections are intentional and should NOT log)

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Both save-restore paths log on rejection with reason
- [ ] UI/builder paths do NOT log on rejection
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
