# PROJ-241: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target:** `filter_ships` function in `game/ui/screens/fleet_report_filters.py` (lines 124-222)
**Current CC:** 36 (grade F)
**Goal:** Reduce to below 20

The function applies 6 independent filter categories to a list of ships:
1. Warp capability (has/lacks)
2. Spaceyard capability (has/lacks)
3. Cargo filter (has/lacks)
4. Special capabilities (5 abilities, each has/lacks)
5. Status filter (destroyed/derelict/damaged/undamaged)

## Swarm Findings Summary

### Structure Analysis
- **Binary filter pattern** repeats 4+ times with identical structure
- **Status cascade** uses if/continue patterns for mutual exclusivity
- **Special capability loop** iterates 5 abilities with `_skip` flag pattern
- Complexity is structural (6 categories x 6 branches = 36), not algorithmic

### Dependency Analysis
- **Single caller:** `FleetListViewModel._refresh()` in `fleet_report_view_model.py`
- **Pure function:** No side effects, returns new list
- **Interface stable:** Uses `.get()` with defaults, adding keys is safe
- **39 test methods** cover the function

### Safety Analysis
- **Highest risk:** Status filter cascade (could double-classify ships)
- **Test gaps:** 6 scenarios missing (combined filters, edge cases)
- **Verdict:** Refactorable with caution - add tests first

## Architecture

### Complexity Breakdown

| Filter Category | CC Contribution | Lines |
|-----------------|-----------------|-------|
| Warp capability | ~6 | 144-153 |
| Spaceyard capability | ~6 | 156-164 |
| Cargo filter | ~6 | 167-174 |
| Special capabilities | ~10 | 176-194 |
| Status cascade | ~8 | 196-220 |
| **Total** | **~36** | |

### Key Patterns to Reuse

- **Binary filter pattern**: `lines 144-153` - Check show_X and show_not_X, skip if filtered
  ```python
  show_X = filter_state.get('show_X', True)
  show_not_X = filter_state.get('show_not_X', True)
  if not show_X or not show_not_X:
      has_X = <check>
      if has_X and not show_X: continue
      if not has_X and not show_not_X: continue
  ```

- **Status classification**: `lines 196-220` - Priority order: destroyed > derelict > damaged > undamaged

### Dependencies & Risks

1. **Status cascade mutual exclusivity** - Ships must be classified into exactly one status
   - Mitigation: Separate `_classify_ship_status()` helper from filter logic

2. **Late imports for circular dependency** - `FleetCapabilityCalculator` imported inside conditionals
   - Mitigation: Keep late imports in extracted helpers

3. **Test coverage gaps** - 6 scenarios not covered
   - Mitigation: Add tests in Phase 1 before any code changes

## Refactoring Strategy

### Approach: Filter Predicate Extraction

Extract each filter category into a predicate function returning `bool`:

```python
def _passes_binary_filter(has_capability: bool, show_has: bool, show_not: bool) -> bool:
    """Returns True if ship passes a binary (has/lacks) filter."""
    if show_has and show_not:
        return True  # Filter disabled
    return (has_capability and show_has) or (not has_capability and show_not)

def _classify_ship_status(ship) -> str:
    """Classify ship into exactly one status category."""
    if not ship.is_alive:
        return 'destroyed'
    if ship.is_derelict:
        return 'derelict'
    if ship.is_damaged():
        return 'damaged'
    return 'undamaged'

def _passes_status_filter(ship, filter_state) -> bool:
    status = _classify_ship_status(ship)
    return filter_state.get(f'show_{status}', True)
```

### Final Structure

```python
def filter_ships(ships, filter_state):
    return [
        ship for ship in ships
        if _passes_warp_filter(ship, filter_state)
        and _passes_spaceyard_filter(ship, filter_state)
        and _passes_cargo_filter(ship, filter_state)
        and _passes_special_filters(ship, filter_state)
        and _passes_status_filter(ship, filter_state)
    ]
```

### Expected CC After Refactoring

| Component | CC |
|-----------|-----|
| `filter_ships` | 6 |
| `_passes_binary_filter` | 3 |
| `_passes_warp_filter` | 2 |
| `_passes_spaceyard_filter` | 2 |
| `_passes_cargo_filter` | 2 |
| `_passes_special_filters` | 7 |
| `_passes_status_filter` | 2 |
| `_classify_ship_status` | 4 |

Main function drops from **36 to 6**.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.

| Decision | Summary |
|----------|---------|
| Proceed with refactoring | Pattern is regular, ideal for extraction |
| Add tests before code changes | 6 coverage gaps identified |
| Separate status classification | Reduces double-classification risk |
| Keep helpers in same file | Private implementation details |
| Preserve late imports | Avoid circular import issues |
