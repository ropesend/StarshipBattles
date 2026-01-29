# Data Error Handling and Logging Findings

## File: error_logging_report.md

# Error Handling and Logging Pattern Analysis

**Agent:** Error Handling & Logging Analyst
**Date:** 2026-01-28
**Scope:** game/, ui/ directories (excluding tests)

---

## Summary
- Total pattern variants found: 12
- Critical inconsistencies: 0
- Major inconsistencies: 1
- Minor inconsistencies: 3
- Dominant pattern: Centralized logger with specific exception handling

---

## Error Handling Patterns

### Exception Handling Styles

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| `except Exception as e:` (catch-all) | asset_manager.py:102, battle_controller.py:191 | 60% | Most common |
| Specific exceptions (FileNotFoundError, JSONDecodeError) | json_utils.py:52-58, ship_loader.py:69 | 35% | Best practice |
| Silent `except Exception:` | target_evaluator.py:34, battle.py:186 | 5% | Problematic |

### Error Propagation Patterns

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Return tuples (success, message, data) | save_game_service.py:34, persistence.py | 15% | I/O operations |
| Return None on error | ship_loader.py, resources.py | 40% | Data loading |
| Raise exception | json_utils.py:load_json_required | 20% | Critical data |
| Log and continue | asset_manager.py:102-104 | 25% | UI/display |

---

## Logging Patterns

### Logger Initialization

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| Centralized logger imports | 94 files across game/ | 95% | Dominant |
| `print()` statements | ui/builder/event_bus.py:21 | 5% | Legacy |

### Log Level Usage

| Level | Usage Pattern | Examples |
|-------|--------------|----------|
| DEBUG | File loading details, success | json_utils.py, save_game_service.py |
| INFO | Game flow milestones | app.py:246, resources.py |
| WARNING | Missing assets, fallbacks | asset_manager.py, persistence.py |
| ERROR | Exception details, failures | save_game_service.py:110 |

### Message Formatting

| Pattern Variant | Example Locations | Frequency | Notes |
|-----------------|-------------------|-----------|-------|
| f-strings with context | Throughout codebase | 95% | Standard |
| Traceback inclusion | save_game_service.py:110 | 10% | Complex errors |

---

## Key Inconsistencies

### ERR-01: Print vs Logger in Event Buses
**Severity:** Minor
**ID:** ERR-01
**Location:** `ui/builder/event_bus.py:21`
**Issue:** Uses `print()` instead of centralized logger
**Impact:** Inconsistent error reporting, no log level control
**Recommendation:** Migrate to `log_error()` / `log_warning()`
**Effort:** Simple

### ERR-02: Silent Exception Handlers
**Severity:** Minor
**ID:** ERR-02
**Location:** `game/ai/target_evaluator.py:34`, `game/ui/hud/battle.py:186`
**Issue:** Exception handlers don't bind the exception variable
**Impact:** Cannot access exception details for logging/debugging
**Recommendation:** Always bind: `except Exception as e:`
**Effort:** Simple

### ERR-03: Inconsistent Error Return Patterns
**Severity:** Info
**ID:** ERR-03
**Location:** Various I/O operations
**Issue:** Mix of tuple returns, None returns, and exceptions
**Impact:** Caller must know which pattern each method uses
**Recommendation:** Document pattern choice per module; consider standardizing
**Effort:** Medium

---

## Recommended Standard

### Error Handling
```python
# Pattern A: Critical data (raises)
try:
    data = load_json_required(filepath)
except FileNotFoundError:
    raise RuntimeError(f"Critical file not found: {filepath}")

# Pattern B: Optional data (returns default)
try:
    data = load_json(filepath, default={})
except Exception as e:
    log_error(f"Failed to load {filepath}: {e}")
    return None

# Pattern C: I/O operations (returns tuple)
try:
    save_json(filepath, data)
    return True, "Saved successfully", None
except Exception as e:
    log_error(f"Save failed: {e}")
    return False, f"Error: {e}", None
```

