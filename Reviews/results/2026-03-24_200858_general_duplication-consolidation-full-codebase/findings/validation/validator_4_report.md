# Validation Report: Validator 4

## Summary
- **Findings Reviewed:** 29
- **Confirmed:** 19
- **Downgraded:** 7
- **Rejected:** 3
- **Rejection Rate:** 10.3%

## Verdicts

#### Finding: DUP-UIW-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Both `DesignReportPanel._update_portrait()` and `PlanetReportPanel._update_portrait()` generate placeholder portraits using the same pattern: gradient fill based on type color map, text rendering with shadow, and border drawing. The logic is structurally identical despite different domain objects (ship class vs planet type).

#### Finding: DUP-UIW-006
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Both report panels use `pygame.transform.smoothscale` to fit images to fixed dimensions. The planet panel scales to (150, 150), while the design panel scales to dynamic portrait dimensions. The pattern is the same but parameters differ. Minor duplication confirmed.

#### Finding: DUP-UIW-007
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Two competing section header patterns exist: (1) `create_section_header()` utility from `game.ui.utils` used by race panels and empire treasury, and (2) inline `UILabel` with `f"-- {title} --"` format in `DesignStatsPanel._build_section()`, and `_add_section_header()` instance method in `ShipDetailPanel`. These are different approaches to the same task.

#### Finding: DUP-UIW-008
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Trivial)
**Reason:** The `for item in list: item.kill()` pattern is a standard pygame_gui cleanup idiom used across all panels. This is a one-liner pattern that is too trivial to consolidate -- every UI toolkit has element cleanup loops. Not worth extracting.

#### Finding: DUP-UIW-009
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The finding claims duplicate vehicle type color maps in UI files, but the vehicle type colors (`VEHICLE_SHIP`, `VEHICLE_FIGHTER`, etc.) are defined once in `game/ui/colors.py` (lines 274-278). The `DesignReportPanel` uses ship class colors (not vehicle type colors), and `PlanetReportPanel` uses planet type colors. These are different color maps for different domains, not duplicates.

#### Finding: DUP-UIW-010
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Four race config panels (`race_identity_panel`, `race_environment_panel`, `race_aptitudes_panel`, `race_description_panel`) plus `base_gallery.py` all implement `update_config()` and `set_from_config()` methods with the same bidirectional sync pattern. This is a genuine interface pattern that could be formalized with an abstract base class or protocol.

#### Finding: DUP-UIW-011
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `game/ui/colors.py` has both a `COLORS` dict (lines 12-43) with keys like `'bg_deep'`, `'text_normal'`, etc., and module-level constants like `TEXT_LIGHT`, `TEXT_MUTED`, `TEXT_DIM`. Some values overlap conceptually (e.g., `COLORS['text_muted']` = (102, 119, 153) vs `TEXT_MUTED` = (150, 150, 150)). Two parallel naming systems coexist.

#### Finding: DUP-SCR-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Three dedicated sidebar classes (`FleetReportSidebar`, `EmpireBuildQueueSidebar`, `EventLogSidebar`) all implement column toggle button creation and management with the same structural pattern: iterate columns, create toggle buttons, handle click events. The sidebar pattern is clearly duplicated.

#### Finding: DUP-SCR-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The `refresh_list()` / `_refresh_list()` methods across windows (fleet report, planet list, empire build queue, event log) call different data refresh logic specific to their domain. The common pattern is just calling `virtual_table.rebuild_row_pool()` + domain-specific data refresh, which is lightweight boilerplate rather than substantial duplication.

#### Finding: DUP-SCR-003
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** MOUSEWHEEL handling appears in 16 files, but most delegate to VirtualTable's built-in scrollbar or camera zoom. The actual wheel-handling code differs per context (scroll table vs zoom camera vs scroll panel). This is event routing, not duplicated logic.

#### Finding: DUP-SCR-004
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `FleetSelectionWindow`, `PlanetSelectionWindow`, and `SystemSelectionWindow` all extend `UIWindow` with the same structural pattern: UISelectionList + Confirm/Cancel buttons + callback on selection. The `FleetSelectionWindow` docstring even says "Follows the PlanetSelectionWindow pattern." This is a clear candidate for a base class.

#### Finding: DUP-SCR-005
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Planet/star info formatting appears in three locations: `strategy_detail_fmt.py` (format_planet_info, format_spectrum_html), `galaxy_test/system_mode.py` (builds inspection text with mass/radius/density), and `planet_report_panel.py` (via delegation to format_planet_info). The galaxy_test system_mode reimplements physical property formatting instead of reusing strategy_detail_fmt.

#### Finding: DUP-SCR-006
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The "facade-or-session command dispatch" pattern exists in strategy-related screens, but these are different screens dispatching different commands to different facades. The dispatch logic is domain-specific. The pattern of calling `self.facade.some_command()` is just standard delegation, not duplication worth consolidating.

#### Finding: DUP-SCR-007
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The four data source classes (FleetDataSource, PlanetDataSource, BuildQueueDataSource, EventLogDataSource) all implement `ITableDataSource` interface with `get_row_count()`, `get_columns()`, `get_cell_value()`. But this is just interface implementation -- each class has completely different data extraction logic. The "boilerplate" is just the interface contract methods, which is expected and proper OOP.

