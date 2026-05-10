# PROJ-250 Phase 2: Add Tests

> **BEFORE MARKING THIS PHASE COMPLETE:**
> Run: `pytest tests/unit/simulation/ -x`

## Objective
Add unit tests proving the retreat priority behavior.

## Status: Not Started

---

### Task 2.1: Test Retreat Priority Behavior [Simple]
**File:** `tests/unit/simulation/test_battle_controller.py` (new or existing)
**Tests:** `pytest tests/unit/simulation/ -x`

- [ ] Test: mode_handler returns False, config.allow_retreat=True → retreat IS allowed (config override)
- [ ] Test: mode_handler returns True, config.allow_retreat=False → retreat IS allowed (mode handler default)
- [ ] Test: mode_handler returns False, config.allow_retreat=False → retreat NOT allowed (both deny)
- [ ] Test: mode_handler returns True, config.allow_retreat=True → retreat IS allowed (both allow)

**Notes:** May need to mock BattleModeHandler.can_retreat() for these tests.
