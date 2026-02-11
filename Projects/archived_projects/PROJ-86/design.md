# PROJ-86: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### TestLabScreen (`game/ui/screens/test_lab/screen.py`)
- **2536 lines**, 58 methods across the `TestLabScreen` class plus 1 module-level function (`get_test_data_dir`)
- Already lives in a package (`test_lab/`) with prior extractions: `dialogs.py`, `json_viewer.py`, `ship_panels.py`, `test_run_card.py`, `test_run_details.py`, `results_panel.py`, `component_dropdown.py`
- The screen class itself was never decomposed -- all extractions so far were widget classes, not responsibility clusters from the main class
- Has a `TestLabUIController` (imported at line 100) which handles some business logic, but the screen still contains data loading, validation, panel creation, test execution, and all rendering

### StrategyUI (`game/ui/screens/strategy_ui.py`)
- **1211 lines**, 41 methods
- One prior extraction exists: `strategy_detail_fmt.py` contains formatting functions (`format_spectrum_html`, `format_atmosphere_raw`, `format_fleet_info`, `get_label_for_object`, etc.)
- StrategyUI still contains `show_detailed_report` (163 lines) which is the main consumer of those formatters -- this should move alongside them
- Heavily coupled to `self.scene` for accessing game state (galaxy, current_empire, turn_engine, facade)
- Manages 8 different window types (fleet_orders, planet_list, build_queue_list, fleet_report, transfer_dialog, menu_panel, empire_build_queue, event_log)

### BuildQueueScreen (`game/ui/screens/build_queue_screen.py`)
- **1185 lines**, 28 methods
- Was previously targeted by PROJ-63 (goal: 603 lines) but grew back due to feature additions in PROJ-67 (Fleet Space Yards), PROJ-69 (Multi Build Queue), PROJ-76 (Empire Build Queue), PROJ-82 (Resource Grid)
- Already has extracted helpers: `BuildQueueDragHandler`, `BuildQueueController`, `BuildQueuePortraitLoader`
- Growth areas likely include: queue selector panel (~100 lines), filter panel (~80 lines), multi-queue support

## Swarm Findings Summary

### Architecture

**TestLabScreen responsibility clusters (5 clusters, 58 methods):**

| Cluster | Methods | Lines | Key Methods |
|---------|---------|-------|-------------|
| Data Extraction | 3 | ~211 | `_extract_ships_from_scenario` (130 lines), `_load_component_data` (27 lines), `get_test_data_dir` (15 lines) |
| Validation | 4 | ~258 | `_validate_all_scenarios` (65 lines), `_build_validation_context_from_files` (52 lines), `_handle_update_expected_values` (48 lines), `_apply_metadata_updates` (90 lines) |
| Panel Creation | 3 | ~209 | `_create_ship_panels` (90 lines), `_create_results_panel` (54 lines), `_create_ui` (25 lines) |
| Test Execution | 5 | ~375 | `_on_run` (77 lines), `_on_run_headless` (130 lines), `_on_run_all_tests` (14 lines), `_run_next_batch_test` (110 lines), `_continue_batch_test` (4 lines) |
| Rendering/Events | 43 | ~1483 | `draw`, `handle_input`, 15x `_draw_*` methods, `_handle_click`, `update`, property accessors |

**StrategyUI responsibility clusters (4 clusters, 41 methods):**

| Cluster | Methods | Lines | Key Methods |
|---------|---------|-------|-------------|
| Detail Formatting | 6 | ~170 | `show_detailed_report` (163 lines), `_compute_planet_production` (32 lines), `show_raw_data_popup` (12 lines), plus 3 thin wrappers |
| Window Lifecycle | 17 | ~200 | 8x `open_*` methods, 6x `_on_*_closed` callbacks, `prompt_planet_selection`, `prompt_move_choice` |
| Panel Layout | 3 | ~360 | `__init__` (324 lines -- panel creation section), `handle_resize` (57 lines), `_apply_hotkey_tooltips` (37 lines) |
| Event Routing | 5 | ~120 | `handle_event` (117 lines), `process_custom_ui_events` (6 lines), `handle_click` (12 lines), `on_ui_selection` (4 lines), `_has_modal_open` (43 lines) |

**BuildQueueScreen responsibility clusters (28 methods, 1185 lines):**
Needs fresh analysis in Phase 8. Preliminary clusters:

| Cluster | Estimated Methods | Notes |
|---------|-------------------|-------|
| Queue Selector | 5 | PROJ-69 multi-queue: `_create_queue_selector_panel`, `_refresh_queue_selector`, `_on_queue_selected`, `_on_queue_toggled`, `_update_queue_header` |
| Layout/Creation | 6 | `_create_background`, `_create_planet_report_panel`, `_create_fleet_info_panel`, `_create_design_report_panel`, `_create_items_list_panel`, `_create_build_queue_panel` |
| Filter Panel | 2 | `_create_filter_panel`, `_format_empire_resources`, `_format_resource_cost` |
| Refresh/Display | 3 | `_refresh_items_list`, `_refresh_queue_display`, `_apply_tooltips` |
| Event Handling | 5 | `handle_event`, `_handle_keydown`, `_handle_remove_hotkey`, `_prompt_target_planet`, `_close` |
| Lifecycle | 3 | `update`, `draw`, `_take_screenshot`, `_show_screenshot_toast`, `_create_bottom_bar` |

### Key Patterns to Reuse

- **Package-internal extraction**: `game/ui/screens/test_lab/` already demonstrates the pattern of extracting into sibling modules within a package. New modules (`data_extractor.py`, `validation_manager.py`, etc.) follow this pattern.
- **Facade delegation**: The original class methods become thin wrappers that call the extracted helper. Example: `def _extract_ships_from_scenario(self, test_id): return self._data_extractor.extract_ships(test_id)`
- **Constructor injection**: Extracted helpers receive necessary state via constructor params (registry, test_history, components_cache) rather than reaching back into the screen.
- **Existing `strategy_detail_fmt.py`**: Already demonstrates the module-level function extraction pattern for StrategyUI.

### Dependencies & Risks

1. **TestExecutor render callbacks (Phase 4)** - `_on_run_headless` and `_run_next_batch_test` draw progress overlays directly to `self.game.screen`. The executor needs a `render_progress` callback or access to screen/fonts. Mitigation: Pass a render callback function during construction.

2. **StrategyUI `__init__` monolith (Phase 7)** - The 324-line `__init__` creates all panels, buttons, labels, and layout rects. Extracting panel creation requires passing the UIManager and all computed rects. Mitigation: Extract a `create_panels(manager, rects)` factory function rather than a full class.

3. **BuildQueueScreen unknown growth (Phase 8)** - Without fresh analysis, we cannot predefine exact extractions. Mitigation: Phase 8 starts with analysis before extraction.

4. **Test coverage gaps** - Poor test coverage means regressions could go unnoticed. Mitigation: Run full test suite after every phase. Manual smoke test for visual UI changes.

### Opportunities Discovered

- `_extract_ships_from_scenario` (130 lines) has significant code duplication across three code paths (conditions parsing, `ship_file` attribute, multi-ship fallback). The extraction is a good time to DRY this up.
- `show_detailed_report` (163 lines) is a massive if/elif chain that could become a strategy pattern or dispatch dict, but that is a behavior change -- defer to a future project.
- `_on_run_headless` and `_run_next_batch_test` share ~60% of their code (engine setup, seed handling, state capture, result storage). Extracting to a shared `_execute_headless` helper within `test_executor.py` would reduce duplication.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
