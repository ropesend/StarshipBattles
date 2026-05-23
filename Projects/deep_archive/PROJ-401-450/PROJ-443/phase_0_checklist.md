# Phase 0: Capture hidden-test baseline (all 6 hidden directories)

**Status:** Complete (2026-05-17, HEAD `42ac82eec`)
**Depends on:** none
**Review Mode:** lightweight
**Files (planned):** `Projects/active_projects/PROJ-443/findings/hidden_test_baseline.md` (new)

**Objective:** Document the current pass/fail count and exact list of failing test IDs in every test directory currently hidden from the sharded suite by `pytest.ini`'s `norecursedirs` token collisions. **6 hidden directories, 126 files total** per the directory audit:

| Hidden directory | `test_*.py` count | Hidden by token |
|---|---|---|
| `tests/unit/strategy/data/` | 95 | `data` |
| `tests/unit/combat_lab/` | 24 | `combat_lab` |
| `tests/unit/data/` | 3 | `data` |
| `tests/unit/assets/` | 2 | `Assets` (case-insensitive fnmatch on Windows) |
| `tests/unit/ui/assets/` | 1 | `Assets` (case-insensitive fnmatch on Windows) |
| `tests/integration/data/` | 1 | `data` |

No code changes in Phase 0. Establishes the baseline ledger that Phases 1-3 work against.

---

## Tasks

### Task 0.1: Audit hidden directories (sanity-check the inventory) [Simple]

- [x] `find tests -type d \( -name data -o -name combat_lab -o -iname assets -o -name ShipThemes \) 2>/dev/null` — confirmed the 6 directories. `tests/unit/research/data/` exists but has 0 test files (informational only).
- [x] Per-dir file counts confirmed: strategy/data=95, combat_lab=24, unit/data=3, unit/assets=2, ui/assets=1, integration/data=1 → **126 total**.
- [x] Recorded directory list + counts in `findings/hidden_test_baseline.md` §"Hidden directories — inventory."
- [x] `ShipThemes` token no-match documented (no test directories match; harmless, retained per `decisions.md` 2026-05-18 row).

### Task 0.2: Capture pass/fail counts per hidden directory [Simple]

- [x] All 6 directories executed via `python -m pytest <dir> -q --no-header -n 4`; raw outputs stored under `findings/raw/<dir>.out`.
- [x] Final pass/fail lines extracted: strategy/data **1506P/67F**, combat_lab **268P/0F**, unit/data **22P/7F**, unit/assets **28P/1F**, ui/assets **30P/0F**, integration/data **23P/0F**.
- [x] Counts recorded in `findings/hidden_test_baseline.md` §"Per-directory counts."

### Task 0.3: Capture exact failing test IDs [Simple]

- [x] All 75 failing test IDs extracted into `findings/hidden_test_baseline.md` §"Failing test inventory (clustered by phase)."
- [x] Cluster tags applied: Phase 1 (test_cargo_tracking.py, 30) / Phase 2 (test_mutator_boundary_ast_guard.py, 4) / Phase 3a strategy/data long-tail (33 across 6 files) / Phase 3b combat_lab (0) / Phase 3c small-dir (8).

### Task 0.4: Capture current visible-suite baseline [Simple]

- [x] `python Tools/test_sharded/test_sharded.py` → **TOTAL: 21233 tests | 21233 passed | 0 failed**, wall 114.5s (16 shards). Matches plan's "~21233" cite exactly.
- [x] Recorded at the top of `findings/hidden_test_baseline.md` §"Visible-suite baseline."

### Task 0.5: Project the post-flip count [Simple]

- [x] Projection recorded: **21233 → ~23185** post-flip (assuming all 75 failures are *fixed*, not *deleted*; conservative band 23110–23185). Plan's stated "21359+" conflated file count with test count (delta is 1952 tests, not 126 files).

### Task 0.6: Commit the baseline ledger [Simple]

- [x] Added: `Projects/active_projects/PROJ-443/findings/hidden_test_baseline.md`, `Projects/active_projects/PROJ-443/plan.md`, `Projects/active_projects/PROJ-443/decisions.md`, `Projects/active_projects/PROJ-443/phase_0_checklist.md`. `phase_state.json` retained but not authoritative (03c dropped per user direction).
- [x] Commit message: `PROJ-443 Phase 0: capture hidden-test baseline (6 directories, 126 files, 75 failures)`

---

## Phase Completion Checklist
- [x] `findings/hidden_test_baseline.md` committed with directory list + counts + failing IDs + cluster tags
- [x] Post-flip count projection recorded
- [x] `plan.md` Current State updated
- [N/A] `phase_state.json` not used — 03c dropped per user direction (see `plan.md` Execution Protocol note)
