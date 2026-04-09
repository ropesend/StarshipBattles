# PROJ-258: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Singleton Landscape

The codebase has 11 singletons using `SingletonMeta` (thread-safe metaclass with double-checked locking). All follow the same pattern: `MyClass(metaclass=SingletonMeta)` with `.instance()` access and `.reset()` for test teardown.

**Call site counts (production):**
- RegistryManager: 9 calls in `game/core/registry.py` (wrapper functions) + `game/app.py` + `game/ui/screens/strategy_detail_fmt.py`
- StrategyMetadataService: 11 calls across AI layer and UI panels/screens
- ShipThemeManager: 8 calls across renderer, panels, and screens
- ScreenshotManager: 6 calls across UI screens
- Profiler: 6 calls in `game/app.py` and `game/core/profiling.py`
- AssetManager: 3 calls in asset manager and data sources
- SpriteManager: 2 calls in `game/app.py` and workshop
- StrategyManager: 2 calls in controller and workshop_data_loader
- ComponentCacheManager: 2 calls in component_loader
- GameSettings: 2 calls via `GameSettings()` (uses `__call__` through metaclass)
- SessionRegistryCache: 3 calls (test infrastructure only, manual singleton)

**Test call sites:** 284 `.instance()` calls across 43 test files. Most are in test setup/teardown for singleton state management.

### Existing DI Infrastructure

DI is already partially implemented for `RegistryManager`:
- `IRegistryProvider` protocol in `game/core/protocols.py`
- `DefaultRegistryProvider` wraps RegistryManager singleton
- `TestRegistryProvider` provides isolated test data
- `get_default_registry_provider()` returns a shared DefaultRegistryProvider

This pattern works well and should be extended to all singletons.

### Test Isolation Current State

Test isolation is handled by scattered mechanisms:
- Per-test-directory `conftest.py` files with autouse fixtures that call `SomeManager.reset()`
- Some tests do their own setup/teardown with `reset()` in `setUp`/`tearDown`
- `SessionRegistryCache` (manual singleton) loads data once per session
- Root `conftest.py` provides `session_registries`, `fresh_registries`, `minimal_registries`
- No global autouse `reset_game_state` fixture exists despite references to it in comments

## ApplicationContext Design

### Core Principle: Container, Not Service Locator

`ApplicationContext` is a **dependency injection container** — it holds references to all services and is passed explicitly to code that needs them. It is **not** a service locator (global registry queried by name at runtime).

**Container (correct):**
```python
class BattleScreen:
    def __init__(self, width, height, ctx: ApplicationContext):
        self.screenshot_mgr = ctx.screenshot_manager
        self.sprite_mgr = ctx.sprite_manager
```

**Service locator (wrong):**
```python
class BattleScreen:
    def __init__(self, width, height):
        self.screenshot_mgr = ApplicationContext.get("screenshot_manager")
```

### Class Design

```python
# game/core/application_context.py

class ApplicationContext:
    """Dependency injection container for all application services.

    Created once at application startup (production) or per-test (testing).
    Passed explicitly to all code that needs service references.

    NOT itself a singleton — the caller (app.py or conftest.py) manages
    the instance lifetime.
    """

    def __init__(
        self,
        registry_manager: RegistryManager,
        profiler: Profiler,
        strategy_metadata: StrategyMetadataService,
        component_cache: ComponentCacheManager,
        strategy_manager: StrategyManager,
        asset_manager: AssetManager,
        sprite_manager: SpriteManager,
        ship_theme_manager: ShipThemeManager,
        screenshot_manager: ScreenshotManager,
        game_settings: GameSettings,
    ):
        self.registry_manager = registry_manager
        self.profiler = profiler
        self.strategy_metadata = strategy_metadata
        self.component_cache = component_cache
        self.strategy_manager = strategy_manager
        self.asset_manager = asset_manager
        self.sprite_manager = sprite_manager
        self.ship_theme_manager = ship_theme_manager
        self.screenshot_manager = screenshot_manager
        self.game_settings = game_settings

    @classmethod
    def create_production(cls) -> 'ApplicationContext':
        """Create the production application context.

        Instantiates all services with their production configurations.
        Called once from game/app.py at startup.
        """
        return cls(
            registry_manager=RegistryManager(),
            profiler=Profiler(),
            strategy_metadata=StrategyMetadataService(),
            component_cache=ComponentCacheManager(),
            strategy_manager=StrategyManager(),
            asset_manager=AssetManager(),
            sprite_manager=SpriteManager(),
            ship_theme_manager=ShipThemeManager(),
            screenshot_manager=ScreenshotManager(),
            game_settings=GameSettings(),
        )

    @classmethod
    def create_test(cls, **overrides) -> 'ApplicationContext':
        """Create a test application context.

        Creates minimal/mock service instances suitable for testing.
        Pass keyword arguments to override specific services.
        """
        # Build with test-friendly defaults, allow overrides
        ...
```

