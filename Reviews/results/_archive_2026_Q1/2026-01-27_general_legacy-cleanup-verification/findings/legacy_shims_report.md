# Legacy Pattern Analyst - Shims Report

## Summary
- Total issues found: 4
- Critical: 1, Major: 2, Minor: 1, Info: 0

---

## Findings

### CRITICAL: ShipControllableAdapter Blocks Interface Migration
**ID:** LPA-01
**Location:** `game/ai/interfaces/controllable.py:162-308`
**Issue:** Adapter uses `__getattr__`/`__setattr__` delegation for backward compatibility. AIController directly accesses 20+ ship attributes instead of using IControllable interface methods.

**Evidence:**
- AIController accesses: `position`, `turn_throttle`, `angle`, `engine_throttle`, `formation_members`, `in_formation`, `formation_master`, `turn_speed`, `radius`, `get_components_by_ability()`
- Comment (lines 189-192): "Until controller.py is refactored to use interface methods exclusively, these delegation methods must remain"

**Impact:** HIGH - Interface migration incomplete; adapter is temporary pattern masking the real dependency

**Recommendation:** Schedule PROJ refactoring to update AIController to use IControllable interface exclusively. Requires ~50 method updates.

**Effort:** Complex

---

### MAJOR: ship_theme.py Deprecation Shim Can Be Removed
**ID:** LPA-02
**Location:** `game/simulation/ship_theme.py:1-19`
**Issue:** Deprecation shim re-exports ShipThemeManager with DeprecationWarning. **ZERO imports** from old path found in production code.

**Evidence:**
- 0 files use `from game.simulation.ship_theme import`
- 72 files import correctly from `game.ui.assets`
- Shim exists with proper deprecation warning but serves no current consumers

**Impact:** MEDIUM - Dead code that provides no value

**Recommendation:** Delete file immediately - no migration needed

**Effort:** Simple

---

### MAJOR: SHIP_CLASSES Alias Has Minimal Usage
**ID:** LPA-03
**Location:** `game/simulation/entities/ship.py:25`
**Issue:** `SHIP_CLASSES = VEHICLE_CLASSES` alias used by only 1 production file (`builder/main.py:858` calls `.clear()`). Creates confusion about canonical name.

**Impact:** MEDIUM - Same dict object; mutations affect both references

**Recommendation:**
1. Update `builder/main.py:858` to use `VEHICLE_CLASSES.clear()`
2. Remove alias from ship.py

**Effort:** Simple

---

### MINOR: _ValidatorProxy Not Used
**ID:** LPA-04
**Location:** `game/simulation/entities/ship.py:28-33`
**Issue:** Lazy-loading proxy for validator defined but VALIDATOR global has zero usages in codebase.

**Impact:** LOW - Dead code pattern

**Recommendation:** Remove `_ValidatorProxy` class and `VALIDATOR` instance (6 lines)

**Effort:** Simple

---

## Top 5 Priority Issues

1. **LPA-01: ShipControllableAdapter** - CRITICAL, blocks interface migration, Complex effort
2. **LPA-02: ship_theme.py shim** - MAJOR, zero usage, delete immediately, Simple
3. **LPA-03: SHIP_CLASSES alias** - MAJOR, 1 usage, update and remove, Simple
4. **LPA-04: _ValidatorProxy** - MINOR, unused pattern, remove, Simple
