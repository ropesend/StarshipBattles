# Phase 9: Constant Consolidation (AR-013, AR-05)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 9`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Single canonical location for LayerType and shared constants

---

## Prerequisites
- [ ] Core phases (1-5) complete

## Background

**Problem (AR-013, AR-05):**
- LayerType defined in `game/simulation/components/component_constants.py`
- Also imported from `game/core/constants.py` in some UI files
- AI layer imports from simulation to use LayerType
- Confusing and error-prone

**Target:** Move LayerType to `game/core/constants.py` if not already, update all imports.

---

## Tasks

### Task 9.1: Audit LayerType Locations [Simple]
**Files:** Multiple
**Tests:** N/A (analysis)

- [ ] Check if LayerType exists in `game/core/constants.py`
- [ ] Check if LayerType exists in `game/simulation/components/component_constants.py`
- [ ] Run grep to find all LayerType imports:
  ```bash
  grep -rn "LayerType" game/
  ```
- [ ] Document all import locations in findings/phase_9_audit.md
- [ ] Identify canonical location

**Notes:**

---

### Task 9.2: Establish Canonical Location [Simple]
**File:** `game/core/constants.py`
**Tests:** `pytest tests/unit/core/`

If LayerType is not in core:
- [ ] Move LayerType enum to `game/core/constants.py`
- [ ] Add to `__all__` exports
- [ ] Verify definition is complete

If already in core:
- [ ] Verify it's in `__all__`
- [ ] Document as canonical location

**Notes:**

---

### Task 9.3: Update Simulation Imports [Medium]
**Files:** All simulation files importing LayerType
**Tests:** `pytest tests/unit/simulation/`

- [ ] Find all simulation files importing LayerType:
  ```bash
  grep -rn "from.*component_constants.*LayerType" game/simulation/
  ```
- [ ] Update to import from `game.core.constants`
- [ ] Remove re-exports from component_constants.py
- [ ] Run simulation tests

**Notes:**

---

### Task 9.4: Update AI Imports (AR-013) [Simple]
**File:** `game/ai/target_evaluator.py`
**Tests:** `pytest tests/unit/ai/`

**Current issue:** AI imports LayerType from simulation

- [ ] Update import to use `game.core.constants`
- [ ] Verify no other AI files import from simulation for constants
- [ ] Run AI tests

**Notes:**

---

### Task 9.5: Update UI Imports [Simple]
**Files:** All UI files importing LayerType
**Tests:** `pytest tests/unit/ui/`

- [ ] Find all UI files importing LayerType
- [ ] Update to import from `game.core.constants`
- [ ] Run UI tests

**Notes:**

---

### Task 9.6: Update Strategy Imports [Simple]
**Files:** All strategy files importing LayerType
**Tests:** `pytest tests/unit/strategy/`

- [ ] Find all strategy files importing LayerType
- [ ] Update to import from `game.core.constants`
- [ ] Run strategy tests

**Notes:**

---

### Task 9.7: Remove Duplicate Definitions [Simple]
**File:** `game/simulation/components/component_constants.py`
**Tests:** `pytest tests/unit/simulation/`

- [ ] Remove LayerType definition if moved to core
- [ ] Or add deprecation re-export:
  ```python
  # Deprecated: import from game.core.constants instead
  from game.core.constants import LayerType
  ```
- [ ] Run tests to verify no breakage

**Notes:**

---

### Task 9.8: Verify No Duplicate Imports [Simple]
**Tests:** `python -c "from game.core.constants import LayerType; from game.simulation.components.component_constants import LayerType"`

- [ ] Verify both imports resolve to same enum
- [ ] Verify no import errors
- [ ] Run full test suite

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] LayerType has single canonical location in game.core.constants
- [ ] All imports updated to use canonical location
- [ ] No duplicate definitions (only re-exports with deprecation warning if needed)
- [ ] All tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 10
