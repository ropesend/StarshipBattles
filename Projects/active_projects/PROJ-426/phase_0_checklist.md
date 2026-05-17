# Phase 0: Preflight and baseline capture

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-426 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** none — preflight phase
**Review Mode:** lightweight
**Files (planned):** none (read-only baseline capture)

**Objective:** Freeze the current seam before moving code. Re-run the source plan's Executor Guardrail grep commands to confirm the side-channel touch list has not grown since verification. Confirm `simulation_adapter.py` is still the only production runtime caller. No code edited.

---

## Reading

- [ ] Read [Projects/active_projects/PROJ-426/plan.md](plan.md), [design.md](design.md), [decisions.md](decisions.md) end-to-end.
- [ ] Read [TD-01 source plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-01_battle_spec_compilation.md) — canonical specification.
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md` (foundation docs per AGENTS.md).
- [ ] Read `game/strategy/combat/spec_compiler.py` end-to-end (959 LOC). Pay attention to lines 78-280 (`build_strategy_battle_spec`), lines 271-279 (the four `object.__setattr__` writes), lines 430-451 (`_split_mine_groups_from_fleets`), lines 454-491 (`build_fighter_reboard_setup`), lines 494-549 (`build_mine_resolver_setup`).
- [ ] Read `game/strategy/adapters/simulation_adapter.py:309-346` (the side-channel readers + pre-tick callback composer).
- [ ] Read `game/simulation/battle_spec.py` (the frozen DTO; confirm it is NOT being modified by this project).

---

## Tasks

### Task 0.1: Re-run side-channel grep baseline [Simple]
**File:** N/A (read-only)
**Tests:** N/A

- [x] Run the first guardrail grep:
  ```bash
  rg -n "build_strategy_battle_spec|object\.__setattr__\(spec|_mine_groups|_owner_to_team_id|_combat_fleets|_engine_ref" game tests
  ```
- [x] Run the second guardrail grep:
  ```bash
  rg -n "from game\.strategy\.combat\.spec_compiler import build_strategy_battle_spec|build_strategy_battle_spec\(" game tests docs
  ```
- [x] Record the counts of `object.__setattr__(spec, ...)` writes in `spec_compiler.py`. Confirmed exactly **4** at lines 271-279.
- [x] Capture the result in `.agent_reports/proj-phase-session/PROJ-426/phase_0/baseline.md`.

**Notes:**

### Task 0.2: Confirm sole production runtime caller [Simple]
**File:** N/A (read-only)
**Tests:** N/A

- [x] Confirm `game/strategy/adapters/simulation_adapter.py` is still the only production runtime caller of `build_strategy_battle_spec(...)`.
- [x] Confirm `game/strategy/engine/conflict_resolution_engine.py` mentions the compiler **in comments only** (no runtime call).
- [x] No new runtime caller appeared.

**Notes:**

### Task 0.3: Inventory tests that pin private side-channels [Simple]
**File:** N/A (read-only)
**Tests:** N/A

- [x] Recorded `:414, 415, 420, 493` in `tests/integration/test_fms_b_e2e.py` (current state matches verification).
- [x] Confirmed both `*_combat_join.py` tests still import `_split_mine_groups_from_fleets`.
- [x] `tests/unit/strategy/adapters/test_simulation_adapter.py` does NOT directly read side-channels — it mocks `_build_spec` plumbing. (Captured in baseline.md.)
- [x] Line-level inventory recorded in `.agent_reports/proj-phase-session/PROJ-426/phase_0/baseline.md`.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked.
- [x] Grep results match expectations (4 side-channels, 1 production caller, 3 test files reaching into private state).
- [x] Session file `.agent_reports/proj-phase-session/PROJ-426/phase_0/baseline.md` captured.
- [x] Status updated to Complete.
- [x] plan.md phase table row updated to Complete.
- [x] plan.md Current State updated.
