# Duplication & Fragmentation Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 20
- **Total Issues Found:** 12
- **Critical:** 0 | **Major:** 4 | **Minor:** 6 | **Info:** 2

## Findings

#### MAJOR: Duplicated Lazy DI Provider Resolution Pattern
**ID:** DUP-UI2-001
**Location:** `game/ui/services/component_service.py:46-50` AND `game/ui/services/vehicle_class_service.py:50-52` AND `game/ui/services/validation_service.py:42-46` AND `game/ui/services/ship_factory.py:49-56`
**Issue:** Four services implement nearly identical patterns for lazy dependency injection resolution:
- `ComponentService._get_provider()` - resolves `IRegistryProvider` with fallback to `get_default_registry_provider()`
- `VehicleClassService._get_provider()` - returns stored `_provider` (no fallback, required)
- `ValidationService._get_validator()` - resolves validator with fallback to `get_or_create_validator()`
- `ShipFactory._get_registries()` - resolves `GameRegistries` with method-level override > instance > global default

Each uses slightly different semantics (some allow None fallback, some require, some support method-level override), but the core pattern is identical. This is a classic example of copy-paste drift where the pattern was duplicated and evolved independently.
**Impact:** When the DI pattern needs updating (e.g., adding logging, error handling, or changing resolution order), four different files must be modified. Risk of inconsistent behavior across services.
**Recommendation:** Create a base mixin or utility function `resolve_dependency(stored, fallback_factory)` that encapsulates the pattern. Services can use it with their specific fallback functions.
**Effort:** Medium

#### MAJOR: Directory Creation Pattern Duplicated in ShipIO
**ID:** DUP-UI2-002
**Location:** `game/ui/services/ship_io.py:49-51` AND `game/ui/services/ship_io.py:91-93`
**Issue:** The `ShipIO` class duplicates the exact same directory creation pattern in both `save_ship()` and `load_ship()`:
```python
ships_folder = os.path.join(os.getcwd(), ShipIO.default_ships_folder)
if not os.path.exists(ships_folder):
    os.makedirs(ships_folder)
```
This 3-line block appears verbatim twice in the same file.
**Impact:** If the directory path logic changes (e.g., using `Paths.SHIPS_DIR` instead of `os.getcwd()`), both locations must be updated. DRY violation within a single file.
**Recommendation:** Extract to a private method `_ensure_ships_folder() -> str` that returns the folder path after ensuring it exists.
**Effort:** Simple

#### MAJOR: Singleton Manager Pattern Triplicated
**ID:** DUP-UI2-003
**Location:** `game/ui/assets/ship_theme_manager.py:11-25` AND `game/ui/services/screenshot_manager.py:11-24` AND `game/ui/renderer/sprites.py:7-20`
**Issue:** Three manager classes (`ShipThemeManager`, `ScreenshotManager`, `SpriteManager`) implement identical singleton patterns with:
- `metaclass=SingletonMeta`
- Same docstring structure ("Singleton manager for...", "Thread Safety:", "Usage:", "Testing:")
- Instance creation via `.instance()` method
- `reset()` method documented for testing

While using `SingletonMeta` is correct and consolidates the singleton logic, the documentation and boilerplate is copy-pasted. Additionally, all three implement similar caching/loading patterns with thread locks.
**Impact:** Documentation drift (if one is updated, others may not be). The actual singleton pattern is properly centralized in `SingletonMeta`, but the manager code structure is duplicated.
**Recommendation:** Create a `SingletonManagerMixin` or document a consistent template for manager classes. Consider whether all three need the same threading model.
**Effort:** Medium

#### MAJOR: Service Adapter Wrapping Pattern
**ID:** DUP-UI2-004
**Location:** `game/ui/services/ship_io_adapter.py:44-103` AND `game/ui/services/design_loader_adapter.py:31-87`
**Issue:** Both adapter classes follow the identical structural pattern:
1. Accept an optional dependency in `__init__`
2. If None, import and instantiate the real implementation
3. Store as `self._ship_io` / `self._loader`
4. Delegate all methods to the wrapped instance

