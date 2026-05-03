# Duplication & Fragmentation Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 25
- **Total Issues Found:** 7
- **Critical:** 0 | **Major:** 3 | **Minor:** 3 | **Info:** 1

## Findings

#### MAJOR: Tkinter Root Initialization Duplicated
**ID:** DUP-UI2-001
**Location:** `game/ui/services/ship_io.py:20-32` AND `game/ui/screens/formation_editor.py:24-30` AND `game/ui/screens/workshop_ship_io.py:21-26`
**Issue:** The same Tkinter root initialization pattern (try/except with TclError/RuntimeError handling, withdraw(), and None fallback) is repeated in at least 3 locations. Each file creates its own module-level `tk_root` or `_tk_root` variable with nearly identical initialization code.

```python
# Pattern repeated in ship_io.py, formation_editor.py, workshop_ship_io.py:
try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
except (tkinter.TclError, RuntimeError):
    tk_root = None
```

**Impact:**
- If error handling needs to be updated (e.g., adding a new exception type), must update 3+ locations
- Inconsistent exception handling between files (ship_io.py catches more exceptions)
- Multiple Tk() instances created if modules are imported together

**Recommendation:** Create a centralized Tkinter manager in `game/ui/services/` that provides a shared, lazily-initialized Tk root. Use singleton pattern like other managers (ScreenshotManager, ShipThemeManager).

**Effort:** Medium

---

#### MAJOR: Registry Provider Lazy Resolution Pattern Duplicated
**ID:** DUP-UI2-002
**Location:** `game/ui/services/component_service.py:46-50` AND `game/ui/services/ship_factory.py:49-56` AND `game/ui/services/validation_service.py:42-46` AND `game/ui/services/design_loader_adapter.py:40-43`
**Issue:** Multiple services implement nearly identical lazy resolution patterns for registry providers:

```python
# ComponentService pattern:
def _get_provider(self) -> IRegistryProvider:
    if self._provider is None:
        self._provider = get_default_registry_provider()
    return self._provider

# ShipFactory pattern:
def _get_registries(self, registry_provider: Optional['GameRegistries'] = None) -> 'GameRegistries':
    if registry_provider is not None:
        return registry_provider
    if self._registry_provider is not None:
        return self._registry_provider
    from game.core.registry import get_default_registries
    return get_default_registries()
```

**Impact:**
- Each service has slightly different naming conventions (_provider vs _registry_provider)
- Different fallback resolution strategies (some support method-level override, some don't)
- Inconsistent behavior expectations for callers

**Recommendation:** Consider extracting a base class `ServiceWithRegistry` or a mixin that provides standardized registry resolution. Or document the pattern formally so new services follow a consistent approach.

**Effort:** Medium

---

#### MAJOR: Image Bounding Box + Scale Logic Duplicated
**ID:** DUP-UI2-003
**Location:** `game/ui/utils.py:116-162` AND `game/ui/screens/design_image_helper.py:131-190`
**Issue:** Both files implement similar logic for:
1. Getting the visible bounding box using `get_bounding_rect()`
2. Calculating scale based on visible height
3. Cropping to visible area and scaling

The `utils.py` version (`scale_image_by_visible_portion`) is more complete and handles edge cases, but `design_image_helper.py` reimplements similar logic instead of using the utility.

**Impact:**
- `design_image_helper.py` doesn't use the helper in `utils.py`, missing the centralized implementation
- Minor behavioral differences in edge case handling
- Maintenance burden if the algorithm needs updating

**Recommendation:** Refactor `design_image_helper.py` to use `scale_image_by_visible_portion` from `game/ui/utils.py`. The utility function already handles placeholders and edge cases properly.

**Effort:** Simple

---

#### MINOR: Singleton Manager Boilerplate
**ID:** DUP-UI2-004
**Location:** `game/ui/assets/ship_theme_manager.py`, `game/ui/renderer/sprites.py`, `game/ui/services/screenshot_manager.py`
**Issue:** Each singleton manager in the UI layer has identical docstring boilerplate:
```python
"""
Singleton manager for X.

Thread Safety:
    - Instance creation is thread-safe via SingletonMeta

Usage:
    manager = XManager.instance()
    ...

Testing:
    - Use reset() to destroy instance completely
"""
```

**Impact:** Low - this is acceptable documentation pattern, but updates to the pattern require changes in multiple places.

**Recommendation:** This is acceptable as-is. The pattern provides clear, consistent documentation. Consider a project-wide template if creating new managers.

**Effort:** Simple (if addressed)

---

#### MINOR: Multiple Image Transform Scale Patterns
**ID:** DUP-UI2-005
**Location:** Multiple files use `pygame.transform.smoothscale` with similar load-scale patterns
**Issue:** Throughout the UI layer, there are 40+ calls to `pygame.transform.smoothscale`. Many follow similar patterns:
- Load image with `pygame.image.load(path).convert_alpha()`
- Scale to target size with `smoothscale(img, (size, size))`
- Cache result

The patterns are similar but not identical enough to warrant a single abstraction without losing flexibility.

**Impact:** Low - this is natural pygame usage, not true duplication

**Recommendation:** The existing `game/ui/utils.py` helpers (calculate_ship_image_scale, scale_and_rotate_image, scale_image_to_fit, scale_image_by_visible_portion) provide good consolidation. Continue using these where applicable.

**Effort:** N/A - acceptable as-is

---

#### MINOR: Clipboard Copy Implementation
**ID:** DUP-UI2-006
**Location:** `game/ui/services/screenshot_manager.py:88-116`
**Issue:** The `_copy_to_clipboard` method implements cross-platform clipboard handling with Tkinter primary and Windows clip.exe fallback. This clipboard logic is currently only used by ScreenshotManager, but could be useful elsewhere.

**Impact:** Low - single location currently, but if clipboard functionality is needed elsewhere, it would likely be duplicated.

**Recommendation:** If clipboard copy is needed elsewhere in the future, extract to a utility function in `game/ui/utils.py` or `game/core/`. For now, acceptable as-is.

**Effort:** Simple (if needed)

---

#### INFO: Consistent Service Adapter Pattern
**ID:** DUP-UI2-007
**Location:** `game/ui/services/` directory
**Issue:** The services directory shows a consistent and well-designed pattern:
- `ValidationService`, `VehicleClassService`, `ComponentService`, `ShipFactory`, `DesignLoaderAdapter`, `ShipIOAdapter`, `BattleUIService`

All follow the adapter/facade pattern wrapping lower-layer functionality. This is intentional design, not duplication.

**Impact:** Positive - good architecture pattern

**Recommendation:** Continue this pattern for new UI services. Consider documenting it as the standard approach.

**Effort:** N/A

---

## Top 5 Priority Issues

1. **DUP-UI2-001 (MAJOR): Tkinter Root Initialization** - Multiple Tk() instances created, inconsistent error handling. Create centralized TkinterManager singleton.

2. **DUP-UI2-003 (MAJOR): Image Bounding Box Logic** - `design_image_helper.py` should use existing `scale_image_by_visible_portion` from `utils.py` instead of reimplementing.

3. **DUP-UI2-002 (MAJOR): Registry Provider Resolution** - Consider base class or documented pattern for consistent DI behavior across services.

4. **DUP-UI2-004 (MINOR): Singleton Boilerplate** - Low priority, acceptable documentation pattern.

5. **DUP-UI2-006 (MINOR): Clipboard Copy** - Low priority, single use currently.
