# Structure Analysis: filter_ships

## Complexity Breakdown

The `filter_ships` function (lines 124-222) has 98 lines and exhibits the following complexity sources:

1. **Multiple Binary Filter Patterns (5 instances)**: Lines 144-194 contain five nearly identical filter blocks for binary capabilities (warp, spaceyard, cargo, plus special capabilities loop). Each follows the same pattern: check two booleans, compute capability, skip if excluded.

2. **Cascading Status Filter Chain (4 states)**: Lines 196-220 handle mutually exclusive ship states (destroyed, derelict, damaged, undamaged) as a sequential if-else chain with early returns.

3. **Late/Repeated Imports Inside Loop**: Lines 159-160 and 185-186 import `FleetCapabilityCalculator` inside conditional blocks, with the import potentially occurring multiple times per ship iteration.

4. **Mixed Control Flow**: The function uses both `continue` statements (to skip ships) and explicit `result.append()` calls scattered throughout, making the flow difficult to trace.

5. **Special Capability Loop with Flag Variable**: Lines 177-194 use a `_skip` flag variable and `break` to exit the loop, adding another layer of control flow complexity.

## Pattern Analysis

### Repeated Patterns

**Binary Filter Pattern** (appears 4 times + loop):
```python
show_has = filter_state.get('show_X', True)
show_not = filter_state.get('show_no_X', True)
if not show_has or not show_not:
    has_capability = <check_capability>(ship)
    if has_capability and not show_has:
        continue
    if not has_capability and not show_not:
        continue
```

Occurrences:
- Lines 144-153: Warp capability filter
- Lines 156-164: Spaceyard capability filter
- Lines 167-174: Cargo filter
- Lines 178-192: Special capabilities (inside loop)

**Status Filter Pattern** (appears 4 times):
```python
if ship.<status_check>:
    if not filter_state.get('show_<status>', True):
        continue
    result.append(ship)
    continue
```

Occurrences:
- Lines 197-201: Destroyed check
- Lines 204-208: Derelict check
- Lines 211-215: Damaged check
- Lines 218-220: Undamaged (default case)

### Nested Conditionals

1. **Lines 148-153**: Two-level nesting for warp filter check
   ```python
   if not show_warp or not show_not_warp:
       is_warp_capable = ...
       if is_warp_capable and not show_warp:
           continue
       if not is_warp_capable and not show_not_warp:
           continue
   ```

2. **Lines 158-164**: Two-level nesting for spaceyard filter

3. **Lines 169-174**: Two-level nesting for cargo filter

4. **Lines 184-192**: Three-level nesting (loop + filter check + capability check):
   ```python
   for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
       if not show_has or not show_not:
           has_ability = ...
           if has_ability and not show_has:
               ...
   ```

5. **Lines 197-201**: Two-level nesting for destroyed status:
   ```python
   if not ship.is_alive:
       if not filter_state.get('show_destroyed', True):
           continue
   ```

### Early Return Opportunities

1. **Lines 141-142**: Could add early return if `filter_state` is empty or all filters are True (no filtering needed).

2. **Lines 144-145**: Reading filter state values inside the loop is inefficient. These could be read once before the loop.

3. **Status cascade (196-220)**: The current cascade uses `continue` after `append`, but this could be simplified using a single status determination followed by a lookup.

## Extraction Candidates

### Candidate 1: Binary Filter Checker (Lines 144-194)
Extract a helper function to handle the binary filter pattern:
```python
def _passes_binary_filter(
    ship: ShipInstance,
    show_has: bool,
    show_not: bool,
    capability_checker: Callable[[ShipInstance], bool]
) -> bool:
```
This would eliminate ~40 lines of repetitive code.

### Candidate 2: Ship Status Classifier (Lines 196-220)
Extract the mutually exclusive status determination:
```python
def _get_ship_status(ship: ShipInstance) -> str:
    """Return 'destroyed', 'derelict', 'damaged', or 'undamaged'."""
```
Then the filter check becomes a simple lookup: `filter_state.get(f'show_{status}', True)`

### Candidate 3: Special Capability Filter (Lines 176-194)
Extract the special capability loop into its own function:
```python
def _passes_special_capability_filters(
    ship: ShipInstance,
    filter_state: Dict[str, bool]
) -> bool:
```

### Candidate 4: Warp Filter (Lines 143-153)
Extract to:
```python
def _passes_warp_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
```

### Candidate 5: Cargo Filter (Lines 166-174)
Extract to:
```python
def _passes_cargo_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
```

## Recommended Simplifications

1. **Extract `_passes_binary_filter()` helper** (High Impact)
   - Consolidates the repeated binary filter pattern into a single reusable function
   - Reduces ~40 lines to ~8 lines in main function
   - Makes the pattern explicit and testable

2. **Extract `_get_ship_status()` classifier** (Medium Impact)
   - Replaces the 4-branch cascade with a single status determination
   - Enables data-driven filter lookup instead of cascading conditionals
   - Makes status hierarchy explicit (destroyed > derelict > damaged > undamaged)

3. **Hoist filter state reads outside loop** (Low Complexity, High Clarity)
   - Read all `filter_state.get()` calls once before the loop
   - Move imports (`FleetCapabilityCalculator`) to function top
   - Reduces repeated dictionary lookups per ship

4. **Use filter chain with early bailout** (Medium Impact)
   - Replace scattered `continue` statements with a list of filter functions
   - `all(f(ship) for f in filters)` pattern provides clear bailout semantics

5. **Convert status filter to lookup table** (Medium Impact)
   - Map status strings to filter state keys
   - `FILTER_KEYS = {'destroyed': 'show_destroyed', 'derelict': 'show_derelict', ...}`
   - Single conditional instead of cascading if-statements

### Recommended Implementation Order

1. Hoist filter state reads and imports (simplest, no behavior change)
2. Extract `_get_ship_status()` classifier (clarifies status logic)
3. Extract `_passes_binary_filter()` helper (biggest deduplication win)
4. Apply binary filter helper to all capability filters
5. Refactor main loop to use filter chain pattern

This approach maintains testability at each step and allows incremental verification that behavior is preserved.
