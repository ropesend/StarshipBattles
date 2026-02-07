# Phase 5: BattleController Compat Cleanup [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-56 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove proxy properties and dual-path fallback logic from BattleController.

---

## Tasks

### Task 5.1: Investigate Collision Defense Score Fallback [Simple]
**File:** `game/engine/collision.py` (~lines 112-121)
**Tests:** Research first, then `pytest tests/unit/combat/ -x`
- [ ] Verify `total_defense_score` is a property on Ship (always present after init)
- [ ] Check if any non-Ship objects pass through the collision system (projectiles, asteroids, etc.)
- [ ] If all collision targets are Ships with `total_defense_score`: remove the `hasattr` fallback and `get_total_ecm_score()` path
- [ ] If non-Ship objects exist: add `total_defense_score` property to those objects instead of keeping fallback
- [ ] Remove the `log_warning` for fallback usage
- [ ] Run tests: `pytest tests/unit/combat/ tests/unit/simulation/ -x`
**Notes:** Decision was to investigate before removing. Document findings here.

### Task 5.2: Remove BattleController Retreat Proxy Properties [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ -x`
- [ ] Find all callers of `controller._retreating_ships` (the property, not `_retreat_manager.retreating_ships`)
- [ ] Update any callers to access `controller._retreat_manager.retreating_ships` directly
- [ ] Remove `_retreating_ships` property and setter (~lines 590-605)
- [ ] Find all callers of `controller._escaped_ships` (the property)
- [ ] Update any callers to access `controller._retreat_manager.escaped_ships` directly
- [ ] Remove `_escaped_ships` property and setter (~lines 607-620)
- [ ] Run tests: `pytest tests/unit/simulation/ -x`
**Notes:** These are private properties (prefixed with `_`) so callers should be limited.

### Task 5.3: Remove BattleController Engine Proxy Property [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ tests/integration/ -x`
- [ ] Find all callers of `controller.engine` (~line 584-586)
- [ ] Update callers to use `controller._service.get_engine()` or appropriate alternative
- [ ] Remove the `engine` property
- [ ] Run tests: `pytest tests/unit/simulation/ tests/integration/ -x`
**Notes:** This exposes the underlying BattleEngine "for backward compatibility".

### Task 5.4: Simplify Retreat/Reinforcement Fallback Logic [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ tests/integration/ -x`
- [ ] In `_retreat_allowed()`: Verify `_mode_handler` is always present (check all BattleController constructors)
- [ ] If always present: simplify to `return self._mode_handler.can_retreat()`
- [ ] If not always present: document WHY and keep the fallback, removing only the "backward compat" comment
- [ ] Repeat for `_reinforcements_allowed()`
- [ ] Remove "backward compat" comments from both methods
- [ ] Run tests: `pytest tests/unit/simulation/ tests/integration/ -x`
**Notes:** The OR logic (`mode_handler.can_retreat() or config.allow_retreat`) may be intentional - investigate before simplifying.

### Task 5.5: Clean Up Remaining Backward Compat Comments [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** No test run needed (comment-only)
- [ ] Search battle_controller.py for remaining "backward compat" or "backward compatibility" comments
- [ ] Remove any that refer to completed transitions
- [ ] Keep any that document genuinely temporary state (with documented timeline)
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
- [ ] No remaining proxy properties on BattleController
- [ ] Retreat/reinforcement logic uses single code path
