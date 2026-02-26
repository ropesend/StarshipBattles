# Phase 1: Expand colors.py Palette [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add all new semantic color constants to `game/ui/colors.py`

---

## Tasks

### Task 1.1: Add Common UI Constants [Simple]
**File:** `game/ui/colors.py`
**Tests:** `pytest tests/ --testmon`

These are the most-repeated tuples across multiple files:

- [x] Add `TEXT_SECONDARY = (180, 180, 180)` — label/stat text (used 17+ times across files)
- [x] Add `TEXT_ITEM = (200, 200, 200)` — list item text, neutral content (used 19+ times)
- [x] Add `BAR_BG = (40, 40, 40)` — progress bar / banner dark fill (used 7+ times)
- [x] Add `BAR_BORDER = (80, 80, 80)` — progress bar outline (used 5+ times)
- [x] Add `BG_PANEL_DARK = (20, 25, 35)` — dark panel backgrounds (used 4+ times)
- [x] Add `BG_ROW_ALT = (35, 35, 45)` — alternating row background
- [x] Add `BG_ITEM = (40, 40, 50)` — list item / tag background
- [x] Add `BORDER_PANEL = (60, 60, 80)` — panel divider lines (used 4+ times)
- [x] Add `GRID_LINE = (45, 45, 55)` — grid/separator lines
- [x] Add `GRID_BG = (30, 30, 40)` — grid/card backgrounds

**Notes:** All added to colors.py

### Task 1.2: Add Team Color Constants [Simple]
**File:** `game/ui/colors.py`

Team 1 (blue) and Team 2 (red) colors used in battle_panels, setup_renderer, setup_screen:

- [x] Add section header comment `# === Team Colors (Battle/Setup) ===`
- [x] Add `TEAM_1_TEXT = (100, 200, 255)` — Team 1 titles, accents
- [x] Add `TEAM_1_BG = (30, 50, 70)` — Team 1 item backgrounds
- [x] Add `TEAM_1_BANNER_BG = (40, 60, 80)` — Team 1 banner/header background
- [x] Add `TEAM_1_BORDER = (100, 150, 200)` — Team 1 borders
- [x] Add `TEAM_2_TEXT = (255, 100, 100)` — Team 2 titles, accents
- [x] Add `TEAM_2_BG = (70, 30, 30)` — Team 2 item backgrounds
- [x] Add `TEAM_2_BANNER_BG = (80, 40, 40)` — Team 2 banner/header background
- [x] Add `TEAM_2_BORDER = (200, 100, 100)` — Team 2 borders

**Notes:** All added to colors.py

### Task 1.3: Add Battle Status Constants [Simple]
**File:** `game/ui/colors.py`

- [x] Add section header comment `# === Battle Status ===`
- [x] Add `STATUS_ACTIVE_TEXT = (255, 255, 100)` — active entity text
- [x] Add `STATUS_ACTIVE_BG = (50, 50, 60)` — active entity background
- [x] Add `STATUS_HIT_TEXT = (50, 255, 50)` — hit confirmed text
- [x] Add `STATUS_DESTROYED_TEXT = (255, 50, 50)` — destroyed text (same as HP_CRITICAL)
- [x] Add `STATUS_DERELICT = (255, 165, 0)` — derelict/orange alert
- [x] Add `SEEKER_TITLE = (255, 200, 100)` — seeker monitor title
- [x] Add `DAMAGE_TEXT = (255, 150, 150)` — damage amount text
- [x] Add `TARGET_TEXT = (150, 200, 150)` — target info text

**Notes:** All added to colors.py

### Task 1.4: Add Button Color Constants [Simple]
**File:** `game/ui/colors.py`

