# Structure Analysis: `filter_ships` Function

**File:** `C:\Dev\Starship Battles\game\ui\screens\fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Current Cyclomatic Complexity:** 36

---

## Overview

The `filter_ships` function filters a list of `ShipInstance` objects based on a `filter_state` dictionary containing boolean flags. The function iterates through each ship and applies multiple filter categories, using `continue` statements to skip ships that don't match the criteria.

---

## 1. Branches/Conditions Contributing Most to Complexity

### High-Impact Complexity Sources

| Filter Category | Lines | Branch Count | Notes |
|-----------------|-------|--------------|-------|
| **Special Capability Loop** | 177-194 | 10+ | Loop over 5 SPECIAL_CAPABILITY_COLUMNS, each with 2 conditional checks |
| **Warp Filter** | 143-153 | 4 | Outer guard + 2 inner conditions |
| **Spaceyard Filter** | 155-164 | 4 | Outer guard + 2 inner conditions |
| **Cargo Filter** | 166-174 | 4 | Outer guard + 2 inner conditions |
| **Status Filters** | 196-220 | 8 | 4 mutually exclusive status checks, each with nested filter check |

### Breakdown by Category

1. **Special Capability Loop (Lines 177-194)** - **Highest contributor**
   - Iterates over `SPECIAL_CAPABILITY_COLUMNS` (5 items)
   - Each iteration has:
     - Guard condition: `if not show_has or not show_not`
     - Two exclusion checks: `if has_ability and not show_has` / `if not has_ability and not show_not`
   - Uses `_skip` flag and `break` to exit early
   - Contributes ~15 to complexity (loop + 3 conditions per iteration)

2. **Binary Capability Filters (Warp, Spaceyard, Cargo)** - Lines 143-174
   - Each follows identical pattern: guard + two exclusion branches
   - Contributes 4 branches each = 12 total

3. **Status Hierarchy (Destroyed, Derelict, Damaged, Undamaged)** - Lines 196-220
   - Mutually exclusive checks with early returns
   - Each status has: condition check + filter check + append + continue
   - Contributes 8 branches

---

## 2. Nested Conditionals That Could Be Flattened

### Pattern A: Guard + Double Exclusion (Repeated 4 times)

```python
# Current pattern (lines 143-153, repeated for warp/spaceyard/cargo)
show_warp = filter_state.get('show_warp_capable', True)
show_not_warp = filter_state.get('show_not_warp_capable', True)
if not show_warp or not show_not_warp:
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        continue
    if not is_warp_capable and not show_not_warp:
        continue
```

**Issue:** Nested conditionals inside guard condition.
**Flattening opportunity:** Extract to predicate function that returns `True` (pass) or `False` (skip).

### Pattern B: Loop with Skip Flag (Lines 177-194)

```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    show_has = filter_state.get(f'show_{col_id}', True)
    no_key = col_id.replace('can_', 'no_', 1)
    show_not = filter_state.get(f'show_{no_key}', True)
    if not show_has or not show_not:
        # ... check and set _skip = True, break
if _skip:
    continue
```

**Issue:** Uses mutable flag + break + post-loop check.
**Flattening opportunity:** Extract to function returning boolean.

### Pattern C: Status Cascade (Lines 196-220)

```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue

if ship.is_derelict:
    if not filter_state.get('show_derelict', True):
        continue
    result.append(ship)
    continue
# ... continues for damaged/undamaged
```

**Issue:** Each status has nested filter check, then append, then continue.
**Flattening opportunity:** Determine ship status once, then single lookup.

---

## 3. Early Returns That Could Simplify Logic

### Current Structure

The function uses a single loop with `continue` statements to skip non-matching ships. This is the opposite of early-return - it's "late-append".

### Opportunities for Early Returns

1. **Empty ships list** - No early return exists; would skip entire loop.
   ```python
   if not ships:
       return []
   ```

2. **All filters enabled** - Could detect "no filtering needed" and return early.
   ```python
   if _all_filters_enabled(filter_state):
       return list(ships)
   ```

3. **Convert loop to filter comprehension** - After extracting predicates:
   ```python
   return [ship for ship in ships if _passes_all_filters(ship, filter_state)]
   ```

---

## 4. Repeated Patterns That Could Be Extracted

### Pattern 1: Binary Filter Check (3 occurrences)

**Current:** Lines 143-153, 155-164, 166-174

```python
show_has = filter_state.get('show_{capability}', True)
show_not = filter_state.get('show_no_{capability}', True)
if not show_has or not show_not:
    has_capability = check_function(ship)
    if has_capability and not show_has:
        continue
    if not has_capability and not show_not:
        continue