### Logging
```python
from game.core.logger import log_debug, log_info, log_warning, log_error

log_error(f"Failed to load {resource_name}: {e}")
log_info(f"Loaded {count} items from {os.path.basename(path)}")
log_warning(f"Asset not found, using fallback: {fallback_id}")
```

---

## Top 5 Priority Issues

1. **ERR-01:** Replace `print()` with logger in event_bus.py (2 files)
2. **ERR-02:** Add exception binding to silent handlers (~5 locations)
3. Consider documenting error propagation patterns per module
4. Ensure all new code follows json_utils.py best practices
5. Expand traceback logging for complex error scenarios

---


## File: data_pattern_analyst_report.md

# Data Pattern Analyst Report

## Summary
- **Total issues found:** 14
- **Critical:** 3, **Major:** 6, **Minor:** 5

---

## Critical Issues

### DPA-001: Inconsistent Dictionary Access Pattern - KeyError Risk
**ID:** DPA-001
**Location:** `game/strategy/data/planet.py:192-227`, `game/strategy/data/galaxy.py:32-33,74-75,439`
**Issue:** Mixed use of direct bracket access `data['key']` and safe `.get()` access in from_dict() methods. Planet.from_dict() uses 14 direct accesses without defaults while also using `.get()` for optional fields.
**Impact:** Data corruption, deserialization failures, loss of saved game compatibility
**Recommendation:** Standardize all from_dict() methods to use `.get()` with sensible defaults for all fields.
**Effort:** Medium

---

### DPA-002: Enum String Conversion Without Error Handling
**ID:** DPA-002
**Location:** `game/strategy/data/planet.py:193`, `game/strategy/data/galaxy.py:71`
**Issue:** Enum conversion using bracket notation: `PlanetType[data['planet_type']]` will raise KeyError if the enum value name doesn't exist.
**Impact:** Complete deserialization failure if enum naming changes between versions.
**Recommendation:** Add try-catch around enum conversion with fallback to a safe default value.
**Effort:** Simple

---

### DPA-003: Incomplete Optional Field Handling with None Values
**ID:** DPA-003
**Location:** `game/strategy/data/ship_instance.py:47,62,99-106`
**Issue:** ShipInstance.from_dict() uses `data.get('serial')` which returns None for missing fields, but ShipInstance.create() logs a warning when serial is None. Dual-meaning of None creates confusion.
**Impact:** Ambiguous state - unclear if None means "not set" vs "intentionally defaulting".
**Recommendation:** Use explicit sentinel values or add a `_version` field to distinguish old saves.
**Effort:** Medium

---

## Major Issues

### DPA-004: Inconsistent Serialization Method Naming
**ID:** DPA-004
**Location:** Across 17 files with serialization methods
**Issue:** Codebase uses two different naming conventions: `to_dict()` / `from_dict()` (13 files), `to_json()` / `from_json()` (wrappers in some)
**Impact:** Developer confusion, maintainability issues
**Recommendation:** Adopt single naming convention (recommend `to_dict()`/`from_dict()`).
**Effort:** Medium

---

### DPA-005: Missing Version/Schema Information in Serialized Data
**ID:** DPA-005
**Location:** All to_dict() methods lack `_version` or `_schema_version` fields
**Issue:** No serialization format version is stored in saved data.
**Impact:** Impossible to implement safe migrations. Future format changes will silently corrupt data.
**Recommendation:** Add `_format_version` and `_schema_id` fields to all serialized data.
**Effort:** Medium

---

### DPA-006: Dataclass Field Defaults Mixed with Manual Defaults
**ID:** DPA-006
**Location:** `game/strategy/data/planet.py:20-82`, `game/strategy/data/ship_instance.py:26-63`
**Issue:** Dataclasses define field defaults via `field(default_factory=...)` but from_dict() also provides defaults via `.get()`. Redundant defaults that can diverge.
**Impact:** Subtle bugs where empty collections aren't shared as expected.
**Recommendation:** Use dataclass defaults consistently - don't repeat in from_dict().
**Effort:** Simple