### Factory Methods

**`create_production()`**
- Called once in `game/app.py` Game.__init__()
- Creates all service instances with real initialization
- Services that need file paths use `Paths` constants

**`create_test(**overrides)`**
- Called in test conftest.py fixtures
- Creates lightweight/minimal service instances
- Individual services can be overridden via kwargs
- No file I/O by default (services created without loading data)

### Migration Strategy: Wrapper First, Then One-at-a-Time

#### Phase 1: Wrapper (all tests stay green)

In Phase 1, `ApplicationContext` is created but wraps existing singletons. The `.instance()` calls still work because singletons still exist. `ApplicationContext` just provides an alternative access path.

```python
# Phase 1: ApplicationContext wraps singletons
@classmethod
def create_production(cls) -> 'ApplicationContext':
    return cls(
        registry_manager=RegistryManager.instance(),
        profiler=Profiler.instance(),
        ...
    )
```

This means:
- All existing code continues to work via `.instance()`
- New code can start using `ctx.profiler` etc.
- Zero risk of breaking anything

#### Phases 2-4: Migrate one singleton at a time

For each singleton:
1. Remove `metaclass=SingletonMeta` from the class
2. The class becomes a plain class (no singleton behavior)
3. `ApplicationContext` creates the instance directly
4. Update all production `.instance()` call sites to receive instance from context
5. Update all test call sites to use `ctx.some_service` or direct construction
6. One commit per singleton for bisectability

#### Phase 5: Simplify test infrastructure

After all singletons are migrated:
- conftest.py provides `ApplicationContext.create_test()` based fixtures
- Per-directory conftest.py autouse fixtures simplified (no more `.reset()` calls)
- `SessionRegistryCache` refactored to work with ApplicationContext

### How conftest.py Simplifies After Migration

**Before (current):**
```python
# tests/unit/core/registry/conftest.py
@pytest.fixture(autouse=True)
def reset_registry(request):
    from game.core.registry import RegistryManager
    from game.core.singleton import SingletonMeta
    original_instance = SingletonMeta._instances.get(RegistryManager)
    # ... 20 lines of save/reset/restore logic ...
    RegistryManager.reset()
    yield
    # ... 15 lines of restore logic ...
```

**After (target):**
```python
# tests/unit/core/registry/conftest.py
@pytest.fixture(autouse=True)
def test_context():
    ctx = ApplicationContext.create_test()
    yield ctx
    # No cleanup needed - context goes out of scope, instances are GC'd
```

**Before (scattered resets):**
```python
# Various conftest.py files
Profiler.reset()
StrategyManager.reset()
ShipThemeManager.reset()
SpriteManager.reset()
RegistryManager.reset()
ComponentCacheManager.reset()
```

**After (single context):**
```python
ctx = ApplicationContext.create_test()
# All services are fresh instances, no global state to reset
```

### Layer Compliance

`ApplicationContext` lives in `game/core/` because:
- Core is the foundation layer, depended on by all other layers
- The context holds references to services from multiple layers
- Upper layers (UI, AI) receive the context via DI, not by importing it

**Import concern:** `ApplicationContext` imports classes from UI, AI, etc. layers. This creates an apparent upward dependency from Core. Resolution: use `TYPE_CHECKING` imports and late binding in factory methods, or place `ApplicationContext` in a new top-level module (`game/context.py`) outside the layer hierarchy.

**Recommended approach:** Place `ApplicationContext` in `game/context.py` (new module at the `game/` package level, outside any layer). The factory methods use late imports to avoid circular dependencies.

```python
# game/context.py — outside layer hierarchy
class ApplicationContext:
    @classmethod
    def create_production(cls):
        from game.core.registry import RegistryManager
        from game.core.profiling import Profiler
        from game.ai.strategy_manager import StrategyManager
        from game.ui.renderer.sprites import SpriteManager
        # ... etc
        return cls(
            registry_manager=RegistryManager(),
            ...
        )
```

### Backward Compatibility During Migration

During the multi-phase migration, some singletons will be migrated while others still use `SingletonMeta`. This is fine because:
- Migrated singletons: accessed via `ctx.some_service`
- Not-yet-migrated singletons: still accessed via `.instance()`
- `ApplicationContext.__init__` accepts any instance, regardless of how it was created

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
