# Agent 3 — Cross-Cutting Review: PROJ-329B + PROJ-329C

**Date**: 2026-05-04
**Scope**: Semantic change detection, Pattern §33 conformance (PlanetAbilitiesWindow), test fixture quality, PROJ-329B class consistency scan.

---

## Semantic Changes Disguised as Refactors

All 11 production files were scanned for unexpected new behavior. **No semantic changes detected.** Every file is a pure code-movement + two-stage rewiring refactor.

### Scanned clean

| File | Status | Notes |
|---|---|---|
| `empire_build_queue_window.py` | Clean | MVVM state hoisted to Stage 1; `EmpireBuildQueueUiBuilder` replaces inline `_init_layout`-style calls. `collect_all_build_queues_for_empire` call moved from post-`super().__init__` to pre-; pure-data function, no UI dependency. |
| `empire_panel_window.py` | Clean | `EmpirePanelUiBuilder.build()` wraps existing `_create_ui()` + `_show_tab(TAB_TREASURY)`. RaceRegistry `getattr` fallback unchanged. |
| `event_log_window.py` | Clean | `EventLogUiBuilder.build()` wraps existing `_init_layout()` + `_rebuild_list()`. Title computation moved into Stage 2; identical value. Widget-ref `None` initializers moved to Stage 1 from post-`_init_layout`. |
| `design_selector_window.py` | Clean | Direct `UIWindow` subclass with inline bypass guard (`type(self).bypass_init`). `DesignSelectorUiBuilder` wraps `_create_sidebar()` + `_create_main_list()` + `_create_bottom_buttons()` + `_refresh_designs()`. |
| `star_list_window.py` | Clean | `StarListWindowUiBuilder` wraps inline widget construction. `gather_stars`, `compute_star_ranges`, column defs hoisted to Stage 1 (pure data). `selected_star`/`btn_navigate` set to `None` in Stage 1 (were previously set after `super().__init__`; documented as required by `set_dimensions`). |
| `race_browser_dialog.py` | Clean | Direct `UIWindow` subclass pattern. `RaceBrowserDialogUiBuilder` wraps scroll_container + buttons. `_load_races()` called after builder in production path; unchanged. |
| `save_selection_window.py` | Clean | Direct `UIWindow` subclass pattern. `SaveSelectionUiBuilder` wraps listbox + buttons. `_load_saves()` called after builder; unchanged. |
| `system_selection_window.py` | Clean | `SystemSelectionUiBuilder` wraps label + selection_list + buttons. `_sorted_display_list` built in Stage 1 (pure data); unchanged. |
| `planet_abilities_window.py` | Clean | Retrofit predates PROJ-329B/C (PROJ-312). Already in canonical two-stage form. |
| `planet_list_window.py` | Clean | `PlanetListUiBuilder` wraps sidebar + main_panel + virtual_table + btn_navigate + `refresh_list()`. `PlanetListController` wraps `resolve_demographic_view` (identical to original inline facade check). Legacy fallback path preserved in `_resolve_demographic_view` (lines 695-701). |
| `cargo_quick_dialog.py` | Clean | `CargoQuickDialogUiBuilder` wraps `_setup_ui` + `_apply_tooltips` + `_populate_items`. `CargoQuickDialogController` wraps `get_unload_items`, `get_load_items`, `issue_orders` (identical logic to original inline code, including per-item logging at controller lines 103-108 and summary log at dialog line 304). |

### Detailed verification: CargoQuickDialog controller logging

The controller's `issue_orders` includes per-item logging (lines 103-108 of `cargo_quick_dialog_controller.py`):
```python
logger.info(f"CargoQuickDialog: Order issued for {item['label']}")
logger.info(f"CargoQuickDialog: Validation failed: {result.message}")
```
Confirmed identical to the original inline `_issue_orders` at commit `851bfa69f~1`. The summary log (`orders_issued > 0`) remains in the dialog wrapper at line 304. No new logging calls.

### Detailed verification: EventLogWindow title computation

