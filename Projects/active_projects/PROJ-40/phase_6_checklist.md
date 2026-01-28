# Phase 6: AI System Improvements

**Status:** Not Started
**Estimated Effort:** 5-7 hours
**Priority:** Medium

## Overview
Address issues in `game/ai/` and `game/engine/` focusing on god class pattern, magic numbers, and interface violations.

---

## Tasks

### 6.1 Plan AIController Decomposition (NEW-AI-001)
**Location:** `game/ai/controller.py` (385 lines, 17 methods)
**Effort:** Complex (planning only in this phase)

- [ ] Document current AIController responsibilities:
  - Behavior selection
  - Target acquisition
  - Formation management
  - Collision avoidance
  - Movement navigation
- [ ] Create extraction plan:
  - [ ] `BehaviorSelector` class
  - [ ] `FormationManager` class
  - [ ] `NavigationController` class
- [ ] Add plan to `decisions.md`
- [ ] Extract ONE class as proof of concept
- [ ] Run: `pytest tests/unit/ai/ -v`

---

### 6.2 Extract AI Magic Numbers (NEW-AI-002)
**Location:** `game/ai/behaviors.py:104-105, 87`
**Effort:** Medium

- [ ] Create `AIConfig` class in `game/ai/config.py`
- [ ] Define named constants:
  - `MIN_SPACING`
  - `FLEE_DISTANCE`
  - `DEFAULT_AVOIDANCE`
  - Other scattered magic numbers
- [ ] Update behaviors.py to use `AIConfig`
- [ ] Update strategy_manager.py to control defaults
- [ ] Run: `pytest tests/unit/ai/ -v`

---

### 6.3 Fix FormationBehavior Interface Violations (NEW-AI-003)
**Location:** `game/ai/behaviors.py:212, 283, 317`
**Effort:** Medium

- [ ] Add `get_formation_rotation_mode()` to `IControllable` interface
- [ ] Remove direct `_ship` attribute access
- [ ] Replace `getattr(ship, '_ship', ship)` with interface method
- [ ] Update all IControllable implementations
- [ ] Run: `pytest tests/unit/ai/ -v -k formation`

---

### 6.4 Fix CollisionSystem Unsafe Access (NEW-AI-004)
**Location:** `game/engine/collision.py:152-166`
**Effort:** Simple

- [ ] Add null checks for `.hp` attribute access
- [ ] Use `getattr(s, 'hp', default_hp)` pattern
- [ ] Define sensible default (e.g., 100)
- [ ] Add type hints to clarify expected object interface
- [ ] Run: `pytest tests/unit/engine/ -v`

---

### 6.5 Move Runtime Imports to Module Level (NEW-AI-005)
**Location:** `game/ai/behaviors.py:378, 387`, `game/ai/target_evaluator.py:229`
**Effort:** Simple

- [ ] Move `import random` to module level
- [ ] Move `import math` to module level
- [ ] Verify no circular import issues
- [ ] Run: `pytest tests/unit/ai/ -v`

---

### 6.6 Add Type Hints to AIController (NEW-AI-006)
**Location:** `game/ai/controller.py:80, 95, 121, 140, 156, 195, 369`
**Effort:** Simple

- [ ] Add return type to `get_resolved_strategy()`
- [ ] Add return type to `find_target()`
- [ ] Add return type to `find_secondary_targets()`
- [ ] Add return type to `update()`
- [ ] Add return type to `navigate_to()`
- [ ] Run mypy if available

---

### 6.7 Fix SpatialGrid Duplicate Handling (NEW-AI-007)
**Location:** `game/engine/spatial.py:17-21`
**Effort:** Simple

- [ ] Add deduplication in `insert()` or `query_radius()`
- [ ] Choose approach: prevent duplicates at insert or filter in query
- [ ] Add unit test for duplicate handling
- [ ] Run: `pytest tests/unit/engine/ -v`

---

### 6.8 Standardize Collision Scoring (NEW-AI-008)
**Location:** `game/engine/collision.py:106-116`
**Effort:** Simple

- [ ] Standardize on single scoring method
- [ ] Remove cascading fallbacks if possible
- [ ] Document expected interface for targets
- [ ] Add warning log for fallback usage
- [ ] Run: `pytest tests/unit/engine/ -v`

---

### 6.9 Add Behavior Documentation (NEW-AI-009)
**Location:** `game/ai/behaviors.py`
**Effort:** Simple

- [ ] Add docstring to `FormationBehavior` explaining state machine
- [ ] Add docstring to `KiteBehavior` with decision tree
- [ ] Add docstring to `AttackRunBehavior` with parameters
- [ ] Document strategy parameters and expected values

---

### 6.10 Fix Division by Zero Risk (NEW-AI-010)
**Location:** `game/ai/behaviors.py:119`
**Effort:** Simple

- [ ] Add check: `if weapon_range == 0: weapon_range = MIN_SPACING`
- [ ] Or use max(weapon_range, MIN_SPACING) for opt_dist calculation
- [ ] Add unit test for zero weapon range case
- [ ] Run: `pytest tests/unit/ai/ -v`

---

## Verification

- [ ] Run AI tests: `pytest tests/unit/ai/ -v`
- [ ] Run engine tests: `pytest tests/unit/engine/ -v`
- [ ] Run integration tests with AI: `pytest tests/integration/test_ai_strategy.py -v`

---

## Notes
- Task 6.1 (AIController decomposition) is too large for one phase - create plan only
- Tasks 6.4-6.10 are quick wins that can be parallelized
- Consider creating separate PROJ for full AI refactoring if needed
