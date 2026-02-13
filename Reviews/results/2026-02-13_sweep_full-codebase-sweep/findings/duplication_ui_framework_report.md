# Duplication & Fragmentation Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Total Issues Found:** 7
- **Critical:** 0 | **Major:** 2 | **Minor:** 4 | **Info:** 1

## Scope Details
Files analyzed in `game/ui/` (root files, services/, renderer/, interfaces/, orchestration/, assets/):
- `game/ui/__init__.py`
- `game/ui/utils.py`
- `game/ui/config.py`
- `game/ui/colors.py`
- `game/ui/services/` (11 files)
- `game/ui/renderer/` (4 files)
- `game/ui/interfaces/` (2 files)
- `game/ui/orchestration/` (2 files)
- `game/ui/assets/` (2 files)

## Findings

#### MAJOR: Dependency Injection Pattern Inconsistency Across Services
**ID:** DUP-UI2-001
**Location:** `game/ui/services/vehicle_class_service.py:36-52` AND `game/ui/services/component_service.py:31-50` AND `game/ui/services/ship_factory.py:40-56` AND `game/ui/services/design_loader_adapter.py:31-44`
**Issue:** Four service classes implement nearly identical patterns for dependency injection with registry providers, but with inconsistent implementation approaches:

1. **VehicleClassService**: Strict DI - raises ValueError if registry_provider is None
2. **ComponentService**: Lazy DI - optional with `get_default_registry_provider()` fallback
3. **ShipFactory**: Hybrid - optional with both method-level and instance-level override capability
4. **DesignLoaderAdapter**: Lazy DI - optional with `get_default_registries()` fallback

Each has a `_get_provider()` or `_get_registries()` method with similar boilerplate (5-8 lines each).

**Impact:**
- Cognitive overhead for developers understanding which pattern each service uses
- Risk of inconsistent behavior when services are composed together
- Approximately 25 lines of near-duplicate boilerplate across 4 services

**Recommendation:** Create a base class or mixin that provides a standardized registry provider pattern. Either adopt strict DI across all services (PROJ-50 compliance) or document the lazy pattern as the standard with a shared implementation.
**Effort:** Medium

---

#### MAJOR: Image Bounding Box and Visible Area Scaling Logic Duplication
**ID:** DUP-UI2-002
**Location:** `game/ui/utils.py:97-163` AND `game/ui/assets/ship_theme_manager.py:155-195` AND `game/ui/screens/design_image_helper.py:165-188`
**Issue:** Three separate implementations of the same concept - finding the visible (non-transparent) portion of an image and scaling based on it:

1. **utils.py**: `get_visible_bounding_box()` + `scale_image_by_visible_portion()` - uses `get_bounding_rect(min_alpha=10)`, crops first then scales
2. **ship_theme_manager.py**: Uses `get_bounding_rect(min_alpha=20)` in `_load_single_image()`, `get_bounding_rect(min_alpha=1)` in `get_image_metrics()`
3. **design_image_helper.py**: Uses `get_bounding_rect(min_alpha=10)` in `_load_topdown_thumbnail_uncached()`, scales full image then crops

All three use pygame's `get_bounding_rect()` but with different alpha thresholds (1, 10, 20) and different scale-then-crop vs crop-then-scale approaches.

**Impact:**
- Different alpha thresholds may produce slightly different results for the same image
- Two different approaches (crop-first vs scale-first) may produce quality differences
- Approximately 40 lines of similar logic spread across 3 files

**Recommendation:** Consolidate into a single utility function in `game/ui/utils.py` with configurable alpha threshold and a standardized approach (crop-then-scale is more memory efficient). Update callers to use the shared function.
**Effort:** Medium

---

#### MINOR: Singleton Manager Pattern Repetition
**ID:** DUP-UI2-003
**Location:** `game/ui/assets/ship_theme_manager.py:11-54` AND `game/ui/services/screenshot_manager.py:11-38` AND `game/ui/renderer/sprites.py:7-25`
**Issue:** Three singleton managers follow the same pattern with near-identical structure:
- `metaclass=SingletonMeta`
- Thread locks (`_init_lock`, `_io_lock`)
- `clear()` method for test isolation
- Cache dictionaries initialized in `__init__`

The structure is consistent (good), but the documentation boilerplate for "Thread Safety", "Usage", and "Testing" is duplicated verbatim across all three.

**Impact:**
- Approximately 15 lines of identical docstring content repeated 3 times
- Low maintenance risk since SingletonMeta handles the complexity

**Recommendation:** This is acceptable duplication - the pattern is well-established and the SingletonMeta already consolidates the implementation. Consider extracting the common docstring pattern into a template for consistency, but not a priority.
**Effort:** Simple (low priority)

---

#### MINOR: Image Transform Operations Scattered Without Central Helper
**ID:** DUP-UI2-004
**Location:** `game/ui/utils.py:66-94` provides centralized functions, but `game/ui/renderer/game_renderer.py:64-69` AND `game/ui/assets/ship_theme_manager.py:147-159` implement their own scaling
**Issue:** While `game/ui/utils.py` provides `calculate_ship_image_scale()` and `scale_and_rotate_image()`, not all callers use them:

