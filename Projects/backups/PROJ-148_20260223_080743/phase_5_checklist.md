# Phase 5: UI-Screens

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-148 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Screens module (7 findings, 1 critical)
**Priority:** High

---

## Tasks

### Task 5.1: DUP-UI1-001 - Duplicate ColumnManager Classes [Medium]
**File:** `game/ui/screens/column_manager.py`, `game/ui/screens/planet_list_columns.py`
**Tests:** N/A - documented as acceptable

- [x] Investigate the issue at the specified location
- [x] Document finding - no code change needed
- [x] Verify: existing tests passing

**Notes:** Two ColumnManager classes serve DIFFERENT domains:
- `column_manager.py`: Fleet report columns with `get_column_value()` for ShipInstance extraction
- `planet_list_columns.py`: Planet list columns with sorting state, header UI buttons
PROJ-108 explicitly SKIPPED BaseColumnManager extraction as low ROI. Classes have different responsibilities - extracting base class would add artificial coupling without meaningful code reduction.

### Task 5.2: DUP-UI1-003 - Duplicate HP Color Calculation Logic [Simple]
**File:** `game/ui/panels/ship_stats_renderer.py`, `game/ui/panels/ship_detail_panel.py`
**Tests:** N/A - documented as intentional variation

- [x] Investigate the issue at the specified location
- [x] Document finding - no code change needed
- [x] Verify: existing tests passing

**Notes:** Two HP color functions with INTENTIONALLY different thresholds:
- `get_hp_bar_color(hp_pct, is_active)`: Battle UI - thresholds 0.5/0.2 (urgent feedback)
- `get_damage_color(hp_percentage)`: Strategy UI - thresholds 0.75/0.5 (fine-grained damage)
Battle mode needs more urgency (red at 20%). Strategy mode shows detailed damage assessment (yellow at 75%). Both have comprehensive tests confirming behavior.

### Task 5.3: DUP-UI1-004 - Duplicate Number Magnitude Formatting [Simple]
**File:** `game/ui/screens/test_lab/formatting_utils.py`
**Tests:** N/A - already centralized

- [x] Investigate the issue at the specified location
- [x] Document finding - ALREADY FIXED in PROJ-108
- [x] Verify: existing tests passing

**Notes:** PROJ-108 created `formatting_utils.py` with `format_value()` function to centralize number formatting. This finding is ALREADY RESOLVED - no further action needed.

### Task 5.4: DUP-UI1-005 - RaceThemeGallery Does Not Extend BaseGallery [Medium]
**File:** `game/ui/panels/race_theme_gallery.py`, `game/ui/panels/base_gallery.py`
**Tests:** N/A - documented as acceptable

- [x] Investigate the issue at the specified location
- [x] Document finding - no code change needed
- [x] Verify: existing tests passing

**Notes:** RaceThemeGallery has DIFFERENT behavior that doesn't fit BaseGallery:
- BaseGallery: Asset selection with scrolling thumbnails + large preview panel
- RaceThemeGallery: Button list with inline ship preview images, no preview panel
BaseGallery (PROJ-108) extracted shared code from RacePortraitGallery and RaceFlagGallery which have identical structure. RaceThemeGallery uses different UI pattern - forcing it into BaseGallery would require violating the abstraction.

### Task 5.5: DUP-UI1-002 - Duplicate draw_stat_bar Implementations [Simple]
**File:** `game/ui/panels/battle_panels.py`, `game/ui/panels/ship_stats_renderer.py`
**Tests:** N/A - already centralized

- [x] Investigate the issue at the specified location
- [x] Document finding - ALREADY FIXED
- [x] Verify: existing tests passing

**Notes:** `BattlePanel.draw_stat_bar()` is a CONVENIENCE METHOD that delegates to `ship_stats_renderer.draw_stat_bar()`:
```python
def draw_stat_bar(self, surface, x, y, width, height, pct, color):
    """Draw a progress bar - delegates to extracted function."""
    draw_stat_bar(surface, x, y, width, height, pct, color)
```
This IS proper centralization - the base class method provides consistent interface for subclasses.

### Task 5.6: DUP-UI1-006 - Duplicate Portrait Loading Logic [Simple]
**File:** `game/ui/screens/design_image_helper.py`
**Tests:** N/A - already centralized

- [x] Investigate the issue at the specified location
- [x] Document finding - ALREADY CENTRALIZED
- [x] Verify: existing tests passing

**Notes:** `design_image_helper.py` provides centralized portrait loading:
- `load_portrait_thumbnail()`: Cached portrait image loading with fallback
- `load_topdown_thumbnail()`: Cached top-down skin loading with scaling
These are the canonical functions for design image loading. No duplication exists.

### Task 5.7: DUP-UI1-008 - Filter/Sort Pattern Duplication [Medium]
**File:** Multiple UI screens (planet_list, fleet_report, design_selector, etc.)
**Tests:** N/A - documented as acceptable

- [x] Investigate the issue at the specified location
- [x] Document finding - no code change needed
- [x] Verify: existing tests passing

**Notes:** Filter/sort patterns across screens handle DIFFERENT data types:
- `planet_list_filters.py`: Planet filtering by owner, star, features
- `fleet_report_window.py`: Ship filtering by status, type
- `design_selector_window.py`: Design filtering by class, theme
Each has unique filter criteria and sort keys specific to domain data. PROJ-108 assessed similar patterns and concluded extraction would add complexity without proportional benefit.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
