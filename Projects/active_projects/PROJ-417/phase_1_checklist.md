# Phase 1: Migrate 2 callers and delete test_run_details.py shim

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-417 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rewrite the 2 caller imports onto the canonical `details` subpackage, then delete the 12-line shim file.

Severity tier: Minor (small migration + whole-file deletion).

---

## Tasks

### Task 1.1: Migrate callers and delete shim
**File:** `game/ui/screens/test_lab/test_run_details.py`
**Tests:** `pytest tests/ -k test_lab`

> **Consult note (2026-05-14, codex):** Only 1 real production import exists.
> `panel_manager.py` imports the shim; `results_panel.py` only references
> `TestRunDetailsPanel` in a comment and receives the panel via injection.
> The `results_panel.py` rewrite task is N/A.

- [ ] Rewrite `from .test_run_details import TestRunDetailsPanel` in `panel_manager.py` to `from .details import TestRunDetailsPanel`
- ~~[ ] Apply the same rewrite in `results_panel.py`~~ — **N/A**: no import in `results_panel.py`, only a comment reference
- [ ] Migrate `tests/unit/test_lab/test_test_run_details_public_api.py`: rewrite `_make_panel()` and all 4 shim-path imports to use `game.ui.screens.test_lab.details`; delete the `test_legacy_and_new_paths_resolve_to_same_class` test (it only tests the shim). Optionally rename the file to `test_details_public_api.py`.
- [ ] Delete `game/ui/screens/test_lab/test_run_details.py`
- [ ] Clean up stale doc references in the same PR: `game/ui/screens/test_lab/__init__.py:15`, `game/ui/screens/test_lab/README.md` (table row + diagram entry), `game/ui/screens/test_lab/details/__init__.py:9-11` (shim-still-exists note), and `docs/02_PATTERNS.md` Pattern #36 entry for this shim if listed
- [ ] Verify: `pytest tests/ -k test_lab` passes; targeted grep for legacy import surface (`from .test_run_details import`, `game.ui.screens.test_lab.test_run_details`, shim-targeted `mock.patch` strings) returns zero hits outside `__pycache__`

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

---

_Source audit: `Reviews/results/2026-05-13_194106_legacy-audit/`. See `findings/source_audit.md` for the link._