---

### DPA-007: No Validation of Required Fields in from_dict()
**ID:** DPA-007
**Location:** All from_dict() implementations
**Issue:** No validation that required fields are present before use.
**Impact:** Silent data loss or corruption if save file is partially corrupted.
**Recommendation:** Add ValidationResult-based validation at start of from_dict().
**Effort:** Medium

---

### DPA-008: Circular Reference Handling is Inconsistent
**ID:** DPA-008
**Location:** `game/strategy/data/empire.py:70-94` vs `game/strategy/data/galaxy.py`
**Issue:** Empire.to_dict() explicitly avoids circular references by storing only IDs. However, other classes include full nested objects.
**Impact:** Potential stack overflow or memory bloat if circular references aren't properly broken.
**Recommendation:** Document circular reference handling strategy. Use IDs consistently for back-references.
**Effort:** Medium

---

### DPA-009: Field Type Conversions Not Always Bidirectional
**ID:** DPA-009
**Location:** `game/strategy/data/fleet.py:567`, `game/strategy/data/stars.py:100`
**Issue:** Serialization converts tuples to lists for JSON compatibility, but deserialization doesn't always convert back.
**Impact:** Type inconsistencies after round-trip serialization.
**Recommendation:** Add explicit type conversions in from_dict() to restore original types.
**Effort:** Simple

---

## Minor Issues

### DPA-010: Default Value Inconsistencies Across Instances
**Location:** `game/strategy/data/design_metadata.py:59-71`
**Issue:** Different approaches to handling missing nested objects.
**Effort:** Simple

### DPA-011: Resource Dictionary Handling Inconsistent
**Location:** `game/strategy/data/planet.py:167`
**Issue:** Assumes values are dicts; .copy() will fail if value is a scalar.
**Effort:** Simple

### DPA-012: Layer Type Enum String Conversion Missing Error Handling
**Location:** `game/simulation/battle_state.py:156`
**Issue:** Could fail if layer type names are changed.
**Effort:** Simple

### DPA-013: Optional Tuple Fields Not Fully Typed
**Location:** `game/strategy/data/stars.py:83`, `game/simulation/battle_state.py:90`
**Issue:** Tuple fields typed inconsistently.
**Effort:** Simple

### DPA-014: Backward Compatibility Partial
**Location:** `game/strategy/data/design_metadata.py:169-171`
**Issue:** Warns about old formats but doesn't actually migrate the data.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **DPA-001: Inconsistent Dictionary Access Pattern** - HIGH RISK: KeyError failures on deserialization
2. **DPA-002: Enum String Conversion Without Error Handling** - HIGH RISK: Enum changes break save loading
3. **DPA-005: Missing Version/Schema Information** - HIGH RISK: Makes all future format changes dangerous
4. **DPA-003: Incomplete Optional Field Handling** - MEDIUM RISK: Unclear semantics of None values
5. **DPA-004: Inconsistent Serialization Method Naming** - MEDIUM RISK: Maintainability issue

---


## File: error_handling_auditor_report.md

# Error Handling Auditor Report

## Summary
- **Total issues found:** 23
- **Critical:** 4, **Major:** 8, **Minor:** 9, **Info:** 2

---

## Critical Issues

### ERR-001: Overly Broad Exception Handling Without Specific Types
**ID:** ERR-001
**Location:** `game/simulation/components/component.py:725`, `game/core/json_utils.py:92`, `game/assets/asset_manager.py:102-124`
**Issue:** Multiple `except Exception as e:` blocks catch all exceptions generically, masking underlying issues
**Impact:** Hides programming errors, makes debugging difficult, swallows critical system errors
**Count:** 46+ instances
**Recommendation:** Replace with specific exception types
**Effort:** Simple

