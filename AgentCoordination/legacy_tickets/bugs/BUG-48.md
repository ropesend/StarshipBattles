# BUG-48: Core Layer Components Display as Blank and Deletion Issues

## Description
When I add a second generator to a design and place it in the core level it shows up as a blank space: C:\Developer\StarshipBattles\screenshots\screenshot_20260124_061019_198733_mouse_focus.png then when I delete the 1st generator that I placed in the outer layer, instead the one that was placed in the core is deleted.

I have similar behaviour with fuel tanks, and crew quarters and life support. If I place a single one of these components in the core 1st it shows normally, but if I place another in the outer layer then a blank space shows where the component was in the core layer. Deleting either seems to only delete the core level component.

### Screenshots
- screenshot_20260124_061019_198733_mouse_focus.png - Second generator in core level showing as blank space

### Affected Components
- Generator
- Fuel Tanks
- Crew Quarters
- Life Support

## Priority
**High** - Significant feature broken (component placement/deletion in core layer is broken)

## Status
Awaiting Confirmation

## Work Log
| Date | Phase | Notes |
|------|-------|-------|
| 2026-01-24 | Ingested | Ticket created from user report |
| 2026-01-24 | Fixed | Root causes identified and fixed |

### Fix Details (2026-01-24)

**Issue 1: Components showing as blank in Core layer**
- **Root Cause:** In `LayerPanel.rebuild()`, the UI cache key was `("group", group_key)` which didn't include the layer type. When the same component type (e.g., Generator) existed in both CORE and OUTER layers with identical modifiers, they had the same cache key. The second component's UI overwrote the first in the cache, causing the first to display blank or with wrong data.
- **Fix:** Changed the cache key to `("group", l_type, group_key)` to include the layer type, ensuring unique cache entries for each layer.
- **File:** `ui/builder/layer_panel.py:213`

**Issue 2: Deletion targeting wrong component (wrong layer)**
- **Root Cause:** The `LayerComponentItem` only passed `group_key` to the delete handler. The handler then searched ALL layers for a matching component, finding the first match which could be in the wrong layer (typically the last layer searched in backwards iteration).
- **Fix:**
  1. Added `layer_type` parameter to `LayerComponentItem.__init__` and stored it
  2. Changed the delete action payload from `group_key` to `(group_key, layer_type)` tuple
  3. Updated `_handle_remove_group()` in event router to unpack the layer type and only search the target layer
- **Files:**
  - `ui/builder/structure_list_items.py:258,260,419`
  - `game/ui/screens/workshop_event_router.py:190-235`
