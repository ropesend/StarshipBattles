# Phase 1: DesignSelectorWindow Image Helper [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-89 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract image loading utilities (`_load_portrait_thumbnail`, `_load_topdown_thumbnail`, `_get_visible_bounding_box`) from DesignSelectorWindow into a standalone `design_image_helper.py` module. These 168 lines of pure image handling have zero coupling to UI state.

**File:** `game/ui/screens/design_selector_window.py`
**New File:** `game/ui/screens/design_image_helper.py`
**Tests:** `pytest tests/integration/ui/test_design_selector.py tests/unit/ui/screens/test_design_image_helper.py`

---

## Tasks
### Task 1.1: Create design_image_helper.py with extracted functions [Simple]
**File:** `game/ui/screens/design_image_helper.py`
- [ ] Create new module with module docstring explaining purpose
- [ ] Move `_load_portrait_thumbnail(design, size=50)` as `load_portrait_thumbnail(design, size=50)` (drop leading underscore - now public API)
  - Function signature: `def load_portrait_thumbnail(design: DesignMetadata, size: int = 50) -> pygame.Surface`
  - Import `os`, `pygame`, `log_warning` from `game.core.logger`
  - TYPE_CHECKING import for `DesignMetadata`
  - Copy implementation verbatim from lines 421-483 of design_selector_window.py
- [ ] Move `_load_topdown_thumbnail(design, target_height=50)` as `load_topdown_thumbnail(design, target_height=50)`
  - Function signature: `def load_topdown_thumbnail(design: DesignMetadata, target_height: int = 50) -> Optional[pygame.Surface]`
  - Copy implementation from lines 485-560, replacing `self._get_visible_bounding_box` with `_get_visible_bounding_box`
- [ ] Move `_get_visible_bounding_box(surface)` as `_get_visible_bounding_box(surface)` (keep private - internal helper)
  - Function signature: `def _get_visible_bounding_box(surface: pygame.Surface) -> Optional[tuple]`
  - Copy implementation from lines 562-591
- [ ] Verify the module has no dependency on UIWindow, pygame_gui, or any UI state

**Notes:**

---

### Task 1.2: Write unit tests for design_image_helper.py [Simple]
**File:** `tests/unit/ui/screens/test_design_image_helper.py`
- [ ] Create test file with `TestLoadPortraitThumbnail` class:
  - Test: returns a pygame.Surface when no files exist (placeholder path)
  - Test: placeholder surface has correct dimensions (size x size)
  - Test: logs warning when file exists but load fails (mock os.path.exists=True, pygame.image.load raises)
  - Test: different vehicle types produce different placeholder colors
- [ ] Create `TestLoadTopdownThumbnail` class:
  - Test: returns None when no skin file found (mock os.path.exists=False)
  - Test: returns a Surface when skin file found (mock pygame.image.load)
  - Test: logs warning when file exists but load fails
- [ ] Create `TestGetVisibleBoundingBox` class:
  - Test: fully transparent surface returns None
  - Test: surface with visible pixels returns correct bounding box
  - Test: single visible pixel returns 1x1 bounding box
- [ ] All tests must initialize pygame display: `pygame.init(); pygame.display.set_mode((1, 1), pygame.NOFRAME)` in setup_method

**Notes:**

---

### Task 1.3: Update DesignSelectorWindow to delegate to helper [Simple]
**File:** `game/ui/screens/design_selector_window.py`
- [ ] Add import: `from game.ui.screens.design_image_helper import load_portrait_thumbnail, load_topdown_thumbnail`
- [ ] Replace `_load_portrait_thumbnail` method body with delegation:
  ```python
  def _load_portrait_thumbnail(self, design, size=50):
      return load_portrait_thumbnail(design, size)
  ```
- [ ] Replace `_load_topdown_thumbnail` method body with delegation:
  ```python
  def _load_topdown_thumbnail(self, design, target_height=50):
      return load_topdown_thumbnail(design, target_height)
  ```
- [ ] Remove `_get_visible_bounding_box` method entirely (no longer called from this class)
- [ ] Remove any imports that are no longer needed (e.g., `os` if only used by image methods)
- [ ] Verify `os` import: check if it is still used elsewhere in the file before removing
- [ ] Run existing tests: `pytest tests/integration/ui/test_design_selector.py` - all must pass unchanged

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/integration/ui/test_design_selector.py` passes (existing tests)
- [ ] `pytest tests/unit/ui/screens/test_design_image_helper.py` passes (new tests)
- [ ] `pytest tests/ -n 12` full suite passes with no regressions
- [ ] Update status at top of this file to Complete
- [ ] Update plan.md phase table row to Complete
- [ ] Update plan.md Current State to point to next phase
