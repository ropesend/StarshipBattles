# PROJ-237: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Synthesized Analysis

### Function Characteristics
- **Target:** `game/ui/screens/fleet_report_filters.py:filter_ships` (lines 124-222)
- **Lines:** 99
- **Cyclomatic Complexity:** 36 (grade F) → goal < 20
- **Filter categories:** 6 (warp, spaceyard, cargo, special capabilities, status)
- **Pattern:** Pure function, no side effects
- **Interface:** Single caller (`FleetListViewModel._refresh`)
- **Test coverage:** Good (20+ tests), but gaps exist

### Root Causes of Complexity

1. **Repeated binary filter pattern** (4x) - Each capability filter follows the same show/no-show pattern with nested conditionals
2. **Special capability loop with flag** - Inner loop uses `_skip` flag and `break`
3. **Status filter cascade** - 4 mutually exclusive states checked sequentially with early returns
4. **Late imports inside loop** - `FleetCapabilityCalculator` imported conditionally

## Critical Invariants

| Invariant | Description |
|-----------|-------------|
| **Status order** | Destroyed → Derelict → Damaged → Undamaged (derelict checked BEFORE damaged) |
| **Default True** | Missing filter keys default to `True` (show all) |
| **Order preservation** | Ships in result maintain original order |
| **No mutation** | Input list and ships are not modified |

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Status hierarchy break | HIGH | Add tests for derelict/damaged precedence |
| Missing default behavior | MEDIUM | Test partial filter_state dicts |
| Late import issues | MEDIUM | Keep imports inside conditionals |
| Cargo None edge case | LOW | Existing code uses `bool()` check |

---

## Refactoring Strategy

### Phase 1: Test Fortification

Add 6 targeted tests before any code changes:
1. Empty list input
2. Empty filter_state dict
3. Partial filter_state (single key)
4. All status filters disabled → empty result
5. Derelict precedence over damaged
6. Combined warp + status filters

### Phase 2: Extract Helper Functions

**Step 2.1: Extract `_passes_binary_filter()` helper**
- Generic helper for show/no-show pattern
- Signature: `(ship, filter_state, show_key, no_key, capability_checker) -> bool`
- Eliminates 3 repeated code blocks (warp, spaceyard, cargo)

**Step 2.2: Extract `_passes_special_capability_filters()` helper**
- Replaces loop with `_skip` flag (lines 177-194)
- Signature: `(ship, filter_state) -> bool`
- Returns True if ship passes all special capability filters

**Step 2.3: Extract `_get_ship_status_category()` helper**
- Returns status string: 'destroyed', 'derelict', 'damaged', 'undamaged'
- Encapsulates the priority logic (destroyed > derelict > damaged > undamaged)

**Step 2.4: Extract `_passes_status_filter()` helper**
- Uses `_get_ship_status_category()` to check single filter key
- Signature: `(ship, filter_state) -> bool`

### Phase 3: Simplify Main Function

Refactor `filter_ships()` to use the helpers:
```python
def filter_ships(ships, filter_state):
    result = []
    for ship in ships:
        if not _passes_binary_filter(ship, filter_state, 'show_warp_capable', 'show_not_warp_capable',
                                      ShipStatsCalculator.has_warp_capability):
            continue
        if not _passes_binary_filter(ship, filter_state, 'show_has_spaceyard', 'show_no_spaceyard',
                                      FleetCapabilityCalculator.ship_has_spaceyard):
            continue
        if not _passes_binary_filter(ship, filter_state, 'show_has_cargo', 'show_no_cargo',
                                      _has_cargo):
            continue
        if not _passes_special_capability_filters(ship, filter_state):
            continue
        if not _passes_status_filter(ship, filter_state):
            continue
        result.append(ship)
    return result
```

### Phase 4: Verification

1. Run full test suite
2. Verify CC is now below 20
3. Clean up any redundant code

---

## Expected Outcomes

| Metric | Before | After |
|--------|--------|-------|
| Cyclomatic Complexity | 36 | ~12-15 |
| Lines (main function) | 99 | ~25-30 |
| Helper functions | 0 | 4-5 |
| Test count | 20 | 26+ |

---

## Key Patterns to Reuse

- **Binary filter pattern**: `filter_state.get('show_X', True)` with early continue
- **Late imports**: Keep `FleetCapabilityCalculator` import inside conditionals to avoid circular dependency

## Dependencies & Risks

1. **FleetCapabilityCalculator circular import** - Must keep late imports or refactor import structure
2. **Status hierarchy** - Tests must verify derelict precedence over damaged
3. **SPECIAL_CAPABILITY_COLUMNS** - Filter key derivation uses string replacement; consider explicit mapping

## Files Modified

| File | Changes |
|------|---------|
| `game/ui/screens/fleet_report_filters.py` | Add helpers, refactor main function |
| `tests/unit/ui/screens/test_fleet_report_filters.py` | Add 6 fortification tests |
