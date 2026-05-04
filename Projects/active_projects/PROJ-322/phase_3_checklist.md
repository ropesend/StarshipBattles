# Phase 3: CAT-6 Mocking Brittleness

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-322 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (12 done in passes 1-3 — pass 3 added 5; 7 obsolete (target files deleted upstream); 7 formally deferred-out-of-scope — UIWindow-inheritance cluster + multi-day production refactors. PROJ-322 pass 3 verified)
**Objective:** Reduce the 26 verified CAT-6 brittle-mocking patterns by patching at public boundaries instead of private internals.

---

## Tasks

### Task 3.1: Boundary-patch builder drag-drop UI [Medium]
**File:** `tests/integration/builder/test_builder_drag_drop_real.py`
**Tests:** `pytest tests/integration/builder/test_builder_drag_drop_real.py`

- [x] S11-CAT6-004: stop patching `DesignWorkshopScreen._create_ui` (lines 29, 55-65) and the 10 manual mock-attr assignments. Use real headless `_create_ui` or refactor to inject UI via DI. Coordinate with APC-003-F08 in Phase 5. _(skipped — `tests/integration/builder/test_builder_drag_drop_real.py` no longer exists; deleted upstream by PROJ-321 cleanup. Pre-flight `ls` confirms file is gone.)_
- [x] Verify: `pytest tests/integration/builder/test_builder_drag_drop_real.py` passes; LOC delta approximately -15 _(skipped — file no longer exists.)_

---

### Task 3.2: Decouple AI attack-run test from approach_distance constant [Simple]
**File:** `tests/unit/ai/test_ai.py`
**Tests:** `pytest tests/unit/ai/test_ai.py`

- [x] S01-CAT6-001: rewrite `test_attack_run_transitions_to_retreat` (lines 228-237) to mock `weapon_range` to a known value or set ship position relative to the calculated threshold instead of hard-coding `(0,0)`/`(150,0)`.
- [x] Verify: `pytest tests/unit/ai/test_ai.py` passes; LOC delta approximately -2

---

### Task 3.3: Convert multi-selection autouse to value-returning fixtures [Medium]
**File:** `tests/unit/builder/test_multi_selection_logic.py`
**Tests:** `pytest tests/unit/builder/test_multi_selection_logic.py`

- [x] S02-CAT6-004: rewrite the autouse setup (lines 10-50) that sets attributes on `self` to a standard fixture returning test objects (or a helper function); this removes the parallel-run fragility. _(done in PROJ-322 pass 3 — converted autouse `setup` to a value-returning `selection_setup` fixture wrapping `_MultiSelectionFixture` dataclass. 3 tests refactored.)_
- [x] Verify: `pytest tests/unit/builder/test_multi_selection_logic.py` passes; LOC delta approximately -10 _(done in PROJ-322 pass 3 — 3 tests pass; net code shape replaces self-mutation with explicit fixture parameter.)_

---

### Task 3.4: Replace inline MockComponent with MagicMock(stats=...) [Medium]
**File:** `tests/unit/modifiers/test_seeker_weapon_bindings.py`
**Tests:** `pytest tests/unit/modifiers/test_seeker_weapon_bindings.py`

- [x] S09-CAT6-003: replace each inline `class MockComponent` definition (lines 103-193, 4 occurrences with only the `stats` dict differing) with `MagicMock(stats={...})`. Coordinate with CAT-4 cleanup (Task 1.2).
- [x] Verify: `pytest tests/unit/modifiers/test_seeker_weapon_bindings.py` passes; LOC delta approximately -55

---

### Task 3.5: Replace research-scene reset call-sequence asserts with state asserts [Complex]
**File:** `tests/unit/research/research_scene/test_reset_state.py`
**Tests:** `pytest tests/unit/research/research_scene/test_reset_state.py`

- [x] S09-CAT6-002: rewrite the 6 tests (lines 17-31, 76-188) to assert observable post-reset state of a real `ResearchControlPanel`; remove `_create_mock_panel` lambda binding and the call-sequence assertions on `clear_selection`/`update_budget_display`/etc. _(skipped — `tests/unit/research/research_scene/test_reset_state.py` no longer exists; deleted upstream.)_
- [x] Verify: `pytest tests/unit/research/research_scene/test_reset_state.py` passes; LOC delta approximately -80 _(skipped — file no longer exists.)_

---

### Task 3.6: Remove source-text camera-import test [Simple]
**File:** `tests/unit/research/test_research_scene_di.py`
**Tests:** `pytest tests/unit/research/test_research_scene_di.py`

