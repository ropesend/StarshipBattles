# Phase 4: `pytest.ini` config flip + regression guard + docs + testmon

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):**
- `pytest.ini` (remove 3 tokens from `norecursedirs`)
- `tests/static_guards/test_no_hidden_test_files.py` (new)
- `docs/guides/testing_infrastructure.md` (refresh embedded `pytest.ini` snippet)

**Objective:** Remove the three problematic tokens (`data`, `combat_lab`, `Assets`) from `pytest.ini`'s `norecursedirs`. **No `--ignore` flag is added** — `testpaths = tests` already prevents pytest from descending into the top-level dirs the tokens were trying to skip, and `--ignore=./data` would be cwd-relative per pytest 9.0.3 source (`_pytest/pathlib.py:998-1004`), creating a foot-gun for non-canonical invocations. Add a file-level structural regression guard so this class of mistake can never silently recur. Refresh the embedded `pytest.ini` snippet in `docs/guides/testing_infrastructure.md`. Document the `.testmondata` rebuild recommendation.

---

## Tasks

### Task 4.1: RED — author the regression guard [Simple]
**File:** `tests/static_guards/test_no_hidden_test_files.py` (new)

- [ ] Write the guard per `design.md` §"Phase 4 regression guard." Asserts every on-disk `test_*.py` under `tests/` is in `pytest tests/ --collect-only` output.
- [ ] Run the guard against the **current** config — confirm it FAILS (proving the bug exists).
- [ ] Capture the missing-files list size: should be 126 modules across 6 hidden directories (95 + 24 + 3 + 2 + 1 + 1).

### Task 4.2: GREEN — flip the config (removal-only) [Simple]
**File:** `pytest.ini`

Before:
```ini
norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv data ShipThemes Assets combat_lab
```

After:
```ini
norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv ShipThemes
```

- [ ] Edit `pytest.ini`: remove `data`, `combat_lab`, `Assets` from `norecursedirs`. Keep `ShipThemes` (harmless; no matches today; future-proofs).
- [ ] Do NOT add any `--ignore` flag to `addopts`. The existing `--ignore=combat_lab` in `addopts` (which IS cwd-relative but works for the sharded runner's PROJECT_ROOT cwd) plus `testpaths = tests` are already sufficient.
- [ ] Re-run the regression guard — must now PASS.
- [ ] Run `python Tools/test_sharded/test_sharded.py 2>&1 | tail -8` — confirm:
  - TOTAL count jumps by ~126 (matches Phase 0 projection).
  - `0 failed, 0 errors, 0 skipped` — Phases 1-3 made the hidden directories green via direct invocation, so the sharded suite stays clean after the flip.
  - Wall time may increase slightly (~5-10s) from the new tests; first-run shard imbalance is expected as `.test_durations.json` lacks data for the freshly-visible tests.

### Task 4.3: Refresh `docs/guides/testing_infrastructure.md` snippet [Simple]
**File:** `docs/guides/testing_infrastructure.md`

- [ ] Read the doc; locate the embedded `pytest.ini` snippet (per Codex's pre-execution consult, around lines 187-194).
- [ ] Update the snippet to show the new `norecursedirs` value.
- [ ] Add a brief 1-2 sentence rationale line citing PROJ-443: "Removed `data`, `combat_lab`, `Assets` from `norecursedirs` per PROJ-443; `testpaths = tests` already covers the top-level dirs these tokens were trying to skip, and the tokens were inadvertently hiding 126 real tests under `tests/.../<token>/`."
- [ ] Update the `> **Last verified:** YYYY-MM-DD` blockquote at the top per `docs/03_CONVENTIONS.md` §"Documentation Freshness."

### Task 4.4: Document the `.testmondata` rebuild [Simple]

- [ ] In `decisions.md`, confirm the existing row on `.testmondata` rebuild and update if Phase 4 surfaces any specifics.
- [ ] In `findings/hidden_test_baseline.md` (or a new findings note), record the one-line rebuild command for future contributors: `rm .testmondata && pytest tests/ --testmon` (Bash) or `Remove-Item .testmondata; python -m pytest tests/ --testmon` (PowerShell).

### Task 4.5: Commit (use explicit file paths) [Simple]

- [ ] `git add pytest.ini tests/static_guards/test_no_hidden_test_files.py docs/guides/testing_infrastructure.md Projects/active_projects/PROJ-443/plan.md Projects/active_projects/PROJ-443/decisions.md Projects/active_projects/PROJ-443/phase_state.json` (NOT `git add -A` — PROJ-438 may have unrelated dirty files).
- [ ] Commit message: `PROJ-443 Phase 4: remove data/combat_lab/Assets tokens from norecursedirs + add regression guard`.

---

## Phase Completion Checklist
- [ ] `pytest.ini`: `norecursedirs` no longer contains `data`, `combat_lab`, or `Assets`. Other tokens unchanged. No `--ignore` flag added.
- [ ] `tests/static_guards/test_no_hidden_test_files.py` green.
- [ ] `docs/guides/testing_infrastructure.md` snippet refreshed + Last verified bumped.
- [ ] Sharded suite count jumped by ~126 (per Phase 0 projection).
- [ ] Sharded suite green (0 failed, 0 errors, 0 skipped).
- [ ] `.testmondata` rebuild recommendation documented.
- [ ] `plan.md` Current State + `phase_state.json` updated.
- [ ] Phase 5 unblocked.
