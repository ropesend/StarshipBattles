# Dead Code Hunter Report
**Review Date:** 2026-02-27
**Scope:** Strategy domain model files (~9,250 lines across 33 files)
**Focus:** God class accumulation patterns - unused methods, dead imports, orphaned helpers

---

## Summary
- **Total issues found:** 15
- **Critical:** 0
- **Major:** 5
- **Minor:** 7
- **Info:** 3
- **Estimated lines removable:** ~150 lines

---

## Findings

### MAJOR: Unused ShipInstance methods (test-only usage)
**ID:** DC-001
**Location:** `game/strategy/data/ship_instance.py:227-233, 417-446`
**Issue:** Multiple methods only called from tests, not production code:
- `get_layer_damage_summary()` (lines 435-446) - Returns empty dict with TODO comment
- `get_component_damage_summary()` (lines 417-424) - Only used in test_ship_instance_damage.py
- `get_damaged_component_count()` (lines 426-433) - Only used in test_ship_instance_damage.py and ship_detail_panel.py
- `get_components_by_layer()` (lines 460-468) - Only used by Ship.get_components_by_layer()

**Impact:** ~45 lines of maintenance burden for methods that provide no production value. `get_layer_damage_summary()` explicitly states it can't work without converting to Ship first.

**Recommendation:**
1. Delete `get_layer_damage_summary()` entirely - it's a no-op placeholder
2. Move `get_component_damage_summary()` and `get_damaged_component_count()` to test helpers
3. Delete `get_components_by_layer()` if only used internally by other dead methods

**Effort:** Simple

---

### MAJOR: ShipInstance.clone() unused
**ID:** DC-002
**Location:** `game/strategy/data/ship_instance.py:717-736`
**Issue:** `clone()` method found in 28 files but all references are in tests, docs, UML diagrams, or old builder code. No production usage in strategy engine or battle systems.

**Impact:** 20 lines of dead code + UUID generation overhead if accidentally called.

**Recommendation:** Delete `clone()` method. If hypothetical battles need ship cloning, they can use `to_dict()` / `from_dict()` serialization or implement cloning at the point of use.

**Effort:** Simple

---

### MAJOR: ShipInstance.from_ship() rarely used
**ID:** DC-003
**Location:** `game/strategy/data/ship_instance.py:184-225`
**Issue:** `from_ship()` class method has 61 references but most are in archived projects, docs, UML. Only real usage is in `design_metadata.py` and possibly battle result processing. Method duplicates functionality of `update_from_ship()`.

**Impact:** 42 lines of duplicate conversion logic.

**Recommendation:** Audit all callers. If only used in design metadata, consider inlining. The instance method `update_from_ship()` covers the battle-update use case.

**Effort:** Medium (requires careful audit of callers)

---

### MAJOR: Fleet._default_formation_positions exposed unnecessarily
**ID:** DC-004
**Location:** `game/strategy/data/fleet.py:308-314`
**Issue:** Public method `_default_formation_positions()` is only called internally by `FleetBattleAdapter._default_formation_positions()`. The leading underscore suggests private intent but it's exposed as public API.

**Impact:** 7 lines + misleading public API surface.

**Recommendation:** Make truly private or delete from Fleet entirely - FleetBattleAdapter already has its own implementation at lines 78-97.

**Effort:** Simple

---

### MAJOR: validate_planet_parameters never called
**ID:** DC-005
**Location:** `game/strategy/data/planet_physics.py:131-211`
**Issue:** `validate_planet_parameters()` function (81 lines) is defined but never called in production code. Only referenced in test file and its own definition file.

**Impact:** 81 lines of untested validation logic that never executes.

**Recommendation:** Either integrate into planet generation workflow (`planet_gen.py`) with proper validation reporting, or delete as premature optimization.

**Effort:** Medium (requires design decision on validation strategy)

---

### MINOR: Unused logging in Planet
**ID:** DC-006
**Location:** `game/strategy/data/planet.py:1`
**Issue:** `import logging` and `logger = logging.getLogger(__name__)` defined but `logger` never used (0 occurrences).

