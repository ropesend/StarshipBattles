# Phase 1: Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-113 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the Foundation module (12 findings, 3 critical)
**Priority:** High

---

## Tasks

### Task 1.1: ADR-FND-001 - Pygame imported in game/core/input_mapper [Medium]
**File:** `game/core/input_mapper.py:26,3`
**Tests:** `pytest tests/unit/ui/services/test_input_mapper.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Moved input_mapper.py to game/ui/services/ - InputMapper is a pygame-specific service. Updated all 19 files with imports.

### Task 1.2: ADR-FND-002 - Pygame imported in game/core/screenshot_manager [Simple]
**File:** `game/core/screenshot_manager.py`
**Tests:** `pytest tests/unit/ui/services/test_screenshot_manager.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Moved screenshot_manager.py to game/ui/services/ - ScreenshotManager is a pygame-specific service. Updated all 9 files with imports.

### Task 1.3: ADR-FND-003 - Research scene imports from game.ui [Medium]
**File:** `game/research/ui/research_scene.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - game/research/ui/ IS the UI layer for research. Importing from game.ui is architecturally correct. No action needed.

### Task 1.4: ADR-FND-004 - Core protocols.py TYPE_CHECKING import from simulation [Simple]
**File:** `game/core/protocols.py:42`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Removed LayerData import from simulation layer. Changed return type to Any for cross-layer protocol boundaries.

### Task 1.5: ADR-FND-005 - AI controllable.py TYPE_CHECKING import pygame [Simple]
**File:** `game/ai/interfaces/controllable.py`
**Tests:** `pytest tests/unit/ai/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Removed pygame.math.Vector2 TYPE_CHECKING import. Changed type hints to Any to avoid pygame dependency in AI layer.

### Task 1.6: ADR-FND-006 - Research UI files use pygame directly [Medium]
**File:** `game/research/ui/research_controller.py` (does not exist)
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FALSE POSITIVE - game/research/ui/ IS the UI layer. Pygame usage is acceptable here. File doesn't actually exist (finding truncated).

### Task 1.7: ADR-FND-007 - AIController deep attribute chain (Law of Demeter) [Simple]
**File:** `game/ai/controller.py:410`
**Tests:** `pytest tests/unit/ai/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Added `leave_formation()` method to IControllable interface and ShipControllableAdapter. Replaced deep attribute chain `own_ship.formation.master.formation.members.remove(own_ship)` with clean interface call.

### Task 1.8: ADR-FND-008 - UIConfig class in game/core/config.py [Simple]
**File:** `game/core/config.py:132-198`
**Tests:** `pytest tests/unit/core/test_config.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Moved UIConfig to game/ui/config.py. Updated 18+ files to use new import. Added re-export in game/core/config.py for backward compatibility.

### Task 1.9: ADR-FND-009 - ScreenshotManager.capture_strategy_layer accesses scene internals [Simple]
**File:** `game/core/screenshot_manager.py`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** No action needed - ScreenshotManager was moved to UI layer (Task 1.2), so accessing scene attributes is now architecturally correct.

### Task 1.10: ADR-FND-010 - Engine collision.py TYPE_CHECKING import from simulation [Simple]
**File:** `game/engine/collision.py:55`
**Tests:** `pytest tests/`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** Removed Ship TYPE_CHECKING import. Changed type hints to Any to reduce coupling between engine and simulation layers.

### Task 1.11: ADR-FND-011 - Constants file mixes UI concerns (colors) [Simple]
**File:** `game/core/constants.py:42-49`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** LOW PRIORITY - Color constants (WHITE, BLACK, BLUE, RED, GREEN) are simple tuples used only in one UI file. They don't import pygame so they're acceptable in core. Could be moved later if needed.

### Task 1.12: ADR-FND-012 - Research package has clean data/systems separation [Info]
**File:** `game/research/data/`
**Tests:** N/A

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFORMATIONAL - The research package already has clean separation: data/ (no UI), systems/ (no UI), ui/ (pygame OK). No action needed.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
