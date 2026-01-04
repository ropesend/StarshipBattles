## Description
I have fuel storage on my design, but the ship stats window claims I still need fuel storage:
C:\Dev\Starship Battles\screenshots\screenshot_20260103_155657_194338_mouse_focus.png (shows that there is a Fuel Tank)
C:\Dev\Starship Battles\screenshots\screenshot_20260103_155737_717184_mouse_focus.png (shows that there is still a need for fuel storage)

## Status (Pending)

## Work Log
- [2026-01-03 17:35] Updated test to use `load_components` and real data. Test PASSED (failed to reproduce). Warning is correctly suppressed in test environment.
- Hypothesis: UI might be using a different validation path or state. Or the component in the screenshot is not `fuel_tank`.
- [2026-01-03 17:50] Discovered root cause: `ClassRequirementsRule` expects `FuelStorage` ability, but `Fuel Tank` provides `ResourceStorage`.
- [2026-01-03 17:55] Created new reproduction test `test_class_requirements_fuel_storage_failure` targeting `get_missing_requirements()`. Test PASSED (reproduction confirmed).
- [2026-01-03 18:05] Applied fix in `ship_stats.py`: Added aliasing to map `ResourceStorage` (fuel) to `FuelStorage` key during aggregation.
- [2026-01-03 18:10] Verified fix with `pytest tests/repro_issues/test_bug_08_fuel_validation.py`. Test PASSED (assertion that no error exists succeeded).
- [2026-01-03 18:15] BUG RESOLVED.

