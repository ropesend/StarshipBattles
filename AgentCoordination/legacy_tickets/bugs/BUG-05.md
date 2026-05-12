---
### 📝 User Update 2026-01-03 15:24
BUG-05

Stats Panel:
Logistics Should have the following entries for all resources that a vehicle consumes/holds/generates
- Max Capacity
- Amount Generated per second (100 game ticks)
- Constant Amount Used per second (100 game ticks) based on the contant usage
- Max Usage per sec (100 game ticks) based on constant usage + all weapons at maximum rate of fire
- Contant Rate Endurance - time that the resource will last at its constant rate of consumption + the amount it generates (this may be infinite if it generates faster than it uses)
- Max Rate Endurance - time that the resource will last at its maximum rate with all at maximum rate of fire.
- If a component is provided that hold, uses, or generates a resource all of the above should be included.  0 values an infinite values are indicated when appropriate.

### 📝 User Update 2026-01-03 16:39
Logistics:
If any component either contains, uses, or generates a resource then there are 6 lines that are nessesary for that resourse in the logistics section:
1) Total capacity
2) The rate of generation (may be 0)
3) The rate of use of the resource based on all of the constant use components
4) The rate of use of the resource if all intermitent use components use it at their fastest rate possible (so for weapons if they fire at their maximum rate) + the constant use amount
5) The endurance (time that the resource will last under constant use) - this should factor in both generation and constant use
6) The Max rate endurance - how long will the resource last if used at the rate defined in (2) rather than (3)

In my design I have Ammo, Energy, and Fuel storage so there should be 18 lines, but there are only 5 lines:
C:\Dev\Starship Battles\screenshots\screenshot_20260103_163646_310748_mouse_focus.png (shows that there are mostly just capacity reports, also shows the endurance being miscalculated which is part or a separate bug.
---

### 📝 User Update 2026-01-03 17:39
BUG-05
This is not yet solved. The 6 lines are now showing up when resource storage is added, or when continuous use items are added, however they are not showing up when items that use the resource are added.  Adding something that consumes a resource should cause the 6 lines to show up.  Examples of thes are a Shileld Regen or any of the weapons.
---

## Work Log
*   **[2026-01-03 16:15] Phase 1 - Reproduction:**
    *   Created test case `tests/repro_issues/test_bug_05_logistics.py`.
    *   Confirmed failure: Test failed with `AssertionError: Missing Energy Generation Row` as expected.
    *   Identified that `ui/builder/stats_config.py` is missing logic to generate rows for Usage, Generation, and Max Usage.

*   **[2026-01-03 16:25] Phase 2 & 3 - Implementation & Verification:**
    *   Implemented `get_resource_max_usage` in `ui/builder/stats_config.py`.
    *   Updated `get_logistics_rows` to generate `_gen`, `_constant`, and `_max_usage` rows.
    *   Updated reproduction test `tests/repro_issues/test_bug_05_logistics.py` to assert new keys and include weapon load.
    *   **VERIFIED:** Test passed. New rows are correctly generated.
    *   **[2026-01-03 16:58] Phase 3 - Verification Complete:**
        *   Ran `pytest tests/repro_issues/test_bug_05_logistics.py`.
        *   Test Passed. Confirmed all 6 required rows.

*   **[2026-01-03 17:45] QA Rejection Handling & Fix:**
    *   Received feedback: "Usage Only" components (Weapons) were not triggering rows, and Max Load was incorrectly 0 for inactive/uncrewed components.
    *   Created deep reproduction suite `tests/repro_issues/repro_bug_05_deep.py` to simulate realistic component loading.
    *   **Fix Implemented:**
        *   Modified `ship_stats.py` to calculate `potential_` consumption stats for all components regardless of active state.
        *   Updated `ui/builder/stats_config.py` to use these potential stats for "Max Load" calculations.
        *   Fixed legacy "Double Counting" of Shield Generation energy cost.
    *   **Verified:**
        *   `repro_bug_05_deep.py` passed: Confirmed Shield Regen cost (2.0) and Laser Cannon potential usage (25.0) even when uncrewed.
        *   Regressions checks passed.

## Solution Summary
Refactored `ship_stats.py` to calculate `potential_fuel/energy/ammo_consumption` which aggregates the theoretical maximum usage of all components on the ship, regardless of their current `is_active` status (e.g. damaged or missing crew). Updated `stats_config.py` to use these potential values for the "Max Load" and "Max Endurance" logistics rows. This ensures that the Ship Builder displays accurate projected stats for weapons and other consumers even during partial design states. Also removed a legacy logic block that was double-counting Shield Regeneration costs.



