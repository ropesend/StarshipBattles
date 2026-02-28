# Bug Reproduction Tests

This directory contains tests that reproduce specific bugs for regression tracking.
All tests in this directory now pass, indicating the bugs have been fixed.

## Status Summary

**Total Tests:** 63
**Status:** All FIXED (passing)
**Last Verified:** 2026-01-27

## Status Categories

- **FIXED**: Bug is fixed, test passes and serves as regression test
- **ACTIVE**: Bug still present, test documents the issue
- **NEEDS REVIEW**: Status unclear, needs investigation

## Test Index

| Test File | Bug ID | Status | Description |
|-----------|--------|--------|-------------|
| test_bug_01_crew_delay.py | BUG-01 | FIXED | Crew stat update on modifier change |
| test_bug_02_seeker.py | BUG-02 | FIXED | Seeker range calculation |
| test_bug_03_validation.py | BUG-03 | FIXED | Ammo/fuel warning persistence |
| test_bug_04_display.py | BUG-04 | FIXED | Stats rebuild hash display |
| test_bug_05_logistics.py | BUG-05 | FIXED | Missing logistics details |
| test_bug_05_rejected_fix.py | BUG-05 | FIXED | Usage visibility and max calculation |
| test_bug_06_combat_propulsion.py | BUG-06 | FIXED | Combat propulsion validation |
| test_bug_07_crash.py | BUG-07 | FIXED | Crash adding component with tohit modifier |
| test_bug_08_fuel_validation.py | BUG-08 | FIXED | Class requirements fuel storage |
| test_bug_09_endurance.py | BUG-09 | FIXED | Fuel endurance infinite |
| test_bug_09_hull_in_palette.py | BUG-09 | FIXED | Hull visibility in component palette |
| test_bug_10_logistics_update.py | BUG-10 | FIXED | Ammo usage triggers logistics row |
| test_bug_11_dialog_size.py | BUG-11 | FIXED | Confirmation dialog scrolling |
| test_bug_11_hull_update.py | BUG-11 | FIXED | Hull updates on class change |
| test_bug_12_energy_gen.py | BUG-12 | FIXED | Generator crew activation |
| test_bug_12_hull_layer_addition.py | BUG-12 | FIXED | Prevent non-hull addition to hull layer |
| test_bug_13_clear_removes_hull.py | BUG-13 | FIXED | Clear design removes hull |
| ~~test_bug_13_colony_flags.py~~ | BUG-13 | DELETED | Colony flag loading — covered by test_race_asset_loader.py and test_empire_asset_loading.py |
| test_bug_13_weapons_report.py | BUG-13 | FIXED | Weapons report drawing structure |
| test_bug_14_multi_planet_offset.py | BUG-14 | FIXED | Multi-planet position offset |
| test_bug_15_screenshot_strategy.py | BUG-15 | FIXED | Screenshot strategy layer support |
| test_bug_16_raw_data_button.py | BUG-16 | FIXED | Raw data button position |
| test_bug_17_drag_preview.py | BUG-17 | FIXED | Drag preview icon rendering |
| test_bug_27_ordertype.py | BUG-27 | FIXED | OrderType import in strategy screen |
| test_crash_planet_list.py | CRASH | FIXED | Planet list crash reproduction |
| test_crash_planet_list_method.py | CRASH | FIXED | Planet list method existence |

## Future Work

Consider merging these fixed bug tests into the main test suite to:
1. Improve test organization
2. Ensure regression coverage is maintained
3. Clean up this directory

This consolidation work was deferred to a future project (see PROJ-21 decisions.md).
