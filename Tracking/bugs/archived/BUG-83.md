# BUG-83: Fleet Report - Missing special capability columns and filters

## Description

The Fleet Report should also have a column for the following: Can Destroy planet, Can open warp point, Can close warp point, Can destroy star, Can create sphere world. These should all allow filtering as well.

## Priority
Medium

## Status (Awaiting Confirmation)

## Fix

Added 5 new special capability columns with full filtering and sorting support across 4 files.

### Columns Added (in `column_manager.py`)
| Column ID | Title | Ability Name |
|---|---|---|
| `can_destroy_planet` | DestrPlanet | DestroyPlanet |
| `can_open_warp` | OpenWarp | OpenWarpPoint |
| `can_close_warp` | CloseWarp | CloseWarpPoint |
| `can_destroy_star` | DestrStar | DestroyStar |
| `can_create_sphere` | Sphere | CreateSphereWorld |

All hidden by default, togglable in sidebar. Uses `FleetCapabilityCalculator._ship_has_ability()`.

### Files Modified
1. **`game/ui/screens/column_manager.py`**: 5 columns, `SPECIAL_CAPABILITY_COLUMNS` mapping, value extraction
2. **`game/ui/screens/fleet_report_view_model.py`**: 10 filter booleans, toggle logic, state dict, labels
3. **`game/ui/screens/fleet_report_filters.py`**: Filtering loop + sorting for special capabilities
4. **`game/ui/screens/fleet_report_window.py`**: "SPECIAL CAPABILITIES" sidebar filter section

### Note
`CreateSphereWorld` ability doesn't exist yet. Column will always show "No" until implemented.

## Tests

13 new tests:
- `TestSpecialCapabilityColumns` (6 tests): existence, visibility, mapping, value extraction
- `TestSpecialCapabilityFilter` (3 tests): filter show/hide logic
- `TestSpecialCapabilitySort` (1 test): sorting by capability
- `TestViewModelSpecialFilters` (3 tests): toggle, state dict, labels

All 145 fleet report tests pass (132 existing + 13 new).

## Work Log
- 2026-02-11: Implemented 5 special capability columns with filters and sorting.
