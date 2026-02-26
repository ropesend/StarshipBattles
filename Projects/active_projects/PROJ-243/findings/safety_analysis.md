# Safety Analysis: filter_ships (CC 36)

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** 36
**Analyzed:** 2026-02-26

---

## 1. Edge Cases and Error Handling Paths

### 1.1 Empty Input Handling
- **Empty ships list:** Returns empty list (implicit - for loop simply doesn't execute)
- **Empty filter_state dict:** All filters default to `True` via `.get()` with default values

### 1.2 Missing Filter Keys (Graceful Defaults)
The function uses `.get(key, True)` extensively, meaning:
- Missing filter keys default to "show all" behavior
- This is intentional: partial filter states still work correctly

### 1.3 Edge Cases in Filter Logic

| Scenario | Behavior | Risk |
|----------|----------|------|
| Ship with `is_alive=False` AND `is_derelict=True` | Handled as destroyed first (line 197-201) | LOW - status checks are ordered correctly |
| Ship that `is_damaged()` AND `is_derelict` | Handled as derelict first (line 204-208) | LOW - derelict takes precedence |
| Ship with `cargo_contents` dict but all values zero | Treated as "no cargo" (line 170) | LOW - explicit sum check |
| Ship with `cargo_contents = None` | Would fail with `bool(ship.cargo_contents)` being `False` | LOW - works as expected |
| SPECIAL_CAPABILITY_COLUMNS iteration with unknown ability | FleetCapabilityCalculator returns False | LOW - graceful handling |

### 1.4 Late Import Locations
```python
Line 159: from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
Line 185: from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator  # duplicate
```
- Import occurs inside loop (lines 159, 185) - performance concern but not correctness issue
- Import only happens if filter is active (`not show_has or not show_not`)

---

## 2. Invariants That Must Be Preserved

### 2.1 Filter Precedence (CRITICAL)
The ship status filter logic has a **strict precedence order**:
```
1. Warp capability filter (lines 143-153)
2. Spaceyard capability filter (lines 155-164)
3. Cargo filter (lines 166-174)
4. Special capability filters loop (lines 176-194)
5. Destroyed check (lines 196-201)
6. Derelict check (lines 203-208)
7. Damaged check (lines 210-215)
8. Undamaged fallthrough (lines 217-220)
```

**INVARIANT:** A ship can only be classified into ONE of: destroyed, derelict, damaged, or undamaged. The ordering ensures mutual exclusivity.

### 2.2 "Both True" Optimization
When both filters in a pair are `True`, the capability check is skipped entirely:
```python
if not show_warp or not show_not_warp:  # Only check if filtering is active
```
**INVARIANT:** If both show_X and show_not_X are True, the ship should pass that filter category without checking.

### 2.3 Filter Independence
- Warp, spaceyard, cargo, and special capability filters are INDEPENDENT of status filters
- A ship must pass ALL filter categories to be included
- Order matters for early exit (`continue` statements)

### 2.4 Special Capability Key Transformation
```python
no_key = col_id.replace('can_', 'no_', 1)  # 'can_destroy_planet' -> 'no_destroy_planet'
```
**INVARIANT:** The "no" variant key is derived by replacing the first `can_` with `no_`.

---

## 3. Risk Areas Where Refactoring Could Introduce Bugs

### 3.1 HIGH RISK: Status Filter Ordering
The status checks (destroyed/derelict/damaged/undamaged) MUST remain in this exact order:
```python
# Line 196-201: Destroyed FIRST
if not ship.is_alive:
    ...

# Line 203-208: Derelict SECOND (implies damaged)
if ship.is_derelict:
    ...

# Line 210-215: Damaged THIRD
if ship.is_damaged():
    ...

# Line 217-220: Undamaged LAST (fallthrough)
```

**Risk:** Extracting to separate functions or reordering will break classification. A derelict ship would be double-counted or misclassified.

### 3.2 HIGH RISK: Early Exit Pattern
The function uses `continue` statements for early rejection. If refactored to helper functions:
- Must preserve early exit behavior
- Returning `False` from a helper doesn't skip to next ship automatically

### 3.3 MEDIUM RISK: The `_skip` Flag Pattern
```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    ...
    if has_ability and not show_has:
        _skip = True
        break
if _skip:
    continue
```
This is the only place a nested loop requires a flag to `continue` the outer loop. Refactoring this loop without preserving the break/skip semantics would cause bugs.

### 3.4 MEDIUM RISK: Duplicate Late Import
The `FleetCapabilityCalculator` import appears twice (lines 159 and 185). If refactored to a single import at function start:
- Would change behavior if only one filter type is used
- Minor performance difference, but semantically correct

### 3.5 LOW RISK: Filter State Key Naming
Filter keys follow patterns:
- `show_damaged`, `show_undamaged`, etc. (status)
- `show_warp_capable`, `show_not_warp_capable` (warp)
- `show_has_spaceyard`, `show_no_spaceyard` (spaceyard)
- `show_has_cargo`, `show_no_cargo` (cargo)
- `show_can_destroy_planet`, `show_no_destroy_planet` (special)

Any refactoring must maintain these exact key names.

---

## 4. Missing Test Coverage

### 4.1 Covered by Existing Tests
| Filter Type | Positive Test | Negative Test | Both Enabled |
|-------------|---------------|---------------|--------------|
| Damaged | YES | YES | YES (implicit) |
| Undamaged | YES | YES | YES (implicit) |
| Derelict | YES | YES | YES (implicit) |
| Destroyed | YES | YES | YES (implicit) |
| Warp capable | YES | YES | YES |
| Not warp capable | YES | YES | YES |
| Has spaceyard | YES | YES | YES |
| No spaceyard | YES | YES | YES |
| Has cargo | YES | YES | YES |
| No cargo | YES | YES | YES |
| Special capability (destroy planet) | YES | YES | YES |

### 4.2 MISSING: Status Classification Edge Cases
```python
# MISSING: Ship that is both destroyed AND derelict
# Should be classified as destroyed, not derelict
def test_destroyed_ship_not_classified_as_derelict():
    """Destroyed ships should be excluded when show_destroyed=False,
    even if they are also derelict."""
    ship = make_mock_ship(is_alive=False, is_derelict=True)
    # ... test destroyed filter excludes it
```

### 4.3 MISSING: Derelict Implies Damaged
```python
# MISSING: Derelict ship should be filtered by derelict filter, not damaged
def test_derelict_ship_not_caught_by_damaged_filter():
    """Derelict ships should only be filtered by derelict filter,
    not by damaged filter even though they are damaged."""
    ship = make_mock_ship(is_derelict=True, is_damaged=True)
    filter_state = {
        'show_damaged': False,
        'show_derelict': True,  # Keep derelict
        ...
    }
    # Ship should be included (derelict takes precedence)
```

### 4.4 MISSING: Multiple Special Capability Filters Active
```python
# MISSING: Test with multiple special filters active simultaneously
def test_multiple_special_capability_filters():
    """Ship must pass ALL active special capability filters."""
    # Ship has DestroyPlanet but not OpenWarpPoint
    # With show_can_destroy_planet=False AND show_can_open_warp=False
    # Ship should be excluded by either
```

### 4.5 MISSING: Empty/Partial Filter State
```python
# MISSING: Filter state with only some keys defined
def test_partial_filter_state():
    """Missing filter keys should default to True (show all)."""
    filter_state = {'show_damaged': False}  # All others missing
    # Undamaged ships should still be shown
```

### 4.6 MISSING: Cargo with Zero Values
```python
# EXISTING in TestFilterShipsCargo.test_filter_cargo_zero_value_treated_as_no_cargo
# This IS covered - good
```

### 4.7 MISSING: Performance Test
```python
# MISSING: Large fleet performance test
def test_filter_ships_performance_large_fleet():
    """Filtering 1000+ ships should complete in reasonable time."""
    ships = [make_mock_ship() for _ in range(1000)]
    # Assert timing is acceptable
```

---

## 5. Refactorability Assessment

### 5.1 Recommended: REFACTORABLE with caution

The function IS refactorable, but requires careful handling of:

1. **Status filter ordering** - Must preserve exact precedence
2. **Early exit pattern** - Must maintain `continue` semantics
3. **Special capability loop with `_skip` flag** - Needs clean extraction

### 5.2 Suggested Refactoring Strategy

**Extract helper predicates:**
```python
def _passes_warp_filter(ship: ShipInstance, filter_state: Dict) -> bool:
    ...

def _passes_spaceyard_filter(ship: ShipInstance, filter_state: Dict) -> bool:
    ...

def _passes_cargo_filter(ship: ShipInstance, filter_state: Dict) -> bool:
    ...

def _passes_special_capability_filters(ship: ShipInstance, filter_state: Dict) -> bool:
    ...

def _passes_status_filter(ship: ShipInstance, filter_state: Dict) -> bool:
    """Check if ship passes status filter (destroyed/derelict/damaged/undamaged)."""
    # CRITICAL: Preserve ordering here
    ...
```

**Main function becomes:**
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    return [
        ship for ship in ships
        if _passes_warp_filter(ship, filter_state)
        and _passes_spaceyard_filter(ship, filter_state)
        and _passes_cargo_filter(ship, filter_state)
        and _passes_special_capability_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```

### 5.3 Before Refactoring: Add These Tests

1. `test_destroyed_derelict_ship_classified_as_destroyed`
2. `test_derelict_damaged_ship_classified_as_derelict`
3. `test_damaged_undamaged_mutual_exclusivity`
4. `test_multiple_special_capability_filters_all_must_pass`
5. `test_partial_filter_state_defaults_to_show_all`

### 5.4 Complexity Reduction Estimate

Current CC: 36

After extracting predicates:
- `_passes_warp_filter`: CC ~3
- `_passes_spaceyard_filter`: CC ~3
- `_passes_cargo_filter`: CC ~3
- `_passes_special_capability_filters`: CC ~5
- `_passes_status_filter`: CC ~8
- `filter_ships` (main): CC ~5

Total distributed complexity stays similar, but each function is individually testable and under CC 10.

---

## 6. Summary

| Aspect | Assessment |
|--------|------------|
| **Refactorability** | YES - with caution |
| **Test Coverage** | GOOD - 27 tests exist, 4-5 edge cases missing |
| **Risk Level** | MEDIUM - status ordering is critical |
| **Blocking Issues** | None - can proceed after adding edge case tests |

### Recommended Next Steps:
1. Add the 5 missing edge case tests identified in section 4
2. Run existing tests to establish baseline
3. Extract helper predicates one at a time
4. Re-run tests after each extraction
5. Final CC reduction to target <15 per function