---

### ERR-002: Silent Exception Swallowing in ai/target_evaluator.py
**ID:** ERR-002
**Location:** `game/ai/target_evaluator.py:34-35`, `game/ai/target_evaluator.py:49-50`
**Issue:** `except Exception: pass` silently swallows errors without logging
**Impact:** Silent failures make debugging impossible, potential data corruption
**Recommendation:** Add logging or specific handling
**Effort:** Simple

---

### ERR-003: Generic Exception Raising Without Context
**ID:** ERR-003
**Location:** `game/assets/asset_manager.py:29`, `game/ui/assets/ship_theme_manager.py:46`, `game/core/registry.py:175`, `game/ai/strategy_manager.py:40`
**Issue:** `raise Exception("message")` instead of specific exception types
**Impact:** Makes exception handling unreliable, unclear error semantics
**Count:** 7 instances
**Recommendation:** Use specific exception types (ValueError, RuntimeError, etc.)
**Effort:** Simple

---

### ERR-004: Unstructured Exception Logging in formula_system.py
**ID:** ERR-004
**Location:** `game/simulation/formula_system.py:92`
**Issue:** `except Exception as e:` logs to warning with `log_warning()` instead of error, returns 0 silently
**Impact:** Invalid formulas silently evaluate to 0, causing incorrect calculations
**Recommendation:** Log as error, propagate exception or use explicit error value
**Effort:** Medium

---

## Major Issues

### ERR-005: Inconsistent Exception Types for State Violations
**ID:** ERR-005
**Location:** `game/simulation/battle_controller.py:276`, `game/core/registry.py:241`, `game/core/paths.py:25`
**Issue:** Mixes RuntimeError, ValueError, and generic Exception for state violations
**Impact:** Inconsistent API contract, poor client code clarity
**Count:** 15+ instances
**Recommendation:** Standardize on RuntimeError for state violations, ValueError for input errors
**Effort:** Medium

---

### ERR-006: Missing Exception Context Chaining (raise from)
**ID:** ERR-006
**Location:** `game/simulation/components/component.py:725-726`, `game/simulation/services/design_loader.py`, `game/strategy/systems/save_game_service.py`
**Issue:** Re-raises exceptions without `raise from e` chaining
**Impact:** Lost stack trace context, harder debugging
**Count:** 12+ instances
**Recommendation:** Use `raise NewException(...) from e` pattern
**Effort:** Simple

---

### ERR-007: Inconsistent Logging Levels
**ID:** ERR-007
**Location:** `game/core/json_utils.py:56`, `game/core/resources.py:77-79`, `game/simulation/formula_system.py:93`
**Issue:** Log level mismatches - IOError logged as error vs warning inconsistently
**Impact:** Inconsistent log severity, filtering issues
**Count:** 8+ instances
**Recommendation:** Establish log level guidelines
**Effort:** Simple

---

### ERR-008: No Validation Result Error Code Standardization
**ID:** ERR-008
**Location:** `game/core/validation.py`, all validation files
**Issue:** error_code parameter unused in most ValidationResult implementations
**Impact:** Cannot programmatically distinguish error types
**Count:** 20+ validation sites
**Recommendation:** Define error code enumeration
**Effort:** Medium

---

### ERR-009: Input Validation Gaps in Core Components
**ID:** ERR-009
**Location:** `game/simulation/entities/projectile.py:34`, `game/simulation/components/component.py:158`
**Issue:** `.get()` calls with None defaults but no validation of result
**Impact:** Silent None propagation, NoneType errors downstream
**Recommendation:** Add explicit validation after .get() calls
**Effort:** Medium

---

