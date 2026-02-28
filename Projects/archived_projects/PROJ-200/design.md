# PROJ-200: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target:** `filter_ships` function in `game/ui/screens/fleet_report_filters.py`
**Current CC:** 36 (Grade F)
**Goal:** Reduce to < 20
**Lines:** 124-222 (99 lines)

The function filters ships based on a dictionary of boolean filter flags. It handles 5 distinct filter categories with similar patterns, creating high cyclomatic complexity through repetition rather than inherent algorithmic complexity.

## Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

### Architecture

The `filter_ships` function is a **pure function** with:
- Single caller: `FleetListViewModel._refresh()` in `fleet_report_view_model.py`
- No side effects or state mutations
- Comprehensive test coverage (21+ test cases)
- Late imports to avoid circular dependencies

**Complexity sources (by contribution):**

| Source | Lines | Branch Count |
|--------|-------|--------------|
| Warp capability filter | 143-153 | 4 |
| Spaceyard capability filter | 155-164 | 4 |
| Cargo filter | 166-174 | 4 |
| Special capabilities loop (5 items) | 176-194 | ~10 |
| Status cascade (4-way) | 196-220 | 8 |
| **Total** | | **~30** |

### Key Patterns to Reuse

- **Binary capability filter**: Lines 143-153 - Pattern for checking has/not-has capability filters
- **Status cascade**: Lines 196-220 - Ordered status checking (destroyed → derelict → damaged → undamaged)
- **Late import pattern**: Lines 159, 185 - Import inside conditional to avoid circular imports

### Dependencies & Risks

1. **Status filter ordering (HIGH)** - Order must be preserved: destroyed → derelict → damaged → undamaged. A derelict ship is also damaged, so order matters.
2. **Special capabilities `_skip` flag (MEDIUM)** - Fragile pattern using flag + break. Must preserve break semantics when extracting.
3. **Circular imports (LOW)** - Late imports for `FleetCapabilityCalculator` must stay inside functions.
4. **Filter key naming (LOW)** - Keys follow `show_X` / `show_no_X` convention. Must not change without updating `get_filter_state()`.

### Opportunities Discovered

- All 5 filter categories follow the same pattern → single helper can handle most cases
- Status classification can be simplified to a lookup
- Pre-computing filter key mappings outside the loop would improve readability

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

---

## Refactoring Strategy

### Approach: Extract Predicate Functions

Convert each filter category into a standalone predicate function that returns `True` if the ship should be **excluded**.

### Target Structure

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """Filter ships based on status filter state."""
    result = []
    for ship in ships:
        if _should_exclude_by_warp(ship, filter_state):
            continue
        if _should_exclude_by_spaceyard(ship, filter_state):
            continue
        if _should_exclude_by_cargo(ship, filter_state):
            continue
        if _should_exclude_by_special_capabilities(ship, filter_state):
            continue
        if _should_exclude_by_status(ship, filter_state):
            continue
        result.append(ship)
    return result
```

### Helper Functions

| Function | Extracts From | Expected CC |
|----------|---------------|-------------|
| `_should_exclude_by_warp(ship, filter_state)` | Lines 143-153 | 4 |
| `_should_exclude_by_spaceyard(ship, filter_state)` | Lines 155-164 | 4 |
| `_should_exclude_by_cargo(ship, filter_state)` | Lines 166-174 | 4 |
| `_should_exclude_by_special_capabilities(ship, filter_state)` | Lines 176-194 | 6-8 |
| `_should_exclude_by_status(ship, filter_state)` | Lines 196-220 | 5 |

**Main function CC after refactoring:** ~6

### Critical Implementation Notes

1. **Status filter order MUST be preserved:**
   - Destroyed (not `is_alive`)
   - Derelict (`is_derelict`) - checked BEFORE damaged because derelict implies damaged
   - Damaged (`is_damaged()`)
   - Undamaged (fallthrough)

2. **Late imports stay inside helpers:**
   ```python
   def _should_exclude_by_spaceyard(...):
       show_has = filter_state.get('show_has_spaceyard', True)
       show_no = filter_state.get('show_no_spaceyard', True)
       if show_has and show_no:
           return False  # No filtering needed
       # Late import inside function
       from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
       has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
       ...
   ```

3. **Special capabilities uses `SPECIAL_CAPABILITY_COLUMNS` from `fleet_data_source.py`**

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Status filter order broken | Medium | High | Add explicit test for order + comment |
| Special capabilities logic error | Low | Medium | Extract carefully, test all 5 capabilities |
| Circular import | Low | High | Keep late imports inside helpers |
| Test failures | Low | Medium | Run targeted tests after each extraction |

---

## Verification Plan

1. **Phase 1:** Add missing tests for filter combinations
2. **Phase 2:** Extract helpers one at a time, verify tests pass after each
3. **Phase 3:** Run full test suite
4. **Phase 4:** Verify CC is below threshold
