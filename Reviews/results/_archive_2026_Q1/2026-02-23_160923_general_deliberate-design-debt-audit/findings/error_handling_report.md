# Error Handling Auditor Report

## Summary
- Total issues found: 15
- Critical: 2, Major: 5, Minor: 6, Info: 2

## Findings

### CRITICAL: Missing Input Validation in Core Constructors
**ID:** ERR-001
**Location:** Multiple files:
- `game/strategy/engine/game_session.py:67` - accepts None config
- `game/simulation/entities/ship.py:48` - some params unchecked
- `game/strategy/systems/design_library.py:21` - accepts None without validation
**Issue:** Many constructors accept parameters without validation. Type errors or None values propagate deeply before detection.
**Impact:** Errors surface far from source, making debugging difficult.
**Deliberate?:** No - gradual erosion as codebase grew.
**Recommendation:** Add parameter validation at public API boundaries. Use ValidationException.
**Effort:** Medium

### CRITICAL: Inconsistent Custom Exception Usage
**ID:** ERR-002
**Location:** 50 ValueError raises vs 26 custom exceptions across game/
**Issue:** Despite comprehensive custom exception hierarchy, much code still raises generic Python exceptions instead of semantic domain exceptions.
**Examples:** asset_manager.py, system_blueprints_loader.py (20+ ValueError), battle_engine.py
**Impact:** Callers cannot programmatically distinguish error types. Violates ERROR_HANDLING_GUIDELINES.md.
**Deliberate?:** No - guidelines established later (PROJ-45), older code not updated.
**Recommendation:** Migration plan to convert ValueError → ValidationException. Linting rule.
**Effort:** Complex

### MAJOR: Swallowed Exception Without Logging
**ID:** ERR-003
**Location:** `scripts/apply_resource_costs.py:96`
**Issue:** Bare `except: pass` silently swallows parsing errors.
**Impact:** Failures invisible, debugging impossible.
**Deliberate?:** No - utility script with minimal error handling.
**Recommendation:** Catch specific exceptions, log warning.
**Effort:** Simple

### MAJOR: Silent Fallback Pattern (Missing Logging)
**ID:** ERR-004
**Location:** `game/ui/panels/battle_panels.py:41-42`, `game/ui/panels/race_environment_panel.py:475-476`
**Issue:** Exception caught but suppressed without logging. Overly broad `except Exception:` with silent fallback.
**Impact:** UI failures invisible, blank fields without explanation.
**Deliberate?:** Partially - graceful degradation intended, logging omitted.
**Recommendation:** Add log_warning with context when fallback triggered. Narrow exception types.
**Effort:** Simple

### MAJOR: Overly Broad Exception Handling
**ID:** ERR-005
**Location:** `game/core/logger.py:107`, `game/formula_system.py:139`, `game/ui/services/tkinter_utils.py:99`
**Issue:** Intentional broad `except Exception` catches risk masking SystemExit, MemoryError, programming errors.
**Impact:** Documented as intentional but risky pattern.
**Deliberate?:** Yes - explicitly commented.
**Recommendation:** Consider re-raising SystemExit/KeyboardInterrupt. Add DEBUG mode flag.
**Effort:** Medium

### MAJOR: Incomplete Error Context
**ID:** ERR-006
**Location:** `game/strategy/systems/design_library.py:90-100`
**Issue:** Catches exceptions but logs generic messages without traceback or context.
**Impact:** Insufficient context for debugging corrupted files.
**Deliberate?:** Partially - basic logging present but incomplete.
**Recommendation:** Include traceback, add context dicts, include file content snippets.
**Effort:** Medium

### MAJOR: Missing Cleanup in Error Paths
**ID:** ERR-007
**Location:** Various - file I/O in ship_io.py, tkinter_utils.py, save/load operations
**Issue:** Some paths have proper try/finally (BattleLogger), but inconsistency elsewhere.
**Impact:** Resource leaks, corrupted saves, state inconsistency.
**Deliberate?:** No - cleanup added piecemeal.
**Recommendation:** Audit file I/O for try/finally. Use context managers. Atomic rename for multi-step ops.
**Effort:** Complex

