# PROJ-228: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The `filter_ships` function (CC 36, lines 124-222) filters `ShipInstance` objects based on a dictionary of boolean filter flags. It implements 5 filter categories:

1. **Warp Capability Filter** - Binary filter for warp drive presence
2. **Spaceyard Filter** - Binary filter for spaceyard component
3. **Cargo Filter** - Binary filter for cargo contents
4. **Special Capability Filters** - Loop over 5 special abilities (dynamic binary filters)
5. **Status Filter** - Priority-based mutually exclusive status categories

## Swarm Findings Summary

Combined analysis from individual agent reports in `findings/`.

### Architecture

**Complexity Sources:**
| Source | Contribution | Pattern |
|--------|--------------|---------|
| Binary filter pattern (x4) | ~12 branches | Repeated `show_has/show_not` checks |
| Special capability loop | ~6 branches | Nested loop with `_skip` flag |
| Status priority chain | ~8 branches | 4 mutually exclusive if-continue blocks |
| Outer ship loop | ~10 branches | `continue` statements for each filter |

### Key Patterns to Reuse

- **Binary Filter Pattern**: `lines 144-153` - Used 4 times with identical structure:
  ```python
  show_has = filter_state.get('show_X', True)
  show_not = filter_state.get('show_not_X', True)
  if not show_has or not show_not:
      has_property = check_property(ship)
      if has_property and not show_has: continue
      if not has_property and not show_not: continue
  ```

- **Status Priority Chain**: `lines 196-220` - Critical ordering: destroyed > derelict > damaged > undamaged

### Dependencies & Risks

1. **Status Priority Chain** - Must preserve destroyed > derelict > damaged > undamaged order
2. **Cargo Detection Logic** - `bool(cargo_contents) and sum(values()) > 0` handles zero-value entries
3. **Late Imports** - `FleetCapabilityCalculator` imported inside function to avoid circular deps
4. **Single Caller** - Only `FleetListViewModel._refresh()` calls this function

### Opportunities Discovered

- Duplicate import inside loop (line 185 = line 159) - easy fix
- `_skip` flag anti-pattern can be replaced with helper function
- Binary filter logic can be extracted once and reused 4+ times
- Status determination can be extracted for reuse (sorting already has similar logic)

## Refactoring Strategy

### Approach: Extract Helper Functions

Extract small, focused helper functions for each filter category:

1. **`_passes_binary_filter(has_property, show_has, show_not)`** - Generic binary filter logic
2. **`_passes_warp_filter(ship, filter_state)`** - Warp capability check
3. **`_passes_spaceyard_filter(ship, filter_state)`** - Spaceyard check
4. **`_passes_cargo_filter(ship, filter_state)`** - Cargo check
5. **`_passes_special_capability_filters(ship, filter_state)`** - All special abilities
6. **`_get_ship_status(ship)`** - Determine status category string
7. **`_passes_status_filter(ship, filter_state)`** - Status filter using helper

### Expected CC Reduction

| Change | CC Impact |
|--------|-----------|
| Extract `_passes_binary_filter()` | -8 (from main function) |
| Extract `_passes_*_filter()` helpers | -4 (cleaner conditionals) |
| Extract `_get_ship_status()` | -4 (status chain) |
| Simplify main loop | -4 (cleaner structure) |
| **New helpers (combined)** | +8 |
| **Net reduction** | ~16 (36 → ~20) |

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

### Key Decisions Made During Analysis

1. **Generic Binary Filter Helper** - Create `_passes_binary_filter()` for reuse across all binary filters
2. **Keep Status Priority Inline Initially** - Extract `_get_ship_status()` but keep filter check inline in Phase 2
3. **Move Imports Before Loop** - Late import should execute once, not inside special capabilities loop
4. **Eliminate _skip Flag** - Use helper function with early return instead of flag pattern
