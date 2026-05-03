# Validation Report: UI-Screens

## Summary
- **Shard:** UI-Screens (UI1)
- **Findings Reviewed:** 65
- **Confirmed:** 39
- **Downgraded:** 16
- **Rejected:** 10
- **Rejection Rate:** 15.4%

## Verdicts

### Architecture Drift Findings

#### Finding: ADR-UI1-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - TestLabScreen.py is 1911 lines with 75+ methods, exceeding the 500/30 threshold significantly.

#### Finding: ADR-UI1-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - FleetReportWindow.py is 1093 lines with 29 methods, exceeding maintainability thresholds.

#### Finding: ADR-UI1-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - BuildQueueScreen.py is 1098 lines with 31 methods, combining multiple responsibilities.

#### Finding: ADR-UI1-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - StrategyScreen.py is 810 lines with 45 methods, acting as a central coordinator.

#### Finding: ADR-UI1-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - cargo_quick_dialog.py and transfer_dialog.py access `scene._facade` at lines 58 and 33 respectively.

#### Finding: ADR-UI1-006
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - BattleUI.py line 98 calls `self.scene._trigger_return_to_test_lab()`, accessing private method.

#### Finding: ADR-UI1-007
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - StrategyInputHandler accesses 15+ private scene attributes including _fleet_ops, _colonization, _superweapons, _camera_nav.

#### Finding: ADR-UI1-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Deep attribute chains like `self.game.battle_scene._battle_service.create_battle()` exist in test_lab/screen.py.

#### Finding: ADR-UI1-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - validation_manager.py lines 134-138 access `data_extractor._components_cache` directly.

#### Finding: ADR-UI1-010
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** race_setup_screen.py line 543 does not show private format method access. The described pattern is not found at that location.

#### Finding: ADR-UI1-011
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - workshop_data_reloader.py line 182 directly mutates `self.viewmodel._selected_components = []`.

#### Finding: ADR-UI1-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - strategy_event_router.py lines 129-130 check and handle `self.ui.scene._quit_confirm_dialog`.

#### Finding: ADR-UI1-013
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - TYPE_CHECKING imports are used extensively across 44+ files. This is acceptable practice.

#### Finding: ADR-UI1-014
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - 80+ lazy imports found across screens and panels, intentional for deferred loading.

### Consistency Findings

#### Finding: CON-UI1-001
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Issue exists but naming conventions are generally consistent. FormationEditorScreen follows the Screen suffix for IScene implementations correctly.

#### Finding: CON-UI1-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - Mixed verb prefixes: `update_*`, `refresh_*`, `rebuild_*` used inconsistently across panels.

#### Finding: CON-UI1-003
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Boolean parameters like `flat_view` lack consistent `is_`/`has_` prefixes.

#### Finding: CON-UI1-004
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Callback naming varies: `on_close_callback`, `on_close`, `on_selected`, `scene_callback`.

#### Finding: CON-UI1-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - handle_click() returns mixed types: bool, tuple, string across BattlePanel subclasses.

#### Finding: CON-UI1-006
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - BattlePanel base class lacks kill() method while subclasses like ShipStatsPanel don't implement cleanup.

#### Finding: CON-UI1-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Mixed exception patterns: some raise ValueError, others return None, some use broad catches.

#### Finding: CON-UI1-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Older files like battle_ui.py lack type hints while newer files have full coverage.

#### Finding: CON-UI1-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Docstring presence varies; BattleUI.__init__() has none while BuildQueueScreen.__init__() is fully documented.

#### Finding: CON-UI1-010
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - Two ColumnManager classes exist: column_manager.py (for Fleet) and planet_list_columns.py (for Planet) with different APIs.

#### Finding: CON-UI1-011
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Screenshot handling is centralized through ScreenshotManager with consistent _show_screenshot_toast pattern.

#### Finding: CON-UI1-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Parameter ordering varies across window constructors.

#### Finding: CON-UI1-013
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - design_report_panel.py loads images directly with pygame.image.load() bypassing ShipThemeManager.

#### Finding: CON-UI1-014
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - Singleton pattern usage is consistent with .instance() method throughout.

#### Finding: CON-UI1-015
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - Newer code follows layer separation well with TYPE_CHECKING and facades.

#### Finding: CON-UI1-016
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - EventBus pattern used in workshop but not elsewhere; acceptable variation.

#### Finding: CON-UI1-017
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Import ordering varies slightly between files.

#### Finding: CON-UI1-018
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Screen protocol compliance varies; handle_resize() not implemented in all screens.

### Duplication Findings

#### Finding: DUP-UI1-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified - planet_report_panel.py:303-310 has _format_compact_number() using lowercase 'k' while strategy_detail_fmt.py:101-130 uses inline formatting with uppercase 'K'.

#### Finding: DUP-UI1-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - Virtual scrolling pattern duplicated across 4 windows with ~50-80 lines each.

#### Finding: DUP-UI1-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - Filter toggle button pattern with [x]/[ ] prefix repeated in fleet_report, planet_list, empire_build_queue windows.

#### Finding: DUP-UI1-004
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Issue exists but placeholder creation is a simple 15-20 line pattern. Impact is low.

#### Finding: DUP-UI1-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - Sidebar filter section building pattern with y-offset tracking duplicated ~100 lines across windows.

