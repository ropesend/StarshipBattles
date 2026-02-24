# Phase 4: Polish

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-169 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove unused imports, fix directory structure issues, clean up empty directories

---

## Tasks

### Task 4.1: Remove Unused Imports [Simple]
**File:** 10 files in `game/`
**Tests:** `pytest tests/ --testmon`

Remove these 14 unused standard library imports:

- [ ] `game/app.py` — remove `import os`
- [ ] `game/simulation/battle_controller.py` — remove `import copy`
- [ ] `game/simulation/components/component.py` — remove `import math`
- [ ] `game/simulation/systems/battle_engine.py` — remove `import math`
- [ ] `game/simulation/systems/battle_engine.py` — remove `import time`
- [ ] `game/simulation/entities/ship.py` — remove `import random`
- [ ] `game/simulation/services/registry_loader.py` — remove `import os`
- [ ] `game/strategy/quickstart_builder.py` — remove `import os`
- [ ] `game/ui/screens/battle_screen.py` — remove `import math`
- [ ] `game/ui/screens/battle_screen.py` — remove `import random`
- [ ] `game/ui/screens/empire_panel_window.py` — remove `import os`
- [ ] `game/ui/screens/race_setup_screen.py` — remove `import os`
- [ ] `game/ui/screens/strategy_panel_manager.py` — remove `import os`
- [ ] `game/ui/screens/test_lab/screen.py` — remove `import sys`

**Notes:**

---

### Task 4.2: Relocate tests/refactor/ to tests/regression/ [Simple]
**File:** `tests/refactor/test_deprecated_code_removed.py` (136 lines)
**Tests:** `pytest tests/regression/` (after move)

- [ ] Read `tests/refactor/test_deprecated_code_removed.py` to confirm it's a regression guard
- [ ] Check if `tests/regression/` exists — if so, merge contents
- [ ] Move `tests/refactor/test_deprecated_code_removed.py` to `tests/regression/test_deprecated_code_removed.py`
- [ ] Delete `tests/refactor/` directory (if now empty — check for __init__.py or other files)
- [ ] Verify moved test passes: `pytest tests/regression/test_deprecated_code_removed.py`

**Notes:**

---

### Task 4.3: Delete Empty Directories [Simple]
**File:** `game/ui/hud/`, `game/simulation/entities/mixins/`
**Tests:** No test run needed

- [ ] Verify `game/ui/hud/` is empty (or contains only `__init__.py` / `__pycache__`)
- [ ] Delete `game/ui/hud/` directory entirely
- [ ] Verify `game/simulation/entities/mixins/` is empty (or contains only `__init__.py` / `__pycache__`)
- [ ] Delete `game/simulation/entities/mixins/` directory entirely
- [ ] Search for imports: `from game.ui.hud` and `from game.simulation.entities.mixins` — expect 0 results

**Notes:**

---

### Task 4.4: Final Verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All tests pass (record count)
- [ ] Commit Phase 4 changes
- [ ] Verify overall project goals met:
  - [ ] No dead code files remain
  - [ ] Tools/ directory fully removed
  - [ ] scripts/ curated to active tools only
  - [ ] No unused imports in game/
  - [ ] No empty directories
  - [ ] pytest.ini clean

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
