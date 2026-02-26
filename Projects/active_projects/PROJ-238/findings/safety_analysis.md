# Safety Analysis: filter_ships Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Test File:** `C:\Dev\Starship Battles\tests\unit\ui\screens\test_fleet_report_filters.py`

---

## Edge Cases

### 1. Empty Input Lists
- **Empty ships list:** Returns empty list (handled correctly via loop that never executes)
- **Missing filter keys:** Uses `.get()` with default `True` for all filter keys, so missing keys mean "show all"

### 2. Ship Status Edge Cases
- **Destroyed ships:** Checked via `ship.is_alive` being `False`; takes precedence over other status checks
- **Derelict ships:** Checked before damaged status (a derelict ship is also damaged but should not be double-counted)
- **Derelict AND damaged:** Derelict check comes first (lines 203-208), so these are categorized as derelict only

### 3. Cargo Edge Cases
- **Empty cargo dict:** `bool({})` is `False`, treated as no cargo
- **Cargo dict with all zeros:** Explicitly handled (line 170): `sum(ship.cargo_contents.values()) > 0` catches this case
- **None cargo_contents:** Would raise AttributeError if `ship.cargo_contents` is None (not tested)

### 4. Special Capability Loop
- **SPECIAL_CAPABILITY_COLUMNS iteration:** Iterates all 5 special columns for every ship that passes prior filters
- **Key derivation:** Uses string replacement `col_id.replace('can_', 'no_', 1)` to derive "no" key from column ID
  - Example: `can_destroy_planet` -> `no_destroy_planet`

---

## Invariants

### 1. Filter State Contract
- All filter keys must be boolean values
- Filter keys follow naming convention: `show_<category>` for positive filters
- Default value for missing filter keys is `True` (show all)

### 2. Ship State Assumptions
- `ship.is_alive` is a boolean attribute (not a method)
- `ship.is_derelict` is a boolean attribute (not a method)
- `ship.is_damaged()` is a method (returns bool)
- `ship.cargo_contents` is a dict (or dict-like) supporting `bool()` and `.values()`

### 3. Order of Evaluation
The function MUST evaluate filters in this specific order:
1. Warp capability (lines 143-153)
2. Spaceyard capability (lines 155-164)
3. Cargo contents (lines 166-174)
4. Special capabilities loop (lines 176-194)
5. Destroyed status (lines 196-201) - terminates early
6. Derelict status (lines 203-208) - terminates early
7. Damaged status (lines 210-215) - terminates early
8. Undamaged fallthrough (lines 217-220)

**Critical:** The status checks (destroyed/derelict/damaged/undamaged) are mutually exclusive and use early return. This prevents ships from being added multiple times.

### 4. Result Integrity
- Ships are appended to `result` exactly once or not at all
- Original `ships` list is not modified (new list created)

---

## Risk Areas

### 1. HIGH RISK: Late Import in Loop
```python
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    ...
    if not show_has or not show_not:
        from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```
- The import is inside the loop, inside a conditional
- This import runs repeatedly (up to 5 times per ship, once per special capability)
- Python caches imports, but this is still inefficient and could cause issues if the module has side effects

### 2. MEDIUM RISK: Spaceyard Import Pattern (Same Issue)
```python
if not show_has_yard or not show_no_yard:
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```
- Import inside conditional, inside loop

### 3. MEDIUM RISK: Control Flow Complexity
- The function uses multiple `continue` statements (10 total)
- Multiple early `return` via `result.append(); continue` pattern
- The `_skip` variable adds another layer of control flow for special capabilities
- Cognitive complexity is high due to nested conditionals and early exits

### 4. LOW RISK: String-Based Key Derivation
```python
no_key = col_id.replace('can_', 'no_', 1)
```
- Relies on column IDs starting with `can_` prefix
- If a column ID doesn't match this pattern, the key derivation produces incorrect results
- Currently all special capability columns follow this convention