**Impact:** 2 lines of dead imports.

**Recommendation:** Remove logging import and logger initialization.

**Effort:** Simple

---

### MINOR: Redundant fleet property delegates
**ID:** DC-007
**Location:** `game/strategy/data/fleet.py:208-215`
**Issue:** Two pass-through properties that just delegate to `_capabilities`:
- `has_space_shipyard` (lines 208-210)
- `space_shipyard_count` (lines 212-215)

Both are single-line delegates adding no value.

**Impact:** 8 lines of facade bloat.

**Recommendation:** Consider exposing `fleet.capabilities.has_space_shipyard` directly instead of pass-through properties. However, verify all callers first - these may be heavily used public APIs.

**Effort:** Medium (requires caller migration)

---

### MINOR: Unused FleetCapabilityCalculator.ship_has_spaceyard
**ID:** DC-008
**Location:** `game/strategy/data/fleet_capability_calculator.py:30-43`
**Issue:** Static method `ship_has_spaceyard()` found in 34 files but only used in fleet_report_filters.py and fleet_data_source.py. Never called internally by FleetCapabilityCalculator itself.

**Impact:** 14 lines of misplaced utility function.

**Recommendation:** Move to `component_inspector.py` as a general utility, or delete if UI code should use `component_inspector.ship_has_ability()` directly.

**Effort:** Simple

---

### MINOR: Unused ability query methods
**ID:** DC-009
**Location:** `game/strategy/data/fleet_capability_calculator.py:144-186`
**Issue:** Three methods with limited usage:
- `has_ability()` (lines 144-154) - 122 files reference `has_ability` but most are unrelated context
- `ships_with_ability()` (lines 156-170) - Only 17 references, mostly in superweapon code
- `ship_has_ability()` (lines 172-186) - 51 references but heavily duplicates `component_inspector.ship_has_ability()`

**Impact:** 43 lines of potential duplication with `component_inspector.py`.

**Recommendation:** Consolidate with `component_inspector.py` to avoid multiple implementations of "does ship have ability X" logic.

**Effort:** Medium (requires refactor to use component_inspector)

---

### MINOR: Planet.total_pressure_atm rarely used
**ID:** DC-010
**Location:** `game/strategy/data/planet.py:282-284`
**Issue:** Property used in 10 files but mostly UI formatting and benchmarks. Not used in any game logic calculations.

**Impact:** 3 lines of niche utility.

**Recommendation:** Keep for now (useful for UI), but document as display-only property.

**Effort:** N/A (informational)

---

### MINOR: Planet.add_production never called
**ID:** DC-011
**Location:** `game/strategy/data/planet.py:337-350`
**Issue:** Method `add_production()` found in 23 references but all in tests and old project docs. Production system uses `construction_queue` directly, not this helper.

**Impact:** 14 lines of dead helper method.

**Recommendation:** Delete. The `construction_queue` list is manipulated directly by `ProductionEngine`.

**Effort:** Simple

---

### MINOR: Unused planet helper module imports
**ID:** DC-012
**Location:** Multiple planet helper modules
**Issue:** Planet helper modules (`planet_atmosphere.py`, `planet_physics.py`, `planet_naming.py`) are only imported by:
- `planet_gen.py` (primary user)
- Test files
- One-off scripts (`diagnose_blueprints.py`, `system_mode.py`)

These are legitimate imports, but the modules are isolated to planet generation only.

**Impact:** None - these are properly scoped helper modules.

**Recommendation:** Keep as-is. These follow good separation of concerns.

**Effort:** N/A (informational)

---

### INFO: Commented code in FleetOrder.to_dict()
**ID:** DC-013
**Location:** `game/strategy/data/fleet.py:75-114`
**Issue:** Extensive inline documentation about target format handling (lines 435-442 in from_dict). Not "dead code" per se, but verbose.

**Impact:** None - documentation is valuable.

