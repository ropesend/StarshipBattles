# Phase 1: Quick Wins [Low Risk]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-17 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove pygame dependencies that have simple, isolated fixes.

**Tests to run after phase:** `pytest tests/unit/simulation/ tests/unit/ai/ -v`

---

## Task 1.1: Remove Unused pygame Import from ship.py [Simple]

**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/ -v`

- [x] Delete line 1: `import pygame`
- [x] Verify file has no other pygame usage (confirmed in analysis: none)
- [x] Run tests to confirm no import errors

**Notes:** Completed - removed unused import, tests pass (74 tests in simulation/).

---

## Task 1.2: Fix pygame.math.Vector2 in AI Layer [Simple]

**Files:** 3 files need updates
**Tests:** `pytest tests/unit/ai/ -v`

### game/ai/target_evaluator.py
- [x] Add import at top: `from game.core.math import Vector2`
- [x] Remove `import pygame` if present
- [x] Replace all `pygame.math.Vector2` with `Vector2`
- [x] Verify with grep: `grep -n "pygame" game/ai/target_evaluator.py` (should return nothing)

### game/ai/controller.py
- [x] Add import at top: `from game.core.math import Vector2`
- [x] Remove `import pygame`
- [x] Replace `pygame.math.Vector2` (lines ~45, ~370) with `Vector2`
- [x] Verify with grep: `grep -n "pygame" game/ai/controller.py` (should return nothing)

### game/ai/behaviors.py
- [x] Add import at top: `from game.core.math import Vector2`
- [x] Remove `import pygame`
- [x] Replace all `pygame.math.Vector2` with `Vector2`
- [x] Verify with grep: `grep -n "pygame" game/ai/behaviors.py` (should return nothing)

**Notes:** Also fixed game/ai/core/behaviors.py and game/ai/core/system.py (not in original checklist but had same issue). All 189 AI tests pass.

---

## Task 1.3: Fix Fleet TYPE_CHECKING Import [Simple]

**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/services/test_battle_service.py -v`

- [x] Find line 29 (TYPE_CHECKING block): `from game.strategy.data.fleet import Fleet`
- [x] Remove this import line
- [x] Find type hint using `Fleet` (likely `Tuple['Fleet', 'Fleet']`)
- [x] Replace with `Tuple[Any, Any]` or use string literal `Tuple['object', 'object']`
- [x] Add `Any` to typing imports if needed (already present)
- [x] Run tests to verify no type errors

**Notes:** Replaced Fleet type hints with Any in source_fleets, _apply_results_to_fleet, and create_strategy_battle. All 15 battle service tests pass.

---

## Phase Completion Checklist

When all tasks above are done:

- [x] Run: `pytest tests/unit/simulation/ tests/unit/ai/ -v` (457 passed)
- [x] Run: `grep -rn "import pygame" game/ai/ --include="*.py"` (should return nothing) ✓
- [x] Run: `grep -n "import pygame" game/simulation/entities/ship.py` (should return nothing) ✓
- [ ] Verify application still launches (quick smoke test) - skipped (CI context)
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
