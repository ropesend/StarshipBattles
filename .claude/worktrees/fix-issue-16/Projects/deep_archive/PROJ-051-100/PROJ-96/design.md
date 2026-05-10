# PROJ-96: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Layout (Ships Tab)
The Ships tab in `game/ui/screens/race_setup_screen.py` uses a stacked layout:
1. Title "Select Ship Theme" at top
2. `RaceThemeGallery` (full width, ~200px tall) containing:
   - "Select Ship Theme:" label
   - Preview panel showing "Selected: {theme_name}"
   - 4 theme buttons stacked vertically (Atlantians, Federation, Klingons, Romulans)
3. `UIScrollingContainer` (full width, remaining height) containing:
   - 2-column grid of 6 ship classes
   - Each cell: label + top-down image (180x180) + portrait image (180x180)

### Problems Identified
1. **Wasted space:** Theme gallery takes ~200px of vertical space on top, pushing ship previews down
2. **Sparse grid:** Only 6 ships in 2 columns - doesn't showcase the theme well
3. **Tiny top-down images:** Ships have large transparent padding; scaling to 180x180 based on full image size makes visible ships very small
4. **Label positioning:** Labels above images but spanning full column width - awkward relative to the image pair
5. **Excessive spacing:** 20px row gaps, 10px image gaps, 35px label-to-image gap

### Key APIs Available
- `ShipThemeManager.get_image_metrics(theme, class)` -> `pygame.Rect` of visible pixels (min_alpha=20)
- `ShipThemeManager.get_portrait_image(theme, class)` -> `pygame.Surface` (cached, thread-safe)
- `ShipThemeManager.load_image(theme, class)` -> `pygame.Surface` (top-down skin)
- `ShipThemeManager.get_available_themes()` -> `List[str]`

## Swarm Findings Summary

### Architecture
- `RaceThemeGallery` is a self-contained component created in PROJ-12 Phase 4
- It receives a parent `UIPanel`, position, width, and callback - no `height` parameter currently
- The gallery creates elements directly on the parent panel (not in its own container)
- `_refresh_ship_preview` in `race_setup_screen.py` handles ship grid rendering independently
- `_load_ship_portrait` (lines 472-508) duplicates `ShipThemeManager.get_portrait_image()` logic

### Key Patterns to Reuse
- **UIScrollingContainer pattern**: `RacePortraitGallery` (lines 106-112) wraps content in a scrollable container with `allow_scroll_y=True` and `set_scrollable_area_dimensions()`
- **Button selection highlighting**: `RaceThemeGallery.on_theme_selected()` uses `btn.select()` / `btn.unselect()` - keep this pattern
- **Visible bounding rect scaling**: `game_renderer.py` and `schematic_view.py` use `get_image_metrics()` for smart scaling - apply same approach

### Dependencies & Risks
1. **Phase ordering dependency:** `RaceThemeGallery` constructor change (adding `height`) must happen before the call site update in `_create_ships_panel_content` - do Phase 1 first, then Phase 2
2. **Atlantians missing LightCruiser_Portrait.jpg:** Avoided by not including Light Cruiser in the 9-ship selection. `get_portrait_image()` returns `None` gracefully for missing files anyway.
3. **Scale factor blowup for tiny sprites:** Small fighters/satellites with lots of transparency could cause absurdly large scaled images. Mitigation: cap `scale_factor` at 3.0.
4. **Scrollbar width:** `UIScrollingContainer` scrollbar takes ~15-20px. Current code already accounts for this with `container_width = container.get_relative_rect().width - 30`.

### Opportunities Discovered
- Delete `_load_ship_portrait` method entirely (lines 472-508) since `ShipThemeManager.get_portrait_image()` does the same thing with proper caching
- Remove unused `self.ship_preview_container` alias (line 375)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## Target Layout

```
+-----------------------------------------------------------------------+
| Select Ship Theme                                                      |
+-------------+---------------------------------------------------------+
| Atlantians  | Fighter(Med)    Satellite(Med)  Escort                  |
| Federation  | [topdn][port]   [topdn][port]   [topdn][port]          |
| Klingons    |                                                         |
| Romulans    | Frigate         Cruiser         Heavy Cruiser           |
|             | [topdn][port]   [topdn][port]   [topdn][port]          |
|  (scroll)   |                                                         |
|             | Battleship      Dreadnought     Superdreadnought       |
|             | [topdn][port]   [topdn][port]   [topdn][port]          |
+-------------+---------------------------------------------------------+
  ~200px wide              remaining width (~2330px at 2560)
```

### Image Sizing Strategy
- Portrait images: 160x160px (scaled to fit, aspect ratio maintained)
- Top-down images: scaled so the VISIBLE portion height matches ~160px, then cropped to visible area
- Image pair gap: 5px
- Row spacing: 10px
- Label height: 25px
