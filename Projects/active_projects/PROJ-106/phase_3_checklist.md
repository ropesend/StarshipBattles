# Phase 3: Create Strategy Metadata Service (Eliminate AI->UI Coupling)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-106 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create a strategy metadata service that provides strategy names and IDs without requiring UI to import from `game.ai.strategy_manager`. Currently 8 UI files import StrategyManager directly -- this phase eliminates all of them.

---

## Context

### What UI Uses StrategyManager For
Analysis of all 10 UI call sites shows UI needs exactly these operations:
1. **Get strategy list** (names + IDs) for dropdowns: `StrategyManager.instance().strategies` (dict of id -> strategy data)
2. **Resolve strategy ID to display name**: `strategies.get(id, {}).get('name', id)`
3. **Resolve display name back to strategy ID**: iterate `strategies.items()` matching on name
4. **Clear strategies**: `StrategyManager.instance().clear()` (only in WorkshopDataLoader)
5. **Load strategies**: `manager.load_data(...)` (only in WorkshopDataLoader)

### Design Decision: StrategyMetadataService in game.core
Create `game.core.strategy_metadata.py` with a simple service that:
- Provides strategy names/IDs for UI dropdowns
- Can be populated by StrategyManager (in AI layer) or directly by data loading
- Has no dependency on game.ai

The StrategyManager remains in game.ai as the authoritative source for AI-layer strategy logic (targeting policies, movement policies). The metadata service only holds the display-facing data.

### Alternative Considered: Move StrategyManager to game.core
Rejected -- StrategyManager has `ensure_loaded()`, default policies, and is tightly coupled to AI behavior loading. It belongs in game.ai. Only the metadata (names/IDs) should be in core.

---

## Tasks

### Task 3.1: Create StrategyMetadataService [Medium]
**File:** `game/core/strategy_metadata.py` (NEW)
**Tests:** `tests/unit/core/test_strategy_metadata.py` (NEW)

- [ ] Create `game/core/strategy_metadata.py` with class `StrategyMetadataService`
- [ ] Implement as a simple singleton (matching existing patterns like StrategyManager)
- [ ] Required public API:
  - `instance()` -> StrategyMetadataService (classmethod, thread-safe)
  - `reset()` -> None (classmethod, for testing)
  - `clear()` -> None (reset data, preserve instance)
  - `strategies` property -> Dict[str, dict] (strategy_id -> {name, ...})
  - `get_strategy_names()` -> List[str] (display names for dropdowns)
  - `get_strategy_display_name(strategy_id: str)` -> str (resolve ID to name)
  - `get_strategy_id_by_name(display_name: str)` -> Optional[str] (resolve name to ID)
  - `load_data(base_path, strategy_file)` -> None (load strategy metadata from JSON)
  - `set_strategies(strategies: dict)` -> None (set data directly, used by StrategyManager)
- [ ] Write unit tests in `tests/unit/core/test_strategy_metadata.py`
- [ ] Run tests: `pytest tests/unit/core/test_strategy_metadata.py -v`

---

### Task 3.2: Wire StrategyManager to Populate StrategyMetadataService [Simple]
**File:** `game/ai/strategy_manager.py`
**Tests:** `pytest tests/unit/ai/ -v`

- [ ] In `StrategyManager.load_data()` (line 117), after loading strategies, call:
  `StrategyMetadataService.instance().set_strategies(self.strategies)`
- [ ] In `StrategyManager.clear()` (line 89), also call:
  `StrategyMetadataService.instance().clear()`
- [ ] Add import: `from game.core.strategy_metadata import StrategyMetadataService`
- [ ] Run tests: `pytest tests/unit/ai/ -v`

---

### Task 3.3: Update builder/right_panel.py [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/ui/ -v -k builder`

- [ ] Replace `from game.ai.strategy_manager import StrategyManager` (line 13) with `from game.core.strategy_metadata import StrategyMetadataService`
- [ ] Line 114: Replace `StrategyManager.instance().strategies` with `StrategyMetadataService.instance().strategies`
- [ ] Line 206: Replace `StrategyManager.instance().strategies` with `StrategyMetadataService.instance().strategies`
- [ ] Run tests: `pytest tests/unit/ui/ -v -k builder`

---

### Task 3.4: Update builder/main.py [Simple]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/ui/ -v -k builder`

