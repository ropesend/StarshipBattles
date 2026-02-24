# Phase 4: UI Layer Color Consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-167 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add categorized constants to `game/ui/colors.py` and update UI files to use them

---

## Approach

This phase adds semantic color constants to the existing `game/ui/colors.py` file. Colors are organized by feature area. Each task updates one file to use the new constants.

**Priority order:** Files with the most hardcoded colors first, then diminishing returns.

**Note:** Not every inline color needs to move. One-off rendering colors (collision radius overlays, dynamic interpolations, alpha blends) are fine to leave inline. Focus on **repeated semantic colors** that appear in multiple files or have clear meaning.

---

## Tasks

### Task 4.1: Extend game/ui/colors.py with semantic constants [Medium]
**File:** `game/ui/colors.py`
**Tests:** `pytest tests/unit/ui/test_colors.py -q`

- [x] Add the following constant groups after the existing `COLORS` dict
- [x] Update `__all__` or verify module exports work
- [x] Verify: `pytest tests/unit/ui/test_colors.py -q` passes
- [x] Verify: `python -c "from game.ui.colors import LAYER_ARMOR, HP_HEALTHY, RESEARCH_LOCKED"` succeeds

**Notes:** Added 50+ semantic color constants organized by category

---

### Task 4.2: Update game_renderer.py [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** `pytest tests/unit/ui/ -q -k render`

- [x] Add import: `from game.ui.colors import LAYER_ARMOR, LAYER_OUTER, LAYER_INNER, LAYER_CORE`
- [x] Replace `LAYER_COLORS` dict values (lines ~38-41) with imported constants
- [x] Verify: tests pass

**Notes:** Complete

---

### Task 4.3: Update research_renderer.py [Simple]
**File:** `game/ui/research/research_renderer.py`
**Tests:** `pytest tests/unit/ui/ -q -k research`

- [x] Add import for all RESEARCH_* constants
- [x] Replace all 11 `COLOR_*` module-level constants with imported constants
- [x] Verify: tests pass

**Notes:** Complete

---

### Task 4.4: Update battle_panels.py [Simple]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/ -q -k battle`

- [x] Add imports for HP_HEALTHY, HP_DAMAGED, HP_CRITICAL, RESOURCE_FUEL
- [x] Replace HP bar color tuples with constants where they match
- [x] Replace fuel color tuples with RESOURCE_FUEL where they match
- [x] Leave one-off status text colors inline (they're context-specific)
- [x] Verify: tests pass

**Notes:** Complete - replaced exact matches only

---

### Task 4.5: Update ship_stats_renderer.py [Simple]
**File:** `game/ui/panels/ship_stats_renderer.py`
**Tests:** `pytest tests/unit/ui/ -q -k stats`

- [x] Add imports for RESOURCE_FUEL, RESOURCE_ENERGY, RESOURCE_AMMO, RESOURCE_SHIELD, HP_HEALTHY, HP_DAMAGED, HP_CRITICAL
- [x] Replace resource color tuples in RESOURCE_COLORS dict
- [x] Replace shield bar color with RESOURCE_SHIELD
- [x] Replace HP bar colors with HP_* constants
- [x] Verify: tests pass

**Notes:** Left get_hp_bar_color function colors unchanged - they use different values

---

### Task 4.6: Update design_stats_panel.py [Simple]
**File:** `game/ui/panels/design_stats_panel.py`
**Tests:** `pytest tests/unit/ui/ -q -k design_stats`

- [x] Add import: `from game.ui.colors import DESIGN_MISSING_REQ, DESIGN_REQS_MET, DESIGN_WARNING, DESIGN_NO_RECS`
- [x] Replace `'#ffaa55'` -> `DESIGN_MISSING_REQ`
- [x] Replace `'#88ff88'` -> `DESIGN_REQS_MET`
- [x] Replace `'#ffff88'` -> `DESIGN_WARNING`
- [x] Replace `'#888888'` -> `DESIGN_NO_RECS`
- [x] Verify: tests pass

**Notes:** Complete

---

### Task 4.7: Update detail_panel.py hex colors [Simple]
**File:** `game/ui/screens/builder/detail_panel.py`
**Tests:** `pytest tests/unit/ui/test_detail_panel*.py -q`

- [x] Add import: `from game.ui.colors import DETAIL_COMPONENT_NAME, DETAIL_COMPONENT_INFO, DETAIL_TEXT`
- [x] Replace `'#FFFF64'` -> `DETAIL_COMPONENT_NAME`
- [x] Replace `'#C8C8C8'` -> `DETAIL_COMPONENT_INFO`
- [x] Replace `'#E0E0E0'` -> `DETAIL_TEXT`
- [x] Verify: tests pass

**Notes:** Complete - added alongside existing HINT_* imports

---

### Task 4.8: Update panel_layout_config.py [Simple]
**File:** `game/ui/screens/builder/panel_layout_config.py`
**Tests:** `pytest tests/unit/ui/ -q -k builder`

- [x] Add import: `from game.ui.colors import BUILDER_ITEM_BG, BUILDER_GROUP_BG, BUILDER_TREE_LINE`
- [x] Replace `'#14181f'` -> `BUILDER_ITEM_BG`
- [x] Replace `'#1a1e26'` -> `BUILDER_GROUP_BG`
- [x] Replace `'#2a3545'` -> `BUILDER_TREE_LINE`
- [x] Verify: tests pass

**Notes:** Complete

---

### Task 4.9: Update design_report_panel.py [Simple]
**File:** `game/ui/panels/design_report_panel.py`
**Tests:** `pytest tests/unit/ui/ -q -k report`

- [x] Add import for ship class color constants
- [x] Replace ship class color mapping with imported constants
- [x] Verify: tests pass

**Notes:** Complete

---

### Task 4.10: Update test_lab screen files [Simple]
**File:** Multiple files in `game/ui/screens/test_lab/`
**Tests:** `pytest tests/unit/ui/ -q -k test_lab`

- [x] Update `test_run_card.py` — replace TEST_PASS/TEST_FAIL colors
- [x] Update `test_run_details.py` — replace pass/fail indicators
- [x] Update `screen.py` — replace pass/fail border/text colors
- [x] Verify: tests pass

**Notes:** Complete - left warning colors (yellow/orange) inline as they're unique

---

### Task 4.11: Update battle_ui_service.py [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/ -q -k battle`

- [x] Add import: `from game.ui.colors import PROJECTILE_STANDARD, PROJECTILE_MISSILE, PROJECTILE_BEAM`
- [x] Replace projectile color tuples in AttackType mapping
- [x] Verify: tests pass

**Notes:** Complete

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full UI tests: `pytest tests/unit/ui/ -q` — 2827 passed
- [x] Spot-check: grep for remaining hardcoded hex strings in modified files
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 5