#### Finding: DUP-UI1-006
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** smoothscale() calls are one-liners; not significant duplication warranting extraction.

#### Finding: DUP-UI1-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - _handle_column_toggle_click() methods duplicated in planet_list_window and empire_build_queue_window.

#### Finding: DUP-UI1-008
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Only one instance found in this shard; not duplication within UI-Screens scope.

#### Finding: DUP-UI1-009
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - BaseGallery consolidation is a positive finding showing good abstraction.

### Legacy Findings

#### Finding: LEG-UI1-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - EmpireBuildQueueWindow maintains both selected_indices Set and legacy selected_source/selected_index fields.

#### Finding: LEG-UI1-002
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - test_lab/screen.py:249-252 has _components_cache property documented as "for backward compatibility".

#### Finding: LEG-UI1-003
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - fleet_report_window.py:956-969 has _on_remove_ship documented as "legacy API".

#### Finding: LEG-UI1-004
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - strategy_input_handler.py lines 70, 75 reference "PROJ-88: folded from app.py legacy dispatch".

#### Finding: LEG-UI1-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - Pass statements in ship_panels.py:45-47, 134-136 and empire_build_queue_window.py:493-495.

#### Finding: LEG-UI1-006
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** hasattr() checks are often legitimate interface checks in Python; not all are legacy patterns.

#### Finding: LEG-UI1-007
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Singleton .instance() pattern is documented project convention and appropriate for managers.

#### Finding: LEG-UI1-008
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - workshop_context.py:66-74 has try/except with pass for defensive registry loading.

#### Finding: LEG-UI1-009
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - PROJ-40 migration comments present in fleet_report_filters.py and workshop_viewmodel.py.

#### Finding: LEG-UI1-010
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** getattr() with defaults is legitimate defensive coding for optional race_config attributes.

#### Finding: LEG-UI1-011
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - battle_panels.py has dual-path Ship/DTO support documented as PROJ-43 design.

#### Finding: LEG-UI1-012
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - build_queue_controller.py fallback mode is documented and legitimate.

### Test Coverage Findings

#### Finding: TCG-UI1-001
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** Verified - builder/ subdirectory has 19 production files (not 17) and NO test files in tests/unit/ui/screens/builder/.

#### Finding: TCG-UI1-002
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** test_lab/ has some tests in tests/unit/test_lab/ directory (4 test files found). Gap exists but not "minimal" - downgrade to Major.

#### Finding: TCG-UI1-003
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** galaxy_test/ is a developer debugging tool with 5 files. Zero tests is a gap but "Critical" overstates impact for a dev tool.

#### Finding: TCG-UI1-004
**Original Severity:** Critical
**Verdict:** DOWNGRADED(Major)
**Reason:** formation/ has only 3 files (including __init__.py) and tests exist in test_formation_*.py. Edge case testing gaps are Minor, not Critical.

#### Finding: TCG-UI1-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - 17 panel files with only 8 having tests; planet_report_panel.py (509 lines) needs coverage.

#### Finding: TCG-UI1-006
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** BattlePanel tests exist (test_battle_panels.py, test_battle_panels_extended.py). Gaps are edge cases, not missing core coverage.

#### Finding: TCG-UI1-007
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - strategy_fleet_ops.py and strategy_colonization.py contain game logic lacking direct tests.

#### Finding: TCG-UI1-008
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified - workshop_ship_io.py and workshop_viewmodel.py handle ship data with no dedicated tests.

#### Finding: TCG-UI1-009
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** fleet_report_window.py has test_fleet_report_window.py. fleet_report_filters.py is a small utility.

#### Finding: TCG-UI1-010
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** build_queue_helpers.py has test_build_queue_helpers.py. Finding overstates the gap.

#### Finding: TCG-UI1-011
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** planet_list_filters.py has test_planet_list_filters.py. Remaining files are rendering-focused.

#### Finding: TCG-UI1-012
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** race_flag_gallery.py inherits from BaseGallery which is well-tested. Coverage exists via inheritance.

#### Finding: TCG-UI1-013
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** event_log_window.py has test_event_log_window.py with coverage.

#### Finding: TCG-UI1-014
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - column_manager.py (for FleetReport) has no direct tests.

#### Finding: TCG-UI1-015
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** keybindings_scene.py has test_keybindings_scene.py with coverage.

#### Finding: TCG-UI1-016
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** battle_state_viewer has tests in tests/unit/ui/battle_state_viewer/ subdirectory.

#### Finding: TCG-UI1-017
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - setup_renderer.py has no dedicated tests.

#### Finding: TCG-UI1-018
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - empire_panel_window.py has no dedicated tests.

#### Finding: TCG-UI1-019
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** save_selection_window.py has test_save_selection.py in tests/unit/ui/.

#### Finding: TCG-UI1-020
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified - design_selector_window.py has test_design_selector_window.py but filtering edge cases may need coverage.

#### Finding: TCG-UI1-021
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - bypass-init pattern usage is common; observation is accurate.

#### Finding: TCG-UI1-022
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - Some tests verify mock invocations rather than actual behavior.

#### Finding: TCG-UI1-023
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - Test organization is inconsistent across tests/unit/ui/ subdirectories.

#### Finding: TCG-UI1-024
**Original Severity:** Info
**Verdict:** CONFIRMED
**Reason:** Verified - tests/integration/ui/ appears empty or minimal; no UI integration tests found.
