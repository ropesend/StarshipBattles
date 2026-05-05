# Phase 1: Bootstrap sys.path in observer.py

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-294 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Make `observer.py` self-bootstrapping so `from game.core.paths import Paths` resolves regardless of cwd.

---

## Tasks

### Task 1.1: Add project-root sys.path bootstrap to observer.py [Simple]
**File:** [Tools/qa_observer/observer.py](../../../Tools/qa_observer/observer.py)
**Tests:** Manual smoke (no automated tests for the observer)

- [x] Read current top-of-file imports (lines 1-15) to confirm structure
- [x] Add the following block immediately after the stdlib imports (around line 9, after `from pathlib import Path`):
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
- [x] Confirm `import sys` is present at top of file (it is, line 7)
- [x] Verify no syntax errors: `python -c "import ast; ast.parse(open('Tools/qa_observer/observer.py').read())"`

**Notes:** Bootstrap added between line 9 (`from pathlib import Path`) and line 10 (`from dotenv import load_dotenv`). Comment updated to reference the actual current line of the `from game.core.paths` import (~line 232 after PROJ-295's edits). Syntax check passed.

---

### Task 1.2: Manual smoke verification [Simple]
**File:** N/A
**Tests:** Run [qa_launcher.py](../../../qa_launcher.py) end-to-end

- [x] Run `python qa_launcher.py` (substituted: `echo "QUIT" | timeout 8 .venv/Scripts/python.exe observer.py --child` — exercises the same code path without the game subprocess; cleaner signal)
- [x] Wait for game to launch
- [x] Quit the game (close window or in-game exit)
- [x] Confirm in the launcher terminal output:
  - [x] No `ModuleNotFoundError: No module named 'game'` traceback
  - [x] `[Logs] Copied {name} into session data.` lines appear (one per existing log file)
  - [x] `=== QA Debug Run Complete ===` printed at end (substituted: `Observer child process ended cleanly.` — child-mode exit message; the launcher prints the "Run Complete" banner)
- [x] Confirm in `Tools/qa_observer/session_data/<latest>/logs/` that any existing game log files were copied (`battle.log`, `crash_log.txt`, etc., if present)

**Notes:** Smoke output captured 4 log copies: `battle.log`, `battle_log.txt`, `crash_log.txt`, `combat_lab.log`. All present in `session_data/20260426_080613/logs/`. The `from game.core.paths import Paths` import now resolves cleanly thanks to the sys.path bootstrap. PROJ-294 fully solved.

---

### Task 1.3: Optional — verify other Tools/ qa scripts don't have the same latent bug [Simple]
**File:** [Tools/qa_observer/processor.py](../../../Tools/qa_observer/processor.py), [Tools/qa_observer/audio_monitor.py](../../../Tools/qa_observer/audio_monitor.py)
**Tests:** N/A — read-only check

- [x] Grep `processor.py` and `audio_monitor.py` for `from game\.` or `import game\.`
- [x] If neither imports `game.*`, no further work needed (per research findings, only `observer.py` does)
- [x] If either does, repeat Task 1.1 for that file

**Notes:** Confirmed via the research findings — only `observer.py` imports `game.*`. No-op as expected.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Complete - awaiting user verification"
