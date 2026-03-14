# Style Analyzer Report

**Date:** 2026-03-13
**Scope:** `game/` directory (429 Python files, ~95K lines)
**Analyzer:** Style Consistency Review

---

## Summary

- **Total issues found:** 12
- **Critical:** 0
- **Major:** 3
- **Minor:** 6
- **Info:** 3

The codebase demonstrates strong overall consistency in naming conventions and Python idiom usage. The main areas of inconsistency are: (1) mixed string quoting style, (2) uneven type hint coverage in the UI layer, and (3) mixed abbreviation conventions for `btn`/`button` and `idx`/`index`. Core architectural patterns (class naming, function naming, docstring format) are highly consistent.

---

## Findings

### MAJOR: Inconsistent String Quoting Convention

**ID:** SA-001
**Location:** Codebase-wide (406+ files)
**Issue:** The codebase uses a mix of single and double quotes for regular strings. Double quotes are dominant overall (~64% of string literals), but file-level analysis shows 47 files predominantly use single quotes, 212 predominantly use double quotes, and 147 files are mixed. There is no enforced convention.
**Impact:** Inconsistent quoting reduces visual uniformity and makes automated formatting harder. New contributors must guess which style to use.
**Recommendation:** Standardize on double quotes (the dominant pattern). Consider adding a formatter like `black` (which enforces double quotes) or `ruff format`.
**Effort:** Simple (automated via formatter)

---

### MAJOR: UI Layer Lacks Return Type Annotations

**ID:** SA-002
**Location:** `game/ui/` (193 files)
**Issue:** Return type annotation coverage in the UI layer is only 46% (994/2135 functions), far below other layers: core 91%, ai 89%, strategy 86%, simulation 77%. Additionally, 41 UI files with >20 lines have zero type hints at all (e.g., `test_run_details.py` at 895 lines, `stats_config.py` at 623 lines, `ship_stats_renderer.py` at 416 lines).
**Impact:** Reduced IDE support, harder refactoring, inconsistent with the rest of the codebase. Type hints are a stated project convention in CLAUDE.md.
**Recommendation:** Prioritize adding type hints to the largest untyped UI files. Target 80%+ return type coverage across all layers.
**Effort:** Complex (many files to update, but can be done incrementally)

---

### MAJOR: Import Ordering Inconsistency

**ID:** SA-003
**Location:** 126 of 348 files with 3+ imports (36%)
**Issue:** 36% of files do not follow the standard Python import ordering convention (stdlib -> third-party -> local). While 64% of files are correctly ordered, the inconsistency is widespread.
**Impact:** Makes it harder to quickly scan imports and identify dependencies. PEP 8 and isort conventions are well-established.
**Recommendation:** Enforce import ordering with `isort` or `ruff` in pre-commit hooks. The dominant pattern (stdlib -> third-party -> local) is correct and should be standardized.
**Effort:** Simple (automated via isort/ruff)

---

### MINOR: Mixed Abbreviation for `btn` vs `button`

**ID:** SA-004
**Location:** Primarily `game/ui/` (42 files use `btn`, 47 use `button`, 24 use both)
**Issue:** The abbreviation `btn` (526 occurrences) and full word `button` (333 occurrences) are used interchangeably, including within the same files (24 files use both). For example, `battle_panels.py`, `research_controls.py`, and several builder screens mix both forms.
**Impact:** Inconsistent naming within the same file creates confusion. Developers must check existing code to know which form to use.
**Recommendation:** Standardize on `button` (full word) for new code, as it is more readable and consistent with the project's preference for full words over abbreviations in other cases (e.g., `manager` over `mgr` at 252 vs 23, `calculate` over `calc` at 102 vs 0, `config` over `cfg` at 294 vs 1). The `btn` abbreviation is a UI-specific legacy pattern.
**Effort:** Medium (widespread in UI code, but low risk)

---

### MINOR: Mixed Abbreviation for `idx` vs `index`