### 5. LOW RISK: Implicit Fallthrough to Undamaged
- Ships that pass all filters and aren't destroyed/derelict/damaged fall through to "undamaged"
- This is correct behavior but relies on exhaustive status categorization

---

## Test Coverage Gaps

### 1. Missing Tests

| Gap | Description | Priority |
|-----|-------------|----------|
| **None input** | `filter_ships(None, {...})` would crash | Low (unlikely in practice) |
| **Empty filter_state** | `filter_ships(ships, {})` - all defaults to True | Medium |
| **cargo_contents is None** | Would raise AttributeError | Medium |
| **Mixed status ships** | Ship that is both derelict AND destroyed | Medium |
| **All filters off** | Filter state with all values False (should return empty) | Medium |
| **Partial filter state** | Only some keys provided | Low |

### 2. Existing Test Coverage (Good)
- Basic show/hide for damaged, undamaged, derelict, destroyed
- Warp capability filtering (both directions)
- Spaceyard filtering (both directions)
- Cargo filtering including zero-value edge case
- Special capability filtering (DestroyPlanet)
- Default filter state shows all ships

### 3. Tests That Should Be Added BEFORE Refactoring

```python
def test_empty_filter_state_shows_all():
    """Empty filter state dict should show all ships (all defaults True)."""
    ships = [make_mock_ship(), make_mock_ship(is_damaged=True)]
    result = filter_ships(ships, {})
    assert len(result) == 2

def test_all_filters_false_shows_none():
    """All filters False should hide all ships."""
    ships = [make_mock_ship()]
    filter_state = {
        'show_damaged': False,
        'show_undamaged': False,
        'show_derelict': False,
        'show_destroyed': False,
    }
    result = filter_ships(ships, filter_state)
    assert len(result) == 0

def test_destroyed_derelict_ship():
    """Destroyed takes precedence over derelict status."""
    ship = make_mock_ship(is_alive=False, is_derelict=True)
    filter_state = {
        'show_damaged': True,
        'show_undamaged': True,
        'show_derelict': True,
        'show_destroyed': False,  # Hide destroyed
    }
    result = filter_ships([ship], filter_state)
    assert len(result) == 0  # Destroyed status takes precedence

def test_order_independence_of_capability_filters():
    """Capability filters should not affect each other."""
    # Test multiple capability filters combined
    pass
```

---

## Recommendation

**REFACTORABLE** with caution.

### Rationale
1. **Good test coverage exists** - The test file has comprehensive tests covering most scenarios
2. **Function is self-contained** - Only one call site in the codebase
3. **Clear structure** - Despite complexity, the function has a clear pattern

### Suggested Refactoring Approach
1. **Extract helper functions** for each filter category:
   - `_passes_warp_filter(ship, filter_state) -> bool`
   - `_passes_spaceyard_filter(ship, filter_state) -> bool`
   - `_passes_cargo_filter(ship, filter_state) -> bool`
   - `_passes_special_capability_filter(ship, filter_state) -> bool`
   - `_passes_status_filter(ship, filter_state) -> bool`

2. **Move imports to top of file** or module level

3. **Simplify control flow**:
   ```python
   for ship in ships:
       if (passes_warp_filter(ship, filter_state) and
           passes_spaceyard_filter(ship, filter_state) and
           passes_cargo_filter(ship, filter_state) and
           passes_special_capability_filter(ship, filter_state) and
           passes_status_filter(ship, filter_state)):
           result.append(ship)
   ```

### Pre-Refactoring Checklist
- [ ] Add test for empty filter_state
- [ ] Add test for all-filters-off scenario
- [ ] Add test for destroyed+derelict ship precedence
- [ ] Verify late imports don't have side effects
- [ ] Consider moving FleetCapabilityCalculator import to top of file

### Risk Level: **LOW-MEDIUM**
The function is complex but well-tested. Refactoring should preserve exact behavior, especially the order of status checks (destroyed -> derelict -> damaged -> undamaged).
