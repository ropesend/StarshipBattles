# Safety Analysis: filter_ships

**Target:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py` (lines 124-222)

**Function signature:**
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]
```

---

## Edge Cases

### 1. Empty Input List
- **Line 141-142:** Function iterates over `ships` list; empty list returns empty result (implicit via loop)
- No explicit empty check, but behavior is correct

### 2. Missing Filter Keys (Default Behavior)
- **Lines 144-145, 156-157, 167-168, 181-183, 198, 205, 212, 218:** All filter state lookups use `.get()` with `True` as default
- Missing keys are treated as "show all" (permissive default)
- This is intentional - partial filter states work correctly

### 3. Ship State Priority (Mutually Exclusive Categories)
- **Lines 196-220:** Status filters are checked in priority order:
  1. `is_alive == False` -> Destroyed (line 197)
  2. `is_derelict == True` -> Derelict (line 204)
  3. `is_damaged() == True` -> Damaged (line 211)
  4. Otherwise -> Undamaged (line 218)
- **Critical:** A derelict ship is NOT filtered as "damaged" even if `is_damaged()` returns True
- This hierarchy ensures each ship falls into exactly one category

### 4. Cargo Contents Edge Cases
- **Line 170:** Checks `bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0`
- Handles: `None` cargo_contents, empty dict `{}`, dict with all zeros `{'minerals': 0}`
- All treated as "no cargo"

### 5. Special Capability Filter Key Derivation
- **Lines 178-183:** Filter keys derived dynamically from column IDs
  - `col_id = 'can_destroy_planet'` -> `show_can_destroy_planet` (has ability)
  - `no_key = 'no_destroy_planet'` -> `show_no_destroy_planet` (lacks ability)
- Uses `col_id.replace('can_', 'no_', 1)` which only replaces FIRST occurrence

---

## Invariants

### Pre-conditions
1. `ships` must be iterable (list of ShipInstance objects)
2. `filter_state` must be a dict (but can be empty or partial)
3. Each ship must have these attributes/methods:
   - `is_alive` (bool property)
   - `is_derelict` (bool property)
   - `is_damaged()` (method returning bool)
   - `cargo_contents` (dict or None)

### Post-conditions
1. **Return value is always a list** (never None)
2. **Original list is not mutated** (creates new `result` list)
3. **Order is preserved** (ships appear in same relative order as input)
4. **Each ship appears at most once** (no duplicates introduced)
5. **All returned ships were in the input** (no ships created)

### Filter Logic Invariants
1. **Both filters True = show all** in that category
2. **Both filters False = show none** in that category (blocks all ships)
3. **Short-circuit on first failed filter** - once a ship is `continue`d, it's excluded
4. **Status filters are mutually exclusive** - a ship matches exactly one status category

---

## Risk Areas

### HIGH RISK

1. **Import Order in Loops (Lines 159, 170, 185)**
   - `FleetCapabilityCalculator` is imported inside the loop body
   - While Python caches imports, this is inefficient for large ship lists
   - **Refactoring risk:** Moving import outside loop could change behavior if import fails mid-iteration

2. **Status Filter Priority Logic (Lines 196-220)**
   - The cascading if/continue/append pattern is subtle
   - **Refactoring risk:** Easy to accidentally change the order or break the mutual exclusivity
   - Each status category MUST `continue` after appending to prevent falling through

3. **Special Capability Loop Break Logic (Lines 177-194)**
   - Uses `_skip` flag with inner loop break
   - **Refactoring risk:** Changing to list comprehension or generator could break early-exit behavior

### MEDIUM RISK

4. **Filter Key Naming Convention (Lines 181-183)**
   - Derives "no_" variant from "can_" variant using string replacement
   - **Refactoring risk:** If column IDs change naming convention, filter matching breaks silently

5. **Cargo Sum Evaluation (Line 170)**
   - `sum(ship.cargo_contents.values())` assumes all values are numeric
   - **Refactoring risk:** Adding non-numeric cargo types would cause TypeError

### LOW RISK

6. **Multiple Continue Statements**
   - 8 different `continue` statements scattered through the function
   - **Refactoring risk:** Adding new filter categories requires understanding all exit points

---

## Test Coverage Assessment

### Existing Tests (in `test_fleet_report_filters.py`)

| Test Class | Coverage |
|------------|----------|
| `TestFilterShips` | Basic damaged/undamaged/derelict/destroyed filters |
| `TestFilterShipsWarp` | Warp capable/not capable filters |
| `TestFilterShipsSpaceyard` | Spaceyard has/no filters |
| `TestFilterShipsCargo` | Cargo has/no filters including zero values |
| `TestSpecialCapabilityFilter` | DestroyPlanet ability filters |

