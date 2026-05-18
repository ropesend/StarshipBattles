# Phase 0: Capture hidden-test baseline (all 6 hidden directories)

**Status:** Not Started
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

- [ ] `find tests -type d \( -name data -o -name combat_lab -o -iname assets -o -name ShipThemes \) 2>/dev/null` — confirm the 6 directories above (plus `tests/unit/research/data/` which has 0 test files).
- [ ] For each, `find <dir> -maxdepth 10 -name "test_*.py" -type f | wc -l` — confirm file counts.
- [ ] Record the directory list + counts in `findings/hidden_test_baseline.md` §"Hidden directories."
- [ ] Document `ShipThemes` token's no-match status — it's harmless and stays in `norecursedirs` per `decisions.md`.

### Task 0.2: Capture pass/fail counts per hidden directory [Simple]

- [ ] For each hidden directory (6 total), run:
  ```
  python -m pytest <dir> -q -n 4 --no-header 2>&1 | tee /tmp/<dirname>.out
  ```
- [ ] Extract the final `N passed, M failed[, E errors][, S skipped]` line per directory.
- [ ] Record counts in `findings/hidden_test_baseline.md` §"Per-directory counts."

### Task 0.3: Capture exact failing test IDs [Simple]

- [ ] For each hidden directory, extract the `FAILED tests/...::test_*` lines into `findings/hidden_test_baseline.md` §"Failing test inventory."
- [ ] Tag each failure by cluster: `test_cargo_tracking.py` (Phase 1) / `test_mutator_boundary_ast_guard.py` (Phase 2) / strategy/data other (Phase 3 cluster a) / combat_lab (Phase 3 cluster b) / other smaller-dir (Phase 3 cluster c).

### Task 0.4: Capture current visible-suite baseline [Simple]

- [ ] `python Tools/test_sharded/test_sharded.py 2>&1 | tail -5` — record TOTAL line and wall time.
- [ ] Record at the top of `findings/hidden_test_baseline.md` for context.

### Task 0.5: Project the post-flip count [Simple]

- [ ] Compute expected post-Phase-4 sharded count: visible baseline + (sum of hidden directory pass counts after Phases 1-3 land). Document the projection in the ledger so Phase 4 has an expected target.

### Task 0.6: Commit the baseline ledger [Simple]

- [ ] `git add Projects/active_projects/PROJ-443/findings/hidden_test_baseline.md Projects/active_projects/PROJ-443/plan.md Projects/active_projects/PROJ-443/decisions.md Projects/active_projects/PROJ-443/phase_state.json` (no `git add -A`; PROJ-438 has unrelated dirty files).
- [ ] Commit message: `PROJ-443 Phase 0: capture hidden-test baseline (6 directories, 126 files)`

---

## Phase Completion Checklist
- [ ] `findings/hidden_test_baseline.md` committed with directory list + counts + failing IDs + cluster tags
- [ ] Post-flip count projection recorded
- [ ] `plan.md` Current State updated
- [ ] `phase_state.json` phase_0.status = `complete`, `phase_head_sha` recorded