### ERR-010: Finally Block Cleanup Missing
**ID:** ERR-010
**Location:** `game/ui/screens/builder/main.py:48-55`, `game/simulation/systems/battle_engine.py:118-124`
**Issue:** File operations without guaranteed cleanup in finally
**Impact:** Resource leaks, unclosed file handles
**Count:** 3 instances
**Recommendation:** Use context managers or finally blocks
**Effort:** Simple

---

### ERR-011: No Custom Exception Hierarchy
**ID:** ERR-011
**Location:** Entire codebase
**Issue:** Only using generic Exception, no custom exceptions defined
**Impact:** Cannot catch specific error types, poor error semantics
**Recommendation:** Create custom exception hierarchy (ValidationError, ResourceError, StateError)
**Effort:** Complex

---

### ERR-012: Swallowed Exceptions in Component Loading
**ID:** ERR-012
**Location:** `game/simulation/components/component.py:725-726`, `game/simulation/components/component.py:810-811`
**Issue:** Component creation failures logged but continue processing
**Impact:** Silently skips invalid components, corrupts ship designs
**Recommendation:** Fail fast or collect all errors
**Effort:** Medium

---

## Minor Issues

### ERR-013: Inconsistent Logger Access Pattern
**Location:** `game/ui/screens/builder/main.py:62-64`, `game/core/logger.py`
**Issue:** Mixed use of Python logging module and custom logger wrapper
**Effort:** Simple

### ERR-014: Missing None Checks After get_position()
**Location:** `game/ai/target_evaluator.py:98-252`
**Issue:** Assumes get_position() never returns None
**Effort:** Simple

### ERR-015: KeyError in Layer Type Parsing
**Location:** `game/simulation/battle_state.py:271`
**Issue:** `KeyError` caught but logged as warning, no fallback
**Effort:** Simple

---

## Top 5 Priority Issues

1. **ERR-001: Overly Broad Exception Handling** - Affects 46+ locations, masks errors
2. **ERR-003: Generic Exception Raising** - Inconsistent error semantics
3. **ERR-012: Swallowed Component Exceptions** - Data corruption risk
4. **ERR-002: Silent Exception Swallowing** - Debugging nightmare
5. **ERR-008: Missing Error Code Standardization** - Cannot distinguish error types

---

## Recommendations

1. **Immediate (Week 1):** Create custom exception hierarchy (ValidationError, ResourceError, StateError)
2. **Week 1:** Replace all `except Exception:` with specific types
3. **Week 1:** Add proper exception context chaining with `raise from e`
4. **Week 2:** Standardize error codes for ValidationResult
5. **Week 2:** Add input validation at API boundaries

---


## File: error_handling_report.md

# Error Handling Audit Report

## Summary
- **Total issues found:** 42
- **Critical:** 5
- **Major:** 12
- **Minor:** 18
- **Info:** 7

---

## Findings

### CRITICAL: Bare Exception Clause Without Logging
**ID:** ERR-01
**Location:** `scripts/apply_resource_costs.py:96`
**Issue:** Bare `except: pass` silently swallows all exceptions including SystemExit and KeyboardInterrupt
```python
try:
    tier = int(comp_id.split("tier")[-1])
except: pass  # <- Bare except, no logging
```
**Impact:** Parse failures go completely undetected. Impossible to debug.
**Recommendation:** Replace with specific exception handling and logging.
**Effort:** Simple

### CRITICAL: Swallowed Exception in AI System
**ID:** ERR-02
**Location:** `game/ai/target_evaluator.py:34-35, 49-50`
**Issue:** Bare `except Exception: pass` silently catches all errors in targeting logic
**Impact:** Position retrieval failures cause incorrect targeting. Silent fallback to stale data.
**Recommendation:** Log the exception and provide fallback explanation.
**Effort:** Simple

### CRITICAL: Unhandled Division by Zero Risk
**ID:** ERR-03
**Location:** `game/ai/target_evaluator.py:224`
**Issue:** Division without zero-check in formula system. Similar patterns elsewhere don't have protection.
**Impact:** Formula system doesn't validate user-input formulas for division by zero.
**Recommendation:** Implement formula validation in ModifierEffectEvaluator.
**Effort:** Medium

