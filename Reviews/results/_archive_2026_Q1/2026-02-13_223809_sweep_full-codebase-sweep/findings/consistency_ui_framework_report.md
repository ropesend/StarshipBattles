# Consistency Violations Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 24
- **Total Issues Found:** 14
- **Critical:** 1 | **Major:** 4 | **Minor:** 7 | **Info:** 2

## Findings

#### CRITICAL: Inconsistent Dependency Injection Patterns Across Services
**ID:** CON-UI2-001
**Location:** `game/ui/services/` (multiple files)
**Issue:** The service layer has three incompatible DI patterns:
1. **Strict DI (required):** `VehicleClassService.__init__` raises `ValueError` if `registry_provider` is None
2. **Lazy DI (optional with fallback):** `ComponentService.__init__` accepts `None` and calls `get_default_registry_provider()` lazily
3. **Class-level default:** `ValidationService.__init__` accepts `None` and uses `get_or_create_validator()` in a getter

Additionally, parameter naming is inconsistent:
- `ShipFactory` uses `registry_provider: Optional['GameRegistries']` (keyword-only `*`)
- `DesignLoaderAdapter` uses both `design_loader` AND `registry_provider` (keyword-only)
- `ComponentService` uses `registry_provider: Optional[IRegistryProvider]`

**Impact:** Developers cannot predict constructor behavior. Some services fail loudly (VehicleClassService), others silently fall back to globals. This creates confusion about which pattern to use when adding new services.
**Recommendation:** Standardize on lazy DI with optional parameter (the dominant pattern in 4 of 6 services). Update `VehicleClassService` to match unless strict DI was explicitly mandated for a documented reason (PROJ-50 mentions it, but most services don't follow it).
**Effort:** Medium

#### MAJOR: Inconsistent Return Value Conventions for Operations
**ID:** CON-UI2-002
**Location:** `game/ui/services/ship_io_adapter.py:72-103`, `game/ui/services/ship_io.py:42-127`
**Issue:** The return value conventions differ between save and load operations in ways that complicate error handling:
- **Save:** `Tuple[bool, Optional[str]]` - success flag + message
- **Load:** `Tuple[Optional[T], Optional[str]]` - object + message

While documented as intentional, the cancel case is inconsistent:
- Save cancel: `(False, None)`
- Load cancel: `(None, None)`

The first element has different semantics (boolean vs object), but the `None` message meaning is the same. This requires callers to check different things for save vs load to detect cancellation.

**Impact:** Callers must use different patterns for save vs load error handling, increasing cognitive load.
**Recommendation:** Consider introducing a dedicated `IOResult` dataclass or enum for operation outcomes (Success, Failed, Cancelled) to provide unified handling.
**Effort:** Medium

#### MAJOR: Singleton Pattern Inconsistency - instance() vs Direct Instantiation
**ID:** CON-UI2-003
**Location:** `game/ui/renderer/sprites.py:8-21`, `game/ui/services/screenshot_manager.py:11-24`, `game/ui/assets/ship_theme_manager.py:11-25`
**Issue:** All three classes use `SingletonMeta` and document `.instance()` as the usage pattern, but:
1. The `SpriteManager` and `ShipThemeManager` docstrings explicitly show `instance()` usage
2. `ScreenshotManager` documents `instance()` in docstring
3. However, none of these classes prevent direct `__init__` calls

Looking at `game/ui/renderer/game_renderer.py:47`:
```python
theme_mgr = ShipThemeManager.instance()
```

This is correct, but there's no enforcement preventing `ShipThemeManager()` direct calls which would bypass singleton semantics.

**Impact:** Inconsistent instantiation could lead to multiple instances bypassing singleton behavior in tests or during refactoring.
**Recommendation:** Add documentation or runtime checks to enforce `.instance()` pattern consistently. Consider adding a `__new__` guard or deprecation warning for direct instantiation.
**Effort:** Simple

#### MAJOR: Mixed Docstring Styles
**ID:** CON-UI2-004
**Location:** Multiple files across `game/ui/services/`, `game/ui/renderer/`
**Issue:** Docstring format varies between files:
1. **Google style (Args/Returns):** Most service files use this consistently
   - `validation_service.py`, `component_service.py`, `vehicle_class_service.py`
2. **Abbreviated inline:** `ship_io.py` uses minimal docstrings
   - Line 42: `"""Save ship design to file. Returns True if successful."""`
3. **Missing returns documentation:** Some functions document Args but not Returns
   - `game_renderer.py:draw_ship` has no docstring at all

**Impact:** Inconsistent documentation style increases cognitive load when navigating the codebase.
**Recommendation:** Standardize on Google-style docstrings (Args/Returns) as the dominant pattern. Add docstrings to `draw_ship` and similar public functions.
**Effort:** Simple

#### MAJOR: Module-Level Side Effects in ship_io.py
**ID:** CON-UI2-005
**Location:** `game/ui/services/ship_io.py:20-32`
**Issue:** The module has module-level initialization that creates a Tkinter root:
```python
try:
    tk_root = tkinter.Tk()
    tk_root.withdraw()
except tkinter.TclError as e:
    ...
```

This violates the lazy initialization pattern used elsewhere:
- `ShipThemeManager` uses lazy `initialize()` method
- `SpriteManager` uses `load_sprites()` after construction

This was noted in `game/ui/__init__.py` line 6-9 as a known issue for `workshop_screen`, but `ship_io` has the same problem.

**Impact:** Importing `ship_io` triggers Tkinter initialization even when file dialogs aren't needed, causing test isolation issues and startup overhead.
**Recommendation:** Convert to lazy initialization pattern: move Tkinter init into a method called on first use.
**Effort:** Medium

#### MINOR: Inconsistent Method Naming - get_ vs load_ for Retrieval Operations
**ID:** CON-UI2-006
**Location:** Multiple files
**Issue:** Retrieval operations use inconsistent verb prefixes:
- `get_*`: `get_all_classes()`, `get_class_definition()`, `get_binding()`, `get_sprite()`, `get_available_themes()`
- `load_*`: `load_image()`, `load_ship_from_file()`, `load_sprites()`, `load_ship()`
- `_load_*` (private): `_load_single_image()`, `_load_portrait_image()`, `_load_bindings_from_file()`

The semantic distinction appears to be:
- `get_*` = cached/memory access
- `load_*` = disk I/O involved

But this isn't consistently applied:
- `get_image_metrics()` may trigger `load_image()` internally
- `get_portrait_image()` calls `_load_portrait_image()` internally

**Impact:** Minor cognitive overhead when predicting method behavior.
**Recommendation:** Document the convention: `get_*` for cached/fast access, `load_*` for explicit I/O. Update `get_portrait_image` to `load_portrait_image` since it does I/O.
**Effort:** Simple

#### MINOR: Inconsistent Type Hint Coverage
**ID:** CON-UI2-007
**Location:** `game/ui/services/ship_io.py:42`, `game/ui/renderer/game_renderer.py:22`
**Issue:** Some files have complete type hints while others have partial or none:
- **Complete:** `validation_service.py`, `input_mapper.py`, `camera.py`, `battle_ui.py`
- **Partial:** `ship_io.py` - missing return types on methods
- **Missing:** `game_renderer.py:draw_ship` - no type hints at all

```python
# ship_io.py:42 - missing return type
def save_ship(ship):  # Should be: def save_ship(ship: Any) -> Tuple[bool, Optional[str]]:

# game_renderer.py:22 - no type hints
def draw_ship(surface, ship, camera):  # Should have all types
```

**Impact:** Reduced IDE support and static analysis coverage.
**Recommendation:** Add type hints to all public functions, prioritizing `ship_io.py` and `game_renderer.py`.
**Effort:** Simple

#### MINOR: Inconsistent Error Logging Patterns
**ID:** CON-UI2-008
**Location:** `game/ui/services/ship_io.py:72-79`, `game/ui/assets/ship_theme_manager.py:112-115`
**Issue:** Error logging format varies:
```python
# ship_io.py - includes class name prefix
log_error(f"ShipIO: Permission denied saving ship: {e}")

# ship_theme_manager.py - no class name prefix
log_error(f"Image not found for {theme_name}/{ship_class}: {filename}")

# screenshot_manager.py - no prefix
log_error(f"Failed to create screenshot directory: {e}")
```

**Impact:** Log analysis is harder when some messages include class context and others don't.
**Recommendation:** Standardize on including class/module context in error messages: `log_error(f"{class_name}: {message}: {error}")`.
**Effort:** Simple

#### MINOR: Inconsistent Private Method Naming
**ID:** CON-UI2-009
**Location:** Multiple files
**Issue:** Private method underscore prefix usage is inconsistent:
- **Single underscore (correct):** `_get_validator()`, `_get_provider()`, `_convert_ship()`, `_load_single_image()`
- **No underscore (should be private):** `camera.py` has no explicit private markers on internal helper methods

In `camera.py`, the zoom anchor fields use underscore:
```python
self._zoom_anchor_world = None
self._zoom_anchor_screen = None
```
But all methods are public despite some being internal helpers.

**Impact:** API surface is unclear - hard to distinguish public vs internal methods.
**Recommendation:** Prefix internal helper methods with underscore consistently.
**Effort:** Simple

#### MINOR: Boolean Parameter Naming Inconsistency
**ID:** CON-UI2-010
**Location:** `game/ui/services/battle_factories.py:35`, `game/ui/services/screenshot_manager.py:119`
**Issue:** Boolean parameters don't consistently use is_/has_/should_ prefixes:
```python
# battle_factories.py
headless: bool = False  # Should be: is_headless or run_headless

# screenshot_manager.py
include_ui=True  # Should be: should_include_ui
include_subwindows=True  # Should be: should_include_subwindows
```

**Impact:** Minor semantic clarity issue.
**Recommendation:** For new code, prefer action-oriented names (should_, include_) or state names (is_). Current usage is acceptable but not optimal.
**Effort:** Simple

#### MINOR: Inconsistent Import Organization
**ID:** CON-UI2-011
**Location:** `game/ui/services/ship_io.py:1-18`, `game/ui/services/screenshot_manager.py:1-8`
**Issue:** Import grouping and ordering varies:
```python
# ship_io.py - mixed stdlib and local
import json
import os
import tkinter
from tkinter import filedialog
from game.core.math import Vector2
from game.simulation.entities.ship import Ship
...

# screenshot_manager.py - grouped but different order
import os
import datetime
import subprocess
import pygame
from game.core.constants import ENABLE_SCREENSHOTS
...
```

PEP 8 convention: stdlib, third-party, local, each separated by blank line.

**Impact:** Minor readability issue.
**Recommendation:** Standardize import ordering: stdlib (alphabetical) -> third-party (pygame) -> local (game.*). Add blank lines between groups.
**Effort:** Simple

#### MINOR: Magic Numbers in Rendering Code
**ID:** CON-UI2-012
**Location:** `game/ui/renderer/game_renderer.py:33-34,81,141`
**Issue:** Several magic numbers in rendering code:
```python
radius_screen = 50 * camera.zoom  # Line 33 - why 50?
pygame.draw.circle(surface, (100, 255, 100), ...)  # Line 81 - what is this color?
pygame.draw.circle(surface, color, (cx, cy), max(2, scale(3)))  # Line 141 - magic 2 and 3
```

Meanwhile, `game/ui/config.py` exists specifically for UI constants but isn't used in `game_renderer.py`.

**Impact:** Hard to understand and maintain rendering constants.
**Recommendation:** Move rendering constants to `UIConfig` or create a `RenderConfig` class in `game_renderer.py`.
**Effort:** Simple

#### INFO: Inconsistent __all__ Export Patterns
**ID:** CON-UI2-013
**Location:** `game/ui/__init__.py`, `game/ui/services/__init__.py`, `game/ui/renderer/__init__.py`
**Issue:** Some `__init__.py` files define `__all__` exports, others are minimal or empty:
- `game/ui/__init__.py`: Full imports + `__all__` list
- `game/ui/services/__init__.py`: Full imports + `__all__` list
- `game/ui/renderer/__init__.py`: Empty (1 line, no exports)
- `game/ui/interfaces/__init__.py`: Full imports + `__all__` list
- `game/ui/orchestration/__init__.py`: Single import + `__all__` list

**Impact:** Inconsistent API discoverability.
**Recommendation:** Either populate `game/ui/renderer/__init__.py` with exports like other packages, or document that some packages are meant to be imported directly.
**Effort:** Simple

#### INFO: Comment Style Variation
**ID:** CON-UI2-014
**Location:** Various files
**Issue:** Inline comments use different styles:
```python
# With space after hash (standard)
# This is a comment

#No space after hash (non-standard, rare)
#some comment

# End-of-line comments with various spacing
self._validator = validator  # Optional validator
self._validator = validator    # Wider spacing
```

**Impact:** Very minor readability variation.
**Recommendation:** Enforce PEP 8 comment style in linting: single space after `#`.
**Effort:** Simple

## Top 5 Priority Issues

1. **CON-UI2-001 (CRITICAL): Inconsistent DI Patterns** - Developers cannot predict constructor behavior across services. Some fail loudly, others silently fall back. Standardize on lazy DI with optional parameter.

2. **CON-UI2-005 (MAJOR): Module-Level Side Effects in ship_io.py** - Tkinter initialization at import time causes test isolation issues and startup overhead. Convert to lazy initialization.

3. **CON-UI2-002 (MAJOR): Inconsistent Return Value Conventions** - Save vs load operations use different return semantics, complicating error handling. Consider introducing `IOResult` dataclass.

4. **CON-UI2-007 (MINOR): Incomplete Type Hints** - Public functions in `ship_io.py` and `game_renderer.py` lack type hints, reducing IDE support and static analysis coverage.

5. **CON-UI2-012 (MINOR): Magic Numbers in Rendering** - Rendering code has undocumented magic numbers while `UIConfig` exists but isn't used. Move constants to config.
