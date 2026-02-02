### Summary
- Total issues found: 3
- Critical: 0, Major: 2, Minor: 1, Info: 0

### Findings

#### MAJOR: Dangerous Use of eval()
**ID:** SEC-01
**Location:** `game/simulation/formula_system.py:120`
**Issue:** Usage of `eval()` to calculate formulas.
**Impact:** Remote Code Execution (RCE) risk if formula strings can be influenced by external sources (e.g., downloaded mods, save files).
**Recommendation:** Replace `eval()` with a safe math parser library (e.g., `simpleeval`, `pyparsing`) or a strict AST whitelist.
**Effort:** Medium

#### MAJOR: Bare Exception in Resource Scripts
**ID:** SEC-02
**Location:** `scripts/apply_resource_costs.py:96`
**Issue:** `except: pass` swallows all errors, including SystemExit and KeyboardInterrupt.
**Impact:** Scripts may fail silently, leaving data in inconsistent states or hiding critical bugs.
**Recommendation:** Catch specific exceptions (`Exception` or specific types) and log the error.
**Effort:** Simple

#### MINOR: Sandbox Reliance
**ID:** SEC-03
**Location:** `game/simulation/components/modifier_effects.py`
**Issue:** Reliance on `eval()` with `__builtins__: {}` sandbox.
**Impact:** Python sandboxes using `eval` are historically bypassable.
**Recommendation:** Audit if this is truly required for flexibility or if a data-driven approach works.
**Effort:** Medium

### Top 5 Priority Issues
1. Replace `eval()` in `formula_system.py` (SEC-01)
2. Fix bare excepts in `apply_resource_costs.py` (SEC-02)
