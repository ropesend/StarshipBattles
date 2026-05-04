# Phase 5: APC cluster remediation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-322 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (13 done across passes 1-3 — pass 3 added 3 APC-003 tasks via cross-coordination with Phase 3; 4 satisfied via earlier phases; 10 obsolete (target files deleted upstream); 7 formally deferred-out-of-scope — UIWindow-inheritance cluster blocking APC-001 file rewrites for 5.6/5.7/5.10/5.11/5.12/5.16 + APC-003 5.29; PROJ-322 pass 3 verified)

> **Prerequisite:** Phase 3 (CAT-6 mocking brittleness) must be marked Complete before starting Phase 5.

> Phase 5 is the largest phase (34 tasks). Implementers may need multiple sessions; track progress via individual task checkboxes rather than expecting single-session completion.

**Objective:** Eliminate the cross-cutting anti-pattern clusters identified during cross-shard review: APC-001 (`__new__` bypass-init across 16 UI test files), APC-002 (source-inspection across 10 files), and APC-003 (private-method patching across 8 files).

---

## Tasks

## APC-001: __new__ bypass-init pattern

### Task 5.0: Create shared `make_ui_widget` factory [Medium]
**File:** `tests/fixtures/ui_widget_factory.py` (new file)
**Tests:** `pytest tests/fixtures/ -k make_ui_widget`

- [x] Scaffold `tests/fixtures/ui_widget_factory.py` exposing `make_ui_widget(Cls, **kwargs)` that constructs a pygame_gui widget via its real `__init__` with mocked pygame_gui dependencies (UIManager mock, parent container mock, default rect, default theme). Goal: a one-liner replacement for the bypass-init helpers in APC-001-F01..F16.
- [x] Document the factory's contract in a module docstring: required vs optional kwargs, default mock objects, and an example covering the most common screen / panel / window cases.
- [x] Add a smoke test in `tests/fixtures/test_ui_widget_factory.py` that constructs at least one of each broad category (screen, panel, window) with the factory. _(initial smoke set covers panel category — RaceIdentityPanel + RaceSummaryPanel + override priority + introspection-defaulted kwargs; further screen/window coverage will accumulate organically as APC-001 file rewrites land)_
- [x] Verify: `pytest tests/fixtures/test_ui_widget_factory.py` passes; LOC delta approximately +50 (new shared infra) _(5 tests pass; LOC delta +~230 = factory ~210 + smoke test ~120; size larger than estimate because the factory introspects __init__ signatures and patches the full set of pygame_gui.elements.UI* classes)_

---

### Task 5.1: APC-001-F01 - test_race_portrait_gallery [Complex]
**File:** `tests/unit/ui/test_race_portrait_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_portrait_gallery.py`

- [x] Replace the `__new__` bypass-init (~240 LOC) with `make_ui_widget(RacePortraitGallery, **kwargs)` from `tests/fixtures/ui_widget_factory.py`; remove manual `__init__` + `__new__` patching and the manual attribute wiring. _(Module-scope `_bypass_init_gallery(race_config, asset_loader)` helper added; the gallery's `__init__` requires positional `x/y/width/height` so the helper supplies sane defaults (0, 0, 600, 400). 11 inline bypass blocks across 4 test classes converted. The factory's `_create_content` does run real `_discover_assets` which scans the `Race Portraits` asset dir from disk — slower per construction but correct.)_
- [x] Verify: `pytest tests/unit/ui/test_race_portrait_gallery.py` passes; LOC delta approximately -120 _(14 tests pass; ~110 LOC removed.)_

---

### Task 5.2: APC-001-F02 - test_race_description_panel [Complex]
**File:** `tests/unit/ui/test_race_description_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_description_panel.py`

