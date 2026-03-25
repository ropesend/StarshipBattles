# PROJ-228: UI Structural Patterns — Decisions

## DEC-001: Project Creation (2026-03-24)
- **Decision:** Create PROJ-228 as dedup campaign item 5/5 for UI structural pattern consolidation
- **Rationale:** Full-codebase duplication review identified significant structural duplication across UI screens, panels, and components
- **Source:** `Reviews/results/2026-03-24_200858_general_duplication-consolidation-full-codebase/`
- **Depends on:** PROJ-227 (already merged)

## DEC-002: ScrollState Utility (2026-03-25)
- **Decision:** Created `ScrollState` class in `game/ui/widgets/scroll_state.py` to replace duplicated scroll_offset + MOUSEWHEEL handling
- **Rationale:** 14+ files had the same ad-hoc pattern of `self.scroll_offset = 0; self.max_scroll = 0` with manual MOUSEWHEEL clamping
- **Migrated:** 9 files (results_panel, test_run_details, dialogs, json_viewer, scrollable_json_panel, modifier_impact_grid, battle_panels, setup_screen, battle_state_viewer)
- **Skipped:** 12 files — either use MOUSEWHEEL for zoom (camera, formation_editor), delegate to other systems (VirtualTable, viewmodel, camera), or have scroll driven by pygame_gui scrollbar widgets

## DEC-003: BaseScene Not Extracted (2026-03-25)
- **Decision:** Do NOT extract a BaseScene class from IScene implementors
- **Rationale:** Scenes share only 3-5 lines of boilerplate (store width/height, create UIManager). 90%+ of each scene is unique logic. The IScene protocol already provides the interface contract. A base class would add inheritance coupling with negligible duplication reduction.

## DEC-004: CallbackWindow Not Extracted (2026-03-25)
- **Decision:** Do NOT extract a CallbackWindow base class from UIWindow subclasses
- **Rationale:** UIWindow subclasses already inherit from pygame_gui UIWindow. Callback patterns vary significantly (on_selection, on_close, button callbacks). No consistent shared boilerplate beyond what UIWindow provides.

## DEC-005: SelectionDialog Not Extracted (2026-03-25)
- **Decision:** Do NOT extract a SelectionDialog base from fleet/planet/system selection windows
- **Rationale:** Selection windows share UIWindow+UISelectionList+Confirm/Cancel pattern but differ in details (PlanetSelection has detail panel + "Any Planet" button, FleetSelection is simple, SystemSelection has hex coordinates, DesignSelector has ship design previews). A base would need too many hooks/overrides.

## DEC-006: Sidebar Pattern Not Extracted (2026-03-25)
- **Decision:** Do NOT extract a SidebarPanel or SidebarMixin
- **Rationale:** Sidebars share high-level structure but differ in filter types (status buttons, tri-state widgets, search entry), layout, and viewmodel interaction. The common column toggle section is ~20 lines per sidebar. Extraction would be more complex than the duplicated code.

## DEC-007: Column Toggle Already Consolidated (2026-03-25)
- **Decision:** No further consolidation needed for column toggle logic
- **Rationale:** `TableColumnManager.toggle_column()` already centralizes the toggle logic. Sidebars just create UI buttons that call this method.

## DEC-008: Data Source Pattern Already Consolidated (2026-03-25)
- **Decision:** No further consolidation needed for VirtualTable data sources
- **Rationale:** All data sources already extend `ITableDataSource` from `game/ui/components/table/data_source.py`. Sorting/filtering is handled by per-window view models. Data sources are correctly domain-specific.

## DEC-009: ISerializable Protocol (2026-03-25)
- **Decision:** Created `ISerializable` protocol in `game/core/protocols.py` for type checking only
- **Rationale:** 5 dataclasses in `battle_state.py` share the `to_dict()`/`from_dict()` contract. Protocol formalizes this for type annotations without requiring a mixin, since each class has domain-specific serialization logic.
- **Note:** `ISerializableShip` in `entity_protocols.py` is a separate, ship-specific protocol and is unrelated.

## DEC-010: DrawablePanel Not Extracted (2026-03-25)
- **Decision:** Do NOT extract a DrawablePanel base class for test_lab panels
- **Rationale:** Test lab panels share method names (draw, handle_event, update) but each method has completely different logic (2-10 lines). Duck typing already provides the interface contract.