**ID:** SA-005
**Location:** Codebase-wide
**Issue:** Both `index` (202 occurrences) and `idx` (105 occurrences) are used as variable name components. Unlike `btn`/`button`, neither form strongly dominates.
**Impact:** Minor readability inconsistency. Both forms are well-understood in Python.
**Recommendation:** Prefer `index` for consistency with other full-word preferences, but `idx` is acceptable in tight loop contexts. Do not enforce strictly.
**Effort:** Simple (convention guidance only)

---

### MINOR: 28 Classes Missing Docstrings

**ID:** SA-006
**Location:** Various files (see list below)
**Issue:** 28 of 617 classes (4.5%) lack docstrings, despite 95% coverage overall. Notable omissions include core domain entities: `Ship` (ship.py:29), `Projectile` (projectile.py:18), `StarSystem` (galaxy.py:72), `Galaxy` (galaxy.py:153), `Star` (stars.py:101), `AIController` (controller.py:70), and several UI builder panels.
**Impact:** These are important domain classes that new developers will seek documentation for. The high overall coverage makes these gaps more conspicuous.
**Recommendation:** Add docstrings to the 28 missing classes, prioritizing domain entities (`Ship`, `Galaxy`, `StarSystem`, `Star`, `Projectile`, `AIController`).
**Effort:** Simple (28 docstrings to add)

---

### MINOR: 20% of Public Methods Lack Docstrings

**ID:** SA-007
**Location:** 685 of 3529 public methods (19.4%)
**Issue:** While class-level docstring coverage is 95%, public method coverage is 80%. The gap is concentrated in UI rendering methods and data transformation helpers.
**Impact:** Moderate - most critical/complex methods are documented, but the gap in UI methods makes the rendering pipeline harder to understand.
**Recommendation:** Focus docstring effort on methods with complex logic or non-obvious behavior. Simple getters/setters and obvious methods do not need docstrings.
**Effort:** Medium (685 methods, but many may not need docstrings)

---

### MINOR: Optional[X] vs X | None Style

**ID:** SA-008
**Location:** Codebase-wide
**Issue:** The codebase uses `Optional[X]` (815 occurrences) almost exclusively over the modern `X | None` syntax (4 occurrences). While this is internally consistent, it uses the older typing style.
**Impact:** None for consistency (it IS consistent). Minor modernization opportunity.
**Recommendation:** Keep `Optional[X]` for now since it is the dominant pattern and the project uses Python 3.10. If/when migrating to Python 3.12+, consider switching to `X | None`. Do not mix styles.
**Effort:** Simple (no action needed, already consistent)

---

### MINOR: Residual .format() and % Formatting

**ID:** SA-009
**Location:** 4 files use `.format()`, 10 files use `%` formatting
**Issue:** f-strings are the dominant string formatting pattern (220+ files, hundreds of uses). However, `.format()` appears in 4 files and `%` formatting in 10 files. These are remnants rather than an active convention.
**Impact:** Very low - the inconsistency is small. Some cases may be intentional (e.g., lazy formatting in logging).
**Recommendation:** Convert remaining `.format()` and `%` formatting to f-strings during normal maintenance. Do not create a dedicated cleanup project.
**Effort:** Simple (14 files, low count per file)

---

### INFO: Naming Convention Compliance is Excellent

**ID:** SA-010
**Location:** Codebase-wide
**Issue:** No issues found. All 617 classes use PascalCase. All 4250 functions/methods use snake_case. Zero camelCase functions detected. Zero underscore-in-class-name violations detected. UPPER_CASE is used consistently for module-level constants (580 instances).
**Impact:** Positive - this is a strength of the codebase.
**Recommendation:** No action needed. The naming discipline is exemplary.
**Effort:** N/A

---

### INFO: Docstring Format is Consistently Google Style