The title computation changed position (moved into Stage 2 from post-`super().__init__`) but produces **identical values**. Original computed `title` after `self.all_events = list(events)`; new computes it before `super().__init__()` but after same Stage 1 assignments. No semantic difference.

### Detailed verification: EmpireBuildQueueWindow `session` dependency

`collect_all_build_queues_for_empire(empire, registries=session.registries)` was hoisted from post-`super().__init__` to Stage 1. `session` has default `None` in the signature, same as before. In production, `session` is always provided. Tests using `bypass_init` still execute Stage 1. This is the same dependency as the original code — no regression.

---

## Pattern §33 Conformance (PlanetAbilitiesWindow)

**Result: FULLY CONFORMANT.** No violations found.

### Stage 1 (lines 199-211) — BEFORE `super().__init__`

| Requirement | Line(s) | Status |
|---|---|---|
| Cheap state set before super().__init__ | 200-203 | PASS: `planet`, `facade`, `component_registry`, callbacks assigned |
| Widget ref placeholders initialized to empty/None | 205-208 | PASS: `_toggle_buttons: Dict[str, UIButton] = {}`, `_editor_buttons: List[UIButton] = []`, `_status_labels: Dict[str, UILabel] = {}`, `_widgets: List = []` |
| Controller delegate created (lazy) | 209-211 | PASS: `PlanetAbilitiesController(planet, facade, component_registry)` — stores references only, no facade I/O in constructor |
| No facade I/O in Stage 1 | 199-211 | PASS: Only reference storage; `scan_abilities`, `get_available_editors` etc. are deferred to builder stage |

### Stage 2 (lines 213-220) — `super().__init__()`

| Requirement | Status |
|---|---|
| Calls `StrategyModalWindow.__init__` | PASS: line 214 |
| Window title, resizable flag forwarded | PASS: `f"Abilities: {planet.name}"`, `resizable=False` |
| `window_manager` forwarded | PASS |

### Stage 3 (lines 222-228) — Bypass guard + widget construction

| Requirement | Line(s) | Status |
|---|---|---|
| Checks `_window_init_bypassed` (StrategyModalWindow subclass pattern) | 223 | PASS |
| Bypass path: calls `ui_builder.build(self)` if supplied, returns | 224-226 | PASS |
| Production path: `(ui_builder or PlanetAbilitiesUiBuilder()).build(self)` | 228 | PASS |
| No `self.rect` assignment in bypass branch | N/A | PASS (bypass is handled in base class; subclass never assigns rect) |

### ui_builder + controller protocol

| Requirement | Status |
|---|---|
| `ui_builder` parameter: `Optional[PlanetAbilitiesUiBuilder] = None` | PASS: line 180 |
| `controller` parameter: `Optional[PlanetAbilitiesController] = None` | PASS: line 181 |
| `PlanetAbilitiesUiBuilder` owns ALL widget construction | PASS: builds editor buttons (lines 59-79), toggleable ability rows (lines 83-153), empty-state labels (lines 85-103) |
| `PlanetAbilitiesUiBuilder` delegates facade queries to `screen.controller` | PASS: `screen.controller.get_available_editors()` (line 52), `screen.controller.should_show_food_editor()` (line 53), `screen.controller.scan_abilities()` (line 83), `screen.controller.get_component_status()` (line 123), `screen.controller.is_component_active()` (line 135) |
| Controller owns facade queries only, NOT widget construction | PASS: `PlanetAbilitiesController` has no pygame_gui imports; methods return data/status/commands |
| Null/Mock fixture pair exists in `tests/fixtures/` | PASS: `planet_abilities_window_ui_builder.py` |

---

## Test Fixture Quality

### Pair 1: PlanetAbilitiesWindow (`planet_abilities_window_ui_builder.py`)

**Null builder**: `build()` returns `None` immediately — correct no-op. **PASS.**