### Test Count: ~25 tests directly for filter_ships

### MISSING Test Coverage

1. **Empty ships list** - No explicit test for `filter_ships([], filter_state)`

2. **All filters disabled** - No test where `show_damaged=False, show_undamaged=False, etc.` (should return empty)

3. **Partial filter state** - No test with minimal filter_state dict (relies on defaults)

4. **Multiple special capabilities** - Tests only cover `can_destroy_planet`, not other special caps

5. **Filter combinations**:
   - Warp + Status combination (e.g., warp-capable damaged ships)
   - Spaceyard + Cargo combination
   - All filters simultaneously

6. **Ship with `cargo_contents = None`** - Tested implicitly but no explicit test

7. **Derelict ship that is also damaged** - Tests don't verify derelict takes priority over damaged

8. **Order preservation** - No test verifying output order matches input order

9. **Large ship list performance** - No benchmark or stress test

---

## Refactorability Assessment

### Verdict: SAFE TO REFACTOR with caution

**Positive factors:**
- Excellent test coverage for core functionality (~25 dedicated tests)
- Clear input/output contract (List -> List)
- No side effects (pure filtering function)
- Well-documented behavior in docstring

**Risk factors:**
- Complex branching logic with 8 continue statements
- Status priority hierarchy must be preserved
- Late imports inside loop
- Filter key derivation from column IDs

### Recommended Refactoring Approaches

1. **Extract filter predicates** - Each filter category (warp, spaceyard, cargo, status, special) could become a separate predicate function
2. **Replace loop with filter chain** - Use `itertools` or comprehensions with explicit predicates
3. **Move imports to top** - Extract late imports outside the function

### Should NOT be Skipped

This function is a good refactoring candidate because:
- It has strong test coverage
- It has clear boundaries and a pure interface
- The complexity (99 lines, 8 continues) warrants simplification
- No external state dependencies

---

## Required Pre-Refactoring Actions

### Tests to Add BEFORE Refactoring

```python
# 1. Empty input list
def test_filter_empty_ships_returns_empty():
    result = filter_ships([], {'show_damaged': True, 'show_undamaged': True})
    assert result == []

# 2. Partial filter state (minimal dict)
def test_filter_with_empty_filter_state_shows_all():
    ships = [make_mock_ship(), make_mock_ship(is_damaged=True)]
    result = filter_ships(ships, {})
    assert len(result) == 2

# 3. All filters disabled returns empty
def test_all_filters_disabled_returns_empty():
    ships = [make_mock_ship()]
    filter_state = {
        'show_damaged': False,
        'show_undamaged': False,
        'show_derelict': False,
        'show_destroyed': False,
    }
    result = filter_ships(ships, filter_state)
    assert len(result) == 0

# 4. Derelict priority over damaged
def test_derelict_priority_over_damaged():
    ship = make_mock_ship(is_derelict=True, is_damaged=True)
    filter_state = {
        'show_damaged': False,
        'show_derelict': True,
    }
    result = filter_ships([ship], filter_state)
    assert len(result) == 1  # Should pass as derelict, not blocked as damaged

# 5. Order preservation
def test_filter_preserves_order():
    ships = [make_mock_ship(serial=3), make_mock_ship(serial=1), make_mock_ship(serial=2)]
    result = filter_ships(ships, {'show_undamaged': True})
    assert [s.serial for s in result] == [3, 1, 2]

# 6. Combined filters (warp + status)
def test_combined_warp_and_status_filters():
    warp_damaged = make_mock_ship(is_damaged=True, mass=1000, warp_tonnage=1500)
    warp_ok = make_mock_ship(is_damaged=False, mass=1000, warp_tonnage=1500)
    no_warp_damaged = make_mock_ship(is_damaged=True, mass=1000, warp_tonnage=None)

    filter_state = {
        'show_warp_capable': True,
        'show_not_warp_capable': False,
        'show_damaged': True,
        'show_undamaged': False,
    }
    result = filter_ships([warp_damaged, warp_ok, no_warp_damaged], filter_state)
    assert len(result) == 1  # Only warp-capable AND damaged
```

### Other Pre-Refactoring Tasks

1. **Run existing tests** to establish baseline: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

2. **Add type hints** to helper function `make_mock_ship` in tests for clarity

3. **Document the status priority** in a code comment if refactoring changes the structure

4. **Consider extracting `SPECIAL_CAPABILITY_COLUMNS`** lookup into a constant at module level (already done - it's imported from `fleet_data_source.py`)
