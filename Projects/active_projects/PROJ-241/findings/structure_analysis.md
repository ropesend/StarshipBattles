# Structure Analysis: `filter_ships` Function

**File:** `game/ui/screens/fleet_report_filters.py`
**Lines:** 124-222
**Function:** `filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]`

---

## 1. Branches/Conditions Contributing Most to Complexity

### 1.1 Binary Filter Pattern (Repeated 4+ Times)
The function uses a repeated pattern for binary filters (has/doesn't have):
```python
show_X = filter_state.get('show_X', True)
show_not_X = filter_state.get('show_not_X', True)
if not show_X or not show_not_X:
    has_X = <expensive_check>
    if has_X and not show_X:
        continue
    if not has_X and not show_not_X:
        continue
```

This pattern appears for:
- **Warp capability** (lines 144-153)
- **Spaceyard capability** (lines 156-164)
- **Cargo filter** (lines 167-174)
- **Special capability filters** (lines 176-194) - looped over 5 abilities

Each instance adds 2-3 conditional branches.

### 1.2 Status Filter Cascade (Lines 196-220)
The mutually-exclusive status checks form a cascade:
```python
if not ship.is_alive:        # destroyed
    ...
if ship.is_derelict:         # derelict
    ...
if ship.is_damaged():        # damaged
    ...
# else: undamaged
```

This creates 4 execution paths with interleaved filter checks and `result.append()` calls.

### 1.3 Special Capability Loop (Lines 176-194)
Iterates over `SPECIAL_CAPABILITY_COLUMNS` (5 items), checking each ability with the binary filter pattern. Uses a `_skip` flag to break out of the loop and signal the outer loop to continue.

---

## 2. Nested Conditionals That Could Be Flattened

### 2.1 Binary Filter Check Nesting
```python
if not show_warp or not show_not_warp:           # Level 1
    is_warp_capable = ...
    if is_warp_capable and not show_warp:        # Level 2
        continue
    if not is_warp_capable and not show_not_warp:  # Level 2
        continue
```

The inner checks could be combined with boolean logic:
```python
should_skip = (is_warp_capable and not show_warp) or (not is_warp_capable and not show_not_warp)
```

### 2.2 Special Capability Loop Skip Flag
```python
_skip = False
for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
    ...
    if has_ability and not show_has:
        _skip = True
        break
    if not has_ability and not show_not:
        _skip = True
        break
if _skip:
    continue
```

The `_skip` flag pattern adds complexity. This could be refactored into a helper function that returns a boolean.

### 2.3 Status Cascade with Embedded Filter Checks
```python
if not ship.is_alive:
    if not filter_state.get('show_destroyed', True):
        continue
    result.append(ship)
    continue
```

Each status check has an embedded filter check. The status determination and filtering are intertwined.

---

## 3. Early Returns That Could Simplify Logic

### 3.1 Empty Input Check (Already Present)
The function does not have an early return for empty input, though this is minor since the loop simply won't execute.

### 3.2 Filter Predicate Functions
Converting filter checks to predicate functions would enable early returns within each predicate:
```python
def passes_warp_filter(ship, filter_state) -> bool:
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)
    if show_warp and show_not_warp:
        return True  # Early return - no filtering needed
    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    return (is_warp_capable and show_warp) or (not is_warp_capable and show_not_warp)
```

### 3.3 Status Classification Early Return
The status cascade could be simplified by first classifying the ship status, then applying a single filter lookup.

---

## 4. Repeated Patterns That Could Be Extracted

### 4.1 Binary Capability Filter Pattern
**Appears 4 times** with identical structure:
1. Warp capability (lines 144-153)
2. Spaceyard capability (lines 156-164)
3. Cargo filter (lines 167-174)
4. Each special capability in loop (lines 181-192)

**Extractable as:**
```python
def _passes_binary_filter(
    has_capability: bool,
    show_has: bool,
    show_not: bool
) -> bool:
    """Return True if ship passes a binary (has/hasn't) filter."""
    if show_has and show_not:
        return True
    return (has_capability and show_has) or (not has_capability and show_not)
```

### 4.2 Filter State Lookup with Default True
**Appears 12+ times:**
```python
filter_state.get('show_X', True)
```

Could use a helper or partial application for cleaner code.

### 4.3 Late Import Pattern
**Appears twice:**
```python
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
```

The import is inside conditional blocks (lines 159, 185) and could be moved to module level or a lazy-loaded helper.

### 4.4 Status Filter + Append + Continue Pattern
**Appears 4 times:**
```python
if not filter_state.get('show_X', True):
    continue
result.append(ship)
continue
```

---

## 5. Data Transformations That Could Be Separated

### 5.1 Capability Detection (Pure Data Extraction)
Several capability checks are currently inline but could be pre-computed:
- `ShipStatsCalculator.has_warp_capability(ship)` - warp detection
- `FleetCapabilityCalculator.ship_has_spaceyard(ship)` - spaceyard detection
- `FleetCapabilityCalculator.ship_has_ability(ship, ability_name)` - special abilities
- `bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0` - cargo detection

These could be extracted into a ship capabilities data structure:
```python
@dataclass
class ShipFilterData:
    ship: ShipInstance
    is_warp_capable: bool
    has_spaceyard: bool
    has_cargo: bool
    special_abilities: Dict[str, bool]  # ability_name -> has_it
    status: Literal['destroyed', 'derelict', 'damaged', 'healthy']
```

### 5.2 Status Classification
Ship status is implicitly determined through cascade:
```python
not ship.is_alive    -> destroyed
ship.is_derelict     -> derelict
ship.is_damaged()    -> damaged
else                 -> healthy/undamaged
```

This could be a separate function:
```python
def classify_ship_status(ship: ShipInstance) -> str:
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'healthy'
```

### 5.3 Filter Key Derivation for Special Capabilities
The key transformation logic (lines 179-183) could be extracted:
```python
# Current inline:
show_has = filter_state.get(f'show_{col_id}', True)
no_key = col_id.replace('can_', 'no_', 1)
show_not = filter_state.get(f'show_{no_key}', True)
```

### 5.4 Separate Filter Configuration from Application
The function mixes:
1. Reading filter configuration (`filter_state.get(...)`)
2. Computing ship properties (capability checks)
3. Applying filter logic (boolean decisions)
4. Building result list (`result.append()`)

These could be separated into:
- **Filter config reader:** Extract relevant filter settings
- **Ship capability analyzer:** Compute all capabilities for a ship
- **Filter predicate:** Pure function `(capabilities, config) -> bool`
- **List builder:** Simple list comprehension

---

## Summary of Complexity Drivers

| Category | Count | Complexity Impact |
|----------|-------|-------------------|
| Binary filter patterns | 4 | High - each adds 3+ branches |
| Special capability loop | 1 | High - nested loop with flag |
| Status cascade | 4 states | Medium - sequential checks |
| Inline imports | 2 | Low - but indicates tight coupling |
| Magic string keys | 12+ | Medium - error-prone, hard to track |

**Estimated Cyclomatic Complexity:** 18-22 (based on branch count)

**Primary Refactoring Opportunities:**
1. Extract binary filter pattern to helper function
2. Pre-compute ship capabilities before filtering
3. Replace status cascade with lookup table
4. Convert to list comprehension with predicate function
