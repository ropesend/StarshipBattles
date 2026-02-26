# PROJ-240: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target:** `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
- Lines: 124-222 (99 lines)
- Cyclomatic Complexity: 36 (grade F)
- Goal: Reduce to below 20

## Swarm Findings Summary

Combined analysis from three parallel review agents:

| Agent | Focus | Key Finding |
|-------|-------|-------------|
| Structure | Control flow | Binary filter pattern repeated 5x (~15 CC points) |
| Dependency | Callers & tests | Single caller, no side effects, 20+ tests |
| Safety | Risks & invariants | Filter order critical; add edge case tests first |

### Architecture

The function is a pure filter with no side effects:
- Input: `List[ShipInstance]` + `Dict[str, bool]` filter state
- Output: New `List[ShipInstance]` (references, not copies)
- Caller: `FleetListViewModel._refresh()` (single production caller)

### Key Patterns to Reuse

- **Binary Filter Pattern**: `lines 144-194` - Same structure for warp/spaceyard/cargo/special
  ```python
  show_has = filter_state.get('show_X', True)
  show_not = filter_state.get('show_no_X', True)
  if not show_has or not show_not:
      has_capability = <check>
      if has_capability and not show_has: continue
      if not has_capability and not show_not: continue
  ```

- **Status Filter Chain**: `lines 196-220` - Mutually exclusive status classification
  ```python
  if not ship.is_alive: ...    # destroyed
  elif ship.is_derelict: ...   # derelict
  elif ship.is_damaged(): ...  # damaged
  else: ...                    # undamaged
  ```

### Dependencies & Risks

1. **Filter Order** - Evaluation order is: Warp → Spaceyard → Cargo → Special → Status
   - Mitigation: Preserve order in extracted helpers

2. **Status Priority** - Destroyed → Derelict → Damaged → Undamaged (mutually exclusive)
   - Mitigation: Extract status classifier preserving priority

3. **Late Imports** - `FleetCapabilityCalculator` imported inside function to avoid circular imports
   - Mitigation: Keep late imports in helper functions

4. **String Key Derivation** - Special capability keys derived via string manipulation
   - Mitigation: Extract to helper, add explicit test

### Opportunities Discovered

- **High Impact:** Extract `_passes_binary_filter()` helper - eliminates ~40 lines of duplication
- **Medium Impact:** Extract `_get_ship_status()` classifier - simplifies status filter
- **Low Impact:** Add early return for empty ships list

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

---

## Refactoring Strategy

### Approach: Extract Helper Functions

Extract repeated patterns into small, focused helper functions:

```
filter_ships (CC ~6)
├── _passes_binary_filter (CC 3)
├── _passes_warp_filter (CC 2)
├── _passes_spaceyard_filter (CC 2)
├── _passes_cargo_filter (CC 2)
├── _passes_special_capability_filters (CC 5)
├── _get_ship_status (CC 4)
└── _passes_status_filter (CC 3)
```

### Target Structure

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """Filter ships based on status filter state."""
    result = []
    for ship in ships:
        if not _passes_warp_filter(ship, filter_state):
            continue
        if not _passes_spaceyard_filter(ship, filter_state):
            continue
        if not _passes_cargo_filter(ship, filter_state):
            continue
        if not _passes_special_capability_filters(ship, filter_state):
            continue
        if not _passes_status_filter(ship, filter_state):
            continue
        result.append(ship)
    return result
```

### Expected CC Reduction

| Function | CC |
|----------|-----|
| `filter_ships` (main) | ~6 |
| `_passes_binary_filter` | 3 |
| `_passes_warp_filter` | 2 |
| `_passes_spaceyard_filter` | 2 |
| `_passes_cargo_filter` | 2 |
| `_passes_special_capability_filters` | 5 |
| `_get_ship_status` | 4 |
| `_passes_status_filter` | 3 |

**Main function target:** CC < 10 (from 36)

---

## Critical Invariants

### MUST PRESERVE

1. **Filter Evaluation Order:**
   ```
   Warp → Spaceyard → Cargo → Special Abilities → Status
   ```

2. **Status Priority Order:**
   ```
   Destroyed → Derelict → Damaged → Undamaged
   ```

3. **Default True Behavior:**
   ```python
   filter_state.get('show_xxx', True)  # Missing = show
   ```

4. **Late Imports Location:**
   ```python
   # Inside helper functions, NOT at module level
   from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
   ```

5. **Return Semantics:**
   - New list containing references to original ships
   - Empty input → empty output

---

## Files to Modify

| File | Changes |
|------|---------|
| `game/ui/screens/fleet_report_filters.py` | Extract helpers, refactor main function |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Add edge case tests |
