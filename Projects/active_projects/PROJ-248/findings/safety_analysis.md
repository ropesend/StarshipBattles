# Safety Analysis: filter_ships Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** 36 (Grade F)
**Function Length:** 99 lines

---

## 1. Function Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a dictionary of boolean filter flags. It handles multiple filter categories:

1. **Warp Capability** - `show_warp_capable`, `show_not_warp_capable`
2. **Spaceyard Capability** - `show_has_spaceyard`, `show_no_spaceyard`
3. **Cargo Contents** - `show_has_cargo`, `show_no_cargo`
4. **Special Capabilities** - Dynamic filters from `SPECIAL_CAPABILITY_COLUMNS` (e.g., `can_destroy_planet`, `can_open_warp`, etc.)
5. **Ship Status** - `show_destroyed`, `show_derelict`, `show_damaged`, `show_undamaged`

---

## 2. Edge Cases and Error Handling Paths

### 2.1 Empty Input Handling
- **Empty ships list:** Returns empty list (safe - loop is skipped)
- **Empty filter_state dict:** All filters default to `True` via `.get()` with default values

### 2.2 Missing Filter Keys
The function uses `.get(key, True)` consistently, defaulting to showing all ships when a filter key is missing. This is a **safe default**.

### 2.3 Cargo Edge Cases
```python
has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
```
- Handles `None` cargo_contents (via `bool()`)
- Handles empty dict `{}`
- Handles dict with all zero values `{'minerals': 0}`

### 2.4 Ship State Priority
The function processes ship status in a specific order that affects classification:
1. **Destroyed** (not alive) - checked first
2. **Derelict** - checked second (note: derelict implies damaged)
3. **Damaged** - checked third
4. **Undamaged** - fallthrough case

This order is **critical** - changing it would alter which filter category captures each ship.

---

## 3. Test Coverage Analysis

### 3.1 Existing Test Classes in `test_fleet_report_filters.py`

