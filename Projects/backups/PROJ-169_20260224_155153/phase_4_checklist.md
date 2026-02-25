# Phase 4: Polish

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-169 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove unused imports, fix directory structure issues, clean up empty directories

---

## Tasks

### Task 4.1: Remove Unused Imports [Simple]
**File:** 10 files in `game/`
**Tests:** `pytest tests/ --testmon`

Remove these 14 unused standard library imports:

- [x] `game/app.py` — remove `import os`
- [x] `game/simulation/battle_controller.py` — remove `import copy`
- [x] `game/simulation/components/component.py` — remove `import math`
- [x] `game/simulation/systems/battle_engine.py` — remove `import math`
- [x] `game/simulation/systems/battle_engine.py` — remove `import time`
- [x] `game/simulation/entities/ship.py` — remove `import random`
- [x] `game/simulation/services/registry_loader.py` — remove `import os`
- [x] `game/strategy/quickstart_builder.py` — remove `import os`
- [x] `game/ui/screens/battle_screen.py` — remove `import math`
- [x] `game/ui/screens/battle_screen.py` — remove `import random`
- [x] `game/ui/screens/empire_panel_window.py` — remove `import os`
- [x] `game/ui/screens/race_setup_screen.py` — remove `import os`
- [x] `game/ui/screens/strategy_panel_manager.py` — remove `import os`
- [x] `game/ui/screens/test_lab/screen.py` — remove `import sys`

**Notes:** All 14 unused imports removed, tests passing.

---

### Task 4.2: Relocate tests/refactor/ to tests/regression/ [Simple]
**File:** `tests/refactor/test_deprecated_code_removed.py` (136 lines)
**Tests:** `pytest tests/regression/` (after move)

- [x] Read `tests/refactor/test_deprecated_code_removed.py` to confirm it's a regression guard
- [x] Check if `tests/regression/` exists — if so, merge contents
- [x] Move `tests/refactor/test_deprecated_code_removed.py` to `tests/regression/test_deprecated_code_removed.py`
- [x] Delete `tests/refactor/` directory (if now empty — check for __init__.py or other files)
- [x] Verify moved test passes: `pytest tests/regression/test_deprecated_code_removed.py`

**Notes:** File moved, directory deleted, 15 tests passing.

---

### Task 4.3: Delete Empty Directories [Simple]
**File:** `game/ui/hud/`, `game/simulation/entities/mixins/`
**Tests:** No test run needed

- [x] Verify `game/ui/hud/` is empty (or contains only `__init__.py` / `__pycache__`)
- [x] Delete `game/ui/hud/` directory entirely
- [x] Verify `game/simulation/entities/mixins/` is empty (or contains only `__init__.py` / `__pycache__`)
- [x] Delete `game/simulation/entities/mixins/` directory entirely
- [x] Search for imports: `from game.ui.hud` and `from game.simulation.entities.mixins` — expect 0 results

**Notes:** Both directories were empty (no __init__.py or __pycache__), deleted successfully.

---

### Task 4.4: Final Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] All tests pass (record count)
- [x] Commit Phase 4 changes
- [x] Verify overall project goals met:
  - [x] No dead code files remain
  - [x] Tools/ directory fully removed
  - [x] scripts/ curated to active tools only
  - [x] No unused imports in game/
  - [x] No empty directories
  - [x] pytest.ini clean

**Notes:** 12023 passed, 1 skipped. All project goals verified complete.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
