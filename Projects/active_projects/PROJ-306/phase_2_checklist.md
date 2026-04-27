# Phase 2: Eliminate `registry_loader` fallback

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-306 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Eliminate the `get_default_registry_provider()` call at `game/simulation/services/registry_loader.py:91`. The line-90 comment already aspires to this state ("PROJ-211: Pass registry_provider explicitly (no fallback)") — make the comment factually true.

**Prerequisites:** Phase 1 complete.

---

## Tasks

### Task 2.1: Survey callers of `registry_loader` [Simple]
**File:** Investigation only — output to `findings/registry_loader_callers.md`
**Tests:** None.

- [x] Read [game/simulation/services/registry_loader.py](game/simulation/services/registry_loader.py) fully — identify the public function(s) that contain line 91 (likely `load_all_registries` or similar)
- [x] `grep -rn "from game.simulation.services.registry_loader\|registry_loader\." game/ tests/ combat_lab/` — list every caller
- [x] For each caller, record whether `registry_provider` is currently passed or not
- [x] Save to `findings/registry_loader_callers.md`

**Notes:** Function name is `reload_registries_from_directory`. **ZERO production callers** — only 23 test callers across 2 test files (`test_registry_manager_reload.py` + `test_registry_loader.py`).

---

### Task 2.2: TDD — write the contract test [Simple]
**File:** `tests/unit/simulation/services/test_registry_loader.py` (NEW or extend existing)
**Tests:** Should fail before Task 2.3.

- [x] Write a test asserting the loader function refuses to run without an explicit `registry_provider` argument (or, if context-fetch pattern chosen, that it correctly fetches from a mocked context)
- [x] Run — confirm failure

**Notes:** Added `TestRegistryProviderIsRequired` class to `tests/unit/simulation/services/test_registry_loader.py` with 2 tests: (1) omitting raises TypeError, (2) provider is threaded through to all 3 loaders. Both fail before implementation (verified).

---

### Task 2.3: Migrate callers + remove fallback [Medium]
**File:** `game/simulation/services/registry_loader.py` and every caller
**Tests:** Targeted suite

- [x] Make `registry_provider` a required parameter (or fetch from `ApplicationContext` per the choice locked in Phase 1 Task 1.2 — be consistent across both sites)
- [x] Delete the line-91 `provider = get_default_registry_provider()` call (replace with the parameter use)
- [x] Update every caller from Task 2.1 inventory to pass `registry_provider` explicitly
- [x] **Verification:** `grep -n "get_default_registry_provider" game/simulation/services/registry_loader.py` returns zero results
- [x] Keep the comment at line 90 — it's now factually accurate
- [x] Run targeted tests

**Notes:** Made `registry_provider` a keyword-only required argument. Removed the import + call. 23 test call sites updated via regex substitution (one followup fix for a `str(tmp_path)` → `str(tmp_path), registry_provider=...)` parenthesis-bumping issue caught immediately by tests). All 30 tests in the two files now pass.

---

### Task 2.4: Sweep for any remaining Simulation-layer global lookups [Simple]
**File:** All of `game/simulation/`
**Tests:** None.

- [x] Final sweep: `grep -rn "get_default_registry_provider" game/simulation/` — should be ZERO
- [x] Final sweep: `grep -rn "from game.core.registry import.*get_default_registry_provider" game/simulation/` — should be ZERO
- [x] If any hits remain, file a Notes entry below describing them and decide rename vs keep

**Notes:** Zero imports, zero calls. The 6 remaining text matches are all in docstrings or error-message string literals — they're explaining the pattern to future maintainers, not invoking it. The AST-based static guard in `tests/unit/simulation/test_battle_runner_di.py::TestSimulationLayerHasNoGlobalLookup` confirms this (passes).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] `grep -rn "get_default_registry_provider" game/simulation/` returns ZERO actual imports/calls (only docstring + string-literal mentions)
- [x] Targeted suite passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 3)