| Test Class | Coverage |
|------------|----------|
| `TestFilterShips` | Basic status filters (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | Warp capability filtering |
| `TestFilterShipsSpaceyard` | Spaceyard filtering |
| `TestFilterShipsCargo` | Cargo filtering (including zero-value edge case) |
| `TestSpecialCapabilityFilter` | Special ability filtering |

### 3.2 Missing Test Coverage (CRITICAL)

The following edge cases **lack explicit tests**:

1. **Empty ships list** - No test for `filter_ships([], filter_state)`
2. **Empty filter_state** - No test for `filter_ships(ships, {})`
3. **Combined filters** - No tests for multiple filter categories active simultaneously
4. **All filters disabled** - No test where all show_* flags are False (should return empty)
5. **Mutually exclusive status ordering** - No test verifying that a destroyed derelict is classified as destroyed, not derelict
6. **Ship that is both damaged AND derelict** - Current logic: derelict takes precedence
7. **None cargo_contents attribute** - Tests use `{}` but not `None`
8. **Filter state with extraneous keys** - Behavior with unknown keys

---

## 4. Invariants That Must Be Preserved

### 4.1 Behavioral Invariants

| ID | Invariant | Risk if Broken |
|----|-----------|----------------|
| INV-1 | Ship status checks follow order: destroyed -> derelict -> damaged -> undamaged | Ships miscategorized, wrong filters applied |
| INV-2 | Default filter value is `True` (show all by default) | Ships unexpectedly hidden |
| INV-3 | Warp/spaceyard checks only performed when at least one filter is off | Performance degradation |
| INV-4 | Special capability loop can break early via `_skip` flag | Performance change if removed |
| INV-5 | Cargo check uses sum > 0, not just bool(dict) | Zero-cargo ships miscategorized |
| INV-6 | Return value preserves input order (no reordering) | Sorting assumptions broken |

### 4.2 External Dependencies

| Dependency | Import Location | Usage |
|------------|-----------------|-------|
| `ShipStatsCalculator.has_warp_capability` | Top-level import | Warp filter |
| `FleetCapabilityCalculator.ship_has_spaceyard` | Lazy import (line 159) | Spaceyard filter |
| `FleetCapabilityCalculator.ship_has_ability` | Lazy import (line 185) | Special capability filter |
| `SPECIAL_CAPABILITY_COLUMNS` | Top-level import | Column-to-ability mapping |

---

## 5. Risk Areas for Refactoring

### 5.1 HIGH RISK

| Area | Risk Description |
|------|------------------|
| Status check ordering | Lines 196-220 have specific sequencing that affects categorization. Refactoring into separate functions must preserve this order. |
| Early continue statements | Six `continue` statements control flow. Converting to filter predicates must replicate exact behavior. |
| _skip flag pattern | The special capability loop uses a flag variable and break. Converting to a generator/any() must handle the same short-circuit logic. |

### 5.2 MEDIUM RISK

| Area | Risk Description |
|------|------------------|
| Lazy imports | Lines 159 and 185 have lazy imports to avoid circular dependencies. Moving code could trigger import cycles. |
| Filter state key derivation | Line 182 derives keys via `col_id.replace('can_', 'no_', 1)`. This pattern must be preserved exactly. |
| Default value handling | All `.get(key, True)` calls must remain consistent. |

### 5.3 LOW RISK

| Area | Risk Description |
|------|------------------|
| Result list accumulation | Simple append pattern, easy to convert to list comprehension if needed. |
| Boolean logic | Filter conditions are straightforward AND/NOT patterns. |

---

## 6. Recommended Tests Before Refactoring

### 6.1 MUST ADD (Critical Path)

```python
def test_filter_empty_ships_list():
    """Empty list returns empty list."""
    result = filter_ships([], {'show_damaged': True})
    assert result == []

def test_filter_empty_filter_state():
    """Empty filter state shows all ships (defaults to True)."""
    ships = [make_mock_ship(), make_mock_ship(is_damaged=True)]
    result = filter_ships(ships, {})
    assert len(result) == 2

def test_filter_all_disabled_returns_empty():
    """All filters False returns no ships."""
    ships = [make_mock_ship()]
    filter_state = {
        'show_damaged': False,
        'show_undamaged': False,
        'show_derelict': False,
        'show_destroyed': False,
    }
    result = filter_ships(ships, filter_state)
    assert len(result) == 0

def test_destroyed_ship_not_matched_as_derelict():
    """Destroyed ship is classified as destroyed, not derelict."""
    ship = make_mock_ship(is_alive=False, is_derelict=True)
    filter_state = {
        'show_destroyed': False,
        'show_derelict': True,
    }
    result = filter_ships([ship], filter_state)
    assert len(result) == 0  # Should be filtered as destroyed

def test_derelict_ship_not_matched_as_damaged():
    """Derelict ship is classified as derelict, not damaged."""
    ship = make_mock_ship(is_derelict=True, is_damaged=True)
    filter_state = {
        'show_derelict': False,
        'show_damaged': True,
    }
    result = filter_ships([ship], filter_state)
    assert len(result) == 0  # Should be filtered as derelict
```

### 6.2 SHOULD ADD (Coverage Gaps)

```python
def test_combined_warp_and_status_filters():
    """Warp filter combines correctly with status filter."""
    warp_damaged = make_mock_ship(is_damaged=True, warp_tonnage=1500)
    warp_healthy = make_mock_ship(warp_tonnage=1500)
    no_warp = make_mock_ship(warp_tonnage=None)

    filter_state = {
        'show_warp_capable': True,
        'show_not_warp_capable': False,
        'show_damaged': False,
        'show_undamaged': True,
    }
    result = filter_ships([warp_damaged, warp_healthy, no_warp], filter_state)
    assert len(result) == 1
    assert result[0] == warp_healthy

def test_filter_with_none_cargo_contents():
    """Ship with None cargo_contents handled gracefully."""
    ship = make_mock_ship()
    ship.cargo_contents = None  # Explicitly None
    filter_state = {'show_no_cargo': True, 'show_has_cargo': False}
    result = filter_ships([ship], filter_state)
    assert len(result) == 1  # None treated as no cargo

def test_order_preserved():
    """Filter preserves input order of ships."""
    ships = [make_mock_ship(serial=i) for i in [5, 3, 7, 1]]
    result = filter_ships(ships, {})
    assert [s.serial for s in result] == [5, 3, 7, 1]
```

---

## 7. Refactorability Assessment

### 7.1 Verdict: REFACTORABLE with CAUTION

The function is suitable for refactoring, but requires careful attention to:

1. **Add missing tests FIRST** - The tests listed in Section 6.1 are critical
2. **Preserve status check ordering** - Extract to helper but maintain sequence
3. **Maintain lazy imports** - Do not move imports to top level without checking for cycles
4. **Validate all invariants** - Run full test suite after each refactoring step

### 7.2 Recommended Refactoring Approach

1. **Extract filter predicates** - Create small functions for each filter category:
   - `_passes_warp_filter(ship, filter_state) -> bool`
   - `_passes_spaceyard_filter(ship, filter_state) -> bool`
   - `_passes_cargo_filter(ship, filter_state) -> bool`
   - `_passes_special_capability_filter(ship, filter_state) -> bool`
   - `_passes_status_filter(ship, filter_state) -> bool`

2. **Compose predicates** - Combine into a single filter:
   ```python
   def filter_ships(ships, filter_state):
       return [s for s in ships if _passes_all_filters(s, filter_state)]
   ```

3. **Status filter MUST remain separate** - The status check has mutually exclusive categories and cannot be a simple predicate.

### 7.3 Do NOT Attempt

- Converting to a single list comprehension (too complex)
- Parallelizing (filter order matters for status)
- Caching filter results (filter_state changes frequently)

---

## 8. Final Recommendation

| Decision | Rationale |
|----------|-----------|
| **PROCEED with refactoring** | High complexity (CC=36) justifies effort |
| **Add tests first** | 5 critical tests missing (Section 6.1) |
| **Incremental approach** | Extract one filter category at a time |
| **Run full suite after each step** | 6246 tests provide safety net |

**Risk Level:** MEDIUM - Well-tested function with clear invariants, but status ordering requires careful handling.