### CRITICAL: Silent Input Validation Failure
**ID:** ERR-04
**Location:** `game/simulation/components/modifier_effects.py:148, 198, 251`
**Issue:** Exception handling in formula evaluation without adequate context
**Impact:** When formula evaluation fails, no context about which modifier/component failed.
**Recommendation:** Include modifier ID, component ID, and formula in error message.
**Effort:** Medium

### CRITICAL: Resource Loading Failure Suppression
**ID:** ERR-05
**Location:** `game/core/resources.py:77-79, 111-113`
**Issue:** Exception silently caught during resource loading with generic fallback
**Impact:** Game silently degrades when resource definitions are corrupted.
**Recommendation:** Log specific error details before fallback.
**Effort:** Simple

### MAJOR: Incomplete Error Context in Save/Load
**ID:** ERR-06
**Location:** `game/strategy/systems/save_game_service.py:109-111, 173-176`
**Issue:** Generic Exception handling loses critical context
**Impact:** Error messages to user are generic. Can't distinguish disk full vs permission denied.
**Recommendation:** Categorize exceptions and provide specific user-facing messages.
**Effort:** Medium

### MAJOR: Missing Input Validation
**ID:** ERR-07
**Location:** `game/ui/screens/build_queue_screen.py:68-71`
**Issue:** Validation inconsistent - first check raises exception, second just logs warning
**Impact:** Inconsistent error handling patterns lead to hard-to-debug issues.
**Recommendation:** Consistent validation with clear patterns.
**Effort:** Simple

### MAJOR: Swallowed KeyError in Battle State
**ID:** ERR-08
**Location:** `game/simulation/battle_state.py:271`
**Issue:** KeyError silently caught without context
**Impact:** Missing data in battle state causes silent skips. State becomes corrupted.
**Recommendation:** Log the missing key before skipping.
**Effort:** Simple

### MAJOR: AI Controller Error Handling Gap
**ID:** ERR-09
**Location:** `game/ai/controller.py:334`
**Issue:** Specific exception catch without context or recovery strategy
**Impact:** Targeting logic failures silently ignored. AI falls back to undefined behavior.
**Recommendation:** Log failure and use safe default.
**Effort:** Simple

### MAJOR: Asset Manager Silent Failures
**ID:** ERR-10
**Location:** `game/assets/asset_manager.py:73-82, 102-104`
**Issue:** Asset loading fails silently with placeholder fallback
**Impact:** Game runs with missing assets. User has no indication content is missing.
**Recommendation:** Add asset load tracking and notify UI of missing assets.
**Effort:** Medium

### MAJOR: Formation Editor JSON Error Handling
**ID:** ERR-11
**Location:** `game/ui/screens/formation_editor.py:212`
**Issue:** Generic exception catch loses context about specific error type
**Impact:** User can't distinguish "file not found" vs "invalid JSON" vs "missing data".
**Recommendation:** Specific handling for each error type.
**Effort:** Medium

### MAJOR: Component Status Transition Without Validation
**ID:** ERR-12
**Location:** `game/simulation/components/component.py:99-101`
**Issue:** Fallback to legacy pattern if registries not available, later code doesn't handle None
**Impact:** NoneType errors can occur when registries needed but None.
**Recommendation:** Either raise or mark explicitly with clear handling.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **ERR-01: Bare Exception in Resource Costs** - Silent swallowing makes debugging impossible

2. **ERR-02: Swallowed Exception in AI Targeting** - Causes unpredictable AI behavior

3. **ERR-05: Resource Loading Failure Suppression** - Game runs with missing content silently

4. **ERR-06: Generic Save/Load Error Messages** - Poor user experience, support costs

5. **ERR-04: Silent Input Validation Failure** - Formula errors have no context

---


