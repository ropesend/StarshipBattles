# Safety Analysis: `_get_column_value` Refactoring

**Target File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_data_source.py`
**Function:** `_get_column_value(self, ship: ShipInstance, col_id: str) -> str`
**Current Cyclomatic Complexity:** 29
**Lines:** 130-233 (104 lines)

---

## 1. Function Overview

The `_get_column_value` method is a dispatch function that returns a string representation of a ship attribute based on the column ID. It handles 19 different column types:

| Category | Column IDs | Logic Type |
|----------|-----------|------------|
| Image columns | `portrait`, `topdown` | Return empty string (images handled separately) |
| Direct attributes | `name` | Simple property access |
| Fallback logic | `serial`, `design` | Primary value with fallback |
| Computed format | `hp_pct`, `tonnage` | Format numeric value |
| Status logic | `status` | Multi-condition evaluation |
| External service | `speed`, `warp`, `spaceyard` | Late import + service call |
| Cargo/transport | `transport`, `resources`, `cargo` | Conditional formatting |
| Special abilities | 5 `can_*` columns | Lookup via SPECIAL_CAPABILITY_COLUMNS |

---

## 2. Test Coverage Analysis

### Covered Cases (Test File: `tests/unit/ui/screens/test_fleet_data_source.py`)

| Column | Tests | Coverage Notes |
|--------|-------|----------------|
| `serial` | 2 tests | Primary display_id + fallback to instance_id[:8] |
| `design` | 2 tests | design_data["name"] + fallback to design_id |
| `name` | 1 test | Direct attribute access |
| `hp_pct` | 2 tests | 75% and 100% formatting |
| `status` | 4 tests | OK, DESTROYED, DERELICT, DAMAGED states |
| `speed` | 1 test | Mocked calculator call |
| `tonnage` | 2 tests | Formatted with comma, zero case |
| `warp` | 2 tests | Yes/No via mocked calculator |
| `spaceyard` | 2 tests | Yes/No via mocked calculator |
| `transport` | 2 tests | current/capacity, "--" for no capacity |
| `resources` | 2 tests | E:xx F:xx A:xx format, "--" for none |
| `cargo` | 3 tests | Total cargo, empty dict, None cargo_contents |
| `can_*` | 3 tests | Yes, No, loop over all 5 columns |
| `portrait` | 1 test | Returns empty string |
| `topdown` | 1 test | Returns empty string |

**Total: 30 tests covering the public interface via `get_cell_value()`**

### Missing Test Cases

1. **Unknown column ID** - No test for calling with an invalid/unknown column ID
   - Current behavior: Returns `""` (empty string) - line 233
   - Risk: Low - fail-safe default behavior

2. **Row out of bounds** - Tested via `get_ship_at_index` returning `None`
   - `get_cell_value` calls `get_ship_at_index` which returns `None`
   - Then returns `""` on line 91 before calling `_get_column_value`
   - Coverage: Adequate

3. **Edge cases in resources**:
   - Negative percentage: Not tested (code checks `pct >= 0`)
   - Partial resources (only some types): Not tested

---

## 3. Invariants That Must Be Preserved

### Critical Invariants

1. **Return type is always `str`** - The interface contract requires string return
2. **Never raise exceptions** - Function must gracefully handle all inputs
3. **Image columns return empty string** - `portrait`/`topdown` must return `""` for text value
4. **Unknown columns return empty string** - Default fallback behavior
5. **Late imports remain inside branches** - Circular import protection

### Column-Specific Invariants

| Column | Invariant |
|--------|-----------|
| `serial` | Fallback to `instance_id[:8]` if no display_id |
| `design` | Fallback to `design_id` if no name in design_data |
| `hp_pct` | Format as `"{pct*100:.0f}%"` |
| `status` | Priority: DESTROYED > DERELICT > DAMAGED > OK |
| `tonnage` | Format with comma separator: `"{mass:,.0f}"` |
| `transport` | Show `"--"` when capacity is 0 |
| `resources` | Show `"--"` when no resources, abbreviations E/F/A |
| `cargo` | Show `"--"` when empty/None |
| `can_*` | Lookup ability name from SPECIAL_CAPABILITY_COLUMNS |

---

## 4. Risk Assessment

### High Risk Areas

1. **Status column logic (lines 156-164)**
   - Multi-condition with specific priority ordering
   - Breaking change risk: Status priority reversal
   - Mitigation: 4 explicit tests cover all branches

2. **Late imports (lines 167-191, 221-230)**
   - 4 different late imports for circular import avoidance
   - Risk: Import path changes break at runtime
   - Mitigation: Tests mock these successfully

3. **Resources formatting (lines 202-214)**
   - Complex iteration with conditional inclusion
   - Risk: Format string changes, ordering changes
   - Mitigation: Test verifies all three abbreviations present

### Medium Risk Areas

1. **SPECIAL_CAPABILITY_COLUMNS lookup (lines 220-231)**
   - Depends on external dict consistency
   - Risk: Dict key mismatch with column IDs
   - Mitigation: Test iterates all 5 columns

2. **Fallback chains (serial, design)**
   - Two-step evaluation with conditional
   - Risk: Incorrect truthiness check
   - Mitigation: Both paths tested

### Low Risk Areas

1. **Simple property access** (`name`)
2. **Image column guards** (`portrait`, `topdown`)
3. **Default return** (line 233)

---

## 5. Refactoring Pattern Analysis

### Current Structure: Long If-Elif Chain

```python
if col_id in ("portrait", "topdown"):
    return ""
