# Phase 2: EmpireBuildQueueWindow Formatter [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-89 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract data formatting methods from EmpireBuildQueueWindow into a standalone `empire_build_queue_formatter.py` module. These are pure data transforms (mostly `@staticmethod`) with no UI dependencies.

**File:** `game/ui/screens/empire_build_queue_window.py`
**New File:** `game/ui/screens/empire_build_queue_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py tests/unit/ui/screens/test_empire_build_queue_formatter.py`

---

## Tasks
### Task 2.1: Create empire_build_queue_formatter.py with extracted functions [Simple]
**File:** `game/ui/screens/empire_build_queue_formatter.py`
- [ ] Create new module with docstring explaining it provides data formatting for build queue display
- [ ] Add imports: `from typing import Any, Optional, TYPE_CHECKING`
- [ ] Add TYPE_CHECKING import for `BuildQueueSource`
- [ ] Extract `get_queue_summary(source)` as standalone function:
  - Signature: `def get_queue_summary(source: BuildQueueSource) -> str`
  - Copy implementation from lines 496-508 of empire_build_queue_window.py
- [ ] Extract `get_first_item_text(source)` as standalone function:
  - Signature: `def get_first_item_text(source: BuildQueueSource) -> str`
  - Copy implementation from lines 511-525
- [ ] Extract `get_capabilities_text(source)` as standalone function:
  - Signature: `def get_capabilities_text(source: BuildQueueSource) -> str`
  - Copy implementation from lines 528-543
- [ ] Extract `get_system_name(source, galaxy)` as standalone function:
  - Signature: `def get_system_name(source: BuildQueueSource, galaxy: Any) -> str`
  - Copy implementation from lines 870-895, replacing `self.galaxy` with `galaxy` parameter
- [ ] Extract `get_sector_text(source)` as standalone function:
  - Signature: `def get_sector_text(source: BuildQueueSource) -> str`
  - Copy implementation from lines 898-917
- [ ] Extract `get_turns_left_text(source)` as standalone function:
  - Signature: `def get_turns_left_text(source: BuildQueueSource) -> str`
  - Copy implementation from lines 920-933
- [ ] Verify the module has no dependency on pygame, pygame_gui, UIWindow, or any UI imports

**Notes:**

---

### Task 2.2: Write unit tests for empire_build_queue_formatter.py [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_formatter.py`
- [ ] Create helper `_make_source()` function (same pattern as existing test file)
- [ ] Create `TestGetQueueSummary` class:
  - Test: empty queue returns "-"
  - Test: single item returns "1 item" (no plural)
  - Test: multiple items returns "N items"
- [ ] Create `TestGetFirstItemText` class:
  - Test: empty queue returns "-"
  - Test: queue with item returns design_id and turns
- [ ] Create `TestGetCapabilitiesText` class:
  - Test: ships only returns "Ships"
  - Test: complexes only returns "Complexes"
  - Test: both returns "Ships & Complexes"
  - Test: neither returns "None"
- [ ] Create `TestGetSystemName` class:
  - Test: planet with system_name attribute returns it
  - Test: planet with galaxy lookup returns system name
  - Test: fleet with location returns system name from galaxy lookup
  - Test: no system found returns "-"
- [ ] Create `TestGetSectorText` class:
  - Test: fleet with location returns str(location)
  - Test: planet with location returns str(location)
  - Test: no location returns "-"
- [ ] Create `TestGetTurnsLeftText` class:
  - Test: empty queue returns "-"
  - Test: queue with item returns "Nt" format
- [ ] No pygame initialization needed - these are pure data tests

**Notes:**

---

### Task 2.3: Update EmpireBuildQueueWindow to delegate to formatter [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
- [ ] Add import: `from game.ui.screens.empire_build_queue_formatter import (get_queue_summary, get_first_item_text, get_capabilities_text, get_system_name, get_sector_text, get_turns_left_text)`
- [ ] Replace `_get_queue_summary` static method body with delegation:
  ```python
  @staticmethod
  def _get_queue_summary(source):
      return get_queue_summary(source)
  ```
- [ ] Replace `_get_first_item_text` static method body with delegation:
  ```python
  @staticmethod
  def _get_first_item_text(source):
      return get_first_item_text(source)
  ```
- [ ] Replace `_get_capabilities_text` static method body with delegation:
  ```python
  @staticmethod
  def _get_capabilities_text(source):
      return get_capabilities_text(source)
  ```
- [ ] Replace `_get_system_name` method body with delegation:
  ```python
  def _get_system_name(self, source):
      return get_system_name(source, self.galaxy)
  ```
- [ ] Replace `_get_sector_text` static method body with delegation:
  ```python
  @staticmethod
  def _get_sector_text(source):
      return get_sector_text(source)
  ```
- [ ] Replace `_get_turns_left_text` static method body with delegation:
  ```python
  @staticmethod
  def _get_turns_left_text(source):
      return get_turns_left_text(source)
  ```
- [ ] Run existing tests: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` - all must pass unchanged

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` passes (existing tests)
- [ ] `pytest tests/unit/ui/screens/test_empire_build_queue_formatter.py` passes (new tests)
- [ ] `pytest tests/ -n 12` full suite passes with no regressions
- [ ] Update status at top of this file to Complete
- [ ] Update plan.md phase table row to Complete
- [ ] Update plan.md Current State to point to next phase
