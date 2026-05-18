# Phase 4: `pytest.ini` config flip + regression guard + docs + testmon

**Status:** Complete (2026-05-17, HEAD pending commit)
**Depends on:** phase_3
**Review Mode:** standard
**Files:**
- `pytest.ini` (3 tokens removed from `norecursedirs`)
- `tests/static_guards/test_no_hidden_test_files.py` (new — file-level regression guard)
- `docs/guides/testing_infrastructure.md` (snippet refreshed + Last verified bumped + rationale paragraph added)
- `Projects/active_projects/PROJ-443/findings/hidden_test_baseline.md` (testmon-rebuild instructions)

**Result summary:**
- Sharded suite: **21233 → 23186 tests** (+1953, within 1 of Phase 0 projection 23185)
- **23184 passed, 0 failed, 0 errors, 2 skipped** — clean across the board
- Regression guard green: every test-bearing file under `tests/` is now in pytest's collection

---

## Tasks

### Task 4.1: RED — author the regression guard [Complete]

- [x] Wrote `tests/static_guards/test_no_hidden_test_files.py`. Asserts every on-disk `test_*.py` with at least one `def test_*` or `class Test*` is in `pytest tests/ --collect-only` output.
- [x] Ran the guard against the *pre-flip* config — **FAILED** with 126 missing files (matches Phase 0 inventory exactly: 95 + 24 + 3 + 2 + 1 + 1 across the 6 hidden directories).
- [x] Hardened against false positives: initial impl flagged scaffold modules like `tests/fixtures/test_scenarios.py` (0 test items, legitimately uncollected). Added an AST filter to only require collection for files that actually define test items. See `decisions.md` 2026-05-17 row "Phase 4 regression guard scoped to 'test-bearing files'".

### Task 4.2: GREEN — flip the config (removal-only) [Complete]

- [x] Edited `pytest.ini`: removed `data`, `combat_lab`, `Assets` from `norecursedirs`. `ShipThemes` retained (no matches today; future-proofs).
- [x] Confirmed **no `--ignore` flag** added — `testpaths = tests` + existing `--ignore=combat_lab` in `addopts` are sufficient. Avoids the cwd-relativity foot-gun documented in `decisions.md` 2026-05-18 row.
- [x] Regression guard re-run — **GREEN** (1 passed in 11.03s).
- [x] Sharded suite re-run: **23186 tests | 23184 passed | 0 failed | 0 errors | 2 skipped, 90.3s wall**. Test-count delta +1953 matches Phase 0 projection (visible-baseline 21233 + 1952 hidden tests, minus the 2 skipped formation tests). The 2 skipped are intentional: Phase 3c marked the formation-file tests as `pytest.skip` when `data/formations/` is absent.

### Task 4.3: Refresh `docs/guides/testing_infrastructure.md` snippet [Complete]

- [x] Located the `pytest.ini` snippet at lines 187-194. The snippet didn't previously include `norecursedirs`; added the new value to the snippet rather than just refreshing an existing line.
- [x] Added a rationale paragraph explaining the PROJ-443 token removal (the basename-glob behavior + the `testpaths` overlap + the regression guard).
- [x] Bumped the doc's `> **Last verified:**` blockquote to 2026-05-17.

### Task 4.4: Document the `.testmondata` rebuild [Complete]

- [x] Added a "Post-flip operations" section to `findings/hidden_test_baseline.md` with the rebuild command in both Bash and PowerShell forms. CI / sharded runs don't use testmon, so no infrastructure-level rebuild is required; the `.testmondata` file is gitignored — each contributor rebuilds once locally.
- [x] `decisions.md` 2026-05-18 row already covered the rationale; no additional decision-log entry needed.

### Task 4.5: Commit [Complete]

- [x] Explicit-path `git add` (no `git add -A`).
- [x] Commit message: `PROJ-443 Phase 4: flip pytest.ini norecursedirs + add regression guard (+1953 tests visible)`.

---

## Phase Completion Checklist
- [x] `pytest.ini`: `norecursedirs` no longer contains `data`, `combat_lab`, or `Assets`. Other tokens unchanged. No `--ignore` flag added.
- [x] `tests/static_guards/test_no_hidden_test_files.py` green.
- [x] `docs/guides/testing_infrastructure.md` snippet refreshed + Last verified bumped + rationale paragraph added.
- [x] Sharded suite count jumped by ~1953 (Phase 0 projection met within 1 test).
- [x] Sharded suite green (23184 passed, 0 failed, 0 errors, 2 intentional skips).
- [x] `.testmondata` rebuild instructions documented.
- [x] `plan.md` Current State updated.
- [x] Phase 5 unblocked.
