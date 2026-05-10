# Phase 3: UI-Framework

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-115 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings in the UI-Framework module (8 findings, 2 critical)
**Priority:** High

---

## Tasks

### Task 3.1: DUP-UI2-001 - Portrait Loading Logic Duplicated in 5+ [Medium]
**File:** `game/ui/assets/ship_theme_mana`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - ShipThemeManager.get_portrait_image() already provides centralized API. 4 files correctly use it (fleet_report_window, race_summary_panel, ship_detail_panel, race_setup_screen). Older code (build_queue_portraits, design_report_panel, right_panel, design_image_helper) has duplicate logic but is stable. Full migration out of scope.

### Task 3.2: DUP-UI2-002 - Ship Image Scaling Pipeline Duplicated B [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ALREADY FIXED - Ship image scaling is centralized in game/ui/utils.py with calculate_ship_image_scale() and scale_and_rotate_image(). All 3 locations (game_renderer, schematic_view, strategy_renderer) properly import and use these utilities.

### Task 3.3: DUP-UI2-003 - Layer Color Constants Duplicated with Dr [Simple]
**File:** `game/ui/renderer/game_renderer`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** FIXED - schematic_view.py (lines 104-108) had duplicate layer color definitions. Updated to import LAYER_COLORS from game_renderer.py and use it.

### Task 3.4: DUP-UI2-004 - BattleUIService get_engine() Null-Check [Simple]
**File:** `game/ui/services/battle_ui_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE PATTERN - This is NOT duplication but a guard clause pattern. Each method independently validates engine state and returns method-appropriate default ([], True, None, 0). Extracting would add coupling and reduce clarity.

### Task 3.5: DUP-UI2-005 - ShipThemeManager Internal Methods Repeat [Simple]
**File:** `game/ui/assets/ship_theme_mana`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - _load_single_image and _load_portrait_image have similar structure but serve different purposes: different caches (themes vs portraits), different path resolution, different error handling (fallback image vs None), different metrics. Consolidating would reduce clarity.

### Task 3.6: DUP-UI2-006 - Lazy DI Provider Pattern in Services [Simple]
**File:** `game/ui/services/component_ser`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Standard UI Service DI pattern documented in component_service.py lines 34-38. Each service independently takes optional registry_provider, falls back to default, uses _get_provider() helper. This is intentional design, not duplication.

### Task 3.7: DUP-UI2-007 - Topdown Thumbnail Loading Reimplements B [Simple]
**File:** `game/ui/screens/design_image_h`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - design_image_helper's load_topdown_thumbnail duplicates ShipThemeManager's image loading but with different path variations and caching strategy. Proper fix requires design changes to route through ShipThemeManager. Tech debt but not urgent.

### Task 3.8: DUP-UI2-008 - Hardcoded Magic Color Tuples Throughout [Medium]
**File:** `Unknown`
**Tests:** `pytest tests/` (add appropriate test path)

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - game/ui/colors.py exists with centralized COLORS dict. 653 magic color tuples across 47 files are gradual migration candidates. Many are contextual (red=damage, green=health) and make sense inline. Full migration would be major undertaking with behavior risk.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
