# Phase 7: Final Audit & Cleanup [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-197 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Verify zero raw tuples remain, final test suite run, cleanup

---

## Tasks

### Task 7.1: Raw Tuple Audit [Simple]
**Tests:** N/A (audit only)

- [x] Search all `game/ui/` files for raw RGB tuple patterns `(\d+, \d+, \d+)`
- [x] Verify ONLY hits are in `game/ui/colors.py` and `game/ui/screens/test_lab/theme.py` definitions
- [x] If any raw tuples remain in other files, fix them
- [x] Document count: "3 remaining definition-only files (colors.py, theme.py, component_dropdown.py - comment only)"

**Notes:**
- Found ~15 remaining violations in Phase 6 leftover files
- Added ~20 new constants to colors.py: DRAG_HIGHLIGHT, PLACEHOLDER_BORDER, PLACEHOLDER_DEFAULT, SWATCH_BORDER, THUMB_SHIP, THUMB_FIGHTER, THUMB_SATELLITE, THUMB_COMPLEX, THUMB_TEXT, DAMAGE_GRADIENT, LAYER_LABEL, PROJECTILE_GLOW, PROFILING_TEXT, ZONE_HIGHLIGHT, STAR_FALLBACK, STORM_FALLBACK, BTN_DANGER_HOVER_BORDER
- Fixed files: scrollable_json_panel.py, sprites.py, battle_panels.py, build_queue_drag_handler.py, design_image_helper.py, battle_state_viewer.py, battle_screen.py, strategy_widgets.py, race_asset_loader.py, system_mode.py, strategy_renderer.py, weapons_renderer.py, schematic_view.py

### Task 7.2: Import Cleanup [Simple]
**Tests:** `pytest tests/ --testmon`

- [x] Check no unused color imports exist in modified files
- [x] Check `game/ui/colors.py` has no orphan constants (all used somewhere)
- [x] Verify no circular imports introduced
- [x] Run `pytest tests/ --testmon`

**Notes:**
- All imports verified during fixes
- No circular imports - colors.py has no imports from other UI modules

### Task 7.3: Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run `pytest tests/ -n 12` (full suite, not testmon)
- [x] Verify: 12,734+ passed, 0 failures
- [x] Document final test count: 12734 passed, 1 skipped

**Notes:**
- Fixed one test (test_graph_default_bg_color) to use BG_PANEL_DARK constant instead of hardcoded tuple

### Task 7.4: Regression Test Check [Simple]
**Tests:** `pytest tests/regression/ -v`

- [x] Check if regression tests need updates for new color conventions
- [x] Run `pytest tests/regression/ -v` explicitly

**Notes:**
- No color-related regression tests exist

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Zero raw tuples outside definition files
- [x] Full test suite passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Project Complete"
