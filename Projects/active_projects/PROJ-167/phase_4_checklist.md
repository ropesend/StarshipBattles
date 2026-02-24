# Phase 4: UI Layer Color Consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-167 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

- [ ] Add the following constant groups after the existing `COLORS` dict:

```python
# === Ship Layer Rendering ===
LAYER_ARMOR = (100, 100, 100)     # Gray
LAYER_OUTER = (200, 50, 50)      # Red
LAYER_INNER = (50, 50, 200)      # Blue
LAYER_CORE = (220, 220, 220)     # Light gray

# === Projectile Colors ===
PROJECTILE_STANDARD = (255, 200, 50)   # Golden yellow
PROJECTILE_MISSILE = (255, 50, 50)     # Red
PROJECTILE_BEAM = (100, 200, 255)      # Light blue

# === HP/Health Status ===
HP_HEALTHY = (0, 255, 0)         # Bright green (>50%)
HP_DAMAGED = (255, 200, 0)       # Yellow (20-50%)
HP_CRITICAL = (255, 50, 50)      # Red (<20%)
HP_DESTROYED = (100, 100, 100)   # Gray (0%)

# === Resource Display ===
RESOURCE_FUEL = (255, 165, 0)    # Orange
RESOURCE_ENERGY = (100, 200, 255) # Light blue
RESOURCE_AMMO = (200, 200, 100)  # Yellowish
RESOURCE_SHIELD = (0, 200, 255)  # Cyan

# === Research Tree Nodes ===
RESEARCH_LOCKED = (80, 80, 90)       # Gray
RESEARCH_AVAILABLE = (50, 100, 180)  # Blue
RESEARCH_COMPLETED = (50, 140, 60)   # Green
RESEARCH_SELECTED = (200, 180, 50)   # Gold
RESEARCH_LINE_UNMET = (60, 65, 75)   # Dark gray
RESEARCH_LINE_MET = (80, 120, 80)    # Muted green
RESEARCH_LINE_NEGATED = (180, 80, 80)    # Red
RESEARCH_LINE_NEGATED_MET = (100, 60, 60) # Dark red
RESEARCH_TEXT = (220, 220, 230)      # Off-white
RESEARCH_CHANCE = (255, 220, 100)    # Gold/yellow
RESEARCH_ALLOCATION = (255, 255, 0)  # Bright yellow

# === Test Lab ===
TEST_PASS = (80, 255, 120)      # Bright green
TEST_FAIL = (255, 80, 80)       # Bright red

# === Scene Backgrounds ===
BG_BATTLE = (10, 10, 20)        # Nearly black (battle + app)
BG_GALAXY = (15, 20, 30)        # Deep dark blue
BG_MENU = (20, 20, 30)          # Dark blue-gray

# === Ship Class Colors (Design Reports) ===
SHIP_CLASS_FIGHTER = (255, 150, 50)   # Orange
SHIP_CLASS_CORVETTE = (100, 200, 100) # Green
SHIP_CLASS_ESCORT = (100, 150, 255)   # Light blue
SHIP_CLASS_DESTROYER = (255, 100, 100) # Red
SHIP_CLASS_CRUISER = (200, 100, 255)  # Purple
SHIP_CLASS_BATTLESHIP = (255, 200, 50) # Yellow
SHIP_CLASS_CARRIER = (150, 255, 200)  # Cyan-green
SHIP_CLASS_DEFAULT = (150, 150, 150)  # Gray

# === Builder Detail Panel (hex for HTML rendering) ===
DETAIL_COMPONENT_NAME = '#FFFF64'   # Yellow-green
DETAIL_COMPONENT_INFO = '#C8C8C8'   # Light gray
DETAIL_TEXT = '#E0E0E0'             # Very light gray

# === Design Stats Panel (hex for HTML rendering) ===
DESIGN_MISSING_REQ = '#ffaa55'     # Orange
DESIGN_REQS_MET = '#88ff88'        # Light green
DESIGN_WARNING = '#ffff88'         # Light yellow
DESIGN_NO_RECS = '#888888'         # Gray

# === Builder Panel Layout ===
BUILDER_ITEM_BG = '#14181f'     # Deep dark
BUILDER_GROUP_BG = '#1a1e26'    # Dark base
BUILDER_TREE_LINE = '#2a3545'   # Dark blue-gray
```

- [ ] Update `__all__` or verify module exports work
- [ ] Verify: `pytest tests/unit/ui/test_colors.py -q` passes
- [ ] Verify: `python -c "from game.ui.colors import LAYER_ARMOR, HP_HEALTHY, RESEARCH_LOCKED"` succeeds

**Notes:**

---

### Task 4.2: Update game_renderer.py [Simple]
**File:** `game/ui/renderer/game_renderer.py`
**Tests:** `pytest tests/unit/ui/ -q -k render`

- [ ] Add import: `from game.ui.colors import LAYER_ARMOR, LAYER_OUTER, LAYER_INNER, LAYER_CORE`
- [ ] Replace `LAYER_COLORS` dict values (lines ~38-41) with imported constants
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.3: Update research_renderer.py [Simple]
**File:** `game/ui/research/research_renderer.py`
**Tests:** `pytest tests/unit/ui/ -q -k research`

