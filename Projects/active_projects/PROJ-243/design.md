# PROJ-243: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Architecture Analysis

### Current State

The `filter_ships` function (CC 36) in `game/ui/screens/fleet_report_filters.py` implements 5 distinct filter categories:

1. **Warp capability filter** (lines 143-153)
2. **Spaceyard capability filter** (lines 155-164)
3. **Cargo filter** (lines 166-174)
4. **Special capability filters** (lines 176-194) - loops over `SPECIAL_CAPABILITY_COLUMNS`
5. **Status filter chain** (lines 196-220) - destroyed/derelict/damaged/undamaged

### Complexity Sources

| Source | Estimated CC | Pattern |
|--------|--------------|---------|
| Binary capability filters (warp, spaceyard, cargo) | ~15 CC | Repeated identical pattern |
| Special capability loop | ~10 CC | Loop + binary pattern + skip flag |
| Status classification chain | ~8 CC | Nested if-continue-append |
| Base control flow | ~3 CC | For loop, final append |

## Swarm Findings Summary

### Structure Analysis
- All capability filters follow identical binary pattern (show_has/show_not)
- The pattern can be extracted to a single helper function
- Status classification can be separated from filtering logic
- Converting to predicate pattern eliminates result list mutation

### Dependency Analysis
- Single production caller: `FleetListViewModel._refresh()`
- Pure function with no side effects
- Interface is stable (uses `.get()` with defaults)
- 20 direct tests + 28 indirect tests provide good coverage

### Safety Analysis
- Status filter ordering is CRITICAL (destroyed > derelict > damaged > undamaged)
- Missing edge case tests for status classification priorities
- The `_skip` flag pattern needs careful extraction
- Function is refactorable with caution

## Key Patterns to Reuse

- **Binary Filter Pattern**: `fleet_report_filters.py:143-174` - Same pattern repeated for warp, spaceyard, cargo filters. Extract to single helper.

## Dependencies & Risks

1. **Status Filter Ordering (HIGH)** - Checks must remain: destroyed > derelict > damaged > undamaged. Mitigation: Add edge case tests first.
2. **Early Exit Semantics (MEDIUM)** - `continue` statements must map to `return False`. Mitigation: Use predicate pattern.
3. **Late Imports (LOW)** - Keep imports inside helpers for same lazy-loading behavior.

---

## Refactoring Strategy

### Approach: Extract Predicate Helpers

Transform the monolithic function into a composition of small, focused helper predicates:

```
filter_ships (CC 36)
    └── iterates ships, applies all filters inline

        ↓ REFACTOR TO ↓

filter_ships (CC 2)
    └── list comprehension calling _ship_passes_filters()

_ship_passes_filters (CC ~8)
    ├── calls _passes_binary_filter() for warp
    ├── calls _passes_binary_filter() for spaceyard
    ├── calls _passes_binary_filter() for cargo
    ├── loops special capabilities calling _passes_binary_filter()
    └── calls _passes_status_filter()

_passes_binary_filter (CC ~3)
    └── handles has/not-has filter pairs

_get_ship_status (CC 4)
    └── classifies ship: destroyed/derelict/damaged/undamaged
```

### Binary Filter Helper

**Signature:**
```python
def _passes_binary_filter(
    ship: ShipInstance,
    filter_state: Dict[str, bool],
    has_key: str,
    not_key: str,
    capability_check: Callable[[ShipInstance], bool]
) -> bool:
    """Check if ship passes a binary has/has-not capability filter."""
    show_has = filter_state.get(has_key, True)
    show_not = filter_state.get(not_key, True)

    if show_has and show_not:
        return True  # No filtering active

    has_capability = capability_check(ship)
    return show_has if has_capability else show_not
```

### Status Classification Helper

**Signature:**
```python
def _get_ship_status(ship: ShipInstance) -> str:
    """Classify ship into one of four status categories.

    CRITICAL: Order matters! Checks must be:
    1. destroyed (not is_alive)
    2. derelict
    3. damaged
    4. undamaged (fallthrough)
    """
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'
```

---

## Expected Results

### Complexity Reduction

| Function | Before | After |
|----------|--------|-------|
| `filter_ships` | CC 36 | CC 2 |
| `_ship_passes_filters` | N/A | CC 8-10 |
| `_passes_binary_filter` | N/A | CC 3 |
| `_get_ship_status` | N/A | CC 4 |
| **Total** | **36** | **17-19** |

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
