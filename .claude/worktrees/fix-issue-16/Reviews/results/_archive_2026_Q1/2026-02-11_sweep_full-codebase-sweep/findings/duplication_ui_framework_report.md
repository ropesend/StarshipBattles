# Duplication & Fragmentation Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Scope:** `game/ui/` root files, `services/`, `renderer/`, `interfaces/`, `orchestration/`, `assets/`, `components/`, `utils/` (excluding `screens/` and `panels/`)
- **Total Issues Found:** 8
- **Critical:** 2 | **Major:** 3 | **Minor:** 2 | **Info:** 1

## Findings

#### CRITICAL: Portrait Loading Logic Duplicated in 5+ Locations
**ID:** DUP-UI2-001
**Location:** `game/ui/assets/ship_theme_manager.py:219-291` AND `game/ui/screens/design_image_helper.py:29-105` AND `game/ui/panels/build_queue_portraits.py:67-120` AND `game/ui/panels/design_report_panel.py:170-215` AND `game/ui/screens/builder/right_panel.py:233-269`
**Issue:** The same portrait image loading pipeline is reimplemented in 5+ places across the codebase. Each implementation:
1. Normalizes the ship class name (handling parenthetical formats like "Fighter (Medium)" -> "MediumFighter")
2. Constructs a `_Portrait.jpg` filename
3. Tries multiple filesystem paths for the portrait
4. Falls back to a default/placeholder image
5. Scales the loaded image to a target size

The class-name normalization logic uses a regex `re.match(r"(.*)\s+\((.*)\)", ship_class)` in at least 3 places (`build_queue_portraits.py:93`, `design_report_panel.py:187`, `right_panel.py:242`), while `ShipThemeManager._ship_class_to_portrait_name()` uses string splitting, and `design_image_helper.py` uses `replace("_", " ")` -- all attempting the same transformation with different approaches.

The fallback path lists also differ:
- `build_queue_portraits.py`: `ShipThemes/{theme}/Portraits/`, `resources/Portraits/{theme}/`, `assets/Images/Default_Ship_Portrait.png`
- `design_report_panel.py`: adds `resources/Portraits/{theme}/{ship_class}_Portrait.jpg` (with spaces)
- `design_image_helper.py`: `ShipThemes/{theme}/Portraits/` (two variations), `assets/Images/Default_Ship_Portrait.png`
- `right_panel.py`: `ShipThemes/{theme}/Portraits/` (two variations), `assets/Images/Default_Ship_Portrait.png`
- `ShipThemeManager`: derives directory from existing theme data

**Impact:** Active divergence creates bugs. If a new portrait path convention is added or a naming scheme changes, only some locations will be updated. The different normalization approaches (regex vs string split) could produce different results for edge-case ship class names. Each copy has slightly different error handling and fallback behavior.
**Recommendation:** Consolidate into a single `PortraitLoader` utility in `game/ui/utils.py` or extend `ShipThemeManager.get_portrait_image()` to be the sole entry point. All call sites should delegate to one canonical implementation.
**Effort:** Medium

#### CRITICAL: Ship Image Scaling Pipeline Duplicated Between game_renderer and schematic_view
**ID:** DUP-UI2-002
**Location:** `game/ui/renderer/game_renderer.py:46-74` AND `game/ui/screens/builder/schematic_view.py:68-95`
**Issue:** The ship theme image loading and scaling pipeline is near-identical in two locations:

Both perform this exact sequence:
1. `theme_mgr.load_image(theme_id, ship.ship_class)`
2. `theme_mgr.get_image_metrics(theme_id, ship.ship_class)`
3. `visible_size = max(metrics.width, metrics.height) if metrics else None`
4. `theme_mgr.get_manual_scale(theme_id, ship.ship_class)`
5. `calculate_ship_image_scale(ship_img.get_size(), target_size, visible_size, manual_scale)`
6. Scale and blit the image

The code in `game_renderer.py` uses the centralized `scale_and_rotate_image()` utility function (with rotation), while `schematic_view.py` manually calls `pygame.transform.scale()` (without rotation). This is a natural divergence (battle view rotates ships, builder does not), but the ~15 lines of setup code are copy-pasted.

**Impact:** If the scaling algorithm changes (e.g., different metrics handling, new scale factors), both locations must be updated independently. The copy-paste has already drifted: `schematic_view.py` adds a `manual_scale <= 0` guard (line 78-79) that `game_renderer.py` lacks.
**Recommendation:** Extract a `prepare_ship_image()` or `get_scaled_ship_image()` function into `game/ui/utils.py` that returns a scaled (but unrotated) surface given a theme manager, theme_id, ship_class, and target_size. Each caller would then optionally rotate.
**Effort:** Simple

