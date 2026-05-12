# BUG-47: Component Modifiers Section and Grid Not Acting Appropriately

## Description
The Component modifiers section and the component modifier Grid are not acting appropriately.

- The grid is not showing anything for the bridge component even when component modifiers are applied
- In the Component modifier panel, different modifiers are visible at different times for the same component, it seems to be affected by whatever component was previously selected. When a new component is placed and selected then sometimes no modifiers are visible - This shows the 1st time the armor plate is selected: C:\Developer\StarshipBattles\screenshots\screenshot_20260124_060606_582360_mouse_focus.png Then if I select a rail gun in the design and then select the armor plate again the size mount is back and visible: C:\Developer\StarshipBattles\screenshots\screenshot_20260124_060644_637316_mouse_focus.png
- When I have the bridge selected and I adjust the size mount it does not show any effect in the grid: C:\Developer\StarshipBattles\screenshots\screenshot_20260124_060806_569413_mouse_focus.png, other components are also not showing all of the modifier effects in the grid, they show some but not all.

### Screenshots
- screenshot_20260124_060606_582360_mouse_focus.png - Armor plate first selection (no size mount visible)
- screenshot_20260124_060644_637316_mouse_focus.png - Armor plate after selecting rail gun (size mount visible)
- screenshot_20260124_060806_569413_mouse_focus.png - Bridge size mount adjustment not reflected in grid

## Priority
**High** - Significant feature broken (modifier panel and grid display issues affect design workflow)

## Status
Awaiting Confirmation

## Work Log
| Date | Phase | Notes |
|------|-------|-------|
| 2026-01-24 | Ingested | Ticket created from user report |
| 2026-01-24 | Fixed | Root causes identified and fixed |

### Fix Details (2026-01-24)

**Issue 1: Modifier panel shows different modifiers depending on previous selection**
- **Root Cause:** In `ModifierEditorPanel.layout()`, when selecting a new component, the scroll container was killed but `self.modifier_rows` (containing `ModifierControlRow` objects) was not cleared. The row objects persisted with dead UI element references. Since `build_ui()` was only called when the y-position changed, rows at the same position never got their UI rebuilt.
- **Fix:** Modified `_clear_scroll_container()` in `builder_widgets.py` to also call `_clear_all_rows()`. This ensures all modifier rows are rebuilt with fresh UI elements when a new component is selected.
- **File:** `game/ui/panels/builder_widgets.py:155-166`

**Issue 2: Grid not showing all modifier effects (e.g., Size Mount not shown for Bridge)**
- **Root Cause:** `ModifierImpactGrid.update()` filtered stat columns to only show stats that the component's abilities consume. For example, the Bridge might only consume `crew_req`, but Size Mount affects `mass_mult`. Since `mass_mult` wasn't in the Bridge's consumed stats, the column wasn't displayed, making Size Mount's row appear empty.
- **Fix:** Removed the stat filtering so ALL stats affected by any modifier are shown as columns. Changed `self.stat_columns = self._get_affected_stats(summary, component_stats)` to `self.stat_columns = self._get_affected_stats(summary, None)`.
- **File:** `game/ui/panels/modifier_impact_grid.py:105-111`
