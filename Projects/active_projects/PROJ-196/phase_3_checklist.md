# Phase 3: Color Constants + TestLabTheme

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-196 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add 6 common color constants to `colors.py` and create `test_lab/theme.py` with all Test Lab color definitions.

---

## Tasks

### Task 3.1: Add common color constants to colors.py [Simple]
**File:** `game/ui/colors.py`
**Tests:** `pytest tests/unit/ui/test_colors.py -v`

- [ ] Add new section after Scene Backgrounds (after line 90):
  ```python
  # === Common UI Colors ===
  TEXT_LIGHT = (220, 220, 220)       # Primary text
  TEXT_MUTED = (150, 150, 150)       # Muted/hint text
  TEXT_DIM = (100, 100, 100)         # Dim/disabled text
  PANEL_BG = (30, 30, 35)           # Popup/dialog background
  BORDER_LIGHT = (100, 100, 120)    # Active borders
  BORDER_DARK = (80, 80, 90)        # Standard borders
  ```
- [ ] Verify import: `python -c "from game.ui.colors import TEXT_LIGHT, TEXT_MUTED, TEXT_DIM, PANEL_BG, BORDER_LIGHT, BORDER_DARK"`
- [ ] Run tests

**Notes:** Names avoid conflicting with COLORS dict string keys.

---

### Task 3.2: Create `game/ui/screens/test_lab/theme.py` [Medium]
**File:** `game/ui/screens/test_lab/theme.py` (new)
**Tests:** `python -c "from game.ui.screens.test_lab.theme import BG_PRIMARY, TEXT, BORDER, STATUS_PASS"`

- [ ] Create module with PROJ-196 docstring
- [ ] Add imports: `from game.ui.colors import TEST_PASS, TEST_FAIL`
- [ ] **Backgrounds:**
  - `BG_PRIMARY = (20, 20, 25)` — Main screen background
  - `BG_PANEL = (25, 25, 30)` — Panel backgrounds
  - `BG_CONTENT = (30, 30, 35)` — Content area / dialog backgrounds
  - `BG_CATEGORY = (35, 35, 40)` — Category buttons / card backgrounds
  - `BG_ITEM_HOVER = (40, 40, 50)` — Hovered item backgrounds
  - `BG_OVERLAY = (40, 40, 45)` — Progress overlay background
- [ ] **Borders:**
  - `BORDER = (80, 80, 90)` — Standard borders
  - `BORDER_ACTIVE = (100, 100, 120)` — Active/popup borders, scrollbar thumbs
- [ ] **Text:**
  - `TEXT = (220, 220, 220)` — Primary text
  - `TEXT_HEADER = (150, 200, 255)` — Header/accent light blue
  - `TEXT_SECONDARY = (140, 140, 160)` — Labels, secondary info
  - `TEXT_EXPECTED = (180, 200, 255)` — Expected values display
  - `TEXT_WHITE = (255, 255, 255)` — Emphasis / button text
  - `TEXT_MUTED = (180, 180, 180)` — Muted info text
  - `TEXT_DIM = (150, 150, 150)` — Dim / hint text
  - `TEXT_LABEL = (140, 140, 160)` — Same as secondary (alias)
- [ ] **Status:**
  - `STATUS_PASS = TEST_PASS`
  - `STATUS_FAIL = TEST_FAIL`
  - `STATUS_WARNING = (255, 200, 80)` — Orange/gold warnings
  - `STATUS_INFO = (120, 120, 200)` — Blue-gray info
  - `STATUS_HIGHLIGHT = (255, 220, 100)` — Gold highlight
- [ ] **Tags/Filters:**
  - `TAG_ACTIVE_BG = (40, 80, 40)` — Green active tag background
  - `TAG_ACTIVE_BORDER = (80, 150, 80)` — Green active tag border
  - `TAG_ACTIVE_TEXT = (150, 255, 150)` — Green active tag text
  - `TAG_EXCLUDED_BG = (100, 40, 40)` — Red excluded tag background
  - `TAG_EXCLUDED_BORDER = (180, 80, 80)` — Red excluded tag border
  - `TAG_EXCLUDED_TEXT = (255, 150, 150)` — Red excluded tag text
  - `TAG_NORMAL_BG = (50, 50, 60)` — Neutral tag background
  - `TAG_NORMAL_BORDER = (100, 100, 110)` — Neutral tag border
  - `TAG_NORMAL_TEXT = (180, 180, 180)` — Neutral tag text
- [ ] **Tabs:**
  - `TAB_NORMAL = (40, 40, 50)` — Inactive tab
  - `TAB_SELECTED = (60, 80, 120)` — Active tab
  - `TAB_HOVER = (50, 50, 60)` — Hovered tab
- [ ] **Selection:**
  - `SELECTED_BG = (0, 100, 200)` — Selected item highlight
  - `SELECTED_CARD_BG = (55, 100, 150)` — Selected card blue tint
  - `SELECTED_BORDER = (100, 150, 255)` — Selected item border
- [ ] **Buttons:**
  - `BUTTON_BLUE = (60, 120, 200)` — Standard blue button
  - `BUTTON_BLUE_HOVER = (80, 140, 220)` — Blue button hover
  - `BUTTON_BLUE_BORDER = (100, 140, 200)` — Blue button border
  - `BUTTON_GREEN = (40, 60, 40)` — Green action button
  - `BUTTON_GREEN_HOVER = (60, 80, 60)` — Green button hover
  - `BUTTON_GREEN_BORDER = (80, 120, 80)` — Green button border
  - `BUTTON_GREEN_TEXT = (150, 200, 150)` — Green button text
- [ ] **Scrollbar:**
  - `SCROLLBAR_TRACK = (40, 40, 50)` — Track background
  - `SCROLLBAR_THUMB = (100, 100, 120)` — Thumb color
- [ ] **Seed controls:**
  - `SEED_RANDOM = (100, 100, 100)` — Random seed indicator
  - `SEED_FIXED = (100, 140, 100)` — Fixed seed indicator (green-tinted)
  - `SEED_CUSTOM = (100, 180, 255)` — Custom seed indicator (blue)
  - `SEED_CUSTOM_PENDING = (180, 140, 100)` — Custom seed pending (orange)
- [ ] **Section headers (test info panel):**
  - `SECTION_CATEGORY = (200, 150, 100)` — Category section (orange)
  - `SECTION_SUMMARY = (100, 200, 150)` — Summary section (green)
  - `SECTION_CONDITIONS = (150, 200, 255)` — Conditions section (blue)
  - `SECTION_EDGE_CASES = (255, 200, 100)` — Edge cases section (orange)
  - `SECTION_OUTCOME = (100, 255, 150)` — Expected outcome (bright green)
  - `SECTION_CRITERIA = (255, 150, 150)` — Pass criteria (pink)
- [ ] Verify import succeeds

**Notes:**

---

### Task 3.3: Run tests [Simple]
**Tests:** `pytest tests/ --testmon`

- [ ] All tests pass (no behavioral changes — only new modules/constants added)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
