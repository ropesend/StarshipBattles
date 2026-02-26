# Phase 3: Simplify Main Function

**Goal:** Refactor `filter_ships()` to use the extracted helpers.

**File:** `game/ui/screens/fleet_report_filters.py`

---

## Checklist

### 3.1 Refactor warp filter

- [ ] **3.1.1 Replace lines 143-153** (warp capability filter)
  - Before:
    ```python
    show_warp = filter_state.get('show_warp_capable', True)
    show_not_warp = filter_state.get('show_not_warp_capable', True)
    if not show_warp or not show_not_warp:
        is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
        if is_warp_capable and not show_warp:
            continue
        if not is_warp_capable and not show_not_warp:
            continue
    ```
  - After:
    ```python
    if not _passes_binary_filter(ship, filter_state, 'show_warp_capable',
                                  'show_not_warp_capable', ShipStatsCalculator.has_warp_capability):
        continue
    ```

- [ ] **3.1.2 Run tests**
  - All tests must pass

### 3.2 Refactor spaceyard filter

- [ ] **3.2.1 Replace lines 155-164** (spaceyard capability filter)
  - Keep the late import at module level in `_passes_binary_filter` or move it
  - **DECISION:** Move late import to top of `filter_ships` function body (before loop)
  - After:
    ```python
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
    # ... (at top of function, outside loop)

    if not _passes_binary_filter(ship, filter_state, 'show_has_spaceyard',
                                  'show_no_spaceyard', FleetCapabilityCalculator.ship_has_spaceyard):
        continue
    ```

- [ ] **3.2.2 Run tests**
  - All tests must pass

### 3.3 Refactor cargo filter

- [ ] **3.3.1 Replace lines 166-174** (cargo filter)
  - After:
    ```python
    if not _passes_binary_filter(ship, filter_state, 'show_has_cargo',
                                  'show_no_cargo', _has_cargo):
        continue
    ```

- [ ] **3.3.2 Run tests**
  - All tests must pass

### 3.4 Refactor special capability filter

- [ ] **3.4.1 Replace lines 176-194** (special capability loop with flag)
  - Before:
    ```python
    _skip = False
    for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
        # ... complex logic with break
    if _skip:
        continue
    ```
  - After:
    ```python
    if not _passes_special_capability_filters(ship, filter_state):
        continue
    ```

- [ ] **3.4.2 Run tests**
  - All tests must pass

### 3.5 Refactor status filter

- [ ] **3.5.1 Replace lines 196-220** (status filter cascade)
  - Before:
    ```python
    if not ship.is_alive:
        if not filter_state.get('show_destroyed', True):
            continue
        result.append(ship)
        continue
    # ... similar for derelict, damaged, undamaged
    ```
  - After:
    ```python
    if not _passes_status_filter(ship, filter_state):
        continue
    result.append(ship)
    ```

- [ ] **3.5.2 Run tests**
  - All tests must pass

### 3.6 Final cleanup

- [ ] **3.6.1 Move late import outside loop**
  - Move `FleetCapabilityCalculator` import to top of `filter_ships` function (still late import, but once per call)

- [ ] **3.6.2 Verify final structure**
  - Main function should be ~25-30 lines
  - Clear sequence of filter checks with `continue`
  - Single `result.append(ship)` at end

- [ ] **3.6.3 Run full test suite**
  - Command: `pytest tests/ -n 12`
  - All tests must pass

---

## Expected Final Code

```python
def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
    """Filter ships based on status filter state."""
    # Late import to avoid circular dependency
    from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator

    result = []
    for ship in ships:
        # Capability filters
        if not _passes_binary_filter(ship, filter_state, 'show_warp_capable',
                                      'show_not_warp_capable', ShipStatsCalculator.has_warp_capability):
            continue
        if not _passes_binary_filter(ship, filter_state, 'show_has_spaceyard',
                                      'show_no_spaceyard', FleetCapabilityCalculator.ship_has_spaceyard):
            continue
        if not _passes_binary_filter(ship, filter_state, 'show_has_cargo',
                                      'show_no_cargo', _has_cargo):
            continue

        # Special capability filters
        if not _passes_special_capability_filters(ship, filter_state):
            continue

        # Status filter
        if not _passes_status_filter(ship, filter_state):
            continue

        result.append(ship)
    return result
```

---

## Verification

```bash
# Run targeted tests
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Full suite
pytest tests/ -n 12
```

---

## Completion Criteria
- [ ] Main function refactored to use helpers
- [ ] All 26+ tests pass
- [ ] Main function ~25-30 lines
- [ ] No behavior changes
