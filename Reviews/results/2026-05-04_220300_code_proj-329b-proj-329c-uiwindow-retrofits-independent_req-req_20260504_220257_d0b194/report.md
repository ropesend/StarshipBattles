# PROJ-329B + PROJ-329C UIWindow Retrofits — Independent Code Review

**Type:** code (production refactor review)
**Review mode:** normal
**Scope:** 11 UIWindow subclass retrofits to two-stage construction per Pattern §33
**Request ID:** req_20260504_220257_d0b194
**Date:** 2026-05-04
**Completed:** 2026-05-04T22:30:00Z

**Limitations:** PROJ-329B/PROJ-329C project plan folders did not exist in the repo at review time. The master plan reference at `C:\Users\rossr\.claude\plans\noble-stirring-galaxy.md` is outside the repo and was not read. Review based on code + PROJ-328 reference checklists only.

---

## Primary Concern: Behavioral Parity

Three classes were selected for deep behavioral parity verification:

### EmpirePanelWindow (PROJ-329B) — `empire_panel_window.py:72–136`

**Verdict: PASS.** Correct two-stage construction with no behavioral differences.

- Stage 1 (lines 100–119): All cheap state set before `super().__init__` — empire, callbacks, registries, asset_loader, tab/panel containers, current_tab, resource icons, treasury panel placeholder.
- Stage 2 (lines 122–128): `super().__init__()` correctly forwards `window_manager`.
- Stage 3 (lines 131–136): Correctly branches on `_window_init_bypassed`, calls `ui_builder.build(self)` only when supplied.
- `process_event` (539–558): Calls `super().process_event()` first, then handles tab button presses.
- `kill()` (560–564): Fires `on_close_callback` before `super().kill()`.

### PlanetAbilitiesWindow (PROJ-329C) — `planet_abilities_window.py:199–228`

**Verdict: PASS.** Correct two-stage construction. Controller properly owns facade I/O.

- Stage 1 (199–211): planet, facade, component_registry, callbacks, slot dicts, controller — all before `super().__init__`.
- Controller construction: three pure attribute assignments, no facade I/O in `__init__`.
- `process_event` (249–271): Calls `self.controller.toggle_ability()`, dispatches result correctly.
- `kill()` (230–233): `_on_close_callback` fires before `super().kill()`.

### PlanetListWindow (PROJ-329C) — `planet_list_window.py:224–326`

**Verdict: PASS.** Correct two-stage construction. `_resolve_demographic_view` fallback is equivalent in both paths.

- Stage 1 (225–310): All cheap state, columns, `gather_planets`, `compute_planet_effect_keys`, filter state, controller — before `super().__init__`.
- Stage 3 (321–326): Correctly branches on `_window_init_bypassed`.
- Controller path vs legacy fallback in `_resolve_demographic_view` (687–701): Both paths produce identical results for all input cases. The fallback correctly guards against `__new__`-based construction where `controller` may not exist.
- `process_event`, `update`, `kill` all preserve original behavior.

---

## Secondary Concern Findings

### 1. Pattern §33 Conformance

**EmpireBuildQueueWindow (PROJ-329B) — `empire_build_queue_window.py:153–211`**

**MAJOR:** 8 widget refs not initialized as placeholders in Stage 1.

The following attributes are set only by the builder in Stage 3, with no `None`/empty placeholder in Stage 1:
`sidebar_panel`, `main_panel`, `_sidebar`, `_virtual_table`, `scroll_bar`, `_data_source`, `_column_manager`, `_selection`

Pattern §33 requires `_init_widget_refs()` with explicit `None` placeholders before `super().__init__`. A test using `NullEmpireBuildQueueWindowUiBuilder` that subsequently calls `kill()` would crash with `AttributeError` at `empire_build_queue_window.py:591` (`self._virtual_table.kill()`).

**PlanetAbilitiesWindow (PROJ-329C) — `planet_abilities_window.py:199–228`**

**Verdict: PASS.** Fully conformant. Widget ref placeholders (`_toggle_buttons`, `_editor_buttons`, `_status_labels`, `_widgets`) all initialized to empty dicts/lists in Stage 1. Controller parameter with default. Builder delegates all facade queries to controller. Null/Mock fixture pair present.

### 2. No Semantic Changes Disguised as Refactors

**Verdict: PASS.** All 11 production files are pure code-movement + two-stage rewiring refactors. No new validation, error handling, or logging found. Key points verified:

| Check | Status |
|-------|--------|
| CargoQuickDialog controller logging | Identical to original inline `_issue_orders` |
| EventLogWindow title computation | Moved in order, produces identical value |
| EmpireBuildQueueWindow `session` dependency | Pre-existing; only hoisted in order |
| All 11 files | No new imports, no new guards, no new side effects |

### 3. PROJ-329C Controller Boundary

**PlanetAbilitiesController — `planet_abilities_controller.py`**

**Verdict: PASS.** Clean boundary.
- Owns facade queries + command dispatch (5 query methods + `toggle_ability`)
- Zero pygame_gui imports — no widget construction
- Window's `__init__` never calls facade methods
- Window's `process_event` routes exclusively through `self.controller.toggle_ability()` and `self.controller.get_component_status()`

All three PROJ-329C controllers (`PlanetAbilitiesController`, `CargoQuickDialogController`, `PlanetListController`) properly separate facade I/O from widget construction.

### 4. Mixed UIWindow Base Classes

