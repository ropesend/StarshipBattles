# UI and Builder System Coverage Audit Report

## 1. Coverage Summary

The UI and Builder system (`builder_gui.py` and `ui/builder/*.py`) has a solid foundation of unit tests covering core logic, interaction flow, and basic rendering. However, significant gaps exist in testing the integration of File I/O within the GUI, complex component visualization, and specific event handling scenarios.

**Current Status:** ~70% Estimated Coverage via Unit Tests.

| Component | Status | Existing Tests |
| :--- | :--- | :--- |
| `builder_gui.py` | ⚠️ Partial | `test_builder_logic`, `test_builder_structure_features` (Logic only) |
| `rendering.py` | ✅ Good | `test_rendering_logic` (Covers `draw_ship`, scaling, culling) |
| `interaction_controller.py` | ✅ Good | `test_builder_interaction` (Drop/Drag Logic) |
| `layer_panel.py` | ⚠️ High Risk | `test_builder_structure_features` (Item UI), `test_builder_interaction` (Drop Acceptance). **Missing Rebuild/Sync tests.** |
| `detail_panel.py` | ❌ Critical | No dedicated tests for HTML generation or image caching. |
| `right_panel.py` | ✅ Good | `test_builder_ui_sync`, `test_ui_dynamic_update` |

## 2. Missing Tests (Coverage Gaps)

### A. I/O Integration in GUI (`builder_gui.py`)
Current tests mock `Ship` heavily. We rely on `ShipIO` having its own tests, but the **GUI's handling of I/O** is untested.
*   **Gap:** `_load_ship` success/failure message handling.
*   **Gap:** `_save_ship` integration.
*   **Gap:** `_reload_data` (Reloading registries and refreshing UI).
*   **Gap:** `_clear_design` (Ensuring all UI panels reset).

### B. Drag-and-Drop Validation with Real Layouts
`test_builder_interaction` uses a `MockDropTarget`. `LayerPanel` is the real target.
*   **Gap:** `LayerPanel.get_target_layer_at` with scrolling enabled.
*   **Gap:** Dropping onto a collapsed group header vs expanded list.
*   **Gap:** Validation feedback loop (displaying errors when `accept_drop` returns False).

### C. Component Detail Rendering (`detail_panel.py`)
There are no tests verifying that `ComponentDetailPanel` correctly generates HTML for complex components.
*   **Gap:** `show_component` generating correct HTML for ability rows.
*   **Gap:** Fallback rendering for unregistered abilities.
*   **Gap:** Image caching logic (`_update_image`) and fallback to placeholders.

### D. Layer Panel Reconciliation (`layer_panel.py`)
`rebuild()` uses a `ui_cache` to preserve UI instances. This logic is complex and untested.
*   **Gap:** Verifying `ui_cache` keys reusing instances correctly.
*   **Gap:** Verifying `handle_item_action` correctly routes events like `ACTION_TOGGLE_GROUP`.

### E. Visual Feedback Logic (`rendering.py`)
*   **Gap:** Specific verification that `draw_ship` colors components correctly based on `has_ability()` (e.g., Red for WeaponAbility, Green for Propulsion). Current tests verify it draws *something*, but not *what color*.

## 3. Plan to Reach 100% Coverage

To achieve 100% coverage, we will create/extend the following test files:

### 1. `unit_tests/test_builder_io_integration.py` (New)
*   **Test:** `test_load_ship_gui_flow`: Mock `ShipIO.load_ship` to return success/failure and verify `builder.show_error` or UI refresh is called.
*   **Test:** `test_save_ship_gui_flow`: Mock `ShipIO.save_ship`.
*   **Test:** `test_clear_design`: Call `_clear_design` and assert `ship.name` resets and `layer_panel` is empty.
*   **Test:** `test_reload_data_flow`: Verify `_reload_data` calls registry clears/loads and triggers `right_panel.refresh_controls`.

### 2. `unit_tests/test_builder_drag_drop_real.py` (New)
*   **Test:** `test_layer_panel_drop_targeting`: Instantiate a real `LayerPanel`. Mock `get_abs_rect` for items. Verify `get_target_layer_at` returns correct layer for various positions (header, item, empty space).
*   **Test:** `test_drop_rejection_ui`: Simulate a rejected drop and verify `builder.show_error` is invoked.

### 3. `unit_tests/test_detail_panel_rendering.py` (New)
*   **Test:** `test_html_generation`: Pass components with known abilities/stats. specific assertions on `stats_text_box.html_text` content (e.g., "Mass:", "WeaponAbility", "Damage:", color codes).
*   **Test:** `test_image_caching`: detailed verification that `_update_image` caches surfaces and doesn't re-load from disk on same component.

### 4. Extend `unit_tests/test_rendering_logic.py`
*   **Task:** Add `test_component_coloring_by_ability`:
    *   Create mock components with specific abilities (`WeaponAbility`, `CombatPropulsion`).
    *   Mock `pygame.draw.circle`.
    *   Assert that the color argument matches expectations (Red, Green).

### 5. `unit_tests/test_layer_panel_reconciliation.py` (New)
*   **Test:** `test_rebuild_caching_behavior`:
    *   Call `rebuild()`. Capture `id(item)` for a component.
    *   Call `rebuild()` again. Assert `id(item)` is identical.
    *   Change sorting/filtering. Call `rebuild()`. Verify behavior.
