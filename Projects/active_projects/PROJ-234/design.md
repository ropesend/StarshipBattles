# PROJ-234: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target:** `filter_ships` function in `game/ui/screens/fleet_report_filters.py` (lines 124-222)
**Current CC:** 36 (grade F)
**Goal:** Reduce to < 20

The function filters ships based on a `filter_state` dictionary containing boolean flags for various filter categories (damage status, capabilities, cargo).

## Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

### Architecture

The `filter_ships` function is a pure function with:
- **Single production caller:** `FleetListViewModel._refresh()` in `fleet_report_view_model.py`
- **No side effects:** Returns new list, doesn't mutate inputs
- **External reads:** `ShipStatsCalculator`, `FleetCapabilityCalculator` for capability checks
- **Late imports:** Intentional to avoid circular dependencies with strategy layer

### Key Patterns to Reuse

- **Binary Filter Pattern**: `lines 143-174` - guard + double-exclusion check repeated 3 times
- **Status Hierarchy**: `lines 196-220` - mutually exclusive status checks in priority order
- **Both-True Optimization**: `if not show_has or not show_not` - skip capability check when both filters enabled

### Dependencies & Risks

1. **Filter order matters** - Status checks must remain: Destroyed → Derelict → Damaged → Undamaged
2. **Special capability key transformation** - `can_X → no_X` must be preserved exactly
3. **Late imports for circular dependency** - `FleetCapabilityCalculator` imported inside function
4. **Both-true optimization** - Must preserve performance optimization in refactored code

### Opportunities Discovered

- Extract generic `_passes_binary_filter()` helper usable by 4+ filter types
- Move late import to module level with TYPE_CHECKING guard
- Convert loop+flag pattern to single predicate function
- Simplify main function to comprehension calling predicates

## Complexity Sources

| Source | Lines | Branches | % of Total |
|--------|-------|----------|------------|
| Special Capability Loop | 177-194 | ~15 | 42% |
| Binary Capability Filters | 143-174 | ~12 | 33% |
| Status Hierarchy | 196-220 | ~8 | 22% |
| Other | - | ~1 | 3% |

## Refactoring Strategy

### Approach: Extract Filter Predicates

Extract each filter category into a dedicated helper function:

| Helper | Purpose | Expected CC |
|--------|---------|-------------|
| `_passes_binary_filter()` | Generic binary filter check | 3 |
| `_passes_warp_filter()` | Warp capability filter | 2 |
| `_passes_spaceyard_filter()` | Spaceyard capability filter | 2 |
| `_passes_cargo_filter()` | Cargo presence filter | 3 |
| `_passes_special_capability_filters()` | All special abilities | 4 |
| `_passes_status_filter()` | Status category filter | 5 |

### Target Structure

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    return [
        ship for ship in ships
        if _passes_warp_filter(ship, filter_state)
        and _passes_spaceyard_filter(ship, filter_state)
        and _passes_cargo_filter(ship, filter_state)
        and _passes_special_capability_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```

Expected main function CC: ~6

## Test Coverage

**Existing:** 19 test methods in `tests/unit/ui/screens/test_fleet_report_filters.py`

**Gaps to fill before refactoring:**
- Empty filter_state dict (should show all)
- Both-false binary filters (should show nothing)
- Combined capability + status filters

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
