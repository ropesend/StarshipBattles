# Pattern Catalogue: game/ Codebase

**Date:** 2026-03-13
**Scope:** `game/` directory -- 429 Python files, ~95K lines
**Layers:** core (21), simulation (73), strategy (113), ai (10), ui (197), engine (3), research (6), assets (1), app (1)

---

## Summary

**Total pattern variants found across 7 categories: 52**

The codebase shows strong consistency in most areas, reflecting disciplined refactoring projects (PROJ-45, PROJ-171, PROJ-204, etc.). The dominant patterns are well-documented with centralized modules. Key outlier areas worth cleanup attention:

1. **Exception types:** ~11 uses of bare `ValueError`/`TypeError`/`RuntimeError` outside the custom hierarchy
2. **Broad except catches:** ~5 unlabeled `except Exception` (vs. ~15 properly annotated ones)
3. **Direct file I/O:** ~5 files bypass `json_utils` for JSON reading/writing
4. **Logging in error handlers:** Some `except` blocks use `print()` (15 occurrences across 9 files)
5. **Import ordering:** Minor inconsistencies (logging import sometimes before, sometimes after local imports)

---

## 1. Error Handling Patterns

### 1.1 Exception Types Used

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| Custom `ValidationException` | `ship_validator.py`, `battle_engine.py`, `component.py`, `ship.py` | ~45 raise sites | **Dominant** for input validation |
| Custom `PersistenceException` | `validation_helpers.py`, `galaxy.py`, `game_session.py`, `stars.py`, `storm.py` | ~30 raise sites | Dominant for serialization/from_dict |
| Custom `FormulaException` | `formula_system.py`, `modifier_effects.py` | ~10 raise sites | Specialized for eval() errors |
| Custom `StateException` | `battle_controller.py`, `battle_state_manager.py`, `ai_factory.py` | ~5 raise sites | Object state violations |
| Custom `FrozenStateException` | `registry.py` | ~3 raise sites | Modifying frozen registries |
| Custom `ResourceException` / `MissingResourceException` | `paths.py`, `asset_manager.py`, `ship_loader.py` | ~4 raise sites | Resource loading failures |
| Custom `ComponentException` | Usage via catch only in `error_codes.py` | ~2 sites | Rarely raised directly |
| Stdlib `ValueError` | `command_handlers.py`, `component.py`, `ship_loader.py`, `fleet_capability_calculator.py` | ~11 raise sites | **Outlier** -- should be custom |
| Stdlib `TypeError` | `abilities/base.py` | 1 raise site | Class attribute validation |
| Stdlib `RuntimeError` | `builder/modifier_logic.py` | 1 raise site | **Outlier** |
| Stdlib `NotImplementedError` | `behaviors.py`, `table/selection.py`, `table/data_source.py`, `battle_panels.py` | ~12 raise sites | ABC-style abstract methods |
| Stdlib `FileNotFoundError` | `tech_preset_loader.py`, `asset_manager.py` | ~3 raise sites | File operations |
| Stdlib `IndexError` | `math.py` | 1 raise site | Vector2 bounds checking |

**Dominant Pattern:** Custom exception hierarchy (`game.core.exceptions`) with error codes (`game.core.error_codes`)
**Recommended Standard:** Migrate remaining `ValueError`/`RuntimeError` raises to appropriate custom exceptions

### 1.2 Exception Handling Styles

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| Specific exception types with `as e` | `json_utils.py`, `save_game_service.py`, `design_library.py`, `race_library.py` | ~85% of catch blocks | **Dominant** -- granular handling |
| Bare `except Exception` with annotation comment | `app.py`, `event_bus.py`, `formula_system.py`, `tkinter_utils.py`, `screenshot_manager.py` | ~15 sites | Properly justified with `# Intentional broad catch:` comment |
| Bare `except Exception` without annotation | `empire.py`, `fleet.py`, `fleet_order_serializer.py`, `design_cost_calculator.py`, `race_environment_panel.py` | ~5 sites | **Outlier** -- needs annotation or narrowing |
| Silent `except` (swallow) with no re-raise | `ship_formation.py` (ValueError), `input_mapper.py` (ValueError), `renderer/sprites.py` (ValueError) | ~10 sites | Conversion/parsing where fallback is expected |