1. `game_renderer.py` correctly uses the utility functions from `utils.py`
2. `ship_theme_manager.py` directly calls `pygame.image.load().convert_alpha()` and caches without using the utils

This is partially by design (ShipThemeManager is the source image loader), but there's opportunity to ensure consistency.

**Impact:**
- Minimal - the utils are available and mostly used
- Some callers bypass the centralized functions for valid reasons

**Recommendation:** Document that `game/ui/utils.py` is the canonical location for image transform operations. ShipThemeManager's direct usage is justified as the caching layer.
**Effort:** Simple (documentation only)

---

#### MINOR: Validation Service Pattern Has Single-Purpose Wrapper
**ID:** DUP-UI2-005
**Location:** `game/ui/services/validation_service.py:20-73`
**Issue:** ValidationService is a thin wrapper that provides only two methods (`validate_addition`, `validate_design`) and simply delegates to the underlying validator. The entire class is 53 lines including docstrings, with only approximately 10 lines of actual logic.

This pattern is duplicated in `game/ui/services/ship_io_adapter.py` (104 lines, approximately 20 lines of logic) and `game/ui/services/design_loader_adapter.py` (88 lines, approximately 15 lines of logic).

**Impact:**
- These are intentional adapter patterns for decoupling UI from simulation
- The wrappers serve a valid architectural purpose (PROJ-43)
- Low actual duplication - the pattern is justified

**Recommendation:** No action needed. The adapter pattern is appropriate for layer isolation. The "duplication" is actually consistent application of an architectural pattern.
**Effort:** N/A (by design)

---

#### MINOR: Camera Coordinate Transform Duplication in Formation Module
**ID:** DUP-UI2-006
**Location:** `game/ui/renderer/camera.py:116-132` provides `world_to_screen()` and `screen_to_world()`, but `game/ui/screens/formation/renderer.py:70-100` reimplements similar transforms
**Issue:** The Camera class provides coordinate transformation, but the formation renderer implements its own transforms with a different signature:
- Camera: Uses pygame.math.Vector2, has offset support
- FormationRenderer: Uses float tuples, simpler transform without offsets

The formation editor has its own `world_to_screen()` and `screen_to_world()` because it doesn't use the standard Camera class - it has a simpler pan/zoom model.

**Impact:**
- Different transform implementations may drift over time
- The formation editor operates independently of battle scenes, so this is somewhat justified

**Recommendation:** Consider whether FormationRenderer could use a Camera instance internally, or document that the two are intentionally independent systems.
**Effort:** Medium (design decision needed)

---

#### INFO: Color Constants Could Be Centralized Further
**ID:** DUP-UI2-007
**Location:** `game/ui/colors.py:7-45` AND `game/ui/renderer/game_renderer.py:14-19`
**Issue:** Layer colors are defined in `game_renderer.py`:
```python
LAYER_COLORS = {
    LayerType.ARMOR: (100, 100, 100),
    LayerType.OUTER: (200, 50, 50),
    LayerType.INNER: (50, 50, 200),
    LayerType.CORE: (220, 220, 220)
}
```

While `colors.py` defines the UI style guide colors. The layer colors could potentially live in `colors.py` for centralization, but they're render-specific.

**Impact:**
- Layer colors are only used in one place (game_renderer.py)
- No actual duplication, just an organizational observation

**Recommendation:** No action needed. Layer colors are appropriately co-located with the rendering logic that uses them.
**Effort:** N/A

---

## Top 5 Priority Issues

1. **DUP-UI2-002 (MAJOR)** - Image bounding box/scaling logic is duplicated with inconsistent alpha thresholds across 3 files. Consolidation would eliminate subtle behavioral differences and reduce code.

2. **DUP-UI2-001 (MAJOR)** - DI pattern inconsistency across 4 services creates cognitive overhead and potential for bugs when services interact. Standardization would improve maintainability.

3. **DUP-UI2-006 (MINOR)** - Formation renderer coordinate transforms are separate from Camera class. Consider unifying if formation editor ever needs to integrate more tightly with other screens.

4. **DUP-UI2-003 (MINOR)** - Singleton docstring boilerplate is repeated but functional. Low priority to address.

5. **DUP-UI2-004 (MINOR)** - Image transform utility functions exist but aren't universally used. Documentation could clarify intended usage.

---

## Analysis Notes

The UI framework layer is well-organized with clear separation of concerns:
- **services/** provides adapter/facade patterns for decoupling from simulation
- **renderer/** handles drawing and coordinate transforms
- **interfaces/** defines protocols and DTOs for clean boundaries
- **orchestration/** coordinates cross-layer operations
- **assets/** manages visual resources

The duplication found is generally either:
1. Justified by architectural patterns (adapters, singletons)
2. Semantic similarity that serves different contexts (formation vs battle cameras)
3. Actual consolidation opportunities (image bounding/scaling logic)

The codebase shows evidence of active refactoring (PROJ-43, PROJ-50, PROJ-113 references) with good progress on reducing duplication through shared patterns like SingletonMeta.
