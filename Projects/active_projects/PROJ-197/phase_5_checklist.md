# Phase 5: Ship Panels & Widgets [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate ship stats, detail panel, JSON panel, and modifier grid

---

## Tasks

### Task 5.1: Consolidate ship_stats_renderer.py [Medium]
**File:** `game/ui/panels/ship_stats_renderer.py` (31 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Add imports from `game.ui.colors`
- [ ] Replace bar bg/border → `BAR_BG`, `BAR_BORDER`
- [ ] Replace status text `(200, 200, 200)` → `TEXT_ITEM`
- [ ] Replace `(255, 50, 50)` → `HP_CRITICAL` (damaged status)
- [ ] Replace `(255, 165, 0)` → `STATUS_DERELICT` (no crew)
- [ ] Replace `(255, 255, 0)` → `COMPONENT_NO_POWER`
- [ ] Replace `(255, 100, 0)` → `COMPONENT_NO_FUEL`
- [ ] Normalize HP bar: `(0, 200, 0)` → `HP_HEALTHY`, `(200, 200, 0)` → `HP_DAMAGED`, `(200, 50, 50)` → `HP_CRITICAL`
- [ ] Replace `(100, 50, 50)` (3x) → `COMPONENT_INACTIVE_BG`
- [ ] Replace `(180, 180, 180)` (6x) → `TEXT_SECONDARY`
- [ ] Replace `(150, 150, 255)` → `WEAPON_STATS_TEXT`
- [ ] Replace `(150, 150, 200)` → `METADATA_FILE_TEXT`
- [ ] Replace `(150, 200, 150)` → `AI_STRATEGY_TEXT`
- [ ] Replace `(255, 200, 100)` → `SEEKER_TITLE`
- [ ] Replace `(200, 200, 150)` → `SECTION_HEADER_WEAPONS`
- [ ] Replace `(200, 200, 100)` → `SECTION_HEADER_COMPONENTS`
- [ ] Replace `(100, 255, 100)` biomass in RESOURCE_COLORS dict
- [ ] Verify: `python -c "from game.ui.panels import ship_stats_renderer"`
- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 5.2: Consolidate ship_detail_panel.py [Simple]
**File:** `game/ui/panels/ship_detail_panel.py` (11 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Add imports from `game.ui.colors`
- [ ] Replace damage colors → `HP_HEALTHY`, `HP_DAMAGED`, `HP_CRITICAL`, `HP_DESTROYED`
- [ ] Replace backgrounds → `BAR_BG` and appropriate constants
- [ ] Replace `(80, 80, 80)` → `BAR_BORDER`
- [ ] Replace `(255, 255, 255)` → `WHITE`
- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 5.3: Consolidate scrollable_json_panel.py [Simple]
**File:** `game/ui/widgets/scrollable_json_panel.py` (20 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Add imports from `game.ui.colors`
- [ ] Replace JSON syntax colors with appropriate constants
- [ ] Replace diff highlight colors → `DIFF_CHANGED_BG/TEXT`, `DIFF_ADDED_BG/TEXT`, `DIFF_REMOVED_BG/TEXT`
- [ ] Replace background/border colors
- [ ] Replace text colors → `TEXT_ITEM`, `TEXT_SECONDARY`, `TEXT_DIM`
- [ ] Run `pytest tests/ --testmon`

**Notes:**

### Task 5.4: Consolidate modifier_impact_grid.py [Simple]
**File:** `game/ui/panels/modifier_impact_grid.py` (8 tuples)
**Tests:** `pytest tests/ --testmon`

- [ ] Add imports from `game.ui.colors`
- [ ] Replace header/row/footer bg tuples
- [ ] Replace text `(200, 200, 200)` → `TEXT_ITEM`
- [ ] Replace buff/debuff/neutral colors
- [ ] Run `pytest tests/ --testmon`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Zero raw tuples in all 4 files
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
