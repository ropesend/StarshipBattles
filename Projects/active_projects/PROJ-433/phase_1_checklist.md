# Phase 1: Split `component_inspector.py` into `component_abilities.py` + `component_layers.py`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-433 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_0
**Review Mode:** standard
**Files (planned):**
- `game/strategy/services/component_inspector.py` (rewrite — re-export shim, or delete if Option B)
- `game/strategy/services/component_abilities.py` (new)
- `game/strategy/services/component_layers.py` (new)
- Caller files in `game/` and `tests/` discovered by Phase 0 grep (if Option B)

**Objective:** Mechanically move Surface A (ability iteration + `has_warp_capability`) into `component_abilities.py` and Surface B (layer-view helpers added by PROJ-425 Phase 2) into `component_layers.py`. Preserve all function signatures and behavior. Apply the Option A or Option B contract locked in Phase 0.

---

## Tasks

### Task 1.1: Create `component_abilities.py` [Standard]
**File:** `game/strategy/services/component_abilities.py`

- [ ] Create the new module with the Surface A function bodies (verbatim from `component_inspector.py:38-401`) plus `has_warp_capability` from line 504.
- [ ] Include the private `_get_component_registry` helper since it is consumed by `extract_abilities_from_component`.
- [ ] Add a module docstring noting "PROJ-433: split from `component_inspector.py` (which exceeded 500 LOC after PROJ-425 Phase 2)".
- [ ] Add `__all__` listing every public name moved into this module.
- [ ] Add the `TYPE_CHECKING`-guarded `ShipInstance` import if any function signature references it.
- [ ] Verify the new module is materially under 500 LOC (expected ~440-450).

### Task 1.2: Create `component_layers.py` [Standard]
**File:** `game/strategy/services/component_layers.py`

- [ ] Create the new module with the Surface B function bodies (verbatim from `component_inspector.py:404-501`).
- [ ] Place `lookup_design_max_hp` per Phase 0's grep result (in `component_layers.py` if it has no non-layer consumer, otherwise in `component_abilities.py` with a `TYPE_CHECKING` import from there if needed).
- [ ] Add a module docstring noting the PROJ-425 Phase 2 origin of the helpers.
- [ ] Add `__all__` listing every public name moved into this module.
- [ ] Add the `TYPE_CHECKING`-guarded `ShipInstance` import (Surface B definitely needs it — signatures take a `ShipInstance`).
- [ ] Verify the new module is materially under 500 LOC (expected ~140-160).

### Task 1.3: Apply the Option A or Option B contract [Standard]
**File:** `game/strategy/services/component_inspector.py` + caller files

- [ ] **Option A (re-export shim):** Replace `component_inspector.py`'s body with one-line-per-name re-exports from `component_abilities` and `component_layers`. Keep `__all__` identical to today. Module shrinks to ~25 LOC.
- [ ] **Option B (caller migration):** Delete `component_inspector.py`. Migrate each import site identified in Phase 0 from `from game.strategy.services.component_inspector import X` to either `from game.strategy.services.component_abilities import X` or `from game.strategy.services.component_layers import X` based on which module owns `X`.
- [ ] Either way: `__all__` snapshot test (Phase 0 Task 0.1) must still pass.

### Task 1.4: Update entity delegate call site [Simple, Option B only]
**File:** `game/strategy/data/ship_instance.py`

- [ ] If Option B is chosen, the entity's three Surface B delegate methods (`get_damaged_component_count`, `iter_all_components_by_layer`, `get_damaged_components_by_layer`) need their `from game.strategy.services.component_inspector import ...` lines updated to import from `component_layers`.

### Task 1.5: Run focused suites [Simple]
**Tests:** `pytest tests/unit/strategy/services/test_component_inspector*.py tests/unit/strategy/ship_instance/ -q`

- [ ] Both suites green.
- [ ] `__all__` snapshot test green (no name drift).

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `component_abilities.py` exists and is under 500 LOC
- [ ] `component_layers.py` exists and is under 500 LOC
- [ ] `component_inspector.py` is either a thin re-export shim (~25 LOC) or deleted (Option B)
- [ ] No function signature changed
- [ ] Focused suites green
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