#### MAJOR: Layer Color Constants Duplicated with Drift
**ID:** DUP-UI2-003
**Location:** `game/ui/renderer/game_renderer.py:14-19` AND `game/ui/screens/builder/schematic_view.py:104-108`
**Issue:** Layer colors for ARMOR, OUTER, INNER, and CORE are defined as a dict constant `LAYER_COLORS` in `game_renderer.py`, and then reimplemented as inline if/elif chains in `schematic_view.py`. The values have already drifted:

| Layer | game_renderer.py | schematic_view.py |
|-------|-----------------|-------------------|
| ARMOR | (100, 100, 100) | (100, 100, 100) |
| OUTER | (200, 50, 50) | (200, 50, 50) |
| INNER | (50, 50, 200) | (50, 50, 200) |
| CORE | **(220, 220, 220)** | **(200, 200, 200)** |

CORE color has diverged: `(220, 220, 220)` vs `(200, 200, 200)`.

**Impact:** Users see inconsistent layer colors between battle view and ship builder. If layer colors are updated for a UI refresh, both locations must be found and synchronized.
**Recommendation:** Move `LAYER_COLORS` to `game/ui/colors.py` (the existing style guide module) and import from both consumers. Remove the inline if/elif chain in `schematic_view.py`.
**Effort:** Simple

#### MAJOR: BattleUIService get_engine() Null-Check Boilerplate Repeated 6 Times
**ID:** DUP-UI2-004
**Location:** `game/ui/services/battle_ui_service.py:56-58, 68-70, 82-84, 94-96, 105-107, 116-118`
**Issue:** Every public method in `BattleUIService` repeats the same 3-line boilerplate:
```python
engine = self._battle_service.get_engine()
if engine is None:
    return <default>
```

This pattern appears 6 times with only the default return value varying (`[]`, `True`, `None`, `0`). The method bodies after this guard are typically 1-2 lines.

**Impact:** Low bug risk since the pattern is simple, but it adds cognitive overhead and makes the class ~18 lines longer than necessary. Adding new methods requires remembering to include this guard.
**Recommendation:** Extract a `_get_engine_or_raise()` helper, or use a `_with_engine()` decorator/helper that handles the None case. Alternatively, a property `_engine` that returns the engine (and methods check once) would reduce repetition.
**Effort:** Simple

#### MAJOR: ShipThemeManager Internal Methods Repeat Theme Resolution Pattern
**ID:** DUP-UI2-005
**Location:** `game/ui/assets/ship_theme_manager.py:117-134, 167-195, 197-204, 219-245`
**Issue:** Four public methods (`load_image`, `get_image_metrics`, `get_manual_scale`, `get_portrait_image`) each independently implement the same theme resolution preamble:
1. Check `if not self.discovery_complete` -- return early with default
2. Check `if theme_name not in self.theme_data` -- fallback to `self.default_theme`

This 2-4 line pattern is repeated in every public method. Additionally, `_load_single_image` and `_load_portrait_image` share the same double-check locking pattern:
```python
with self._io_lock:
    # Double-check cache after acquiring lock
    if theme_name in self.<cache> and ship_class in self.<cache>[theme_name]:
        return self.<cache>[theme_name][ship_class]
```

**Impact:** Low-medium. Adding new public methods requires remembering to include the preamble. The double-check pattern is error-prone if not followed exactly.
**Recommendation:** Extract `_resolve_theme(theme_name)` helper that handles discovery check and default fallback. The double-check locking could be wrapped in a generic `_cached_load(cache_dict, theme, class, loader_fn)` method.
**Effort:** Simple

#### MINOR: Lazy DI Provider Pattern in Services
**ID:** DUP-UI2-006
**Location:** `game/ui/services/component_service.py:31-49` AND `game/ui/services/validation_service.py:33-46` AND `game/ui/services/ship_factory.py:40-56` AND `game/ui/services/design_loader_adapter.py:31-44`
**Issue:** Four UI service classes implement the same lazy dependency injection pattern:
1. Accept an optional provider/dependency in `__init__`
2. Store it as `self._provider` / `self._validator` / `self._registry_provider`
3. Provide a `_get_provider()` / `_get_validator()` / `_get_registries()` method that lazily resolves via global default if None

Each does this slightly differently:
- `ComponentService._get_provider()` calls `get_default_registry_provider()`
- `ShipFactory._get_registries()` calls `get_default_registries()` (imports lazily)
- `ValidationService._get_validator()` calls `get_or_create_validator()`
- `DesignLoaderAdapter.__init__()` resolves eagerly if None (creates `SimulationDesignLoader`)
- `VehicleClassService.__init__()` raises `ValueError` if None (strict DI, no lazy)

