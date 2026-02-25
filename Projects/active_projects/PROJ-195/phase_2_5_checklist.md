# Phase 2.5: Ship Internal Singleton Investigation & Fix [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 2.5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Investigate and fix any Ship/Component internal methods that read from the global singleton, then fix all tests broken by Phase 2 removals

---

## Tasks

### Task 2.5.1: Investigate Ship internal singleton access [Medium]
**Files:** `game/simulation/entities/ship.py`, `game/simulation/components/component.py`
**Tests:** N/A — investigation only

- [ ] Search `game/simulation/entities/ship.py` for any `RegistryManager.instance()` or `get_default_registry_provider()` calls
- [ ] Search `game/simulation/components/component.py` for same
- [ ] Search `game/simulation/services/` for any service that Ship calls internally
- [ ] Document all internal singleton access points found
- [ ] For each access point, determine: does the code have a `registries=` parameter it could use instead?

**Notes:** If internal methods read from the singleton, we need to fix them to use the `registries` that was passed to the Ship constructor.

### Task 2.5.2: Fix internal singleton access in production code [Medium]
**Files:** As identified in Task 2.5.1
**Tests:** `pytest tests/ --testmon`

- [ ] For each internal access point found, refactor to use the `registries` attribute stored on the Ship/Component instance
- [ ] Ensure no new singleton leaks are introduced
- [ ] Run tests after each fix

**Notes:** This may be empty if no internal access is found. The autouse `reset_game_state` fixture hydrates the singleton, so internal singleton reads may have been silently working.

### Task 2.5.3: Fix all broken tests from Phase 2 [Medium]
**Tests:** `pytest tests/unit/entities/ tests/unit/ui/services/ tests/unit/builder/test_builder_ui_sync.py -v`

- [ ] Run the full test suite for Phase 2 files
- [ ] For each failure, diagnose root cause (internal singleton access vs missing DI parameter vs other)
- [ ] Fix each failure — prefer fixing the production code to propagate `registries` rather than re-adding singleton hydration
- [ ] All Phase 2 tests green

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/unit/entities/ tests/unit/ui/services/ tests/unit/builder/test_builder_ui_sync.py` passes
- [ ] All internal singleton access points documented or fixed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
