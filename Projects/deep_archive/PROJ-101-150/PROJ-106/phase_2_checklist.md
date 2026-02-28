# Phase 2: Remove Deprecated Legacy AI Paths in BattleEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-106 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
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

- [x] Grep for `engine.start(` or `.start(` calls that target BattleEngine across entire codebase
- [x] For each call site, verify it passes `ai_controllers=` or `ai_factory=` parameter
- [x] Document any callers that use the legacy path (no ai_controllers/ai_factory)
- [x] Check test fixtures in `tests/fixtures/battle.py` and `tests/unit/combat/conftest.py`
- [x] List all callers and their status in Notes below

**Notes:**
Audited all call sites:
- `tests/fixtures/battle.py`: Already injects `_ai_factory` at line 57-58
- `tests/integration/fleet_combat/test_service_integration.py`: Uses `create_battle_engine()` which has ai_factory
- `game/ui/screens/test_lab/`: Uses BattleScreen which uses BattleService which injects ai_factory
- `simulation_tests/scenarios/`: All scenarios get engine from test runners with ai_factory
- `test_framework/runner.py`: Was NOT injecting ai_factory - FIXED (added ai_factory injection at lines 28-31 and 96-98)
- `test_framework/scenarios/`: Uses engines from runner - now covered by fix

---

### Task 2.2: Audit add_ship_mid_battle() Call Sites [Simple]
- [x] Grep for `add_ship_mid_battle(` across entire codebase
- [x] For each call site, verify it passes `ai_controller=` or uses engine with `ai_factory`
- [x] Document any callers that rely on the legacy path

**Notes:**
- `game/simulation/battle_controller.py:370`: Calls without ai_controller, BUT engine is from BattleService which injects ai_factory - OK
- `tests/unit/combat/test_battle_engine_core.py`: Tests pass ai_controller or use factory - OK
- `tests/unit/simulation/battle_controller/test_mechanics.py`: Uses mock - OK

---

### Task 2.3: Make ai_factory Required or Assert Present [Medium]
**File:** `game/simulation/systems/battle_engine.py`
**Tests:** `pytest tests/unit/combat/ tests/unit/simulation/ simulation_tests/ -v`

Depending on audit results from 2.1/2.2:

**Option A: All callers provide ai_factory/ai_controllers (expected)** - IMPLEMENTED
- [x] In `start()` (around line 267): Remove the entire `else` block (lines 268-291) that does legacy AI creation
- [x] Replace with a clear error: `raise ValueError("BattleEngine.start() requires ai_controllers or ai_factory parameter")`
- [x] In `add_ship_mid_battle()` (around line 338): Remove the `else` block (lines 339-352)
- [x] Replace with: `raise ValueError("add_ship_mid_battle() requires ai_controller or ai_factory")`
- [x] In `update()` fighter launch (around line 503): Remove the `else` block (lines 504-510)
- [x] Replace with: `raise ValueError("Fighter launch requires ai_factory on BattleEngine")`
- [x] Remove all `import warnings` and `warnings.warn(...)` calls from these methods
- [x] Kept TYPE_CHECKING import of AIController on line 73 (still needed for type hints)
- [x] Run tests: `pytest tests/unit/combat/ tests/unit/simulation/ simulation_tests/ -v`

**Option B: Some callers still need legacy path (unlikely)**
- N/A - test_framework/runner.py was the only caller, and we fixed it to inject ai_factory

---

### Task 2.4: Verify No Direct AI Imports Remain in Simulation [Simple]
**Finding:** ADR-SIM-002 final verification

- [x] Grep for `from game.ai` in `game/simulation/` (exclude TYPE_CHECKING blocks)
- [x] Only acceptable remaining import: `game/simulation/factories/ai_factory.py` (this is the designated boundary-crossing point)
- [x] Verify `ai_factory.py` is the ONLY file in simulation that imports from `game.ai`
- [x] Run full test suite: `pytest tests/ -n 12`

**Notes:**
- `battle_engine.py:73`: Inside TYPE_CHECKING block - acceptable (type hints only)
- `ai_factory.py:57-58`: Runtime imports - acceptable (designated boundary crossing point)
- All other simulation files: No direct game.ai imports

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All legacy `from game.ai.controller import AIController` removed from battle_engine.py (only TYPE_CHECKING import remains)
- [x] All `warnings.warn()` deprecation paths removed
- [x] Only `ai_factory.py` imports from `game.ai` in simulation layer
- [x] Full test suite passes: `pytest tests/ -n 12` (8164 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

## Summary of Changes
1. **test_framework/runner.py**: Added AIControllerFactory import and injection at construction (line 28-31) and in run_scenario() (line 96-98)
2. **battle_engine.py start()**: Removed legacy path (lines 268-291), replaced with ValueError
3. **battle_engine.py add_ship_mid_battle()**: Removed legacy path, replaced with ValueError
4. **battle_engine.py update() fighter launch**: Removed legacy path, replaced with ValueError
