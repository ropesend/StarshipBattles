# PROJ-231: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target:** `filter_ships` in `game/ui/screens/fleet_report_filters.py` (lines 124-222)
**Current CC:** 36 (grade F)
**Target CC:** < 20
**Lines:** ~99

The function filters ships based on a `filter_state` dictionary containing ~20 boolean keys across four categories: capability filters (warp, spaceyard, cargo), special capability filters (5 abilities), and status filters (destroyed, derelict, damaged, undamaged).

## Swarm Findings Summary

Combined analysis from three parallel review agents in `findings/`.

### Architecture

**Complexity Sources:**
| Source | Lines | CC Contribution | Pattern |
|--------|-------|-----------------|---------|
| Warp capability filter | 144-153 | +4 | Binary filter |
| Spaceyard filter | 156-164 | +4 | Binary filter |
| Cargo filter | 167-174 | +4 | Binary filter |
| Special capabilities loop | 177-194 | +6 | Loop with nested conditionals |
| Status filters (4 states) | 196-220 | +9 | Cascade with append |
| Main loop + function entry | - | +1 | Baseline |

**Interface:**
- Single production caller: `FleetListViewModel._refresh()`
- ~20 test invocations provide good coverage
- Pure function with no side effects
- Filter keys default to `True` via `.get(key, True)`

### Key Patterns to Reuse

- **Binary Filter Pattern**: `lines 144-174` - Check `show_has/show_not`, short-circuit if both True, then evaluate capability
- **Status Cascade**: `lines 196-220` - Strict order: destroyed → derelict → damaged → undamaged

### Dependencies & Risks

1. **Status filter order** - MUST preserve: destroyed > derelict > damaged > undamaged
2. **Default behavior** - MUST preserve: missing keys default to True (show all)
3. **Short-circuit optimization** - MUST preserve: skip expensive checks when both filters are True
4. **Late imports** - MUST preserve: `FleetCapabilityCalculator` imports inside function to avoid circular imports
5. **Special capability key derivation** - MUST preserve: `can_X` → `no_X` transformation

### Opportunities Discovered

- Three binary filter patterns are nearly identical → extract generic helper
- Status filter cascade can be isolated → extract `_passes_status_filter()`
- Special capabilities loop is self-contained → extract `_passes_special_capability_filters()`

## Refactoring Strategy

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
        if not _passes_special_capability_filters(ship, filter_state):
            continue
        if not _passes_status_filter(ship, filter_state):
            continue
        result.append(ship)
    return result
```

### Expected CC Reduction

| Component | Before | After |
|-----------|--------|-------|
| `filter_ships` main | 36 | ~8 |
| `_passes_warp_filter` | - | ~3 |
| `_passes_spaceyard_filter` | - | ~3 |
| `_passes_cargo_filter` | - | ~3 |
| `_passes_special_capability_filters` | - | ~5 |
| `_passes_status_filter` | - | ~5 |

**Target achieved:** `filter_ships` CC ≤ 15

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