```

**Extraction:** Single helper function

```python
def _passes_binary_filter(
    filter_state: Dict[str, bool],
    has_key: str,
    not_key: str,
    has_capability: bool
) -> bool:
    """Return True if ship passes the binary filter, False to exclude."""
    show_has = filter_state.get(has_key, True)
    show_not = filter_state.get(not_key, True)
    if show_has and show_not:
        return True  # No filtering
    if has_capability:
        return show_has
    return show_not
```

### Pattern 2: Status-to-Filter Mapping

**Current:** Lines 196-220 - Cascading if/elif for status determination

**Extraction:** Map ship status to filter key

```python
def _get_ship_status_filter_key(ship: ShipInstance) -> str:
    """Return the filter key for ship's current status."""
    if not ship.is_alive:
        return 'show_destroyed'
    if ship.is_derelict:
        return 'show_derelict'
    if ship.is_damaged():
        return 'show_damaged'
    return 'show_undamaged'
```

### Pattern 3: Import-and-Check (4 occurrences)

**Current:** Repeated late imports of `FleetCapabilityCalculator`

```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
```

**Extraction:** Move import to module level or create wrapper function that handles import once.

---

## 5. Data Transformations That Could Be Separated

### Transformation 1: Filter State Normalization

**Current:** Each filter check calls `filter_state.get(key, True)` with default.

**Separation opportunity:** Pre-process filter state once at function start:

```python
def _normalize_filter_state(filter_state: Dict[str, bool]) -> Dict[str, bool]:
    """Ensure all filter keys have explicit boolean values."""
    defaults = {
        'show_warp_capable': True,
        'show_not_warp_capable': True,
        'show_has_spaceyard': True,
        'show_no_spaceyard': True,
        # ... all other keys
    }
    return {**defaults, **filter_state}
```

### Transformation 2: Ship Capability Pre-computation

**Current:** Capability checks (warp, spaceyard, cargo, special abilities) computed per-ship inline.

**Separation opportunity:** Compute all capabilities upfront if any filter needs them:

```python
@dataclass
class ShipCapabilities:
    is_warp_capable: bool
    has_spaceyard: bool
    has_cargo: bool
    special_abilities: Dict[str, bool]  # col_id -> has_ability
    status_key: str  # 'show_destroyed', 'show_derelict', etc.
```

### Transformation 3: Filter Key Generation for Special Capabilities

**Current:** String manipulation inline (line 182):
```python
no_key = col_id.replace('can_', 'no_', 1)
```

**Separation opportunity:** Pre-compute mapping:

```python
SPECIAL_CAPABILITY_FILTER_KEYS = {
    'can_destroy_planet': ('show_can_destroy_planet', 'show_no_destroy_planet'),
    'can_open_warp': ('show_can_open_warp', 'show_no_open_warp'),
    # ...
}
```

---

## Summary: Recommended Refactoring Strategy

### Priority 1: Extract Binary Filter Helper (Highest Impact)
- Reduces 12+ branches to 4 function calls
- Eliminates duplicate guard + exclusion pattern

### Priority 2: Extract Status Filter Logic
- Convert cascading if/elif to single status lookup + filter check
- Reduces 8 branches to 2

### Priority 3: Extract Special Capability Filter
- Replace loop + flag + break with single function call
- Reduces ~15 branches to 1 function call

### Priority 4: Separate Data Transformations
- Pre-normalize filter state
- Consider pre-computing ship capabilities

### Expected Complexity Reduction

| Refactoring | Estimated CC Reduction |
|-------------|------------------------|
| Binary filter extraction | -8 to -10 |
| Status filter extraction | -6 |
| Special capability extraction | -10 to -12 |
| **Total** | **-24 to -28** |

**Target Complexity:** 8-12 (down from 36)
