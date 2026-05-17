# Phase 0: Preflight and baseline capture

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-426 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Run the first guardrail grep:
  ```bash
  rg -n "build_strategy_battle_spec|object\.__setattr__\(spec|_mine_groups|_owner_to_team_id|_combat_fleets|_engine_ref" game tests
  ```
- [ ] Run the second guardrail grep:
  ```bash
  rg -n "from game\.strategy\.combat\.spec_compiler import build_strategy_battle_spec|build_strategy_battle_spec\(" game tests docs
  ```
- [ ] Record the counts of `object.__setattr__(spec, ...)` writes in `spec_compiler.py`. Confirm there are exactly **4** (`_mine_groups`, `_owner_to_team_id`, `_engine_ref`, `_combat_fleets` at `spec_compiler.py:271-279`). If a 5th has appeared since verification, extend the touch list and surface to coordinator before starting Phase 1.
- [ ] Capture the result in this phase's session file under `.agent_reports/proj-phase-session/PROJ-426/phase_0/baseline.md`.

**Notes:**

### Task 0.2: Confirm sole production runtime caller [Simple]
**File:** N/A (read-only)
**Tests:** N/A

- [ ] Confirm `game/strategy/adapters/simulation_adapter.py` is still the only production runtime caller of `build_strategy_battle_spec(...)`.
- [ ] Confirm `game/strategy/engine/conflict_resolution_engine.py` mentions the compiler **in comments only** (no runtime call).
- [ ] If a new runtime caller appears, surface to coordinator and extend the touch list before Phase 1.

**Notes:**

### Task 0.3: Inventory tests that pin private side-channels [Simple]
**File:** N/A (read-only)
**Tests:** N/A

- [ ] Record exact line numbers of `spec._mine_groups`, `spec._owner_to_team_id`, `spec._combat_fleets`, `spec._engine_ref` reads in `tests/integration/test_fms_b_e2e.py` (verification cited `:414, 415, 420, 493`; confirm current state).
- [ ] Confirm `tests/unit/strategy/combat/test_fighter_group_combat_join.py` and `tests/unit/strategy/combat/test_satellite_group_combat_join.py` still import `_split_mine_groups_from_fleets` from `spec_compiler`.
- [ ] Confirm `tests/unit/strategy/adapters/test_simulation_adapter.py` reads side-channels off the spec.
- [ ] Record line-level inventory in the session file so Phase 4's migration commit has an authoritative target list.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked.
- [ ] Grep results match expectations (4 side-channels, 1 production caller, 3 test files reaching into private state).
- [ ] Session file `.agent_reports/proj-phase-session/PROJ-426/phase_0/baseline.md` captured.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to point to Phase 1.
