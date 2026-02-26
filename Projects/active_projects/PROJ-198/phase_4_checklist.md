# Phase 4: Bug Fixes & Dead Code Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-198 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix 4 discovered bugs/dead code paths that were masked by duck typing.

---

## Tasks

### Task 4.1: Fix strategy_detail_formatter.py — turn_engine Path [Medium]
**File:** `game/ui/screens/strategy_detail_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

**Bug:** L346 `hasattr(self.scene, 'turn_engine')` always returns False. `turn_engine` is on `self.scene.session`, not on `StrategyScreen`. The colonize button validation block never executes.

- [ ] Investigate what the code inside the block does (colonize validation logic)
- [ ] Fix attribute path to `self.scene.session.turn_engine` (or via facade)
- [ ] Or remove block entirely if validation is unnecessary
- [ ] Add a test verifying the corrected behavior
- [ ] Verify: tests pass

**Notes:**

### Task 4.2: Fix strategy_input_handler.py — planet_list_window Path [Medium]
**File:** `game/ui/screens/strategy_input_handler.py`
**Tests:** `pytest tests/unit/ui/screens/ -k strategy --testmon`

**Bug:** L61 `hasattr(self.scene.ui, 'planet_list_window')` always returns False. `planet_list_window` lives on `StrategyWindowManager`, not `StrategyUI`. The early-return branch never triggers.

- [ ] Investigate intended behavior (route events to planet list when open?)
- [ ] Fix path to `self.scene.ui.window_manager.planet_list_window`
- [ ] Or use `self.scene.ui._has_modal_open()` if intent is just "modal is open"
- [ ] Add a test verifying the corrected behavior
- [ ] Verify: tests pass

**Notes:**

### Task 4.3: Fix planet_list_filters.py — empires Lookup [Medium]
**File:** `game/ui/screens/planet_list_filters.py`
**Tests:** `pytest tests/unit/ui/screens/ -k planet --testmon`

**Bug:** L260 `hasattr(galaxy, 'empires')` always returns False. Galaxy has no `empires` attribute. The owner name lookup block is dead code.

- [ ] Change `get_owner_name(planet, galaxy, empire)` signature to `get_owner_name(planet, empires, current_empire)`
- [ ] Update caller in `planet_list_window.py` L83 to pass `session.empires`
- [ ] Remove the dead `hasattr(galaxy, 'empires')` guard
- [ ] Also remove `_temp_system_ref` monkey-patch (L27) — replace with a dict parameter
- [ ] Update `get_system_name()` to accept system name from dict instead of `planet._temp_system_ref`
- [ ] Update `gather_planets()` to return `(planets, system_name_map)` instead of monkey-patching
- [ ] Update all callers of gather_planets/get_system_name
- [ ] Add/update tests for owner name resolution
- [ ] Verify: tests pass

**Notes:**

### Task 4.4: Fix empire_build_queue_formatter.py — Dead Code [Medium]
**File:** `game/ui/screens/empire_build_queue_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/ -k empire --testmon`

**Dead code:**
- L79: `getattr(entity, 'system_name', None)` always returns None for Planet
- L112: `getattr(entity, 'global_hex', None)` always returns None for Planet

- [ ] L79: Remove dead `system_name` lookup block
- [ ] L112: Determine if global hex is needed
  - If yes: use `galaxy.get_planet_global_hex(entity.id)` or equivalent
  - If no: simplify to `entity.location`
- [ ] Add tests for correct system name and sector resolution
- [ ] Verify: tests pass

**Notes:**

### Task 4.5: Run full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All tests pass
- [ ] New tests added for fixed bugs

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
