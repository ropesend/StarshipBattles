# PROJ-248: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target:** `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
- Lines: 124-222 (99 lines)
- Cyclomatic Complexity: 36 (Grade F)
- Goal: Reduce CC below 20

## Swarm Findings Summary

Combined analysis from 3 parallel review agents.

### Structure Analysis

The function has five major complexity drivers:

| Section | Lines | Complexity Contribution |
|---------|-------|------------------------|
| Warp capability filter | 144-153 | 2 conditions + 2 continue paths |
| Spaceyard capability filter | 156-164 | 2 conditions + 2 continue paths + import |
| Cargo filter | 167-174 | 2 conditions + 2 continue paths |
| Special capability loop | 176-194 | Loop + nested conditions + flag variable |
| Status cascade | 196-220 | 4 mutually exclusive states |

Key structural issues:
- Binary filter pattern repeated 4 times with identical structure
- `_skip` flag anti-pattern for early loop exit
- Repeated late imports inside loop
- 3-4 levels of nesting throughout

### Dependency Analysis

- **Single caller:** `FleetListViewModel._refresh()` in `fleet_report_view_model.py` (line 215)
- **Interface stability:** CAN be changed with coordinated updates
- **Side effects:** None - function is pure
- **Test coverage:** HIGH - comprehensive unit tests in `test_fleet_report_filters.py`

### Safety Analysis

- **Verdict:** REFACTORABLE with caution
- **Critical invariant:** Status check ordering (destroyed -> derelict -> damaged -> undamaged)
- **Missing tests:** 5 critical edge cases need coverage before refactoring
- **Risk level:** MEDIUM

---

## Architecture

### Key Patterns to Reuse

- **Binary filter pattern**: Lines 144-153, 156-164, 167-174 - identical structure can be extracted
- **Status categorization**: Lines 196-220 - mutually exclusive cascade

### Dependencies & Risks

1. **Status ordering** - Must preserve destroyed -> derelict -> damaged -> undamaged sequence
2. **Lazy imports** - `FleetCapabilityCalculator` imported conditionally to avoid circular imports
3. **Filter key naming** - Keys like `show_warp_capable`, `show_not_warp_capable` must be preserved

### Opportunities Discovered

- Extract generic `_passes_binary_filter()` utility (removes ~20 lines duplication)
- Convert main function to list comprehension with predicate
- Simplify special capability loop by removing `_skip` flag

---

## Refactoring Strategy

### Approach: Extract Filter Predicates

Transform the monolithic function into composed filter predicates:

```python
# Before (CC=36): Single function with all logic inline
def filter_ships(ships, filter_state):
    result = []
    for ship in ships:
        # 99 lines of nested conditions...
    return result

# After (CC<20): Composed predicates
def filter_ships(ships, filter_state):
    return [s for s in ships if _passes_all_filters(s, filter_state)]
```

### Helper Functions to Extract

1. **`_passes_binary_filter(has_capability, show_has, show_not)`** - Generic utility
2. **`_passes_warp_filter(ship, filter_state)`** - Lines 144-153
3. **`_passes_spaceyard_filter(ship, filter_state)`** - Lines 156-164
4. **`_passes_cargo_filter(ship, filter_state)`** - Lines 167-174
5. **`_passes_special_capability_filters(ship, filter_state)`** - Lines 176-194
6. **`_passes_status_filter(ship, filter_state)`** - Lines 196-220 (ORDER CRITICAL)

### Expected Complexity Reduction

| Component | Before | After |
|-----------|--------|-------|
| `filter_ships` main | CC 36 | CC 2-3 |
| `_passes_binary_filter` | - | CC 3 |
| `_passes_warp_filter` | - | CC 3 |
| `_passes_spaceyard_filter` | - | CC 3 |
| `_passes_cargo_filter` | - | CC 3 |
| `_passes_special_capability_filters` | - | CC 7 |
| `_passes_status_filter` | - | CC 4 |

**Result:** No single function above CC 10.

---

## Risk Assessment

### High Risk Areas
| Area | Mitigation |
|------|------------|
| Status check ordering | Extract as single function, preserve exact sequence |
| `_skip` flag removal | Convert to early `return False` in predicate |
| Lazy imports | Keep inside helpers to avoid circular imports |

### Medium Risk Areas
| Area | Mitigation |
|------|------------|
| Filter key names | Keep identical key strings |
| Default values | All `.get(key, True)` patterns preserved |
| Cargo sum > 0 check | Preserve exact boolean logic |

---

## Alternatives Considered

1. **Filter Class** - Rejected: Overkill for single-use filtering
2. **Configuration-Driven** - Rejected: Adds complexity, harder to debug
3. **Skip Refactoring** - Rejected: CC 36 IS reducible with clear extraction points

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
