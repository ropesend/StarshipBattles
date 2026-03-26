# Phase 3: Consolidate Damage Color Call Sites

## Task 3.1: Replace ship_stats_renderer.get_hp_bar_color [Simple]
**File:** `game/ui/panels/ship_stats_renderer.py`
**Tests:** `pytest tests/ --testmon`
- [x] Import `get_damage_color` from `game.ui.utils.formatters`
- [x] Replace `get_hp_bar_color` function body with delegation to `get_damage_color` (keeping COMPONENT_INACTIVE_BG for inactive case)
- [x] Update all call sites within the file
- [x] Verify existing callers of `get_hp_bar_color` are updated (grep for imports)
- [x] Run tests
**Notes:** `get_hp_bar_color` kept as thin wrapper for COMPONENT_INACTIVE_BG case. Updated boundary test at 50% (now HEALTHY not DAMAGED).

## Task 3.2: Replace ship_detail_panel.get_damage_color [Simple]
**File:** `game/ui/panels/ship_detail_panel.py`
**Tests:** `pytest tests/ --testmon`
- [x] Import `get_damage_color` from `game.ui.utils.formatters`
- [x] Remove local `get_damage_color` function
- [x] Verify no other files import from ship_detail_panel.get_damage_color (they do, but the re-export still works)
- [x] Run tests
**Notes:** Removed local function, import from formatters is at module level so `from game.ui.panels.ship_detail_panel import get_damage_color` still works. Updated tests in test_ship_detail_panel.py and test_ship_instance_damage.py to match new thresholds (>=50% HEALTHY, 25-49% DAMAGED, <25% CRITICAL). Removed unused `Tuple` import.

## Task 3.3: Run full regression [Simple]
- [x] Run: `pytest tests/ --testmon`
**Notes:** 56 affected tests, all passing.