- [x] Add section header comment `# === Button Colors ===`
- [x] Add `BTN_NEUTRAL_BG = (60, 60, 80)`
- [x] Add `BTN_NEUTRAL_BORDER = (100, 100, 150)`
- [x] Add `BTN_NEUTRAL_TEXT = (200, 200, 255)`
- [x] Add `BTN_DANGER_BG = (50, 30, 30)`
- [x] Add `BTN_DANGER_HOVER = (60, 40, 40)`
- [x] Add `BTN_DANGER_BORDER = (100, 60, 60)`
- [x] Add `BTN_DANGER_TEXT = (255, 150, 150)`
- [x] Add `BTN_PRIMARY_BG = (50, 150, 50)`
- [x] Add `BTN_PRIMARY_BORDER = (100, 200, 100)`
- [x] Add `BTN_DISABLED_BG = (50, 50, 50)`
- [x] Add `BTN_RETURN_BG = (0, 100, 150)`
- [x] Add `BTN_RETURN_HOVER = (0, 150, 200)`
- [x] Add `BTN_END_BG = (80, 40, 40)`
- [x] Add `BTN_END_BORDER = (150, 80, 80)`
- [x] Add `BTN_END_TEXT = (255, 200, 200)`
- [x] Add `BTN_VICTORY_BG = (50, 80, 120)`
- [x] Add `BTN_VICTORY_BORDER = (100, 150, 200)`

**Notes:** All added to colors.py

### Task 1.5: Add Component Status Constants [Simple]
**File:** `game/ui/colors.py`

- [x] Add section header comment `# === Component Status ===`
- [x] Add `COMPONENT_NO_POWER = (255, 255, 0)` — no power status yellow
- [x] Add `COMPONENT_NO_FUEL = (255, 100, 0)` — no fuel status orange
- [x] Add `COMPONENT_INACTIVE_BG = (100, 50, 50)` — inactive component dark red bg
- [x] Add `WEAPON_STATS_TEXT = (150, 150, 255)` — weapon S:H stats
- [x] Add `SECTION_HEADER_WEAPONS = (200, 200, 150)` — weapons section header
- [x] Add `SECTION_HEADER_COMPONENTS = (200, 200, 100)` — components section header
- [x] Add `AI_STRATEGY_TEXT = (150, 200, 150)` — AI strategy name
- [x] Add `METADATA_FILE_TEXT = (150, 150, 200)` — source file path text

**Notes:** All added to colors.py

### Task 1.6: Add Setup Screen Constants [Simple]
**File:** `game/ui/colors.py`

- [x] Add section header comment `# === Setup Screen ===`
- [x] Add `SETUP_TITLE = (200, 200, 255)`
- [x] Add `SETUP_LABEL_SHIPS = (150, 150, 200)`
- [x] Add `SETUP_LABEL_FORMATIONS = (150, 200, 150)`
- [x] Add `FORMATION_TEXT = (200, 255, 200)`
- [x] Add `FORMATION_BG = (35, 50, 35)`
- [x] Add `FORMATION_BORDER = (80, 120, 80)`
- [x] Add `FORMATION_TEAM_BG = (30, 60, 50)`
- [x] Add `FORMATION_TEAM_BORDER = (100, 200, 150)`
- [x] Add `ITEM_BG = (40, 45, 55)`
- [x] Add `ITEM_BORDER = (80, 80, 100)`
- [x] Add `DROPDOWN_BG = (30, 30, 40)`
- [x] Add `DROPDOWN_BUTTON_BG = (40, 60, 90)`
- [x] Add `DROPDOWN_BUTTON_BORDER = (80, 120, 180)`
- [x] Add `DROPDOWN_BUTTON_TEXT = (150, 200, 255)`
- [x] Add `BTN_CLEAR_BG = (120, 50, 50)`
- [x] Add `BTN_CLEAR_BORDER = (200, 100, 100)`
- [x] Add `BTN_CLEAR_TEXT = (255, 200, 200)`
- [x] Add `BTN_QUICK_BG = (80, 50, 120)`
- [x] Add `BTN_QUICK_BORDER = (150, 100, 200)`
- [x] Add `BTN_QUICK_TEXT = (220, 200, 255)`

