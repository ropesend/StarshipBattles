# Phase 2: Eliminate `registry_loader` fallback

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-306 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate the `get_default_registry_provider()` call at `game/simulation/services/registry_loader.py:91`. The line-90 comment already aspires to this state ("PROJ-211: Pass registry_provider explicitly (no fallback)") — make the comment factually true.

**Prerequisites:** Phase 1 complete.

---

## Tasks

### Task 2.1: Survey callers of `registry_loader` [Simple]
**File:** Investigation only — output to `findings/registry_loader_callers.md`
**Tests:** None.

- [ ] Read [game/simulation/services/registry_loader.py](game/simulation/services/registry_loader.py) fully — identify the public function(s) that contain line 91 (likely `load_all_registries` or similar)
- [ ] `grep -rn "from game.simulation.services.registry_loader\|registry_loader\." game/ tests/ combat_lab/` — list every caller
- [ ] For each caller, record whether `registry_provider` is currently passed or not
- [ ] Save to `findings/registry_loader_callers.md`

**Notes:**

---

### Task 2.2: TDD — write the contract test [Simple]
**File:** `tests/unit/simulation/services/test_registry_loader.py` (NEW or extend existing)
**Tests:** Should fail before Task 2.3.

- [ ] Write a test asserting the loader function refuses to run without an explicit `registry_provider` argument (or, if context-fetch pattern chosen, that it correctly fetches from a mocked context)
- [ ] Run — confirm failure

**Notes:**

---

### Task 2.3: Migrate callers + remove fallback [Medium]
**File:** `game/simulation/services/registry_loader.py` and every caller
**Tests:** Targeted suite

- [ ] Make `registry_provider` a required parameter (or fetch from `ApplicationContext` per the choice locked in Phase 1 Task 1.2 — be consistent across both sites)
- [ ] Delete the line-91 `provider = get_default_registry_provider()` call (replace with the parameter use)
- [ ] Update every caller from Task 2.1 inventory to pass `registry_provider` explicitly
- [ ] **Verification:** `grep -n "get_default_registry_provider" game/simulation/services/registry_loader.py` returns zero results
- [ ] Keep the comment at line 90 — it's now factually accurate
- [ ] Run targeted tests

**Notes:**

---

### Task 2.4: Sweep for any remaining Simulation-layer global lookups [Simple]
**File:** All of `game/simulation/`
**Tests:** None.

- [ ] Final sweep: `grep -rn "get_default_registry_provider" game/simulation/` — should be ZERO
- [ ] Final sweep: `grep -rn "from game.core.registry import.*get_default_registry_provider" game/simulation/` — should be ZERO
- [ ] If any hits remain, file a Notes entry below describing them and decide rename vs keep

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `grep -rn "get_default_registry_provider" game/simulation/` returns ZERO results
- [ ] Targeted suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3)
