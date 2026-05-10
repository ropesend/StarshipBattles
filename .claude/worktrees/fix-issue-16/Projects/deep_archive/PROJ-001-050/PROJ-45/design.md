# PROJ-45: Error Handling and Exception Management Refactor

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Scope of Issues
The findings document (`findings_04_error_handling.md`) identifies **30+ distinct issues** across:
- **Critical:** 9 issues (ERR-001 through ERR-05, plus CORE-006, CQ-05)
- **Major:** 15 issues (ERR-005 through ERR-12, CORE-009, ERR-01-03 consistency)
- **Minor:** 6 issues (ERR-013 through ERR-015, ERR-01-03 consistency report)

### Current State Summary
- **156 total exception handlers** across 68 files
- **88 instances** (56%) use `except Exception as e:` (catch-all with binding)
- **11 instances** (7%) use bare `except Exception:` (no binding)
- **6 instances** (4%) use silent `except: pass` or `except Exception: pass`
- **No custom exception hierarchy exists** - all exceptions are built-in Python types

### Baseline Test Results
- **5199 tests passed**, 3 skipped, 1 import error (unrelated to this project)
- Test infrastructure has good coverage with `pytest.raises` patterns
- Core modules (`json_utils.py`, `validation.py`, `logger.py`) are well-tested

---

## Swarm Findings Summary

### Architecture Analysis

**Layer Structure (Dependency Flow):**
```
UI Layer (game/ui/) - Catches ALL exceptions, converts to user messages
    ↓
Strategy Layer (game/strategy/) - Returns tuples/DTOs, wraps simulation
    ↓
Simulation Layer (game/simulation/) - ValidationResult for validation, exceptions for state
    ↓
Core Layer (game/core/) - Raises specific exceptions, returns validated data
```

**Current Error Boundary Patterns:**
| Layer | Error Pattern | Key Files |
|-------|--------------|-----------|
| Core | Specific exceptions + ValidationResult DTO | `json_utils.py`, `validation.py` |
| Simulation | Broad catches, logs + continues | `component.py`, `formula_system.py` |
| Strategy | Returns `(success, message, data)` tuples | `save_game_service.py` |
| UI | Silent fallbacks to placeholders | `asset_manager.py`, `ship_theme_manager.py` |

**Architecture Issues:**
- AR-005: UI directly imports from Simulation layer (bypasses Strategy)
- AR-004: 20+ deferred imports indicating circular dependency risks
- No standardized error propagation between layers

### Key Patterns to Reuse

- **Gold Standard - JSON Utils**: `game/core/json_utils.py:49-60`
  - Specific exception types (FileNotFoundError, JSONDecodeError, IOError)
  - Appropriate logging levels (debug for expected, error for unexpected)
  - Context in messages, graceful fallbacks

- **ValidationResult Pattern**: `game/core/validation.py:17-136`
  - Cross-layer validation DTO
  - Supports error codes (unused currently), error accumulation, merging
  - Factory methods: `.create()`, `.add_error()`, `.merge()`

- **Service Result Tuple**: `game/strategy/systems/save_game_service.py:34-111`
  - Returns `(success: bool, message: str, data: Optional)`
  - Logs with traceback before returning
  - Specific error messages for different failure modes

- **Graceful Degradation**: `game/core/screenshot_manager.py:59-68`
  - Feature disables itself on initialization error
  - Prevents cascade failures, logs context

### Dependencies & Import Analysis

**Core Module Importers:**
- `logger.py`: 95 files import logging functions
- `validation.py`: 20 files import ValidationResult
- `json_utils.py`: 41 files import JSON utilities

**Safe Location for Custom Exceptions:**
- Create `game/core/exceptions.py` with **NO imports from game.***
- All game modules can then import from it safely
- Avoids circular dependencies

**Refactoring Order (Safest):**
1. Create `game/core/exceptions.py` (pure, no game imports)
2. Update `game/core/json_utils.py` (internal module, 41 dependents)
3. Update `game/strategy/systems/save_game_service.py` (service layer)
4. Update `game/simulation/components/component.py` (simulation layer)
5. Propagate to validation and UI layers

