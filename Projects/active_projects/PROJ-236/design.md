# PROJ-236: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Target Function Analysis

**File:** `game/ui/screens/fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Current CC:** 36 (Grade F)
**Goal:** Reduce to below 20

## Swarm Findings Summary

### Structure Analysis
The function has 5 major complexity sources:
1. **5 repeated binary filter patterns** (warp, spaceyard, cargo, special capabilities) - each follows identical `show_has`/`show_not` logic
2. **4-way cascading status filter chain** (destroyed > derelict > damaged > undamaged)
3. **Late imports inside conditional blocks** that execute per-ship
4. **Mixed control flow** with 8 `continue` statements scattered throughout
5. **Special capability loop with flag variable** for early exit

### Dependency Analysis
- **Single caller:** `FleetListViewModel._refresh()` in `fleet_report_view_model.py`
- **Pure function:** No side effects, returns new list
- **Interface stable:** Signature and 20 filter keys must be preserved
- **Test coverage:** ~25 dedicated tests across 5 test classes

### Safety Analysis
- **Edge cases handled:** Empty input, missing keys (default True), cargo edge cases
- **Critical invariant:** Status priority hierarchy (destroyed > derelict > damaged > undamaged)
- **Risk areas:** Status cascade logic, late imports inside loop, dynamic filter key derivation
- **Verdict:** SAFE TO REFACTOR

## Architecture

### Key Patterns to Reuse

- **Binary Filter Pattern**: Lines 144-153, 156-164, 167-174 - `show_has`/`show_not` checks with capability evaluation
- **Status Priority Cascade**: Lines 196-220 - destroyed > derelict > damaged > undamaged
- **Late Import Pattern**: Lines 159, 185 - `FleetCapabilityCalculator` imported inside conditionals

### Dependencies & Risks

1. **Circular Import Risk** - `FleetCapabilityCalculator` cannot be imported at module level; keep late imports
2. **Status Priority Order** - Must preserve destroyed > derelict > damaged > undamaged hierarchy
3. **Filter Key Names** - All 20 filter keys must continue working with same semantics

## Refactoring Strategy

### Approach: Extract Filter Predicates + Filter Chain Pattern

Transform the 99-line function into a clean filter chain by:
1. Adding safety tests for edge cases
2. Extracting each filter category into a predicate function
3. Hoisting imports and filter state reads outside the loop
4. Replacing the cascading status checks with a status classifier
5. Composing filters using list comprehension with predicates

### Expected CC Reduction

| Component | Current CC | After Extraction |
|-----------|------------|------------------|
| Warp filter block | ~4 | 2 (helper) |
| Spaceyard filter block | ~4 | 2 (helper) |
| Cargo filter block | ~4 | 2 (helper) |
| Special capabilities loop | ~8 | 4 (helper) |
| Status cascade | ~8 | 3 (classifier + lookup) |
| Main function | 36 | ~8 (filter chain) |

**Expected final CC:** 8-12 (well below threshold of 20)

### Helper Functions to Extract

1. **`_passes_binary_filter(has_capability, show_has, show_not)`**
   - Generic helper for the repeated binary filter pattern
   - Returns True if ship passes the filter

2. **`_get_ship_status(ship)`**
   - Returns: `'destroyed'`, `'derelict'`, `'damaged'`, or `'undamaged'`
   - Encapsulates the priority hierarchy

3. **`_passes_status_filter(ship, filter_state)`**
   - Uses status classifier + lookup
   - Replaces 25-line cascade with 5 lines

4. **`_passes_capability_filters(ship, filter_state)`**
   - Handles warp, spaceyard, cargo filters
   - Hoists imports outside the per-ship loop

5. **`_passes_special_capability_filters(ship, filter_state)`**
   - Handles the SPECIAL_CAPABILITY_COLUMNS loop
   - Isolates the dynamic key derivation logic

### Target Structure

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """Filter ships based on status filter state."""
    return [
        ship for ship in ships
        if _passes_capability_filters(ship, filter_state)
        and _passes_special_capability_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
