# PROJ-246: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Target Function Analysis

**File:** `game/ui/screens/fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Current CC:** 36 (Grade F)
**Target CC:** < 20

---

## Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

### Architecture

The `filter_ships` function is a **pure function** with a single production caller (`FleetListViewModel._refresh()`). It applies multiple binary filter patterns in sequence:

1. **Warp capability filter** (lines 144-153)
2. **Spaceyard filter** (lines 156-164)
3. **Cargo filter** (lines 167-174)
4. **Special capabilities loop** (lines 176-194)
5. **Status filter cascade** (lines 196-220)

Each binary filter follows an identical pattern that can be extracted.

### Key Patterns to Reuse

- **Binary filter pattern**: `fleet_report_filters.py:144-153` - Check show/hide flags, compute property, filter based on flags
- **Status cascade pattern**: `fleet_report_filters.py:196-220` - Mutually exclusive classification with priority order

### Dependencies & Risks

1. **Late imports required** - `FleetCapabilityCalculator` must be imported inside functions (circular import avoidance)
2. **Status priority invariant** - Order: Destroyed > Derelict > Damaged > Undamaged (must preserve)
3. **Interface stability** - Function signature cannot change; 19 tests and 1 production caller depend on it

### Opportunities Discovered

- Generic `_check_binary_filter()` helper eliminates 4 repeated patterns (~30 lines)
- Status classification can be extracted to `_get_ship_status()` for reuse
- Main loop can be reduced from 98 lines to ~20 lines

---

## Refactoring Strategy

### Approach: Extract Filter Predicates

Transform the 98-line function into a clean main loop calling well-named predicate functions.

**Before:**
```python
def filter_ships(ships, filter_state):
    result = []
    for ship in ships:
        # 80+ lines of inline filter logic with nested conditionals
        ...
    return result
```

**After:**
```python
def filter_ships(ships, filter_state):
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

### Helper Functions to Extract

| Helper | Source Lines | Purpose | Expected CC |
|--------|--------------|---------|-------------|
| `_check_binary_filter()` | N/A (new) | Generic binary filter check | 3 |
| `_passes_warp_filter()` | 144-153 | Warp capability check | 2 |
| `_passes_spaceyard_filter()` | 156-164 | Spaceyard check | 2 |
| `_passes_cargo_filter()` | 167-174 | Cargo check | 3 |
| `_passes_special_capability_filters()` | 176-194 | All special caps | 5 |
| `_get_ship_status()` | N/A (new) | Classify ship status | 4 |
| `_passes_status_filter()` | 196-220 | Status filter check | 2 |

### CC Impact Estimate

- Original `filter_ships`: CC 36
- Refactored `filter_ships`: CC ~7 (one branch per filter type)
- Total CC distributed across helpers: ~28

**Goal achieved:** `filter_ships` CC reduced from 36 to ~7

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

Key decisions:
1. Extract helpers as private module functions (`_helper_name()`)
2. Create generic `_check_binary_filter()` for repeated pattern
3. Keep late imports inside helpers that need them
4. Add safety tests before any code changes
5. Preserve exact behavior of status cascade
