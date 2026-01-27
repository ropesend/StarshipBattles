# Phase 4: Assets/UI

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-39 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate asset and UI files to use centralized paths

---

## Tasks

### Task 4.1: Update game/assets/asset_manager.py [Simple]
**File:** `game/assets/asset_manager.py`
**Tests:** `pytest tests/ -v -k asset`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace hardcoded manifest path (line 31):
  - `self.manifest_path = "assets/asset_manifest.json"` → `self.manifest_path = Paths.ASSET_MANIFEST_FILE`
- [ ] Replace any other hardcoded asset paths
- [ ] Verify asset loading works

**Notes:**

### Task 4.2: Update game/ui/assets/ship_theme_manager.py [Simple]
**File:** `game/ui/assets/ship_theme_manager.py`
**Tests:** `pytest tests/ -v -k theme`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace hardcoded themes path (line 91):
  - `"assets/ShipThemes"` → `Paths.SHIP_THEMES_DIR`
- [ ] Remove any local dirname calculations (line 302 if present)
- [ ] Verify ship themes load correctly in ship designer

**Notes:**

### Task 4.3: Update game/simulation/systems/tech_preset_loader.py [Simple]
**File:** `game/simulation/systems/tech_preset_loader.py`
**Tests:** `pytest tests/ -v -k tech or preset`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Replace hardcoded path (line 19):
  - `"..", "..", "..", "data", "tech_presets"` chain → `Paths.TECH_PRESETS_DIR`
- [ ] Verify tech presets load correctly

**Notes:**

### Task 4.4: Update game/ui/screens/setup_data_io.py [Medium]
**File:** `game/ui/screens/setup_data_io.py`
**Tests:** `pytest tests/ -v -k setup or formation`

- [ ] Add import: `from game.core.paths import Paths`
- [ ] Remove dirname chain (line 18 area)
- [ ] Replace hardcoded formations path (line 51):
  - `os.path.join(base_path, "data", "formations")` → `Paths.FORMATIONS_DIR`
- [ ] Replace any other hardcoded data paths
- [ ] Verify formation loading/saving works

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No hardcoded "assets/" strings remain in updated files:
  ```bash
  grep -n '"assets/' game/assets/asset_manager.py
  grep -n '"assets/' game/ui/assets/ship_theme_manager.py
  ```
- [ ] No dirname chains remain in updated files
- [ ] Asset manifest loads correctly
- [ ] Ship themes display in designer
- [ ] Tech presets load
- [ ] Formations load/save correctly
- [ ] Full test suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