elif col_id == "serial":
    # ...
elif col_id == "design":
    # ...
# ... 15 more branches
return ""
```

### Is This a Clean Dispatch Table Pattern?

**No.** This is NOT a clean dispatch table because:

1. **Variable logic per branch** - Some branches are 1 line, others are 10+ lines
2. **Late imports** - Cannot use a simple dict lookup without restructuring imports
3. **Multiple return value types** - Some format strings, some call services, some use lookups
4. **Stateful dependencies** - Several branches need `self` access indirectly

### Recommended Refactoring Approach

**Strategy Map Pattern with Handler Functions:**

```python
def _get_column_value(self, ship: ShipInstance, col_id: str) -> str:
    handler = self._column_handlers.get(col_id)
    if handler:
        return handler(self, ship)
    return ""
```

With individual handler methods:
- `_get_serial_value(ship) -> str`
- `_get_status_value(ship) -> str`
- `_get_resources_value(ship) -> str`
- etc.

**Advantages:**
- Each handler is testable in isolation
- Cyclomatic complexity distributed across methods
- Late imports stay contained in their handlers
- Easy to add/remove columns

---

## 6. Pre-Refactoring Checklist

### Required Before Starting

- [x] All 30 existing tests pass
- [x] Function behavior documented
- [x] Invariants identified
- [x] Risk areas mapped

### Recommended Additions

- [ ] Add test for unknown column ID returning `""`
- [ ] Add test for resources with partial data (e.g., only ENERGY)
- [ ] Add explicit tests for status priority (DESTROYED checked before DERELICT)

### Not Required

- Edge cases in calculators (mocked in tests)
- Image handling (separate method `get_cell_image`)
- Row bounds checking (handled in `get_cell_value` before calling `_get_column_value`)

---

## 7. Final Recommendation

### REFACTOR

**Rationale:**

1. **High test coverage (30 tests)** - All column types have at least one test
2. **Clear invariants** - Behavior is well-defined and documented
3. **Safe default behavior** - Unknown columns return empty string
4. **Clean extraction path** - Handler method pattern is straightforward
5. **CC=29 is genuinely high** - Not a simple dispatch table, actual complexity

**Suggested Approach:**

1. Extract each column handler to a private method
2. Create column handler registry dict
3. Update `_get_column_value` to dispatch via registry
4. Run tests after each extraction (incremental)
5. Target final CC < 5 for the dispatch method

**Risk Level:** Low-Medium

The existing test suite provides a strong safety net. The refactoring is mechanical (extract method) rather than behavioral, reducing the chance of subtle bugs. The main risk is accidentally changing status priority or format strings, both of which have explicit tests.
