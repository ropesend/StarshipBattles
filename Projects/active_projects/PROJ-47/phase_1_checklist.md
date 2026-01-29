# Phase 1: Critical UI Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-47 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Document the core UI builder components that lack docstrings

---

## Tasks

### Task 1.1: EventBus Documentation (DOC-01) [Simple]
**File:** `game/ui/screens/builder/event_bus.py`
**Tests:** `python -m py_compile game/ui/screens/builder/event_bus.py`

- [ ] Add class docstring (line 4) explaining pub/sub pattern, thread safety, event naming conventions
- [ ] Add `subscribe(event_type, callback)` docstring - document callback signature expectations
- [ ] Add `unsubscribe(event_type, callback)` docstring - note silent ignore for missing callbacks
- [ ] Add `emit(event_type, data=None)` docstring - document synchronous callback execution, error handling
- [ ] Verify: Run py_compile, check docstrings render in IDE

**Notes:**

---

### Task 1.2: InteractionController Documentation (DOC-02) [Medium]
**File:** `game/ui/screens/builder/interaction_controller.py`
**Tests:** `python -m py_compile game/ui/screens/builder/interaction_controller.py`

- [ ] Add class docstring (line 4) explaining drag-drop system, selection model, keyboard modifiers (Alt=clone, Shift=multi)
- [ ] Add `__init__` docstring documenting builder/view dependencies and initial state
- [ ] Add `register_drop_target(target)` docstring - document DropTarget interface contract
- [ ] Add `handle_event(event)` docstring - document MOUSEBUTTONDOWN/UP handling, modifier keys
- [ ] Add `update()` docstring - document hover detection purpose
- [ ] Verify: Run py_compile, check docstrings render in IDE

**Notes:**

---

### Task 1.3: ModifierControlRow Documentation (DOC-06) [Medium]
**File:** `game/ui/screens/builder/modifier_row.py`
**Tests:** `python -m py_compile game/ui/screens/builder/modifier_row.py`

- [ ] Expand class docstring (line 6) to document lifecycle: build_ui -> update -> handle_event -> kill
- [ ] Add `__init__` docstring documenting all parameters
- [ ] Add `_build_linear_controls()` docstring (line ~60) - document slider/button/preset layout
- [ ] Add `_clear_ui()` docstring - document cleanup pattern
- [ ] Verify: Run py_compile, check docstrings render in IDE

**Notes:**

---

### Task 1.4: ModifierLogic Class Docstring (DOC-08) [Simple]
**File:** `game/ui/screens/builder/modifier_logic.py`
**Tests:** `python -m py_compile game/ui/screens/builder/modifier_logic.py`

- [ ] Add class docstring (line 10) explaining static utility pattern, relationship with ModifierService
- [ ] Verify: Run py_compile, check docstrings render in IDE

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - affected tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
