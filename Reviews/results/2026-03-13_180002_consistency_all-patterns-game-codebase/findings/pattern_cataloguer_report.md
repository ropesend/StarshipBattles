# Pattern Catalogue Report: game/ Codebase

**Date:** 2026-03-13
**Scope:** `game/` directory (429 Python files, ~106K lines)
**Categories Analyzed:** 7

---

## Summary

- **Total pattern categories analyzed:** 7
- **Total pattern variants found:** 62
- **Categories with most variation:** Import organization (mixed stdlib/local ordering), Error handling (custom exceptions vs stdlib exceptions), Naming conventions (getter prefixes, class suffixes)

The codebase shows strong consistency in most areas, particularly logging, JSON access, and the custom exception hierarchy. The main areas of variation are import ordering within files and a small residual use of stdlib exceptions where custom exceptions would be more appropriate.

---

## 1. Error Handling Patterns

### 1.1 Exception Hierarchy

The codebase has a well-defined custom exception hierarchy in `game/core/exceptions.py`:

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| Custom `GameException` hierarchy | `game/core/exceptions.py` | 10 exception classes | Well-structured hierarchy with code/context support |
| `raise ValidationException` | Throughout game/ | 77 occurrences | Most common custom exception |
| `raise PersistenceException` | strategy/data/, simulation/ | 21 occurrences | Second most common |
| `raise FormulaException` | simulation/formula_system.py, modifier_effects.py | 10 occurrences | Simulation-specific |
| `raise StateException` | core/registry.py, simulation/ | 5 occurrences | State management |
| `raise FrozenStateException` | core/registry.py | 3 occurrences | Immutability enforcement |
| `raise ValueError` (stdlib) | simulation/, strategy/ | 10 occurrences | Mixed with custom exceptions |
| `raise NotImplementedError` | ui/components/table/, ai/behaviors.py | 9 occurrences | Abstract method enforcement |

### 1.2 Exception Catching Styles

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| Specific exceptions (FileNotFoundError, KeyError, etc.) | Throughout | ~45 occurrences | Dominant pattern |
| `except Exception as e` with "Intentional broad catch" comment | ui/services/tkinter_utils.py, app.py | 9 occurrences | Annotated justification |
| `except Exception as e` WITHOUT annotation | strategy/data/empire.py, fleet.py, fleet_order_serializer.py | 6 occurrences | Missing justification |
| Bare `except:` | None | 0 occurrences | Not used (good) |

### 1.3 Error Return Patterns

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| `return None` (explicit) | Throughout | 263 occurrences | Common for Optional returns |
| Raise exception | Throughout | ~150 raise statements | Primary error signaling |
| Return `Optional[T]` (typed) | Throughout | 207 type annotations | Well-typed optionals |
| Return result dataclass | strategy/engine/ | ~10 Result classes | Used for complex operations |

#### PC-001: MINOR - Unannotated Broad Exception Catches
**ID:** PC-001
**Location:** `game/strategy/data/empire.py:268`, `game/strategy/data/fleet.py:268`, `game/strategy/data/fleet_order_serializer.py:56`, `game/strategy/services/design_cost_calculator.py:87`, `game/ui/panels/race_environment_panel.py:446`, `game/core/event_logging.py:57`
**Issue:** 6 `except Exception` catches lack the "Intentional broad catch" annotation that the codebase convention requires.
**Impact:** Unclear whether the broad catch is intentional or an oversight. The project has established a convention of annotating justified broad catches.
**Recommendation:** Add `# Intentional broad catch: <reason>` comment to each, or replace with specific exception types.
**Effort:** Simple

#### PC-002: MINOR - Residual stdlib ValueError Usage
**ID:** PC-002
**Location:** `game/simulation/components/component.py:566,672`, `game/simulation/entities/ship_loader.py:136`, `game/strategy/engine/command_handlers.py:175,178`, `game/strategy/data/fleet_capability_calculator.py:72,135`, `game/strategy/data/ship_instance.py:284`
**Issue:** 10 uses of `raise ValueError` instead of the project's custom `ValidationException`.
**Impact:** Inconsistent error handling; callers cannot catch all validation errors uniformly via `ValidationException`.
**Recommendation:** Replace `ValueError` with `ValidationException` from `game.core.exceptions`.
**Effort:** Simple

