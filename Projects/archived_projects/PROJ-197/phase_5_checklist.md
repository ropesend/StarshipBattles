# Phase 5: Ship Panels & Widgets [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Consolidate ship stats, detail panel, JSON panel, and modifier grid

---

## Tasks

### Task 5.1: Consolidate ship_stats_renderer.py [Medium]
**File:** `game/ui/panels/ship_stats_renderer.py` (31 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Add imports from `game.ui.colors`
- [x] Replace bar bg/border → `BAR_BG`, `BAR_BORDER`
- [x] Replace status text `(200, 200, 200)` → `TEXT_ITEM`
- [x] Replace `(255, 50, 50)` → `HP_CRITICAL` (damaged status)
- [x] Replace `(255, 165, 0)` → `STATUS_DERELICT` (no crew)
- [x] Replace `(255, 255, 0)` → `COMPONENT_NO_POWER`
- [x] Replace `(255, 100, 0)` → `COMPONENT_NO_FUEL`
- [x] Normalize HP bar: `(0, 200, 0)` → `HP_HEALTHY`, `(200, 200, 0)` → `HP_DAMAGED`, `(200, 50, 50)` → `HP_CRITICAL`
- [x] Replace `(100, 50, 50)` (3x) → `COMPONENT_INACTIVE_BG`
- [x] Replace `(180, 180, 180)` (6x) → `TEXT_SECONDARY`
- [x] Replace `(150, 150, 255)` → `WEAPON_STATS_TEXT`
- [x] Replace `(150, 150, 200)` → `METADATA_FILE_TEXT`
- [x] Replace `(150, 200, 150)` → `AI_STRATEGY_TEXT`
- [x] Replace `(255, 200, 100)` → `SEEKER_TITLE`
- [x] Replace `(200, 200, 150)` → `SECTION_HEADER_WEAPONS`
- [x] Replace `(200, 200, 100)` → `SECTION_HEADER_COMPONENTS`
- [x] Replace `(100, 255, 100)` biomass in RESOURCE_COLORS dict → `RESOURCE_BIOMASS`
- [x] Verify: `python -c "from game.ui.panels import ship_stats_renderer"`
- [x] Run `pytest tests/ --testmon`

**Notes:** Added ~15 new color constant imports. Added RESOURCE_BIOMASS, WEAPON_INACTIVE, WEAPON_INACTIVE_STATUS, CREW_LOW to colors.py.

### Task 5.2: Consolidate ship_detail_panel.py [Simple]
**File:** `game/ui/panels/ship_detail_panel.py` (11 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Add imports from `game.ui.colors`
- [x] Replace damage colors → `HP_HEALTHY`, `HP_DAMAGED`, `HP_CRITICAL`, `HP_DESTROYED`
- [x] Replace backgrounds → `BAR_BG` and appropriate constants
- [x] Replace `(80, 80, 80)` → `BAR_BORDER`
- [x] Replace `(255, 255, 255)` → (not needed, only placeholder drawing)
- [x] Run `pytest tests/ --testmon`

**Notes:** Updated get_damage_color() to use HP_* constants. Updated _get_scaled_image() placeholder drawing.

### Task 5.3: Consolidate scrollable_json_panel.py [Simple]
**File:** `game/ui/widgets/scrollable_json_panel.py` (20 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Add imports from `game.ui.colors`
- [x] Replace JSON syntax colors with appropriate constants
- [x] Replace diff highlight colors → `DIFF_CHANGED_BG/TEXT`, `DIFF_ADDED_BG/TEXT`, `DIFF_REMOVED_BG/TEXT`
- [x] Replace background/border colors
- [x] Replace text colors → `TEXT_ITEM`, `TEXT_SECONDARY`, `TEXT_DIM`
- [x] Run `pytest tests/ --testmon`

**Notes:** Added JSON_* constants and SCROLLBAR_* constants to colors.py. All 20 tuples consolidated.

### Task 5.4: Consolidate modifier_impact_grid.py [Simple]
**File:** `game/ui/panels/modifier_impact_grid.py` (8 tuples)
**Tests:** `pytest tests/ --testmon`

- [x] Add imports from `game.ui.colors`
- [x] Replace header/row/footer bg tuples
- [x] Replace text `(200, 200, 200)` → `TEXT_ITEM`
- [x] Replace buff/debuff/neutral colors
- [x] Run `pytest tests/ --testmon`

**Notes:** Added MODIFIER_* constants to colors.py. All 8 tuples consolidated.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Zero raw tuples in all 4 files
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