### Dependencies & Risks

1. **Silent Failures Becoming Visible** - HIGH RISK
   - AI targeting (`target_evaluator.py:34-35, 49-50`) uses silent fallbacks
   - If changed to throw, AI behavior changes significantly
   - **Mitigation:** Add logging first, keep fallbacks, create strict mode for testing

2. **Formula System Returns 0 on Error** - CRITICAL
   - `formula_system.py:92-94` returns 0 for ANY error
   - Components with broken formulas get 0 mass/hp silently
   - **Mitigation:** Preserve 0-return behavior but add detailed logging with context

3. **Save/Load Partial Corruption** - CRITICAL
   - Metadata can be saved even if turn state fails
   - **Mitigation:** Two-phase save (temp → validate → final)

4. **Backward Compatibility** - MEDIUM
   - `GameSession.from_dict()` exception types may change
   - UI code expects tuple returns, not exceptions
   - **Mitigation:** Maintain existing public APIs, only change internal handling

5. **Performance Impact** - MEDIUM
   - Adding logging to AI targeting could cause frame drops in dense combat
   - **Mitigation:** Sampling/throttling for high-frequency error logs

### Opportunities Discovered

1. **ValidationResult.error_code is unused** - Can standardize error codes for programmatic handling
2. **Centralized logger exists** - Can add exception-specific logging helpers
3. **Good test infrastructure** - 73 exception handling tests exist as patterns
4. **json_utils.py is excellent** - Use as template for other modules

---

## Recommended Exception Hierarchy

```python
# game/core/exceptions.py

class GameException(Exception):
    """Base class for all Starship Battles exceptions."""
    def __init__(self, message: str, code: str = None, context: dict = None):
        super().__init__(message)
        self.code = code
        self.context = context or {}

# State Management
class StateException(GameException): pass
class FrozenStateException(StateException): pass

# Validation
class ValidationException(GameException): pass

# Resources & I/O
class ResourceException(GameException): pass
class MissingResourceException(ResourceException): pass
class PersistenceException(GameException): pass

# Simulation
class SimulationException(GameException): pass
class ComponentException(SimulationException): pass
class FormulaException(SimulationException): pass
```

---

## Error Code Standardization

```python
# game/core/error_codes.py
from enum import Enum

class ErrorCode(Enum):
    # Validation (V-xxx)
    VALIDATION_FAILED = "V001"
    INVALID_COMPONENT = "V002"
    MISSING_REQUIRED = "V003"

    # State (S-xxx)
    STATE_FROZEN = "S001"
    NOT_INITIALIZED = "S002"

    # Resource (R-xxx)
    RESOURCE_NOT_FOUND = "R001"
    INVALID_FORMAT = "R002"

    # Persistence (P-xxx)
    SAVE_FAILED = "P001"
    LOAD_FAILED = "P002"
    CORRUPT_DATA = "P003"

    # Formula (F-xxx)
    SYNTAX_ERROR = "F001"
    UNDEFINED_VAR = "F002"
    EVAL_ERROR = "F003"
```

---

## Test Impact Summary

**Tests Requiring Updates:**
- `tests/unit/core/test_json_utils.py` - Add custom exception tests
- `tests/unit/core/test_validation.py` - Add ValidationException tests
- `tests/unit/core/test_registry.py` - Update RuntimeError → custom types
- `tests/unit/refactor/test_formula_error_handling.py` - Update caplog assertions

**New Tests Required:**
- `tests/unit/core/test_exceptions.py` - Test exception hierarchy
- `tests/unit/core/test_error_codes.py` - Test error code enum
- Integration tests for exception propagation through layers

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Key Decisions Made:
1. **Custom exceptions import nothing** - Avoids circular dependencies
2. **Preserve existing public APIs** - Only change internal error handling
3. **Add logging before changing behavior** - Visibility before breaking changes
4. **Phase-based rollout** - Core → Simulation → Strategy → UI