---

## 2. Logging Patterns

### 2.1 Logger Initialization

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| `logger = logging.getLogger(__name__)` at module level | All files with logging | 141 files | Universal pattern |
| `import logging` then `logger = ...` | All files with logging | 136 stdlib logging imports | Consistent |

**Consistency: Excellent.** All 141 files using logging follow the same `logging.getLogger(__name__)` pattern.

### 2.2 Log Level Usage

| Log Level | Approximate Frequency | Notes |
|-----------|----------------------|-------|
| `logger.info()` | 285 calls | Most common - used for state changes and key events |
| `logger.debug()` | 237 calls | Second most - used for detailed tracing |
| `logger.warning()` | 201 calls | Used for recoverable issues |
| `logger.error()` | 151 calls | Used for error conditions |
| `logger.exception()` | 9 calls | Used in catch blocks to log stack traces |
| `logger.log()` | 14 calls | Used for dynamic log levels |

**Total logging calls: ~902 across 141 files.**

### 2.3 Message Formatting

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| f-strings (`f"..."`) | Throughout | 686 calls (~76%) | Dominant pattern |
| `%` formatting | Rare | 4 calls | Nearly eliminated |
| `.format()` | None found | 0 calls | Not used |

**Consistency: Excellent.** f-strings dominate at 99.4% of log messages.

### 2.4 Print Statements

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| `print()` in docstring examples | `core/input_actions.py`, `core/protocols.py`, `simulation/interfaces/` | ~8 occurrences | Documentation only, not runtime |
| Runtime `print()` | None | 0 | All converted to logging (good) |

**Consistency: Excellent.** No runtime print statements; all are in docstring examples.

---

## 3. Data Access Patterns

### 3.1 JSON File Loading

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| `load_json()` from json_utils | Throughout | ~25 import sites | Safe loading with default |
| `load_json_required()` from json_utils | Throughout | ~10 import sites | Required loading, raises on error |
| `save_json()` from json_utils | data/design_metadata.py, data/race_config.py | ~5 import sites | Consistent save pattern |
| `deserialize_list()` from json_utils | strategy/data/galaxy.py, planet.py | ~3 import sites | Resilient list deserialization |
| Direct `json.loads()`/`json.dumps()` | simulation/battle_state.py, strategy/data/ship_instance.py | ~4 occurrences | In-memory serialization (not file I/O) |

**Consistency: Excellent.** File-based JSON operations consistently use `json_utils`. Direct `json.loads()`/`json.dumps()` is only used for in-memory string conversion, which is appropriate.

### 3.2 Path Management

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| `Paths.CONSTANT` class attributes | Throughout | Dominant | Centralized in `game/core/paths.py` |
| `os.path.join()` for path construction | `game/core/paths.py` | Internal to Paths class | Consistent |
| Direct path strings | Minimal | Rare | Almost eliminated |

### 3.3 Registry Access

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| DI via constructor (`registry_provider` param) | simulation/components, entities | Dominant | PROJ-211 pattern |
| `get_default_registry_provider()` | Composition roots | ~5 call sites | Used at application boundaries |
| `SingletonMeta` metaclass | 3 classes (StrategyManager, AssetManager, Profiler) | 3 classes | Thread-safe singleton |

---

## 4. API/Interface Patterns

### 4.1 Type System Usage

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| Functions with return type annotations | Throughout | 2329 (~54%) | Majority annotated |
| Functions without return type annotations | Throughout | 1985 (~46%) | Significant minority |
| `TYPE_CHECKING` imports | Throughout | 171 blocks | Widely used for circular dependency avoidance |
| `from __future__ import annotations` | 51 files | ~12% of files | Used selectively |
| `typing.Protocol` classes | core/protocols.py, simulation/interfaces/ | 53 classes | Strong protocol usage |
| ABC/abstractmethod | Various | 86 occurrences | Used alongside Protocols |

