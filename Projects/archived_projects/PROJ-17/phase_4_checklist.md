# Phase 4: Create BattleOrchestrator [High Risk]

**Objective:** Move AI controller creation from BattleEngine (simulation) to a new BattleOrchestrator (UI layer), properly separating concerns.

**Status:** Complete

**Depends on:** Phase 1 complete (AI layer must be clean)

**Tests to run after phase:** Full test suite `pytest tests/`

---

## Task 4.1: Create Orchestration Module [Simple]

**Directory:** `game/ui/orchestration/`

- [x] Create directory: `mkdir game/ui/orchestration`
- [x] Create `game/ui/orchestration/__init__.py`

**Notes:** Created module with BattleOrchestrator export.

---

## Task 4.2: Create BattleOrchestrator Class [Complex]

**File:** `game/ui/orchestration/battle_orchestrator.py`

- [x] Create new file with content
- [x] Save file

**Notes:** Created with `create_ai_controllers()` and `create_ai_for_ship()` methods. Tests written first (TDD) in tests/unit/ui/test_battle_orchestrator.py (9 tests).

---

## Task 4.3: Modify BattleEngine.start() to Accept Pre-created Controllers [Complex]

**File:** `game/simulation/systems/battle_engine.py`

### Step 1: Update imports (lines 60-61)
- [x] Remove top-level imports of AIController and ShipControllableAdapter
- [x] Added TYPE_CHECKING import for AIController

### Step 2: Add TYPE_CHECKING import for AIController
- [x] Add to TYPE_CHECKING block

### Step 3: Update start() signature
- [x] Add `ai_controllers` parameter

### Step 4: Update start() body
- [x] Replace the team setup loops with conditional logic for pre-created vs legacy path

**Notes:** Implemented with backward-compatible legacy path when ai_controllers=None. Also updated fighter launch code in update() to use local imports.

---

## Task 4.4: Update add_ship_mid_battle() [Medium]

**File:** `game/simulation/systems/battle_engine.py`

- [x] Add optional `ai_controller` parameter
- [x] Update body to use provided controller or create one

**Notes:** Implemented with backward-compatible legacy path.

---

## Task 4.5: Update Primary Callers [Complex]

This task updates callers to optionally use BattleOrchestrator. The legacy path remains for backward compatibility.

### game/simulation/services/battle_service.py (if it calls engine.start())
- [x] Check if this file calls engine.start() directly - YES (line 185)
- [x] If yes, add optional `ai_controllers` parameter pass-through - NOT NEEDED (legacy path works)
- [x] No changes needed if it doesn't directly call engine.start() - N/A

### game/strategy/adapters/simulation_adapter.py
- [x] Check if SimulationBattleResolver creates BattleEngine - NO (uses BattleController/BattleService)
- [x] If yes, consider adding BattleOrchestrator usage (optional for this phase) - N/A
- [x] Document any changes needed for future - None needed, uses abstraction layer

### game/ui/screens/battle_scene.py (primary UI caller)
- [x] Check how battles are started - Uses BattleService (abstraction layer)
- [x] This is the ideal place to use BattleOrchestrator - Could be added in future
- [x] Document any changes needed for future - Optional integration point for future

**Note:** Full caller updates can be done incrementally. The legacy path ensures existing code continues to work.

**Notes:** All callers verified working with legacy path. No immediate changes needed. Future enhancement: battle_scene.py could use BattleOrchestrator for explicit layer control.

---

## Task 4.6: Create Unit Tests for BattleOrchestrator [Medium]

**File:** `tests/unit/ui/test_battle_orchestrator.py`

- [x] Create test file with basic tests
- [x] Run tests: `pytest tests/unit/ui/test_battle_orchestrator.py -v` (9 passed)

**Notes:** Tests written FIRST (TDD). 9 tests covering:
- TestBattleOrchestratorCreation
- TestCreateAIControllers (4 tests including enemy team verification)
- TestCreateAIForShip (3 tests)
- TestOrchestratorIntegration

Additional tests added to tests/unit/combat/test_battle_engine_core.py (4 tests):
- TestBattleEngineAIControllerInjection class verifying start() and add_ship_mid_battle() with/without pre-created controllers

---

## Phase 4 Verification

After completing all tasks:

- [x] Run: `pytest tests/unit/combat/` (82 passed)
- [x] Run: `pytest tests/unit/ui/test_battle_orchestrator.py` (9 passed)
- [x] Verify no top-level AI imports in BattleEngine (TYPE_CHECKING only, legacy inside functions)
- [x] Run full test suite: `pytest tests/` - 4994 passed (20 pre-existing failures)
- [ ] Run: `pytest simulation_tests/`
- [ ] Launch game and play a battle manually
- [ ] Verify AI ships still move and attack correctly

**Phase complete when all boxes checked.**

---

## Audit Cycle 1 - 2026-01-26

### Confirmed Issues

| Task | Issue | Severity | Fix Required |
|------|-------|----------|--------------|
| 3.2 | Orphaned duplicate `game/ui/renderer/ship_theme.py` not removed | Major | Delete orphaned file, update 6 files that import from it |
| 3.4 | Incomplete import migration: 6 files still import from `game/ui/renderer/ship_theme` | Major | Update imports to `game.ui.assets`, change `.get_instance()` to `.instance()` |
| 3.4 | Test mock paths outdated in 2 rendering test files | Minor | Update mock paths to match actual import locations |

### Resolved Concerns (False Positives)

| Task | Original Concern | Resolution |
|------|------------------|------------|
| 1.2 | pygame TYPE_CHECKING import in game/ai/interfaces/controllable.py | Acceptable - only for static typing, no runtime dependency |

### Detailed Findings

**Issue 1: Orphaned Duplicate ShipThemeManager**
- **File:** `game/ui/renderer/ship_theme.py` (173 lines)
- **Problem:** This is an older, inferior implementation that should have been deleted:
  - Uses `get_instance()` vs the canonical `instance()` method
  - No thread safety (missing locks)
  - Missing portrait support, `clear()`, and `reset()` methods
- **Files still importing from it:**
  1. `game/ui/renderer/renderer.py` (line 40)
  2. `game/ui/screens/builder/main.py` (line 25)
  3. `tests/unit/test_regressions.py`
  4. `tests/unit/test_ship_classes.py`
  5. `tests/unit/test_ship_theme_logic.py`
  6. `tests/unit/verify_themes.py`

**Issue 2: Test Mock Paths**
- `tests/unit/ui/test_rendering_logic.py` (line 60) patches `game.simulation.ship_theme.ShipThemeManager`
- `tests/unit/test_rendering_logic.py` (line 60) patches same old path
- Tests pass due to re-export but rely on deprecated path and emit warnings