- [x] S06-CAT6-001: delete `test_camera_import_is_direct` (lines 88-97); behavioural DI tests already cover Camera injection. Coordinate with APC-002-F06 in Phase 5.
- [x] Verify: `pytest tests/unit/research/test_research_scene_di.py` passes; LOC delta approximately -10

---

### Task 3.7: Extract _make_projectile helper for CCD tests [Complex]
**File:** `tests/unit/simulation/projectile/test_ccd.py`
**Tests:** `pytest tests/unit/simulation/projectile/test_ccd.py`

- [x] S08-CAT6-001: extract a `_make_projectile(**overrides)` helper (or use real `Projectile` / sparse spec); avoid hand-wiring 15-attr MagicMocks per test (lines 23-376). _(skipped — `tests/unit/simulation/projectile/test_ccd.py` no longer exists; deleted upstream.)_
- [x] Verify: `pytest tests/unit/simulation/projectile/test_ccd.py` passes; LOC delta approximately -100 _(skipped — file no longer exists.)_

---

### Task 3.8: Replace mock-delegate validator tests with behavioural ones [Medium]
**File:** `tests/unit/simulation/services/test_validation_service.py`
**Tests:** `pytest tests/unit/simulation/services/test_validation_service.py`

- [x] S11-CAT6-003: replace the 4 mock-delegation tests (lines 14-100) with behavioural tests exercising the real validator chain; keep `test_service_creates_default_validator_when_none_provided`. _(skipped — `tests/unit/simulation/services/test_validation_service.py` no longer exists; deleted upstream.)_
- [x] Verify: `pytest tests/unit/simulation/services/test_validation_service.py` passes; LOC delta approximately -50 _(skipped — file no longer exists.)_

---

### Task 3.9: Drive battle-engine init through public API [Medium]
**File:** `tests/unit/simulation/systems/test_battle_engine_init_ship.py`
**Tests:** `pytest tests/unit/simulation/systems/test_battle_engine_init_ship.py`

- [x] S02-CAT6-002: rewrite the 4 tests at lines 65, 73, 82, 90 to drive the engine via `start()` / `start_teams()` instead of calling `battle_engine._initialize_ship(ship)`. Coordinate with APC-003-F02 in Phase 5. _(done in PROJ-322 pass 3 — 4 tests rewritten to drive `engine.start([ship_a], [ship_b], ai_controllers=[])`. Renamed class to `TestStartInitializesEachShip`. Each test now also asserts on the second ship to prove parity across both teams.)_
- [x] Verify: `pytest tests/unit/simulation/systems/test_battle_engine_init_ship.py` passes; LOC delta approximately -15 _(done in PROJ-322 pass 3 — 4 tests pass; net -2 LOC after dropping the explicit fixture.)_

---

### Task 3.10: Refactor or document build-order auto-completion entry point [Medium]
**File:** `tests/unit/strategy/engine/test_build_order_processor.py`
**Tests:** `pytest tests/unit/strategy/engine/test_build_order_processor.py`

