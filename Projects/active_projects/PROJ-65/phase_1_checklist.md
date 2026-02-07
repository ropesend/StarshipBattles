# Phase 1: Foundation — IScene Protocol & WIDTH/HEIGHT

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-65 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Define the IScene protocol, eliminate global WIDTH/HEIGHT, move module-level side effects into proper locations.

---

## Tasks

### Task 1.1: Define IScene Protocol [Simple]
**File:** `game/core/protocols.py`
**Tests:** `pytest tests/unit/ -k "protocol" --tb=short`

- [ ] Add IScene protocol after Combat Entity Protocols section (after line 282):
  ```python
  @runtime_checkable
  class IScene(Protocol):
      """Protocol for game scenes (PROJ-65)."""
      def handle_event(self, event: Any) -> None: ...
      def update(self, dt: float) -> None: ...
      def draw(self, screen: Any) -> None: ...
      def handle_resize(self, width: int, height: int) -> None: ...
  ```
- [ ] Add `is_scene` TypeGuard function
- [ ] Add `IScene` and `is_scene` to module docstring imports example

**Notes:**

### Task 1.2: Eliminate Global WIDTH/HEIGHT [Medium]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/test_app_integration.py tests/unit/systems/test_main_integration.py --tb=short`

- [ ] Remove module-level `WIDTH, HEIGHT = DEFAULT_WIDTH, DEFAULT_HEIGHT` (line 43)
- [ ] Add `self.width` and `self.height` instance attributes in `__init__` (replace `global WIDTH, HEIGHT` at line 70)
- [ ] Replace all `WIDTH` references in `__init__` with `self.width` (lines 72-89, 127-134)
- [ ] Replace `global WIDTH, HEIGHT` in `_handle_resize` (line 558) with `self.width, self.height = w, h`
- [ ] Replace all `WIDTH`/`HEIGHT` references in remaining methods with `self.width`/`self.height` (~37 occurrences)
- [ ] Keep `DEFAULT_WIDTH, DEFAULT_HEIGHT` constants (used for initial value only)
- [ ] Verify: `grep "global WIDTH\|global HEIGHT" game/app.py` returns nothing

**Notes:**

### Task 1.3: Move Module-Level Side Effects [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/test_app_integration.py --tb=short`

- [ ] Move `argparse` parsing (lines 13-16) into `main()` function; pass `args` to `Game.__init__`
- [ ] Move `pygame.font.init()` and font creation (lines 53-56) into `Game.__init__`; store as `self.font_small`, `self.font_med`, `self.font_large`
- [ ] Update `draw_battle_hud` call (line 734) to pass `self.font_med` instead of module-level `font_med`
- [ ] Update `draw_exit_dialog` call (line 696) to pass `self.font_large, self.font_med`
- [ ] Verify: no module-level function calls in app.py (only imports, constants, class/function defs)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Tests pass: `pytest tests/unit/test_app_integration.py tests/unit/systems/test_main_integration.py`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
