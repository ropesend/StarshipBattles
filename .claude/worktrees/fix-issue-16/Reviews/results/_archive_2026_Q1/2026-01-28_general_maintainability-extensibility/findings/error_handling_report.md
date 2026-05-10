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
