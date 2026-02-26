# Safety Analysis: `filter_ships` Function

**Target File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Analysis Date:** 2026-02-26

---

## 1. Function Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a dictionary of boolean filter states. It supports multiple filter categories:

1. **Status filters**: damaged, undamaged, derelict, destroyed
2. **Capability filters**: warp_capable, not_warp_capable, has_spaceyard, no_spaceyard
3. **Cargo filters**: has_cargo, no_cargo
4. **Special capability filters**: Dynamically derived from `SPECIAL_CAPABILITY_COLUMNS` (destroy_planet, open_warp, close_warp, destroy_star, create_sphere)

### Complexity Characteristics

- **Lines of code:** ~100 lines
- **Cyclomatic complexity:** HIGH (estimated 15-20 due to nested conditionals)
- **Number of filter categories:** 6
- **External dependencies:** 2 (ShipStatsCalculator, FleetCapabilityCalculator)
- **Late imports:** 2 (FleetCapabilityCalculator imported conditionally inside the function)

---

## 2. Current Test Coverage Analysis

### Tests Found

**File:** `tests/unit/ui/screens/test_fleet_report_filters.py`

| Test Class | Coverage Area |
|------------|---------------|
| `TestFilterShips` | Basic status filters (damaged, undamaged, derelict, destroyed) |
| `TestFilterShipsWarp` | Warp capability filters |
| `TestFilterShipsSpaceyard` | Spaceyard capability filters |
| `TestFilterShipsCargo` | Cargo filters |
| `TestSpecialCapabilityFilter` | Special capability filters (BUG-83) |

### Coverage Gaps Identified

| Gap | Risk Level | Description |
|-----|------------|-------------|
| **Empty list input** | LOW | No explicit test for `filter_ships([], filter_state)` |
| **Empty filter_state dict** | MEDIUM | No test with `{}` or missing keys |
| **All filters disabled** | MEDIUM | No test where ALL show_ flags are False (should return empty) |
| **Status hierarchy edge cases** | HIGH | Derelict ships are also damaged; filter ordering matters |
| **Combined filter interactions** | HIGH | No tests combining multiple filter categories simultaneously |
| **None values in cargo_contents** | MEDIUM | What if `ship.cargo_contents` is None? |
| **Special capability filter key derivation** | MEDIUM | The `no_key = col_id.replace('can_', 'no_', 1)` pattern is brittle |

---

## 3. Invariants That Must Be Preserved

### Critical Invariants

1. **Filter independence**: Each filter category should work independently of others
2. **Filter order for status**: Destroyed -> Derelict -> Damaged -> Undamaged (mutually exclusive categories)
3. **Default pass-through**: If a filter key is missing from filter_state, the function defaults to `True` (show all)
4. **Warp capability check optimization**: Only checks `ShipStatsCalculator.has_warp_capability()` if one of the warp filters is disabled
5. **Original list unchanged**: Input list is not modified (new result list is created)
6. **Order preservation**: Ships appear in result in the same relative order as input (no sorting)

### Status Categorization Hierarchy

```
Ship Status Categories (mutually exclusive):
1. DESTROYED (is_alive == False) -> checked first, exits early
2. DERELICT (is_derelict == True) -> checked second, exits early
3. DAMAGED (is_damaged() == True) -> checked third
4. UNDAMAGED -> default category (none of above)
```

**CRITICAL:** The `is_derelict` check happens BEFORE `is_damaged()` because a derelict ship would also return `True` for `is_damaged()`. Changing this order would break behavior.

---

## 4. Risk Areas for Refactoring

### HIGH RISK

| Area | Risk | Mitigation |
|------|------|------------|
| **Status filter order** | Changing the evaluation order of destroyed/derelict/damaged/undamaged will change which category a ship falls into | Add explicit tests for edge case ships (derelict + damaged, destroyed + damaged) |
| **Early return logic** | The `continue` statements create early exits that skip subsequent filters | Document that status filters are terminal (after passing, ship is added) |
| **Special capability key derivation** | `no_key = col_id.replace('can_', 'no_', 1)` is fragile | Consider extracting to a mapping or adding validation |

### MEDIUM RISK

| Area | Risk | Mitigation |
|------|------|------------|
| **Late imports** | `FleetCapabilityCalculator` is imported inside conditionals; moving this could affect import order and circular dependency handling | Keep import location or document why it was moved |
| **Default True behavior** | `filter_state.get('key', True)` means missing keys show everything; refactoring could accidentally remove this default | Add tests verifying partial filter_state dicts work |
| **Cargo check with sum()** | `sum(ship.cargo_contents.values()) > 0` assumes cargo_contents is never None and all values are numeric | Add defensive checks or tests for edge cases |

### LOW RISK

| Area | Risk | Mitigation |
|------|------|------------|
| **Loop structure** | Converting to list comprehension would require careful handling of the multi-stage filter logic | Keep imperative style for clarity |
| **Variable naming** | `_skip` flag pattern is non-standard | Consider refactoring to nested function or early break |

---

## 5. Required Tests Before Refactoring

### Must-Have Tests

