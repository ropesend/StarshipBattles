# PROJ-239: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target:** `filter_ships` function in `game/ui/screens/fleet_report_filters.py` (lines 124-222)
**Current CC:** 36 (Grade F)
**Goal CC:** Below 20

The function filters ships based on 10+ boolean filter criteria across 4 categories:
1. Capability filters (warp, spaceyard, cargo)
2. Special ability filters (5 abilities from SPECIAL_CAPABILITY_COLUMNS)
3. Status filters (destroyed, derelict, damaged, undamaged)

## Swarm Findings Summary

Combined analysis from 3 parallel review agents:

### Architecture

**Single Caller Pattern**
- Only one production caller: `FleetListViewModel._refresh()` in `fleet_report_view_model.py:215`
- Interface can be modified with coordinated updates
- Filter state dict built by `FleetListViewModel.get_filter_state()` (20 boolean keys)

**Pure Function**
- No side effects, no state mutation
- Returns new list containing filtered ship references
- Safe to refactor without affecting callers

**Late Import Pattern**
- `FleetCapabilityCalculator` imported inside conditionals (lines 159, 185)
- `ShipStatsCalculator` already imported at module level
- Late imports prevent circular dependencies between ui.screens and strategy.data

### Key Patterns to Reuse

- **Binary Filter Pattern**: `fleet_report_filters.py:144-153` - check show_X/show_not_X, compute property only if needed
- **Status Classification**: `fleet_report_filters.py:196-220` - mutually exclusive cascading checks
- **Capability Column Mapping**: `fleet_data_source.py:46-52` - SPECIAL_CAPABILITY_COLUMNS dict

### Dependencies & Risks

1. **Filter Order Dependency** - Capability filters must run before status categorization; changing order changes results
2. **Status Mutual Exclusivity** - destroyed > derelict > damaged > undamaged priority must be preserved
3. **Late Imports** - Must preserve or carefully relocate to avoid circular imports
4. **String Key Derivation** - `col_id.replace('can_', 'no_', 1)` assumes prefix convention

### Opportunities Discovered

- Extract reusable `_apply_binary_filter()` helper (used 4x)
- Extract `_get_ship_status()` classifier (simplifies status block)
- Move `FleetCapabilityCalculator` import outside loop for performance
- Pre-compute capability filter key mappings

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

---

## Refactoring Strategy

### Approach: Extract Predicate Helpers

Convert each filter category into a standalone predicate function returning `True` if ship passes.

### Helper Functions to Create

| Helper | Lines Affected | Purpose | CC per Helper |
|--------|---------------|---------|---------------|
| `_passes_warp_filter` | 143-153 | Warp capability binary filter | ~4 |
| `_passes_spaceyard_filter` | 155-164 | Spaceyard binary filter | ~4 |
| `_passes_cargo_filter` | 166-174 | Cargo binary filter | ~4 |
| `_passes_capability_filters` | 176-194 | Special ability loop | ~6 |
| `_get_ship_status_filter_key` | 196-220 | Status classification | ~4 |

### Target Structure

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    result = []
    for ship in ships:
        if not _passes_warp_filter(ship, filter_state):
            continue
        if not _passes_spaceyard_filter(ship, filter_state):
            continue
        if not _passes_cargo_filter(ship, filter_state):
            continue
        if not _passes_capability_filters(ship, filter_state):
            continue

        status_key = _get_ship_status_filter_key(ship)
        if filter_state.get(status_key, True):
            result.append(ship)
    return result
```

**Expected Final CC:** Main function ~8-10, total distributed across helpers

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Filter order change | HIGH | Keep capability filters before status filter |
| Status mutual exclusivity broken | MEDIUM | Single `_get_ship_status_filter_key` function |
| Missing edge case tests | MEDIUM | Add tests in Phase 1 before code changes |
| Import pattern broken | LOW | Move imports to top of helper functions |

---

## Conclusion

**Function is REFACTORABLE.** CC 36 comes from mechanical duplication, not inherent complexity. Extraction into 5 helpers will reduce main function CC to ~10 while improving readability and testability.