- [x] S10-CAT6-001 (NEEDS_REWORK): refactor `test_build_order_auto_completes_when_queue_empties` (lines 60-81) to use `OrderProcessor.execute_action_order` public boundary; OR add a clear docstring explaining why `ActionExecutionEngine.process_action_ticks` is the correct entry point and document the design intent. _(verification adjusted from review's "Test through OrderProcessor.execute_action_order public boundary" - see verification_report.md)_ _(done in PROJ-322 pass 3 — chose the documentation path: strengthened docstring to explain that BUILD auto-pop is owned by `ActionExecutionEngine.process_action_ticks` (the post-tick sweep), not `execute_action_order` (the per-order dispatcher). The alternative would test a code path the engine never takes.)_
- [x] Verify: `pytest tests/unit/strategy/engine/test_build_order_processor.py` passes; LOC delta approximately -10 (if refactored) or 0 (if documented) _(done in PROJ-322 pass 3 — 6 tests pass; LOC delta 0 (docstring only).)_

---

### Task 3.11: Accept positional-or-keyword in superweapon-stabilizers assert [Simple]
**File:** `tests/unit/strategy/engine/test_superweapon_stabilizers.py`
**Tests:** `pytest tests/unit/strategy/engine/test_superweapon_stabilizers.py`

- [x] S03-CAT6-001: replace `assert sentinel in mock_find.call_args.args` (lines 89-92) with a `call_args_list` comprehension accepting either positional or kwargs - matches the documented intent.
- [x] Verify: `pytest tests/unit/strategy/engine/test_superweapon_stabilizers.py` passes; LOC delta approximately 0

---

### Task 3.12: Inject path-finder via DI in fleet-movement basics [Medium]
**File:** `tests/unit/strategy/fleet_movement_engine/test_basics.py`
**Tests:** `pytest tests/unit/strategy/fleet_movement_engine/test_basics.py`

- [x] S08-CAT6-002: stop patching `fleet_navigation_service.find_hybrid_path` in `test_recalculates_path_if_destination_changed` (lines 77-108); inject a fake path-finder via DI. Coordinate with APC-003-F07 in Phase 5. _(done in PROJ-322 pass 3 — pass `nav_service=fake_nav_service` to `FleetMovementEngine(...)` constructor and assert that `calculate_fleet_next_hex` was called on the injected service. No more module-level patch.)_
- [x] Verify: `pytest tests/unit/strategy/fleet_movement_engine/test_basics.py` passes; LOC delta approximately -10 _(done in PROJ-322 pass 3 — 9 tests pass.)_

---

### Task 3.13: Inject fake movement_engine instead of patching dispatch [Simple]
**File:** `tests/unit/strategy/turn_engine/test_tick_mechanics.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_tick_mechanics.py`

- [x] S05-CAT6-003: stop patching `turn_engine.movement_engine.calculate_next_hex` (lines 149, 177); inject a fake `movement_engine` via DI. Coordinate with APC-003-F04 in Phase 5.
- [x] Verify: `pytest tests/unit/strategy/turn_engine/test_tick_mechanics.py` passes; LOC delta approximately -2

---

### Task 3.14: Move pygame_gui patches to module-scoped autouse for virtual-table [Medium]
**File:** `tests/unit/ui/components/table/test_virtual_table.py`
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py`

- [ ] S11-CAT6-001: move the 5 `@patch` decorators (UIImage, UILabel, UIVerticalScrollBar, UIPanel, TableHeader) from each method (lines 78-82) into a class-level or module-scoped autouse fixture; 12+ tests share them. **DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** the file has 81 `@patch` decorators across 17 tests; tests substantively manipulate the patch-injected mocks (`return_value=`, `side_effect=`, `assert_called`). Converting to an autouse fixture requires rewriting every test signature and the mock-access pattern (fixture would need to return a NamedTuple of mocks). Net change spans ~700 LOC of test code with high regression risk. Worth a dedicated session if cycle-time benefit is measured to be substantial.
- [ ] Verify: `pytest tests/unit/ui/components/table/test_virtual_table.py` passes; LOC delta approximately -50 _(deferred-out-of-scope — see above.)_

---

### Task 3.15: Replace empire-treasury private-attr asserts with public refresh asserts [Simple]
**File:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`

- [ ] S05-CAT6-001: rewrite `test_refresh_clears_old_elements` (lines 419-437) to verify observable behaviour of `refresh()`; remove `panel._elements` / `panel._scroll_container` private-attr access. **DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** the test specifically verifies that the panel cleans up its internal element-tracking lists when refreshed. With pygame_gui mocked out (no real renderable surfaces), there is no observable side effect to assert other than the internal `_elements`/`_scroll_container` lists. Public `refresh()` returns None; the only contract worth verifying without internals is "old container.kill() was called", which is already in the test. Removing the private-attr read would weaken the test rather than improve it.
- [ ] Verify: `pytest tests/unit/ui/panels/test_empire_treasury_panel.py` passes; LOC delta approximately -5 _(deferred-out-of-scope — see above.)_

---

### Task 3.16: Assert on cloned ship attributes, not ShipInstance.create kwargs [Simple]
**File:** `tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py`

- [x] S01-CAT6-002: rewrite `test_clone_ship_calls_ship_instance_create` (lines 81-98) to verify the cloned ship's attributes; remove `ShipInstance.create` mock + kwargs assertion.
- [x] Verify: `pytest tests/unit/ui/screens/battle_setup/test_fleet_hierarchy_editor.py` passes; LOC delta approximately -5

---

### Task 3.17: Promote `_get_base_firing_arc` to public surface or test through public API [Medium]
**File:** `tests/unit/ui/screens/builder/test_modifier_logic_service.py`
**Tests:** `pytest tests/unit/ui/screens/builder/test_modifier_logic_service.py`

- [x] S02-CAT6-001: rewrite the 5 tests in `TestGetBaseFiringArc` (lines 47, 57, 67, 73, 84) to use the public API (`get_initial_value`, `get_local_min_max`); OR promote `_get_base_firing_arc` to a public helper. Coordinate with APC-003-F01 in Phase 5. _(done in PROJ-322 pass 3 — chose the public-API path: rewrote 5 tests to call `service.get_initial_value('turret_mount', comp)` (which internally consumes `_get_base_firing_arc`). The "no arc found" test now asserts the public fallback to `mod_def.min_val` instead of None, which is the observable behaviour callers rely on. Class fixture extended with the `turret_mount` mod_def.)_
- [x] Verify: `pytest tests/unit/ui/screens/builder/test_modifier_logic_service.py` passes; LOC delta approximately -10 _(done in PROJ-322 pass 3 — 23 tests pass.)_

---

### Task 3.18: Replace patch.dict(sys.modules) with targeted patch.object [Medium]
**File:** `tests/unit/ui/screens/test_battle_panels_extended.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_panels_extended.py`

- [x] S11-CAT6-002: replace `patch.dict(sys.modules, {'pygame': mock_pygame})` + `importlib.reload(battle_panels)` (lines 48-49) with targeted `patch.object` on specific pygame paths; eliminates state leakage between classes that share the module reference. _(skipped — `tests/unit/ui/screens/test_battle_panels_extended.py` no longer exists; deleted upstream.)_
- [x] Verify: `pytest tests/unit/ui/screens/test_battle_panels_extended.py` passes; LOC delta approximately -2 _(skipped — file no longer exists.)_

---

### Task 3.19: Patch at boundary instead of `_build_list` private method [Simple]
**File:** `tests/unit/ui/screens/test_build_queue_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_list_window.py`

- [ ] S05-CAT6-002: stop patching `BuildQueueListWindow._build_list` in `mock_window_base` (lines 10-13, 28); patch at the pygame_gui boundary, or promote `_build_list` to public if independently testable. 11 tests depend on this fixture. Coordinate with APC-003-F03 in Phase 5. **DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** `BuildQueueListWindow` inherits from `pygame_gui.elements.UIWindow`; the `mock_window_base` fixture patches both UIWindow.__init__ AND _build_list because the make_ui_widget factory cannot bypass the super-init chain (same blocker as Phase 5 Tasks 5.6/5.7/5.10/5.11/5.12/5.16). Promoting `_build_list` is a production change out of P1 scope.
- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_list_window.py` passes; LOC delta approximately -5 _(deferred-out-of-scope — see above.)_

---

### Task 3.20: Extract patch chain helper for fleet-report-window-multi-select [Complex]
**File:** `tests/unit/ui/screens/test_fleet_report_window_multi_select.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_window_multi_select.py`

- [ ] S03-CAT6-001b: extract the 3-5 nested `with patch()` blocks (lines 76-117, 148-178, 234-268, 389-427) into a single helper; prefer patching at service boundary instead of `_init_layout`/`refresh_list` private methods. Coordinate with APC-001-F07 in Phase 5. **DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** depends on Task 5.7 unblocking. `FleetReportWindow` inherits `StrategyModalWindow → UIWindow`; the make_ui_widget factory cannot bypass the super-init chain. The boundary-patching half (replacing `_init_layout`/`refresh_list` private patches with service-boundary patches) requires coordinating with the production service-interface refactor that's out of P1 scope.
- [ ] Verify: `pytest tests/unit/ui/screens/test_fleet_report_window_multi_select.py` passes; LOC delta approximately -50 _(deferred-out-of-scope — see above.)_

---

### Task 3.21: Use real `__init__` for new-game-setup-extended screen [Medium]
**File:** `tests/unit/ui/screens/test_new_game_setup_extended.py`
**Tests:** `pytest tests/unit/ui/screens/test_new_game_setup_extended.py`

- [ ] S08-CAT6-003: rewrite `_make_screen` (lines 16-49) to construct via real `__init__` with mocked pygame_gui dependencies; eliminate the manual 16+ attribute wiring. Coordinate with APC-001-F12 in Phase 5. **DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** `NewGameSetupScreen` inherits `pygame_gui.elements.UIWindow`; the make_ui_widget factory cannot patch through the `super().__init__()` chain (same root cause as Phase 5 Task 5.12). Tracked alongside the UIWindow inheritance cluster.
- [ ] Verify: `pytest tests/unit/ui/screens/test_new_game_setup_extended.py` passes; LOC delta approximately -20 _(deferred-out-of-scope — see above.)_

---

### Task 3.22: Note bypass-init convention for planet-list-window [Simple]
**File:** `tests/unit/ui/screens/test_planet_list_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_window.py`

- [x] S10-CAT6-002: keep current shape (the deep mocking of PlanetReportPanel/`compute_planet_production`/UIButton at lines 71-111 follows the project bypass-init convention). Add a note pointing to Phase 5 APC-001 cleanup, to be revisited when the bypass-init pattern is consolidated globally.
- [x] Verify: `pytest tests/unit/ui/screens/test_planet_list_window.py` passes; LOC delta approximately 0 (note only)

---

### Task 3.23: Drive selection via real pygame_gui events for save-selection [Medium]
**File:** `tests/unit/ui/screens/test_save_selection.py`
**Tests:** `pytest tests/unit/ui/screens/test_save_selection.py`

- [x] S09-CAT6-001: rewrite `test_buttons_enable_after_selection` (lines 274-327) to drive selection through real pygame_gui events; assert observable button state. Remove mutation of `first_item['selected']` and the `_handle_selection_change()` private call. _(skipped — `tests/unit/ui/screens/test_save_selection.py` no longer exists; deleted upstream.)_
- [x] Verify: `pytest tests/unit/ui/screens/test_save_selection.py` passes; LOC delta approximately -10 _(skipped — file no longer exists.)_

---

### Task 3.24: Use real headless pygame_gui session for strategy-modal-window [Medium]
**File:** `tests/unit/ui/screens/test_strategy_modal_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_modal_window.py`

- [ ] S08-CAT6-004: rewrite `_make_modal_window` (lines 16-37) to use a real headless pygame_gui session; remove the `pygame_gui.elements.UIWindow.__init__` lambda patch and the manual base-init call. **DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** `StrategyModalWindow` IS the UIWindow subclass that's the root cause of the Phase 5 cluster of deferrals. The "real headless pygame_gui session" approach requires either an integration-test harness (out of unit-test scope) OR factory enhancement to patch the super-init chain. The current shape is the canonical workaround.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_modal_window.py` passes; LOC delta approximately -15 _(deferred-out-of-scope — see above.)_

---

### Task 3.25: Test strategy-screen public surface [Complex]
**File:** `tests/unit/ui/screens/test_strategy_screen.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_screen.py`

- [ ] S02-CAT6-003: rewrite `_make_strategy_screen` (lines 66-74) and the ~50 dependent tests to assert observable outcomes from public methods (`update`, `draw`, `handle_event`, `handle_resize`, `handle_click`); drop the `__new__` bypass-init that injects MagicMock for 8 internal sub-objects. (Big change; consider splitting into sub-PRs.) **DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** the task's own description acknowledges this is a "big change; consider splitting into sub-PRs". The 50 dependent tests + 8 sub-objects make this a multi-day production refactor that wholly exceeds the P1 polish scope. Tracked as a candidate standalone follow-up project.
- [ ] Verify: `pytest tests/unit/ui/screens/test_strategy_screen.py` passes; LOC delta approximately -200 _(deferred-out-of-scope — see above.)_

---

### Task 3.26: Real construction for sub-window hotkey tests [Complex]
**File:** `tests/unit/ui/screens/test_sub_window_hotkeys.py`
**Tests:** `pytest tests/unit/ui/screens/test_sub_window_hotkeys.py`

- [ ] S12-CAT6-001: rewrite the constructor-bypass pattern (lines 36-294) for `OrdersWindow`/`BuildQueueScreen`/`TransferDialog`/`BuildQueueListWindow` to use real construction with mocked pygame_gui; or refactor windows so hotkey logic lives in a separately testable module. Coordinate with APC-001-F16 in Phase 5. **DEFERRED-OUT-OF-SCOPE (PROJ-322 pass 3):** all four target classes inherit from `pygame_gui.elements.UIWindow` (or `StrategyModalWindow`); the make_ui_widget factory cannot bypass the super-init chain (same root cause as Task 5.16 and the entire Phase 5 deferred cluster). The alternative — extracting hotkey logic into a separate module — is a production refactor out of P1 scope.
- [ ] Verify: `pytest tests/unit/ui/screens/test_sub_window_hotkeys.py` passes; LOC delta approximately -150 _(deferred-out-of-scope — see above.)_

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (or marked deferred-out-of-scope with concrete blockers)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source review: `Reviews/results/2026-05-02_204633_test-review/`. See `findings/source_review.md` for the link._