**Impact:** Low. Each service wraps a different dependency type, so full unification is not practical. However, the inconsistency between lazy vs strict patterns could confuse developers.
**Recommendation:** Document the two DI patterns (lazy-optional and strict-required) in a shared docstring or convention guide. Consider a small `LazyProvider` mixin or base class if more services adopt this pattern. Not high priority given the current count.
**Effort:** Simple

#### MINOR: Topdown Thumbnail Loading Reimplements Bounding-Box Scaling from utils.py
**ID:** DUP-UI2-007
**Location:** `game/ui/screens/design_image_helper.py:131-190` AND `game/ui/utils.py:97-163`
**Issue:** `design_image_helper._load_topdown_thumbnail_uncached()` manually implements bounding-box detection and visible-portion scaling:
```python
bbox = loaded_img.get_bounding_rect(min_alpha=10)
...
scale = target_height / visible_height
new_width = int(loaded_img.get_width() * scale)
new_height = int(loaded_img.get_height() * scale)
scaled_img = pygame.transform.smoothscale(loaded_img, (new_width, new_height))
# Crop to visible area
```

This is semantically identical to `game/ui/utils.py:scale_image_by_visible_portion()` which was created specifically for this purpose:
```python
bbox = get_visible_bounding_box(surface)
...
scale = target_height / visible_height
new_width = max(1, int(visible_width * scale))
return pygame.transform.smoothscale(cropped, (new_width, target_height))
```

The approaches differ subtly: `design_image_helper` scales the full image then crops, while `utils.py` crops first then scales. The `utils.py` version is more memory-efficient (scales a smaller surface).

Note: `design_image_helper.py` is in `screens/` so technically outside this shard's primary scope, but it overlaps significantly with `utils.py` which is in scope.

**Impact:** Low. The `utils.py` function was likely created to replace this pattern but the original was never updated. Both produce similar visual results.
**Recommendation:** Replace `design_image_helper._load_topdown_thumbnail_uncached()` body with a call to `scale_image_by_visible_portion()` from `game/ui/utils.py`.
**Effort:** Simple

#### INFO: Hardcoded Magic Color Tuples Throughout Rendering Code
**ID:** DUP-UI2-008
**Location:** Throughout `game/ui/renderer/game_renderer.py` and `game/ui/widgets.py`
**Issue:** Common color tuples appear as magic values throughout the framework files:
- `(100, 100, 100)` appears in `widgets.py:6,99`, `game_renderer.py:15,127,200`, `ship_theme_manager.py:210-212` (~8 occurrences in scope)
- `(200, 200, 200)` appears in `widgets.py:101`, `game_renderer.py:124,150,181,184,187,206` (~7 occurrences in scope)
- `(50, 50, 50)` appears in `game_renderer.py:148,218` (~2 occurrences in scope)
- `(255, 255, 255)` appears in `widgets.py:30,32` as white

Meanwhile, `game/ui/colors.py` defines a `COLORS` style guide dictionary with semantic names (`text_muted`, `bg_dark`, etc.) but it is only used by `screens/builder/` and `screens/strategy_renderer.py`. The legacy `widgets.py` and `renderer/game_renderer.py` files predate this system and use raw tuples.

**Impact:** Low. These are stable legacy files that work correctly. However, a future UI color theme change would require finding every hardcoded tuple.
**Recommendation:** No immediate action needed. When these files are next refactored, consider replacing magic color tuples with `COLORS` dict references for consistency. The `COLORS` dict in `colors.py` could also benefit from having general-purpose entries like `'gray_medium': (100, 100, 100)` to replace the most common magic values.
**Effort:** Medium (many files to touch, low risk of regressions but tedious)

## Top 5 Priority Issues

1. **DUP-UI2-001 (CRITICAL):** Portrait loading duplicated in 5+ places with active divergence in name normalization and path resolution. Highest bug risk and maintenance burden. Consolidate to a single `PortraitLoader` utility.

2. **DUP-UI2-002 (CRITICAL):** Ship image scaling pipeline copy-pasted between `game_renderer.py` and `schematic_view.py` with early drift (`manual_scale <= 0` guard only in one). Extract `prepare_ship_image()` helper.

3. **DUP-UI2-003 (MAJOR):** Layer colors duplicated between `game_renderer.py` (dict) and `schematic_view.py` (inline if/elif) with CORE color already diverged ((220,220,220) vs (200,200,200)). Move to `colors.py`.

4. **DUP-UI2-005 (MAJOR):** ShipThemeManager repeats theme resolution preamble (discovery check + default fallback) in every public method plus duplicated double-check locking. Extract `_resolve_theme()` helper.

5. **DUP-UI2-004 (MAJOR):** BattleUIService repeats engine null-check boilerplate 6 times. Extract helper method or use decorator pattern.