**Notes:** All added to colors.py

### Task 1.7: Add Strategy/Galaxy Constants [Simple]
**File:** `game/ui/colors.py`

- [x] Add section header comment `# === Strategy Map ===`
- [x] Add `WARP_LANE = (50, 50, 100)`
- [x] Add `STAR_LABEL = (200, 200, 200)`
- [x] Add `FLEET_SELECTED = (255, 255, 0)`
- [x] Add `PATH_MOVE = (0, 255, 100)`
- [x] Add `PATH_WARP = (255, 50, 50)`
- [x] Add `PATH_LABEL = (200, 200, 255)`
- [x] Add `OVERLAY_PROCESSING = (255, 200, 0)`
- [x] Add `WARPPOINT_FALLBACK = (200, 0, 255)`
- [x] Add `DYSON_FALLBACK = (0, 200, 200)`
- [x] Add `PLANET_FALLBACK = (100, 100, 100)`
- [x] Add section header comment `# === Storm Effects ===`
- [x] Add `STORM_ION = (100, 150, 255)`
- [x] Add `STORM_PLASMA = (255, 100, 100)`
- [x] Add `STORM_GRAVITATIONAL = (180, 100, 255)`
- [x] Add `STORM_RADIATION = (255, 255, 100)`
- [x] Add `STORM_DARK_NEBULA = (150, 150, 150)`
- [x] Add section header comment `# === Star Spectrum ===`
- [x] Add `SPECTRUM_GAMMA = (200, 0, 255)`
- [x] Add `SPECTRUM_XRAY = (148, 0, 211)`
- [x] Add `SPECTRUM_UV = (75, 0, 130)`
- [x] Add `SPECTRUM_BLUE = (0, 0, 255)`
- [x] Add `SPECTRUM_GREEN = (0, 255, 0)`
- [x] Add `SPECTRUM_RED = (255, 0, 0)`
- [x] Add `SPECTRUM_INFRARED = (139, 0, 0)`
- [x] Add `SPECTRUM_MICROWAVE = (160, 82, 45)`
- [x] Add `SPECTRUM_RADIO = (128, 128, 128)`
- [x] Add section header comment `# === Atmospheric Gases ===`
- [x] Add `GAS_N2 = (173, 216, 230)`
- [x] Add `GAS_O2 = (0, 0, 255)`
- [x] Add `GAS_CO2 = (100, 100, 100)`
- [x] Add `GAS_H2O = (0, 0, 139)`
- [x] Add `GAS_CH4 = (255, 165, 0)`
- [x] Add `GAS_H2 = (255, 192, 203)`
- [x] Add `GAS_HE = (255, 255, 255)`
- [x] Add `GAS_AR = (128, 0, 128)`
- [x] Add `GAS_SO2 = (255, 255, 0)`
- [x] Add `GAS_UNKNOWN = (100, 150, 100)`

**Notes:** All added to colors.py

### Task 1.8: Add Planet & Vehicle Type Constants [Simple]
**File:** `game/ui/colors.py`

