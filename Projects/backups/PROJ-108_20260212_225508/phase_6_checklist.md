# Phase 6: UI Layer Deduplication

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-108 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Consolidate UI formatting utilities, gallery base class, and column manager base class.
**Findings:** DUP-UI1-001, DUP-UI1-002, DUP-UI1-003, DUP-UI1-005

---

## Tasks

### Task 6.1: Extract shared value formatting utility [Simple]
**File:** `game/ui/screens/test_lab/formatting_utils.py` (NEW)
**Tests:** `pytest tests/unit/ui/test_lab_formatting_utils.py -v`

DUP-UI1-002: `test_run_details.py:_format_value()` (lines 882-901) and `test_run_card.py:_format_value_short()` (lines 213-228) share identical probability detection and formatting logic.

- [x] Create `game/ui/screens/test_lab/formatting_utils.py`
- [x] Implement `format_value(value, precision='full')`:
  - `precision='full'`: probability `{:.2%}`, scientific `{:.6e}`, float `{:.4f}` (details panel behavior)
  - `precision='compact'`: probability `{:.1%}`, scientific `{:.2e}`, float `{:.3f}` (card behavior)
  - Handle None -> "None", int -> str, bool check, integer-like float detection
- [x] Write tests for both precision modes (23 tests)
- [x] Update `test_run_details.py`: replace `_format_value()` with `format_value(value, precision='full')`
  - Import: `from game.ui.screens.test_lab.formatting_utils import format_value`
  - Delete `_format_value()` method (~19 lines removed)
  - Update calls at lines 381, 390
- [x] Update `test_run_card.py`: replace `_format_value_short()` with `format_value(value, precision='compact')`
  - Import: `from game.ui.screens.test_lab.formatting_utils import format_value`
  - Delete `_format_value_short()` method (~15 lines removed)
  - Update calls at lines 151, 152
- [x] Verify: `pytest tests/ -n 12` passes

### Task 6.2: Consolidate empire resource formatting [Simple]
**File:** `game/ui/screens/build_queue_helpers.py`
**Tests:** `pytest tests/ -n 12`

DUP-UI1-003: Resource abbreviation logic (Met/Org/Vap/Rad/Exo) in `build_queue_helpers.py:format_empire_resources()` and `strategy_ui.py` duplicated.

- [x] Found duplication: `strategy_ui.py` line 287 has identical `abbrevs` dict
- [x] Extracted RESOURCE_ABBREVS and RESOURCE_ABBREVS_SHORT constants in build_queue_helpers.py
- [x] Updated strategy_ui.py to import and use RESOURCE_ABBREVS constant
- [x] Updated build_queue_helpers.py functions to use the constants
- [x] Verify: `pytest tests/ -n 12` passes

### Task 6.3: Extract BaseGallery class [Complex]
**File:** `game/ui/panels/base_gallery.py` (NEW)
**Tests:** `pytest tests/unit/ui/test_race_portrait_gallery.py tests/unit/ui/test_race_flag_gallery.py -v`

DUP-UI1-005: `RacePortraitGallery` and `RaceFlagGallery` share ~70% code.

- [x] Read full source of both gallery classes to identify exact shared vs. divergent methods
- [x] Create `game/ui/panels/base_gallery.py` with `BaseGallery` abstract class (240 lines)
- [x] Move shared constructor logic to `BaseGallery.__init__()`:
  - `panel`, `ui_manager`, `race_config`, `on_select_callback`, `_asset_loader`
  - Gallery button list, preview image, scroll container, preview panel
  - Asset cache
- [x] Define template methods (abstract, override in subclasses):
  - `_get_label_text()`, `_get_thumb_size()`, `_get_preview_size()`, `_get_object_id_prefix()`
  - `_get_preview_panel_object_id()`, `_discover_assets()`, `_get_current_selection()`, `_set_selection()`
  - `_update_preview(asset_id)` - subclass-specific preview rendering
- [x] Move shared methods to base class:
  - `_create_content()` (gallery + preview layout)
  - `_populate_gallery()` (button grid with thumbnails)
  - `_sanitize_object_id()` (object ID cleaning)
  - `on_asset_selected()` (update config, callback, refresh preview)
  - `set_from_config()`, `handle_button_click()`
- [x] Update `RacePortraitGallery` to extend `BaseGallery`:
  - Override template methods only (~170 lines, down from ~260)
  - Added legacy compatibility aliases (portrait_buttons, portrait_scroll, portrait_preview_panel)
- [x] Update `RaceFlagGallery` to extend `BaseGallery`:
  - Override template methods only (~183 lines, down from ~270)
  - Added legacy compatibility aliases (flag_buttons, flag_scroll, flag_preview_panel)
- [x] Updated tests to use base class attribute names (asset_buttons, scroll_container, preview_panel)
- [x] Verify: `pytest tests/unit/ui/test_race_portrait_gallery.py -v` passes (15 tests)
- [x] Verify: `pytest tests/unit/ui/test_race_flag_gallery.py -v` passes (15 tests)
- [x] Verify: `pytest tests/ -n 12` passes

**Callers:** `game/ui/screens/race_setup_screen.py` imports both (lines 33-34). No changes needed -
constructor signature unchanged.

### Task 6.4: Extract BaseColumnManager [SKIPPED - Low ROI]
**File:** `game/ui/screens/base_column_manager.py` (NOT CREATED)
**Tests:** N/A

DUP-UI1-001: Two `ColumnManager` classes with identical concepts but different data models.

**Analysis:**
After reading both column managers, the shared code is minimal (~20 lines):
- Fleet `ColumnManager` (column_manager.py): Data-focused, handles value extraction for ship data
- Planet `ColumnManager` (planet_list_columns.py): UI-focused, manages pygame_gui header buttons, sort state

The only truly shared methods are `get_visible_columns()` and `toggle_visibility()` - insufficient
overlap to justify the complexity of a base class with inheritance hierarchy.

- [SKIPPED] Create `game/ui/screens/base_column_manager.py` - Low ROI, different concerns
- [SKIPPED] Update column manager implementations - Not needed

**Decision:** Keep classes separate. The classes serve different purposes and the ~20 lines of
shared code doesn't warrant the abstraction overhead.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (or explicitly skipped with rationale)
- [x] No `_format_value` method in test_run_details.py
- [x] No `_format_value_short` method in test_run_card.py
- [x] `BaseGallery` exists and both galleries extend it
- [x] Task 6.4 SKIPPED - low ROI (documented rationale above)
- [x] `pytest tests/ -n 12` -- full suite passes (8260 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to audit
