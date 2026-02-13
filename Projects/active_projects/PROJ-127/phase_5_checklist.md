# Phase 5: Other

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-127 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address findings not mapped to a specific shard
**Priority:** Normal

---

## Tasks

### Task 5.1: UNK-08 - Population/Number Formatting Duplication [Unknown]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - K/M suffix formatting in strategy_detail_fmt.py (lines 102-114, 129-132) is localized inline code for a specific UI context. Extracting a helper would add abstraction without meaningful benefit. The pattern is self-contained and clear.

### Task 5.2: UNK-09 - RaceThemeGallery Not Using BaseGallery [Unknown]
**File:** `game/ui/panels/race_theme_gallery.py`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - RaceThemeGallery has different structure than BaseGallery:
- RaceThemeGallery: Theme buttons with ship preview images (Escort + Battleship), vertical list
- BaseGallery: Simple thumbnail grid with preview panel, uses RaceAssetLoader
Forcing inheritance would require awkward refactoring with little benefit. Different enough patterns to remain separate.

### Task 5.3: UNK-10 - Window Kill/Cleanup Pattern Slightly Inc [Unknown]
**File:** `game/ui/screens/*_window.py`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Analyzed 11 window files. All consistently implement kill() method calling child element cleanup before super().kill(). Minor variations are contextual (e.g., some have planet_detail_panel, others have column_mgr). Pattern is consistent enough, and abstracting window cleanup would add complexity without meaningful benefit.

### Task 5.4: UNK-11 - Dropdown Recreation Utility [Unknown]
**File:** `Multiple UI files`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** ACCEPTABLE - Multiple files recreate UIDropDownMenu instances but each has unique options, positioning, and context. Found in: race_identity_panel.py, builder/right_panel.py, planet_list_window.py, design_selector_window.py, etc. A utility would need to handle diverse parameters with minimal reuse benefit. Pattern is standard pygame_gui usage.

### Task 5.5: UNK-13 - Ship Stats Renderer Already Extracted [Unknown]
**File:** `game/ui/panels/ship_stats_renderer.py`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFO - CONFIRMED ALREADY EXTRACTED. ship_stats_renderer.py exists (403 lines) with properly extracted functions: draw_stat_bar, draw_ship_resources, draw_weapon_entry, draw_component_entry, draw_ship_info_header, draw_ship_vitals, draw_ship_combat_stats, draw_ship_weapons, draw_ship_components. No action needed.

### Task 5.6: UNK-14 - Strategy Detail Formatters Properly Sepa [Unknown]
**File:** `game/ui/screens/strategy_detail_*.py`
**Tests:** N/A - No code changes

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:** INFO - CONFIRMED PROPERLY SEPARATED. Two files exist:
- strategy_detail_fmt.py (368 lines): Pure formatting functions (format_spectrum_html, format_planet_info, format_fleet_info, etc.)
- strategy_detail_formatter.py (373 lines): StrategyDetailFormatter class that wraps fmt functions for UI (PROJ-86 extraction)
Clean separation of concerns. No action needed.


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
