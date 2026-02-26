# Safety Analysis: filter_ships Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Cyclomatic Complexity:** 36 (Grade F)
**Analysis Date:** 2026-02-26

---

## Tested Scenarios

### Status Filtering (Comprehensive Coverage)

| Scenario | Test Class/Method | File |
|----------|-------------------|------|
| Show all filters enabled | `TestFilterShips.test_filter_show_all` | test_fleet_report_filters.py:198 |
| Hide damaged ships | `TestFilterShips.test_filter_hide_damaged` | test_fleet_report_filters.py:217 |
| Hide undamaged ships | `TestFilterShips.test_filter_hide_undamaged` | test_fleet_report_filters.py:236 |
| Hide derelict ships | `TestFilterShips.test_filter_hide_derelict` | test_fleet_report_filters.py:255 |
| Hide destroyed ships | `TestFilterShips.test_filter_hide_destroyed` | test_fleet_report_filters.py:274 |

### Warp Capability Filtering (Good Coverage)

| Scenario | Test Class/Method | File |
|----------|-------------------|------|
| Hide warp-capable ships | `TestFilterShipsWarp.test_filter_hide_warp_capable` | test_fleet_report_filters.py:348 |
| Hide non-warp-capable ships | `TestFilterShipsWarp.test_filter_hide_not_warp_capable` | test_fleet_report_filters.py:370 |
| Both warp filters enabled | `TestFilterShipsWarp.test_filter_show_all_warp_states` | test_fleet_report_filters.py:392 |

### Spaceyard Capability Filtering (Good Coverage)

| Scenario | Test Class/Method | File |
|----------|-------------------|------|
| Hide ships with spaceyard | `TestFilterShipsSpaceyard.test_filter_hide_has_spaceyard` | test_fleet_report_filters.py:591 |
| Hide ships without spaceyard | `TestFilterShipsSpaceyard.test_filter_hide_no_spaceyard` | test_fleet_report_filters.py:620 |
| Both spaceyard filters enabled | `TestFilterShipsSpaceyard.test_filter_show_all_spaceyard_states` | test_fleet_report_filters.py:649 |

### Cargo Filtering (Good Coverage)

| Scenario | Test Class/Method | File |
|----------|-------------------|------|
| Hide ships with cargo | `TestFilterShipsCargo.test_filter_hide_has_cargo` | test_fleet_report_filters.py:675 |
| Hide ships without cargo | `TestFilterShipsCargo.test_filter_hide_no_cargo` | test_fleet_report_filters.py:700 |
| Population counts as cargo | `TestFilterShipsCargo.test_filter_cargo_with_population` | test_fleet_report_filters.py:725 |
| Zero-value cargo treated as no cargo | `TestFilterShipsCargo.test_filter_cargo_zero_value_treated_as_no_cargo` | test_fleet_report_filters.py:750 |
| Both cargo filters enabled | `TestFilterShipsCargo.test_filter_show_all_cargo_states` | test_fleet_report_filters.py:771 |

### Special Capability Filtering (Partial Coverage)

| Scenario | Test Class/Method | File |
|----------|-------------------|------|
| Hide ships with DestroyPlanet ability | `TestSpecialCapabilityFilter.test_filter_hides_ships_with_ability` | test_fleet_report_filters.py:799 |
| Hide ships without DestroyPlanet ability | `TestSpecialCapabilityFilter.test_filter_hides_ships_without_ability` | test_fleet_report_filters.py:826 |
| Default shows all (no special filters) | `TestSpecialCapabilityFilter.test_filter_default_shows_all` | test_fleet_report_filters.py:853 |

---

## Edge Cases

### Handled Edge Cases

| Edge Case | Handling | Evidence |
|-----------|----------|----------|
| Empty ships list | Implicit: loop never executes, returns `[]` | Not explicitly tested |
| Missing filter keys | `.get(key, True)` defaults to show | All filter checks use this pattern |
| Cargo dict with zero values | `sum(values) > 0` catches this | test_filter_cargo_zero_value_treated_as_no_cargo |
| Empty cargo_contents dict | `bool(ship.cargo_contents)` handles | Implicit in hide_no_cargo test |

### Unhandled Edge Cases (Risk)

