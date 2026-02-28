# Dependency Analysis: `_get_column_value` in FleetDataSource

## Summary

`_get_column_value` is a **private method** in `FleetDataSource` that extracts display values for ship columns. It is only called internally through the public `get_cell_value` method, which is part of the `ITableDataSource` interface.

**Key Finding:** The interface can change freely since `_get_column_value` is private and has no external callers.

---

## 1. Callers of `_get_column_value`

### Direct Callers

| Caller | Location | Call Pattern |
|--------|----------|--------------|
| `get_cell_value` | `fleet_data_source.py:93` | `return self._get_column_value(ship, column_id)` |

**Only one internal caller.** The method is called from `get_cell_value()` after ship lookup:

```python
def get_cell_value(self, row_index: int, column_id: str) -> str:
    ship = self.get_ship_at_index(row_index)
    if ship is None:
        return ""
    return self._get_column_value(ship, column_id)
```

### Similar Methods in Other Classes

| Class | Method | File |
|-------|--------|------|
| `EmpireBuildQueueDataSource` | `_get_column_value` | `empire_build_queue_data_source.py:93` |
| `EmpireBuildQueueWindow` | `_get_column_value` | `empire_build_queue_window.py:462` |

These are **separate implementations** with the same pattern, not shared code.

---

## 2. Parameters and Return Values

### Method Signature

```python
def _get_column_value(self, ship: "ShipInstance", col_id: str) -> str:
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `ship` | `ShipInstance` | Ship instance to extract data from |
| `col_id` | `str` | Column identifier (e.g., "serial", "design", "hp_pct") |

### Return Value

- Always returns `str`
- Returns `""` for unknown column IDs
- Returns `""` for image columns (portrait, topdown)
- Returns formatted strings like "75%", "12,500", "Yes", "No", "E:80 F:90 A:100"

### Column ID Usage

The method handles 19 column types:

| Column ID | Return Format | Dependencies |
|-----------|---------------|--------------|
| `portrait`, `topdown` | `""` | None (images handled separately) |
| `serial` | `"SN-0001"` or first 8 chars of instance_id | `ship.get_display_id()`, `ship.instance_id` |
| `design` | Design name or ID | `ship.design_data`, `ship.design_id` |
| `name` | Ship name | `ship.name` |
| `hp_pct` | `"75%"` | `ship.get_hp_percentage()` |
| `status` | `"OK"`, `"DESTROYED"`, `"DERELICT"`, `"DAMAGED"` | `ship.is_alive`, `ship.is_derelict`, `ship.is_damaged()` |
| `speed` | `"5"` | `FleetSpeedCalculator.calculate_ship_speed()` |
| `tonnage` | `"12,500"` | `ship.get_calculated_stats()` |
| `warp` | `"Yes"` / `"No"` | `ShipStatsCalculator.has_warp_capability()` |
| `spaceyard` | `"Yes"` / `"No"` | `FleetCapabilityCalculator.ship_has_spaceyard()` |
| `transport` | `"50/100"` or `"--"` | `ship.get_cargo_capacity()`, `ship.get_current_cargo()` |
| `resources` | `"E:80 F:90 A:100"` or `"--"` | `ship.get_resource_percentage()` |
| `cargo` | `"80"` or `"--"` | `ship.cargo_contents` |
| `can_destroy_planet`, etc. | `"Yes"` / `"No"` | `FleetCapabilityCalculator.ship_has_ability()` |

---

## 3. Interface Stability Assessment

### Can the Interface Change?

**YES** - The interface can change freely because:

1. **Private method** - Prefixed with `_`, indicating internal use only
2. **Single internal caller** - Only called from `get_cell_value()`
3. **No external dependencies** - Not imported or used elsewhere in the codebase
4. **No subclasses override it** - `FleetDataSource` has no subclasses

### What Must Stay Stable?

The **public interface** that must remain stable:

```python
# From ITableDataSource - MUST NOT CHANGE
def get_cell_value(self, row_index: int, column_id: str) -> str:
    """Return string value for a cell."""
