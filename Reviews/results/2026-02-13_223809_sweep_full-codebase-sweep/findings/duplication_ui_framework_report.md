# Duplication & Fragmentation Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 26
- **Total Issues Found:** 8
- **Critical:** 1 | **Major:** 3 | **Minor:** 3 | **Info:** 1

## Findings

#### CRITICAL: Tkinter Root Initialization Duplicated Across 4 Files
**ID:** DUP-UI2-001
**Location:**
- `game/ui/services/ship_io.py:20-32`
- `game/ui/services/screenshot_manager.py:95-104`
- `game/ui/screens/formation_editor.py:23-30`
- `game/ui/screens/workshop_ship_io.py:18-26`

**Issue:** Identical Tkinter initialization pattern with try/except blocks is duplicated across 4 files. Each file separately:
1. Creates a `tkinter.Tk()` instance
2. Calls `withdraw()` to hide it
3. Handles `TclError` and `RuntimeError` exceptions
4. Sets a module-level variable to None on failure

The code is near-identical with minor variations:
- `ship_io.py` catches TclError, RuntimeError, and broad Exception separately
- `screenshot_manager.py` does per-use initialization inside a method (different pattern)
- `formation_editor.py` catches `(TclError, RuntimeError)` as tuple
- `workshop_ship_io.py` adds SDL_VIDEODRIVER dummy check

**Impact:** High maintenance risk - if initialization logic needs to change (e.g., new exception type), 4 files must be updated. Active divergence already exists in exception handling approaches, suggesting bugs may hide in the less-tested variants. If one location gets a fix for a Tkinter edge case, others will be missed.

**Recommendation:** Extract a shared `get_tk_root()` function in `game/ui/utils.py` or create a dedicated `game/ui/services/tkinter_utils.py` module:
```python
# game/ui/services/tkinter_utils.py
_tk_root = None
_initialized = False

def get_tk_root():
    global _tk_root, _initialized
    if _initialized:
        return _tk_root
    # ... unified initialization logic
```

**Effort:** Simple

---

#### MAJOR: Battle Factory Functions Follow Identical Structural Pattern
**ID:** DUP-UI2-002
**Location:** `game/ui/services/battle_factories.py:31-179`

**Issue:** Four factory functions (`create_manual_battle`, `create_test_battle`, `create_strategy_battle`, `create_hypothetical_battle`) follow an almost identical pattern:
1. Create `BattleController(ai_factory=_create_default_ai_factory())`
2. Create `BattleConfig(mode=..., seed=seed, headless=..., <mode-specific args>)`
3. Call `controller.configure(config)`
4. Optionally add ships and call `controller.start()`

Lines 49, 81, 114, and 147 all repeat `controller = BattleController(ai_factory=_create_default_ai_factory())`. The BattleConfig construction is near-identical with only the mode and 1-2 parameters varying.

**Impact:** Moderate maintenance risk. Changes to the battle creation workflow require updates to 4 functions. The structural similarity (80%+ shared logic) indicates a builder or template pattern would be more appropriate.

**Recommendation:** Consider a single `create_battle()` function with a mode parameter or a BattleBuilder class:
```python
def create_battle(mode: BattleMode, **kwargs) -> BattleController:
    controller = BattleController(ai_factory=_create_default_ai_factory())
    config = BattleConfig(mode=mode, **kwargs)
    controller.configure(config)
    return controller
```

**Effort:** Medium

---

#### MAJOR: Service DI Pattern Duplicated with Inconsistent Implementations
**ID:** DUP-UI2-003
**Location:**
- `game/ui/services/component_service.py:31-50`
- `game/ui/services/vehicle_class_service.py:36-52`
- `game/ui/services/validation_service.py:33-46`
- `game/ui/services/ship_factory.py:40-56`
- `game/ui/services/design_loader_adapter.py:31-44`

**Issue:** Five service classes implement similar dependency injection patterns with slight inconsistencies:
- `ComponentService`: Optional `registry_provider`, lazy resolution via `get_default_registry_provider()`
- `VehicleClassService`: **Required** `registry_provider`, raises ValueError if None (PROJ-50 strict DI)
- `ValidationService`: Optional `validator`, lazy resolution via `get_or_create_validator()`
- `ShipFactory`: Optional `registry_provider`, supports method-level override
- `DesignLoaderAdapter`: Optional both `design_loader` and `registry_provider`

The `_get_provider()` pattern is duplicated in `ComponentService` and `VehicleClassService` with identical logic.

**Impact:** Inconsistent DI patterns create cognitive overhead. Developers must check each service to know if the provider is required or optional. The drift between "strict DI" (VehicleClassService) and "lazy resolution" (others) is undocumented in the pattern itself.

**Recommendation:** Create a base class or mixin for common DI patterns:
```python
class RegistryConsumerMixin:
    def __init__(self, registry_provider: Optional[IRegistryProvider] = None, strict: bool = False):
        if strict and registry_provider is None:
            raise ValueError("registry_provider is required (strict DI)")
        self._provider = registry_provider

    def _get_provider(self) -> IRegistryProvider:
        if self._provider is None:
            self._provider = get_default_registry_provider()
        return self._provider
```

**Effort:** Medium

---

#### MAJOR: BattleUIService Repeated Null-Check Pattern
**ID:** DUP-UI2-004
**Location:** `game/ui/services/battle_ui_service.py:62-131`

