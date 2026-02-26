# PROJ-230: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Synthesized Analysis

### Function Overview
- **File:** `game/ui/screens/fleet_report_filters.py`
- **Function:** `filter_ships` (lines 124-222)
- **Current CC:** 36 (Grade F)
- **Target CC:** <20
- **Length:** 99 lines

### Multi-Agent Review Synthesis

**Structure Analysis:**
- 5 distinct boolean filter pair blocks (warp, spaceyard, cargo, special capabilities, status)
- Each filter pair contributes ~4 branches following identical pattern
- Status cascade (lines 196-220) contributes 8 branches with critical flow control
- Special capability loop multiplies complexity by number of capabilities

**Dependency Analysis:**
- Single production caller: `FleetListViewModel._refresh()`
- Pure function with no side effects
- Interface can change with low risk (coordinate with view model)
- 25+ tests across 5 test classes

**Safety Analysis:**
- Critical invariant: status filter mutual exclusivity (destroyed > derelict > damaged > undamaged)
- The `continue` statements after `result.append()` are critical for correct behavior
- Test gaps identified: no explicit tests for status hierarchy, empty inputs, order preservation
- 8-10 new tests recommended before refactoring

---

## Refactoring Strategy

### Approach: Extract Filter Predicates

Extract 5 helper functions, one per filter dimension:

```python
def _passes_warp_filter(ship, filter_state) -> bool
def _passes_spaceyard_filter(ship, filter_state) -> bool
def _passes_cargo_filter(ship, filter_state) -> bool
def _passes_special_ability_filters(ship, filter_state) -> bool
def _passes_status_filter(ship, filter_state) -> bool
```

### Rationale

1. **Repeated Pattern Extraction:** The boolean filter pair pattern appears 5 times with identical structure. Extracting to helpers eliminates duplication.

2. **Status Filter Isolation:** The status filter has unique semantics (cascade with mutual exclusivity). Isolating it preserves the critical flow control while making it testable independently.

3. **Testability:** Each predicate can be unit tested in isolation, improving coverage confidence.

4. **Interface Stability:** The main `filter_ships` function signature remains unchanged. Internal refactoring is invisible to callers.

### Implementation Skeleton

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """Filter ships based on status filter state."""
    return [
        ship for ship in ships
        if _passes_warp_filter(ship, filter_state)
        and _passes_spaceyard_filter(ship, filter_state)
        and _passes_cargo_filter(ship, filter_state)
        and _passes_special_ability_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]


def _passes_warp_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes warp capability filter."""
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)

    if show_warp and show_not_warp:
        return True  # No filtering needed

    is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
    if is_warp_capable and not show_warp:
        return False
    if not is_warp_capable and not show_not_warp:
        return False
    return True
```

---

## Risk Assessment

### High Risk: Status Filter Mutual Exclusivity

The current status cascade relies on `continue` statements to ensure each ship matches exactly one status category. When converting to a predicate function, this logic must be preserved:

```python
def _passes_status_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Check if ship passes status filter (destroyed/derelict/damaged/undamaged)."""
    # Determine ship's status category (mutually exclusive)
    if not ship.is_alive:
        status_key = 'show_destroyed'
    elif ship.is_derelict:
        status_key = 'show_derelict'
    elif ship.is_damaged():
        status_key = 'show_damaged'
    else:
        status_key = 'show_undamaged'

    return filter_state.get(status_key, True)
```

**Mitigation:** Add explicit tests for status hierarchy before refactoring.

### Medium Risk: Late Imports

The function uses late imports for `FleetCapabilityCalculator` to avoid circular imports. These must be preserved in the extracted helpers.

**Mitigation:** Keep imports inside helper functions.

### Low Risk: Special Capability Key Derivation

String manipulation derives filter keys dynamically. This is already tested for 2 of 5 capabilities.

**Mitigation:** Add tests for remaining 3 capabilities.

---

## Expected Outcome

| Metric | Before | After |
|--------|--------|-------|
| `filter_ships` CC | 36 | ~6 |
| Helper functions | 0 | 5 (CC 4-8 each) |
| Total functions | 3 | 8 |
| Test count | ~35 | ~45 |
| Max CC in file | 36 | ~8 |

---

## Files to Modify

| File | Changes |
|------|---------|
| `game/ui/screens/fleet_report_filters.py` | Extract helpers, simplify main function |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Add safety tests |

No interface changes required. No other files need modification.
