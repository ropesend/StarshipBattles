# Phase 2: Remove Deprecated Legacy AI Paths in BattleEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-106 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove all deprecated legacy code paths in BattleEngine that directly import from `game.ai`. After PROJ-17/PROJ-43, all production code uses `ai_factory` or pre-created `ai_controllers`. The legacy paths exist only as fallbacks with deprecation warnings.

---

## Context

BattleEngine has three legacy code paths that directly import from `game.ai`:
1. **`start()` method** (line 268-291): Legacy path when neither `ai_controllers` nor `ai_factory` is provided
2. **`add_ship_mid_battle()` method** (line 339-352): Legacy path when no `ai_controller` or `ai_factory` available
3. **`update()` fighter launch** (line 504-510): Legacy path when `_ai_factory` is None during fighter launch

All three emit `DeprecationWarning` and have comments referencing PROJ-17/PROJ-43.

**Key Question:** Can we safely remove these, or do any callers still rely on them?

---

## Tasks

### Task 2.1: Audit All BattleEngine.start() Call Sites [Medium]
**Tests:** `pytest tests/ -n 12 -k "battle" --co -q` (list test names)

- [ ] Grep for `engine.start(` or `.start(` calls that target BattleEngine across entire codebase
- [ ] For each call site, verify it passes `ai_controllers=` or `ai_factory=` parameter
- [ ] Document any callers that use the legacy path (no ai_controllers/ai_factory)
- [ ] Check test fixtures in `tests/fixtures/battle.py` and `tests/unit/combat/conftest.py`
- [ ] List all callers and their status in Notes below

**Notes:** [Fill during implementation]

---

### Task 2.2: Audit add_ship_mid_battle() Call Sites [Simple]
- [ ] Grep for `add_ship_mid_battle(` across entire codebase
- [ ] For each call site, verify it passes `ai_controller=` or uses engine with `ai_factory`
- [ ] Document any callers that rely on the legacy path

**Notes:** [Fill during implementation]

---

### Task 2.3: Make ai_factory Required or Assert Present [Medium]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ simulation_tests/ -v`

Depending on audit results from 2.1/2.2:

**Option A: All callers provide ai_factory/ai_controllers (expected)**
- [ ] In `start()` (around line 267): Remove the entire `else` block (lines 268-291) that does legacy AI creation
- [ ] Replace with a clear error: `raise ValueError("BattleEngine.start() requires ai_controllers or ai_factory parameter")`
- [ ] In `add_ship_mid_battle()` (around line 338): Remove the `else` block (lines 339-352)
- [ ] Replace with: `raise ValueError("add_ship_mid_battle() requires ai_controller or ai_factory")`
- [ ] In `update()` fighter launch (around line 503): Remove the `else` block (lines 504-510)
- [ ] Replace with: `raise ValueError("Fighter launch requires ai_factory on BattleEngine")`
- [ ] Remove all `import warnings` and `warnings.warn(...)` calls from these methods
- [ ] Remove the TYPE_CHECKING import of AIController on line 73 (if no longer needed anywhere in file)
- [ ] Run tests: `pytest tests/unit/combat/ tests/unit/simulation/ simulation_tests/ -v`

**Option B: Some callers still need legacy path (unlikely)**
- [ ] Update those callers to use ai_factory pattern instead
- [ ] Then proceed with Option A

---

### Task 2.4: Verify No Direct AI Imports Remain in Simulation [Simple]
**Finding:** ADR-SIM-002 final verification

- [ ] Grep for `from game.ai` in `game/simulation/` (exclude TYPE_CHECKING blocks)
- [ ] Only acceptable remaining import: `game/simulation/factories/ai_factory.py` (this is the designated boundary-crossing point)
- [ ] Verify `ai_factory.py` is the ONLY file in simulation that imports from `game.ai`
- [ ] Run full test suite: `pytest tests/ -n 12`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All legacy `from game.ai.controller import AIController` removed from battle_engine.py
- [ ] All `warnings.warn()` deprecation paths removed
- [ ] Only `ai_factory.py` imports from `game.ai` in simulation layer
- [ ] Full test suite passes: `pytest tests/ -n 12` (8164+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
