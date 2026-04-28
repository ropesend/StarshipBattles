# Phase 1: Foundation (Base Class + Manager Methods)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-313 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the `StrategyModalWindow` base class and the new `StrategyWindowManager` API (`register_modal`, `unregister_modal`, `iter_live_modals`). No behaviour change in this phase — the modal list starts empty, the router is unchanged. Establish unit-test coverage for the base class invariants.

---

## Tasks

### Task 1.1: Create `StrategyModalWindow` base class [Simple]
**File:** `game/ui/screens/strategy_modal_window.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_modal_window.py` (NEW test file, see Task 1.3)

- [ ] Create new file with module docstring describing the structural contract
- [ ] Import `pygame_gui.elements.UIWindow` (the same import used by existing windows — verify via grep on existing modal subclasses)
- [ ] Define `class StrategyModalWindow(UIWindow):` with:
  - [ ] Class-level `_registered_subclasses: set[type] = set()`
  - [ ] `__init_subclass__(cls, **kwargs)` that calls `super().__init_subclass__(**kwargs)` and adds `cls` to `_registered_subclasses`
  - [ ] `__init__(self, *, window_manager: "StrategyWindowManager", **kwargs)` that calls `super().__init__(**kwargs)`, stores `window_manager`, and calls `window_manager.register_modal(self)`
  - [ ] `kill(self) -> None` that calls `unregister_modal` in `try/finally` before `super().kill()`
- [ ] Use forward reference `"StrategyWindowManager"` in the type hint to avoid circular import
- [ ] Add return-type annotations (`-> None`) per docs/03_CONVENTIONS.md §8
**Notes:** [Filled during implementation]

### Task 1.2: Add modal-list API to `StrategyWindowManager` [Simple]
**File:** `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_window_manager_public_api.py`

- [ ] Add `from typing import Iterator` if not present
- [ ] In `__init__`, add `self._modals: list[UIWindow] = []` near the existing slot fields (do NOT remove any slots yet — Phase 1 is additive)
- [ ] Add method `register_modal(self, w: UIWindow) -> None` that appends to `self._modals`
- [ ] Add method `unregister_modal(self, w: UIWindow) -> None` that does `self._modals.remove(w)` inside `try/except ValueError: pass` (idempotent)
- [ ] Add method `iter_live_modals(self) -> Iterator[UIWindow]` that performs the GC walk: `self._modals = [w for w in self._modals if w.alive()]; yield from self._modals`
- [ ] Add return-type annotations on all three new methods
**Notes:** [Filled during implementation]

### Task 1.3: Unit tests for the base class [Medium]
**File:** `tests/unit/ui/screens/test_strategy_modal_window.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_modal_window.py -v`

- [ ] Create test file with imports for pygame, pygame_gui, the new `StrategyModalWindow`, and `StrategyWindowManager`
- [ ] Test `test_subclass_registers_on_construction` — instantiate a stub subclass, assert it appears in `manager.iter_live_modals()` exactly once
- [ ] Test `test_kill_deregisters_synchronously` — instantiate, call `kill()`, assert it disappears from `iter_live_modals()`
- [ ] Test `test_kill_is_idempotent` — call `kill()` twice; second call must not raise
- [ ] Test `test_iter_live_modals_reaps_dead_refs` — instantiate, simulate parent-kill cascade by calling `super().kill()` directly without going through the override (manually set `.alive()` to return False), then iterate — assert dead ref is reaped within one walk
- [ ] Test `test_init_subclass_populates_registry` — define a new subclass mid-test, assert it's in `StrategyModalWindow._registered_subclasses`
- [ ] Test `test_multiple_managers_isolated` — create two managers, register one window in each, assert each manager sees only its own
**Notes:** Use a minimal stub subclass for tests — does not need the full pygame_gui rendering setup, just enough to instantiate. Reuse fixtures from existing modal tests if possible.

### Task 1.4: Verify baseline + new tests pass [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded suite — assert 15893 + N new tests passing where N is the number added in Task 1.3 (likely 6)
- [ ] No existing tests break (this phase is purely additive — new file + new methods, no changes to existing code paths)
**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2 (Router OR-bridge)
