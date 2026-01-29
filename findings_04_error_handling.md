# Error Handling & Exception Management

**Theme:** Exception handling patterns, silent failures, logging inconsistencies, error propagation, and validation gaps.

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

### ERR-01: Bare Exception Clause Without Logging
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

---

### ERR-02: Swallowed Exception in AI System
**ID:** ERR-02
**Location:** `game/ai/target_evaluator.py:34-35, 49-50`
**Issue:** Bare `except Exception: pass` silently catches all errors in targeting logic
**Impact:** Position retrieval failures cause incorrect targeting. Silent fallback to stale data.
**Recommendation:** Log the exception and provide fallback explanation.
**Effort:** Simple

---

### ERR-03: Unhandled Division by Zero Risk
**ID:** ERR-03
**Location:** `game/ai/target_evaluator.py:224`
**Issue:** Division without zero-check in formula system. Similar patterns elsewhere don't have protection.
**Impact:** Formula system doesn't validate user-input formulas for division by zero.
**Recommendation:** Implement formula validation in ModifierEffectEvaluator.
**Effort:** Medium

---

### ERR-04: Silent Input Validation Failure
**ID:** ERR-04
**Location:** `game/simulation/components/modifier_effects.py:148, 198, 251`
**Issue:** Exception handling in formula evaluation without adequate context
**Impact:** When formula evaluation fails, no context about which modifier/component failed.
**Recommendation:** Include modifier ID, component ID, and formula in error message.
**Effort:** Medium

---

### ERR-05: Resource Loading Failure Suppression
**ID:** ERR-05
**Location:** `game/core/resources.py:77-79, 111-113`
**Issue:** Exception silently caught during resource loading with generic fallback
**Impact:** Game silently degrades when resource definitions are corrupted.
**Recommendation:** Log specific error details before fallback.
**Effort:** Simple

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

### ERR-06: Incomplete Error Context in Save/Load
**ID:** ERR-06
**Location:** `game/strategy/systems/save_game_service.py:109-111, 173-176`
**Issue:** Generic Exception handling loses critical context
**Impact:** Error messages to user are generic. Can't distinguish disk full vs permission denied.
**Recommendation:** Categorize exceptions and provide specific user-facing messages.
**Effort:** Medium

---

### ERR-07: Missing Input Validation
**ID:** ERR-07
**Location:** `game/ui/screens/build_queue_screen.py:68-71`
**Issue:** Validation inconsistent - first check raises exception, second just logs warning
**Impact:** Inconsistent error handling patterns lead to hard-to-debug issues.
**Recommendation:** Consistent validation with clear patterns.
**Effort:** Simple

---

### ERR-08: Swallowed KeyError in Battle State
**ID:** ERR-08
**Location:** `game/simulation/battle_state.py:271`
**Issue:** KeyError silently caught without context
**Impact:** Missing data in battle state causes silent skips. State becomes corrupted.
**Recommendation:** Log the missing key before skipping.
**Effort:** Simple

---

### ERR-09: AI Controller Error Handling Gap
**ID:** ERR-09
**Location:** `game/ai/controller.py:334`
**Issue:** Specific exception catch without context or recovery strategy
**Impact:** Targeting logic failures silently ignored. AI falls back to undefined behavior.
**Recommendation:** Log failure and use safe default.
**Effort:** Simple

---

### ERR-10: Asset Manager Silent Failures
**ID:** ERR-10
**Location:** `game/assets/asset_manager.py:73-82, 102-104`
**Issue:** Asset loading fails silently with placeholder fallback
**Impact:** Game runs with missing assets. User has no indication content is missing.
**Recommendation:** Add asset load tracking and notify UI of missing assets.
**Effort:** Medium

---

### ERR-11: Formation Editor JSON Error Handling
**ID:** ERR-11
**Location:** `game/ui/screens/formation_editor.py:212`
**Issue:** Generic exception catch loses context about specific error type
**Impact:** User can't distinguish "file not found" vs "invalid JSON" vs "missing data".
**Recommendation:** Specific handling for each error type.
**Effort:** Medium

---

### ERR-12: Component Status Transition Without Validation
**ID:** ERR-12
**Location:** `game/simulation/components/component.py:99-101`
**Issue:** Fallback to legacy pattern if registries not available, later code doesn't handle None
**Impact:** NoneType errors can occur when registries needed but None.
**Recommendation:** Either raise or mark explicitly with clear handling.
**Effort:** Medium

---