**Issue:** Six methods in `BattleUIService` repeat the same pattern:
```python
engine = self._battle_service.get_engine()
if engine is None:
    return <default_value>
```

Lines 68-72, 80-84, 94-98, 106-109, 117-120, 128-131 all follow this pattern. The early-return default varies by method (empty list, True, None, 0).

**Impact:** Low-moderate risk. The pattern is functionally correct but violates DRY. If `get_engine()` semantics change (e.g., throws instead of returning None), 6 locations need updating.

**Recommendation:** Extract a helper method or use a decorator:
```python
def _with_engine(self, fallback):
    engine = self._battle_service.get_engine()
    if engine is None:
        return fallback
    return engine

# Or use a property:
@property
def _engine(self) -> Optional[BattleEngine]:
    return self._battle_service.get_engine()
```

**Effort:** Simple

---

#### MINOR: Image Loading Pattern Repeated Without Caching Abstraction
**ID:** DUP-UI2-005
**Location:** Multiple files across UI layer (not all in scope, but pattern visible in):
- `game/ui/assets/ship_theme_manager.py:146-165` (with caching)
- `game/ui/renderer/sprites.py:80-82` (basic load)

**Issue:** The pattern `pygame.image.load(path).convert_alpha()` followed by error handling appears throughout the UI layer. While `ShipThemeManager` implements proper caching, the `SpriteManager` in `sprites.py` loads without the same sophisticated caching and metrics extraction.

Both are singletons that manage image loading but with different approaches:
- `ShipThemeManager`: Thread-safe lazy loading with metrics caching
- `SpriteManager`: Eager bulk loading without thread safety

**Impact:** Low. These serve different purposes (ship themes vs component sprites) but the divergent patterns suggest consolidation opportunities.

**Recommendation:** Consider a shared `ImageLoader` utility that both managers could use for the actual pygame loading, error handling, and basic caching.

**Effort:** Medium

---

#### MINOR: Ship Cloning Logic in create_hypothetical_battle
**ID:** DUP-UI2-006
**Location:** `game/ui/services/battle_factories.py:158-173`

**Issue:** Ship cloning logic is duplicated for team 1 and team 2:
```python
cloned1 = []
for ship in ships1:
    data = ShipSerializer.to_dict(ship)
    cloned = ShipSerializer.from_dict(data, registries=ship.registries)
    cloned.x, cloned.y = ship.x, ship.y
    cloned1.append(cloned)

cloned2 = []
for ship in ships2:
    # ... identical logic
```

**Impact:** Low. Only affects one function, but it's a clear copy-paste that could be extracted.

**Recommendation:** Extract to a helper function:
```python
def _clone_ships(ships: List['Ship']) -> List['Ship']:
    cloned = []
    for ship in ships:
        data = ShipSerializer.to_dict(ship)
        clone = ShipSerializer.from_dict(data, registries=ship.registries)
        clone.x, clone.y = ship.x, ship.y
        cloned.append(clone)
    return cloned
```

**Effort:** Simple

---

#### MINOR: Singleton Pattern with Same Structure
**ID:** DUP-UI2-007
**Location:**
- `game/ui/services/screenshot_manager.py:11-28`
- `game/ui/renderer/sprites.py:8-26`
- `game/ui/assets/ship_theme_manager.py:11-54`

**Issue:** Three classes use `SingletonMeta` with similar initialization patterns. All have:
- `__init__` that initializes state
- Comment blocks explaining thread safety via SingletonMeta
- Similar usage patterns (`ClassName.instance()`)

**Impact:** Low. The pattern itself is consistent (using `SingletonMeta`), but the docstrings are slightly duplicated explaining the same metaclass behavior.

**Recommendation:** No immediate action needed - using a shared metaclass is already the right abstraction. Could optionally add a base class docstring that explains the pattern once.

**Effort:** N/A (informational)

---

#### INFO: Adapter Classes Follow Consistent Pattern (Good)
**ID:** DUP-UI2-008
**Location:**
- `game/ui/services/ship_io_adapter.py`
- `game/ui/services/design_loader_adapter.py`

**Issue:** Both adapter classes follow a consistent pattern: wrapping a lower-layer class with a UI-friendly interface. This is intentional structural similarity, not harmful duplication. The pattern is:
1. Accept optional dependency in `__init__`
2. Lazy-resolve dependency if not provided
3. Delegate to underlying service

**Impact:** None - this is good design following the Adapter pattern consistently.

**Recommendation:** No changes needed. Document this as the standard adapter pattern for UI services in the codebase.

**Effort:** N/A

---

## Top 5 Priority Issues

1. **DUP-UI2-001 (CRITICAL):** Tkinter initialization duplicated across 4 files with active divergence - highest maintenance risk and bug potential
2. **DUP-UI2-003 (MAJOR):** Service DI pattern inconsistency creates developer confusion and maintenance burden
3. **DUP-UI2-002 (MAJOR):** Battle factory functions have 80%+ structural duplication that could be consolidated
4. **DUP-UI2-004 (MAJOR):** BattleUIService engine null-check repeated 6 times - simple extraction opportunity
5. **DUP-UI2-006 (MINOR):** Ship cloning copy-paste in hypothetical battle factory - quick win
