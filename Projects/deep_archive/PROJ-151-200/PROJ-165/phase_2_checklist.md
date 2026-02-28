# Phase 2: Migrate Race Editor Panels (19 sites)

## Task 2.1: Migrate race_identity_panel.py (3 sites)
**File:** `game/ui/panels/race_identity_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`

- [x] Add import: `from game.ui.utils import create_section_header`
- [x] Site 1 (~line 101, "Species Identity:"): Replace 6-line UILabel block → `create_section_header("Species Identity:", y, 200, self.ui_manager, self.panel)`
- [x] Site 2 (~line 166, "Government:"): Replace → `create_section_header("Government:", y, 200, self.ui_manager, self.panel)`
- [x] Site 3 (~line 268, "Faction:"): Replace → `create_section_header("Faction:", y, 200, self.ui_manager, self.panel)`
- [x] Run tests

**Notes:** All 3 use identical params: width=200, x=10, height=25.

## Task 2.2: Migrate race_environment_panel.py (6 sites)
**File:** `game/ui/panels/race_environment_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`

- [x] Add import: `from game.ui.utils import create_section_header`
- [x] Site 4 (~line 135, "Homeworld Type:"): Replace → `create_section_header("Homeworld Type:", y, 200, self.ui_manager, self.panel)`
- [x] Site 5 (~line 169, "Gravity Preferences:"): Replace → `create_section_header("Gravity Preferences:", y, 200, self.ui_manager, self.panel)`
- [x] Site 6 (~line 228, "Temperature Preferences:"): Replace → `create_section_header("Temperature Preferences:", y, 200, self.ui_manager, self.panel)`
- [x] Site 7 (~line 287, "Radiation Tolerance:"): Replace → `create_section_header("Radiation Tolerance:", y, 200, self.ui_manager, self.panel)`
- [x] Site 8 (~line 323, "Water Preferences:"): Replace → `create_section_header("Water Preferences:", y, 200, self.ui_manager, self.panel)`
- [x] Site 9 (~line 382, "Atmosphere Preferences..."): Replace → `create_section_header("Atmosphere Preferences (-100 toxic to +100 beneficial):", y, width, self.ui_manager, self.panel)` — note: uses variable `width`, not `200`
- [x] Run tests

**Notes:** 5 of 6 use width=200. Site 9 uses panel `width` variable.

## Task 2.3: Migrate race_aptitudes_panel.py (3 sites)
**File:** `game/ui/panels/race_aptitudes_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`

- [x] Add import: `from game.ui.utils import create_section_header`
- [x] Site 10 (~line 108, "Point Budget:"): Replace → `create_section_header("Point Budget:", y, 200, self.ui_manager, self.panel)`
- [x] Site 11 (~line 132, "Aptitudes (1-100, base 50):"): Replace → `create_section_header("Aptitudes (1-100, base 50):", y, 200, self.ui_manager, self.panel)`
- [x] Site 12 (~line 191, "Cost Breakdown:"): Replace → `create_section_header("Cost Breakdown:", y, 200, self.ui_manager, self.panel)`
- [x] Run tests

**Notes:**

## Task 2.4: Migrate race_description_panel.py (2 sites)
**File:** `game/ui/panels/race_description_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`

- [x] Add import: `from game.ui.utils import create_section_header`
- [x] Site 13 (~line 65, "Biological Description:"): Replace → `create_section_header("Biological Description:", y, 300, self.ui_manager, self.panel)` — note: width=300
- [x] Site 14 (~line 90, "Sociological Description:"): Replace → `create_section_header("Sociological Description:", y, 300, self.ui_manager, self.panel)` — note: width=300
- [x] Run tests

**Notes:** Both use width=300, wider than the other race panels.

## Task 2.5: Migrate race_summary_panel.py (4 sites)
**File:** `game/ui/panels/race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/ -v --testmon`

- [x] Add import: `from game.ui.utils import create_section_header`
- [x] Read the file first — verify the x and col_width variables used at each site
- [x] Site 15 (~line 130, "Faction:"): **Stores result** — `self.summary_labels['faction_header'] = create_section_header("Faction:", y, col_width, self.ui_manager, self.panel, x=x)`
- [x] Site 16 (~line 229, "Environment:"): Replace → `create_section_header("Environment:", y, col_width, self.ui_manager, self.panel, x=x)`
- [x] Site 17 (~line 285, "Aptitudes:"): Replace → `create_section_header("Aptitudes:", env_y, col_width, self.ui_manager, self.panel, x=x)`
- [x] Site 18 (~line 318, "Descriptions:"): Replace → `create_section_header("Descriptions:", env_y, col_width, self.ui_manager, self.panel, x=x)`
- [x] Run tests

**Notes:** Summary panel uses multi-column layout — x is variable (col1_x or col3_x), so passed explicitly with `x=x`.

## Phase 2 Completion
- [x] All 19 sites migrated across 5 files
- [x] All tests pass: `pytest tests/unit/ui/ -v`
- [x] Each file imports `create_section_header` from `game.ui.utils`
