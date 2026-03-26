# Correctness Review: FleetDataSource._get_column_value Refactoring

**Project:** PROJ-201
**File:** `game/ui/screens/fleet_data_source.py`
**Reviewer:** Claude Code
**Date:** 2025-02-27

---

## Summary

The refactoring extracts inline column handling logic from `_get_column_value` into individual handler methods, then dispatches to them via a handler dictionary. This review verifies that all behavior is preserved exactly.

**Final Verdict: CORRECT**

All handlers preserve original behavior exactly. No issues found.

---

## Refactoring Overview

### Before (Original)
- Single large `_get_column_value` method with if/elif chain
- Cyclomatic complexity: 29
- All formatting logic inline

### After (Refactored)
- `_get_column_handlers()` returns dispatch dictionary
- `_get_column_value` dispatches to handlers or returns `""`
- Individual `_format_*` methods for each column type
- Cyclomatic complexity: 4

---

## Handler-by-Handler Verification

### 1. Image Columns (`portrait`, `topdown`)

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Check | `if col_id in ("portrait", "topdown")` | `if col_id in ("portrait", "topdown")` | YES |
| Return | `return ""` | `return ""` | YES |

**Verdict:** CORRECT

---

### 2. `_format_serial`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Logic | `display_id = ship.get_display_id(); return display_id if display_id else ship.instance_id[:8]` | Same | YES |
| Fallback | `ship.instance_id[:8]` | `ship.instance_id[:8]` | YES |

**Verdict:** CORRECT

---

### 3. `_format_design`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Logic | `ship.design_data.get("name", ship.design_id)` | `ship.design_data.get("name", ship.design_id)` | YES |
| Fallback | `ship.design_id` | `ship.design_id` | YES |

**Verdict:** CORRECT

---

### 4. `_format_name`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Logic | `return ship.name` | `return ship.name` | YES |

**Verdict:** CORRECT

---

### 5. `_format_hp_pct`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Format string | `f"{ship.get_hp_percentage() * 100:.0f}%"` | `f"{ship.get_hp_percentage() * 100:.0f}%"` | YES |

**Verdict:** CORRECT

---

### 6. `_format_status`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Priority order | DESTROYED > DERELICT > DAMAGED > OK | DESTROYED > DERELICT > DAMAGED > OK | YES |
| Check 1 | `if not ship.is_alive: return "DESTROYED"` | Same | YES |
| Check 2 | `elif ship.is_derelict: return "DERELICT"` | Same | YES |
| Check 3 | `elif ship.is_damaged(): return "DAMAGED"` | Same | YES |
| Default | `return "OK"` | `else: return "OK"` | YES |

**Note:** Original called `self._format_status(ship)` from the elif chain. The handler itself existed before and is unchanged.

**Verdict:** CORRECT

---

### 7. `_format_speed`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Late import | `from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator` | Same (with comment) | YES |
| Logic | `speed = FleetSpeedCalculator.calculate_ship_speed(ship); return str(speed)` | Same | YES |

**Verdict:** CORRECT

---

### 8. `_format_tonnage`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Mass retrieval | `ship.get_calculated_stats().get("mass", 0)` | Same | YES |
| Format string | `f"{mass:,.0f}"` | `f"{mass:,.0f}"` | YES |

**Note:** Format uses comma thousands separator and zero decimal places.

**Verdict:** CORRECT

---

### 9. `_format_warp`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Late import | `from game.strategy.services.ship_stats_calculator import ShipStatsCalculator` | Same (with comment) | YES |
| Logic | `"Yes" if ShipStatsCalculator.has_warp_capability(ship) else "No"` | Same | YES |

**Verdict:** CORRECT

---

### 10. `_format_spaceyard`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Late import | `from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator` | Same (with comment) | YES |
| Logic | `"Yes" if FleetCapabilityCalculator.ship_has_spaceyard(ship) else "No"` | Same | YES |

**Verdict:** CORRECT

---

### 11. `_format_transport`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Capacity | `ship.get_cargo_capacity("passengers")` | Same | YES |
| Current | `ship.get_current_cargo("passengers")` | Same | YES |
| Format | `f"{current}/{capacity}" if capacity > 0 else "--"` | Same | YES |

**Verdict:** CORRECT

---

### 12. `_format_resources`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Resource order | ENERGY, FUEL, AMMO | ENERGY, FUEL, AMMO | YES |
| Abbreviations | E, F, A | E, F, A | YES |
| Format | `f"{abbrev}:{int(pct * 100)}"` | Same | YES |
| Condition | `pct is not None and pct >= 0` | Same | YES |
| Empty case | `"--"` | `"--"` | YES |

**Note:** Original called `self._format_resources(ship)` from the elif chain. The handler itself existed before and is unchanged.

**Verdict:** CORRECT

---

### 13. `_format_cargo`

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Sum logic | `sum(ship.cargo_contents.values()) if ship.cargo_contents else 0` | Same | YES |
| Display | `str(total) if total > 0 else "--"` | Same | YES |

**Verdict:** CORRECT

---

### 14. `_format_capability` (Special Capability Columns)

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Late import | `from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator` | Same (with comment) | YES |
| Ability lookup | `SPECIAL_CAPABILITY_COLUMNS[col_id]` | Same | YES |
| Logic | `"Yes" if FleetCapabilityCalculator.ship_has_ability(ship, ability_name) else "No"` | Same | YES |

**Note:** This is the only handler that requires `col_id` as an additional parameter, which is why it's handled separately from the dispatch dict.

**Verdict:** CORRECT

---

### 15. Unknown Columns

| Aspect | Original | Refactored | Match |
|--------|----------|------------|-------|
| Final return | `return ""` | `return ""` | YES |

**Verdict:** CORRECT

---

## Key Invariants Verified

| Invariant | Status |
|-----------|--------|
| Return type is always `str` | VERIFIED - All handlers return str |
| Image columns return `""` | VERIFIED - Checked first, returns `""` |
| Unknown columns return `""` | VERIFIED - Default fallback is `""` |
| Status priority: DESTROYED > DERELICT > DAMAGED > OK | VERIFIED - If/elif chain preserved |
| Late imports stay inside handler methods | VERIFIED - All 4 late imports retained with comments |
| Format strings exact (e.g., `"{mass:,.0f}"`) | VERIFIED - All format strings identical |

---

## Edge Cases Analysis

1. **Null/empty `display_id`**: Handled by `_format_serial` fallback to `instance_id[:8]`
2. **Missing `name` in `design_data`**: Handled by `_format_design` fallback to `design_id`
3. **Zero capacity for transport**: Returns `"--"` correctly
4. **Empty `cargo_contents`**: Returns `"--"` correctly
5. **No resources**: Returns `"--"` correctly
6. **Resource percentage is None or negative**: Skipped in loop, handled correctly

---

## Dispatch Mechanism Analysis

The refactored `_get_column_value` uses a three-tier dispatch:

1. **Image columns** - Direct check, return `""`
2. **Special capability columns** - Check against `SPECIAL_CAPABILITY_COLUMNS`, call `_format_capability(ship, col_id)`
3. **Standard columns** - Lookup in handler dict, call handler or return `""`

This preserves the exact behavior of the original if/elif chain while reducing cyclomatic complexity from 29 to 4.

---

## Conclusion

All extracted handlers preserve the original behavior exactly. The refactoring is a pure mechanical extraction with no behavioral changes. Late imports are correctly preserved inside handler methods to avoid circular import issues.

**Final Verdict: CORRECT**
