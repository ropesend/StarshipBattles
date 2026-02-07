# Lessons Learned & Technical Post-Mortems

This document serves as the long-term memory for the AI agent. Before fixing a bug, check this file to see if a similar issue has been solved before.

## [Example] Game crash on startup (2025-12-26)
**Cause:** An `IndentationError` was introduced in `main.py` during a refactor of the initialization logic. Python is sensitive to mixed tabs/spaces or incorrect block levels.
**Fix:** aligned the `try/except` block correctly.
**Prevention:**
- Always adhere to strict indentation rules (4 spaces).
- Run the code immediately after any refactor involving control flow changes.

## [UI] Range Mount Slider Increment Issue (2025-12-26)
**Cause:** The `min_val` and `max_val` from `modifiers.json` were Integers (0, 3). `pygame_gui.UIHorizontalSlider` seemingly respects the type of the range values; when given integers, it may default to integer stepping (1.0) regardless of the configured `click_increment` (0.1), or process internal math as integers.
**Fix:** Explicitly cast `min_val`, `max_val`, and `start_value` to `float` when creating the `UIHorizontalSlider`.
**Prevention:**
- When using UI sliders that require decimal precision, ALWAYS explicitly cast range limits to `float`.
- In TDD, verify not just the specific configuration values (like 0.1) but also the data types being passed to libraries.

## [UI] Ship structure component selection indicator not visible (2025-12-26)
**Cause:** 
1. The Left Panel was never told to deselect its items when the user clicked elsewhere (Structure List).
2. The Structure List (`LayerPanel`) relied on a hash key (based on component modifiers) to track selection. Because the "Mass Scaling" modifier automatically updates values based on ship state, this hash key was volatile. When the UI refreshed, the key changed, causing the selection check to fail and the highlight to disappear.
**Fix:** 
1. Implemented `deselect_all()` in the Left Panel.
2. Switched `LayerPanel` selection logic to use Python object identity (checking if `component in selected_group_list`) rather than hash keys.
**Prevention:**
- Avoid using calculated hashes for long-lived UI state if the underlying data is mutable. Use object identity (`id()` or `is`) where possible for tracking "which object is selected".
- Ensure that UI panels have clear "On Deselect" or "Lost Focus" handlers to clean up their state.

## [UI] Ship Structure Selection Volatility (2025-12-26)
**Cause:** Selection in the "Ship Structure" list was failing because the "group key" used to identify identical components included the value of *all* modifiers. The "Mass Scaling" modifier (and potentially others) is `readonly` and updates its value every frame based on the ship's total mass. This float value fluctuation caused the component's "key" to change between the `draw` call and the `click` event handling, causing component lookups to fail and the selection state to be lost.
**Fix:** Modified `get_component_group_key` in `ui/builder/layer_panel.py` to explicitly ignore `readonly` modifiers when generating the hash key.
**Prevention:**
- When creating hash keys for UI validation or grouping, ALWAYS exclude fields that are volatile, auto-calculated, or frequently updated (like animation states or physics-derived values).
- Ensure that "Identity" (what makes this group THE SAME group) relies only on user-controlled inputs, not engine-controlled outputs.

## [UI] Selection State Sync (2025-12-26)
**Cause:** 
1. The `LayerPanel` was handling its own selection logic and rebuilding itself immediately *before* passing the event to `builder_gui`.
2. `builder_gui` was the "Source of Truth" for selection state (via `selected_component_group`), but `LayerPanel` rebuilt using the *old* state, causing the visual selection to fail (it looked unselected).
3. The Left Panel was not visually deselecting because I hadn't confirmed if the `pygame_gui` `unselect()` method was propagating correctly, but fixing the event flow ensures `deselect_all` is called at the correct time.

**Fix:** 
1. Removed `self.rebuild()` from `LayerPanel`'s selection event handlers. It now just returns the action.
2. `builder_gui` handles the action, updates the global `selected_component_group`, and *then* explicitly calls `self.layer_panel.rebuild()`, ensuring the UI reflects the new state.

**Prevention:** 
- In Model-View-Controller (MVC) or ownership hierarchies, the Child (Panel) should not update its own View based on Global State until the Parent (Controller/Builder) has actually updated that state.
- Prefer "Action Bubbling" (return action to parent) over "Immediate Updates" if the update depends on parent-managed state.
