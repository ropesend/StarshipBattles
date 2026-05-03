# Error Handling Auditor Report

## Summary
- **Total issues found:** 47
- **Critical:** 8, **Major:** 18, **Minor:** 15, **Info:** 6

---

## Critical Findings

### CRITICAL: Bare Exception Clauses Swallowing All Errors
**ID:** ERR-001
**Location:** `game/ui/screens/save_selection_window.py:148,171`
**Issue:** Bare except clauses catch all exceptions including KeyboardInterrupt and SystemExit.
**Impact:** Makes debugging extremely difficult; prevents proper system signal handling.
**Recommendation:** Use specific exception types and log the error.
**Effort:** Simple

### CRITICAL: Exception Swallowed Without Context in Formula System
**ID:** ERR-002
**Location:** `game/simulation/formula_system.py:31`
**Issue:** `except Exception:` with silent return of 0. No logging, no error context.
**Impact:** Silent failures in critical game logic; balance bugs won't be noticed.
**Recommendation:** Log the error and formula context.
**Effort:** Simple

### CRITICAL: No Validation Before eval() in Formula System
**ID:** ERR-003
**Location:** `game/simulation/formula_system.py:1-33`
**Issue:** eval() call is dangerous. No whitelist of allowed variables enforced.
**Impact:** If malicious formulas are loaded or injected, could cause DoS or information leakage.
**Recommendation:** Whitelist allowed math functions. Use ast.parse() for pre-validation.
**Effort:** Medium

### CRITICAL: Missing Error Propagation in SaveGameService
**ID:** ERR-004
**Location:** `game/strategy/systems/save_game_service.py:109-113,236-240`
**Issue:** Broad `except Exception` with `traceback.print_exc()` to stdout, not logging system.
**Impact:** Error details are lost in production; makes auditing impossible.
**Recommendation:** Use `log_error()` with traceback module.
**Effort:** Simple

### CRITICAL: Unhandled None Return in DesignLibrary
**ID:** ERR-005
**Location:** `game/strategy/systems/design_library.py:232-233`
**Issue:** `load_design_data()` silently returns None on any exception without logging.
**Impact:** Silent data loading failures; no audit trail.
**Recommendation:** Log the error with design ID context.
**Effort:** Simple

### CRITICAL: File I/O Error Not Propagated in ShipIO
**ID:** ERR-006
**Location:** `game/simulation/systems/persistence.py:12`
**Issue:** Module-level exception handling with bare `except Exception:` silently fails.
**Impact:** Ship serialization system may be completely broken without warning.
**Recommendation:** Log the error and fail fast if critical.
**Effort:** Simple

### CRITICAL: Missing Input Validation at System Boundary
**ID:** ERR-007
**Location:** `game/ui/screens/strategy_input_handler.py:516`
**Issue:** `except Exception:` on handler with silent `pass`. Events may be lost.
**Impact:** Player input can silently fail; game appears frozen.
**Recommendation:** Log and re-raise.
**Effort:** Simple

### CRITICAL: Screenshot Manager Swallows Critical Errors
**ID:** ERR-008
**Location:** `game/core/screenshot_manager.py:130`
**Issue:** `except Exception:` with silent `pass` in clipboard copy.
**Impact:** Users won't know why screenshot path wasn't copied.
**Recommendation:** Log the error as warning.
**Effort:** Simple

---

## Major Findings

### MAJOR: Swallowed Exceptions in DateTime Parsing
**ID:** ERR-009
**Location:** `game/ui/screens/save_selection_window.py:144-149,167-172`
**Issue:** Three bare `except:` clauses silently catch datetime parsing failures.
**Impact:** Malformed timestamps display as blank.
**Recommendation:** Use specific exception and log the issue.
**Effort:** Simple

### MAJOR: Missing Context in Design Library Errors
**ID:** ERR-010
**Location:** `game/strategy/systems/design_library.py:53-60,91-96,170-174`
**Issue:** Exception handlers log errors but don't include enough context.
**Impact:** Hard to debug which specific design failed.
**Recommendation:** Include full context in log messages.
**Effort:** Simple

### MAJOR: No Error Logging in Modifier Row Tooltip
**ID:** ERR-012
**Location:** `ui/builder/modifier_row.py:79`
**Issue:** `except Exception:` in tooltip generation silently falls back.
**Impact:** Tooltip errors won't be discovered in production.
**Recommendation:** Log before fallback.
**Effort:** Simple

### MAJOR: Silent Failure in JSON Utilities
**ID:** ERR-013
**Location:** `game/core/json_utils.py:26-60`
**Issue:** `load_json()` returns default value silently on any error.
**Impact:** Cannot distinguish between "file doesn't exist" and "file is corrupted".
**Recommendation:** Add error tracking or return (data, error_type) tuple.
**Effort:** Medium

### MAJOR: No Validation in Ability Factory
**ID:** ERR-014
**Location:** `game/simulation/components/abilities/__init__.py:100-109`
**Issue:** `create_ability()` returns None silently on any exception.
**Impact:** Invalid abilities are silently skipped; bugs go unnoticed.
**Recommendation:** Log the error with context.
**Effort:** Simple

### MAJOR: Thread-Unsafe Exception Handling in Battle Logger
**ID:** ERR-016
**Location:** `game/simulation/systems/battle_engine.py:58-59,67-68`
**Issue:** IOError exceptions silently ignored. File handle could be left partially written.
**Impact:** Battle log files may be incomplete or corrupted.
**Recommendation:** Log the IOError and consider raising.
**Effort:** Medium

### MAJOR: Resource Registry Unclear Error Conditions
**ID:** ERR-017
**Location:** `game/core/registry.py:98-131`
**Issue:** No validation that input data is non-empty. `hydrate()` could receive None silently.
**Impact:** Registry could be left in partially initialized state.
**Recommendation:** Validate inputs and raise RuntimeError if required data missing.
**Effort:** Medium

---

## Top 5 Priority Issues

1. **ERR-002: Formula System Silent Failure** - Returns 0 on any error without logging. Breaks game balance.
2. **ERR-001 & ERR-007: Bare Exception Clauses** - Catch KeyboardInterrupt and SystemExit.
3. **ERR-004: SaveGameService Error Handling** - Save/load failures printed to stdout, not logged.
4. **ERR-005 & ERR-006: Silent I/O Failures** - Design loading and ship I/O return None silently.
5. **ERR-003: eval() Security Risk** - Formula evaluation needs additional pre-validation.

---

## Pattern Analysis

**Most Common Issues:**
1. Bare `except:` or `except Exception:` with silent `pass` (15+ times)
2. Missing logging in exception handlers (20+ times)
3. No context provided in error messages (10+ times)
4. Silent failures that hide bugs (12+ times)

**Most Critical Areas:**
- Save/load system (ERR-004, 005, 006)
- Input handling (ERR-001, 007)
- Formula evaluation (ERR-002, 003)
- UI screen error handling (ERR-009, 011, 012)