```

This is called by `VirtualTable` at line 247:
```python
text = self._data_source.get_cell_value(data_idx, col_id)
```

---

## 4. Side Effects and State Mutations

### Analysis

**The method is PURE** - no side effects or state mutations.

| Aspect | Finding |
|--------|---------|
| Instance state mutation | None |
| Global state mutation | None |
| I/O operations | None |
| External service calls | None |

### Dependencies with Side Effects

The method uses late imports to avoid circular dependencies:

```python
from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
from game.strategy.services.ship_stats_calculator import ShipStatsCalculator
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

These calculator calls are also read-only:
- `FleetSpeedCalculator.calculate_ship_speed(ship)` - Computes speed, no mutation
- `ShipStatsCalculator.has_warp_capability(ship)` - Boolean check, no mutation
- `FleetCapabilityCalculator.ship_has_spaceyard(ship)` - Boolean check, no mutation
- `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` - Boolean check, no mutation

---

## 5. Test Coverage

### Test File

`tests/unit/ui/screens/test_fleet_data_source.py`

### Coverage Summary

| Test Class | Tests | Coverage |
|------------|-------|----------|
| `TestFleetDataSourceColumns` | 3 | Column definitions |
| `TestFleetDataSourceRowCount` | 2 | Row count delegation |
| `TestFleetDataSourceCellValueSerial` | 2 | Serial column |
| `TestFleetDataSourceCellValueDesign` | 2 | Design column |
| `TestFleetDataSourceCellValueName` | 1 | Name column |
| `TestFleetDataSourceCellValueHpPct` | 2 | HP percentage |
| `TestFleetDataSourceCellValueStatus` | 4 | Status states |
| `TestFleetDataSourceCellValueSpeed` | 1 | Speed column |
| `TestFleetDataSourceCellValueTonnage` | 2 | Tonnage column |
| `TestFleetDataSourceCellValueWarp` | 2 | Warp column |
| `TestFleetDataSourceCellValueSpaceyard` | 2 | Spaceyard column |
| `TestFleetDataSourceCellValueTransport` | 2 | Transport column |
| `TestFleetDataSourceCellValueResources` | 2 | Resources column |
| `TestFleetDataSourceCellValueCargo` | 3 | Cargo column |
| `TestFleetDataSourceCellValueSpecialCapabilities` | 3 | Special abilities |
| `TestFleetDataSourceCellValueImageColumns` | 2 | Image handling |
| `TestFleetDataSourceGetCellImage` | 4 | Image retrieval |
| `TestFleetDataSourceGetShipAtIndex` | 2 | Index bounds |

### Test Patterns

Tests call through the **public interface** (`get_cell_value`), not `_get_column_value` directly:

```python
ds = FleetDataSource(view_model)
assert ds.get_cell_value(0, "serial") == "SN-0001"
```

This is the correct approach - tests validate behavior without coupling to implementation.

### Coverage Quality

- **Comprehensive** - All 19 column types have dedicated tests
- **Edge cases covered** - Empty values, fallbacks, None handling
- **Mocking used correctly** - External dependencies patched

---

## 6. Refactoring Implications

### Safe Refactoring Options

Since `_get_column_value` is private and well-tested through the public interface:

1. **Extract helper methods** - Can freely split into smaller methods
2. **Change internal structure** - Dictionary dispatch, strategy pattern, etc.
3. **Rename method** - No external callers to update
4. **Change parameters** - Only need to update `get_cell_value` call site

### Recommended Approach

The current method has **high cyclomatic complexity** due to the long if-elif chain (19 branches). Refactoring options:

| Approach | Complexity Reduction | Effort |
|----------|---------------------|--------|
| Dictionary dispatch | High | Low |
| Extract column handlers | High | Medium |
| Strategy pattern | Medium | High |

### Constraints

1. **Keep return type as `str`** - Required by `ITableDataSource.get_cell_value`
2. **Preserve late imports** - Required to avoid circular dependencies
3. **Maintain test coverage** - Tests already validate all column behaviors

---

## Conclusion

`_get_column_value` is a **safe target for refactoring**:

- Private method with single internal caller
- No external dependencies on its interface
- Pure function with no side effects
- Comprehensive test coverage through public API
- Can be freely restructured without breaking contracts