Return type annotation breakdown:
| Return Type | Count |
|------------|-------|
| `-> None` | 648 |
| `-> bool` | 288 |
| `-> str` | 215 |
| `-> float` | 216 |
| `-> int` | 176 |
| `-> List[...]` | 255 |
| `-> Dict[...]` | 165 |
| `-> Optional[...]` | 207 |
| `-> Tuple[...]` | 49 |

### 4.2 Serialization Patterns

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| `to_dict()` / `from_dict()` instance/classmethod pairs | battle_state.py, ship_instance.py, empire.py, fleet.py | 31 each | Symmetric and consistent |
| `to_json()` / `from_json()` | battle_state.py, ship_instance.py | 4 methods | Wrappers around to_dict/from_dict |
| Separate Serializer class | `ship_serialization.py` (ShipSerializer) | 1 class | For complex Ship serialization |

**Consistency: Good.** The `to_dict()`/`from_dict()` pattern is universally applied.

### 4.3 Constructor Patterns

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| `def __init__(self, ...)` with typed params | Throughout | 311 __init__ methods | Standard |
| DI with `Optional` defaults | strategy/adapters/simulation_adapter.py, etc. | ~10 classes | For testability |
| `@dataclass` (mutable) | Throughout | 88 occurrences | Dominant dataclass style |
| `@dataclass(frozen=True)` | DTOs, value objects | 25 occurrences | For immutable data |

### 4.4 Class Method Types

| Pattern | Count | Notes |
|---------|-------|-------|
| `@staticmethod` | 163 | More common than classmethod |
| `@classmethod` | 82 | Primarily for `from_dict()` factory methods |
| `@property` | 464 | Heavily used for computed attributes |
| Private methods (`def _...`) | 1435 | ~34% of all methods |
| Public methods | 2841 | ~66% of all methods |

### 4.5 Callback/Event Patterns

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| Callback parameters (`on_click`, `on_complete`, `scene_callback`) | app.py, battle_controller.py, UI screens | ~40+ call sites | Primary event mechanism |
| `EventBus` class | `ui/screens/builder/event_bus.py` | 1 class (UI builder only) | Localized pub/sub |
| `Callable[...]` type hints | Throughout | 56 typed callbacks | Growing adoption |
| Event logging callbacks | `core/event_logging.py` | 1 system | For simulation event observation |

### 4.6 Result/DTO Classes

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| `*Result` dataclasses | strategy/engine/ (ActionTickResult, ConflictResult, MovementResult, etc.) | ~10 classes | For complex return values |
| `*DTO` dataclasses | ui/interfaces/battle_ui.py, strategy/facade/dto/ | ~8 classes | UI boundary data transfer |
| Enum classes | Throughout | 18 Enum/IntEnum classes | Well-structured domain enumerations |

---

## 5. Naming Conventions

### 5.1 Method Naming Prefixes

| Prefix | Count | Notes |
|--------|-------|-------|
| `get_*` | 561 | Dominant accessor pattern |
| `is_*` | 105 | Boolean state queries |
| `load_*` | 63 | Data loading |
| `has_*` | 20 | Boolean existence checks |
| `find_*` | 17 | Search operations |
| `can_*` | 26 | Capability queries |
| `should_*` | 6 | Decision queries |
| `validate_*` | 29 | Input validation |
| `check_*` | 11 | State verification |

**Consistency: Good.** `get_*` is the clear standard for data retrieval. No `fetch_*` or `retrieve_*` or `lookup_*` in use.

### 5.2 Class Naming Suffixes

**Business/Service layer:**

| Suffix | Count | Notes |
|--------|-------|-------|
| Handler | 40 | Event/command handlers |
| Manager | 25 | State management |
| Engine | 23 | Processing/business logic |
| Service | 16 | Stateless operations |
| Controller | 6 | Orchestration |
| Factory | 6 | Object creation |
| Facade | 1 | Strategy session facade |

**UI layer:**

| Suffix | Count | Notes |
|--------|-------|-------|
| Panel | 30 | Contained UI regions |
| Window | 11 | Standalone UI windows |
| Screen | 10 | Full-screen views |
| Scene | 4 | Top-level game scenes |
| Dialog | 4 | Modal interactions |