### 1.3 Error Propagation Strategies

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| Catch-and-convert with `raise ... from e` | `formula_system.py`, `modifier_effects.py`, `validation_helpers.py`, `game_session.py`, `galaxy.py` | ~27 sites | **Dominant** for boundary crossing |
| Catch-and-convert without chaining | `component.py`, `ship_serialization.py` | ~8 sites | Older code, should add `from e` |
| Log-and-return-default | `json_utils.py` `load_json()`, `save_game_service.py` | ~20 sites | For non-critical loads |
| Log-and-skip (resilient degradation) | `json_utils.py` `deserialize_list()`, `save_game_service.py`, `galaxy.py` | ~10 sites | Skip invalid items in lists |
| Re-raise unchanged | `app.py` (top-level crash handler), `ship_serialization.py` | ~3 sites | Diagnostic logging before re-raise |

### 1.4 Error Context

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| ErrorCode enum + context dict | `validation_helpers.py`, `registry.py`, `battle_engine.py`, `astrophysics_loader.py` | ~60% of custom exceptions | **Dominant** -- PROJ-45 standard |
| Message-only (no code/context) | `command_handlers.py`, `fleet_capability_calculator.py` (ValueError) | ~20% of raises | Older code or stdlib exceptions |
| Context dict without ErrorCode | Some `ValidationException` raises | ~20% of custom exceptions | Missing code parameter |

**Dominant Pattern:** `raise CustomException("msg", code=ErrorCode.XXX.value, context={...}) from e`
**Recommended Standard:** All exception raises should include error code and context dict

---

## 2. Logging Patterns

### 2.1 Logger Initialization

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| Module-level `logger = logging.getLogger(__name__)` | 130+ files across all layers | ~97% of files using logging | **Dominant** -- consistent |
| Inside-function/method `logger = logging.getLogger(__name__)` | `galaxy.py:606`, `strategy_window_manager.py:617`, `design_report_panel.py:216` | 3 sites | **Outlier** -- lazy init in methods |
| Inside `try/except` for conditional import | `event_logging.py`, `ai/__init__.py` | 2 sites | Import-time fallback |

### 2.2 Log Message Formatting

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| f-strings: `logger.info(f"msg {var}")` | All layers extensively | ~97% (~678 of ~874 log calls) | **Dominant** |
| %-style: `logger.info("msg %s", var)` | `ai/__init__.py`, `combat_utils.py`, `battle_panels.py`, `race_environment_panel.py` | ~4 sites (0.5%) | **Outlier** -- legacy |
| Plain strings (no interpolation) | Scattered | ~22% (~162 calls) | Status messages, no data |

### 2.3 Log Level Usage

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `logger.debug()` | `json_utils.py`, `ship.py`, `battle_service.py` | ~15% of log calls | File ops, state transitions |
| `logger.info()` | `production_engine.py`, `fleet_order_processor.py`, `command_handlers.py` | ~35% of log calls | Business logic events |
| `logger.warning()` | `design_library.py`, `registry_loader.py`, `save_game_service.py` | ~30% of log calls | Recoverable issues |
| `logger.error()` | `json_utils.py`, `save_game_service.py`, `asset_manager.py` | ~20% of log calls | Errors that may lose data |
| `logger.critical()` | None found | 0% | Not used anywhere |

### 2.4 print() vs. logging

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `logging` module | 130+ files | ~99% of debug output | **Dominant** |
| `print()` calls | `protocols.py`, `stars.py`, `system_blueprints_loader.py`, `system_mode.py` | 15 total across 9 files | **Outlier** -- mostly debug prints or Protocol docs |

**Dominant Pattern:** Module-level `logger = logging.getLogger(__name__)` with f-string messages
**Recommended Standard:** Convert remaining %-style formatting to f-strings; replace `print()` with `logger.debug()`

---

## 3. Data Access Patterns

### 3.1 JSON File I/O

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `load_json()` / `save_json()` from `game.core.json_utils` | `save_game_service.py`, `design_library.py`, `race_library.py`, `setup_data_io.py`, etc. | 74 call sites across 34 files | **Dominant** -- centralized |
| `load_json_required()` | `tech_preset_loader.py`, `ship_loader.py` | ~5 call sites | For critical files |
| Direct `json.load()` / `json.dump()` | `battle_state.py`, `ship_instance.py`, `naming.py`, `battle_engine.py`, `test_lab/validation_manager.py` | ~10 sites (5 files) | **Outlier** -- bypass centralized |
| `json.loads()` / `json.dumps()` (in-memory) | `battle_state.py`, `ship_instance.py`, `scrollable_json_panel.py` | ~15 sites | Appropriate -- serialization to/from strings |