- [x] Add section header comment `# === Planet Types ===`
- [x] Add `PLANET_CONTINENTAL = (70, 130, 70)`
- [x] Add `PLANET_ARID = (180, 140, 80)`
- [x] Add `PLANET_PELAGIC = (50, 80, 180)`
- [x] Add `PLANET_MAGMA = (200, 50, 30)`
- [x] Add `PLANET_CRYO = (180, 200, 220)`
- [x] Add `PLANET_BARREN = (130, 130, 130)`
- [x] Add `PLANET_JOVIAN = (200, 160, 100)`
- [x] Add `PLANET_ICE_GIANT = (100, 150, 200)`
- [x] Add `PLANET_CHTHONIAN = (100, 80, 60)`
- [x] Add `PLANET_ICE_DWARF = (200, 210, 230)`
- [x] Add `PLANET_PLANETOID = (90, 90, 90)`
- [x] Add `PLANET_TERRESTRIAL = (100, 150, 200)`
- [x] Add `PLANET_GAS_GIANT = (200, 150, 100)`
- [x] Add `PLANET_ICE = (150, 200, 255)`
- [x] Add `PLANET_ROCKY = (150, 100, 80)`
- [x] Add `PLANET_OCEANIC = (50, 100, 200)`
- [x] Add section header comment `# === Vehicle Types ===`
- [x] Add `VEHICLE_SHIP = (80, 100, 180)`
- [x] Add `VEHICLE_FIGHTER = (180, 180, 80)`
- [x] Add `VEHICLE_STATION = (180, 100, 80)`
- [x] Add `VEHICLE_COMPLEX = (80, 180, 100)`
- [x] Add section header comment `# === Resource Placeholders ===`
- [x] Add `RESOURCE_METALS = (192, 192, 192)`
- [x] Add `RESOURCE_ORGANICS = (80, 180, 80)`
- [x] Add `RESOURCE_VAPORS = (100, 150, 220)`
- [x] Add `RESOURCE_RADIOACTIVES = (220, 180, 50)`
- [x] Add `RESOURCE_EXOTICS = (180, 80, 200)`

**Notes:** All added to colors.py

### Task 1.9: Add Remaining Misc Constants [Simple]
**File:** `game/ui/colors.py`

- [x] Add section header comment `# === Battle HUD ===`
- [x] Add `SPEED_PAUSED = (255, 100, 100)`
- [x] Add `SPEED_SLOWMO = (255, 200, 100)`
- [x] Add `SPEED_FAST = (100, 255, 100)`
- [x] Add `HUD_TEXT = (180, 180, 180)`
- [x] Add section header comment `# === Diff Viewer ===`
- [x] Add `DIFF_CHANGED_BG = (60, 50, 20)`
- [x] Add `DIFF_CHANGED_TEXT = (255, 220, 100)`
- [x] Add `DIFF_ADDED_BG = (20, 50, 30)`
- [x] Add `DIFF_ADDED_TEXT = (100, 255, 150)`
- [x] Add `DIFF_REMOVED_BG = (50, 20, 20)`
- [x] Add `DIFF_REMOVED_TEXT = (255, 120, 120)`
- [x] Add section header comment `# === Formation Editor ===`
- [x] Add `FORMATION_GRID = (45, 45, 55)`
- [x] Add `FORMATION_AXIS = (60, 60, 70)`
- [x] Add `FORMATION_ARROW = (100, 200, 255)`
- [x] Add `FORMATION_ARROW_SELECTED = (255, 255, 100)`
- [x] Add `FORMATION_FIXED = (100, 255, 100)`
- [x] Add `FORMATION_FIXED_SELECTED = (200, 255, 200)`
- [x] Add section header comment `# === Weapon Renderer ===`
- [x] Add `WEAPON_BAR_BEAM = (40, 80, 40)`
- [x] Add `WEAPON_BAR_PROJECTILE = (80, 60, 40)`
- [x] Add `WEAPON_BAR_SEEKER = (80, 40, 80)`
- [x] Add `WEAPON_ACCURACY_HIGH = (0, 200, 0)`
- [x] Add `WEAPON_ACCURACY_MED = (200, 100, 0)`
- [x] Add `WEAPON_ACCURACY_LOW = (200, 50, 50)`
- [x] Add `WEAPON_LABEL = (200, 200, 100)`
- [x] Add `WEAPON_RANGE_LABEL = (150, 150, 200)`
- [x] Add `WEAPON_ARC = (200, 150, 50)`

Final verification:
- [x] Verify file is syntactically valid: `python -c "import game.ui.colors"`
- [x] Run `pytest tests/ --testmon`

**Notes:** All added. File valid. Tests pass (3161 UI tests)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
