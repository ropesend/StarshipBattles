# Phase 2: Remove Legacy hasattr Checks

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-184 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove 3 unnecessary hasattr guards for methods that always exist on Galaxy

---

## Tasks

### Task 2.1: Remove hasattr in game_session.py [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/engine/ tests/integration/strategy/ -x`

- [ ] Remove `hasattr(self.galaxy, 'get_system_of_object')` guard (line 133-134) — delete both lines
- [ ] Verify: the `for empire in self.empires:` loop on line 135 is now the first line of the method body

**Notes:**

### Task 2.2: Simplify hasattr in empire_build_queue_window.py [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -x`

- [ ] Simplify line 348 from `if self.galaxy and hasattr(self.galaxy, 'get_system_of_planet'):` to `if self.galaxy:`

**Notes:**

### Task 2.3: Simplify hasattr in empire_build_queue_formatter.py [Simple]
**File:** `game/ui/screens/empire_build_queue_formatter.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_formatter.py -x`

- [ ] Simplify line 83 from `if galaxy and hasattr(galaxy, 'get_system_of_planet'):` to `if galaxy:`

**Notes:**

### Task 2.4: Run full test suite [Simple]

- [ ] Run `pytest tests/ -n 12` — 12,366+ passed, 0 failed

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
