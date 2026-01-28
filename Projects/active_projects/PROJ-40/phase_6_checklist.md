# Phase 6: AI System Improvements

**Status:** Not Started
**Estimated Effort:** 2-3 hours
**Priority:** Medium

## Overview
Address remaining issues in `game/ai/` and `game/engine/` focusing on unsafe access and documentation.

> **Note:** This phase was reduced from 10 tasks to 4 after Category 3 audit verification:
> - Task 6.1 (NEW-AI-001) REMOVED - AIController is well-organized (384 lines, 16 methods)
> - Task 6.2 (NEW-AI-002) REMOVED - Magic numbers ARE properly defined as AIConfig constants
> - Task 6.3 (NEW-AI-003) REMOVED - Uses safe getattr() with defaults
> - Task 6.5 (NEW-AI-005) REMOVED - Localized imports are acceptable
> - Task 6.7 (NEW-AI-007) REMOVED - Intentional spatial indexing behavior
> - Task 6.10 (NEW-AI-010) REMOVED - No division operation exists at cited location

---

## Tasks

### 6.1 Fix CollisionSystem Unsafe Access (NEW-AI-004)
**Location:** `game/engine/collision.py:152-166`
**Effort:** Simple

- [ ] Add null checks for `.hp` attribute access
- [ ] Use `getattr(s, 'hp', default_hp)` pattern
- [ ] Define sensible default (e.g., 100)
- [ ] Add type hints to clarify expected object interface
- [ ] Run: `pytest tests/unit/engine/ -v`

---

### 6.2 Add Type Hints to AIController (NEW-AI-006)
**Location:** `game/ai/controller.py:80, 95, 121, 140, 156, 195, 369`
**Effort:** Simple

- [ ] Add return type to `get_resolved_strategy()`
- [ ] Add return type to `find_target()`
- [ ] Add return type to `find_secondary_targets()`
- [ ] Add return type to `update()`
- [ ] Add return type to `navigate_to()`
- [ ] Run mypy if available

---

### 6.3 Standardize Collision Scoring (NEW-AI-008)
**Location:** `game/engine/collision.py:106-116`
**Effort:** Simple

- [ ] Standardize on single scoring method
- [ ] Remove cascading fallbacks if possible
- [ ] Document expected interface for targets
- [ ] Add warning log for fallback usage
- [ ] Run: `pytest tests/unit/engine/ -v`

---

### 6.4 Add Behavior Documentation (NEW-AI-009)
**Location:** `game/ai/behaviors.py`
**Effort:** Simple

- [ ] Add docstring to `FormationBehavior` explaining state machine
- [ ] Add docstring to `KiteBehavior` with decision tree
- [ ] Add docstring to `AttackRunBehavior` with parameters
- [ ] Document strategy parameters and expected values

---

## Removed Tasks (Audit Verification)

### ~~6.1 Plan AIController Decomposition (NEW-AI-001)~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** AIController (384 lines, 16 methods) is well-organized with focused methods for strategy resolution, target selection, formation handling, collision avoidance, and navigation.

### ~~6.2 Extract AI Magic Numbers (NEW-AI-002)~~
**Status:** REMOVED - ALREADY COMPLETE
**Reason:** All magic numbers ARE properly defined as class constants via AIConfig:
```python
FLEE_DISTANCE: int = AIConfig.FLEE_DISTANCE
MIN_SPACING: int = AIConfig.MIN_SPACING
DEFAULT_AVOIDANCE: bool = True
```

### ~~6.3 Fix FormationBehavior Interface Violations (NEW-AI-003)~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** Uses safe patterns: `getattr(ship, '_ship', ship)` with safe fallback.

### ~~6.5 Move Runtime Imports to Module Level (NEW-AI-005)~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** Localized imports of `random` and `math` are acceptable practice.

### ~~6.7 Fix SpatialGrid Duplicate Handling (NEW-AI-007)~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** Intentional spatial indexing behavior.

### ~~6.10 Fix Division by Zero Risk (NEW-AI-010)~~
**Status:** REMOVED - NOT AN ISSUE
**Reason:** No division operation exists at the cited location (behaviors.py:119).

---

## Verification

- [ ] Run AI tests: `pytest tests/unit/ai/ -v`
- [ ] Run engine tests: `pytest tests/unit/engine/ -v`
- [ ] Run integration tests with AI: `pytest tests/integration/test_ai_strategy.py -v`

---

## Notes
- All remaining tasks are relatively simple
- Tasks can be parallelized
- Focus on documentation and defensive coding