The adapters exist purely to wrap simulation/IO classes for UI consumption, but the wrapping boilerplate is duplicated. Both also have similar return value conventions (tuples with success/object and message).
**Impact:** When adding new adapter methods or changing the wrapping pattern, multiple files need identical changes.
**Recommendation:** Consider a generic `LazyAdapter` base class that handles the import-and-cache pattern, allowing subclasses to only specify the import path and wrapped class.
**Effort:** Medium

#### MINOR: Font Creation Throughout UI Without Centralization
**ID:** DUP-UI2-005
**Location:** `game/ui/renderer/game_renderer.py:155-157` AND many other locations in screens/panels (excluded from this shard but noted as cross-cutting concern)
**Issue:** Within the framework shard, `game_renderer.py` creates fonts inline:
```python
font_title = pygame.font.SysFont("Arial", 16, bold=True)
font_med = pygame.font.SysFont("Arial", 14)
font_small = pygame.font.SysFont("Arial", 12)
```
While `UIConfig` exists with `FONT_TITLE`, `FONT_NAME`, `FONT_STAT` size constants and `colors.py` has `FONT_MAIN = "Arial"`, they are not used consistently. The renderer creates its own fonts rather than using centralized constants.
**Impact:** Font sizes/families are scattered. Changing the UI font requires hunting down every `pygame.font.SysFont` call.
**Recommendation:** Create a `FontManager` or extend `UIConfig` with pre-built font objects (lazily initialized) that can be imported and used consistently.
**Effort:** Simple (for framework scope)

#### MINOR: Image Scaling Utility Functions Have Overlapping Purposes
**ID:** DUP-UI2-006
**Location:** `game/ui/utils.py:32-64` AND `game/ui/utils.py:66-94` AND `game/ui/utils.py:116-163` AND `game/ui/utils.py:165-202`
**Issue:** The `utils.py` module contains four scaling-related functions:
- `calculate_ship_image_scale()` - calculates scale factor
- `scale_and_rotate_image()` - scales and rotates
- `scale_image_by_visible_portion()` - scales based on non-transparent bounds
- `scale_image_to_fit()` - scales to fit within target, centered

While not exact duplicates, these functions have overlapping concerns and some internal logic overlap (e.g., handling invalid dimensions, creating placeholder surfaces). The relationship between them is not immediately clear.
**Impact:** Developers may use the wrong function or duplicate logic when the existing functions don't quite fit their needs.
**Recommendation:** Document the function relationships clearly, or consider consolidating into a single class `ImageScaler` with clear method names indicating the transformation type.
**Effort:** Simple

#### MINOR: Placeholder Surface Creation Pattern
**ID:** DUP-UI2-007
**Location:** `game/ui/utils.py:141-143` AND `game/ui/utils.py:150-152` AND `game/ui/assets/ship_theme_manager.py:208-213`
**Issue:** Placeholder/fallback surface creation follows the same pattern in multiple places:
```python
placeholder = pygame.Surface((width, height), pygame.SRCALPHA)
placeholder.fill(color)
```
In `utils.py`, this exact pattern appears twice within the same function. `ShipThemeManager._create_fallback_image()` creates a similar fallback with lines drawn on it.
**Impact:** Minor - placeholder creation is simple. However, inconsistent placeholder appearances could confuse users during loading states.
**Recommendation:** Create a shared `create_placeholder_surface(size, color, style='solid')` utility.
**Effort:** Simple

#### MINOR: Error Exception Handling Pattern in ShipIO
**ID:** DUP-UI2-008
**Location:** `game/ui/services/ship_io.py:71-82` AND `game/ui/services/ship_io.py:115-129`
**Issue:** Both `save_ship()` and `load_ship()` have similar exception handling blocks catching multiple exception types with logging and message formatting. The patterns are similar:
```python
except PermissionError as e:
    log_error(f"ShipIO: Permission denied {verb}ing ship: {e}")
    return Error, f"{Verb} failed: Permission denied"
except OSError as e:
    log_error(f"ShipIO: OS error {verb}ing ship: {e}")
    return Error, f"{Verb} failed: {str(e)}"
```
Additionally, both have a catch-all at the end that redundantly catches `OSError, PermissionError` again.
**Impact:** Redundant exception handlers (OSError/PermissionError caught twice). Similar error formatting logic duplicated.
**Recommendation:** Extract a helper `_handle_io_error(e, operation: str) -> Tuple[bool/None, str]` that formats the error message consistently. Remove the redundant catch-all handlers.
**Effort:** Simple