**SaveSelectionWindow, RaceBrowserDialog, DesignSelectorWindow — `save_selection_window.py`, `race_browser_dialog.py`, `design_selector_window.py`**

**Verdict: PASS.** All 3 fully conformant. All 6 checklist items verified per class:

| Criterion | All 3 |
|-----------|:-----:|
| Inline `getattr(type(self), 'bypass_init', False)` guard | ✓ |
| `self.ui_manager = manager` in bypass | ✓ |
| `self._window_init_bypassed = True` in bypass | ✓ |
| No `self.rect` assignment in bypass | ✓ |
| `ui_builder.build(self)` only when non-None | ✓ |
| `super().__init__` only in production path | ✓ |
| All cheap state + delegates BEFORE guard | ✓ |

Each has the corresponding `Null`/`Mock` fixture pair in `tests/fixtures/`.

### 5. CargoQuickDialog Light-Touch

**Verdict: PASS.** `cargo_quick_dialog.py:228–258`
- Two-stage construction correctly applied
- Controller wraps facade calls (get_unload_items, get_load_items, issue_orders)
- Existing tests using real UIManager + production `__init__` path unaffected
- `bypass_init` path present and correct, even if unused by existing tests

### 6. PlanetListWindow Legacy Fallback

**Verdict: PASS.** `_resolve_demographic_view` (`planet_list_window.py:687–701`)
- Controller path and legacy fallback produce identical results for all input cases
- Fallback is necessary: guards `__new__`-based construction where `controller` may not exist
- Under `bypass_init`, the controller *is* constructed, so the controller path fires — also correct
- No behavioral difference between paths

### 7. Test Fixture Quality

**Verdict: PASS with 1 MINOR issue.**

| Fixture Pair | Null Builder | Mock Builder | Protocol |
|---|---|---|---|
| PlanetAbilitiesWindow | ✓ no-op | ✓ Populates slots, checks Stage 1 attrs, hardcodes `_is_active=False` (deliberate simplification) | ✓ |
| PlanetListWindow | ✓ no-op | ✓ Populates all sidebar + main widgets, configures mocks to prevent update loops | ✓ |
| CargoQuickDialog | ✓ no-op | ✓ Checks Stage 1 attrs, seeds cargo_items from mock_items, proper row shape | ✓ |

**MINOR:** `MockCargoQuickDialogUiBuilder` (`cargo_quick_dialog_ui_builder.py:46`): `show_no_items` defaults to `not self.mock_items`. When both `mock_items=[]` and `show_no_items=False` are passed, the default evaluates to `True`, showing the empty label. Callers passing `show_no_items=False` with an empty mock_items list would get unexpected behavior. No current test hits this edge case.

---

## Summary

| Category | Count |
|----------|------:|
| CRITICAL (behavioral regression) | 0 |
| MAJOR (pattern violation) | 1 |
| MINOR (edge-case or convention gap) | 3 |
| OBSERVATION (notable, non-blocking) | 6 |

### Findings Detail

**MAJ-001** — `empire_build_queue_window.py:173–195`  
8 widget refs (`sidebar_panel`, `main_panel`, `_sidebar`, `_virtual_table`, `scroll_bar`, `_data_source`, `_column_manager`, `_selection`) not initialized as `None` placeholders in Stage 1. Pattern §33 requires `_init_widget_refs()`. Null-builder tests that call `kill()` would crash on `self._virtual_table.kill()` (line 591).

**MIN-001** — `event_log_window.py:115–133`  
Several filter-button and panel widget refs not initialized in Stage 1. Production path always sets these via builder before any event handler. No behavioral impact.

**MIN-002** — `star_list_window.py:155–216`  
Several sidebar and table widget refs not initialized in Stage 1. Same pattern-convention gap as EventLogWindow. No behavioral impact.

**MIN-003** — `cargo_quick_dialog_ui_builder.py:46`  
`show_no_items` default logic (`not self.mock_items`) produces unexpected behavior when `mock_items=[]` and `show_no_items=False` are both passed explicitly.

**OBS-001** — `empire_panel_window.py:116`  
`load_resource_icons()` call in Stage 1. Currently safe via module-level cache. Latent issue if cache ever misses and requires initialized display.

**OBS-002** — `planet_abilities_window.py:201`  
`self.facade` stored on window but never referenced post-init. All facade access goes through controller.

**OBS-003** — `planet_abilities_controller.py:78–188`  
4/5 controller query methods don't call facade — they read planet model directly. Valid pattern, but blurs stated "facade-wrapper" intent.

**OBS-004** — `planet_list_window.py:690–693`  
Fallback comment references obsolete `__new__` pattern. Under `bypass_init`, the fallback never fires. Harmless.

**OBS-005** — `planet_list_controller.py:42–45`  
`navigate_to()` method defined but never called by window. Window uses own callback directly. Dead code.

**OBS-006** — `empire_build_queue_window.py:189`  
`collect_all_build_queues_for_empire` call in Stage 1 references `session.registries`. Pre-existing dependency, only moved earlier in `__init__`. Low risk.

---

## Overall Verdict

**APPROVE with 1 MAJOR finding.** The two-stage construction retrofit is correctly applied across all 11 classes. Behavioral parity is preserved. No regressions found. The 1 MAJOR finding (EmpireBuildQueueWindow missing widget ref placeholders) is a pattern-convention gap that could cause test crashes in the Null-builder path — recommended fix before merging but not a production regression.
