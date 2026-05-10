# Phase 3: Shim-scope freeze + AST guard

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-377 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_2
**Review Mode:** lightweight
**Objective:** Add an AST-walking guard test that pins the surviving `pathfinding.py` free-function set to exactly what Phase 2 left in place — preventing silent regrowth. Update the shim's module docstring to reflect its post-PROJ-377 role (permanent test-patch surface). Backfill the cross-link to PROJ-372.

**Files (planned):** see manifest.md "Phase 3" row group.
**Test target:** `pytest tests/unit/strategy/data/test_pathfinding_shim_scope.py -v`
**Sharded suite:** must remain green; pass count grows by 1.

---

## Reading

- [x] Phase 2 outcomes — list of migrated and deferred sites
- [x] PROJ-377 [decisions.md](decisions.md) — confirm the deferred-site pinning rows exist
- [x] `game/strategy/data/pathfinding.py` — current module shape (top-level FunctionDefs)
- [x] `tests/unit/strategy/data/test_galaxy_planet_star_loc_ceilings.py` — reference for AST-walk test style (PROJ-372 Phase 5 added this; mirror its conventions)

---

## Tasks

### Task 3.1: Determine the surviving free-function set [Simple]
**File:** N/A — analysis
**Tests:** N/A

- [x] Walk through PROJ-377 plan.md Phase 2 scope table. Functions imported by Class B (deferred) + Class C (stays) + the helpers `_pathfinder_for` / `_intercept_for` form the surviving set. Likely:
  - `strip_start_hex` (Class B sites #1, #4, #5)
  - `find_hybrid_path` (Class B sites #1, #4, #5; Class C site #8)
  - `project_fleet_path` (Class B site #2; Class C site #7)
  - `calculate_intercept_point` (Class B site #6)
  - `get_system_at_hex` (Class B site #13; possibly site #9)
  - `_pathfinder_for` (helper)
  - `_intercept_for` (helper)
- [x] Functions Phase 3 is allowed to drop (no production caller AND no test patch):
  - `find_path_deep_space` — re-grep `tests/` for `from game.strategy.data.pathfinding import find_path_deep_space` and `patch.*find_path_deep_space`. If zero hits, drop the shim wrapper.
  - `find_path_interstellar` — re-grep similarly.
  - `find_nearest_system` — used only by Class A site #12 (migrated). Re-grep tests; if zero patches, drop.
- [x] Document the final surviving list in PROJ-377 `decisions.md` as a pinned row.

**Notes:**

### Task 3.2: Optionally remove the dropped free functions [Simple]
**File:** `game/strategy/data/pathfinding.py`
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] **Skip if Task 3.1 found all functions still have callers or test patches.**
- [x] For each function the analysis says is unused: delete its `def` block.
- [x] **Verify:** sharded green.
- [x] **Verify:** focused pathfinding tests still green: `pytest tests/unit/strategy/pathfinding/ -v`.

**Notes:**

### Task 3.3: Write the AST shim-scope guard [Medium]
**File:** `tests/unit/strategy/data/test_pathfinding_shim_scope.py` (NEW)
**Tests:** `pytest tests/unit/strategy/data/test_pathfinding_shim_scope.py -v`

- [x] Module docstring: explain the test's role (AST walk over `pathfinding.py`; assert top-level `FunctionDef` names ≡ pinned set; prevents silent regrowth of the shim). Direct future agents to update the pinned list **deliberately**, not silently, with a decisions.md row when they add or remove a function.
- [x] Test function `test_pathfinding_shim_function_set_pinned()`:
  - Read `game/strategy/data/pathfinding.py` via `pathlib.Path(...).read_text()`.
  - Parse with `ast.parse(...)`.
  - Walk top-level `ast.FunctionDef` nodes; collect their `.name` values into a set.
  - Compare against a hard-coded `EXPECTED_FUNCTIONS = frozenset({...})` set matching Task 3.1's final list.
  - `assert actual == EXPECTED_FUNCTIONS, f"pathfinding.py shim function set drift: actual={actual}, expected={EXPECTED_FUNCTIONS}"`.
- [x] Add a small acceptance test `test_helpers_present()` asserting `_pathfinder_for` and `_intercept_for` are in the set (since they're the test-patch transparency infrastructure).
- [x] Run focused: `pytest tests/unit/strategy/data/test_pathfinding_shim_scope.py -v`. Expect green.
- [x] **Verify:** test passes.

**Notes:**

### Task 3.4: Update the shim's module docstring [Simple]
**File:** `game/strategy/data/pathfinding.py`
**Tests:** N/A

- [x] Replace the current docstring (lines 1-18) with a new docstring that:
  - Names PROJ-377 as the resolution to the Phase 5 leftover.
  - Explains the surviving functions exist as a "permanent test-patch transparency surface" — tests rely on `unittest.mock.patch('game.strategy.data.pathfinding.X')` reaching production code paths in the deferred sites listed in PROJ-377 plan.md.
  - Points future agents at `tests/unit/strategy/data/test_pathfinding_shim_scope.py` for the pinned list and at PROJ-377 decisions.md for the per-site rationale.
  - Drops the "PROJ-376 follow-up" wording.
  - Keeps the explanation of `_pathfinder_for` / `_intercept_for` (it's correct and still load-bearing).
- [x] **Verify:** the file LOC count stays roughly the same (no drift in code, just docstring rewrite).

**Notes:**

### Task 3.5: Backfill PROJ-372 cross-link [Simple]
**File:** `Projects/active_projects/PROJ-372/decisions.md`

- [x] Append a new row dated 2026-XX-XX (Phase 3 commit date):
  > **PROJ-377 closeout:** PROJ-372 review MAJ-001 (golden-save fixture) and MIN-002 (pathfinding shim sweep) closed by PROJ-377. Two JSON golden fixtures committed at `tests/fixtures/saves/galaxy_proj372_baseline.json` and `..._populated.json`; round-trip identity tests added to `test_save_round_trip.py`. Pathfinding shim partial sweep migrated N of 14 sites; M sites remain on the shim by design (test-patch transparency); pinned by `tests/unit/strategy/data/test_pathfinding_shim_scope.py`. See PROJ-377 plan.md and decisions.md for the per-site decisions.
- [x] **Verify:** PROJ-372 plan.md and decisions.md are mutually consistent re: Phase 5 leftovers status (both should now reference PROJ-377 as the resolution).

**Notes:**

### Task 3.6: Optional doc update — `docs/systems/strategy_layer.md` [Simple]
**File:** `docs/systems/strategy_layer.md`
**Tests:** N/A

- [x] If the doc references the shim's "deprecated" status or a "PROJ-376 follow-up", update to point at PROJ-377 closeout.
- [x] If no such reference exists, skip (no update needed).
- [x] Update `> **Last verified:** 2026-XX-XX` blockquote per `docs/03_CONVENTIONS.md` §9.

**Notes:**

### Task 3.7: Run sharded suite [Medium]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run the full sharded suite.
- [x] **Verify:** pass count = baseline + 3 (2 golden-fixture tests from Phase 1 + 1 AST shim-scope test from Phase 3); zero new failures.

**Notes:**

### Task 3.8: Run final-verification grep sweep [Simple]
**File:** N/A
**Tests:** N/A

- [x] `Grep` for `from game\.strategy\.data\.pathfinding import|from game\.strategy\.data import pathfinding` under `game/`. Confirm count matches the deferred-site list pinned in decisions.md.
- [x] `Grep` for `galaxy\._intercept\b` under `game/`. Confirm zero hits (PROJ-372 review MIN-001 remediation preserved).
- [x] `Grep` for `from game\.strategy\.data\.pathfinding import` under `tests/`. Pin the count in decisions.md as the "test-patch surface dependency count" — for documentation only, no migration this phase.

**Notes:**

### Task 3.9: Commit Phase 3 [Simple]
**File:** N/A

- [x] `git add tests/unit/strategy/data/test_pathfinding_shim_scope.py game/strategy/data/pathfinding.py Projects/active_projects/PROJ-372/decisions.md Projects/active_projects/PROJ-377/decisions.md` (and `docs/systems/strategy_layer.md` if Task 3.6 modified it).
- [x] Commit message: `PROJ-377 phase 3: AST shim-scope guard + docstring update + PROJ-372 cross-link (closes MIN-002)`
- [x] **Verify:** `git status` clean; `git log -1 --stat` shows expected files.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] AST shim-scope guard committed and green
- [x] Shim docstring reflects PROJ-377 closeout
- [x] PROJ-372 cross-link backfilled
- [x] Sharded suite green; pass count = baseline + 3
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Awaiting user verification"
- [x] Final audit log entry in plan.md