#### MINOR: Tkinter Initialization Error Handling
**ID:** DUP-UI2-009
**Location:** `game/ui/services/ship_io.py:21-32` AND `game/ui/services/screenshot_manager.py:95-116`
**Issue:** Both modules have Tkinter-related code with broad exception handling:
- `ship_io.py` initializes `tkinter.Tk()` at module level with try/except catching `TclError`, `RuntimeError`, and generic `Exception`
- `screenshot_manager.py` has `_copy_to_clipboard()` with try/except for Tkinter clipboard operations

The Tkinter initialization pattern is particularly concerning as it's at module level and can affect import behavior.
**Impact:** Platform-dependent behavior scattered across files. Module-level side effects can cause issues during testing.
**Recommendation:** Centralize Tkinter initialization into a single lazy-loading utility (e.g., `TkinterHelper.get_root()`) that all UI code can use safely.
**Effort:** Medium

#### MINOR: Return Value Conventions Partially Documented
**ID:** DUP-UI2-010
**Location:** `game/ui/services/ship_io_adapter.py:28-36` (documented) vs `game/ui/services/ship_io.py` (not documented) AND `game/ui/services/design_loader_adapter.py` (partially documented)
**Issue:** The tuple return pattern `(success/object, message)` with `message=None` for cancelled operations is documented in `ShipIOAdapter` but not consistently in `ShipIO` or `DesignLoaderAdapter`. The convention exists but is scattered.
**Impact:** Developers must read code to understand return value semantics. Inconsistent null-handling expectations.
**Recommendation:** Document the return convention in a central location (perhaps in a `ReturnConventions` section of `services/__init__.py` or a dedicated conventions doc).
**Effort:** Simple

#### INFO: Camera Zoom Clamping Pattern
**ID:** DUP-UI2-011
**Location:** `game/ui/renderer/camera.py:114` AND `game/ui/renderer/camera.py:155`
**Issue:** The pattern `max(self.min_zoom, min(self.max_zoom, zoom_value))` appears twice in Camera class. This is the standard clamp pattern.
**Impact:** Minimal - this is a simple clamping operation that's clear in context.
**Recommendation:** Could add a `_clamp_zoom(value)` helper for clarity, but this is low priority. Python 3.9+ offers `math.clamp()` or `numpy.clip()`.
**Effort:** Simple (optional)

#### INFO: Vector2 Import and Usage Consistency
**ID:** DUP-UI2-012
**Location:** `game/ui/interfaces/battle_ui.py:13` AND `game/ui/services/battle_ui_service.py:24` AND `game/ui/services/ship_io.py:15`
**Issue:** Vector2 is imported from `game.core.math` in some files and from `pygame.math` in others (e.g., `camera.py` uses `pygame.math.Vector2`). Within the framework shard, there's inconsistent usage.
**Impact:** Minor confusion about which Vector2 to use. Both should be compatible, but inconsistency suggests lack of convention.
**Recommendation:** Establish a convention: use `game.core.math.Vector2` for data/interface objects, `pygame.math.Vector2` for rendering operations.
**Effort:** Simple

## Top 5 Priority Issues

1. **DUP-UI2-001 (MAJOR): Duplicated Lazy DI Provider Resolution Pattern** - Four services duplicate the same pattern with slight variations. This is the most impactful because it affects the core architecture and will require consistent updates as DI patterns evolve.

2. **DUP-UI2-004 (MAJOR): Service Adapter Wrapping Pattern** - Two adapters follow identical structural patterns. As more adapters are added (likely given the project's service architecture), this duplication will compound.

3. **DUP-UI2-003 (MAJOR): Singleton Manager Pattern Triplicated** - Three managers share the same structure. While the singleton logic is properly centralized in `SingletonMeta`, the surrounding code and documentation patterns are duplicated.

4. **DUP-UI2-002 (MAJOR): Directory Creation Pattern Duplicated in ShipIO** - Within a single file, the same 3-line block is copy-pasted. This is the simplest fix with clear benefit.

5. **DUP-UI2-009 (MINOR): Tkinter Initialization Error Handling** - Module-level Tkinter initialization can cause test isolation issues and platform-dependent behavior. Centralizing this would improve testability.
