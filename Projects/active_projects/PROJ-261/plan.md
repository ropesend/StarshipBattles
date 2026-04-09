# PROJ-261: Fix Test Suite Production Bugs

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-261` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-261 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Fix shadowed test classes (BUG-1, BUG-2) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Fix no-op assertions (BUG-3) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Fix save_game_service NameError (BUG-4) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Fix research budget clamping (BUG-5) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-09
**Active Phase:** Planning Complete
**Last Action:** Plan written with verified line numbers
**Next Action:** Begin Phase 1 implementation
**Blockers:** None
**Context for Next Agent:** All 5 bugs have been verified in the codebase with exact line numbers. Phases 1-3 are mechanical fixes. Phase 4 requires a new test (TDD: write test first, then implement clamping logic).

## Overview
Five production bugs were found during a test suite review (see `Reviews/results/2026-04-08_test-review/final_report.md`). Two are shadowed test classes (Python silently replaces the first class with the second, so the first class's tests never run). Three are `assert X or True` no-op assertions that always pass. One is a latent `NameError` in exception handling. One is a missing allocation clamp when research budget is reduced.

## Goals
- Restore 5 shadowed test methods to the test suite (BUG-1: 1 method, BUG-2: 2 methods)
- Make 3 no-op assertions actually assert their conditions (BUG-3)
- Fix latent NameError that would mask JSONDecodeError in save loading (BUG-4)
- Prevent research allocations from exceeding budget after budget reduction (BUG-5)

## Scope
**In:**
- Renaming shadowed test classes (2 files)
- Removing `or True` from 3 assertions (3 files)
- Fixing `json.JSONDecodeError` to `JSONDecodeError` (1 file)
- Adding allocation clamping to `set_rp_budget()` (1 file + new test)

**Out:**
- Fixing test logic beyond what's needed to unshadow classes
- Refactoring the test files more broadly
- Any changes to save/load behavior beyond the exception fix
- Redesigning the research allocation system

## Key Files Reference
| Component | File Path | Line(s) | Bug |
|-----------|-----------|---------|-----|
| Shadowed TestHullAutoEquip (1st) | `tests/unit/entities/test_ship.py` | 276-292 | BUG-1 |
| Shadowed TestHullAutoEquip (2nd) | `tests/unit/entities/test_ship.py` | 403-441 | BUG-1 |
| Shadowed TestGameStateQueries (1st) | `tests/unit/strategy/facade/test_strategy_session_facade.py` | 453-478 | BUG-2 |
| Shadowed TestGameStateQueries (2nd) | `tests/unit/strategy/facade/test_strategy_session_facade.py` | 695-718 | BUG-2 |
| No-op assert (geometric) | `tests/unit/strategy/generation/density/test_geometric.py` | 86 | BUG-3 |
| No-op assert (spiral arm) | `tests/unit/strategy/generation/density/test_spiral_arm.py` | 78 | BUG-3 |
| No-op assert (layout loader) | `tests/unit/strategy/generation/density/test_layout_loader.py` | 150 | BUG-3 |
| JSONDecodeError import | `game/strategy/systems/save_game_service.py` | 13 | BUG-4 |
| json.JSONDecodeError except | `game/strategy/systems/save_game_service.py` | 463 | BUG-4 |
| set_rp_budget (no clamp) | `game/research/data/research_tracker.py` | 206-213 | BUG-5 |
| Existing budget tests | `tests/unit/research/test_research_tracker.py` | 235-257 | BUG-5 |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- `Reviews/results/2026-04-08_test-review/final_report.md` - Source review that found these bugs

---

## Detailed Bug Analysis

### BUG-1: Shadowed TestHullAutoEquip class
**File:** `tests/unit/entities/test_ship.py`

Two classes named `TestHullAutoEquip` exist at lines 276 and 403. Python silently replaces the first definition with the second. The first class (line 276) contains `test_hull_auto_equip` which verifies Ship auto-equips `default_hull_id` from vehicle class and checks `base_mass == 0.0`. This test never runs.

The second class (line 403, from PROJ-225) contains 3 tests for the extracted `_equip_default_hull` method.

**Fix:** Rename the first class (line 276) to `TestHullAutoEquipVerification` to match its docstring "TC-3.2.1: Hull Auto-Equip Verification". The second class keeps `TestHullAutoEquip` since it was written later as part of the PROJ-225 extraction and is the more comprehensive set.

**Impact:** Restores 1 test method to the suite.

### BUG-2: Shadowed TestGameStateQueries class
**File:** `tests/unit/strategy/facade/test_strategy_session_facade.py`

Two classes named `TestGameStateQueries` exist at lines 453 and 695. The first class (line 453) contains `test_get_turn_number` and `test_get_human_player_ids`. The second class (line 695, from PROJ-208 Phase 4) contains `test_get_save_path_returns_session_save_path` and `test_get_save_path_returns_none_when_not_saved`.

**Fix:** Rename the second class (line 695) to `TestGameStateQueriesSavePath` to reflect its specific scope (save path queries). The first class keeps the generic name since it tests the more fundamental queries.

**Impact:** Restores 2 test methods to the suite.

### BUG-3: `assert X or True` no-op assertions
Three assertions in density generation tests are no-ops because `or True` makes them always pass regardless of the left operand.

1. `test_geometric.py:86` -- `assert d1 != d2 or True` with comment "May be equal by coincidence"
2. `test_spiral_arm.py:78` -- `assert d1 != d2 or True` with comment "May be equal by coincidence"
3. `test_layout_loader.py:150` -- `assert coord is not None or True` with comment "Allow None for very sparse configs"

The original authors added `or True` as an escape hatch for non-deterministic results. The proper fix is to remove `or True` and let the assertions actually test. If the values really can be equal by coincidence, the test inputs should be chosen to make them reliably different; if they cannot be reliably different, the assertion should be removed entirely rather than kept as a no-op.

**Fix:** Remove `or True` from all three assertions. The test inputs (fixed coordinates, fixed seeds) are deterministic, so the assertions should be reliable.

**Impact:** 3 assertions now actually validate their conditions.

### BUG-4: Potential NameError in save_game_service.py
**File:** `game/strategy/systems/save_game_service.py`

Line 13 imports `from json import JSONDecodeError` (bare name). Line 282 correctly catches `except JSONDecodeError`. But line 463 catches `except (PermissionError, OSError, json.JSONDecodeError)` -- referencing `json.JSONDecodeError` when `json` module was never imported. If a `JSONDecodeError` is raised during `_read_save_info()`, Python will raise `NameError: name 'json' is not defined` instead, masking the real error.

**Fix:** Change `json.JSONDecodeError` to `JSONDecodeError` on line 463 to match the import and line 282's usage.

**Impact:** Fixes latent NameError that would occur on corrupt save file reads.

### BUG-5: Research budget reduction does not clamp allocations
**File:** `game/research/data/research_tracker.py`

`set_rp_budget()` (lines 206-213) sets the budget but does not check whether existing allocations exceed the new budget. If a player allocates 200 RP across nodes and then the budget drops to 100 (e.g., colony loss), `get_total_allocated()` returns 200 while `rp_budget` is 100 -- an impossible state. `get_remaining_rp()` uses `max(0, ...)` to avoid negative values but the core invariant (`total_allocated <= rp_budget`) is violated.

**Fix:** After clamping the budget, call a proportional clamp that scales down allocations if `get_total_allocated() > self.rp_budget`. The simplest correct approach: iterate all nodes with allocations, scale each down proportionally, and distribute any remainder from integer rounding.

**Impact:** Prevents impossible allocation state; needs new test.

---

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-09 | Rename first TestHullAutoEquip to TestHullAutoEquipVerification | Matches its TC-3.2.1 docstring; second class has more tests and is from later PROJ-225 work |
| 2026-04-09 | Rename second TestGameStateQueries to TestGameStateQueriesSavePath | Second class only tests save_path; first class has the more general queries |
| 2026-04-09 | Remove `or True` rather than removing entire assertions | The test inputs are deterministic (fixed coords/seeds), so the assertions should reliably pass |
| 2026-04-09 | Change `json.JSONDecodeError` to `JSONDecodeError` | Matches existing import on line 13 and usage on line 282; minimal change |
| 2026-04-09 | Proportional clamp in set_rp_budget | Preserves relative allocation priorities; better than clearing all allocations or arbitrary truncation |

---

## Phases

### Phase 1: Fix Shadowed Test Classes (BUG-1, BUG-2) [Simple]
**Objective:** Rename shadowed test classes so all test methods are discoverable by pytest.

**Tasks:**
1. Rename `TestHullAutoEquip` at line 276 to `TestHullAutoEquipVerification` in `tests/unit/entities/test_ship.py`
2. Rename `TestGameStateQueries` at line 695 to `TestGameStateQueriesSavePath` in `tests/unit/strategy/facade/test_strategy_session_facade.py`
3. Run affected test files and verify restored tests appear and pass

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

### Phase 2: Fix No-Op Assertions (BUG-3) [Simple]
**Objective:** Remove `or True` from 3 assertions so they actually validate.

**Tasks:**
1. Fix `test_geometric.py:86` -- remove `or True`
2. Fix `test_spiral_arm.py:78` -- remove `or True`
3. Fix `test_layout_loader.py:150` -- remove `or True`
4. Run all three test files and verify assertions pass without the escape hatch

See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

### Phase 3: Fix save_game_service NameError (BUG-4) [Simple]
**Objective:** Fix `json.JSONDecodeError` reference to use the already-imported `JSONDecodeError`.

**Tasks:**
1. Change `json.JSONDecodeError` to `JSONDecodeError` at line 463
2. Write a test that verifies `_read_save_info()` handles JSONDecodeError correctly (returns None, logs error)
3. Run existing save_game_service tests

See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

### Phase 4: Fix Research Budget Clamping (BUG-5) [Medium]
**Objective:** Ensure `set_rp_budget()` clamps allocations when budget decreases below total allocated.

**Tasks:**
1. **Write failing test first** (TDD): test that allocating RP then reducing budget clamps allocations
2. Implement proportional clamping in `set_rp_budget()`
3. Verify `get_total_allocated() <= rp_budget` invariant holds
4. Run all research_tracker tests

See [phase_4_checklist.md](phase_4_checklist.md) for detailed tasks.

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Run full test suite: `pytest tests/ -n 12` -- all tests pass (baseline)
- [ ] Note test count for comparison after fixes

### After Each Phase
- [ ] Run affected test files -- all pass
- [ ] Run `pytest tests/ --testmon` -- no regressions

### Final Verification
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py`
- [ ] Verify test count increased by at least 3 (restored shadowed tests)
- [ ] Verify no new test failures

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All tests passing
- [ ] Test count increased (restored shadowed tests)
- [ ] User verified
