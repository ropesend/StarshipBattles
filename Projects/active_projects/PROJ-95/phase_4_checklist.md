# Phase 4: Audit & Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-95 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Full test suite, verification greps, document results.

---

## Tasks

### Task 4.1: Run full test suite [Simple]
- [ ] `pytest tests/ -n 12` -- all tests pass
- [ ] Record test count (baseline: 7616)

---

### Task 4.2: Verification grep checks [Simple]
**Phase 1 checks (ResourceType constants):**
- [ ] Grep: No bare `'fuel'` string literals in `game/` (except ResourceType.FUEL definition line and docstring examples)
- [ ] Grep: No bare `'energy'` string literals in `game/` (except ResourceType.ENERGY definition line and docstring examples)
- [ ] Grep: No bare `'ammo'` string literals in `game/` (except ResourceType.AMMO definition line and docstring examples)

**Phase 2 checks (is_alive rename):**
- [ ] Grep: No `is_destroyed` in `game/`
- [ ] Grep: No `is_destroyed` in `tests/`

**Phase 3 checks (None-means-full elimination):**
- [ ] Grep: No `.get(resource_type, max` or `.get('fuel', max` patterns in `game/strategy/`
- [ ] Grep: No `del self._ship.resource_levels` in `game/strategy/`
- [ ] Grep: No `not in self._ship.resource_levels` in `game/strategy/`

---

### Task 4.3: Document results [Simple]
- [ ] Record final test count
- [ ] Document any findings or deviations
- [ ] Update plan.md Audit Log

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
