# Phase 3: DI & Service-Locator Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-212 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace service-locator anti-patterns with constructor dependency injection; audit remaining deferred registry imports
**Priority:** Medium
**Effort:** Medium

---

## Tasks

### Task 3.1: RS-007 — Replace service-locator in fleet_capability_calculator.py [Medium]
**File:** `game/strategy/data/fleet_capability_calculator.py`
**Finding:** Uses module-level `_get_default_component_registry()` helper that calls `get_default_registry_provider().get_components()`. This is a service-locator anti-pattern — the calculator should receive the registry via constructor injection.
**Tests:** `pytest tests/unit/strategy/data/ -x`

- [ ] Read file, understand current service-locator usage
- [ ] Add `component_registry` parameter to constructor (with default=None for DI fallback)
- [ ] Update all callers to pass the registry if available
- [ ] Remove the `_get_default_component_registry()` helper function
- [ ] Run tests, verify no regressions

**Notes:** [Filled during implementation]

### Task 3.2: IIA-005 — Audit deferred registry imports [Medium]
**Finding:** `game.core.registry` (specifically `get_default_registry_provider` and `GameRegistries`) is deferred in ~12 files across all layers. Many of these may be unnecessary after the OrderType extraction (Phase 2) reduced transitive import chains.
**Tests:** `pytest tests/ -n 12`

- [ ] Grep for all deferred imports of `game.core.registry` across the codebase
- [ ] For each occurrence, determine if the deferral is still necessary:
  - Is there an actual circular dependency?
  - Is this a DI fallback pattern (intentional)?
  - Could it safely be promoted to top-level?
- [ ] Promote to top-level where safe
- [ ] Document any that must remain deferred (with inline comment explaining why)
- [ ] Run full test suite, verify no regressions

**Notes:** This is an audit task — not all deferred registry imports are wrong. Some are intentional DI fallback patterns (e.g., `if registry is None: from game.core.registry import ...`). Only promote the ones that are clearly unnecessary.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "All phases complete"