### 3.2 Serialization Pattern

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `to_dict()` / `from_dict()` class methods | `fleet.py`, `empire.py`, `galaxy.py`, `ship_instance.py`, `stars.py`, `storm.py`, `battle_state.py` | 210 references across 38 files | **Dominant** |
| `deserialize_list()` helper | `galaxy.py`, `planet.py` | 9 call sites | Centralized resilient list deserialization (PROJ-204) |
| `require_keys()` / `validate_enum()` / `validate_positive()` | `validation_helpers.py` users: `galaxy.py`, `stars.py`, `storm.py`, etc. | ~25+ call sites | PROJ-171 standard for from_dict validation |
| `safe_from_dict()` wrapper | via `validation_helpers.py` | ~5 call sites | Wraps nested from_dict with PersistenceException |

### 3.3 Registry/DI Access

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| Constructor injection of `IRegistryProvider` | `component.py`, `ship.py`, `ship_loader.py`, `vehicle_design_service.py`, `registry_loader.py` | 179 references across 27 files | **Dominant** -- PROJ-211 standard |
| `get_default_registry_provider()` function | `app.py`, `setup_screen.py`, `workshop_data_loader.py` | ~10 call sites | Composition root usage |
| `TestRegistryProvider` for tests | Referenced in `registry.py` docstring | Test-only | Isolated test data |
| Direct `GameRegistries` dataclass | `harvesting_engine.py`, `registry_loader.py` | ~5 sites | Lower-level registry access |

### 3.4 Configuration Access

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| Import constants from `game.core.config` classes | `engine/*.py`, `simulation/*.py`, `ai/*.py` | 21 import sites | **Dominant** -- `DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleConfig` |
| Import from `game.core.constants` | All layers | 69 import sites | Enums: `GameState`, `LayerType`, `AttackType`, etc. |
| Import from domain-specific constants | `physics_constants.py`, `component_constants.py` | ~15 import sites | Module-level constants for formulas |

**Dominant Pattern:** Centralized `json_utils` for file I/O; `to_dict()`/`from_dict()` for serialization; constructor DI for registries
**Recommended Standard:** Migrate remaining direct `json.load()`/`json.dump()` to `json_utils`; expand `deserialize_list()` usage

---

## 4. API/Interface Patterns

### 4.1 Interface Definition Style

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `Protocol` classes (structural typing) | `core/protocols.py` (27 protocols), `simulation/interfaces/` (8), `ai/protocols.py` (3), `strategy/` (5) | 43 Protocol classes total | **Dominant** for cross-layer interfaces |
| `ABC` + `@abstractmethod` (nominal typing) | `strategy/interfaces/engines.py` (12 ABCs), `ai/interfaces/controllable.py`, `validation/base.py`, `battle_mode_handler.py`, `base_gallery.py` | 16 ABC classes, 70 abstract methods | **Dominant** for within-layer inheritance |
| Plain class inheritance (no formal interface) | Various | Scattered | Used for concrete specialization |

### 4.2 Method Naming for Accessors/Computations

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `get_*()` methods | All layers | 561 method definitions | **Dominant** (~88%) -- data retrieval |
| `calculate_*()` methods | `formulas/`, `services/`, `data/` | 51 method definitions (~8%) | Multi-step computations |
| `compute_*()` methods | `fleet_navigation_service.py` | 7 method definitions (~1%) | **Outlier** -- synonym for calculate_ |
| `find_*()` methods | `controller.py`, `pathfinding.py`, `targeting_system.py` | 17 method definitions (~3%) | Search/lookup operations |
| `@property` accessors | `ship.py`, `fleet.py`, `protocols.py`, `formation_editor.py`, `workshop_viewmodel.py` | 464 total | Significant complement to get_ methods |

### 4.3 Return Value Patterns

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `-> bool` return type | Validators, predicates, UI handlers | ~200 typed returns | Common for success/failure |
| `-> None` return type | Side-effect methods, engine ticks | ~300+ typed returns | State mutation methods |
| `-> Optional[T]` return type | Lookups, searches | 782 references to `Optional[` | **Dominant** for nullable returns |
| Named tuples | `production_engine.py` (`TickExpenditure`) | 1 class | **Rare** -- potential for wider use |
| `@dataclass` for return types | DTOs: `facade/dto/`, `battle_config.py`, `commands.py`, etc. | 113 dataclass usages | **Growing** -- structured data returns |
| `tuple` returns | `hex_math.py`, `config.py`, physics calculations | 72 typed tuple returns | Positional return values |
| Dict returns | `from_dict` patterns, stats calculations | Moderate | When flexible structure needed |

