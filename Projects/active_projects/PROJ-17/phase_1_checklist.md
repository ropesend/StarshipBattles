# Phase 1: Quick Wins [Low Risk]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-17 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove pygame dependencies that have simple, isolated fixes.

**Tests to run after phase:** `pytest tests/unit/simulation/ tests/unit/ai/ -v`

---

## Task 1.1: Remove Unused pygame Import from ship.py [Simple]

**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/ -v`

- [ ] Delete line 1: `import pygame`
- [ ] Verify file has no other pygame usage (confirmed in analysis: none)
- [ ] Run tests to confirm no import errors

**Notes:**

---

## Task 1.2: Fix pygame.math.Vector2 in AI Layer [Simple]

**Files:** 3 files need updates
**Tests:** `pytest tests/unit/ai/ -v`

### game/ai/target_evaluator.py
- [ ] Add import at top: `from game.core.math import Vector2`
- [ ] Remove `import pygame` if present
- [ ] Replace all `pygame.math.Vector2` with `Vector2`
- [ ] Verify with grep: `grep -n "pygame" game/ai/target_evaluator.py` (should return nothing)

### game/ai/controller.py
- [ ] Add import at top: `from game.core.math import Vector2`
- [ ] Remove `import pygame`
- [ ] Replace `pygame.math.Vector2` (lines ~45, ~370) with `Vector2`
- [ ] Verify with grep: `grep -n "pygame" game/ai/controller.py` (should return nothing)

### game/ai/behaviors.py
- [ ] Add import at top: `from game.core.math import Vector2`
- [ ] Remove `import pygame`
- [ ] Replace all `pygame.math.Vector2` with `Vector2`
- [ ] Verify with grep: `grep -n "pygame" game/ai/behaviors.py` (should return nothing)

**Notes:**

---

## Task 1.3: Fix Fleet TYPE_CHECKING Import [Simple]

**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/services/test_battle_service.py -v`

- [ ] Find line 29 (TYPE_CHECKING block): `from game.strategy.data.fleet import Fleet`
- [ ] Remove this import line
- [ ] Find type hint using `Fleet` (likely `Tuple['Fleet', 'Fleet']`)
- [ ] Replace with `Tuple[Any, Any]` or use string literal `Tuple['object', 'object']`
- [ ] Add `Any` to typing imports if needed
- [ ] Run tests to verify no type errors

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] Run: `pytest tests/unit/simulation/ tests/unit/ai/ -v`
- [ ] Run: `grep -rn "import pygame" game/ai/ --include="*.py"` (should return nothing)
- [ ] Run: `grep -n "import pygame" game/simulation/entities/ship.py` (should return nothing)
- [ ] Verify application still launches (quick smoke test)
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
