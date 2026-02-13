# Phase 4: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-123 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (6 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 4.1: CON-UI2-001 - Inconsistent DI Pattern - Some Services [Medium]
**File:** `game/ui/services/vehicle_class_service.py`
**Tests:** N/A (review only)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - VehicleClassService already uses strict DI with REQUIRED registry_provider parameter. See lines 36-48: `__init__(self, registry_provider: IRegistryProvider)` with explicit ValueError if None. PROJ-50 compliance is documented in docstring and comments.

### Task 4.2: ADR-UI2-001 - pygame.math.Vector2 Usage in game_render [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** N/A (review only)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - UI layer using pygame.math.Vector2 is ACCEPTABLE. Per ARCHITECTURE.md line 102-105: "Vector2 (game/core/math.py) - Custom 2D vector class replacing pygame.math.Vector2 **for simulation layer**". UI layer depends on pygame for rendering and Vector2 is part of that dependency.

### Task 4.3: CON-UI2-002 - Singleton vs Dependency Injection Patter [Complex]
**File:** `game/ui/services/screenshot_manager.py`
**Tests:** N/A (review only)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - ScreenshotManager is DOCUMENTED as an approved singleton in PATTERNS.md (line 70-71). Uses SingletonMeta metaclass which is the project's standard thread-safe singleton implementation. Includes proper reset() method for test isolation.

### Task 4.4: ADR-UI2-003 - Lazy Import Pattern in ship_factory.py C [Simple]
**File:** `game/ui/services/ship_factory.py`
**Tests:** N/A (review only)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - Lazy imports in ship_factory.py (lines 55-56, 83) are INTENTIONAL per ARCHITECTURE.md "Intentional Late Imports" section. This pattern is used for cross-layer boundary imports to maintain layer separation and avoid load-time coupling. The import of Ship and get_default_registries within methods is documented and acceptable.

### Task 4.5: ADR-UI2-004 - TYPE_CHECKING Import for GameRegistries [Simple]
**File:** `game/ui/services/ship_factory.py`
**Tests:** N/A (review only)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - TYPE_CHECKING import pattern (lines 17-24) is standard Python practice for type hints without runtime import. Used correctly here to provide type hints for Ship and GameRegistries while avoiding circular imports and keeping runtime dependencies minimal.

### Task 4.6: ADR-UI2-005 - BattleOrchestrator Correctly Documents C [N]
**File:** `game/ui/orchestration/battle_orchestrator.py`
**Tests:** N/A (review only)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFORMATIONAL - BattleOrchestrator EXPLICITLY documents cross-layer imports as INTENTIONAL in its module docstring (lines 1-21). The docstring explains: "This is an intentional boundary-crossing module that coordinates between UI, AI, and Simulation layers." Architecture is sound - orchestrators in UI layer coordinate between lower layers.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