### 4.4 Optional Parameter Handling

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `Optional[T] = None` with explicit check | Throughout codebase | ~85% of optional params | **Dominant** |
| `**kwargs` | `app.py`, `singleton.py`, `profiling.py`, `setup_screen.py`, `density_map.py` | 20 uses across 12 files | Rare, mostly in decorators/metaclasses |
| Default value objects | `context: dict = None` -> `context or {}` | In `GameException.__init__` | Safe mutable default pattern |

### 4.5 Callback/Event Patterns

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `Callable` type hints for callbacks | `build_queue_controller.py`, `fleet_orders_window.py`, `formation/input_handler.py` | 56 references across 30 files | Used in UI panels |
| `EventBus` pattern | `builder/event_bus.py` | 1 class, ~40 references | Builder screen events |
| `EventLog` / `EventType` | `strategy/events/event_log.py`, `event_types.py` | ~30 references | Strategy turn events |
| Direct method calls | Most engine interactions | **Dominant** | Facade pattern over events |
| `on_*` callback methods | `behaviors.py`, `event_logging.py`, `controllable.py` | ~80+ method names | UI event handlers |

**Dominant Pattern:** `Protocol` for structural interfaces; `get_*()` for retrieval; `Optional[T]` for nullable returns; direct calls over events
**Recommended Standard:** Standardize `compute_*` -> `calculate_*` (7 methods to rename)

---

## 5. Naming Conventions

### 5.1 Class Naming

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| PascalCase | All classes | 100% | Universal compliance |
| `I` prefix for interfaces/protocols | `IRegistryProvider`, `ICombatShip`, `IFleet`, `IValidationRule`, `IControllable` | ~43 protocol/interface classes | **Dominant** for interfaces |
| No prefix for implementations | `Ship`, `Fleet`, `Galaxy`, `DamageCalculator` | All implementations | Standard |
| `*Manager` suffix | `ProjectileManager`, `ModifierManager`, `AbilityManager`, `RetreatManager` | ~15 classes | Service-like orchestrators |
| `*Engine` suffix | `BattleEngine`, `TurnEngine`, `ProductionEngine`, `HarvestingEngine` | ~12 classes | Strategy layer processing |
| `*Service` suffix | `BattleService`, `ModifierService`, `ResearchService`, `FleetNavigationService` | ~10 classes | Cross-cutting services |
| `*Calculator` suffix | `DamageCalculator`, `ShipStatsCalculator`, `DesignCostCalculator` | ~5 classes | Pure computation |
| `*Handler` suffix | `BattleModeHandler`, `CommandHandler`, `ClickModeDispatcher` | ~8 classes | Event/command processing |
| `*Validator` suffix | `ShipValidator`, `ColonizeValidator`, `SuperweaponValidator` | ~4 classes | Validation rules |
| `*Loader` suffix | `ShipLoader`, `DesignLoader`, `RegistryLoader` | ~5 classes | Data loading |

### 5.2 Method Naming

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `get_*` | Dominant retrieval pattern | 561 methods | Data access |
| `calculate_*` | Computation methods | 51 methods | Multi-step math |
| `_private_*` | Internal methods | ~1435 methods | Leading underscore convention |
| `process_*` | `fleet_order_processor.py`, `turn_engine.py` | ~20 methods | Batch operations |
| `apply_*` | `damage_calculator.py`, `modifier_service.py` | ~15 methods | State mutation |
| `validate_*` | Validators, helpers | ~30 methods | Input checking |
| `load_*` / `save_*` | I/O operations | ~25 methods each | Persistence |
| `create_*` | Factory methods | ~20 methods | Object construction |

### 5.3 File Naming vs. Class Naming

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `snake_case.py` containing `PascalCase` class | `damage_calculator.py` -> `DamageCalculator` | 100% | Universal standard |
| One primary class per file | Most files | ~90% | Clean separation |
| Multiple related classes per file | `component_constants.py` (3 classes), `abilities/base.py` (2 classes), `registry.py` (4 classes) | ~10% | Cohesive groupings |
| File name matches class name (snake -> Pascal) | `ship.py` -> `Ship`, `fleet.py` -> `Fleet` | ~85% | Strong correspondence |
| File name describes purpose, not class | `builder_utils.py`, `builder_selection.py` | ~15% | Utility/helper modules |

