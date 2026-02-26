# PROJ-229: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Target Function Overview
- **File:** `game/ui/screens/fleet_report_filters.py`
- **Function:** `filter_ships` (lines 124-222)
- **Current CC:** 36 (Grade F)
- **Target CC:** < 20
- **Length:** 99 lines

### Complexity Breakdown

| Source | Branches | Notes |
|--------|----------|-------|
| Warp capability filter | 4 | Boolean pair pattern |
| Spaceyard filter | 4 | Boolean pair pattern |
| Cargo filter | 4 | Boolean pair pattern |
| Special capability loop | ~20 | 5 capabilities × 4 branches |
| Status filters | 8 | Destroyed/Derelict/Damaged/Undamaged cascade |

## Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

### Architecture

**Structure Analysis:**
- Repeated boolean pair filter pattern appears 6+ times
- Same 4-branch structure for each show/hide filter dimension
- Special capability loop contains nested complexity with `_skip` flag
- Status filters implement a mutually exclusive hierarchy

**Dependency Analysis:**
- Single production caller: `FleetListViewModel._refresh()`
- Pure function with no side effects
- Interface can remain stable (dict-based `filter_state`)
- 43+ tests provide comprehensive coverage

**Safety Analysis:**
- Status hierarchy is CRITICAL: destroyed > derelict > damaged > undamaged
- Derelict ships must NOT match the damaged filter
- Order preservation required
- Missing tests for edge cases and invariants

### Key Patterns to Reuse

- **Boolean pair filter pattern**: `lines 144-153` - Used for warp, spaceyard, cargo filters
  ```python
  show_X = filter_state.get('show_X', True)
  show_not_X = filter_state.get('show_not_X', True)
  if not show_X or not show_not_X:
      has_X = <check>
      if has_X and not show_X: continue
      if not has_X and not show_not_X: continue
  ```

- **Status cascade pattern**: `lines 196-220` - Mutually exclusive status classification
  ```python
  if not ship.is_alive:  # Destroyed
  elif ship.is_derelict:  # Derelict (NOT damaged)
  elif ship.is_damaged(): # Damaged
  else:                   # Undamaged
  ```

### Dependencies & Risks

1. **Status mutual exclusivity** - HIGH RISK
   - Derelict ships must NOT match damaged filter
   - Destroyed ships must NOT match derelict filter
   - Mitigation: Extract `_get_ship_status()` returning single status string

2. **Late imports** - MEDIUM RISK
   - `FleetCapabilityCalculator` imported inside conditionals
   - Mitigation: Keep imports inside helper functions

3. **Special capability key derivation** - LOW RISK
   - Dynamic key construction using `.replace('can_', 'no_', 1)`
   - Mitigation: Preserve exact logic in extracted helper

### Opportunities Discovered

- Generic `_passes_boolean_filter()` helper can eliminate ~16 branches
- Status determination can be separated from filtering
- List comprehension with predicate functions is cleaner than manual loop

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

---

## Refactoring Strategy

### Approach: Extract Predicate Helpers

Transform the monolithic function into a composition of focused predicate functions:

```python
# Before: Single 99-line function with CC 36
def filter_ships(ships, filter_state):
    result = []
    for ship in ships:
        # 36 branches of filter logic...
        result.append(ship)
    return result

# After: Composed predicates with CC ~6 main + helpers
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

### Helper Function Signatures

```python
def _passes_boolean_filter(has_attribute: bool, show_has: bool, show_not: bool) -> bool:
    """Generic boolean pair filter logic. Returns True if ship should be included."""

def _passes_warp_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes warp capability filters."""

def _passes_spaceyard_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes spaceyard capability filters."""

def _passes_cargo_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes cargo presence filters."""

def _passes_special_ability_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes all special ability filters."""

def _get_ship_status(ship: ShipInstance) -> str:
    """Return ship status: 'destroyed', 'derelict', 'damaged', or 'undamaged'."""

def _passes_status_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes status filters based on its determined status."""
```

### Expected Complexity After Refactoring

| Function | Expected CC |
|----------|-------------|
| `filter_ships` (main) | 6 |
| `_passes_boolean_filter` | 4 |
| `_passes_warp_filter` | 3 |
| `_passes_spaceyard_filter` | 3 |
| `_passes_cargo_filter` | 3 |
| `_passes_special_ability_filters` | 6 |
| `_get_ship_status` | 4 |
| `_passes_status_filter` | 2 |

**Total distributed:** ~31 across 8 functions (avg 4 each)
**Main function:** 6 (target achieved)

---

## Test Fortification Requirements

**Must add before refactoring:**
1. Empty ships list handling
2. Empty filter_state defaults to all True
3. Derelict-not-damaged invariant
4. Destroyed-not-derelict invariant
5. Both filter pairs False edge case
6. Order preservation
7. Input non-mutation

These tests will catch any behavioral regressions during refactoring.
