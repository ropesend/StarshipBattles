# Phase 6: UI Layer Deduplication

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-108 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate UI formatting utilities, gallery base class, and column manager base class.
**Findings:** DUP-UI1-001, DUP-UI1-002, DUP-UI1-003, DUP-UI1-005

---

## Tasks

### Task 6.1: Extract shared value formatting utility [Simple]
**File:** `game/ui/screens/test_lab/formatting_utils.py` (NEW)
**Tests:** `pytest tests/unit/ui/test_lab_formatting_utils.py -v`

DUP-UI1-002: `test_run_details.py:_format_value()` (lines 882-901) and `test_run_card.py:_format_value_short()` (lines 213-228) share identical probability detection and formatting logic.

- [ ] Create `game/ui/screens/test_lab/formatting_utils.py`
- [ ] Implement `format_value(value, precision='full')`:
  - `precision='full'`: probability `{:.2%}`, scientific `{:.6e}`, float `{:.4f}` (details panel behavior)
  - `precision='compact'`: probability `{:.1%}`, scientific `{:.2e}`, float `{:.3f}` (card behavior)
  - Handle None -> "None", int -> str, bool check, integer-like float detection
- [ ] Write tests for both precision modes
- [ ] Update `test_run_details.py`: replace `_format_value()` with `format_value(value, precision='full')`
  - Import: `from game.ui.screens.test_lab.formatting_utils import format_value`
  - Delete `_format_value()` method (lines 882-901)
  - Update calls at lines 381, 390
- [ ] Update `test_run_card.py`: replace `_format_value_short()` with `format_value(value, precision='compact')`
  - Import: `from game.ui.screens.test_lab.formatting_utils import format_value`
  - Delete `_format_value_short()` method (lines 213-228)
  - Update calls at lines 151, 152
- [ ] Verify: `pytest tests/ -n 12` passes

### Task 6.2: Consolidate empire resource formatting [Simple]
**File:** `game/ui/screens/build_queue_helpers.py`
**Tests:** `pytest tests/ -n 12`

DUP-UI1-003: Resource abbreviation logic (Met/Org/Vap/Rad/Exo) in `build_queue_helpers.py:format_empire_resources()` (lines 9-29). Check if `strategy_ui.py` has independent duplication.

- [ ] Verify `strategy_ui.py:_format_spectrum()` (line 255) already delegates to `strategy_detail_formatter._format_spectrum()` -- this is star spectrum, NOT resource formatting. **If no real duplication exists, skip this task.**
- [ ] Search for any other independent resource abbreviation logic:
  `grep -r "Met.*Org.*Vap\|Metals.*Organics\|abbrevs.*Met" game/ui/`
- [ ] If found: extract to `game/ui/formatting.py` and update callers
- [ ] If not found: Mark as SKIPPED (sweep false positive)
- [ ] Verify: `pytest tests/ -n 12` passes

### Task 6.3: Extract BaseGallery class [Complex]
**File:** `game/ui/panels/base_gallery.py` (NEW)
**Tests:** `pytest tests/unit/ui/test_race_portrait_gallery.py tests/unit/ui/test_race_flag_gallery.py -v`

DUP-UI1-005: `RacePortraitGallery` and `RaceFlagGallery` share ~70% code.

- [ ] Read full source of both gallery classes to identify exact shared vs. divergent methods
- [ ] Create `game/ui/panels/base_gallery.py` with `BaseGallery` class
- [ ] Move shared constructor logic to `BaseGallery.__init__()`:
  - `panel`, `ui_manager`, `race_config`, `on_select_callback`, `_asset_loader`
  - Gallery button list, preview image, scroll container, preview panel
  - Asset cache
- [ ] Define template methods (abstract, override in subclasses):
  - `_get_asset_config_key()` -> str: `'portrait_id'` vs `'flag_id'`
  - `_get_thumb_size()` -> int: thumbnail pixel size
  - `_discover_assets()` -> list: how to discover available assets
  - `_create_preview_area()`: how to render preview (single image vs. three shapes)
  - `_get_current_selection()` -> str: read from race_config
  - `_set_selection(asset_id)`: write to race_config
- [ ] Move shared methods to base class:
  - `_create_content()` (gallery + preview layout)
  - `_create_gallery_buttons()` (button grid with thumbnails)
  - `handle_event()` (button click -> selection handling)
  - `_handle_selection(asset_id)` (update config, callback, refresh preview)
  - `cleanup()` / `destroy()` if present
- [ ] Update `RacePortraitGallery` to extend `BaseGallery`:
  - Override template methods only
  - Import: `from game.ui.panels.base_gallery import BaseGallery`
- [ ] Update `RaceFlagGallery` to extend `BaseGallery`:
  - Override template methods only
  - Import: `from game.ui.panels.base_gallery import BaseGallery`
- [ ] Verify: `pytest tests/unit/ui/test_race_portrait_gallery.py -v` passes
- [ ] Verify: `pytest tests/unit/ui/test_race_flag_gallery.py -v` passes
- [ ] Verify: `pytest tests/ -n 12` passes

**Callers:** `game/ui/screens/race_setup_screen.py` imports both (lines 33-34). No changes needed
unless constructor signature changes.

### Task 6.4: Extract BaseColumnManager [Complex]
**File:** `game/ui/screens/base_column_manager.py` (NEW)
**Tests:** `pytest tests/unit/ui/test_column_manager.py -v`

DUP-UI1-001: Two `ColumnManager` classes with identical concepts but different data models.

- [ ] Read full source of both column managers:
  - `game/ui/screens/column_manager.py` (fleet reports): data model = `ColumnManager` with `_columns` list, `get_visible_columns()`, `toggle_visibility()`, `move_left()`/`move_right()`
  - `game/ui/screens/planet_list_columns.py` (planet list): data model = `ColumnManager` with UI elements (header buttons, sort state)
- [ ] Identify shared methods/concepts:
  - Column visibility management
  - Column ordering
  - `get_visible_columns()` method
- [ ] Identify divergent features:
  - Fleet ColumnManager: value extraction for ship data, no UI elements
  - Planet ColumnManager: pygame_gui header buttons, sort state, rebuild_headers()
- [ ] Create `game/ui/screens/base_column_manager.py` with `BaseColumnManager`:
  - Shared: `__init__(columns)`, `get_columns()`, `get_visible_columns()`, `toggle_visibility()`, `move_column_left()`, `move_column_right()`
- [ ] Update fleet `ColumnManager` to extend `BaseColumnManager`:
  - Keep fleet-specific value extraction methods
- [ ] Rename planet `ColumnManager` to `PlanetColumnManager` in `planet_list_columns.py`:
  - Keep sort state, header UI, rebuild_headers()
  - Extend `BaseColumnManager` for shared column management
- [ ] Update planet column manager callers:
  - `game/ui/screens/planet_list_window.py:16` -- change import to `PlanetColumnManager`
  - `game/ui/screens/empire_build_queue_window.py:55` -- change import to `PlanetColumnManager`
  - `tests/repro_issues/test_crash_planet_list_method.py:1` -- change import
- [ ] Verify: `pytest tests/unit/ui/test_column_manager.py -v` passes
- [ ] Verify: `pytest tests/ -n 12` passes

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No `_format_value` method in test_run_details.py
- [ ] No `_format_value_short` method in test_run_card.py
- [ ] `BaseGallery` exists and both galleries extend it
- [ ] `BaseColumnManager` exists and both column managers extend it
- [ ] `pytest tests/ -n 12` -- full suite passes (8164+ tests)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
