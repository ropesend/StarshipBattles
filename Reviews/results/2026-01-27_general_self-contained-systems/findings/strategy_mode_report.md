# Strategy Mode Analysis Report

## Summary
- **Total issues found:** 3
- **Critical:** 1, **Major:** 1, **Minor:** 1, **Info:** 0

---

## LARGEST ISSUE

### CRITICAL: Direct Simulation Layer Import Violates Architectural Boundaries

**ID:** STRAT-01

**Location:** `game/strategy/systems/design_library.py:14`

**Issue:**
`DesignLibrary` has a direct import of `game.simulation.entities.ship.Ship`:
```python
from game.simulation.entities.ship import Ship
```

This import is used in two methods:
1. **`save_design()` (line 138)**: Calls `DesignMetadata.from_ship(ship, design_id)`
2. **`load_design()` (lines 195-202)**: Creates Ship objects directly and calls `ship.recalculate_stats()`

**Impact on Maintenance/Extensibility:**
1. **Hard Coupling**: Strategy layer is tightly coupled to simulation layer internals
2. **Circular Dependencies Risk**: Makes future circular imports more likely
3. **Testing Difficulty**: Strategy layer cannot be tested in isolation
4. **Extensibility Blocked**: Cannot easily replace or mock Ship objects
5. **Architectural Violation**: Violates stated layering model

**Root Cause:**
The `load_design()` method exists to support the Ship Builder UI tool (simulation layer), not the strategy layer. This method is fundamentally a simulation-layer concern incorrectly placed in strategy-layer.

**Recommendation:**
1. **Remove `load_design()` entirely** from DesignLibrary
2. **Keep `load_design_data()` only** (returns dict, no Ship instantiation)
3. **Move Ship loading to simulation layer**: Create SimulationDesignLoader
4. **Update Ship Builder** to use simulation layer loader

**Effort:** Medium (2-3 days)

---

## Secondary Findings

### MAJOR: Service Layer Importing from Simulation Layer

**ID:** STRAT-02

**Location:** `game/strategy/services/ship_stats_service.py:20-21`

```python
from game.simulation.formula_system import evaluate_math_formula
from game.simulation.components.modifiers import calculate_stat_multipliers
```

**Issue:**
`ShipStatsService` couples strategy layer to simulation layer's formula and modifier systems.

**Impact:**
- Strategy layer dependent on simulation implementation details
- Difficult to customize stat calculation for different game modes

**Recommendation:**
Abstract formula evaluation into strategy-layer interface or duplicate calculation logic.

**Effort:** Medium

---

### MINOR: TYPE_CHECKING Imports Don't Fully Solve Coupling

**ID:** STRAT-03

**Location:** `game/strategy/data/fleet.py:5-7`, `game/strategy/data/ship_instance.py:17-18`

**Issue:**
While `TYPE_CHECKING` prevents runtime circular imports, it's a code smell indicating structural problems.

**Impact:**
- Fragile typing
- Misleading: Code looks decoupled but isn't

**Recommendation:**
Will be resolved when STRAT-01 is fixed.

**Effort:** Simple (but wait for STRAT-01 fix)

---

## Assessment

**System Health: POOR from Maintenance/Extensibility Perspective**

The Strategy Mode system's architecture is **undermined by a fundamental cross-layer violation** in DesignLibrary.

1. **Violated Separation of Concerns**: Strategy layer has methods that exist only for simulation layer needs
2. **Maintenance Burden**: Every change to Ship ripples into strategy layer
3. **Testing Obstacles**: Cannot unit test strategy features without full simulation layer
4. **Extensibility Blocked**: Hard to support alternative battle systems

**Overall Assessment:**
The system has good structure in most areas (adapters, interfaces, data models), but STRAT-01 is a **blocking issue** for any significant refactoring. Once STRAT-01 is resolved, the system would achieve "Good" health rating.

**Effort to Fix All Issues:** 3-4 days
