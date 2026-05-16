# PROJ-410 Phase B: Yard-Selector Root-Cause Investigation

## Executive Summary

The **missing yard-selector on second player's planet** is a **separate, selector-specific bug**, NOT caused by the shared VirtualTable widget-cache contamination. The selector correctly refreshes all yard buttons on every open_for_yard(), but the buttons are created and added to a pygame_gui container that has stale visibility/focus state from the previous player's context.

**Root cause:** The selector's UIScrollingContainer persists hidden or unfocused state after the first player closes the build queue. When the second player opens, refresh() creates new buttons and adds them to this recycled container, but the container's visibility flags may not fully re-initialize on the show() + open_for_yard() path.

**Evidence:** 
- selector refresh() kills and recreates all buttons (lines 91-95, 113-123)
- collect_build_queues_at_hex() correctly filters by active empire (line 414)
- open_for_yard() updates queue_sources correctly and calls refresh()
- BUT: refresh() does NOT call show() on the scrollable container
- AND: show() only explicitly calls show() on background, not child panels

---

## Detailed Findings

### Selector Architecture
- Custom UIButton panel (build_queue_selector.py)
- Does NOT use VirtualTable
- Does NOT cache widget objects
- refresh() completely destroys and rebuilds buttons on every call

### Container Lifecycle Issue
- UIScrollingContainer created once in constructor (build_queue_selector.py:75-79)
- Same container object reused across yard switches (PROJ-376 reuse)
- hide() recursively hides all children including selector panel (screen.py:365)
- show() only explicitly shows background, not child panels (screen.py:372)
- Result: selector container may not fully re-initialize event delivery/visibility on second player open

### Why NOT the VirtualTable Bug
1. Selector doesn't use VirtualTable widget pool
2. Selector doesn't retain cached widget state
3. Selector calls refresh() which completely kills and recreates buttons
4. Problem is container lifecycle, not widget cache

### Second-Player Path
1. First player opens → selector creates buttons in visible container
2. First player closes → hide() recursively hides all panels
3. Second player opens → open_for_yard() calls refresh()
4. refresh() creates fresh buttons BUT adds to hidden/unfocused container
5. show() may not fully restore container visibility/focus
6. Result: buttons exist but are not interactive

---

## Code Changes Needed

**File:** game/ui/screens/build_queue_screen.py, lines 333-337

Add explicit visibility reset before calling refresh():

```python
# Refresh queue selector against the new sources.
self._queue_selector.queue_sources = self.queue_sources
self._queue_selector.selected_indices = self.selected_queue_indices
self._queue_selector.active_source = self.active_queue_source
# PROJ-410: Ensure selector panel is visible before refresh
if self._queue_selector.panel and not self._queue_selector.panel.visible:
    self._queue_selector.panel.show()
self._queue_selector.refresh()
```

---

## Regression Test

test_yard_selector_visible_on_second_player_planet:
- Two empires, each with a planet having both shipyard + planetary yard
- First empire opens → selector shows 2 buttons
- First empire closes → screen hidden
- Second empire opens → assert selector shows 2 buttons, buttons are interactive
- Click buttons → assert callback fires

---

## Decision: Scope

**This is a separate bug requiring separate fix, but should be included in PROJ-410 Phase B** because:

1. Both bugs manifest at turn boundaries and second-player opens
2. Both are symptoms of reused BuildQueueScreen not fully resetting state
3. Turn-boundary hook should trigger both the cache-invalidation fix (B+C) AND this selector visibility fix
4. Regression tests should cover both together

---

## File References

- game/ui/screens/build_queue_selector.py:29-87 (constructor), 89-134 (refresh)
- game/ui/screens/build_queue_screen.py:264-344 (open_for_yard), 346-377 (show/hide)
- game/ui/screens/build_queue_panel_factory.py:293-312 (selector creation)
- game/strategy/data/build_queue_source.py:392-424 (collect correctly filters by empire)

**Status:** Root cause identified. Separate fix required. Recommend inclusion in PROJ-410 Phase B.
