# Phase 1: Migrate pathfinding shim callers, then delete the shim file

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-414 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate all import and patch sites of `game.strategy.data.pathfinding` to canonical service calls, then delete the 102-line shim module and its guard test.

Severity tier: Major (whole-file deletion after migration).

> **Caller count note:** The audit row states 19 call sites; the verifier's source grep found ~8 production files; a fresh grep (2026-05-14) finds 11 production import statements across 9 files plus 11 test import statements across 8+ files, plus ~30 `patch(...)` sites across 9 test files. The plan's "19" is an approximation. Task 1a produces the definitive list.

---

## Tasks

### Task 1a: Audit and classify all import and patch sites
**File:** `game/strategy/data/pathfinding.py` (read-only in this phase)
**Tests:** none — audit only

- [ ] Grep both import forms across `game/`, `tests/`, `combat_lab/`, `Tools/`:
  ```
  grep -rn 'from game\.strategy\.data\.pathfinding\|from game\.strategy\.data import pathfinding' game/ tests/ combat_lab/ Tools/
  ```
- [ ] Grep for all patch sites referencing the shim path:
  ```
  grep -rn "patch.*game\.strategy\.data\.pathfinding" tests/
  ```
- [ ] Grep for SUT-local patch targets that become broken after callers migrate (e.g. `patch.*handlers\.base\.find_hybrid_path`, `patch.*fleet_navigation_service\.find_hybrid_path`, `patch.*superweapon_order_processor\.get_system_at_hex`):
  ```
  grep -rn "patch.*find_hybrid_path\|patch.*strip_start_hex\|patch.*get_system_at_hex\|patch.*calculate_intercept_point\|patch.*project_fleet_path\|patch.*find_path_interstellar" tests/
  ```
- [ ] For each patch site, record: current patch target → new patch target (must match the name looked up by migrated production code; do NOT add a new forwarding layer)
- [ ] Note `intercept_calculator.py` lines 121 and 169: these deliberately route through the shim for test-patch transparency; migration must decide whether to patch at `game.strategy.services.intercept_calculator.project_fleet_path` / `GalaxyPathfindingService.find_hybrid_path` or restructure the intercept tests
- [ ] Note `tests/unit/strategy/data/test_pathfinding_shim_scope.py`: this guard test pins the shim's function set and must be **deleted** (not updated) as part of the deletion PR
- [ ] Produce a migration table: file | kind (import/patch/guard) | current target | new target | notes

### Task 1b: Migrate tests and production callers
**File:** all files identified in Task 1a
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ --testmon` (focused; run after each code-path group)

Work by code-path group (not file-by-file) to keep each group testable end-to-end:

- [ ] Write/identify failing tests for each group **before** migrating (TDD — confirm test fails, then implement)
- [ ] **Group A — direct pathfinding imports** (`fleet_warp_resolution.py`, `handlers/base.py`, `fleet_navigation_service.py:24`): replace `from game.strategy.data.pathfinding import find_hybrid_path, strip_start_hex` with `GalaxyPathfindingService(galaxy)` injection or `galaxy._pathfinder` access; update corresponding SUT-local patch targets in tests
- [ ] **Group B — intercept callers** (`fleet_navigation_service.py:185`, `intercept_calculator.py:121,169`, `game_session.py`): the `intercept_calculator.py` routes through the shim intentionally; replace shim routing with direct service calls; update test patches to the canonical object/method now called
- [ ] **Group C — get_system_at_hex callers** (`superweapon_order_processor.py`, `strategy_superweapons.py`, `planet_slice.py`, `game_session.py`): replace shim import with `galaxy._pathfinder.get_system_at_hex(...)` or constructed `GalaxyPathfindingService(galaxy).get_system_at_hex(...)`; update patches
- [ ] **Group D — test-only imports** (pathfinding test files importing shim functions directly, integration tests): migrate to import canonical service functions or test the services directly
- [ ] **Group E — shim patch sites** (all `patch('game.strategy.data.pathfinding.X')` sites): rewrite each using the new patch target from the Task 1a migration table
- [ ] Run focused tests after each group; all must pass before proceeding to next group

### Task 1c: Delete shim and verify
**File:** `game/strategy/data/pathfinding.py`, `tests/unit/strategy/data/test_pathfinding_shim_scope.py`
**Tests:** `pytest tests/ --testmon`

- [ ] Delete `game/strategy/data/pathfinding.py`
- [ ] Delete `tests/unit/strategy/data/test_pathfinding_shim_scope.py` (guard test is no longer needed)
- [ ] Verify zero import hits: `grep -rn 'from game\.strategy\.data\.pathfinding\|from game\.strategy\.data import pathfinding' game/ tests/ combat_lab/ Tools/` returns zero results
- [ ] Verify zero patch hits: `grep -rn 'patch.*game\.strategy\.data\.pathfinding' tests/` returns zero results
- [ ] Run: `pytest tests/ --testmon` — must pass

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

---

_Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`. See `findings/source_audit.md` for the link._
