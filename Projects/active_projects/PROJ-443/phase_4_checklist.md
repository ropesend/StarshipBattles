# Phase 4: Switch `pytest.ini` from `norecursedirs = data` to `--ignore=./data`

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):**
- `pytest.ini`
- `tests/static_guards/test_no_hidden_test_directories.py` (new)

**Objective:** Flip the pytest config so the top-level `data/` is excluded by path (anchored to repo root) rather than by directory-name glob. This stops any `tests/.../data/` test directory from being hidden. Add a regression guard so this class of mistake (`norecursedirs` token matching a real test directory) can never silently recur.

---

## Tasks

### Task 4.1: RED — author the regression guard [Simple]
**File:** `tests/static_guards/test_no_hidden_test_directories.py` (new)

- [ ] Write the guard per `design.md` §"Phase 4 regression guard." Asserts every on-disk `test_*.py` under `tests/` is in `pytest tests/ --collect-only` output.
- [ ] Run the guard against the **current** config — confirm it FAILS (proving the bug exists).
- [ ] Capture the missing-files list size; should be ~94 modules from `tests/unit/strategy/data/` (per Phase 0 ledger).

### Task 4.2: GREEN — flip the config [Simple]
**File:** `pytest.ini`

- [ ] Edit `pytest.ini`:
  - Remove `data` from `norecursedirs`.
  - Add `--ignore=./data` to `addopts` (place it alongside the existing `--ignore=Refactoring`).
- [ ] Re-run the regression guard — must now PASS.
- [ ] Run `python Tools/test_sharded/test_sharded.py 2>&1 | tail -5` — confirm:
  - TOTAL count jumps from ~21233 to ~22700+ (the freshly-collected directory).
  - `0 failed, 0 errors, 0 skipped` — Phases 1-3 made the hidden directory green via direct invocation, so the sharded suite should stay clean after the flip.

### Task 4.3: Commit [Simple]

- [ ] `git add pytest.ini tests/static_guards/test_no_hidden_test_directories.py Projects/active_projects/PROJ-443/{plan.md,decisions.md,phase_state.json}`
- [ ] Commit message: `PROJ-443 Phase 4: switch pytest.ini to --ignore=./data + add regression guard`

---

## Phase Completion Checklist
- [ ] `pytest.ini` flipped; `--ignore=./data` in `addopts`; `data` removed from `norecursedirs`
- [ ] `tests/static_guards/test_no_hidden_test_directories.py` green
- [ ] Sharded suite count jumped (~21233 → ~22700+)
- [ ] Sharded suite green at the new higher count
- [ ] `plan.md` + `phase_state.json` updated
- [ ] Phase 5 unblocked
