# PROJ-247: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Overview

Refactoring the `filter_ships` function (CC 36) in `game/ui/screens/fleet_report_filters.py` to reduce cyclomatic complexity below 20 through predicate extraction.

## Multi-Agent Review Findings

### Structure Analysis
- Binary filter pattern (show_X/show_not_X) repeated 5 times, each adding 3-4 branches
- Special capability loop (lines 177-194) is highest complexity contributor with nested conditions
- Status filter cascade (lines 196-220) creates waterfall of 4 consecutive checks
- Flag variable `_skip` indicates loop body should be extracted

### Dependency Analysis
- Single production caller: `FleetListViewModel._refresh()`
- Pure function with no side effects
- 20 filter state keys, all defaulting to `True`
- Comprehensive test coverage: 18 tests across 5 test classes

### Safety Analysis
- Status check order is CRITICAL invariant: destroyed > derelict > damaged > undamaged
- Short-circuit optimization must be preserved (expensive capability checks)
- Late imports avoid circular dependencies (must remain late)
- Missing test coverage: empty list, all-filters-disabled, combined filters, status priority

## Refactoring Strategy

### Approach: Predicate Extraction

Extract filter logic into focused helper functions that return `bool`:

```python
def _passes_binary_filter(filter_state, show_key, show_not_key, has_capability) -> bool
def _passes_warp_filter(ship, filter_state) -> bool
def _passes_spaceyard_filter(ship, filter_state) -> bool
def _passes_cargo_filter(ship, filter_state) -> bool
def _passes_special_capability_filters(ship, filter_state) -> bool
def _passes_status_filter(ship, filter_state) -> bool
def _classify_ship_status(ship) -> str  # Shared with sort_ships
```

### Final Structure

```python
def filter_ships(ships, filter_state):
    return [
        ship for ship in ships
        if _passes_warp_filter(ship, filter_state)
        and _passes_spaceyard_filter(ship, filter_state)
        and _passes_cargo_filter(ship, filter_state)
        and _passes_special_capability_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```

### CC Impact Estimate

| Component | Current CC | After Extraction |
|-----------|------------|------------------|
| `filter_ships` main | 36 | ~6 |
| `_passes_binary_filter` | - | 3 |
| `_passes_warp_filter` | - | 2 |
| `_passes_spaceyard_filter` | - | 2 |
| `_passes_cargo_filter` | - | 2 |
| `_passes_special_capability_filters` | - | 6 |
| `_passes_status_filter` | - | 5 |
| `_classify_ship_status` | - | 4 |

**Expected result:** `filter_ships` CC reduced from 36 to ~6

## Invariants to Preserve

1. **Status check order:** destroyed > derelict > damaged > undamaged (mutual exclusivity)
2. **Short-circuit optimization:** Only check capabilities when filter is active
3. **AND semantics:** Ship must pass ALL filter categories
4. **Default True:** Missing filter keys default to showing ships
5. **Late imports:** Keep `FleetCapabilityCalculator` as late import to avoid circular dependency

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Breaking status hierarchy | HIGH | Add explicit status priority test before refactoring |
| Losing short-circuit | MEDIUM | Preserve conditional inside helper functions |
| Circular imports | MEDIUM | Keep late imports inside helper functions |
| Test regression | LOW | Add missing tests before any code changes |

## Test Gaps to Fill (Phase 1)

1. Empty ship list handling
2. All filters disabled (should return empty)
3. Status priority (derelict not caught by damaged filter)
4. Combined filters (multiple categories active)
5. Partial filter_state (missing keys)

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
