# Architecture Reviewer - Duplicates Report

## Summary
- Total issues found: 2
- Critical: 2, Major: 0, Minor: 0, Info: 0

---

## Findings

### CRITICAL: Dead Code - Obsolete Physics Mixin
**ID:** AR-01
**Location:** `game/simulation/entities/mixins/physics.py` (102 lines)
**Issue:** Complete dead code duplicate. Canonical version is `game/simulation/entities/ship_physics.py` (84 lines).

**Key Evidence:**
- `ship.py` line 14 imports from `ship_physics.py` ONLY
- `ship_physics.py` imports constants: `from game.simulation.physics_constants import K_SPEED, K_THRUST`
- `mixins/physics.py` HARDCODES constants: `K_THRUST = 2500`, `K_SPEED = 25`
- **ZERO imports** of mixins/physics.py found in entire codebase
- Contains 18+ lines of unresolved TODO comments

**Impact:** Violates Single Source of Truth for physics constants; maintenance burden

**Recommendation:** Delete `game/simulation/entities/mixins/physics.py` entirely

**Effort:** Simple

---

### CRITICAL: Dead Code - Obsolete Combat Mixin
**ID:** AR-02
**Location:** `game/simulation/entities/mixins/combat.py` (437 lines)
**Issue:** Legacy monolithic implementation superseded by modern facade pattern (PROJ-12). Canonical version is `game/simulation/entities/ship_combat.py` (186 lines) + `ShipCombatEngine` (655 lines).

**Key Evidence:**
- `ship.py` line 15 imports from `ship_combat.py` ONLY
- `ship_combat.py`: Thin facade with lazy-initialized ShipCombatEngine
- `mixins/combat.py`: Old monolithic implementation with 437 lines of embedded logic
- **ZERO imports** of mixins/combat.py found in entire codebase
- Pre-PROJ-12 code that should have been deleted

**Impact:** 437 lines of abandoned dead code; contradicts current architecture

**Recommendation:** Delete `game/simulation/entities/mixins/combat.py` entirely

**Effort:** Simple

---

## Comparison Summary

| Aspect | ship_physics.py (CANONICAL) | mixins/physics.py (DEAD) |
|--------|---------------------------|------------------------|
| Lines | 84 | 102 |
| Constants | Imports from physics_constants | Hardcoded values |
| Used by ship.py | Yes | No |
| Status | **Active** | **Dead** |

| Aspect | ship_combat.py (CANONICAL) | mixins/combat.py (DEAD) |
|--------|--------------------------|------------------------|
| Lines | 186 | 437 |
| Pattern | Facade (PROJ-12) | Monolithic (legacy) |
| Delegates to | ShipCombatEngine | N/A |
| Used by ship.py | Yes | No |
| Status | **Active** | **Dead** |

---

## Top 5 Priority Issues

1. **AR-02: Delete mixins/combat.py** - 437 lines of dead code, HIGHEST priority
2. **AR-01: Delete mixins/physics.py** - 102 lines of dead code with hardcoded constants

## Cleanup Impact

**Code to Remove:** 539 lines total
- `mixins/physics.py`: 102 lines
- `mixins/combat.py`: 437 lines

**Functionality Impact:** Zero
**Breaking Changes:** None
**Test Impact:** None
**Risk Level:** Minimal
