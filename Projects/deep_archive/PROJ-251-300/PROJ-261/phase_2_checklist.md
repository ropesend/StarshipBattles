# Phase 2: Fix No-Op Assertions (BUG-3) [Simple]

**Objective:** Remove `or True` from 3 assertions so they actually validate their conditions.
**Status:** Not Started

---

## Task 2.1: Fix test_geometric.py assertion [Simple]
**File:** `tests/unit/strategy/generation/density/test_geometric.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_geometric.py -v`
- [ ] Read the test at line 86 to confirm `assert d1 != d2 or True`
- [ ] Change `assert d1 != d2 or True` to `assert d1 != d2` (line 86)
- [ ] Run the test file — verify the assertion passes without the escape hatch
- [ ] If the assertion fails, the test inputs need to be made deterministic (pick coordinates that reliably produce different values with rotation)
**Notes:**

## Task 2.2: Fix test_spiral_arm.py assertion [Simple]
**File:** `tests/unit/strategy/generation/density/test_spiral_arm.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_spiral_arm.py -v`
- [ ] Read the test at line 78 to confirm `assert d1 != d2 or True`
- [ ] Change `assert d1 != d2 or True` to `assert d1 != d2` (line 78)
- [ ] Run the test file — verify the assertion passes
- [ ] If the assertion fails, adjust test coordinates to reliably differentiate rotated patterns
**Notes:**

## Task 2.3: Fix test_layout_loader.py assertion [Simple]
**File:** `tests/unit/strategy/generation/density/test_layout_loader.py`
**Tests:** `pytest tests/unit/strategy/generation/density/test_layout_loader.py -v`
- [ ] Read the test at line 150 to confirm `assert coord is not None or True`
- [ ] Change `assert coord is not None or True` to `assert coord is not None` (line 150)
- [ ] Run the test file — verify the assertion passes
- [ ] If the assertion fails for sparse configs, either pick a denser config for the test or remove the assertion entirely with a comment explaining why
**Notes:**

## Phase 2 Verification
- [ ] All 3 test files pass: `pytest tests/unit/strategy/generation/density/ -v`
- [ ] No regressions: `pytest tests/ --testmon`