#### Finding: DUP-SCR-008
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `_get_column_value` is duplicated between `empire_build_queue_window.py` (line 481) and `empire_build_queue_data_source.py` (line 93) with essentially identical logic: special-casing 'system' and 'sector' columns, delegating others to viewmodel. This is a direct copy that should exist in only one place.

#### Finding: DUP-SCR-009
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** The value `5.97e24` (Earth mass) is hardcoded as a local variable in at least 4 locations: `planet_list_filters.py` (lines 19, 183, 283), `strategy_detail_fmt.py` (line 81), and `galaxy_test/system_mode.py` (imports from planet_physics). `planet_physics.py` defines the canonical `MASS_EARTH = 5.97e24` but the UI files duplicate it as inline literals instead of importing.

#### Finding: DUP-SCR-010
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The screenshot pattern (`sm = ScreenshotManager.instance(); sm.capture(label=...); sm.show_toast(...)`) appears in 3-4 screens. However, this is a 3-line pattern using a singleton service, and each call passes different labels and parameters. The duplication is trivial.

#### Finding: DUP-SCR-011
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Header sort/swap handling appears in fleet_report_window, planet_list_window, empire_build_queue_window, and event_log_window. Each window implements sort column toggling and column reordering through similar event handling code.

#### Finding: DUP-SCR-012
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Multiple windows implement the kill pattern with VirtualTable cleanup + close callback invocation in their `kill()` or `close()` methods. This is a standard teardown pattern across fleet_report, planet_list, empire_build_queue, and event_log windows.

#### Finding: DUP-SCR-013
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** TriStateFilterWidget polling appears in both `FleetReportSidebar` and `EmpireBuildQueueSidebar` with the same pattern: iterate tri-state widgets, collect filter states, update view model. The `EventLogSidebar` does not use tri-state filters.

#### Finding: DUP-SCR-014
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Population formatting with K/M suffixes appears in `strategy_detail_fmt.py` (lines 109-120), `planet_report_panel.py` (`_format_compact_number`), and `planet_list_filters.py` (line 300-303 for resources). The same conversion logic (>=1M -> "XM", >=1K -> "Xk") is reimplemented in each location.

#### Finding: DUP-SCR-015
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** The three sidebar classes (`FleetReportSidebar`, `EmpireBuildQueueSidebar`, `EventLogSidebar`) all follow the same initialization pattern: accept a UIPanel container, build widgets with y-offset tracking, create column toggle buttons. The structural layout code is duplicated.

#### Finding: DUP-SCR-016
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** This is the same issue as DUP-SCR-008 but from a different angle. `_get_column_value` in `empire_build_queue_window.py` duplicates the logic in `empire_build_queue_data_source.py`. The window version appears to be legacy code that should have been removed when the data source was created.

#### Finding: DUP-UIS-001
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Four UI service files (`ComponentService`, `VehicleClassService`, `ShipFactory`, `DesignLoaderAdapter`) all implement the same null-check pattern: `if registry_provider is None: raise ValidationException("registry_provider is required", code=ErrorCode.MISSING_DEPENDENCY.value, context={...})`. This is identical boilerplate that could be extracted to a shared validator.

#### Finding: DUP-UIS-002
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** `ComponentService` and `VehicleClassService` both have `_get_provider()` returning `self._provider`, while `ShipFactory` has `_get_registries()` returning `self._registry_provider`. These are trivial one-line accessor methods that merely return a stored field. The "duplication" is just standard encapsulation pattern, not meaningful logic duplication worth consolidating.

#### Finding: DUP-UIS-003
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Searching for bounding-box center camera patterns across `game/ui` found no matching code for "bounding box center" or "fit to bounds" patterns. The camera-related files (`camera.py`, `strategy_camera_nav.py`) exist but without evidence of duplicated bounding-box centering logic in 4+ locations as claimed. The finding's location is too vague to verify.

#### Finding: DUP-UIS-004
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** In `ShipIO`, the ships folder path is constructed via `os.path.join(os.getcwd(), ShipIO.default_ships_folder)` in both `save_ship()` (line 95) and `load_ship()` (line 142), with the same `os.makedirs` check. This is a minor duplication within the same class that could be extracted to a helper method.

#### Finding: DUP-UIS-005
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `ShipIOAdapter` is a pure pass-through wrapper with no additional logic. `save_ship()` calls `self._ship_io.save_ship(ship)`, `load_ship()` calls `self._ship_io.load_ship(width, height)`, `set_ships_folder()` sets `self._ship_io.default_ships_folder`. The adapter adds no value since ShipIO is already in the UI layer (moved in PROJ-113).

#### Finding: DUP-UIS-006
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The finding claims overlap between `BattleOrchestrator` and `battle_factories.py`, but `battle_factories.py` does not exist in `game/ui/orchestration/`. Only `battle_orchestrator.py` exists there. The grep for "battle_factories" only found a reference in `game/ui/services/__init__.py`. The claimed duplicate file does not exist at the specified location.