**ID:** SA-011
**Location:** Codebase-wide
**Issue:** No issues found. Google-style docstrings (`Args:`, `Returns:`, `Raises:`) are used in 330 files. Zero files use NumPy style. Zero files use reST (`:param`) style. All docstrings use triple double-quotes (`"""`); zero use triple single-quotes (`'''`).
**Impact:** Positive - highly consistent docstring convention.
**Recommendation:** No action needed. Continue using Google-style docstrings with triple double-quotes.
**Effort:** N/A

---

### INFO: Python Idiom Usage is Consistent

**ID:** SA-012
**Location:** Codebase-wide
**Issue:** No issues found. The codebase shows consistent Python idiom preferences:
- `isinstance()` strongly preferred over `type()` comparison (334 vs 0 confirmed type() comparisons)
- List/dict comprehensions used appropriately (346 instances)
- Ternary expressions used moderately (268 instances)
- `@dataclass` used extensively (113 instances)
- `Protocol` preferred over `ABC` for interfaces (52 vs 16)
- No walrus operator usage (consistent avoidance, compatible with Python 3.10 baseline)
- Only 2 TODOs, 0 FIXMEs, 0 HACKs in the entire codebase (very clean)
**Impact:** Positive - modern Python patterns used consistently.
**Recommendation:** No action needed.
**Effort:** N/A

---

## Style Consistency Summary Table

| Style Aspect | Variants Found | Dominant Pattern | Recommendation |
|---|---|---|---|
| Class naming | 1 (PascalCase) | PascalCase (100%) | No action needed |
| Function naming | 1 (snake_case) | snake_case (100%) | No action needed |
| Constants | 1 (UPPER_CASE) | UPPER_CASE (100%) | No action needed |
| String quoting | 2 (single, double) | Double quotes (64%) | Standardize on double quotes |
| String formatting | 3 (f-string, .format, %) | f-strings (93%+) | Convert remaining to f-strings |
| Docstring format | 1 (Google style) | Google style (100%) | No action needed |
| Docstring quotes | 1 (triple double) | `"""` (100%) | No action needed |
| Type hints (params) | Mixed coverage | 71% overall | Improve UI layer coverage |
| Return type hints | Mixed coverage | 64% overall, UI at 46% | Improve UI layer to 80%+ |
| Optional syntax | 1 (Optional[X]) | Optional[X] (99.5%) | No action needed |
| Import ordering | 2 (ordered, unordered) | Correct ordering (64%) | Enforce with isort/ruff |
| Boolean prefixes | is_, has_, can_ | is_ dominant (482) | No action needed |
| Private methods | 1 (single underscore) | `_method` (100%) | No action needed |
| Accessor prefix | get_, load_ | get_ (561) vs load_ (63) | No action needed (semantic) |
| Abbreviations | Mixed (btn/button, idx/index) | Full words preferred | Standardize on full words |
| isinstance vs type | 1 (isinstance) | isinstance (100%) | No action needed |
| Interface pattern | 2 (Protocol, ABC) | Protocol (76%) | No action needed |

---

## Top 5 Priority Issues

1. **SA-003 - Import Ordering (Major):** 36% of files have non-standard import ordering. Fix with `isort` or `ruff` - fully automatable, zero risk, immediate consistency win.

2. **SA-001 - String Quoting (Major):** Mixed single/double quotes across 406+ files. Fix with `black` or `ruff format` - fully automatable, one-time change.

3. **SA-002 - UI Type Hints (Major):** UI layer has only 46% return type coverage vs 86-91% elsewhere. This is the largest organic inconsistency and impacts IDE support and refactoring confidence. Requires manual effort but can be done incrementally.

4. **SA-004 - btn vs button (Minor):** 24 files use both forms. Standardize on `button` to match the project's general preference for full words. Can be done during normal maintenance.

5. **SA-006 - Missing Class Docstrings (Minor):** 28 classes (including `Ship`, `Galaxy`, `StarSystem`) lack docstrings despite 95% overall coverage. Quick wins that improve documentation for the most important domain entities.
