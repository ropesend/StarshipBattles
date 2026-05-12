# BUG-11: Hull Not Updated When Switching Ship/Class Type

## Description
From the recent Refactor: `active_refactor.md`
- Switching to a different type of ship or class of ship should change the type of hull in the vehicle.

## Status
Fixed

## Work Log
| Date | Action |
| :--- | :--- |
| 2026-01-07 | Ticket created via Protocol 01. |
| 2026-01-07 | BUG Resolution started. Status set to [In-Progress]. |
| 2026-01-07 | Created reproduction test `tests/repro_issues/test_bug_11_hull_update.py`. |
| 2026-01-07 | Confirmed failure: `AssertionError: Hull should have updated to hull_frigate`. |
| 2026-01-08 | Reproduced failure with `tests/repro_issues/test_bug_11_hull_update.py`. |
| 2026-01-08 | Implemented fix in `Ship.change_class`. Auto-equips new default hull after layer initialization. Excludes old hull from migration list. |
| 2026-01-08 | Resolved regressions in `test_ship.py` and `test_planetary_complex.py` caused by increased component count/mass. |
| 2026-01-08 | All entity tests passed. |

## Reproduction Test Results
```bash
pytest tests/repro_issues/test_bug_11_hull_update.py -v
...
FAILED tests/repro_issues/test_bug_11_hull_update.py::test_hull_updates_on_class_change_no_migrate - AssertionError: Hull should have updated to hull_frigate
FAILED tests/repro_issues/test_bug_11_hull_update.py::test_hull_updates_on_class_change_with_migrate - AssertionError: Hull should have updated to hull_frigate
```
