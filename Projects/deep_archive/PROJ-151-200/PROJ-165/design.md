# PROJ-165: Design Document

## Architecture Analysis

### Current State
24 call sites across 8 UI files independently construct `pygame_gui.elements.UILabel` instances with `object_id="#section_header"`. Each repeats 5-6 lines of identical constructor parameters with only the text and width varying.

### Target State
A single `create_section_header()` function in `game/ui/utils.py` that all 8 files import and call. Each call site becomes 1 line instead of 5-6.

## Design Decisions

### Why `game/ui/utils.py`?
This module already exists and contains standalone UI utility functions (`create_centered_rect`, `calculate_ship_image_scale`, etc.). Adding another utility function here is consistent with the established pattern.

Alternatives considered:
- **New file `game/ui/widgets.py`**: Unnecessary — we're adding one function, not a widget library
- **Base class method**: The 8 consuming classes don't share a base class, and forcing one would be over-engineering
- **Mixin**: Same issue — adds complexity for one function

### Function Signature

```python
def create_section_header(
    text: str,
    y: int,
    width: int,
    manager,
    container,
    x: int = 10,
    height: int = 25
) -> 'pygame_gui.elements.UILabel':
```

**Why these defaults?**
- `x=10`: 23 of 24 sites use x=10. The one exception (empire_treasury) can pass `x=LEFT_MARGIN`.
- `height=25`: 19 of 24 sites use height=25. The 5 empire_panel_window sites use `ROW_HEIGHT` and can pass it explicitly.
- `text`, `y`, `width` are always different — no sensible defaults.
- `manager` and `container` vary by class attribute names — must be explicit.

**Why return the UILabel?**
- One call site (race_summary_panel) stores the result in `self.summary_labels`
- One call site (empire_treasury_panel) appends to `self._elements`
- Returning allows callers to store/track the element when needed
- Callers that don't need the reference can ignore the return value

**Why NOT advance y?**
- Callers use 3 different y-advancement patterns:
  - `y += 28` (race panels)
  - `y_offset += ROW_HEIGHT + 5` (empire_panel_window)
  - `y += ROW_HEIGHT` (empire_panel_window descriptions, empire_treasury)
- Embedding y-advancement in the helper would require an output y parameter or tuple return, adding complexity
- The `ship_detail_panel._add_section_header()` does return y, but it's a class method with a fixed spacing — different pattern

### Import Strategy
The function uses a lazy import of `pygame_gui` inside the function body, matching the pattern where `game/ui/utils.py` currently only imports `pygame` at module level. This avoids adding a hard dependency on `pygame_gui` for any code that imports other utilities from `utils.py`.

## Risk Assessment
**Risk:** Very low
- Pure UI cosmetic helper — no logic changes
- All 24 sites produce identical UILabel instances before and after
- Existing tests cover the UI panel construction
- Visual verification is easy (open Race Setup, check headers render)