| Edge Case | Risk Level | Current Behavior | Recommendation |
|-----------|------------|------------------|----------------|
| `None` in ships list | MEDIUM | Would raise `AttributeError` | Consider input validation |
| `filter_state` is `None` | HIGH | Would raise `TypeError` on `.get()` | Document or validate |
| `ship.cargo_contents = None` | MEDIUM | Would fail on `bool()` check | Mock always uses dict |
| Missing ship attributes | MEDIUM | `AttributeError` on access | Mocks ensure attributes exist |

---

## Invariants

### Critical Invariants (MUST Preserve)

1. **Order Preservation**
   Ships that pass filters MUST remain in their original relative order.
   *Currently tested:* NO (implicit in test assertions but not explicit)

2. **No Mutation**
   Input list and ship objects MUST NOT be modified.
   *Currently tested:* NO

3. **Complete Filtering**
   Every ship MUST be evaluated against ALL applicable filters.
   *Currently tested:* YES (via integration tests)

4. **Default True Semantics**
   Missing filter keys MUST default to `True` (show all).
   *Currently tested:* PARTIALLY (implicit in some tests)

5. **Status Filter Mutual Exclusivity**
   Each ship MUST match exactly ONE status category:
   - Destroyed (checked first) - never also derelict/damaged/undamaged
   - Derelict (checked second) - never also damaged/undamaged
   - Damaged (checked third) - never also undamaged
   - Undamaged (checked last) - only if none of the above

   *Currently tested:* NO (critical gap)

### Filter Pair Semantics

Each capability has a pair of filters (`show_X` / `show_no_X`):
- Both True: no filtering on that dimension (all ships pass)
- Both False: no ships pass that dimension (edge case)
- One True: filter to that subset

*Currently tested:* PARTIALLY (all-true cases covered, both-false NOT tested)

---

## Risks

### HIGH RISK: Status Filter Mutual Exclusivity

**Location:** Lines 196-220

```python
# DESTROYED path (checked FIRST)
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue  # <-- Critical: prevents fall-through

# DERELICT path (checked SECOND)
if ship.is_derelict:
    if not filter_state.get('show_derelict', True):
        continue
    result.append(ship)
    continue  # <-- Critical: prevents fall-through

# DAMAGED path (checked THIRD)
if ship.is_damaged():
    if not filter_state.get('show_damaged', True):
        continue
    result.append(ship)
    continue  # <-- Critical: prevents fall-through

# UNDAMAGED path (implicit fall-through)
```

**Why Risky:**
- The `continue` statements after `result.append()` are CRITICAL
- Removing or changing these creates silent bugs where ships match multiple categories
- A derelict ship that is also `is_damaged()=True` would incorrectly match damaged filter
- Refactoring to helper functions could break this flow control

**Mitigation:** Add explicit tests for:
- Derelict ship with `is_damaged()=True` matches derelict, NOT damaged
- Destroyed ship that was derelict matches destroyed, NOT derelict

### MEDIUM RISK: Late Imports Inside Conditionals

**Location:** Lines 159, 185

```python
if not show_has_yard or not show_no_yard:
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
    # ...
```

**Why Risky:**
- Import timing changes if extracted to module-level helpers
- Could cause subtle import order issues or circular imports
- Performance: repeated imports inside loop (Python caches, but still)

**Mitigation:** Keep imports inside extracted helper functions OR move to module level with explicit documentation.

### MEDIUM RISK: Special Capability Key Derivation

**Location:** Lines 181-183

