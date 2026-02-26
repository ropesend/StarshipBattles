# PROJ-227: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Target Function Overview

**File:** `game/ui/screens/fleet_report_filters.py`
**Function:** `filter_ships` (lines 124-222)
**Current CC:** 36 (grade F)
**Target CC:** < 20
**Length:** 99 lines

The `filter_ships` function implements a multi-criteria filtering system for ship lists in the Fleet Report UI. It handles 22+ filter flags across 6 filter categories.

## Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

### Complexity Sources

| Source | Contribution | Lines |
|--------|-------------|-------|
| Binary filter pattern (x4) | 12-16 branches | 143-174 |
| Special capability loop | 6 branches | 176-194 |
| Status cascade | 8 branches | 196-220 |
| Loop overhead | 2 branches | 142 |

### Architecture

**Structure Analysis:**
- The binary filter pattern (has/lacks attribute) is repeated 4 times with identical logic
- Status cascade mixes categorization and filtering concerns
- Special capability loop uses fragile `_skip` flag pattern

**Dependency Analysis:**
- Single production caller: `FleetListViewModel._refresh()`
- Pure function with no side effects
- ~55 tests provide comprehensive coverage
- Interface can change with coordinated updates

**Safety Analysis:**
- 6 critical invariants must be preserved
- Filter application order matters (capabilities before status)
- Status mutual exclusivity via early returns
- Short-circuit optimization skips expensive checks when filters disabled
- Late imports avoid circular dependencies

### Key Patterns to Reuse

- **Binary Filter Pattern**: `lines 143-153` - has/lacks toggle with short-circuit optimization
- **Status Cascade**: `lines 196-220` - mutually exclusive status categorization via early return

### Dependencies & Risks

1. **Import Cycles** - `FleetCapabilityCalculator` must be late-imported to avoid circular deps
2. **Status Mutual Exclusivity** - Early returns enforce one status per ship; must preserve
3. **Short-Circuit Optimization** - Skip expensive capability checks when both toggles enabled
4. **Filter Application Order** - Capabilities must filter before status

### Missing Test Coverage (Add Before Refactoring)

1. Empty ships list
2. Partial/missing filter_state keys
3. Mutually exclusive status handling (destroyed+derelict ship)
4. Combined capability + status filters
5. All-filters-disabled edge case

---

## Refactoring Strategy

### Approach: Extract Predicate Helpers

Extract the repeated patterns into focused helper functions, keeping them private to the module.

### Helper Functions to Extract

#### 1. `_passes_binary_filter(filter_state, positive_key, negative_key, has_attribute) -> bool`

Reusable helper for all binary (has/lacks) filters. Preserves short-circuit optimization.

**Estimated CC:** 3

```python
def _passes_binary_filter(
    filter_state: Dict[str, bool],
    positive_key: str,
    negative_key: str,
    has_attribute: bool
) -> bool:
    show_with = filter_state.get(positive_key, True)
    show_without = filter_state.get(negative_key, True)
    if show_with and show_without:
        return True
    if has_attribute:
        return show_with
    return show_without
```

#### 2. `_get_ship_status(ship) -> str`

Extracts status categorization into a pure function returning status string.

**Estimated CC:** 4

```python
def _get_ship_status(ship: "ShipInstance") -> str:
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

#### 3. `_passes_capability_filters(ship, filter_state) -> bool`

Isolates the special capability loop. Handles late import internally.

**Estimated CC:** 5-6

#### 4. Individual filter wrappers

For warp, spaceyard, cargo - thin wrappers that compute attribute and call `_passes_binary_filter`.

**Estimated CC:** 2 each

### Refactored Main Function

After extraction, `filter_ships` becomes:

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    result = []
    for ship in ships:
        # Capability filters
        if not _passes_warp_filter(ship, filter_state):
            continue
        if not _passes_spaceyard_filter(ship, filter_state):
            continue
        if not _passes_cargo_filter(ship, filter_state):
            continue
        if not _passes_capability_filters(ship, filter_state):
            continue

        # Status filter
        status = _get_ship_status(ship)
        if not filter_state.get(f'show_{status}', True):
            continue

        result.append(ship)
    return result
```

**Estimated CC:** 6-8

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking status mutual exclusivity | HIGH | Extract status categorization, not filtering logic |
| Losing short-circuit optimization | MEDIUM | Preserve early return in `_passes_binary_filter` |
| Import cycles | MEDIUM | Keep late imports in helper function scope |
| Changing filter order | HIGH | Maintain capability-then-status order in main function |
| Behavioral regression | LOW | Comprehensive test coverage provides safety net |

---

## Expected Outcome

| Component | Before | After |
|-----------|--------|-------|
| `filter_ships` | CC=36 | CC=6-8 |
| `_passes_binary_filter` | N/A | CC=3 |
| `_get_ship_status` | N/A | CC=4 |
| `_passes_capability_filters` | N/A | CC=5-6 |
| Individual wrappers | N/A | CC=2 each |

**Total:** Same logic distributed across focused helpers, no function exceeds CC=10.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
