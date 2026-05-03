# Module Structure Analyst Report

## Summary
- Total issues found: 5
- Critical: 1, Major: 2, Minor: 2, Info: 0

---

## Findings

### CRITICAL: Incorrect ValidationResult Import Chain
**ID:** MSA-01
**Location:** `game/simulation/entities/ship.py:12`
**Issue:** Imports `ValidationResult` from `game.simulation.ship_validator` instead of canonical source `game.core.validation`. Creates indirect dependency chain.

**Import Analysis:**
- Canonical: `game.core.validation` - 12 files use this
- Indirect: `game.simulation.ship_validator` - 2 files use this
- Dead re-export: `game.simulation.validation` - 0 files use this

**Impact:** Violates single source of truth; complicates dependencies

**Recommendation:** Change import to `from game.core.validation import ValidationResult`

**Effort:** Simple

---

### MAJOR: Dead Re-export in validation/__init__.py
**ID:** MSA-02
**Location:** `game/simulation/validation/__init__.py:9,12`
**Issue:** Re-exports ValidationResult from game.core.validation with backward compat note, but **ZERO files** import from this path.

**Impact:** Confusing dead code suggesting incomplete migration

**Recommendation:** Remove ValidationResult from __all__ and imports; update documentation

**Effort:** Simple

---

### MAJOR: Inconsistent Import in vehicle_design_service.py
**ID:** MSA-03
**Location:** `game/simulation/services/vehicle_design_service.py:18`
**Issue:** Uses conditional import from ship_validator (TYPE_CHECKING guard) instead of canonical game.core.validation.

**Impact:** Creates multiple import paths; suggests circular dependency workaround

**Recommendation:** Use consistent import from game.core.validation; fix circular dependencies at root

**Effort:** Medium

---

### MINOR: Dead LayerType Re-export
**ID:** MSA-04
**Location:** `game/simulation/components/component_constants.py:17-19`
**Issue:** LayerType re-exported from game.core.constants with PROJ-17 backward compat comment. **59 files** import directly from canonical source; **0 files** use re-export.

**Impact:** Dead re-export adds clutter

**Recommendation:** Remove re-export - all usages already use canonical path

**Effort:** Simple

---

### MINOR: Unclear Validation Module API
**ID:** MSA-05
**Location:** `game/simulation/validation/__init__.py:10-11`
**Issue:** Re-exports DesignValidationRule and AdditionValidationRule as public API but unclear if these should be public or internal.

**Impact:** Exposes internal implementation details

**Recommendation:** Review and clarify public API scope

**Effort:** Simple

---

## Import Pattern Summary

| Import Path | Files Using | Status |
|-------------|-------------|--------|
| `game.core.validation.ValidationResult` | 12 | CANONICAL |
| `game.simulation.ship_validator.ValidationResult` | 2 | Indirect |
| `game.simulation.validation.ValidationResult` | 0 | DEAD |
| `game.core.constants.LayerType` | 59 | CANONICAL |
| `game.simulation.components.component_constants.LayerType` | 0 | DEAD |

---

## Top 5 Priority Issues

1. **MSA-01: Fix ship.py import** - CRITICAL, canonical source
2. **MSA-02: Remove dead validation re-export** - MAJOR, zero usage
3. **MSA-03: Fix vehicle_design_service import** - MAJOR, consistency
4. **MSA-04: Remove LayerType re-export** - MINOR, zero usage
5. **MSA-05: Clarify validation API** - MINOR, documentation

## Migration Status

PROJ-21 Phase 1 (Consolidate duplicates) is mostly complete:
- 12 files use canonical path vs 2 using indirect
- Re-exports exist but have zero consumers
- **Safe to remove all dead re-exports**
