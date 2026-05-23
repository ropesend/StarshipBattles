# Phase 4: Audit remediation (Codex consult 2026-05-23)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-478 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address 3 VERIFIED + IN-SCOPE findings from the Codex mid-project audit. See `findings/audit_verification.md` for the full verdict table.

---

## Tasks

### Task 4.1: Remove dead guard below unconditional skip (F1) [Simple]
**File:** `tests/unit/builder/test_ship_loading.py`
**Tests:** `pytest tests/unit/builder/test_ship_loading.py -v`

- [x] At line 96, the `pytest.skip(...)` fires unconditionally. Lines 102-end of `test_all_ships_match_expected_stats` are unreachable. Delete all code after the `pytest.skip(...)` block (the `# Find all ship JSON files...` comment through the end of the function body). Keep the docstring and the `pytest.skip(...)` call.
- [x] Confirm the function ends with just docstring + skip, no dead loop/assertions.
- [x] Remove any imports that become unused after the dead-code deletion (e.g., `glob`, `load_json` etc. — only remove if unused elsewhere in the file).
- [x] Verify: `pytest tests/unit/builder/test_ship_loading.py` — test should report SKIPPED.

**Notes:** The skip is correct given DI-2026-05-23-002. The `len(ship_files) >= 1` guard from phase_1 task 1.10 had legitimate intent (fail-loud), but only matters when the test runs. With the unconditional skip in place, keeping the guard is dead code and misleading.

---

### Task 4.2: Rename benchmark functions to bench_* prefix (F2) [Simple]
**File:** `profiling/panels/bench_panel_full_open.py`
**Tests:** N/A (file is outside `tests/` per pytest.ini testpaths)

- [x] Line 141: rename `def test_full_window_open_uncached(` → `def bench_full_window_open_uncached(`
- [x] Line 164: rename `def test_full_window_open_with_cache(` → `def bench_full_window_open_with_cache(`
- [x] Grep the rest of the file for cross-references to these names and update if any.
- [x] Verify: `python -c "import ast; ast.parse(open('profiling/panels/bench_panel_full_open.py').read())"` parses clean.

**Notes:** No live pytest-collection bug (testpaths excludes `profiling/`), but the manifest in `manifest.md:34` claims the rename happened. Make the code match the manifest claim.

---

### Task 4.3: Fix manifest drift (F3) [Simple]
**File:** `Projects/active_projects/PROJ-478/manifest.md`
**Tests:** N/A (project artifact)

- [x] Line 20 (`tests/unit/builder/test_ship_loading.py`): rewrite Notes column to: `Phase 1 — add minimum-files guard; guard surfaced DI-2026-05-23-002 (fixtures dir tests/unit/ships/ never existed), test now skipped pending fixture sourcing`
- [x] Line 22 (`tests/unit/strategy/consumable_management_engine/conftest.py`): rewrite Notes column to: `Phase 1 — plan said delete; preserved (3 sibling test files consume its fixtures across ~30 tests). Removed only the redundant inline mock_registries from test_initialization.py.`
- [x] Line 37 (`tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`): rewrite Notes column to: `Phase 3 — plan said add @pytest.mark.skip to 4 issue17 tests pending PROJ-410 Phase 2; SCOPE DECISION: skip NOT added because verification report premise is stale (helper now exists in production at game/ui/components/table/virtual_table.py and all 9 affected tests pass)`
- [x] Line 34 stays as-is (the F2 rename in Task 4.2 makes the claim true).
- [x] Verify: `python Projects/scripts/validate_phase.py PROJ-478 4` returns PASSED.

**Notes:** "Keep code and docs consistent" per CLAUDE.md.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (or close)
