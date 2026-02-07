# Phase 6: BattleController & Collision Cleanup [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove BattleController proxy properties, simplify fallback logic, remove collision hasattr chain.

---

## Tasks

### Task 6.1: Remove BattleController engine Property [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ -x`
- [ ] Find all callers of `controller.engine` (expected: 2 test callers at `tests/fixtures/battle.py:154` and `tests/unit/simulation/battle_controller/test_utilities.py:73`)
- [ ] Update test callers to use `controller._service.get_engine()` or appropriate alternative
- [ ] Remove the `engine` property (~lines 589-592)
- [ ] Run tests: `pytest tests/unit/simulation/ -x`

### Task 6.2: Remove _retreating_ships and _escaped_ships Properties [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ -x`
- [ ] Find all callers of `_retreating_ships` (expected: 4 test callers)
- [ ] Update to `controller._retreat_manager.retreating_ships` directly
- [ ] Remove `_retreating_ships` property and setter (~lines 605-615)
- [ ] Find all callers of `_escaped_ships` (expected: 3 test callers + 1 internal at line 659)
- [ ] Update to `controller._retreat_manager.escaped_ships` directly
- [ ] Remove `_escaped_ships` property and setter (~lines 617-628)
- [ ] Run tests: `pytest tests/unit/simulation/ -x`

### Task 6.3: Simplify Retreat/Reinforcement Fallback Logic [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ tests/integration/ -x`
- [ ] Verify `_mode_handler` is always present after `configure()` is called (check all constructors)
- [ ] In `_retreat_allowed()` (~line 454-462): Investigate the OR pattern `mode_handler.can_retreat() or config.allow_retreat`
- [ ] If mode_handler is single source of truth: simplify to just `self._mode_handler.can_retreat()`
- [ ] If both are needed: keep but remove "backward compat" comment, document why both are needed
- [ ] Repeat for `_reinforcements_allowed()` (~line 464-472)
- [ ] Run tests: `pytest tests/unit/simulation/ tests/integration/ -x`
**Notes:** The OR logic may be intentional (config overrides mode handler). Investigate before simplifying.

### Task 6.4: Remove Collision Defense Score Fallback [Simple]
**File:** `game/engine/collision.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -x`
- [ ] Verify `total_defense_score` is always present on Ship (initialized to 1.0 at `ship.py:168`)
- [ ] Verify all collision targets are Ship instances (check what objects enter the collision system)
- [ ] Replace hasattr fallback chain (~lines 112-121) with direct access: `defense_score = target.total_defense_score`
- [ ] Remove the `elif hasattr(target, 'get_total_ecm_score')` branch
- [ ] Remove the `log_warning` for fallback
- [ ] Run tests: `pytest tests/unit/combat/ tests/unit/simulation/ -x`

### Task 6.5: Remove BattleScreen Backward Compat References [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/ -x`
- [ ] Lines 48-49: Remove "backward compatibility" comment about initial battle/engine
- [ ] Lines 161-162: Remove "backward compatibility" comment about engine access
- [ ] Check if any actual compat code exists beyond comments
- [ ] Run tests: `pytest tests/unit/ui/ -x`

### Task 6.6: Clean Up Remaining Comments [Simple]
**File:** `game/simulation/battle_controller.py`, `game/simulation/systems/battle_engine.py`
**Tests:** No test run needed (comment-only)
- [ ] Remove all "backward compat" / "backward compatibility" comments that reference completed transitions
- [ ] `battle_engine.py` lines 268-272: Keep the legacy controller creation path (out of scope) but remove/update the "backward compatibility" comment to explain its actual purpose
- [ ] Keep `apply_results_to_fleets()` legacy fallback comment but update to reference PROJ-41 blocker
- [ ] Search for any remaining "backward compat" comments in `game/simulation/`

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
