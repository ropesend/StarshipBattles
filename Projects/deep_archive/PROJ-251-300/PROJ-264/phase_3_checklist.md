# Phase 3: Facade Dispatch Helpers [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-264 3`
> 2. Only proceed if output shows PASSED

**Objective:** Write tests for all 26+ dispatch methods on StrategySessionFacade plus build queue queries.
**Status:** Not Started

---

## Task 3.1: Create test_facade_dispatch.py [Medium]
**File:** `tests/unit/strategy/facade/test_facade_dispatch.py` (NEW)
**Source:** `game/strategy/facade/strategy_session_facade.py` lines 89-242, 600-622
**Tests:** `pytest tests/unit/strategy/facade/test_facade_dispatch.py -v`

### Setup
- [ ] Read source to catalog all dispatch methods and their command classes
- [ ] Create fixture with mocked session and mocked handle_command
- [ ] Use parametrize to reduce boilerplate

### Dispatch method tests (one per method)
- [ ] All 31 dispatch methods tested (see plan.md Phase 3 for full list)

### Build queue query tests (lines 600-622)
- [ ] `test_get_empire_build_queues_valid_empire`
- [ ] `test_get_empire_build_queues_unknown_empire`
- [ ] `test_get_hex_build_queues_valid`
- [ ] `test_get_hex_build_queues_unknown_empire`

## Phase 3 Verification
- [ ] New test file passes
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Coverage increased on strategy_session_facade.py
