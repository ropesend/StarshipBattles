# Phase 3: Implement Dispatch & Verify

**Goal:** Replace if-elif chain with dispatch dict, verify final CC, and clean up.

**Expected final CC:** <5 for `_get_column_value`

---

## Tasks

### 3.1 Create Dispatch Dict

- [x] **Add class-level constant** after line 52 (after SPECIAL_CAPABILITY_COLUMNS):
  ```python
  # Column handlers that take only ship parameter
  # Capability columns are handled separately (require col_id)
  ```

- [x] **Add property or method** to build handler dict in `__init__` or as lazy property:
  ```python
  def _get_column_handlers(self) -> Dict[str, Callable]:
      """Return mapping of column IDs to handler methods."""
      return {
          "serial": self._format_serial,
          "design": self._format_design,
          "name": self._format_name,
          "hp_pct": self._format_hp_pct,
          "status": self._format_status,
          "speed": self._format_speed,
          "tonnage": self._format_tonnage,
          "warp": self._format_warp,
          "spaceyard": self._format_spaceyard,
          "transport": self._format_transport,
          "resources": self._format_resources,
          "cargo": self._format_cargo,
      }
  ```

---

### 3.2 Refactor `_get_column_value` to Use Dispatch

- [x] **Replace entire if-elif chain** with dispatch logic:
  ```python
  def _get_column_value(self, ship: "ShipInstance", col_id: str) -> str:
      """Get display value for a column.

      Args:
          ship: Ship instance.
          col_id: Column identifier.

      Returns:
          String value to display.
      """
      # Image columns handled separately
      if col_id in ("portrait", "topdown"):
          return ""

      # Special capability columns need col_id parameter
      if col_id in SPECIAL_CAPABILITY_COLUMNS:
          return self._format_capability(ship, col_id)

      # Dispatch to handler
      handlers = self._get_column_handlers()
      handler = handlers.get(col_id)
      if handler:
          return handler(ship)

      # Unknown column
      return ""
  ```

- [x] **Run tests:** `pytest tests/unit/ui/screens/test_fleet_data_source.py -v`
- [x] **Verify:** All 41 tests pass

---

### 3.3 Verify Cyclomatic Complexity

- [x] **Run radon:**
  ```bash
  radon cc game/ui/screens/fleet_data_source.py -s -a
  ```

- [x] **Actual results:**
  - `_get_column_value`: CC = 4 (was 29) ✅
  - `_format_status`: CC = 4
  - `_format_resources`: CC = 5
  - Other handlers: CC = 1-2 each
  - File average: A (2.17)

- [x] **Document final CC** in decisions.md

---

### 3.4 Run Full Test Suite

- [x] **Run targeted tests:**
  ```bash
  pytest tests/unit/ui/screens/test_fleet_data_source.py -v
  ```
  Result: 41 passed

- [x] **Run full suite:**
  ```bash
  pytest tests/ -n 12
  ```
  Result: 12734 passed, 1 skipped

---

### 3.5 Final Cleanup

- [x] **Review code:** All handlers have consistent docstrings
- [x] **Check imports:** Added `Callable` import for type hint
- [x] **Verify formatting:** Code follows project patterns

---

### 3.6 Update Project Status

- [x] **Update plan.md:** All phases marked complete
- [x] **Update decisions.md:** Final CC documented (CC 29 -> 4)
- [x] **Commit changes:** (pending)

---

## Completion Criteria

- `_get_column_value` CC reduced from 29 to <5
- All tests passing (30+ tests)
- Dispatch dict pattern implemented
- Code is clean and well-documented
- Changes committed