### 5.4 Constant Naming

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `UPPER_SNAKE_CASE` module-level | `physics_constants.py`, `constants.py` | ~95% | **Dominant** |
| Class-level constants in namespace classes | `DisplayConfig.DEFAULT_WIDTH`, `AIConfig.MIN_SPACING`, `CombatConstants.DEFAULT_MAX_TARGETS` | ~30 constants | Grouped by domain |
| Enum members | `GameState.MENU`, `LayerType.HULL`, `ErrorCode.VALIDATION_FAILED` | 15 Enum classes | Typed constant groups |

**Dominant Pattern:** Highly consistent PascalCase classes, `I*` prefix for interfaces, `get_*` for accessors
**Recommended Standard:** Rename `compute_*` to `calculate_*` for consistency (7 methods)

---

## 6. Structural Patterns

### 6.1 Import Organization

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| stdlib -> third-party -> local (PEP 8) | `damage_calculator.py`, `strategy_click_dispatcher.py`, most newer files | ~80% of files | **Dominant** |
| Mixed ordering (local between stdlib) | `harvesting_engine.py` (logger init between import groups) | ~10% of files | **Outlier** -- minor disorder |
| `from __future__ import annotations` | `strategy_click_dispatcher.py`, `input_mapper.py` | ~10 files | Forward ref pattern |
| `TYPE_CHECKING` guard imports | `damage_calculator.py`, `harvesting_engine.py`, `strategy_click_dispatcher.py` | ~40+ files | Circular import prevention |

### 6.2 __init__.py Patterns

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| Re-export with docstring and `from .module import *` | `core/__init__.py` (147 lines), `simulation/interfaces/__init__.py` (132), `simulation/components/abilities/__init__.py` (184) | ~35 packages | **Dominant** -- public API definition |
| Empty `__init__.py` (namespace only) | `game/__init__.py`, `simulation/components/__init__.py`, `strategy/data/__init__.py`, `ui/panels/__init__.py`, `ui/screens/__init__.py`, `ui/renderer/__init__.py` | 6 packages | Leaf-level data packages |
| `__all__` exports | `exceptions.py`, `error_codes.py`, `constants.py`, `singleton.py`, `validation_helpers.py`, + 45 other files | 50 files total | Explicit public API |
| Lazy imports (inside try/except) | `ai/__init__.py` (pygame import fallback) | 1 file | Platform-dependent |

### 6.3 Class Structure

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `__init__` first, then public, then private | Most classes | ~90% | **Dominant** |
| Module docstring -> imports -> logger -> class | `harvesting_engine.py`, `damage_calculator.py`, `strategy_click_dispatcher.py` | ~85% | **Dominant** module layout |
| `@dataclass` for data containers | `GameRegistries`, `BattleConfig`, DTOs, `Command*` types | 113 usages across 59 files | Growing pattern |
| `@staticmethod` for pure utility methods | `target_evaluator.py`, `modifier_manager.py`, `ship_stats_calculator.py` | 163 across 40 files | Where no instance state needed |
| `@classmethod` for alternative constructors | `from_dict`, factory methods, `Config.default_resolution()` | 82 across 37 files | Dominant for deserialization |

### 6.4 Singleton Pattern

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| `SingletonMeta` metaclass (centralized) | `singleton.py`, used by ~7 classes | **Dominant** for singletons | Thread-safe, test-resettable |
| Module-level singletons (implicit) | `_default_provider` in `registry.py` | ~2 cases | Global state pattern |

**Dominant Pattern:** PEP 8 import ordering; rich `__init__.py` re-exports; docstring-first module layout
**Recommended Standard:** Fix ~10% of files with mixed import ordering; ensure `TYPE_CHECKING` guards are used consistently

---

## 7. Configuration/Constants Patterns

### 7.1 Where Constants Live

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| Dedicated constants module | `core/constants.py`, `simulation/physics_constants.py`, `simulation/components/component_constants.py` | 3 centralized files | **Dominant** -- single source of truth |
| Namespace classes in `config.py` | `core/config.py`: `DisplayConfig`, `AIConfig`, `PhysicsConfig`, `BattleConfig` | 1 file, 4 classes | Grouped configuration |
| Domain-specific constant files | `core/paths.py`, `ui/colors.py`, `ui/config.py` | ~5 files | Layer-specific settings |
| Class-level constants | `LayerDefaults`, `CombatConstants`, `SimulationConstants` (in `constants.py`) | 3 classes in constants | Named constant groups |
| Module-level `UPPER_CASE` | `physics_constants.py` (`K_SPEED`, `K_THRUST`, `K_TURN`) | ~20 constants | Formula coefficients |

