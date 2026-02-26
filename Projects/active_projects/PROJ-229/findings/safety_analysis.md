# Safety Analysis: filter_ships Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Lines:** 124-222
**Cyclomatic Complexity:** 36 (Grade F)

---

## 1. Function Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a dictionary of boolean filter flags. It implements a multi-pass filtering system covering:

1. **Warp capability** (lines 143-153)
2. **Spaceyard capability** (lines 155-164)
3. **Cargo presence** (lines 166-174)
4. **Special abilities** (lines 176-194) - dynamic based on `SPECIAL_CAPABILITY_COLUMNS`
5. **Ship status** (lines 196-220) - destroyed, derelict, damaged, undamaged

---

## 2. Edge Cases and Error Handling

### 2.1 Handled Edge Cases

| Edge Case | Handling | Lines |
|-----------|----------|-------|
| Empty ships list | Returns empty list (implicit) | N/A |
| Missing filter keys | Uses `.get(key, True)` defaulting to show | All filter checks |
| Cargo dict with zero values | Explicitly handled: `sum(values) > 0` | 170 |
| Empty cargo_contents dict | Handled via `bool(ship.cargo_contents)` | 170 |

### 2.2 Potential Edge Cases NOT Explicitly Tested

| Edge Case | Risk | Current Behavior |
|-----------|------|------------------|
| `None` in ships list | **MEDIUM** | Would raise AttributeError |
| `filter_state` is `None` | **HIGH** | Would raise TypeError on `.get()` |
| Ship with `cargo_contents = None` | **MEDIUM** | Would fail on `bool()` check |
| Ship attributes missing (e.g., `is_alive`) | **MEDIUM** | Would raise AttributeError |

---

## 3. Invariants That Must Be Preserved

### 3.1 Critical Invariants

1. **Order preservation**: Ships that pass filters must remain in their original relative order
2. **No mutation**: Input list and ships must not be modified
3. **Complete filtering**: Every ship must be evaluated against ALL applicable filters
4. **Early exit on filter failure**: Once a ship fails any filter, it should be excluded immediately (performance)
5. **Default True**: Missing filter keys default to `True` (show all)

### 3.2 Filter Priority (Order Matters!)

The function processes filters in a specific order that affects results:

1. Warp capability (can exclude early)
2. Spaceyard capability (can exclude early)
3. Cargo presence (can exclude early)
4. Special abilities (loop, can exclude early)
5. **Status filters evaluated mutually exclusively**:
   - Destroyed ships checked FIRST (lines 196-201)
   - Derelict ships checked SECOND (lines 203-208)
   - Damaged ships checked THIRD (lines 210-215)
   - Undamaged ships checked LAST (lines 217-220)

**CRITICAL**: Status classification is hierarchical:
- A destroyed ship is ONLY classified as destroyed (never derelict/damaged)
- A derelict ship is ONLY classified as derelict (not damaged, even if `is_damaged()` returns True)
- A damaged ship is ONLY classified as damaged (not undamaged)
- An undamaged ship is only reached if none of the above conditions matched

### 3.3 Filter Pair Semantics

Each capability filter comes in pairs:
- `show_X` / `show_not_X` (or `show_no_X`)
- When BOTH are True: no filtering on that dimension
- When BOTH are False: no ships pass (edge case)
- When one is True: filter to that subset

---

## 4. Risk Areas for Refactoring

### 4.1 HIGH RISK: Status Filter Mutual Exclusivity

```python
# Lines 196-220 - These if/elif blocks implement mutual exclusivity
if not ship.is_alive:
    # DESTROYED path
    continue  # or append and continue

if ship.is_derelict:
    # DERELICT path (never reached if destroyed)
    continue

if ship.is_damaged():
    # DAMAGED path (never reached if derelict)
    continue

# UNDAMAGED path (never reached if damaged)
```

**Risk**: Refactoring into separate helper functions could break this mutual exclusivity if:
- Each helper returns a result instead of using `continue`
- The calling code doesn't maintain the same flow control

**Mitigation**: Any refactoring MUST preserve the "one status category per ship" invariant.

### 4.2 MEDIUM RISK: Late Imports Inside Loop

```python
# Lines 159, 185 - FleetCapabilityCalculator imported inside conditionals
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

**Risk**: Extracting these into helpers changes import timing. If extracted to module-level helpers, imports would happen at module load instead of lazily.

**Mitigation**: Keep imports inside extracted functions OR document that import timing is now different (acceptable if tests pass).

### 4.3 MEDIUM RISK: Special Capability Filter Key Derivation

```python
# Lines 181-183
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

**Risk**: This string manipulation derives filter keys dynamically. The `SPECIAL_CAPABILITY_COLUMNS` dict keys (e.g., `can_destroy_planet`) are transformed to filter keys (e.g., `show_can_destroy_planet`, `show_no_destroy_planet`).

**Mitigation**: Any refactoring must preserve this naming convention. Tests should verify all 5 special capabilities work.

### 4.4 LOW RISK: Cargo Filter Boolean Logic

```python
# Line 170
has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
```

**Risk**: Two conditions ANDed together. Both must be true for "has cargo". This handles:
- Empty dict `{}` -> `bool({})` is False
- Dict with zero values `{'a': 0}` -> `bool()` is True but `sum()` is 0

**Mitigation**: Keep both conditions or ensure replacement logic handles both cases.

---