### MINOR: Inconsistent Validation at Boundaries
**ID:** ERR-008
**Location:** Strategy layer has dedicated validators, simulation layer lacks equivalent.
**Issue:** ColonizeValidator, SuperweaponValidator have comprehensive checking. Simulation lacks boundary validation.
**Impact:** Inconsistent error quality across layers.
**Deliberate?:** Partially - validators added for strategy (PROJ-36/55/102), not extended.
**Recommendation:** Create validation layer for simulation boundary.
**Effort:** Complex

### MINOR: Missing Error Codes Usage
**ID:** ERR-009
**Location:** `game/core/error_codes.py` defined but ~5% adoption
**Issue:** ErrorCode enum defined but most exceptions raised without codes.
**Impact:** Cannot programmatically handle specific error types.
**Deliberate?:** No - error codes added (PROJ-45) but adoption incomplete.
**Recommendation:** Add error codes to all custom exception raises.
**Effort:** Medium

### MINOR: No Retry Logic for Transient Failures
**ID:** ERR-010
**Location:** File I/O operations across codebase
**Issue:** Single-attempt operations fail immediately on transient failures (file locks, antivirus).
**Impact:** Flaky failures, lost work on save.
**Deliberate?:** Yes - intentional simplicity for single-player game.
**Recommendation:** Add retry with exponential backoff for save operations.
**Effort:** Medium

### MINOR: Inconsistent Logging Levels
**ID:** ERR-011
**Location:** Across codebase
**Issue:** Some modules overuse log_error() for recoverable issues, others underuse for critical failures.
**Impact:** Log spam, critical failures invisible.
**Deliberate?:** No - per-module judgment without global guidelines.
**Recommendation:** Update ERROR_HANDLING_GUIDELINES.md with logging level decision tree.
**Effort:** Medium

### MINOR: Missing Validation in Deserialization
**ID:** ERR-012
**Location:** ship_serialization.py, strategy/data/ serialization
**Issue:** from_dict methods assume well-formed input, raising generic KeyError/TypeError.
**Impact:** Corrupt saves produce cryptic errors.
**Deliberate?:** No.
**Recommendation:** Add schema validation before deserialization.
**Effort:** Medium

### MINOR: No Circuit Breaker for Repeated Failures
**ID:** ERR-013
**Location:** asset_manager.py, ship_theme_manager.py
**Issue:** Asset loading retries same failed operations repeatedly, spamming logs.
**Impact:** Log spam, performance overhead.
**Deliberate?:** No - caching added but failure tracking missed.
**Recommendation:** Cache failure state, log error once.
**Effort:** Simple

### INFO: Intentional Broad Catches Well-Documented
**ID:** ERR-014
**Issue:** Broad catches in logger.py, formula_system.py, tkinter_utils.py are commented with rationale.
**Deliberate?:** Yes.

### INFO: Excellent Error Handling in Core Utilities
**ID:** ERR-015
**Issue:** json_utils.py and formula_system.py exemplify best practices: specific exceptions, proper logging, exception chaining, clear contracts.

## Metrics
- log_error: 166 calls, log_warning: 175 calls
- Try/Except blocks: 629 across 296 files
- Bare except: 1 (scripts only)
- except Exception: 46
- Guidelines compliance: ~30%

## Top 5 Priority Issues

1. **ERR-002 (CRITICAL):** Inconsistent Custom Exception Usage
2. **ERR-001 (CRITICAL):** Missing Input Validation in Core Constructors
3. **ERR-007 (MAJOR):** Missing Cleanup in Error Paths
4. **ERR-006 (MAJOR):** Incomplete Error Context
5. **ERR-003 (MAJOR):** Swallowed Exception Without Logging