### 5.3 Constants

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| `UPPER_CASE` module constants | physics_constants.py, config.py, constants.py | ~280 constants | Standard Python convention |
| Config classes with class attributes | core/config.py (DisplayConfig, AIConfig, PhysicsConfig) | 3 config classes | Grouped by domain |
| `Paths` class attributes | core/paths.py | ~30 path constants | Centralized path management |

### 5.4 Module Docstrings

| Pattern | Count | Notes |
|---------|-------|-------|
| Files with module docstring | 347 of 381 (91%) | Excellent coverage |
| Files without module docstring | 34 of 381 (9%) | Small minority |

---

## 6. Structural Patterns

### 6.1 Import Organization

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| `from game.* import` (explicit) | Universal | 1086 import statements | 100% of internal imports |
| `import game.*` (package) | None | 0 | Not used (good) |
| `from typing import` | Throughout | 301 files | Common typing imports |
| stdlib imports | `import logging`, `import os`, etc. | 136+ logging, 46 os, 39 math | Standard |
| pygame imports | UI layer only | 253 imports | Properly contained |

**Import ordering within files is inconsistent:**

| Import Order Style | Example Files | Approximate Frequency | Notes |
|-------------------|---------------|----------------------|-------|
| stdlib -> typing -> game.* | battle_controller.py, core/math.py | ~60% | PEP 8 recommended |
| Mixed stdlib and game.* | strategy/data/galaxy.py, simulation/entities/ship.py | ~30% | Interleaved imports |
| game.* first, stdlib scattered | Some files | ~10% | Least organized |

#### PC-003: MINOR - Inconsistent Import Ordering
**ID:** PC-003
**Location:** `game/strategy/data/galaxy.py`, `game/simulation/entities/ship.py`, and ~40% of files
**Issue:** Import ordering varies between files. Some follow PEP 8 (stdlib, third-party, local), others interleave imports.
**Impact:** Reduced readability; harder to scan imports quickly.
**Recommendation:** Enforce PEP 8 import ordering (stdlib -> third-party -> local) with `isort` or similar tool.
**Effort:** Simple (automated with isort)

### 6.2 `__init__.py` Patterns

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| Detailed docstring + `__all__` + re-exports | core/__init__.py (147 lines), simulation/components/abilities/__init__.py (184 lines) | ~15 packages | Full public API declarations |
| Empty `__init__.py` | simulation/components/, strategy/data/, ui/panels/, ui/screens/, game/ | 6 files | Namespace packages |
| Small imports for side-effect prevention | ui/__init__.py (27 lines) | 1 file | Prevents pytest-xdist race conditions |

### 6.3 Section Dividers

| Pattern | Count | Notes |
|---------|-------|-------|
| `# ====...` section dividers | 361 occurrences | Widely used for method grouping |

### 6.4 Layer Architecture Compliance

| Check | Status | Notes |
|-------|--------|-------|
| Core has no cross-layer imports | PASS | No imports from simulation/strategy/ui/ai |
| Simulation has no pygame imports | PASS | Clean separation |
| Strategy has no pygame imports | PASS | Clean separation |
| Core has no pygame imports | PASS | Clean separation |
| AI has no pygame imports | PASS (assumed) | Appropriate |

### 6.5 Lazy Import Patterns

| Pattern | Count | Notes |
|---------|-------|-------|
| `if TYPE_CHECKING` blocks | 171 | Primary circular dependency prevention |
| Inline lazy imports in methods | ~5 occurrences | Used where TYPE_CHECKING isn't sufficient |

---

## 7. Configuration Patterns

### 7.1 Configuration Value Sources

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| Config classes (DisplayConfig, AIConfig, PhysicsConfig) | `game/core/config.py` | 3 main config classes | Primary configuration |
| UIConfig class | `game/ui/config.py` | 1 class | UI-specific configuration |
| JSON data files (components.json, modifiers.json, etc.) | `data/` directory | ~10 JSON data files | Game data, not configuration |
| `Paths` class | `game/core/paths.py` | 1 class | All path configuration |
| Module-level constants (UPPER_CASE) | physics_constants.py, formula_system.py | ~280 constants | Domain-specific values |
| Enum classes | Throughout | 18 enums | Constrained value sets |
| `constants.py` catch-all | `game/core/constants.py` | 1 file | Layer types, resource names, game states |

