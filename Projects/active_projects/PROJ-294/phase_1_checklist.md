# Phase 1: Bootstrap sys.path in observer.py

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-294 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make `observer.py` self-bootstrapping so `from game.core.paths import Paths` resolves regardless of cwd.

---

## Tasks

### Task 1.1: Add project-root sys.path bootstrap to observer.py [Simple]
**File:** [Tools/qa_observer/observer.py](../../../Tools/qa_observer/observer.py)
**Tests:** Manual smoke (no automated tests for the observer)

- [ ] Read current top-of-file imports (lines 1-15) to confirm structure
- [ ] Add the following block immediately after the stdlib imports (around line 9, after `from pathlib import Path`):
  ```python
  # Make the project root importable so the post-session log-copy step
  # (line ~222: `from game.core.paths import Paths`) works regardless
  # of the launcher's cwd. Mirrors the pattern used by other Tools/
  # scripts that import from game.* (e.g. visual_test_galaxy.py:17,
  # analyze_dependency_graph.py:26).
  _PROJECT_ROOT = Path(__file__).resolve().parents[2]  # Tools/qa_observer/observer.py -> repo root
  if str(_PROJECT_ROOT) not in sys.path:
      sys.path.insert(0, str(_PROJECT_ROOT))
  ```
- [ ] Confirm `import sys` is present at top of file (it is, line 7)
- [ ] Verify no syntax errors: `python -c "import ast; ast.parse(open('Tools/qa_observer/observer.py').read())"`

**Notes:** [Filled during implementation]

---

### Task 1.2: Manual smoke verification [Simple]
**File:** N/A
**Tests:** Run [qa_launcher.py](../../../qa_launcher.py) end-to-end

- [ ] Run `python qa_launcher.py`
- [ ] Wait for game to launch
- [ ] Quit the game (close window or in-game exit)
- [ ] Confirm in the launcher terminal output:
  - [ ] No `ModuleNotFoundError: No module named 'game'` traceback
  - [ ] `[Logs] Copied {name} into session data.` lines appear (one per existing log file)
  - [ ] `=== QA Debug Run Complete ===` printed at end
- [ ] Confirm in `Tools/qa_observer/session_data/<latest>/logs/` that any existing game log files were copied (`battle.log`, `crash_log.txt`, etc., if present)

**Notes:** If `Paths.LOGS_DIR` doesn't exist (no game logs yet), the for-loop just produces no output — that's still success; the import not crashing is the success signal.

---

### Task 1.3: Optional — verify other Tools/ qa scripts don't have the same latent bug [Simple]
**File:** [Tools/qa_observer/processor.py](../../../Tools/qa_observer/processor.py), [Tools/qa_observer/audio_monitor.py](../../../Tools/qa_observer/audio_monitor.py)
**Tests:** N/A — read-only check

- [ ] Grep `processor.py` and `audio_monitor.py` for `from game\.` or `import game\.`
- [ ] If neither imports `game.*`, no further work needed (per research findings, only `observer.py` does)
- [ ] If either does, repeat Task 1.1 for that file

**Notes:** Per [findings/research.md](findings/research.md) §4, only observer.py imports game.* — this task should be a no-op confirmation.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete - awaiting user verification"
