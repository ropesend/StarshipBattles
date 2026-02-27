# Structure Analysis: `_get_column_value`

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_data_source.py`
**Lines:** 130-233
**Current Cyclomatic Complexity:** High (14+ branches in a single if-elif chain)

---

## 1. Branches/Conditions Contributing Most to Complexity

The function is a 104-line if-elif chain with 14 branches. The branches contributing most to complexity are:

### High Complexity Branches

| Branch | Lines | Why It's Complex |
|--------|-------|------------------|
| `status` | 156-164 | **4 nested conditions** - checks `is_alive`, `is_derelict`, `is_damaged()` with nested if-elif-else |
| `resources` | 202-214 | **Loop + conditional** - iterates over resource types, checks `pct is not None and pct >= 0` |
| `transport` | 197-200 | **2 method calls + conditional expression** |
| `warp` | 179-185 | **Late import + ternary** |
| `spaceyard` | 187-195 | **Late import + ternary** |
| `SPECIAL_CAPABILITY_COLUMNS` | 220-231 | **Late import + dictionary lookup + ternary** |

### Low Complexity Branches (simple lookups)

- `portrait/topdown` (140-141) - simple return ""
- `serial` (143-145) - conditional expression
- `design` (147-148) - dict get with fallback
- `name` (150-151) - simple property access
- `hp_pct` (153-154) - formatted string
- `speed` (166-173) - late import + method call
- `tonnage` (175-177) - dict get + format
- `cargo` (216-218) - sum + conditional

---

## 2. Nested Conditionals That Could Be Flattened

### Primary Nesting Issue: `status` Branch (lines 156-164)

```python
elif col_id == "status":
    if not ship.is_alive:
        return "DESTROYED"
    elif ship.is_derelict:
        return "DERELICT"
    elif ship.is_damaged():
        return "DAMAGED"
    else:
        return "OK"
```

**Problem:** 4-level decision tree inside an elif branch.

**Refactoring options:**
1. Extract to `_get_status_display(ship)` method
2. Use a status priority lookup pattern

### Secondary Nesting: `resources` Branch (lines 202-214)

```python
elif col_id == "resources":
    parts = []
    resource_abbrevs = [...]
    for res_type, abbrev in resource_abbrevs:
        pct = ship.get_resource_percentage(res_type)
        if pct is not None and pct >= 0:
            parts.append(...)
    return " ".join(parts) if parts else "--"
```

**Problem:** Loop with conditional inside a branch.

**Refactoring option:** Extract to `_format_resources(ship)` method

---

## 3. Early Returns That Could Simplify Logic

The function already uses early returns for each branch. However, the structure could benefit from:

### Opportunity 1: Guard Clause at Top

Currently line 140-141:
```python
if col_id in ("portrait", "topdown"):
    return ""  # Images handled separately
```

This is already a guard clause. Good pattern.

### Opportunity 2: Default Return at Bottom

Line 233:
```python
return ""
```

This is the implicit "unknown column" case. Could be made explicit:
```python
# Unknown column - return empty string
return ""
```

### Opportunity 3: Dispatch Table Pattern

Replace entire if-elif chain with a dispatch dictionary:
```python
handlers = {
    "serial": self._get_serial_value,
    "design": self._get_design_value,
    ...
}
handler = handlers.get(col_id)
return handler(ship) if handler else ""
```

This would eliminate all branching complexity from this function.

---

## 4. Repeated Patterns That Could Be Extracted

### Pattern A: Late Import + Boolean Display (3 occurrences)

**Lines 179-185 (warp), 187-195 (spaceyard), 220-231 (special capabilities)**

```python
# INTENTIONAL LATE IMPORT: Avoid circular import
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
return "Yes" if ShipStatsCalculator.has_warp_capability(ship) else "No"
```

**Extraction:** Create `_format_yes_no(condition: bool) -> str` helper.

Better yet, create a capability checker that handles all boolean capability columns:
```python
def _get_capability_value(self, ship, capability_type: str) -> str:
    # Handle late imports internally
    has_capability = self._check_capability(ship, capability_type)
    return "Yes" if has_capability else "No"
```

### Pattern B: Conditional Formatting with "--" Fallback (3 occurrences)

**Lines 200, 214, 218:**
```python
return f"{current}/{capacity}" if capacity > 0 else "--"
return " ".join(parts) if parts else "--"
return str(total) if total > 0 else "--"
```

**Extraction:** Not worth extracting due to different conditions. The pattern is consistent enough to be readable.

### Pattern C: Dict Get with Fallback (2 occurrences)

**Lines 148, 176:**
```python
ship.design_data.get("name", ship.design_id)
ship.get_calculated_stats().get("mass", 0)
```

These are standard dict access patterns - no extraction needed.

---

## 5. Data Transformations That Could Be Separated

### Pure Data Lookups (No Side Effects)

These branches perform pure data extraction and could be moved to a separate layer:

| Column ID | Pure Transformation |
|-----------|---------------------|
| `serial` | `ship.get_display_id() or ship.instance_id[:8]` |
| `design` | `ship.design_data.get("name", ship.design_id)` |
| `name` | `ship.name` |
| `hp_pct` | `f"{ship.get_hp_percentage() * 100:.0f}%"` |
| `tonnage` | `f"{ship.get_calculated_stats().get('mass', 0):,.0f}"` |

### Stateful/Complex Transformations

These require imports or complex logic:

| Column ID | Reason |
|-----------|--------|
| `status` | Multi-condition logic |
| `speed` | Requires FleetSpeedCalculator import |
| `warp` | Requires ShipStatsCalculator import |
| `spaceyard` | Requires FleetCapabilityCalculator import |
| `resources` | Loop iteration |
| `transport` | Multiple method calls |
| `cargo` | Collection sum |
| `SPECIAL_CAPABILITY_COLUMNS` | Dynamic ability check |

### Recommendation: Two-Tier Architecture

```
_get_column_value(ship, col_id)
    |
    +-- Simple columns: Direct property access (inline or small helper)
    |
    +-- Complex columns: Dedicated formatter methods
        +-- _format_status(ship)
        +-- _format_resources(ship)
        +-- _get_capability_display(ship, col_id)
```

---

## Summary of Recommended Refactorings

| Priority | Refactoring | Impact |
|----------|-------------|--------|
| **High** | Extract `_format_status(ship)` | Removes nested conditionals |
| **High** | Extract `_format_resources(ship)` | Removes loop from main function |
| **Medium** | Consolidate capability checks into `_get_capability_display()` | Removes 4 similar branches |
| **Medium** | Consider dispatch table pattern | Eliminates entire if-elif chain |
| **Low** | Extract simple formatters | Cleaner but adds method count |

The highest-value refactoring is consolidating the capability-checking branches (warp, spaceyard, special capabilities) since they all follow the same pattern: late import, boolean check, Yes/No display.
