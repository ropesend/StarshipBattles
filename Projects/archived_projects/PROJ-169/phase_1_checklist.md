# Phase 1: Zero-Risk Deletes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-169 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete files with zero dependencies — legacy scripts, duplicate image processors, untrack __pycache__

---

## Tasks

### Task 1.1: Delete Legacy Migration Scripts [Simple]
**File:** `docs/_legacy_docs/Tools/` (10 Python files, ~904 LOC)
**Tests:** `pytest tests/ -n 12` (full suite — first run of project, establishes baseline)

- [x] Verify directory exists: `docs/_legacy_docs/Tools/`
- [x] Verify zero imports: search codebase for `from docs._legacy_docs` or `legacy_docs.Tools` — expect 0 results
- [x] Delete all 10 files:
  - `docs/_legacy_docs/Tools/fix_modifiers.py`
  - `docs/_legacy_docs/Tools/fix_modifiers_v2.py`
  - `docs/_legacy_docs/Tools/migrate_data.py`
  - `docs/_legacy_docs/Tools/migrate_legacy_components.py`
  - `docs/_legacy_docs/Tools/refactor_phase2.py`
  - `docs/_legacy_docs/Tools/refactor_phase3.py`
  - `docs/_legacy_docs/Tools/refactor_phase4.py`
  - `docs/_legacy_docs/Tools/refactor_phase5.py`
  - `docs/_legacy_docs/Tools/refactor_phase6.py`
  - `docs/_legacy_docs/Tools/refactor_phase6b.py`
- [x] Delete `docs/_legacy_docs/Tools/` directory if now empty (may contain non-.py files — check first)
- [x] Verify: no test failures

**Notes:** Directory was empty after file deletion, removed. Imports found only in project documentation, not actual code.

---

### Task 1.2: Delete Duplicate formatimg.py Files [Simple]
**File:** 5 identical files in `assets/ShipThemes/` (81 lines each, ~11.5KB total)
**Tests:** No test run needed (asset files, not Python imports)

- [x] Verify zero imports: search codebase for `formatimg` — expect 0 results
- [x] Delete all 5 files:
  - `assets/ShipThemes/Atlantians/Origonal Art/Editing/formatimg.py`
  - `assets/ShipThemes/Federation/Origonal art/Editing/formatimg.py`
  - `assets/ShipThemes/Federation/Origonal art/formatimg.py`
  - `assets/ShipThemes/Klingons/Origonal art/Editing/formatimg.py`
  - `assets/ShipThemes/Romulans/Origonal Art/Processsing/formatimg.py`

**Notes:** References found only in documentation and reports, no actual code imports.

---

### Task 1.3: Untrack __pycache__ from Git [Simple]
**File:** 176 `__pycache__/` directories, 1,593 .pyc files (~22.8MB)
**Tests:** No test run needed (git tracking only)

- [x] Verify `.gitignore` has `__pycache__/` entry
- [x] Run: `git rm -r --cached **/__pycache__` (untrack only — does NOT delete local files)
- [x] Verify: `git status` shows __pycache__ files as deleted from index
- [x] Verify: local __pycache__ directories still exist (Python needs them)

**Notes:** No __pycache__ directories were tracked in git (0 files found via `git ls-files | grep __pycache__`). Already clean.

---

### Task 1.4: Phase 1 Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] All tests pass (record count: expected ~7353+)
- [x] Commit Phase 1 changes

**Notes:** 12023 passed, 1 skipped in 61.11s

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
