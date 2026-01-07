# UI Specialist Report: Builder UI & UX Compatibility (Phase 3)

## Phase Status: [IN PROGRESS]

## Summary of Findings
The Ship Builder UI currently suffers from significant layout conflicts and brittle state synchronization. While the individual components (panels, schematic view) are feature-rich, their integration into the `BuilderSceneGUI` is hardcoded for a non-standard resolution or has evolved into a state where elements overlap catastrophically on common display sizes (e.g., 1080p).

## Critical Issues (UI/UX Compatibility)

### 1. Massive Horizontal Overlap
The horizontal layout logic in `builder_screen.py` contains hardcoded widths that exceed standard screen dimensions and cause overlapping:
- **Overlap Conflict**: With a 1920px width, the `detail_panel` (x=620, w=550) starts 280px *before* the `layer_panel` ends (x=450, w=450).
- **Schematic Obstruction**: The `detail_panel` completely covers the `SchematicView` (x=900, w=270). The center workspace is effectively unusable as the "Detail" overlay blocks the primary interaction area.

### 2. Vertical Layout Collision
The vertical layout also contains overlapping regions:
- **Weapons Report Overlap**: The `weapons_report_panel` (height 600) is placed at `y = height - bottom_bar - 600`. On a 1080p screen, this is `y=420`.
- **Panel Height Mismatch**: `left_panel` and `layer_panel` are assigned a height of `panels_height` (approx. 660px on 1080p). 
- **Result**: The Weapons Report overlaps the bottom 240px of the Left/Layer panels, obscuring critical navigation elements and structure lists.

### 3. Resolution Incompatibility
The UI is not currently responsive. The hardcoded widths for the `left_panel` (450), `right_panel` (750), `layer_panel` (450), and `detail_panel` (550) total **2200px**, which exceeds even a Full HD (1920px) workspace. On smaller resolutions (e.g., 1600px or the test `800x600`), panels are pushed off-screen or rendered useless.

## Interface Integrity & UX

### 1. Brittle Data-Sync Coupling
The `BuilderSceneGUI._reload_data` method directly manipulates the internal state of `BuilderRightPanel` by killing and recreating dropdown menus (`class_dropdown`, `vehicle_type_dropdown`). 
- **UX Risk**: This direct manipulation bypasses standard event flows and can lead to inconsistent states (e.g., the Class dropdown showing options for the wrong Vehicle Type after a reload).
- **Regression**: The `test_builder_ui_sync.py` confirms that UI elements must be manually refreshed to match ship state, indicating a lack of reactive data binding.

### 2. Drawing Order Hazards
The `draw` method explicitly calls `left_panel.draw` and `layer_panel.draw` *after* `ui_manager.draw_ui`.
- **UX Issue**: This is likely a workaround to force selection highlights on top, but it creates a risk where standard UI components (like tooltips or dropdown lists) may be rendered *under* the panel's custom drawing layers if they happen to overlap.

## Technical Debt & Regressions

### 1. Missing Library
- **Critical Failure**: `game/ui/screens/builder_utils.py` is missing from the directory. This file likely contains standardized layout calculations that were bypassed in favor of the current hardcoded implementation.

### 2. Multi-Selection UX Ambiguity
- The homogeneity check in `on_selection_changed` replaces the entire selection if a user clicks a component of a different type. This "replace-on-mismatch" behavior is inconsistent with standard Windows application patterns where selection is usually additive (Shift) or toggled (Ctrl) regardless of item properties.

## Recommendations
1.  **Dynamic Layout Calculation**: Replace hardcoded pixel widths with a percentage-based or grid-based layout system.
2.  **Centralize Configuration**: Move all panel dimensions to `panel_layout_config.py`.
3.  **Implement Event-Driven Sync**: Shift from manual reconstruction of dropdowns to an event-based system where panels subscribe to `DATA_RELOADED` events.
4.  **Z-Order Standardization**: Integrate custom drawing (highlights/overlays) into the `pygame_gui` rendering pipeline (e.g., via `UIElement` subclasses) rather than drawing "naked" to the screen after the manager.
