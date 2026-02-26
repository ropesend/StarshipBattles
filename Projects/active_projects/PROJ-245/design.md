# PROJ-245: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The `filter_ships` function (lines 124-222, CC=36) implements ship filtering for the Fleet Report UI. It uses a repeated binary filter pattern that appears 5 times, plus a loop over special capabilities, resulting in high cyclomatic complexity.

## Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

### Architecture

**Current State:**
- Single function handling all filter types (warp, spaceyard, cargo, special abilities, status)
- Pure function with no side effects
- Single caller: `FleetListViewModel._refresh()`
- Late imports to avoid circular dependencies

**Complexity Breakdown:**
| Section | Branches | Notes |
|---------|----------|-------|
| Warp filter | 4 | 2 conditions × 2 checks |
| Spaceyard filter | 4 | Same pattern |
| Cargo filter | 4 | Same pattern |
| Special capabilities loop | 10+ | Loop + 4 branches per iteration |
| Status chain | 8 | 4 mutually exclusive states × 2 checks each |
| **Total** | ~36 | |

### Key Patterns to Reuse

- **Binary Filter Pattern**: `filter_state.get('show_X', True)` with fallthrough on both-True
- **Status Classification**: destroyed > derelict > damaged > undamaged priority chain
- **Late Import Pattern**: Import inside function body to avoid circular deps

### Dependencies & Risks

1. **Filter Order Dependency** - Filters must be evaluated in exact sequence. Mitigation: Preserve order in predicate chain.
2. **Status Priority Chain** - Mutually exclusive status classification. Mitigation: Keep in single helper, document invariant.
3. **Special Capability Loop Break** - `_skip` flag with early break. Mitigation: Preserve fail-fast behavior in helper.
4. **Cargo Edge Cases** - Empty dict and zero values handled specially. Mitigation: Preserve exact boolean logic.

### Opportunities Discovered

- Extract generic `_passes_binary_filter()` helper for repeated pattern
- Convert main function to simple list comprehension
- Add unit tests for extracted helpers (improved testability)

## Design Decisions

### Approach: Predicate Extraction

Extract each filter section into a named predicate function that returns `True` if the ship should be INCLUDED (passes the filter).

**Target Structure:**
```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    return [
        ship for ship in ships
        if _passes_warp_filter(ship, filter_state)
        and _passes_spaceyard_filter(ship, filter_state)
        and _passes_cargo_filter(ship, filter_state)
        and _passes_special_capability_filter(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```

### Helper Signatures

```python
def _passes_warp_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Return True if ship passes the warp capability filter."""

def _passes_spaceyard_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Return True if ship passes the spaceyard filter."""

def _passes_cargo_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Return True if ship passes the cargo filter."""

def _passes_special_capability_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Return True if ship passes all special capability filters."""

def _passes_status_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
    """Return True if ship passes the status filter (destroyed/derelict/damaged/undamaged)."""
```

### Expected Complexity Distribution

| Function | Expected CC |
|----------|-------------|
| `filter_ships` (main) | 2-3 |
| `_passes_warp_filter` | 4-5 |
| `_passes_spaceyard_filter` | 4-5 |
| `_passes_cargo_filter` | 4-5 |
| `_passes_special_capability_filter` | 6-8 |
| `_passes_status_filter` | 5-6 |

All individual functions will be under 10 CC.

## Invariants to Preserve

### Critical Invariants (MUST preserve)

1. **Filter evaluation order**: warp → spaceyard → cargo → special capabilities → status
2. **Status classification priority**: destroyed > derelict > damaged > undamaged (mutually exclusive)
3. **Both-True optimization**: Skip capability check when both complementary filters are True
4. **Late imports**: Keep `FleetCapabilityCalculator` import inside function to avoid circular deps
5. **AND semantics**: Ship must pass ALL enabled filters to be included

### Filter Key Derivation

Special capability filters use key derivation:
- `col_id = "can_destroy_planet"` → `show_can_destroy_planet`, `show_no_destroy_planet`
- The "no" key is derived: `no_key = col_id.replace('can_', 'no_', 1)`

See [decisions.md](decisions.md) for the full log with rationale.