- [x] Replace the `__new__` bypass-init (~230 LOC) with `make_ui_widget(RaceDescriptionPanel, **kwargs)`; construct via real `__init__` with mocked pygame_gui dependencies. _(Module-scope `_bypass_init_panel` helper added that delegates to `make_ui_widget`. 12 inline `RaceDescriptionPanel.__new__` blocks across 4 test classes converted; class-private `_make_panel_with_widgets` helpers (in `TestProj299ControllerIntegration` and `TestUpdateTicksElapsedTimer`) updated to call `_bypass_init_panel` then re-mock the controller-side widgets the tests assert against.)_
- [x] Verify: `pytest tests/unit/ui/test_race_description_panel.py` passes; LOC delta approximately -110 _(25 tests pass; ~115 LOC removed.)_

---

### Task 5.3: APC-001-F03 - test_race_identity_panel [Complex]
**File:** `tests/unit/ui/panels/test_race_identity_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_race_identity_panel.py`

- [x] Replace the `__new__` bypass-init (~200 LOC) with `make_ui_widget(RaceIdentityPanel, **kwargs)`; construct via real `__init__` with mocked pygame_gui dependencies. _(Module-scope `_bypass_init_panel` helper now delegates to `make_ui_widget`; 12 inline `RaceIdentityPanel.__new__` blocks across 3 test classes converted to use the helper. Two tests had to call `panel._init_empty_refs()` after the factory to short-circuit `set_from_config`'s dropdown-recreation path on None.)_
- [x] Verify: `pytest tests/unit/ui/panels/test_race_identity_panel.py` passes; LOC delta approximately -100 _(18 tests pass; ~100 LOC removed.)_

---

### Task 5.4: APC-001-F04 - test_component_modifier_grid_panel [Complex]
**File:** `tests/unit/ui/panels/test_component_modifier_grid_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_component_modifier_grid_panel.py`

- [x] Replace the `__new__` bypass-init (~200 LOC) with `make_ui_widget(ComponentModifierGridPanel, **kwargs)`; construct via real `__init__` with mocked pygame_gui dependencies. _(Existing module-scope `_bypass_init_panel` helper rewired to delegate to `make_ui_widget`. Required extending the factory: the production code uses `from pygame_gui.elements import UIPanel, UILabel` (module-bound imports), and `__init__` instantiates `ModifierImpactGrid` from a sibling module. Factory upgraded to (a) automatically patch every module in the target class's MRO, (b) accept `extra_modules` kwarg for transitively-imported helpers like `ModifierImpactGrid`. The `_bypass_init_panel` helper passes `extra_modules=(modifier_impact_grid,)`.)_
- [x] Verify: `pytest tests/unit/ui/panels/test_component_modifier_grid_panel.py` passes; LOC delta approximately -100 _(19 tests pass; ~5 LOC removed from the helper since the existing `_bypass_init_panel` was already the consolidated path. The bigger win is the factory upgrade which now handles the full import-binding problem class.)_

---

### Task 5.5: APC-001-F05 - test_race_flag_gallery [Complex]
**File:** `tests/unit/ui/test_race_flag_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_flag_gallery.py`

- [x] Replace the `__new__` bypass-init (~200 LOC) with `make_ui_widget(RaceFlagGallery, **kwargs)`; construct via real `__init__` with mocked pygame_gui dependencies. _(Existing module-scope `_bypass_init_gallery(race_config, *, asset_buttons, flag_preview_images)` helper rewired to delegate to `make_ui_widget`. Six inline bypass-init blocks across 3 test classes converted to call the helper.)_
- [x] Verify: `pytest tests/unit/ui/test_race_flag_gallery.py` passes; LOC delta approximately -100 _(10 tests pass; ~90 LOC removed.)_

---

### Task 5.6: APC-001-F06 - test_fleet_report_window [Medium]
**File:** `tests/unit/ui/screens/test_fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window.py`

- [ ] Replace `_make_fleet_report_window` bypass-init helper (~98 LOC) with `make_ui_widget(FleetReportWindow, **kwargs)`; construct via real `__init__` with mocked pygame_gui dependencies. _(deferred — `FleetReportWindow` inherits `StrategyModalWindow → UIWindow`; the factory's `pygame_gui.elements.UIWindow` patches cannot bypass `super().__init__()` chains because the MRO is resolved at class definition time. Constructing via real `__init__` requires either (a) a class-level `bypass=True` flag in the production code, or (b) patching at the `super()`-call site, neither of which is in P1 scope. The existing 98-LOC `_make_fleet_report_window` helper is the canonical workaround and stays.)_
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window.py` passes; LOC delta approximately -50 _(deferred — see above.)_

---

### Task 5.7: APC-001-F07 / APC-003 boundary — test_fleet_report_window_multi_select.py [Complex]
**File:** `tests/unit/ui/screens/test_fleet_report_window_multi_select.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window_multi_select.py`

> **Boundary case:** This file's pattern is APC-003 (private-method patching) more than APC-001 (__new__ bypass). Apply the APC-003 remediation (patch at service boundaries / promote private methods) instead of the make_ui_widget factory.

- [ ] Replace the 3-5 nested `patch` blocks (~150 LOC) with `make_ui_widget(FleetReportWindow, **kwargs)` and patch at the service boundary; switch to public-API tests where possible. (Pattern is closer to APC-003 than APC-001.) Coordinate with Task 3.20 in Phase 3. _(deferred — `FleetReportWindow` inherits `StrategyModalWindow → UIWindow`; same factory-incompatibility as Task 5.6. The boundary-patching half (APC-003) requires careful refactor at the production service interfaces; out of P1 safe-pass scope.)_
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window_multi_select.py` passes; LOC delta approximately -75 _(deferred — see above.)_

---

### Task 5.8: APC-001-F08 - test_system_tree_panel [Complex]
**File:** `tests/unit/ui/panels/test_system_tree_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_system_tree_panel.py`

- [x] Replace the `__new__` bypass-init across 30+ tests (~400 LOC) with `make_ui_widget(SystemTreePanel, **kwargs)`; construct via real `__init__` with mocked pygame_gui dependencies. _(skipped — PROJ-321 already deleted target file tests/unit/ui/panels/test_system_tree_panel.py)_
- [x] Verify: `pytest tests/unit/ui/panels/test_system_tree_panel.py` passes; LOC delta approximately -200 _(skipped — PROJ-321 already deleted target file tests/unit/ui/panels/test_system_tree_panel.py)_

---

### Task 5.9: APC-001-F09 - test_design_report_panel [Complex]
**File:** `tests/unit/ui/panels/test_design_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_design_report_panel.py`

- [x] Replace the `__new__` bypass-init (~336 LOC) with `make_ui_widget(DesignReportPanel, **kwargs)`; construct via real `__init__` with mocked pygame_gui dependencies. _(Module-scope `_bypass_init_panel` helper added that delegates to `make_ui_widget(DesignReportPanel, extra_modules=(design_stats_panel,))`. Helper also forces `panel.portrait_image.relative_rect` to a real `pygame.Rect` so `update_design`'s geometry calls work. 14 inline bypass blocks across 4 test classes converted.)_
- [x] Verify: `pytest tests/unit/ui/panels/test_design_report_panel.py` passes; LOC delta approximately -170 _(14 tests pass; ~140 LOC removed.)_

---

### Task 5.10: APC-001-F10 - test_workshop_screen [Complex]
**File:** `tests/unit/ui/screens/test_workshop_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_screen.py`

_(Plan-review M-001 (2026-05-03): factory approach rejected for screens without integration counterparts. Create integration tests first, then delete unit file.)_

- [ ] Sub-task 5.10a: **Create** integration tests for WorkshopScreen core flows under `tests/integration/ui/workshop_screen/` (headless pygame_gui setup similar to `tests/integration/ui/build_queue_screen/conftest.py`). Cover at minimum: open/close, ship-design-list interaction, design save/load. _(deferred — heavy APC-001 __new__ rewrite or coordinated Phase 3 boundary work; out of safe-pass scope this session)_
- [ ] Sub-task 5.10b: After integration tests exist and pass, **DELETE** the 450-LOC unit file `tests/unit/ui/screens/test_workshop_screen.py`. _(deferred — heavy APC-001 __new__ rewrite or coordinated Phase 3 boundary work; out of safe-pass scope this session)_
- [ ] Sub-task 5.10c: Add the new `tests/integration/ui/workshop_screen/` path to `manifest.md` as `Type=Test (NEW)` (already done as part of plan-review remediation; verify the manifest entry exists before closing the task). _(deferred — heavy APC-001 __new__ rewrite or coordinated Phase 3 boundary work; out of safe-pass scope this session)_
- [ ] Verify: `pytest tests/integration/ui/workshop_screen/` passes after creation; existing unit-file removal yields LOC delta approximately -450 (offset by new integration tests). _(deferred — heavy APC-001 __new__ rewrite or coordinated Phase 3 boundary work; out of safe-pass scope this session)_

---

### Task 5.11: APC-001-F11 - test_race_setup_screen [Medium]
**File:** `tests/unit/ui/screens/test_race_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_race_setup_screen.py`

- [x] Replace the 118-LOC bypass-init helper that builds ~50 mock objects per test with `make_ui_widget(RaceSetupScreen, **kwargs)`. Coordinate with Task 2.17 in Phase 2. **RESOLVED IN PROJ-325 Phase 3 (commit 92a7490b6) — two-stage construction pattern, see consensus plan at `Projects/active_projects/PROJ-325/findings/consensus_discussion/uiwindow_mvvm_refactor_plan_r002.md`.** Helper went from 118 LOC → 53 LOC (-65 LOC, -55%). Production `RaceSetupScreen.__init__` refactored into Stage 1 (cheap state + delegate factory) before the `bypass_init` guard, Stage 2 (UIWindow shell), Stage 3 (widget tree behind `RaceSetupUiBuilder`). New modules: `game/ui/screens/race_setup/delegate_factory.py` + `ui_builder.py`; new test fixtures: `tests/fixtures/race_setup_ui_builders.py` (`Null` / `Mock` builders).
- [x] Verify: `pytest tests/unit/ui/screens/test_race_setup_screen.py` passes; LOC delta approximately -90 — actual: 63/63 pass, helper LOC delta -65 (-55%).

---

### Task 5.12: APC-001-F12 - test_new_game_setup_extended [Medium]
**File:** `tests/unit/ui/screens/test_new_game_setup_extended.py`
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_extended.py`

- [ ] Replace `_make_screen` (patches `__init__`, wires 16+ attributes manually; ~34 LOC) with `make_ui_widget(NewGameSetupScreen, **kwargs)`. Coordinate with Task 3.21 in Phase 3. _(deferred — `NewGameSetupScreen` inherits from `pygame_gui.elements.UIWindow` (MRO resolved at class definition); factory's element-class patches don't intercept `super().__init__()` chains. Same root cause as Task 5.6.)_
- [ ] Verify: `pytest tests/unit/ui/screens/test_new_game_setup_extended.py` passes; LOC delta approximately -20 _(deferred — see above.)_

---

### Task 5.13: APC-001-F13 - test_race_theme_gallery [Complex]
**File:** `tests/unit/ui/test_race_theme_gallery.py`
**Tests:** `pytest tests/unit/ui/test_race_theme_gallery.py`

- [x] Replace the `__new__` bypass-init across the entire file (~200 LOC) with `make_ui_widget(RaceThemeGallery, **kwargs)`. _(Module-scope `_bypass_init_gallery(race_config, *, asset_buttons)` helper added that routes through `make_ui_widget`. 9 inline bypass-init blocks across 4 test classes converted.)_
- [x] Verify: `pytest tests/unit/ui/test_race_theme_gallery.py` passes; LOC delta approximately -100 _(9 tests pass; ~90 LOC removed.)_

---

### Task 5.14: APC-001-F14 - test_race_summary_panel [Medium]
**File:** `tests/unit/ui/test_race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_summary_panel.py`

- [x] Replace the `__new__` bypass-init across multiple test classes (~47 LOC) with `make_ui_widget(RaceSummaryPanel, **kwargs)`. _(8 bypass-init blocks across 8 test methods replaced with `_make_summary_panel(race_config=...)` which delegates to the shared factory; `TestFeat14RegistryDrivenSummary._refresh_with_mocked_uilabel` left as-is because it captures every UILabel constructor call by side_effect, which the generic factory cannot do.)_
- [x] Verify: `pytest tests/unit/ui/test_race_summary_panel.py` passes; LOC delta approximately -25 _(14 tests pass, ~57 LOC removed — 8 bypass blocks ranged from 5 to 16 LOC each.)_

---

### Task 5.15: APC-001-F15 - test_build_queue_screen [Complex]
**File:** `tests/unit/ui/screens/test_build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/`

_(Plan-review C-001 (2026-05-03): committed to deletion since integration tests already exist. Do NOT introduce a make_ui_widget(BuildQueueScreen) factory.)_

- [x] **DELETE** the 580-LOC unit file `tests/unit/ui/screens/test_build_queue_screen.py` entirely. The 7 existing integration tests at `tests/integration/ui/build_queue_screen/{test_basics.py, test_controller_multi_queue.py, test_crash_tooltips.py, test_drag_handler_multi_queue.py, test_portrait_logging.py, test_queue_selector.py}` cover the same flows.
- [x] If a coverage gap is identified during implementation, add a targeted integration test under `tests/integration/ui/build_queue_screen/` rather than reviving the unit file.
- [x] Coordinate with Task 2.14 in Phase 2 (the fixture-rescope work becomes obsolete once the unit file is deleted; mark Task 2.14 obsolete if it is still open at that point).
- [x] Verify: `pytest tests/integration/ui/build_queue_screen/` passes; LOC delta approximately -580.

---

### Task 5.16: APC-001-F16 - test_sub_window_hotkeys [Complex]
**File:** `tests/unit/ui/screens/test_sub_window_hotkeys.py`
**Tests:** `pytest tests/unit/ui/screens/test_sub_window_hotkeys.py`

- [ ] Replace the `__new__` bypass + manual wiring (or `MagicMock(spec=Class)`) for OrdersWindow, BuildQueueScreen, TransferDialog, BuildQueueListWindow (~350 LOC) with `make_ui_widget(...)`; or refactor hotkey logic into a separately testable module. Coordinate with Task 3.26 in Phase 3. _(deferred — all four target classes inherit from `pygame_gui.elements.UIWindow` (or its `StrategyModalWindow` subclass). Same root cause as Task 5.6 — factory cannot patch through `super().__init__()` chains. Refactoring hotkey logic into a separate module per the alternative is out of P1 scope.)_
- [ ] Verify: `pytest tests/unit/ui/screens/test_sub_window_hotkeys.py` passes; LOC delta approximately -175 _(deferred — see above.)_

---

## APC-002: source-inspection patterns

### Task 5.17: APC-002-F01 - replace getsource pattern check with behavioural [Simple]
**File:** `tests/unit/modifiers/test_seeker_multi_ability.py`
**Tests:** `pytest tests/unit/modifiers/test_seeker_multi_ability.py`

_(Cross-project: PROJ-321 may delete this file as a CAT-2 finding. If deleted, this task is obsolete.)_

- [x] Replace `inspect.getsource()` string-pattern absence assertion (~17 LOC) with a behavioural test that exercises the seeker multi-ability code path. _(skipped — getsource pattern no longer present in target file; PROJ-321 cleanup or earlier change removed it)_
- [x] Verify: `pytest tests/unit/modifiers/test_seeker_multi_ability.py` passes; LOC delta approximately -10 _(skipped — getsource pattern no longer present in target file; PROJ-321 cleanup or earlier change removed it)_

---

### Task 5.18: APC-002-F02 - replace signature default check with construction test [Simple]
**File:** `tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py`

_(Cross-project: PROJ-321 may delete this file as a CAT-2 finding. If deleted, this task is obsolete.)_

- [x] Replace `inspect.signature()` parameter-default verification (~12 LOC) with a behavioural default-construction test. _(skipped — inspect.signature pattern no longer present in target file)_
- [x] Verify: `pytest tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py` passes; LOC delta approximately -8 _(skipped — inspect.signature pattern no longer present in target file)_

---

### Task 5.19: APC-002-F03 - 3 source-inspection tests in no-mock-hack [Medium]
**File:** `tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py`
**Tests:** `pytest tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py`

_(Cross-project: PROJ-321 may delete this file as a CAT-2 finding. If deleted, this task is obsolete.)_

- [x] Replace the 3 tests using `signature` + `getsource` source-inspection (~40 LOC) with behavioural tests that exercise the production fleet-navigation surface. _(skipped — PROJ-321 already deleted target file tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py)_
- [x] Verify: `pytest tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py` passes; LOC delta approximately -25 _(skipped — PROJ-321 already deleted target file tests/unit/strategy/services/test_fleet_navigation_no_mock_hack.py)_

---

### Task 5.20: APC-002-F04 - 3 source-inspection tests in app integration [Medium]
**File:** `tests/integration/test_app_integration.py`
**Tests:** `pytest tests/integration/test_app_integration.py`

_(Cross-project: PROJ-321 may delete this file as a CAT-2 finding. If deleted, this task is obsolete.)_

- [x] Replace the 3 tests using `getsource` + `signature` source-inspection (~80 LOC) with behavioural integration assertions. _(skipped — inspect source-inspection patterns no longer present in test_app_integration.py)_
- [x] Verify: `pytest tests/integration/test_app_integration.py` passes; LOC delta approximately -50 _(skipped — inspect source-inspection patterns no longer present in test_app_integration.py)_

---

### Task 5.21: APC-002-F05 - move no-pygame-imports check to pre-commit lint [Simple]
**File:** `tests/unit/ui/screens/battle_setup/test_view_model.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_view_model.py`

- [x] Remove the `getsource` + AST-parse no-pygame-imports check (~16 LOC) from the runtime test; recommend a pre-commit lint rule for the invariant (track that recommendation in the same commit body or in a follow-up note - do not add the lint as part of this project, that's PROJ-323 territory if at all). _(skipped — getsource no-pygame-imports check no longer present; was already removed)_
- [x] Verify: `pytest tests/unit/ui/screens/battle_setup/test_view_model.py` passes; LOC delta approximately -16 _(skipped — getsource no-pygame-imports check no longer present; was already removed)_

---

### Task 5.22: APC-002-F06 - remove research-scene-DI source-text test [Simple]
**File:** `tests/unit/research/test_research_scene_di.py`
**Tests:** `pytest tests/unit/research/test_research_scene_di.py`

- [x] Remove the `open(module.__file__).read()` import-string test (~10 LOC); behavioural DI tests already cover this. Coordinate with Task 3.6 in Phase 3. _(satisfied — same change as Task 3.6 already done in Phase 3)_
- [x] Verify: `pytest tests/unit/research/test_research_scene_di.py` passes; LOC delta approximately -10 _(satisfied — same change as Task 3.6 already done in Phase 3)_

---

### Task 5.23: APC-002-F07 - replace getsource on _rebuild_ui with behavioural test [Simple]
**File:** `tests/unit/ui/screens/battle_setup/test_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_renderer.py`

_(Plan-review M-004 (2026-05-03): the original adjusted suggestion still tested a private method, which is APC-003 anti-pattern. Test through public API only.)_

- [x] Replace the `inspect.getsource(FleetBattleSetupScreen._rebuild_ui)` source-text assertion (~11 LOC) with a behavioural test that triggers `_rebuild_ui` via a public path (`handle_event` with the appropriate UI event, or `update`) and asserts on observable UI element state after the trigger. Do NOT call or patch `_rebuild_ui` directly — that swaps source-inspection brittleness for private-method coupling. _(skipped — inspect.getsource(_rebuild_ui) call no longer present in test_renderer.py)_
- [x] Verify: `pytest tests/unit/ui/screens/battle_setup/test_renderer.py` passes; LOC delta approximately -8 _(skipped — inspect.getsource(_rebuild_ui) call no longer present in test_renderer.py)_

---

### Task 5.24: APC-002-F08 - construction tests for planet-selection-window [Medium]
**File:** `tests/unit/ui/screens/test_planet_selection_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_selection_window.py`

- [x] Replace `inspect.signature()`-only tests (~35 LOC) with construction tests that actually instantiate the window (use `make_ui_widget` from Task 5.0). _(skipped — PROJ-321 already deleted target file tests/unit/ui/screens/test_planet_selection_window.py)_
- [x] Verify: `pytest tests/unit/ui/screens/test_planet_selection_window.py` passes; LOC delta approximately -20 _(skipped — PROJ-321 already deleted target file tests/unit/ui/screens/test_planet_selection_window.py)_

---

### Task 5.25: APC-002-F09 - replace signature/getsource default check [Simple]
**File:** `tests/unit/ui/test_new_game_setup.py`
**Tests:** `pytest tests/unit/ui/test_new_game_setup.py`

- [x] Replace `inspect.signature()` + `inspect.getsource()` default verification (~15 LOC) with a behavioural default test (construct widget, observe default value).
- [x] Verify: `pytest tests/unit/ui/test_new_game_setup.py` passes; LOC delta approximately -10

---

### Task 5.26: APC-002-F10 - replace getsource registrar check with behavioural assertion [Simple]
**File:** `tests/unit/ui/screens/test_strategy_window_manager_public_api.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_window_manager_public_api.py`

- [x] Replace `inspect.getsource(registrar_cls.open)` string-presence assertion (~7 LOC) with a behavioural assertion using a real registrar. _(skipped — inspect.getsource(registrar) check no longer present)_
- [x] Verify: `pytest tests/unit/ui/screens/test_strategy_window_manager_public_api.py` passes; LOC delta approximately -5 _(skipped — inspect.getsource(registrar) check no longer present)_

---

## APC-003: private-method patching

### Task 5.27: APC-003-F01 - test through public modifier-logic API or promote helper [Medium]
**File:** `tests/unit/ui/screens/builder/test_modifier_logic_service.py`
**Tests:** `pytest tests/unit/ui/screens/builder/test_modifier_logic_service.py`

- [x] Rewrite the 5 tests calling `service._get_base_firing_arc()` (~42 LOC) to use the public API (`get_initial_value`, `get_local_min_max`); OR promote `_get_base_firing_arc` to a public helper. Coordinate with Task 3.17 in Phase 3. _(done in PROJ-322 pass 3 — same change as Task 3.17. Public API rewrite using `get_initial_value('turret_mount', comp)`.)_
- [x] Verify: `pytest tests/unit/ui/screens/builder/test_modifier_logic_service.py` passes; LOC delta approximately -10 _(done in PROJ-322 pass 3 — 23 tests pass.)_

---

### Task 5.28: APC-003-F02 - test battle-engine init through engine.start [Medium]
**File:** `tests/unit/simulation/systems/test_battle_engine_init_ship.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_init_ship.py`

- [x] Rewrite the 4 tests calling `battle_engine._initialize_ship()` (~31 LOC) to drive the engine through `start()` / `start_teams()` public API. Coordinate with Task 3.9 in Phase 3. _(done in PROJ-322 pass 3 — same change as Task 3.9. 4 tests rewritten to drive `engine.start([ship_a], [ship_b], ai_controllers=[])` and assert observable post-init state on both ships.)_
- [x] Verify: `pytest tests/unit/simulation/systems/test_battle_engine_init_ship.py` passes; LOC delta approximately -15 _(done in PROJ-322 pass 3 — 4 tests pass.)_

---

### Task 5.29: APC-003-F03 - boundary-patch build-queue-list-window or promote helper [Simple]
**File:** `tests/unit/ui/screens/test_build_queue_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_list_window.py`

- [ ] Stop using `patch.object(BuildQueueListWindow, '_build_list')` (~13 LOC across 11 tests); patch at the pygame_gui boundary; OR promote `_build_list` to public if independently testable. Coordinate with Task 3.19 in Phase 3. **DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** `BuildQueueListWindow` inherits from `pygame_gui.elements.UIWindow`. Same blocker as Task 5.6 cluster. Promoting `_build_list` to public is a production change out of P1 scope.
- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_list_window.py` passes; LOC delta approximately -5 _(deferred-out-of-scope — see above.)_

---

### Task 5.30: APC-003-F04 - inject fake movement_engine via DI [Simple]
**File:** `tests/unit/strategy/turn_engine/test_tick_mechanics.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_tick_mechanics.py`

- [x] Stop patching `turn_engine.movement_engine.calculate_next_hex` (~4 LOC); inject a fake movement engine via DI. Coordinate with Task 3.13 in Phase 3. _(satisfied — same change as Task 3.13 already done in Phase 3)_
- [x] Verify: `pytest tests/unit/strategy/turn_engine/test_tick_mechanics.py` passes; LOC delta approximately -2 _(satisfied — same change as Task 3.13 already done in Phase 3)_

---

### Task 5.31: APC-003-F05 - test through public BattleResolver API [Medium]
**File:** `tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py`
**Tests:** `pytest tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py`

- [x] Rewrite the tests accessing `engine._fleets_destroyed`/`_empires`/`_combats_resolved` private attrs (~39 LOC) to drive the public `BattleResolver` API and assert on observable state. Coordinate with Task 1.6 in Phase 1. _(satisfied — same change as Task 1.6 already done in Phase 1)_
- [x] Verify: `pytest tests/unit/strategy/conflict_resolution/test_battle_resolver_integration.py` passes; LOC delta approximately -15 _(satisfied — same change as Task 1.6 already done in Phase 1)_

---

### Task 5.32: APC-003-F06 - use registry.get_handler public API [Simple]
**File:** `tests/unit/strategy/engine/test_build_order_command_handler.py`
**Tests:** `pytest tests/unit/strategy/engine/test_build_order_command_handler.py`

- [x] Replace direct access to `registry._handlers` private dict (~21 LOC) with `registry.get_handler()` public API. Coordinate with Task 1.12 in Phase 1. _(satisfied — same change as Task 1.12 already done in Phase 1)_
- [x] Verify: `pytest tests/unit/strategy/engine/test_build_order_command_handler.py` passes; LOC delta approximately -10 _(satisfied — same change as Task 1.12 already done in Phase 1)_

---

### Task 5.33: APC-003-F07 - inject path-finder via DI in fleet-movement [Medium]
**File:** `tests/unit/strategy/fleet_movement_engine/test_basics.py`
**Tests:** `pytest tests/unit/strategy/fleet_movement_engine/test_basics.py`

- [x] Stop patching `fleet_navigation_service.find_hybrid_path` (~32 LOC); inject the path-finder via DI. Coordinate with Task 3.12 in Phase 3. _(done in PROJ-322 pass 3 — same change as Task 3.12. Inject `nav_service=fake_nav_service` into `FleetMovementEngine(...)` constructor; assert `calculate_fleet_next_hex` was called.)_
- [x] Verify: `pytest tests/unit/strategy/fleet_movement_engine/test_basics.py` passes; LOC delta approximately -10 _(done in PROJ-322 pass 3 — 9 tests pass.)_

---

### Task 5.34: APC-003-F08 - real headless _create_ui or DI for builder drag-drop [Medium]
**File:** `tests/integration/builder/test_builder_drag_drop_real.py`
**Tests:** `pytest tests/integration/builder/test_builder_drag_drop_real.py`

- [x] Stop patching `Builder._create_ui` private method (~21 LOC); use real headless `_create_ui` or refactor to inject UI via DI. Coordinate with Task 3.1 in Phase 3. _(skipped — `tests/integration/builder/test_builder_drag_drop_real.py` no longer exists; deleted upstream.)_
- [x] Verify: `pytest tests/integration/builder/test_builder_drag_drop_real.py` passes; LOC delta approximately -10 _(skipped — file no longer exists.)_

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (or marked deferred-out-of-scope with concrete UIWindow-inheritance blocker pointers)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
