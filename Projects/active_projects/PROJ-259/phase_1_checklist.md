# Phase 1: Screen State Machine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-259 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create a generic `ScreenStateMachine` class in `game/core/state_machine.py`, write comprehensive tests, then refactor `game/app.py` to use it -- replacing all 23 `_switch_scene()` calls and the three ad-hoc return-state fields.

---

## Tasks

### Task 1.1: Write Tests for ScreenStateMachine [Medium]
**File:** `tests/unit/core/test_state_machine.py` (NEW)
**Tests:** `pytest tests/unit/core/test_state_machine.py`

- [ ] Create test file `tests/unit/core/test_state_machine.py`
- [ ] Test: initial state is set correctly
- [ ] Test: `transition()` to allowed state succeeds and updates `.state`
- [ ] Test: `transition()` to disallowed state raises `StateException`
- [ ] Test: `can_transition()` returns True for allowed, False for disallowed
- [ ] Test: `transition()` with passing guard succeeds
- [ ] Test: `transition()` with failing guard raises `StateException`
- [ ] Test: `on_exit` callback fires when leaving a state
- [ ] Test: `on_enter` callback fires when entering a state
- [ ] Test: `on_exit` fires before `on_enter` during transition
- [ ] Test: `push_and_transition()` pushes current state onto stack
- [ ] Test: `pop_and_return()` returns to previously pushed state
- [ ] Test: `pop_and_return()` on empty stack raises `StateException`
- [ ] Test: multiple push/pop cycles work correctly (LIFO order)
- [ ] Test: push_and_transition validates transition is allowed
- [ ] Test: pop_and_return validates return transition is allowed
- [ ] Test: works with IntEnum (GameState) as state type
- [ ] Run tests -- confirm all fail (no implementation yet)

**Notes:** Use `GameState` enum from `game/core/constants.py` in tests for realistic type checking. Use `StateException` from `game/core/exceptions.py`.

---

### Task 1.2: Implement ScreenStateMachine [Medium]
**File:** `game/core/state_machine.py` (NEW)
**Tests:** `pytest tests/unit/core/test_state_machine.py`

- [ ] Create `game/core/state_machine.py`
- [ ] Implement `ScreenStateMachine.__init__()` accepting initial_state, transitions, guards, on_enter, on_exit
- [ ] Implement `state` property
- [ ] Implement `transition(to_state)` with transition table check, guard check, on_exit/on_enter hooks
- [ ] Implement `can_transition(to_state)` -- pure check, no side effects
- [ ] Implement `push_and_transition(to_state)` -- push current to stack, then transition
- [ ] Implement `pop_and_return()` -- pop from stack, transition to popped state
- [ ] Raise `StateException` (from `game/core/exceptions.py`) on illegal transitions and empty stack
- [ ] Add type hints and docstrings
- [ ] Run tests -- confirm all pass
- [ ] Add `ScreenStateMachine` to `game/core/__init__.py` exports

**Notes:** Keep the class generic (no Pygame, no IScene). It only knows about states and transitions.

---

### Task 1.3: Define Transition Table for app.py [Simple]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/core/test_state_machine.py`

- [ ] Define `_SCREEN_TRANSITIONS: frozenset` constant in `game/app.py` (or a module-level variable) containing all 24 valid (from_state, to_state) tuples from the transition map in design.md
- [ ] Write a test that verifies the transition table contains exactly the expected transitions (no extras, no missing)
- [ ] Verify transition count matches the 24 documented transitions

**Notes:** The transition table is the source of truth. All transitions in the current code must be represented.

---

### Task 1.4: Refactor app.py to Use State Machine [Complex]
**File:** `game/app.py` (lines 71-773)
**Tests:** `pytest tests/unit/core/test_state_machine.py` + full suite

- [ ] In `Game.__init__()`: create `self.state_machine = ScreenStateMachine(initial_state=GameState.MENU, transitions=_SCREEN_TRANSITIONS)`
- [ ] Replace `self.state` property to delegate to `self.state_machine.state`
- [ ] Replace `_switch_scene()` method with a new method that calls `self.state_machine.transition(state)` then sets `self.active_scene = scene`
- [ ] Refactor `start_builder()` (line 194): use `push_and_transition(BUILDER)` instead of storing `self.builder_return_state`
- [ ] Refactor `on_builder_return()` (line 211): use `pop_and_return()` instead of checking `self.builder_return_state`
- [ ] Refactor `start_keybindings()` (line 452): use `push_and_transition(KEYBINDINGS)` instead of storing `self._keybindings_return_state`
- [ ] Refactor `on_keybindings_return()` (line 465): use `pop_and_return()` instead of checking `self._keybindings_return_state`
- [ ] Refactor battle return routing: push source state (BATTLE_SETUP or TEST_LAB) before entering BATTLE, use `pop_and_return()` in `_return_to()`
- [ ] Remove `self.builder_return_state` field
- [ ] Remove `self._keybindings_return_state` field
- [ ] Remove `self.return_state` field (line 111)
- [ ] Remove `_switch_scene()` method (line 188-191)
- [ ] Verify `self.state` reads from state machine everywhere (search for `self.state ==` and `self.state !=`)
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py`

**Notes:** This is the largest task. Work methodically through each `_switch_scene()` call site. The state machine enforces that only declared transitions happen -- any missed transition will fail loudly at runtime.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All tests pass: `pytest tests/unit/core/test_state_machine.py`
- [ ] Full suite passes: `python Tools/test_sharded/test_sharded.py`
- [ ] `_switch_scene()` method no longer exists in app.py
- [ ] `self.builder_return_state`, `self._keybindings_return_state`, `self.return_state` removed from app.py
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