**Recommendation:** Keep. The target format documentation is critical for understanding serialization.

**Effort:** N/A (informational)

---

### INFO: Planet helper functions working correctly
**ID:** DC-014
**Location:** `game/strategy/data/planet_atmosphere.py`, `planet_physics.py`, `planet_naming.py`
**Issue:** All helper functions are called appropriately:
- `generate_atmosphere()` - used by planet_gen.py
- `calculate_*()` physics functions - used by planet_gen.py
- `assign_body_names()` - used by planet_gen.py

**Impact:** None - these are NOT dead code.

**Recommendation:** No action needed. These are properly scoped utility modules.

**Effort:** N/A (informational)

---

### INFO: PlanetaryFacility.is_shipyard used correctly
**ID:** DC-015
**Location:** `game/strategy/data/planet.py:130-148`
**Issue:** Property found in 19 files with legitimate usage in build queue systems and production engine.

**Impact:** None - this is active production code.

**Recommendation:** No action needed.

**Effort:** N/A (informational)

---

## Top 5 Priority Issues

1. **DC-005 - validate_planet_parameters never called (81 lines)** - Largest single chunk of dead code. Either use it or lose it.

2. **DC-001 - Unused ShipInstance damage query methods (~45 lines)** - Test-only methods cluttering the public API.

3. **DC-003 - ShipInstance.from_ship() redundant (42 lines)** - Overlaps with update_from_ship(), needs audit.

4. **DC-009 - Duplicate ability query methods (43 lines)** - Consolidate with component_inspector.py.

5. **DC-002 - ShipInstance.clone() unused (20 lines)** - Dead cloning code with UUID overhead.

**Total high-priority removable lines:** ~231 lines (if all deleted)

---

## Recommendations Summary

### Quick Wins (Simple effort, <1 hour)
- DC-006: Remove unused logging in Planet.py (2 lines)
- DC-011: Delete Planet.add_production() (14 lines)
- DC-002: Delete ShipInstance.clone() (20 lines)
- DC-004: Delete Fleet._default_formation_positions or make private (7 lines)
- DC-008: Move ship_has_spaceyard to component_inspector (14 lines)

**Total quick wins: 57 lines**

### Medium Effort (2-4 hours)
- DC-001: Move test-only ShipInstance methods to test helpers (45 lines)
- DC-003: Audit ShipInstance.from_ship() usage (42 lines)
- DC-007: Remove pass-through fleet properties after caller migration (8 lines)
- DC-009: Consolidate ability queries with component_inspector (43 lines)

**Total medium effort: 138 lines**

### Design Decisions Required
- DC-005: validate_planet_parameters - integrate or delete (81 lines)

---

## Architecture Notes

### God Class Patterns Observed
The strategy domain models show **good delegation patterns** overall:
- Fleet properly delegates to FleetResourceAggregator, FleetCapabilityCalculator, FleetBattleAdapter
- ShipInstance properly delegates to ShipResourceManager, ShipCargoManager, ShipDisplayFormatter
- Planet uses helper modules (planet_physics, planet_atmosphere, planet_naming)

**Dead code accumulates in two patterns:**
1. **Test-only methods** that never got cleaned up (DC-001, DC-002)
2. **Superseded helpers** where new systems replaced old entry points (DC-003, DC-011)

### No Major God Class Issues Found
Despite the review focus on "god class accumulation," the strategy data models are **well-factored**:
- Delegation is clean and consistent
- Helper modules are properly scoped
- Most methods have legitimate production usage

The ~150 lines of removable code are mostly **test artifacts and orphaned helpers**, not god class bloat.

---

## Conclusion

The strategy domain models are in **good shape** from a dead code perspective. The main issues are:
- Test-only methods that should be extracted to test utilities
- A large unused validation function (validate_planet_parameters)
- Minor duplication between Fleet/component_inspector for ability queries

**Recommended action:** Execute the 5 quick wins (57 lines) immediately, then audit the medium-effort items (138 lines) during the next refactoring cycle.