### CORE-006: Broad Exception Catching Without Context
**ID:** CORE-006
**Location:** `game/core/resources.py:77-79, 111-113` and `game/core/screenshot_manager.py:115-116, 216-217`
**Issue:** Bare `except Exception:` blocks suppress all errors without logging specifics. In resources.py line 77, silently falls back to defaults without logging context.
**Impact:** Makes debugging harder. Hides genuine bugs under fallback behavior.
**Recommendation:** Log exception type/message in except blocks: `except Exception as e: log_warning(f"Failed to load resources: {type(e).__name__}: {e}")`. Distinguish recoverable vs critical errors.
**Effort:** Simple

---

### CQ-05: Missing Error Handling - Resource Consumption
**ID:** CQ-05
**Location:** `game/simulation/components/component.py:335-357`
**Issue:** `try_activate()`, `consume_activation()` methods silently return False/None without logging.
**Impact:** Silent failures in activation logic. Debugging UI issues becomes difficult.
**Recommendation:** Add logging at WARN level for failures. Return typed Result objects.
**Effort:** Simple

---

## Minor Issues

### ERR-013: Inconsistent Logger Access Pattern
**ID:** ERR-013
**Location:** `game/ui/screens/builder/main.py:62-64`, `game/core/logger.py`
**Issue:** Mixed use of Python logging module and custom logger wrapper
**Effort:** Simple

---

### ERR-014: Missing None Checks After get_position()
**ID:** ERR-014
**Location:** `game/ai/target_evaluator.py:98-252`
**Issue:** Assumes get_position() never returns None
**Effort:** Simple

---

### ERR-015: KeyError in Layer Type Parsing
**ID:** ERR-015
**Location:** `game/simulation/battle_state.py:271`
**Issue:** `KeyError` caught but logged as warning, no fallback
**Effort:** Simple

---

### ERR-01 (Consistency Report): Print vs Logger in Event Buses
**ID:** ERR-01 (Consistency)
**Location:** `ui/builder/event_bus.py:21`
**Issue:** Uses `print()` instead of centralized logger
**Impact:** Inconsistent error reporting, no log level control
**Recommendation:** Migrate to `log_error()` / `log_warning()`
**Effort:** Simple

---

### ERR-02 (Consistency Report): Silent Exception Handlers
**ID:** ERR-02 (Consistency)
**Location:** `game/ai/target_evaluator.py:34`, `game/ui/hud/battle.py:186`
**Issue:** Exception handlers don't bind the exception variable
**Impact:** Cannot access exception details for logging/debugging
**Recommendation:** Always bind: `except Exception as e:`
**Effort:** Simple

---

### ERR-03 (Consistency Report): Inconsistent Error Return Patterns
**ID:** ERR-03 (Consistency)
**Location:** Various I/O operations
**Issue:** Mix of tuple returns, None returns, and exceptions
**Impact:** Caller must know which pattern each method uses
**Recommendation:** Document pattern choice per module; consider standardizing
**Effort:** Medium

---

### CORE-009: Inconsistent Error Messages and Formatting
**ID:** CORE-009
**Location:** `game/core/registry.py:269, 296` and `game/core/screenshot_manager.py:28`
**Issue:** Error messages vary in capitalization and punctuation. Inconsistent tone.
**Impact:** Professional polish; makes code feel less polished.
**Recommendation:** Standardize error message format across modules.
**Effort:** Simple

---

## Logging Pattern Analysis

### Current State

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

### Log Level Usage

| Level | Usage Pattern | Examples |
|-------|--------------|----------|
| DEBUG | File loading details, success | json_utils.py, save_game_service.py |
| INFO | Game flow milestones | app.py:246, resources.py |
| WARNING | Missing assets, fallbacks | asset_manager.py, persistence.py |
| ERROR | Exception details, failures | save_game_service.py:110 |

---

## Recommended Standards

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

## Top Priority Issues

1. **ERR-001/ERR-01: Overly Broad Exception Handling** - Affects 46+ locations, masks errors
2. **ERR-002/ERR-02: Silent Exception Swallowing in AI** - Causes unpredictable AI behavior, debugging nightmare
3. **ERR-012: Swallowed Component Exceptions** - Data corruption risk in ship designs
4. **ERR-003: Generic Exception Raising** - Inconsistent error semantics, 7 instances
5. **ERR-011: No Custom Exception Hierarchy** - Cannot distinguish error types programmatically

---

## Recommendations Timeline

1. **Immediate (Week 1):**
   - Create custom exception hierarchy (ValidationError, ResourceError, StateError)
   - Replace all bare `except:` with specific types

2. **Week 1:**
   - Add proper exception context chaining with `raise from e`
   - Fix silent exception handlers in AI targeting

3. **Week 2:**
   - Standardize error codes for ValidationResult
   - Add input validation at API boundaries

4. **Week 3:**
   - Establish log level guidelines document
   - Review and standardize error message formatting