- [ ] Add import: `from game.ui.colors import RESEARCH_LOCKED, RESEARCH_AVAILABLE, RESEARCH_COMPLETED, RESEARCH_SELECTED, RESEARCH_LINE_UNMET, RESEARCH_LINE_MET, RESEARCH_LINE_NEGATED, RESEARCH_LINE_NEGATED_MET, RESEARCH_TEXT, RESEARCH_CHANCE, RESEARCH_ALLOCATION`
- [ ] Replace all 11 `COLOR_*` module-level constants (lines ~32-43) with imported constants
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.4: Update battle_panels.py [Simple]
**File:** `game/ui/panels/battle_panels.py`
**Tests:** `pytest tests/unit/ui/ -q -k battle`

- [ ] Add imports for HP_HEALTHY, HP_DAMAGED, HP_CRITICAL, HP_DESTROYED, RESOURCE_FUEL
- [ ] Replace HP bar color tuples with constants where they match
- [ ] Replace fuel color tuples with RESOURCE_FUEL where they match
- [ ] Leave one-off status text colors inline (they're context-specific)
- [ ] Verify: tests pass

**Notes:** Be selective — only replace colors that exactly match the constants. Some battle panel colors are slightly different from the standard palette.

---

### Task 4.5: Update ship_stats_renderer.py [Simple]
**File:** `game/ui/panels/ship_stats_renderer.py`
**Tests:** `pytest tests/unit/ui/ -q -k stats`

- [ ] Add imports for RESOURCE_FUEL, RESOURCE_ENERGY, RESOURCE_AMMO, RESOURCE_SHIELD
- [ ] Replace resource color tuples (lines with fuel orange, energy blue, ammo yellow, shield cyan)
- [ ] Replace HP bar colors if they match HP_HEALTHY/HP_DAMAGED/HP_CRITICAL
- [ ] Verify: tests pass

**Notes:** This file has slightly different HP bar values ((0,200,0) vs (0,255,0)) — check if they should be unified or left distinct.

---

### Task 4.6: Update design_stats_panel.py [Simple]
**File:** `game/ui/panels/design_stats_panel.py`
**Tests:** `pytest tests/unit/ui/ -q -k design_stats`

- [ ] Add import: `from game.ui.colors import DESIGN_MISSING_REQ, DESIGN_REQS_MET, DESIGN_WARNING, DESIGN_NO_RECS`
- [ ] Line ~392: Replace `'#ffaa55'` → `DESIGN_MISSING_REQ`
- [ ] Line ~395: Replace `'#88ff88'` → `DESIGN_REQS_MET`
- [ ] Line ~406: Replace `'#ffff88'` → `DESIGN_WARNING`
- [ ] Line ~409: Replace `'#888888'` → `DESIGN_NO_RECS`
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.7: Update detail_panel.py hex colors [Simple]
**File:** `game/ui/screens/builder/detail_panel.py`
**Tests:** `pytest tests/unit/ui/test_detail_panel*.py -q`

- [ ] Add import: `from game.ui.colors import DETAIL_COMPONENT_NAME, DETAIL_COMPONENT_INFO, DETAIL_TEXT`
- [ ] Line ~130: Replace `'#FFFF64'` → `DETAIL_COMPONENT_NAME`
- [ ] Lines ~131-133: Replace `'#C8C8C8'` → `DETAIL_COMPONENT_INFO`
- [ ] Line ~209: Replace `'#E0E0E0'` → `DETAIL_TEXT`
- [ ] Verify: tests pass

**Notes:** This file already has HINT_* imports from Phase 2. Add new imports alongside.

---

### Task 4.8: Update panel_layout_config.py [Simple]
**File:** `game/ui/screens/builder/panel_layout_config.py`
**Tests:** `pytest tests/unit/ui/ -q -k builder`

- [ ] Add import: `from game.ui.colors import BUILDER_ITEM_BG, BUILDER_GROUP_BG, BUILDER_TREE_LINE`
- [ ] Line ~65: Replace `'#14181f'` → `BUILDER_ITEM_BG`
- [ ] Line ~66: Replace `'#1a1e26'` → `BUILDER_GROUP_BG`
- [ ] Line ~68: Replace `'#2a3545'` → `BUILDER_TREE_LINE`
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.9: Update design_report_panel.py [Simple]
**File:** `game/ui/panels/design_report_panel.py`
**Tests:** `pytest tests/unit/ui/ -q -k report`

- [ ] Add import for ship class color constants
- [ ] Replace ship class color mapping with imported constants
- [ ] Verify: tests pass

**Notes:**

---

### Task 4.10: Update test_lab screen files [Simple]
**File:** Multiple files in `game/ui/screens/test_lab/`
**Tests:** `pytest tests/unit/ui/ -q -k test_lab`

- [ ] Update `test_run_card.py` — replace TEST_PASS/TEST_FAIL colors
- [ ] Update `test_run_details.py` — replace pass/fail indicators
- [ ] Update `screen.py` — replace pass/fail border/text colors
- [ ] Verify: tests pass

**Notes:** Only replace exact matches for TEST_PASS and TEST_FAIL. Leave button state colors (hover, active, etc.) inline — they're context-specific UI states.

---

### Task 4.11: Update battle_ui_service.py [Simple]
**File:** `game/ui/services/battle_ui_service.py`
**Tests:** `pytest tests/unit/ui/ -q -k battle`

- [ ] Add import: `from game.ui.colors import PROJECTILE_STANDARD, PROJECTILE_MISSILE, PROJECTILE_BEAM`
- [ ] Replace projectile color tuples in AttackType mapping
- [ ] Verify: tests pass

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full UI tests: `pytest tests/unit/ui/ -q` — all pass
- [ ] Spot-check: grep for remaining hardcoded hex strings in modified files
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 5
