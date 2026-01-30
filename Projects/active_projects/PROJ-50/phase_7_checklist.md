# Phase 7: Big Bang Removal

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove global state functions from registry.py

---

## Tasks

### Task 7.1: Remove Provider Functions [Medium]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/ -n 4`

- [ ] Remove `_default_provider` global variable (line 514)
- [ ] Remove `get_default_registry_provider()` function (lines 517-531)
- [ ] Remove `DefaultRegistryProvider` class (lines 440-464) if no remaining usages
- [ ] Update `__all__` exports in `game/core/__init__.py`
- [ ] Verify no imports remain: `grep -r "get_default_registry_provider" game/`

**Notes:**

---

### Task 7.2: Decide on get_default_registries() [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/ -n 4`

- [ ] Option A: Keep `get_default_registries()` for app.py composition root only
- [ ] Option B: Remove entirely, have app.py use different pattern
- [ ] Document decision in decisions.md
- [ ] If keeping, mark as internal (prefix with underscore or document)

**Notes:**

---

### Task 7.3: Update App Entry Point [Simple]
**File:** `game/app.py`
**Tests:** Manual - launch game

- [ ] Verify app.py still initializes registries correctly
- [ ] Pass registries explicitly to all scene constructors
- [ ] Remove any remaining global state dependencies

**Notes:**

---

### Task 7.4: Final grep Verification [Simple]
**Tests:** `grep -r "get_default_registry_provider" game/`

- [ ] Verify only registry.py definition remains (if keeping)
- [ ] Verify `grep -r "_get_registries_fallback" game/` returns 0 results
- [ ] Document any intentional remaining usages in decisions.md

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ -n 4` - full suite passes
- [ ] Run `grep -r "get_default_registry_provider" game/` - only registry.py or 0
- [ ] Run `grep -r "_get_registries_fallback" game/` - returns 0
- [ ] Manual test: Game launches and runs
- [ ] Manual test: Workshop creates ship successfully
- [ ] Manual test: Battle simulation completes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md to mark project complete
