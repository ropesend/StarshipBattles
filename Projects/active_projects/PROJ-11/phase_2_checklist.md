# Phase 2: God Objects Refactoring

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-11 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Break up large classes that violate Single Responsibility Principle
**Priority:** CRITICAL - Blocks maintainability

---

## Tasks

### Task 2.1: AR-01/MOD-UI-01 - Break Up StrategyInterface [High]
**File:** `game/ui/screens/strategy_screen.py` (885 lines, 28 methods, 30+ fields)
**Tests:** `pytest tests/unit/ui/test_strategy_screen.py`

**Issue:** StrategyInterface manages layout, events, state, windows, and business logic in single class.

**Implementation:**
- [ ] Create `StrategyUILayout` - panel creation and positioning
- [ ] Create `StrategyUIState` - state tracking (selections, filters)
- [ ] Create `StrategyUIEventHandler` - event routing logic
- [ ] Create `StrategyUIWindowManager` - window/dialog management
- [ ] Refactor StrategyInterface to compose these components
- [ ] Target: StrategyInterface < 200 lines

**Notes:** Extract one component at a time. Keep tests passing after each extraction.

---

### Task 2.2: CQ-05/MOD-SIM-06 - Refactor Ship Class [High]
**File:** `game/simulation/entities/ship.py` (763 lines)
**Tests:** `pytest tests/unit/simulation/test_ship.py`

**Issue:** Ship combines 10+ concerns: physics, combat, resources, formation, validation, serialization, stat caching.

**Implementation:**
- [ ] Extract ComponentLayerManager - manage layers and components
- [ ] Move formation logic to ShipFormation (delegation already exists, clean up)
- [ ] Extract ResourceRegistry management to separate helper
- [ ] Move validation to ShipValidator (already exists, ensure used)
- [ ] Move serialization to ShipSerializer (already exists, ensure clean)
- [ ] Target: Ship < 400 lines, focused on coordination

**Notes:** Ship can remain the "facade" that coordinates, but shouldn't implement everything.

---

### Task 2.3: AR-08 - Refactor app.py Orchestrator [High]
**File:** `game/app.py` (733 lines, 50+ imports)
**Tests:** All integration tests

**Issue:** app.py imports from all layers and manages everything. Changes to any system require touching app.py.

**Implementation:**
- [ ] Create SceneManager - scene lifecycle management
- [ ] Create GameStateMachine - state transitions
- [ ] Create EventDispatcher - event routing
- [ ] Refactor Game class to compose managers
- [ ] Target: app.py < 300 lines

**Notes:** This is high risk. Make small changes, test frequently.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] StrategyInterface < 200 lines
- [ ] Ship < 400 lines
- [ ] app.py < 300 lines
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
