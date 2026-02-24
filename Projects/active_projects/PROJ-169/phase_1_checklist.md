# Phase 1: Zero-Risk Deletes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-169 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete files with zero dependencies — legacy scripts, duplicate image processors, untrack __pycache__

---

## Tasks

### Task 1.1: Delete Legacy Migration Scripts [Simple]
**File:** `docs/_legacy_docs/Tools/` (10 Python files, ~904 LOC)
**Tests:** `pytest tests/ -n 12` (full suite — first run of project, establishes baseline)

- [ ] Verify directory exists: `docs/_legacy_docs/Tools/`
- [ ] Verify zero imports: search codebase for `from docs._legacy_docs` or `legacy_docs.Tools` — expect 0 results
- [ ] Delete all 10 files:
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
- [ ] Delete `docs/_legacy_docs/Tools/` directory if now empty (may contain non-.py files — check first)
- [ ] Verify: no test failures

**Notes:**

---

### Task 1.2: Delete Duplicate formatimg.py Files [Simple]
**File:** 5 identical files in `assets/ShipThemes/` (81 lines each, ~11.5KB total)
**Tests:** No test run needed (asset files, not Python imports)

- [ ] Verify zero imports: search codebase for `formatimg` — expect 0 results
- [ ] Delete all 5 files:
  - `assets/ShipThemes/Atlantians/Origonal Art/Editing/formatimg.py`
  - `assets/ShipThemes/Federation/Origonal art/Editing/formatimg.py`
  - `assets/ShipThemes/Federation/Origonal art/formatimg.py`
  - `assets/ShipThemes/Klingons/Origonal art/Editing/formatimg.py`
  - `assets/ShipThemes/Romulans/Origonal Art/Processsing/formatimg.py`

**Notes:**

---

### Task 1.3: Untrack __pycache__ from Git [Simple]
**File:** 176 `__pycache__/` directories, 1,593 .pyc files (~22.8MB)
**Tests:** No test run needed (git tracking only)

- [ ] Verify `.gitignore` has `__pycache__/` entry
- [ ] Run: `git rm -r --cached **/__pycache__` (untrack only — does NOT delete local files)
- [ ] Verify: `git status` shows __pycache__ files as deleted from index
- [ ] Verify: local __pycache__ directories still exist (Python needs them)

**Notes:**

---

### Task 1.4: Phase 1 Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass (record count: expected ~7353+)
- [ ] Commit Phase 1 changes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