### 7.2 How Configuration Is Passed

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| Direct class attribute access | `DisplayConfig.DEFAULT_WIDTH`, `AIConfig.MIN_SPACING` | ~85% of config usage | **Dominant** -- simple and explicit |
| Constructor injection (DI) | `IRegistryProvider` injection in `ship.py`, `component.py`, etc. | 179 references | **Dominant** for registries |
| Import from specific module | `from game.core.config import BattleConfig` | 21 import sites for config | Standard |
| `@classmethod` factory with config | `DisplayConfig.default_resolution()` | ~5 methods | Typed config accessors |
| Global/singleton fallback | `get_default_registry_provider()` | ~10 call sites | Composition root only |

### 7.3 Magic Numbers

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| Named constants in dedicated files | `K_SPEED = 25`, `TICKS_PER_SECOND = 100`, `DEFAULT_MAP_SIZE = 100000` | ~95% of numeric constants | **Dominant** -- well-documented |
| Named constants in config classes | `AIConfig.MIN_SPACING = 150`, `PhysicsConfig.TICK_RATE = 0.01` | ~30 constants | Grouped by domain |
| Enum values | `GameState.MENU = 0`, `LayerType.HULL = 0` | 15 Enum classes | Type-safe constants |
| Inline magic numbers | Possibly in UI rendering code (padding, offsets) | Not systematically audited | Likely present in `ui/` layer |

### 7.4 Feature Flags

| Pattern Variant | Location Examples | Approx. Frequency | Notes |
|-----------------|-------------------|--------------------|-------|
| Module-level boolean | `ENABLE_SCREENSHOTS = True` (in `constants.py`) | 1 flag | Simple toggle |
| No feature flag system | N/A | N/A | No centralized feature flag mechanism |

**Dominant Pattern:** Centralized constants in dedicated files; namespace classes for grouped config; DI for runtime dependencies
**Recommended Standard:** Audit UI layer for inline magic numbers; consider consolidating all config namespace classes

---

## Cross-Cutting Observations

### Patterns with High Consistency (No Action Needed)
1. **Logger initialization** -- 97% use `logger = logging.getLogger(__name__)` at module level
2. **Custom exception hierarchy** -- Well-defined 9-class hierarchy, used correctly in ~90% of raise sites
3. **Protocol-based interfaces** -- 43 Protocol classes provide clean structural typing
4. **to_dict/from_dict serialization** -- Universal pattern for persistence
5. **JSON utils centralization** -- `load_json`/`save_json` used in 34 files (dominant)
6. **Singleton metaclass** -- Single reusable implementation

### Patterns with Cleanup Opportunity (Recommended Actions)
1. **11 bare ValueError/TypeError/RuntimeError raises** -- Migrate to custom exceptions (low effort)
2. **5 unannotated `except Exception` blocks** -- Add justification comments or narrow (low effort)
3. **5 direct json.load/dump bypasses** -- Migrate to `json_utils` (low effort)
4. **7 `compute_*` methods** -- Rename to `calculate_*` for consistency (low effort)
5. **15 print() calls** -- Replace with `logger.debug()` (low effort)
6. **4 %-style log format strings** -- Convert to f-strings (trivial)
7. **3 method-level logger initializations** -- Move to module level (trivial)
8. **~8 catch-and-convert without `from e`** -- Add exception chaining (low effort)
9. **Import ordering inconsistencies in ~10% of files** -- Standardize stdlib/third-party/local grouping (medium effort)
10. **UI magic numbers** -- Audit and extract to constants (medium effort, not fully cataloged)

### Pattern Maturity by Layer
| Layer | Consistency | Notes |
|-------|-------------|-------|
| `core/` | **Excellent** | Foundation layer, well-refactored (PROJ-45, PROJ-171, PROJ-211) |
| `simulation/` | **Very Good** | Clean interfaces, good exception usage |
| `strategy/` | **Good** | Some bare ValueError in command_handlers, some broad catches |
| `ai/` | **Good** | Small layer, consistent patterns |
| `ui/` | **Fair** | Largest layer; some print() usage, some unannotated broad catches |
| `research/` | **Good** | Small, follows established patterns |
| `engine/` | **Good** | Small, clean physics code |