**Mock builder**:
- Checks required attributes (`_toggle_buttons`, `_editor_buttons`, `_status_labels`, `_widgets`) exist before populating (lines 51-63). **PASS.**
- `_editor_type` assignment matches production pattern (line 67: `btn._editor_type = label.lower()`). **PASS.**
- Toggle button attrs set: `_ability_name`, `_facility_id`, `_component_key`, `_is_active` (line 82-85). **PASS.**
- Name labels appended to `_widgets` before status labels and toggle buttons (matching production row ordering at lines 121, 132, 151). **PASS.**
- `row_key` format matches production: `f"{facility_id}:{component_key}"` (line 72). **PASS.**
- Parameterizable via `mock_rows` and `mock_editor_buttons`. **PASS.**

**Minor observation**: `_is_active` is hardcoded to `False` (line 85). Production builder reads the real state. This is a deliberate Mock simplification — tests that care about active/inactive toggle behavior should seed `mock_rows` with their own mocks. **Not a defect.**

**Protocol**: Both builders implement `build(screen) -> None`. Structurally conform to `UiBuilder` protocol. **PASS.**

### Pair 2: PlanetListWindow (`planet_list_window_ui_builder.py`)

**Null builder**: `build()` returns `None` immediately — correct no-op. **PASS.**

**Mock builder**:
- Checks required attributes (`columns`, `all_planets`, `preset_manager`, `_filter_mgr`, `_planet_ranges`, `_effect_keys`, `ui_filters`) exist (lines 44-59). **PASS.**
- Populates sidebar widget references (lines 62-76): `sidebar_panel`, `sidebar_scroller`, `txt_name_filter`, all All/None buttons, `btn_apply`, `btn_save_preset`, `txt_preset_name`, `dd_presets`. **PASS.**
- `ui_filters` populated with gravity/temp/mass slider mocks (lines 80-91) — each with `get_current_value.return_value = 0.0` and `limits` tuple. **PASS.**
- Empty section dicts for `types`, `owners`, `effects`, `columns` (lines 92-95) — prevents `KeyError` during `process_event` iterations. **PASS.**
- Main content area: `main_panel`, `column_manager` (with `sort_column_id='owner'`), `data_source`, `selection`, `virtual_table`, `btn_navigate` (lines 98-107). **PASS.**
- `virtual_table.scroll_bar` mock with `check_has_moved_recently.return_value = False` — prevents scroll-triggered update loops. **PASS.**
- `dd_presets.selected_option = "Default"` — prevents preset-change detection loops. **PASS.**
- `txt_name_filter.get_text.return_value = ""` — prevents search string interactions. **PASS.**

**Protocol**: Both builders implement `build(screen) -> None`. Structurally conform to `UiBuilder` protocol. **PASS.**

### Pair 3: CargoQuickDialog (`cargo_quick_dialog_ui_builder.py`)

**Null builder**: `build()` returns `None` immediately — correct no-op. **PASS.**

**Mock builder**:
- Checks required attributes (`cargo_items`, `fleet`, `direction`) exist (lines 49-56). These are Stage 1 attributes; the check ensures Stage 1 ran. **PASS.**
- Populates `lbl_title`, `btn_confirm`, `btn_cancel` with MagicMocks (lines 58-60). **PASS.**
- Seeds `cargo_items` from `mock_items` with proper row shape: `label`, `type`, `species_id`, `max`, `planet_id`, `slider`, `lbl_val`, `btn_all`, `lbl` (lines 62-74). **PASS.**
- `show_no_items` branch: sets `lbl_no_items` when `cargo_items` is empty and `show_no_items` is True (lines 76-77). **PASS.**
- Constructor accepts `mock_items` (list of dicts) and `show_no_items` (bool) with sensible defaults (lines 41-46). **PASS.**

**Observation**: `show_no_items` defaults to `not self.mock_items` (line 46). When both `mock_items=[]` and `show_no_items=False` are passed, `show_no_items` is `True` (since `not []` is `True`). Callers passing `show_no_items=False` expecting no-empty-label would get unexpected behavior. This is a **MINOR** edge-case API quirk — the default logic is backwards-compatible with expected usage (callers passing non-empty `mock_items` or no args). **No test currently hits this edge case.** See `cargo_quick_dialog_ui_builder.py:46`.

