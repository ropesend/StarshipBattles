# PROJ-329C Review: 3 Facade-Coupled Retrofits + 3 Controllers

**Review date:** 2026-05-04
**Reviewer:** OpenCode (deepseek-v4-pro)
**SHA:** 9211246b8 (target refactor), 0f45e8de8 (pre-refactor baseline)

---

## CRITICAL

- **[C1] Controller reads pygame_gui widget state (boundary violation)** | `game/ui/screens/cargo_quick_dialog_controller.py:78` | `issue_orders()` receives `cargo_items` dicts with raw `UIHorizontalSlider` widgets and calls `item['slider'].get_current_value()`. Controllers must not touch pygame_gui widgets — the PROJ-328 Phase C `TransferController` model explicitly keeps all widget access in the renderer/window. The slider-value extraction should happen in `CargoQuickDialog._issue_orders` before passing clean data (list of `(type, amount, species_id, planet_id)` tuples) to the controller. This coupling means the controller cannot be tested without constructing or mocking pygame_gui sliders, defeating a primary purpose of the controller split.

## MAJOR

- **[M1] Dead method `navigate_to` in PlanetListController** | `game/ui/screens/planet_list_controller.py:42-45` | `navigate_to()` is never called by `PlanetListWindow`. The window calls `self.on_navigate_callback(loc)` directly at `planet_list_window.py:625`, bypassing the controller entirely. The same callback reference is stored redundantly in both the window (`planet_list_window.py:244`) and the controller (`planet_list_controller.py:33`). Either wire `_navigate_to_selected` to use `self.controller.navigate_to(loc)` or remove the dead method and the unused `on_navigate_callback` parameter from the controller.

- **[M2] Duplicate demographic-view logic** | `planet_list_window.py:698-701` vs `planet_list_controller.py:38-40` | The fallback branch in `_resolve_demographic_view` duplicates `PlanetListController.resolve_demographic_view` byte-for-byte. The comment correctly states this is for bypass-init test compatibility (where the controller may not exist), but two independent code paths calling `self.facade.get_colony_demographic_view(planet.id)` create a maintenance hazard — any interface change to the facade requires updating both locations. Consider refactoring the bypass-init tests to always wire a controller so the fallback can be removed.

- **[M3] `scene.facade` property access in Stage 1** | `game/ui/screens/cargo_quick_dialog.py:235` | `self.facade = scene.facade` runs before `super().__init__()` in Stage 1. The comment at lines 233-234 asserts this is a cheap property read, but it is a reach-through into a passed-in object whose internal lifecycle is opaque to the dialog. If the scene ever lazily initialises or recreates its facade, the dialog would hold a stale reference. The dialog already receives `scene` as a parameter — consider passing `facade` directly from the registrar instead of reaching through `scene` in Stage 1.

## PASS

- **Behavioral parity (PlanetListWindow spot-check).** `__init__`, `process_event`, `update`, and `kill` are behaviorally identical to pre-refactor SHA `0f45e8de8`. Key control flow verified: `_on_planet_selected` is unreachable during `super().__init__()` → `set_dimensions()` because `selected_planet` is `None` at that point, making the Stage-1 state reordering safe.
- **Pattern §33 two-stage construction.** All 3 windows correctly implement three-stage `__init__` (cheap state → `super().__init__()` → widget builder), carry the `ui_builder` test seam, and gate Stage 3 behind `_window_init_bypassed`. All 3 test-fixture files provide canonical `Null*UiBuilder` and `Mock*UiBuilder` classes.
- **Controller boundary discipline (PlanetAbilitiesController, PlanetListController).** Both controllers contain only facade queries (read-only) and command emission — zero pygame_gui imports, zero widget construction, zero direct game-state mutation. `PlanetAbilitiesController.toggle_ability()` correctly dispatches through `facade.handle_command()`.
- **Controller-window coupling.** All 3 windows accept an optional `controller` parameter defaulting to a self-constructed instance; no circular imports; import direction is exclusively Window → Controller.
- **Test fixture shape conformance.** All 3 fixture files validate required Stage-1 attributes exist before populating widget slots, matching the PROJ-328 Phase C convention. `MockPlanetListWindowUiBuilder` correctly populates the full `ui_filters` shape needed by `refresh_list()` iterations.
- **StrategyModalWindow super chain.** All 3 windows correctly call `StrategyModalWindow.__init__` as Stage 2; `kill()` properly chains `super().kill()` after cleanup.
- **`CargoQuickDialogController` facade queries.** `get_unload_items` / `get_load_items` / `get_target_planet_id` correctly delegate to `CargoTransferService` static methods, keeping the facade read path centralized.
- **`PlanetAbilitiesController` activation-state formatting.** `get_component_status` and `is_component_active` correctly handle all `ActivationPhase` variants and return sensible defaults for missing facilities.
