# Inconsistency Hunter Report

## Summary
- Total issues found: 20
- Critical: 1, Major: 2, Minor: 12, Info: 5
- Overall Grade: B+ (Good consistency with clear improvement paths)

## Findings

### CRITICAL: Exception Handling — ValueError vs Custom Exceptions
**ID:** IH-005
**Location:** 50 ValueError raises vs 26 custom exception raises across game/
**Issue:** Despite well-designed exception hierarchy (PROJ-45), much code still raises generic Python exceptions.
**Pattern A:** Semantic custom exceptions (ValidationException, etc.) — 26 uses
**Pattern B:** Generic ValueError — 50 uses across 17 files
**Pattern C:** Generic RuntimeError — 4 uses
**Impact:** Callers cannot programmatically distinguish error types
**Deliberate?:** No — guidelines established later, older code not updated
**Recommendation:** HIGH PRIORITY — Migrate all ValueError/RuntimeError to semantic exceptions
**Effort:** Medium (50 occurrences)

### MAJOR: Logger Initialization Pattern (3 competing patterns)
**ID:** IH-001
**Location:** 118 files use custom Logger, 6 use standard logging, 4 use test lab logger
**Issue:** Three competing logging approaches
**Pattern A:** `logging.getLogger(__name__)` — 6 files (standard)
**Pattern B:** `game.core.logger.Logger.instance()` / `log_info()` — 118 files
**Pattern C:** `simulation_tests.logging_config.get_logger` — 4 files (test lab)
**Impact:** Inconsistent logging infrastructure
**Deliberate?:** No — organic growth
**Recommendation:** Standardize on `logging.getLogger(__name__)`
**Effort:** Medium (118 files)

### MAJOR: JSON Loading Pattern — Direct vs Utility
**ID:** IH-010
**Location:** 18 direct json.load/dump calls vs 101 load_json/save_json utility calls
**Issue:** Centralized JSON utilities exist but some files bypass them
**Pattern A:** `json.load(f)` — 18 instances across 9 files
**Pattern B:** `core.json_utils.load_json()` — 101 instances across 30 files
**Impact:** Inconsistent error handling and path resolution
**Deliberate?:** No
**Recommendation:** Standardize on core.json_utils
**Effort:** Low (18 occurrences)

### MINOR: Import Style — Absolute vs Relative
**ID:** IH-002
**Pattern A:** Absolute imports — 868 files (dominant)
**Pattern B:** Relative imports — 100 files (subsystems)
**Deliberate?:** Partially — relative for subsystem cohesion
**Recommendation:** Establish rule: relative only within tightly-coupled subsystems

### MINOR: Optional Type Annotation Syntax
**ID:** IH-003
**Pattern A:** `Optional[str]` — 607 instances (dominant)
**Pattern B:** `str | None` — 4 instances (recent code)
**Recommendation:** Continue Optional[X] for consistency

### MINOR: Dict Type Annotation Syntax
**ID:** IH-004
**Pattern A:** `Dict[K, V]` — 506 instances
**Pattern B:** `dict[k, v]` — 21 instances
**Recommendation:** Continue Dict[K, V] for consistency

### MINOR: String Formatting Style
**ID:** IH-006
**Pattern A:** f-strings — 1840 instances (dominant)
**Pattern B:** .format() — 2 instances
**Pattern C:** % formatting — 13 instances (legacy)
**Recommendation:** Migrate remaining to f-strings

### MINOR: None-Checking Patterns
**ID:** IH-007
**Pattern A:** `if x is None:` — 323 instances
**Pattern B:** `if not x:` — 815 instances
**Recommendation:** Context-dependent, both valid

### MINOR: Dataclass vs Regular Class
**ID:** IH-008
**Pattern A:** @dataclass — 98 classes (DTOs, value objects)
**Pattern B:** Regular classes — 239 classes (stateful objects)
**Deliberate?:** Yes — appropriate usage

### MINOR: Module Docstrings
**ID:** IH-013
**Issue:** Core modules well-documented, 200+ files lack module docstrings
**Recommendation:** Add during normal maintenance

### MINOR: __all__ Exports Declaration
**ID:** IH-014
**Pattern A:** Explicit __all__ — 44 files
**Pattern B:** No __all__ — 326 files
**Recommendation:** Continue current selective approach

### MINOR: Any Type Overuse
**ID:** IH-019
**Location:** 199 `: Any` instances across 47 files
**Issue:** Reduces type safety benefits
**Recommendation:** Gradually replace with specific types

### MINOR: Logging Module Access (Reinforces IH-001)
**ID:** IH-020
**Issue:** Multiple competing logging approaches
**Recommendation:** Same as IH-001

### MINOR: Dictionary Access Pattern
**ID:** IH-011
**Pattern A:** `.get()` — 1010 instances
**Pattern B:** `dict['key']` — 1322 instances
**Recommendation:** No change — contextual usage

### INFO: Property Decorator Usage
**ID:** IH-009
**Issue:** 1087 @property, 132 @staticmethod, 76 @classmethod — appropriate usage

### INFO: Method Privacy Convention
**ID:** IH-012
**Issue:** Consistent underscore prefix for private methods

### INFO: Assert vs Raise
**ID:** IH-015
**Issue:** Zero asserts in production code — correct practice

### INFO: Protocol Definitions
**ID:** IH-018
**Issue:** 28 protocols, centralized with domain-specific exceptions — deliberate

### INFO: Empty Method Bodies
**ID:** IH-016
**Issue:** Only 2 instances of `pass` — minimal occurrence

## Top 5 Priority Issues

1. **IH-005 (Critical):** Exception handling — migrate 50 ValueError to custom exceptions
2. **IH-001/020 (Major):** Logger pattern — standardize 118 files
3. **IH-010 (Major):** JSON loading — standardize 18 direct calls
4. **IH-006 (Minor):** String formatting — migrate 15 legacy occurrences
5. **IH-019 (Minor):** Any type overuse — gradually replace 199 occurrences
