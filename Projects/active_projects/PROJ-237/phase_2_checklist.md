# Phase 2: Extract Helper Functions

**Goal:** Extract 4 helper functions to reduce complexity without changing behavior.

**File:** `game/ui/screens/fleet_report_filters.py`

---

## Checklist

### 2.1 Extract `_passes_binary_filter()` helper

- [ ] **2.1.1 Create helper function**
  - Location: After line 122 (after `calculate_fleet_stats`, before `filter_ships`)
  - Signature:
    ```python
    def _passes_binary_filter(
        ship: "ShipInstance",
        filter_state: Dict[str, bool],
        show_key: str,
        no_key: str,
        capability_checker: Callable[["ShipInstance"], bool]
    ) -> bool:
        """Return True if ship passes the binary filter, False if it should be excluded."""
    ```
  - Logic:
    ```python
    show_has = filter_state.get(show_key, True)
    show_not = filter_state.get(no_key, True)
    if show_has and show_not:
        return True  # No filtering needed
    has_capability = capability_checker(ship)
    if has_capability and not show_has:
        return False
    if not has_capability and not show_not:
        return False
    return True
    ```

- [ ] **2.1.2 Add Callable import**
  - Add `Callable` to typing imports at top of file

- [ ] **2.1.3 Run tests**
  - Command: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
  - All tests must pass

### 2.2 Extract `_has_cargo()` helper

- [ ] **2.2.1 Create helper function**
  - Location: After `_passes_binary_filter`
  - Signature:
    ```python
    def _has_cargo(ship: "ShipInstance") -> bool:
        """Return True if ship has any cargo (including population)."""
        return bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
    ```

- [ ] **2.2.2 Run tests**
  - All tests must pass

### 2.3 Extract `_passes_special_capability_filters()` helper

- [ ] **2.3.1 Create helper function**
  - Location: After `_has_cargo`
  - Signature:
    ```python
    def _passes_special_capability_filters(
        ship: "ShipInstance",
        filter_state: Dict[str, bool]
    ) -> bool:
        """Return True if ship passes all special capability filters."""
    ```
  - Logic: Move lines 177-194 from `filter_ships` into this function
  - **IMPORTANT:** Keep the late import inside this function
  - Return `True` if passes all, `False` if any filter excludes

- [ ] **2.3.2 Run tests**
  - All tests must pass

### 2.4 Extract `_get_ship_status_category()` helper

- [ ] **2.4.1 Create helper function**
  - Location: After `_passes_special_capability_filters`
  - Signature:
    ```python
    def _get_ship_status_category(ship: "ShipInstance") -> str:
        """Return the ship's status category for filtering.

        Categories are mutually exclusive and checked in priority order:
        destroyed > derelict > damaged > undamaged
        """
        if not ship.is_alive:
            return 'destroyed'
        if ship.is_derelict:
            return 'derelict'
        if ship.is_damaged():
            return 'damaged'
        return 'undamaged'
    ```

- [ ] **2.4.2 Run tests**
  - All tests must pass

### 2.5 Extract `_passes_status_filter()` helper

- [ ] **2.5.1 Create helper function**
  - Location: After `_get_ship_status_category`
  - Signature:
    ```python
    def _passes_status_filter(ship: "ShipInstance", filter_state: Dict[str, bool]) -> bool:
        """Return True if ship passes the status filter."""
        category = _get_ship_status_category(ship)
        return filter_state.get(f'show_{category}', True)
    ```

- [ ] **2.5.2 Run tests**
  - All tests must pass

---

## Verification

```bash
# After each extraction
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Full suite after all extractions
pytest tests/ -n 12
```

---

## Completion Criteria
- [ ] 5 helper functions created
- [ ] All tests pass (26+)
- [ ] No behavior changes (helpers not yet used by main function)
