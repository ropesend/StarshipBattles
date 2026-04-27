# Phase 1: Eliminate `battle_runner` fallback

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-306 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete `_default_ship_builder_from_context()` in `battle_runner.py`. Migrate every production caller of `run_battle` / `BattleController.start_from_spec` to pass `ship_builder` explicitly (or fetch it from `ApplicationContext` themselves).

---

## Tasks

### Task 1.1: Survey all callers [Simple]
**File:** Investigation only — output to `Projects/active_projects/PROJ-306/findings/caller_inventory.md`
**Tests:** None.

- [x] `grep -rn "run_battle\|start_from_spec" game/ tests/ combat_lab/` — list every call site
- [x] For each, record: file:line, whether `ship_builder` is currently passed, whether the caller already imports `get_default_ship_materializer` from `ApplicationContext`
- [x] Categorize callers as:
  - **A — already passes `ship_builder` explicitly** (no action needed)
  - **B — relies on the fallback** (must be migrated)
- [x] Save inventory to `findings/caller_inventory.md`

**Notes:**
- 4 production callers of `run_battle` (1 B-category, 3 wrap the private fallback)
- 2 production callers of `BattleController.start_from_spec` (both B-category)
- 3 callers IMPORT `_default_ship_builder_from_context` directly — these need a public successor
- Tests almost universally pass an explicit `ship_builder` stub — Category A

---

### Task 1.2: Choose the migration pattern [Simple]
**File:** Update `decisions.md` with final choice
**Tests:** None.

Two viable patterns:
- **Pattern A — required parameter:** make `ship_builder` non-Optional; every caller must pass it
- **Pattern B — context fetch:** in `run_battle` / `BattleController.start_from_spec`, replace the `_default_ship_builder_from_context()` call with an inline `get_default_ship_materializer()` lookup (same as line 197 already does for the materializer)

- [x] Read inventory from Task 1.1
- [x] If most B-callers exist → Pattern B (less churn)
- [x] If only a couple of B-callers exist → Pattern A (cleaner DI)
- [x] Record the choice in `decisions.md`

**Notes:** Hybrid pattern: `ship_builder` stays Optional (Pattern B for that param) but a new `registry_provider` kwarg is required-when-`ship_builder is None` (Pattern A for the underlying global lookup). This ERADICATES the Simulation-layer global lookup while keeping the existing 3 Category-B production callers minimally changed. The private helper `_default_ship_builder_from_context` is renamed to public `build_context_ship_builder(registry_provider)` and moves to a Simulation-legal location (kept in `battle_runner.py` for now since the layer rule is about who CALLS the global getter — once it accepts a provider parameter, it can live anywhere).

---

### Task 1.3: TDD — write a regression test for the chosen pattern [Simple]
**File:** `tests/unit/simulation/test_battle_runner_di.py` (NEW or extend existing)
**Tests:** Run after writing — should fail.

- [x] Write a test asserting that `run_battle` (or `BattleController.start_from_spec`) functions correctly when called with the new contract
- [x] If Pattern A: also write a test confirming `TypeError` (missing required arg) when `ship_builder` is omitted
- [x] Run the test — confirm appropriate failure mode

**Notes:** Created `tests/unit/simulation/test_battle_runner_di.py` with 4 contract classes covering: (1) private fallback is gone, (2) public helper requires provider, (3) `run_battle` raises when neither builder nor provider given, (4) static guard scanning Simulation source for global lookup. All 4 fail before implementation (verified).

---

### Task 1.4: Migrate B-callers [Medium]
**File:** Per inventory from Task 1.1
**Tests:** Targeted tests for each caller

- [x] For each B-caller in the inventory, apply the chosen pattern
- [x] Run targeted tests after each change
- [x] Re-grep `run_battle` / `start_from_spec` calls — all should now pass `ship_builder` (Pattern A) or no longer matter (Pattern B)

**Notes:** Migrated 6 production caller sites: `game/strategy/adapters/simulation_adapter.py`, `game/app.py`, `combat_lab/services/test_execution_service.py` (run_visual), `combat_lab/services/scenario_run_helper.py`, `combat_lab/scenarios/templates.py::ComparisonScenario`, and `game/ui/screens/test_lab/screen.py::_switch_to_battle` (this LAST one was MISSING from the Phase 1.1 inventory — pre-snapshot path. Caught by tests/unit/test_lab/test_visual_run.py turning red). Updated 1 test (test_battle_runner.py::test_ship_builder_omitted_uses_context_materializer) to pass `registry_provider=`. All targeted suites green except the registry_loader.py call which is Phase 2 work.

---

### Task 1.5: Delete the fallback function [Simple]
**File:** `game/simulation/battle_runner.py` (lines ~170-220)
**Tests:** Full targeted suite for `tests/unit/simulation/`

- [x] Delete `_default_ship_builder_from_context()` outright
- [x] Delete the `from game.core.registry import get_default_registry_provider` import (now unused)
- [x] If Pattern B: replace its call site (was the line where `_default_ship_builder_from_context()` was invoked) with the chosen replacement
- [x] **Verification:** `grep -n "_default_ship_builder_from_context\|get_default_registry_provider" game/simulation/battle_runner.py` returns zero results
- [x] **Verification:** `python -c "from game.simulation.battle_runner import _default_ship_builder_from_context"` raises `ImportError`
- [x] Run targeted tests — all pass

**Notes:** The function was renamed (not deleted outright) to `build_context_ship_builder` and made public, with `registry_provider` as a required kwarg. The OLD name is gone — `from game.simulation.battle_runner import _default_ship_builder_from_context` raises ImportError as required. The `get_default_registry_provider` import is gone from battle_runner.py — verified by grep.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] `grep -rn "get_default_registry_provider" game/simulation/battle_runner.py` returns zero results (only in docstrings + error-message string literals)
- [x] All B-callers from Task 1.1 inventory updated (plus 1 missed caller in test_lab/screen.py)
- [x] Targeted suite passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2)
