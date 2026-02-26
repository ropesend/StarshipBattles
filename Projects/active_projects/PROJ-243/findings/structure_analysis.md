# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Current Cyclomatic Complexity:** 36
**Target Complexity:** < 20

---

## Executive Summary

The `filter_ships` function has high complexity due to **five distinct filter categories**, each with **similar binary logic patterns** (show/hide based on capability). The complexity can be reduced by:

1. Extracting repeated binary filter patterns into a helper
2. Separating ship status classification from filtering
3. Converting the final status chain into a lookup/mapping

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Binary Capability Filters (4 occurrences, ~20 decision points)

Each of these filter blocks follows the **identical pattern**:

```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_no_X', True)
if not show_has or not show_not:      # +1 CC (compound: +1 more)
    has_capability = check_capability(ship)
    if has_capability and not show_has:  # +1 CC (compound: +1 more)
        continue
    if not has_capability and not show_not:  # +1 CC (compound: +1 more)
        continue
```

**Occurrences:**
- Warp capability filter (lines 144-153): ~5 CC
- Spaceyard capability filter (lines 156-164): ~5 CC
- Cargo filter (lines 167-174): ~5 CC
- Special capability loop (lines 176-194): ~5 CC base + loop iterations

### 1.2 Special Capability Loop (lines 176-194, ~10 decision points)

```python
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():  # +1 CC (loop)
    show_has = filter_state.get(f'show_{col_id}', True)
    no_key = col_id.replace('can_', 'no_', 1)
    show_not = filter_state.get(f'show_{no_key}', True)
    if not show_has or not show_not:                    # +2 CC
        has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
        if has_ability and not show_has:                # +2 CC
            _skip = True
            break
        if not has_ability and not show_not:            # +2 CC
            _skip = True
            break
if _skip:                                               # +1 CC
    continue
```

This is the single largest contributor, containing:
- 1 loop
- 3 compound conditionals
- 1 post-loop check
- State mutation (`_skip` flag)

### 1.3 Status Classification Chain (lines 196-220, ~8 decision points)

```python
if not ship.is_alive:                           # +1 CC
    if not filter_state.get('show_destroyed'):  # +1 CC
        continue
    result.append(ship)
    continue

if ship.is_derelict:                            # +1 CC
    if not filter_state.get('show_derelict'):   # +1 CC
        continue
    result.append(ship)
    continue

if ship.is_damaged():                           # +1 CC
    if not filter_state.get('show_damaged'):    # +1 CC
        continue
    result.append(ship)
    continue

if not filter_state.get('show_undamaged'):      # +1 CC
    continue
result.append(ship)
```

This chain classifies ships into 4 mutually exclusive states, but the logic is spread across nested conditionals with early continues.

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Capability Filter Nesting

**Current pattern:**
```python
if not show_has or not show_not:
    has_capability = check_capability(ship)
    if has_capability and not show_has:
        continue
    if not has_capability and not show_not:
        continue
```

**Can be flattened to:**
```python
# Extract to helper: returns True if ship should be excluded
if _should_exclude_by_binary_filter(ship, show_has, show_not, check_fn):
    continue
```

### 2.2 Status Filter Chain

**Current:** Nested if-continue-append-continue pattern

**Can be flattened to:**
```python
status = _classify_ship_status(ship)  # Returns 'destroyed'|'derelict'|'damaged'|'undamaged'
if not filter_state.get(f'show_{status}', True):
    continue
result.append(ship)
```

---

## 3. Early Returns That Could Simplify Logic

The function uses `continue` statements extensively, which is appropriate for filtering. However, the early returns can be reorganized:

### 3.1 Extract Filter Predicate

Instead of mutating `result` inside the loop, use a predicate:

```python
def _ship_passes_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Return True if ship passes all filters."""
    # ... all filter checks, returning False if any fail
    return True

return [ship for ship in ships if _ship_passes_filters(ship, filter_state)]
```

This eliminates the `result = []` / `result.append()` pattern and makes the function's intent clearer.

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Binary Capability Filter Pattern (appears 4+ times)

**Pattern:**
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_no_X', True)
if not show_has or not show_not:
    has_capability = capability_check_function(ship)
    if has_capability and not show_has:
        continue/return False
    if not has_capability and not show_not:
        continue/return False
```

**Extraction:**
```python
def _passes_binary_filter(
    ship: ShipInstance,
    filter_state: Dict[str, bool],
    has_key: str,
    not_key: str,
    capability_check: Callable[[ShipInstance], bool]
) -> bool:
    """Check if ship passes a binary has/has-not filter."""
    show_has = filter_state.get(has_key, True)
    show_not = filter_state.get(not_key, True)

    if show_has and show_not:
        return True  # No filtering active

    has_capability = capability_check(ship)

    if has_capability:
        return show_has
    else:
        return show_not