- [ ] Line 724: Replace `from game.ai.strategy_manager import StrategyManager` with `from game.core.strategy_metadata import StrategyMetadataService`
- [ ] Line 726: Replace `StrategyManager.instance().strategies` with `StrategyMetadataService.instance().strategies`
- [ ] Run tests: `pytest tests/unit/ui/ -v -k builder`

---

### Task 3.5: Update setup_renderer.py [Simple]
**File:** `game/ui/screens/setup_renderer.py`
**Tests:** `pytest tests/unit/ui/ -v -k setup`

- [ ] Line 10: Replace `from game.ai.strategy_manager import StrategyManager` with `from game.core.strategy_metadata import StrategyMetadataService`
- [ ] Line 98: Replace `StrategyManager.instance().strategies` with `StrategyMetadataService.instance().strategies`
- [ ] Line 197: Replace `StrategyManager.instance().strategies` with `StrategyMetadataService.instance().strategies`
- [ ] Run tests: `pytest tests/unit/ui/ -v -k setup`

---

### Task 3.6: Update setup_screen.py [Simple]
**File:** `game/ui/screens/setup_screen.py`
**Tests:** `pytest tests/unit/ui/ -v -k setup`

- [ ] Line 15: Replace `from game.ai.strategy_manager import StrategyManager` with `from game.core.strategy_metadata import StrategyMetadataService`
- [ ] Line 59: Replace `StrategyManager.instance().strategies` with `StrategyMetadataService.instance().strategies`
- [ ] Run tests: `pytest tests/unit/ui/ -v -k setup`

---

### Task 3.7: Update ship_stats_renderer.py [Simple]
**File:** `game/ui/panels/ship_stats_renderer.py`
**Tests:** `pytest tests/unit/ui/ -v -k stats`

- [ ] Line 12: Replace `from game.ai.strategy_manager import StrategyManager` with `from game.core.strategy_metadata import StrategyMetadataService`
- [ ] Line 243: Replace `StrategyManager.instance().strategies` with `StrategyMetadataService.instance().strategies`
- [ ] Run tests: `pytest tests/unit/ui/ -v`

---

### Task 3.8: Update workshop_data_loader.py [Medium]
**File:** `game/ui/screens/workshop_data_loader.py`
**Tests:** `pytest tests/unit/ui/ -v -k workshop`

This file uses StrategyManager for more than just reading -- it calls `clear()` and `load_data()`.

- [ ] Line 99: Replace `from game.ai.strategy_manager import StrategyManager` with `from game.core.strategy_metadata import StrategyMetadataService`
- [ ] Line 104: Replace `StrategyManager.instance().clear()` with `StrategyMetadataService.instance().clear()`
- [ ] Line 160: Replace `from game.ai.strategy_manager import StrategyManager` with `from game.core.strategy_metadata import StrategyMetadataService`
- [ ] Lines 165-174: Replace `StrategyManager.instance()` usage with `StrategyMetadataService.instance()`
- [ ] NOTE: The `load_data()` call on StrategyMetadataService must load the same strategy JSON data. Ensure the service's `load_data()` method supports the same `base_path` + file name parameters
- [ ] Run tests: `pytest tests/unit/ui/ -v -k workshop`

---

### Task 3.9: Update workshop_event_router.py [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/ui/ -v -k workshop`

- [ ] Line 455: Replace `from game.ai.strategy_manager import StrategyManager` with `from game.core.strategy_metadata import StrategyMetadataService`
- [ ] Lines 457-463: Replace `StrategyManager.instance()` with `StrategyMetadataService.instance()`
- [ ] Run tests: `pytest tests/unit/ui/ -v -k workshop`

---

### Task 3.10: Verify No AI Imports Remain in UI (except intentional) [Simple]

- [ ] Grep for `from game.ai` in `game/ui/` directory
- [ ] Only acceptable remaining imports:
  - `game/ui/orchestration/battle_orchestrator.py` -- intentional cross-layer orchestration (ADR-UI2-010)
- [ ] Verify zero `StrategyManager` references in `game/ui/`
- [ ] Run full test suite: `pytest tests/ -n 12`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `StrategyMetadataService` created and tested in `game/core/`
- [ ] All 8 UI files updated to use `StrategyMetadataService` instead of `StrategyManager`
- [ ] Zero `from game.ai.strategy_manager` imports remain in `game/ui/`
- [ ] Full test suite passes: `pytest tests/ -n 12` (8164+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
