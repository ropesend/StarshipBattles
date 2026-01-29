# Phase 10: Package API Definition (AR-014)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-43 10`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Define explicit public APIs in __init__.py files with __all__

---

## Prerequisites
- [ ] Core phases complete

## Background

**Problem (AR-014):**
- Packages have inconsistent __init__.py organization
- No clear public vs. private module distinction
- Unclear package contracts, encourages implementation imports
- Refactoring harder due to unclear public API

**Target:** Add `__all__` to each package's __init__.py.

---

## Tasks

### Task 10.1: Audit Current __init__.py Files [Simple]
**Files:** All package __init__.py files
**Tests:** N/A (analysis)

- [ ] List all packages and their __init__.py status:
  - game/core/__init__.py
  - game/simulation/__init__.py
  - game/strategy/__init__.py
  - game/ui/__init__.py
  - game/engine/__init__.py
  - game/ai/__init__.py
- [ ] Document which have __all__ defined
- [ ] Document which exports are currently available
- [ ] Add to findings/phase_10_audit.md

**Notes:**

---

### Task 10.2: Define game/core Public API [Simple]
**File:** `game/core/__init__.py`
**Tests:** `pytest tests/unit/core/`

- [ ] Review all modules in game/core/
- [ ] Define `__all__` with public exports:
  - Vector2, clamp, lerp, angle_diff (math)
  - GameRegistries, get_default_registry_provider, etc. (registry)
  - GameState, LayerType, AttackType, etc. (constants)
  - log_info, log_error, etc. (logger)
  - ValidationResult (validation)
  - Paths (paths)
- [ ] Add docstring explaining public API
- [ ] Run core tests

**Notes:**

---

### Task 10.3: Define game/simulation Public API [Medium]
**File:** `game/simulation/__init__.py`
**Tests:** `pytest tests/unit/simulation/`

- [ ] Review all modules in game/simulation/
- [ ] Define `__all__` with public exports:
  - Ship, ShipSerializer (entities)
  - BattleEngine, BattleService (systems/services)
  - Component base classes (components)
  - Key data structures
- [ ] Keep internal modules private (not in __all__)
- [ ] Add docstring explaining public API
- [ ] Run simulation tests

**Notes:**

---

### Task 10.4: Define game/strategy Public API [Medium]
**File:** `game/strategy/__init__.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Review all modules in game/strategy/
- [ ] Define `__all__` with public exports:
  - Fleet, ShipInstance (data)
  - TurnEngine (engine)
  - StrategySessionFacade (facade)
  - IBattleResolver, BattleResult (interfaces)
- [ ] Keep internal modules private
- [ ] Add docstring explaining public API
- [ ] Run strategy tests

**Notes:**

---

### Task 10.5: Define game/ui Public API [Medium]
**File:** `game/ui/__init__.py`
**Tests:** `pytest tests/unit/ui/`

- [ ] Review all modules in game/ui/
- [ ] Define `__all__` with public exports:
  - Screen base classes
  - Key UI services
  - Public components
- [ ] Keep internal modules private
- [ ] Add docstring explaining public API
- [ ] Handle workshop_screen carefully (AR-006)
- [ ] Run UI tests

**Notes:**

---

### Task 10.6: Define game/engine Public API [Simple]
**File:** `game/engine/__init__.py`
**Tests:** `pytest tests/unit/engine/`

- [ ] Review all modules in game/engine/
- [ ] Define `__all__` with public exports:
  - Physics classes
  - Collision detection
  - Spatial queries
- [ ] Add docstring explaining public API
- [ ] Run engine tests

**Notes:**

---

### Task 10.7: Define game/ai Public API [Simple]
**File:** `game/ai/__init__.py`
**Tests:** `pytest tests/unit/ai/`

- [ ] Review all modules in game/ai/
- [ ] Define `__all__` with public exports:
  - AIController
  - Strategy classes
- [ ] Add docstring explaining public API
- [ ] Run AI tests

**Notes:**

---

### Task 10.8: Update Import Documentation [Simple]
**File:** `docs/ARCHITECTURE.md`
**Tests:** N/A

- [ ] Document recommended import patterns
- [ ] Explain public vs. private modules
- [ ] Provide examples of correct imports
- [ ] Document which __all__ are defined

**Notes:**

---

### Task 10.9: Verify Import Consistency [Simple]
**Tests:** Full test suite

- [ ] Run full test suite
- [ ] Verify no import errors
- [ ] Verify package-level imports work
- [ ] Test import from __all__ items

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All major packages have __all__ defined
- [ ] Public API documented in each __init__.py
- [ ] Architecture doc updated
- [ ] All tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 11