**Protocol**: Both builders implement `build(screen) -> None`. Structurally conform to `UiBuilder` protocol. **PASS.**

---

## Quick Scan — Remaining PROJ-329B Classes

### `event_log_window.py` (lines 100-155)

- **Subclass**: `StrategyModalWindow` ✓
- **Stage 1** (lines 114-133): `all_events`, `current_filter`, callbacks, replay wiring, `_last_click_time`/`_last_click_row`, widget-ref placeholders (data_source, column_manager, virtual_table, sidebar) → all `Optional[...] = None`. ✓
- **Stage 2** (lines 135-147): Title computed in-place, `super().__init__()` with `window_manager`. ✓
- **Stage 3** (lines 149-155): `_window_init_bypassed` guard → `EventLogUiBuilder` fallback. ✓
- **No violations.** Clean pattern following.

### `star_list_window.py` (lines 140-232)

- **Subclass**: `DataListWindowMixin, StrategyModalWindow` ✓
- **Stage 1** (lines 155-216): `selected_star`/`btn_navigate` → `None`, cheap state, layout constants, `gather_stars`, preset/filter managers, `compute_star_ranges`, column defs, `ui_filters` → `{}`. ✓
- **Stage 2** (lines 218-224): `super().__init__()` with `window_manager`. ✓
- **Stage 3** (lines 226-232): `_window_init_bypassed` guard → `StarListWindowUiBuilder` fallback. ✓
- **No violations.** Clean pattern following.

### `system_selection_window.py` (lines 81-137)

- **Subclass**: `StrategyModalWindow` ✓
- **Stage 1** (lines 104-123): `systems`, `current_system`, `callback`, `display_to_name`, `_sorted_display_list` (pure data). ✓
- **Stage 2** (lines 125-129): `super().__init__()` with `window_manager`. ✓
- **Stage 3** (lines 131-137): `_window_init_bypassed` guard → `SystemSelectionUiBuilder` fallback. ✓
- **No violations.** Clean pattern following.

### `empire_build_queue_window.py` (lines 153-211)

- **Subclass**: `StrategyModalWindow` ✓
- **Stage 1** (lines 173-196): `empire`, `galaxy`, callbacks, session/facade, layout constants, MVVM (event_bus, viewmodel, filter_mgr). ✓
- **Stage 2** (lines 198-203): `super().__init__()` with `window_manager`. ✓
- **Stage 3** (lines 205-211): `_window_init_bypassed` guard → `EmpireBuildQueueUiBuilder` fallback. ✓
- **OBSERVATION** — `collect_all_build_queues_for_empire` is called in Stage 1 (line 189) referencing `session.registries`. `session` has default `None` in the signature. If a bypass-init test constructs this window with `session=None`, Stage 1 will crash on `session.registries` before the bypass guard ever runs. This is an existing pre-PROJ-329B dependency — `session` was never `None` in production. The two-stage rewiring did not create this dependency, it only moved it earlier in `__init__`. **Low-risk.** No test currently hits this because mock builders are used in bypass mode and tests providing a real builder also provide a real session.
- **No violations.** Clean pattern following.

---

## Summary

| Category | Count |
|---|---|
| CRITICAL (behavioral regression) | 0 |
| MAJOR (pattern violation) | 0 |
| MINOR (edge-case quirk) | 1 — CargoQuickDialog Mock `show_no_items` default edge case |
| OBSERVATION | 2 — EmpireBuildQueueWindow Stage-1 session dependency; MockPlanetAbilitiesWindowUiBuilder hardcoded `_is_active` |

**Overall verdict**: All 11 production files are clean refactors with no semantic changes. PlanetAbilitiesWindow fully conforms to Pattern §33. All 3 fixture pairs are well-structured and protocol-compliant. All 4 remaining PROJ-329B classes correctly follow the StrategyModalWindow two-stage pattern.
