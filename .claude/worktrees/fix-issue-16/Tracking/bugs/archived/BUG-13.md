## Description
Weapons Report:
The report of damage, accuracy and range markers should be somewhat simplified,  At any point of interest all 3 should be indicated, damage, range and accuracy(for beam weapons), points of intest are:
0 range, 20%, 40%, 60%, 80%, 100% range, 99% accuracy, 90%, 80%, 70%... down to 10% and then 1% (accuracy percentages only apply for beam weapons)
So each of the points of interest should report all 3 values.  Calculate the size needed for each displaye element, if they are too crowded then ommit some.  prioritize the 0 range and max range, if there are other overlaps prioritize accuracy, and if ranges overlap with each other then change to 30% or 40% between points.  What is displayed will depend on the scale, so a point defense cannon displayed with a seeker might not have room for all the elements but if it is displayed on its own then it probably does.

## Status (Awaiting Confirmation)

## Work Log

- [2026-01-03 19:47] Reproduction confirmed.
  - Created `tests/repro_issues/test_bug_13_weapons_report.py`.
  - Confirmed `WeaponsReportPanel` lacks `INTEREST_POINTS` and a unified drawing method.
  - Current implementation uses separate `_draw_beam_weapon_bar` and `_draw_projectile_weapon_bar` with hardcoded, non-unified breakpoints.
- [2026-01-03 19:50] Fix Implemented and Verified.
  - Implemented `_draw_unified_weapon_bar` with priority-based collision detection.
  - Unified `INTEREST_POINTS_RANGE` and `INTEREST_POINTS_ACCURACY`.
  - Verified with `tests/repro_issues/test_bug_13_weapons_report.py`.
  - Status set to Awaiting Confirmation.

