# Phase 6: Full Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-181 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Complete eradication verification - grep for deprecated patterns, full test suite, simulation tests.

---

## Tasks

### Task 6.1: Grep verification [Simple]

- [ ] `grep -r "get_default_registries" game/` returns ZERO hits
- [ ] `grep -r "set_default_registries" game/` returns ZERO hits
- [ ] `grep -r "get_default_registries" tests/` returns ZERO hits (outside comments)
- [ ] `grep -r "set_default_registries" tests/` returns ZERO hits (outside comments)
- [ ] `grep -r "get_default_registries" simulation_tests/` returns ZERO hits
- [ ] `grep -r "set_default_registries" simulation_tests/` returns ZERO hits
- [ ] `grep -r "game.core.registries" game/` returns ZERO hits
- [ ] `grep -r "_default_registries" game/core/registry.py` returns ZERO hits

### Task 6.2: Full test suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] All tests pass (baseline: 12,338 passed, 1 skipped)
- [ ] No new DeprecationWarnings related to registry access

### Task 6.3: Simulation tests [Simple]
**Tests:** `pytest simulation_tests/`

- [ ] All simulation tests pass

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "AUDIT READY"
