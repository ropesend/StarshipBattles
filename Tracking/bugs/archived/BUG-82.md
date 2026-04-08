# BUG-82: Design Workshop - Load Design window is very slow to open

## Description

IT TAKES A LONG TIME FOR THE Load design window to load from the design workshop. Possibly the image processing for the icons is the bottleneck. Consider preprocessing them and saving icon versions of the images. Try to use existing asset systems.

## Priority
Medium

## Status (Awaiting Confirmation)

## Root Cause

Two performance bottlenecks in `game/ui/screens/design_image_helper.py`:

1. **Pixel-by-pixel bounding box scan** (`_get_visible_bounding_box`): For every top-down skin thumbnail, the code iterated over every pixel using `surface.get_at()` (Python-level calls) to find the visible bounding box. For a 512x512 image, that's 262,144 individual Python calls per design. With 20+ designs, this alone takes several seconds.

2. **No caching**: Every time the design list is refreshed (filtering, scrolling), ALL thumbnails are reloaded from disk and reprocessed from scratch.

## Fix

In `game/ui/screens/design_image_helper.py`:

1. **Replaced `_get_visible_bounding_box` with `surface.get_bounding_rect(min_alpha=10)`**: This is pygame's native C-level implementation that does the same thing orders of magnitude faster. The codebase already uses this pattern in `ship_theme_manager.py`.

2. **Added module-level thumbnail caches**: `_portrait_cache` and `_topdown_cache` keyed by `(design_id, size)`. After first load, subsequent calls return instantly from cache.

3. **Added `clear_thumbnail_cache()`**: Public function to clear caches when needed (new game, design changes).

4. **Extracted uncached versions**: `_load_portrait_thumbnail_uncached` and `_load_topdown_thumbnail_uncached` for the actual loading logic.

## Tests

Updated `tests/unit/ui/screens/test_design_image_helper.py`:
- Added `clear_thumbnail_cache()` to `setup_method` of portrait and topdown test classes to prevent cross-test contamination
- Replaced `TestGetVisibleBoundingBox` class (tested removed internal function) with `TestThumbnailCache` class:
  - `test_portrait_cache_returns_same_surface` - Cache hits return same object
  - `test_topdown_cache_returns_same_surface` - Cache hits return same object
  - `test_clear_cache_resets_both_caches` - clear_thumbnail_cache works

All 49 design-related tests pass (12 image helper + 22 selector window + 15 integration).

## Work Log
- 2026-02-11: Root cause identified. Replaced O(n*pixels) bounding box scan with native C call. Added thumbnail caching.