```python
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

**Why Risky:**
- String manipulation derives filter keys dynamically
- `can_destroy_planet` -> `show_can_destroy_planet` / `show_no_destroy_planet`
- If naming convention changes, this breaks silently
- Only 2 of 5 special capabilities are tested

**Mitigation:** Add tests for all 5 special capabilities.

### LOW RISK: Cargo Boolean Logic

**Location:** Line 170

```python
has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
```

**Why Risky:**
- Two conditions ANDed: empty dict AND zero-sum dict both = "no cargo"
- Refactoring might simplify to just one check, changing behavior

**Mitigation:** Current tests cover this edge case adequately.

---

## Test Gaps

### Critical Gaps (MUST FIX Before Refactoring)

1. **Status Hierarchy Tests**
   ```python
   def test_derelict_not_counted_as_damaged():
       """Ship that is derelict AND is_damaged()=True matches ONLY derelict filter."""
       ship = make_mock_ship(is_derelict=True, is_damaged=True)
       filter_state = {'show_damaged': False, 'show_derelict': True, ...}
       result = filter_ships([ship], filter_state)
       assert len(result) == 1  # Ship passes as derelict, not filtered by damaged

   def test_destroyed_not_counted_as_derelict():
       """Ship that is destroyed AND was derelict matches ONLY destroyed filter."""
       ship = make_mock_ship(is_alive=False, is_derelict=True)
       filter_state = {'show_destroyed': True, 'show_derelict': False, ...}
       result = filter_ships([ship], filter_state)
       assert len(result) == 1  # Ship passes as destroyed
   ```

2. **Empty Input Tests**
   ```python
   def test_empty_ships_list():
       result = filter_ships([], {'show_damaged': True, ...})
       assert result == []

   def test_empty_filter_state_shows_all():
       ships = [make_mock_ship() for _ in range(3)]
       result = filter_ships(ships, {})
       assert len(result) == 3  # All defaults to True
   ```

3. **Order Preservation Test**
   ```python
   def test_preserves_input_order():
       ships = [make_mock_ship(serial=i) for i in [5, 2, 8, 1, 9]]
       result = filter_ships(ships, {'show_undamaged': True, ...})
       assert [s.serial for s in result] == [5, 2, 8, 1, 9]
   ```

4. **Input Non-Mutation Test**
   ```python
   def test_does_not_mutate_input():
       ships = [make_mock_ship()]
       original_len = len(ships)
       filter_ships(ships, {'show_undamaged': False})
       assert len(ships) == original_len
   ```

5. **Both Pairs False Edge Case**
   ```python
   def test_both_warp_filters_false_shows_none():
       ships = [make_mock_ship(warp_tonnage=1500), make_mock_ship(warp_tonnage=None)]
       filter_state = {'show_warp_capable': False, 'show_not_warp_capable': False, ...}
       result = filter_ships(ships, filter_state)
       assert len(result) == 0
   ```

### Important Gaps (Should Fix)

6. **All 5 Special Capabilities Tested**
   - Only `DestroyPlanet` is tested
   - Need tests for: `OpenWarpPoint`, `CloseWarpPoint`, `DestroyStar`, `CreateSphereWorld`

7. **Combined Filter Interactions**
   - Warp capable AND has cargo: both should apply independently
   - Derelict AND has spaceyard: both should apply

---

## Recommendation

### Verdict: REFACTORABLE with Pre-Work

The `filter_ships` function is a good candidate for refactoring, but **8-10 new tests must be added BEFORE any refactoring begins** to create a safety net.

### Pre-Refactoring Checklist

- [ ] Add test: `test_empty_ships_list`
- [ ] Add test: `test_empty_filter_state_shows_all`
- [ ] Add test: `test_derelict_not_counted_as_damaged` (CRITICAL)
- [ ] Add test: `test_destroyed_not_counted_as_derelict` (CRITICAL)
- [ ] Add test: `test_both_filter_pairs_false_shows_none`
- [ ] Add test: `test_preserves_input_order`
- [ ] Add test: `test_does_not_mutate_input`
- [ ] Add tests for remaining 4 special abilities
- [ ] Run full test suite to establish baseline
- [ ] Document test count before and after

### Recommended Refactoring Approach

Extract 5 helper functions:
```python
def _passes_warp_filter(ship, filter_state) -> bool
def _passes_spaceyard_filter(ship, filter_state) -> bool
def _passes_cargo_filter(ship, filter_state) -> bool
def _passes_special_ability_filters(ship, filter_state) -> bool
def _passes_status_filter(ship, filter_state) -> bool
```

Simplify main function to:
```python
def filter_ships(ships, filter_state):
    return [
        ship for ship in ships
        if _passes_warp_filter(ship, filter_state)
        and _passes_spaceyard_filter(ship, filter_state)
        and _passes_cargo_filter(ship, filter_state)
        and _passes_special_ability_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```

### Expected Outcome

| Metric | Before | After |
|--------|--------|-------|
| Main function CC | 36 | ~6 |
| Helper functions CC | N/A | 4-8 each |
| Test count | ~35 | ~45 |
| Risk of regression | N/A | LOW (with new tests) |

### Alternative: Skip If Tests Fail

If adding the missing tests reveals bugs in the current implementation, or if the status hierarchy proves too fragile to safely refactor, add to skip list with rationale:
- "Status filter mutual exclusivity requires precise flow control"
- "Refactoring risk exceeds complexity benefit"