```python
# 1. Empty input list
def test_filter_empty_list_returns_empty():
    result = filter_ships([], {'show_damaged': True})
    assert result == []

# 2. Empty filter state (all defaults)
def test_filter_empty_state_shows_all():
    ships = [make_ship(is_damaged=True), make_ship(is_damaged=False)]
    result = filter_ships(ships, {})
    assert len(result) == 2  # All pass with defaults

# 3. Partial filter state
def test_filter_partial_state_uses_defaults():
    ships = [make_ship(is_damaged=True), make_ship(is_damaged=False)]
    result = filter_ships(ships, {'show_damaged': False})  # Only specify one
    assert len(result) == 1

# 4. All filters disabled returns empty
def test_filter_all_disabled_returns_empty():
    ships = [make_ship()]
    result = filter_ships(ships, {
        'show_damaged': False, 'show_undamaged': False,
        'show_derelict': False, 'show_destroyed': False
    })
    assert len(result) == 0

# 5. Derelict ship is NOT also matched as damaged
def test_derelict_ship_not_matched_as_damaged():
    """Derelict filter takes precedence over damaged filter."""
    ship = make_ship(is_derelict=True, is_damaged=True)
    result = filter_ships([ship], {
        'show_derelict': False, 'show_damaged': True,
        'show_undamaged': True, 'show_destroyed': True
    })
    assert len(result) == 0  # Filtered out as derelict, not kept as damaged

# 6. Destroyed ship is NOT also matched as derelict or damaged
def test_destroyed_ship_not_matched_as_derelict():
    ship = make_ship(is_alive=False, is_derelict=True, is_damaged=True)
    result = filter_ships([ship], {
        'show_destroyed': False, 'show_derelict': True,
        'show_damaged': True, 'show_undamaged': True
    })
    assert len(result) == 0  # Filtered out as destroyed

# 7. Combined capability + status filters
def test_combined_warp_and_status_filters():
    warp_damaged = make_ship(warp_capable=True, is_damaged=True)
    warp_healthy = make_ship(warp_capable=True, is_damaged=False)
    no_warp_damaged = make_ship(warp_capable=False, is_damaged=True)
    result = filter_ships([warp_damaged, warp_healthy, no_warp_damaged], {
        'show_warp_capable': True, 'show_not_warp_capable': False,
        'show_damaged': False, 'show_undamaged': True,
        'show_derelict': True, 'show_destroyed': True
    })
    assert len(result) == 1
    assert warp_healthy in result

# 8. cargo_contents is None
def test_cargo_filter_handles_none_cargo():
    ship = make_ship()
    ship.cargo_contents = None  # Edge case
    result = filter_ships([ship], {
        'show_has_cargo': True, 'show_no_cargo': True
    })
    # Should not crash, should be treated as no cargo

# 9. Order preservation
def test_filter_preserves_order():
    ships = [make_ship(serial=i) for i in range(5)]
    ships[2].is_damaged = lambda: True  # Mark middle ship damaged
    result = filter_ships(ships, {'show_damaged': False, 'show_undamaged': True})
    serials = [s.serial for s in result]
    assert serials == [0, 1, 3, 4]  # Order preserved, #2 removed
```

---

## 6. Recommendation

### Refactorability Assessment: PROCEED WITH CAUTION

**Overall Rating:** MEDIUM COMPLEXITY, REFACTORABLE

The function is a good candidate for refactoring because:
- Clear responsibility (filtering ships)
- Well-defined inputs and outputs
- Existing test coverage for major paths
- No side effects (pure function)

However, refactoring requires:
1. **Adding 5-8 new tests** before making any changes (see Section 5)
2. **Preserving filter evaluation order** for status categories
3. **Maintaining default True behavior** for missing filter keys
4. **Keeping late imports** in place or documenting circular dependency mitigation

### Suggested Refactoring Approach

1. **Extract filter predicates**: Create small predicate functions for each filter category
2. **Use filter chaining**: Apply filters in sequence rather than nested conditionals
3. **Explicit category priority**: Document and test the destroyed->derelict->damaged->undamaged hierarchy
4. **Consider dataclass for filter state**: Instead of Dict[str, bool], use a typed FilterState class

### Do Not Skip This Function

The function should NOT be skipped because:
- It has business logic that benefits from clearer structure
- Test coverage exists and can be expanded
- The complexity is manageable with proper decomposition
- No fundamental design issues that would require architectural changes

---

## 7. Appendix: Dependency Graph

```
filter_ships
    |
    +-- ShipStatsCalculator.has_warp_capability (external)
    |       |
    |       +-- ship.get_calculated_stats()
    |       +-- ship.design_data['expected_stats']
    |
    +-- FleetCapabilityCalculator.ship_has_spaceyard (external, late import)
    |       |
    |       +-- component_inspector.ship_has_ability
    |
    +-- FleetCapabilityCalculator.ship_has_ability (external, late import)
    |       |
    |       +-- component_inspector.ship_has_ability
    |
    +-- SPECIAL_CAPABILITY_COLUMNS (constant from fleet_data_source.py)
    |
    +-- ShipInstance attributes:
            +-- is_alive
            +-- is_derelict
            +-- is_damaged()
            +-- cargo_contents
```

---

## 8. Files to Modify

If refactoring proceeds, the following files may need updates:

| File | Reason |
|------|--------|
| `game/ui/screens/fleet_report_filters.py` | Primary target |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Add missing tests |
| `game/ui/screens/fleet_report_view_model.py` | Caller - verify interface unchanged |
