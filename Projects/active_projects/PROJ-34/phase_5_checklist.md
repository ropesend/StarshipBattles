# Phase 5: Cleanup and Documentation

**Objective:** Final cleanup and verification
**Status:** Not Started

---

## Task 5.1: Remove Deprecated Code [Simple]
**Tests:** Full test suite

- [ ] Review all deprecation warnings from Phase 4
- [ ] If all UI modules migrated successfully:
  - [ ] Consider removing deprecated properties (or keep with warnings for one release cycle)
- [ ] Remove unused imports from refactored files:
  - `strategy_fleet_ops.py`: Remove FleetOrder, OrderType if unused
  - `strategy_colonization.py`: Remove find_hybrid_path, FleetOrder, OrderType if unused
- [ ] Clean up any TODO comments added during refactoring
- [ ] Run full test suite to verify no regressions

**Notes:**

---

## Task 5.2: Update Tests [Medium]
**Tests:** `pytest tests/`

- [ ] Review tests that mock `session` directly
- [ ] Update tests to mock `facade` instead where appropriate
- [ ] Add integration tests for full command flow through facade:
  - [ ] `test_move_command_through_facade`
  - [ ] `test_colonize_command_through_facade`
  - [ ] `test_intercept_command_through_facade`
  - [ ] `test_join_command_through_facade`
  - [ ] `test_colonize_mission_through_facade`
- [ ] Verify no tests access deprecated properties directly
- [ ] Run full test suite: `pytest tests/`

**Notes:**

---

## Task 5.3: Update Design Document [Simple]
**File:** `Projects/active_projects/PROJ-34/design.md`

- [ ] Document final facade interface
- [ ] Document DTO structure
- [ ] Document command flow diagram
- [ ] Note any deviations from original plan
- [ ] Add lessons learned

**Notes:**

---

## Task 5.4: Final Verification [Medium]

### Automated Tests
- [ ] Run full test suite: `pytest tests/` (NOT --testmon)
- [ ] All tests pass (target: 4594+ tests)

### Manual Playtesting
- [ ] Start new game
- [ ] Issue move order - fleet moves correctly
- [ ] Issue colonize order - colony established
- [ ] Issue intercept order - fleet follows target
- [ ] Issue join order - fleets merge
- [ ] Queue colonize mission (distant planet) - path calculated, orders queued
- [ ] Process 5 turns - no crashes or unexpected behavior

### Code Review Checklist
- [ ] No direct `fleet.add_order()` in UI modules (grep search)
- [ ] No direct `fleet.path =` in UI modules (grep search)
- [ ] No direct `session.galaxy` access without deprecation warning
- [ ] All commands defined in `commands.py`
- [ ] All command handlers in `game_session.py`
- [ ] Facade returns DTOs, never domain objects

**Notes:**

---

## Phase 5 Verification
- [ ] All cleanup complete
- [ ] All tests updated and passing
- [ ] Documentation updated
- [ ] Final verification passed
- [ ] Project ready for closure
