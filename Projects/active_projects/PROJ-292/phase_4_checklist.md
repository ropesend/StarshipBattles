# Phase 4: H3 — Narrow `except (AttributeError, Exception)` in `_build_projection_grid`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-292 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Stop the catch-all exception handler in `_build_projection_grid`'s net-cell colour code from swallowing programming errors. Narrow to `except AttributeError` only — the original intent (handle pygame_gui version variance on `text_colour` setter) survives; real bugs propagate.

---

## Tasks

### Task 4.1: Locate the catch-all [Simple]
**File:** [game/ui/panels/planet_report_panel.py](game/ui/panels/planet_report_panel.py)
**Tests:** None (read-only)

- [ ] Open the file. Search for `text_colour`. Find the try/except block in `_build_projection_grid` (likely around line 450-460):
  ```python
  try:
      cell.text_colour = color
      cell.rebuild()
  except (AttributeError, Exception):
      pass
  ```
- [ ] Document the file:line in your task notes.

**Notes:**

### Task 4.2: Write a failing test that proves the swallow [Medium]
**File:** [tests/unit/ui/panels/test_planet_report_panel.py](tests/unit/ui/panels/test_planet_report_panel.py)
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py::TestNetCellColorExceptionHandling -v`

- [ ] Add a new test class `TestNetCellColorExceptionHandling`.
- [ ] Test 1: `test_attribute_error_silently_swallowed`. Use the bypass-init pattern. Mock a `cell` whose `text_colour` setter raises `AttributeError`. Call `_build_projection_grid` with a single-row view. Assert NO exception propagates (current behaviour preserved).
- [ ] Test 2: `test_runtime_error_propagates`. Mock a `cell` whose `text_colour` setter raises `RuntimeError`. Call `_build_projection_grid`. Assert `RuntimeError` propagates (this is the bug being fixed; today's catch-all swallows it).
- [ ] Run the tests. Test 1 should pass; Test 2 FAILS (the catch-all swallows the RuntimeError).

**Notes:**

### Task 4.3: Apply the narrow [Simple]
**File:** [game/ui/panels/planet_report_panel.py](game/ui/panels/planet_report_panel.py)
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py -v`

- [ ] Change the catch:
  ```python
  # Before:
  except (AttributeError, Exception):
      pass
  # After:
  except AttributeError:
      # PROJ-292 H3: pygame_gui versions vary on text_colour setter support;
      # accept silent fallback only for AttributeError. Other exceptions
      # propagate so real bugs surface.
      pass
  ```
- [ ] Run Task 4.2's tests. Test 2 now passes (RuntimeError propagates).
- [ ] Run the full file — existing tests still pass.

**Notes:**

### Task 4.4: Targeted regression suite [Simple]
**Tests:** `pytest tests/unit/ui/panels/ -q`

- [ ] Panel suite green.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
