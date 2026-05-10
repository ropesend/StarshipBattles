# Phase 6: BattleController & Collision Cleanup [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-58 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove BattleController proxy properties, simplify fallback logic, remove collision hasattr chain.

---

## Tasks

### Task 6.1: Remove BattleController engine Property [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ -x`
- [x] Find all callers of `controller.engine` (found: 1 test caller at `test_utilities.py:73`; `tests/fixtures/battle.py:154` is BattleScreen.engine, not BattleController)
- [x] Update test caller to use `controller.service.get_engine()`
- [x] Remove the `engine` property
- [x] Run tests: `pytest tests/unit/simulation/ -x`

### Task 6.2: Remove _retreating_ships and _escaped_ships Properties [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ -x`
- [x] Find all callers of `_retreating_ships` (found: test_utilities, test_mechanics, test_initialization)
- [x] Update to `controller._retreat_manager.retreating_ships` directly
- [x] Remove `_retreating_ships` property and setter
- [x] Find all callers of `_escaped_ships` (found: test_utilities, test_initialization, test_state)
- [x] Update to `controller._retreat_manager.escaped_ships` directly
- [x] Remove `_escaped_ships` property and setter
- [x] Removed unused `RetreatState` import from battle_controller.py
- [x] Fixed test imports: test_config.py and test_mechanics.py now import RetreatState from retreat_manager
- [x] Fixed test_initialization.py: init test checks `_retreat_manager is None`, configure test calls configure() first
- [x] Run tests: `pytest tests/unit/simulation/battle_controller/ -x` → 110 passed

### Task 6.3: Simplify Retreat/Reinforcement Fallback Logic [Medium]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/ tests/integration/ -x`
- [x] Investigated OR pattern: config.allow_retreat overrides mode_handler, not backward compat
- [x] Both are needed: mode handler provides defaults per mode, config can override to enable
- [x] Updated docstrings to explain the OR pattern purpose (not "backward compat")
- [x] Updated inline comments from "backward compat" to accurate descriptions

### Task 6.4: Remove Collision Defense Score Fallback [Simple]
**File:** `game/engine/collision.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ -x`
- [x] Verified `total_defense_score` always present on Ship (initialized to 1.0 at ship.py:168)
- [x] Replaced hasattr fallback chain with direct access: `defense_score = target.total_defense_score`
- [x] Removed `elif hasattr(target, 'get_total_ecm_score')` branch
- [x] Removed unused `log_warning` import
- [x] Removed 2 obsolete tests (test_beam_defense_score_fallback_logs_warning, test_beam_defense_score_uses_primary_attribute)
- [x] Run tests: `pytest tests/unit/combat/ tests/unit/engine/ -x` → 132 passed

### Task 6.5: Remove BattleScreen Backward Compat References [Simple]
**File:** `game/ui/screens/battle_screen.py`
**Tests:** `pytest tests/unit/ui/ -x`
- [x] Updated comment about initial battle creation (no longer mentions "backward compatibility")
- [x] Updated engine property docstring (no longer mentions "backward compatibility")
- [x] No actual compat code existed — only comments

### Task 6.6: Clean Up Remaining Comments [Simple]
**File:** `game/simulation/battle_controller.py`, `game/simulation/systems/battle_engine.py`
**Tests:** No test run needed (comment-only)
- [x] Updated 3 "backward compat" comments in battle_controller.py to accurate descriptions
- [x] Updated battle_engine.py legacy controller comment to clearer DEPRECATED label
- [x] Searched `game/simulation/` — no remaining "backward compat" references

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 7