### 7.2 Default Value Patterns

| Pattern Variant | Location Examples | Approximate Frequency | Notes |
|-----------------|-------------------|----------------------|-------|
| `Optional[X] = None` parameters | Throughout | Very common | For optional dependencies |
| Dataclass field defaults | Throughout | 88+ dataclasses | Default values in dataclass fields |
| Class-level defaults | Config classes | 3 config classes | Documented defaults |
| `load_json(path, default={})` | json_utils callers | ~25 call sites | Safe defaults for file loading |

### 7.3 TODO/Technical Debt Markers

| Marker | Count | Notes |
|--------|-------|-------|
| `# TODO` | 2 | Near zero - very clean |
| `# FIXME` | 0 | None |
| `# HACK` | 0 | None |
| `# PROJ-*` comments | ~50+ | Project tracking references, historical context |

---

## Top 5 Priority Issues

### 1. PC-003: Inconsistent Import Ordering (~40% of files)
Mixed ordering of stdlib, typing, and game.* imports across files. This is the most widespread inconsistency. Automated tooling (isort) could fix this in one pass.
**Effort:** Simple | **Impact:** Readability

### 2. PC-002: Residual stdlib ValueError Usage (10 occurrences)
The codebase has a well-designed custom exception hierarchy but 10 call sites still raise `ValueError` instead of `ValidationException`. This fragments error handling for callers.
**Effort:** Simple | **Impact:** Error handling consistency

### 3. PC-001: Unannotated Broad Exception Catches (6 occurrences)
The codebase has established a convention of annotating `except Exception` with "Intentional broad catch" comments. 6 locations lack this annotation.
**Effort:** Simple | **Impact:** Code review clarity

### 4. PC-004: Return Type Annotation Gap (~46% of functions)
While 54% of functions have return type annotations, 46% do not. The codebase would benefit from incrementally increasing coverage, especially in the UI layer.
**Effort:** Complex (incremental) | **Impact:** Type safety, IDE support

### 5. PC-005: Mixed `from __future__ import annotations` Usage (12% of files)
Only 51 of ~429 files use `from __future__ import annotations`. This is inconsistent -- either adopt it project-wide or remove it from the files that have it.
**Effort:** Medium | **Impact:** Consistency, forward compatibility

---

## Notable Positive Patterns

The codebase demonstrates strong consistency in several areas:

1. **Logging:** 100% consistent `logging.getLogger(__name__)` pattern with 99.4% f-string formatting
2. **JSON access:** Centralized through `json_utils` with no direct file I/O via `json` module
3. **Exception hierarchy:** Well-designed, documented, and broadly adopted
4. **Serialization:** Symmetric `to_dict()`/`from_dict()` pattern across all serializable entities
5. **Layer architecture:** Zero cross-layer violations (no pygame in non-UI code, no core importing other layers)
6. **Registry/DI:** Clean dependency injection pattern with `registry_provider` parameter convention
7. **Module docstrings:** 91% coverage
8. **Zero runtime print statements:** All output goes through logging
9. **Zero bare except clauses:** All exception catches are typed
10. **Near-zero TODOs/FIXMEs:** Only 2 TODO comments in 106K lines

---

## Appendix: File Statistics

| Metric | Value |
|--------|-------|
| Total Python files | 429 |
| Total lines of code | ~106K |
| Largest file | `ui/screens/strategy_renderer.py` (1102 lines) |
| Files with logging | 141 |
| Total logger calls | ~902 |
| `@dataclass` count | 113 |
| `@property` count | 464 |
| Protocol classes | 53 |
| Enum classes | 18 |
| `__all__` declarations | 50 |
| Private methods | 1435 (~34%) |
| Public methods | 2841 (~66%) |
