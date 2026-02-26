# Phase 4: Verify & Cleanup

**Objective:** Verify complexity reduction, run full test suite, clean up.

**File:** `game/ui/screens/fleet_report_filters.py`

---

## Tasks

### 4.1 Measure Complexity Reduction
- [ ] Run: `radon cc game/ui/screens/fleet_report_filters.py -s -a`
- [ ] Record `filter_ships` CC: _____ (target: < 15)
- [ ] Record helper function CCs:
  - `_get_ship_status_category`: _____ (target: < 5)
  - `_passes_status_filter`: _____ (target: < 3)
  - `_passes_binary_capability_filter`: _____ (target: < 4)
  - `_passes_warp_filter`: _____ (target: < 5)
  - `_passes_spaceyard_filter`: _____ (target: < 5)
  - `_passes_cargo_filter`: _____ (target: < 5)
  - `_passes_special_capabilities_filter`: _____ (target: < 8)
- [ ] Verify NO function exceeds CC 20

### 4.2 Run Full Test Suite
- [ ] Run: `pytest tests/ -n 12`
- [ ] Verify all tests pass (baseline: 6246)
- [ ] Record: _____ passed, _____ failed, _____ skipped

### 4.3 Run Targeted Filter Tests
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify all filter tests pass
- [ ] Record test count: _____ passed

### 4.4 Code Cleanup
- [ ] Remove any commented-out code
- [ ] Ensure all helper functions have docstrings
- [ ] Verify import organization (module-level vs late imports)
- [ ] Check for any unused imports

### 4.5 Final Verification
- [ ] Run: `radon cc game/ui/screens/fleet_report_filters.py -s -a`
- [ ] Confirm `filter_ships` CC < 20 (target: < 15)
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Confirm all tests pass

---

## Completion Criteria

- [ ] `filter_ships` CC reduced from 36 to below 15
- [ ] All helper functions have CC < 10
- [ ] Full test suite passes
- [ ] No behavioral changes (pure refactoring)
- [ ] Code is clean and well-documented