```

**Impact:** This single extraction handles:
- Warp capability filter
- Spaceyard capability filter
- Cargo filter
- Each special capability filter

### 4.2 Special Capability Loop Can Use Same Helper

The special capability loop (lines 176-194) can be refactored to use the same binary filter helper:

```python
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    has_key = f'show_{col_id}'
    not_key = f'show_{col_id.replace("can_", "no_", 1)}'
    check_fn = lambda s, name=ability_name: FleetCapabilityCalculator.ship_has_ability(s, name)

    if not _passes_binary_filter(ship, filter_state, has_key, not_key, check_fn):
        return False  # or _skip = True; break
```

---

## 5. Data Transformations That Could Be Separated

### 5.1 Ship Status Classification

**Current:** Mixed with filtering logic (lines 196-220)

**Extract to:**
```python
def _get_ship_status(ship: ShipInstance) -> str:
    """Classify ship into one of four status categories."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

**Impact:** Reduces main function complexity by 4 CC (the chain of if/elif).

### 5.2 Filter Configuration Pre-processing

The filter state is accessed repeatedly with defaults. Consider pre-processing:

```python
@dataclass
class FilterConfig:
    """Pre-processed filter configuration."""
    show_warp: bool = True
    show_not_warp: bool = True
    show_has_yard: bool = True
    show_no_yard: bool = True
    # ... etc

    @classmethod
    def from_state(cls, filter_state: Dict[str, bool]) -> 'FilterConfig':
        return cls(
            show_warp=filter_state.get('show_warp_capable', True),
            # ...
        )
```

This is optional but improves readability.

---

## Recommended Extraction Plan

### Phase 1: Extract Binary Filter Helper (~-16 CC)

Create `_passes_binary_filter()` helper and apply to all 4 capability filters.

**Expected CC reduction:** From 36 to ~20

### Phase 2: Extract Status Classification (~-4 CC)

Create `_get_ship_status()` helper.

**Expected CC reduction:** From ~20 to ~16

### Phase 3: Convert to Predicate Pattern (optional, cleaner code)

Convert the main loop to use `_ship_passes_filters()` predicate.

**Expected CC:** ~14-16

---

## Proposed Refactored Structure

```python
def _passes_binary_filter(
    ship: ShipInstance,
    filter_state: Dict[str, bool],
    has_key: str,
    not_key: str,
    capability_check: Callable[[ShipInstance], bool]
) -> bool:
    """Check if ship passes a binary has/has-not capability filter."""
    show_has = filter_state.get(has_key, True)
    show_not = filter_state.get(not_key, True)

    if show_has and show_not:
        return True

    has_capability = capability_check(ship)
    return show_has if has_capability else show_not


def _get_ship_status(ship: ShipInstance) -> str:
    """Classify ship status: destroyed, derelict, damaged, or undamaged."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'


def _ship_passes_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Return True if ship passes all active filters."""
    # Warp filter
    if not _passes_binary_filter(
        ship, filter_state,
        'show_warp_capable', 'show_not_warp_capable',
        ShipStatsCalculator.has_warp_capability
    ):
        return False

    # Spaceyard filter
    if not _passes_binary_filter(
        ship, filter_state,
        'show_has_spaceyard', 'show_no_spaceyard',
        FleetCapabilityCalculator.ship_has_spaceyard
    ):
        return False

    # Cargo filter
    if not _passes_binary_filter(
        ship, filter_state,
        'show_has_cargo', 'show_no_cargo',
        lambda s: bool(s.cargo_contents) and sum(s.cargo_contents.values()) > 0
    ):
        return False

    # Special capability filters
    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        has_key = f'show_{col_id}'
        not_key = f'show_{col_id.replace("can_", "no_", 1)}'
        check_fn = lambda s, n=ability_name: FleetCapabilityCalculator.ship_has_ability(s, n)

        if not _passes_binary_filter(ship, filter_state, has_key, not_key, check_fn):
            return False

    # Status filter
    status = _get_ship_status(ship)
    return filter_state.get(f'show_{status}', True)


def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """Filter ships based on status filter state."""
    return [ship for ship in ships if _ship_passes_filters(ship, filter_state)]
```

---

## Complexity Estimate After Refactoring

| Function | Estimated CC |
|----------|--------------|
| `_passes_binary_filter` | 3 |
| `_get_ship_status` | 4 |
| `_ship_passes_filters` | 8-10 |
| `filter_ships` | 2 |
| **Total distributed** | 17-19 |

**Target achieved:** Main function `filter_ships` drops to CC 2, with complexity distributed across focused helper functions.