## 5. Test Coverage Analysis

### 5.1 Current Test Coverage

| Filter Type | Positive Test | Negative Test | Edge Cases |
|-------------|---------------|---------------|------------|
| Damaged | Yes | Yes | No |
| Undamaged | Yes | Yes | No |
| Derelict | Yes | Yes | No |
| Destroyed | Yes | Yes | No |
| Warp capable | Yes | Yes | Both enabled |
| Not warp capable | Yes | Yes | Both enabled |
| Has spaceyard | Yes | Yes | Both enabled |
| No spaceyard | Yes | Yes | Both enabled |
| Has cargo | Yes | Yes | Zero values, population |
| No cargo | Yes | Yes | Both enabled |
| Special abilities (5) | Yes (2 abilities) | Yes (2 abilities) | Default shows all |

### 5.2 Missing Test Coverage (MUST ADD BEFORE REFACTORING)

#### Critical Missing Tests

1. **Combined filter interactions**
   - Ship is derelict AND damaged: should ONLY match derelict filter, NOT damaged
   - Ship is destroyed AND was derelict: should ONLY match destroyed filter
   - Warp capable AND has cargo: both filters should apply independently

2. **Empty input list**
   - `filter_ships([], filter_state)` should return `[]`

3. **All filters disabled (both pairs False)**
   - `show_damaged=False, show_undamaged=False`: no ships pass status filter
   - `show_warp_capable=False, show_not_warp_capable=False`: no ships pass warp filter

4. **Default filter_state (empty dict)**
   - `filter_ships(ships, {})` should return all ships (defaults to True)

5. **Partial filter_state**
   - Missing some keys should default to True for those filters

6. **All special abilities tested**
   - Only `DestroyPlanet` is tested; need tests for:
     - `OpenWarpPoint` (can_open_warp)
     - `CloseWarpPoint` (can_close_warp)
     - `DestroyStar` (can_destroy_star)
     - `CreateSphereWorld` (can_create_sphere)

#### Recommended New Tests

```python
class TestFilterShipsInvariants:
    """Tests for filter_ships invariants and edge cases."""

    def test_empty_ships_list(self):
        """Empty list returns empty list."""
        pass

    def test_empty_filter_state_shows_all(self):
        """Empty filter state defaults to showing all."""
        pass

    def test_derelict_not_counted_as_damaged(self):
        """Derelict ship matches derelict filter, not damaged filter."""
        pass

    def test_destroyed_not_counted_as_derelict(self):
        """Destroyed ship matches destroyed filter, not derelict."""
        pass

    def test_both_filter_pairs_false_shows_none(self):
        """When both sides of a filter pair are False, no ships pass."""
        pass

    def test_preserves_input_order(self):
        """Filtered ships maintain original relative order."""
        pass

    def test_does_not_mutate_input(self):
        """Input list and ships are not modified."""
        pass
```

---

## 6. Refactorability Assessment

### 6.1 Complexity Sources

| Source | Contribution | Reducible? |
|--------|-------------|------------|
| 6 filter dimensions | ~12 branches | Extractable |
| 5 special capabilities in loop | ~10 branches | Extractable |
| Status hierarchy (4 states) | ~8 branches | Partially extractable |
| Null checks / defaults | ~6 branches | Minimal reduction |

### 6.2 Recommended Refactoring Strategy

**YES, this function is refactorable.** Recommended approach:

1. **Extract filter dimension helpers**:
   ```python
   def _passes_warp_filter(ship, filter_state) -> bool
   def _passes_spaceyard_filter(ship, filter_state) -> bool
   def _passes_cargo_filter(ship, filter_state) -> bool
   def _passes_special_ability_filters(ship, filter_state) -> bool
   def _passes_status_filter(ship, filter_state) -> bool
   ```

2. **Simplify main loop**:
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

3. **Expected complexity reduction**:
   - Main function: CC ~6 (loop + 5 helper calls)
   - Each helper: CC 4-8
   - Total distributed complexity is same, but each unit is manageable

### 6.3 Alternative: Skip Refactoring

If refactoring introduces risk of subtle bugs in the status hierarchy logic, the function could be added to the skip list with rationale:
- "Status filter mutual exclusivity requires careful flow control"
- "Current structure is verbose but correct and readable"

---

## 7. Pre-Refactoring Checklist

Before any refactoring begins:

- [ ] Add test for empty ships list
- [ ] Add test for empty filter_state (defaults to all True)
- [ ] Add test for derelict-not-damaged invariant
- [ ] Add test for destroyed-not-derelict invariant
- [ ] Add test for both-pairs-false edge case
- [ ] Add test for order preservation
- [ ] Add test for input non-mutation
- [ ] Add tests for remaining 4 special abilities
- [ ] Run full test suite to establish baseline
- [ ] Document current test count

---

## 8. Conclusion

| Criterion | Assessment |
|-----------|------------|
| **Refactorable?** | YES |
| **Risk Level** | MEDIUM |
| **Pre-work Required** | Add 8-10 new tests |
| **Estimated Complexity After** | ~6 (main) + 5 helpers of CC 4-8 each |
| **Recommendation** | Proceed with refactoring after adding missing tests |

The function is a good candidate for refactoring. The main risks are:
1. Breaking the status filter mutual exclusivity
2. Changing behavior when both filter pairs are False

Adding the recommended tests before refactoring will create a safety net that catches any behavioral changes.
