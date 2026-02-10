# Phase 2: EmpireBuildQueueWindow Formatter [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-89 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract data formatting methods from EmpireBuildQueueWindow into a standalone `empire_build_queue_formatter.py` module. These are pure data transforms (mostly `@staticmethod`) with no UI dependencies.

**File:** `game/ui/screens/empire_build_queue_window.py`
**New File:** `game/ui/screens/empire_build_queue_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py tests/unit/ui/screens/test_empire_build_queue_formatter.py`

---

## Tasks
### Task 2.1: Create empire_build_queue_formatter.py with extracted functions [Simple]
**File:** `game/ui/screens/empire_build_queue_formatter.py`
- [x] Create new module with docstring explaining it provides data formatting for build queue display
- [x] Add imports: `from typing import Any, Optional, TYPE_CHECKING`
- [x] Add TYPE_CHECKING import for `BuildQueueSource`
- [x] Extract `get_queue_summary(source)` as standalone function:
  - Signature: `def get_queue_summary(source: BuildQueueSource) -> str`
  - Copy implementation from lines 496-508 of empire_build_queue_window.py
- [x] Extract `get_first_item_text(source)` as standalone function:
  - Signature: `def get_first_item_text(source: BuildQueueSource) -> str`
  - Copy implementation from lines 511-525
- [x] Extract `get_capabilities_text(source)` as standalone function:
  - Signature: `def get_capabilities_text(source: BuildQueueSource) -> str`
  - Copy implementation from lines 528-543
- [x] Extract `get_system_name(source, galaxy)` as standalone function:
  - Signature: `def get_system_name(source: BuildQueueSource, galaxy: Any) -> str`
  - Copy implementation from lines 870-895, replacing `self.galaxy` with `galaxy` parameter
- [x] Extract `get_sector_text(source)` as standalone function:
  - Signature: `def get_sector_text(source: BuildQueueSource) -> str`
  - Copy implementation from lines 898-917
- [x] Extract `get_turns_left_text(source)` as standalone function:
  - Signature: `def get_turns_left_text(source: BuildQueueSource) -> str`
  - Copy implementation from lines 920-933
- [x] Verify the module has no dependency on pygame, pygame_gui, UIWindow, or any UI imports

**Notes:** Created 131-line module with 6 pure data formatting functions.

---

### Task 2.2: Write unit tests for empire_build_queue_formatter.py [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_formatter.py`
- [x] Create helper `_make_source()` function (same pattern as existing test file)
- [x] Create `TestGetQueueSummary` class:
  - Test: empty queue returns "-"
  - Test: single item returns "1 item" (no plural)
  - Test: multiple items returns "N items"
- [x] Create `TestGetFirstItemText` class:
  - Test: empty queue returns "-"
  - Test: queue with item returns design_id and turns
- [x] Create `TestGetCapabilitiesText` class:
  - Test: ships only returns "Ships"
  - Test: complexes only returns "Complexes"
  - Test: both returns "Ships & Complexes"
  - Test: neither returns "None"
- [x] Create `TestGetSystemName` class:
  - Test: planet with system_name attribute returns it
  - Test: planet with galaxy lookup returns system name
  - Test: fleet with location returns system name from galaxy lookup
  - Test: no system found returns "-"
- [x] Create `TestGetSectorText` class:
  - Test: fleet with location returns str(location)
  - Test: planet with location returns str(location)
  - Test: no location returns "-"
- [x] Create `TestGetTurnsLeftText` class:
  - Test: empty queue returns "-"
  - Test: queue with item returns "Nt" format
- [x] No pygame initialization needed - these are pure data tests

**Notes:** Created 23 unit tests covering all functions.

---

### Task 2.3: Update EmpireBuildQueueWindow to delegate to formatter [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
- [x] Add import: `from game.ui.screens.empire_build_queue_formatter import (get_queue_summary, get_first_item_text, get_capabilities_text, get_system_name, get_sector_text, get_turns_left_text)`
- [x] Replace `_get_queue_summary` static method body with delegation
- [x] Replace `_get_first_item_text` static method body with delegation
- [x] Replace `_get_capabilities_text` static method body with delegation
- [x] Replace `_get_system_name` method body with delegation
- [x] Replace `_get_sector_text` static method body with delegation
- [x] Replace `_get_turns_left_text` static method body with delegation
- [x] Run existing tests: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` - all must pass unchanged

**Notes:** 949 → 870 lines (-79 lines, 8% reduction). All 107 existing tests pass.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes (existing tests)
- [x] `pytest tests/unit/ui/screens/test_empire_build_queue_formatter.py` passes (new tests)
- [x] `pytest tests/ -n 12` full suite passes with no regressions
- [x] Update status at top of this file to Complete
- [x] Update plan.md phase table row to Complete
- [x] Update plan.md Current State to point to next phase
