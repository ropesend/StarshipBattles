# ✅ Solved Bugs Archive
*DO NOT DELETE FROM THIS FILE. APPEND ONLY.*

## [BUG-ID] - [Bug Name/Brief Description]
* **Date Solved:** YYYY-MM-DD HH:MM
* **Original Issue:** [Summary of what was wrong]
* **Solution Implemented:** [Technical details of the code change that fixed it]
* **Test Case:** [Reference to the test file that covers this]
* **Notes:** [Any warnings for future refactors]

## [BUG-01] - Stats Panel Crew Update Delay
* **Date Solved:** 2026-01-03 14:26
* **Original Issue:** The "Crew required" statistic in the Stats Panel did not update immediately when a modifier (like Mount Size) was applied. Life Support requirements also failed to scale with modifiers.
* **Solution Implemented:** 
    1. Updated `ship_stats.py` to correctly iterate over `ability_instances` as a list instead of a dictionary, ensuring dynamic ability values are used.
    2. Updated `modifiers.py` to include `crew_req_mult`, `crew_capacity_mult`, `life_support_capacity_mult`, and other resource multipliers in `apply_modifier_effects`.
* **Test Case:** `tests/repro_issues/test_bug_01_crew_delay.py`
* **Notes:** `ability_instances` is a list, not a dict. Future refactors should maintain this structure or update `ship_stats.py` accordingly. Modifier keys must be explicitly handled in `apply_modifier_effects`.

---

## [BUG-02] - Weapons Report: Seeker Stats missing
* **Date Solved:** 2026-01-03 15:40
* **Original Issue:** The Weapons Report Panel did not display range and damage for seeker weapons. The range should be calculated as 80% * Speed * Endurance, but reverted to 0.0.
* **Solution Implemented:** Updated `SeekerWeaponAbility.__init__` in `game/simulation/components/abilities.py` to correctly synchronize `_base_range` with the calculated range.
* **Test Case:** `tests/repro_issues/test_bug_02_seeker.py`
* **Notes:** `_base_range` must be kept in sync with derived values for the weapon report to pick it up correctly.

---


## [BUG-03] - Stats Panel Resource Validation Logic
* **Date Solved:** 2026-01-03 15:55
* **Original Issue:** Stats Panel validation logic accepted *any* resource to satisfy a specific requirement (e.g., adding Energy satisfied Fuel recommendations).
* **Solution Implemented:** Refactored `ResourceDependencyRule` in `ship_validator.py` to use a generic Set-based approach (`missing = needed - stored`). Logic guarantees only specific missing resources trigger warnings.
* **Test Case:** `tests/repro_issues/test_bug_03_validation.py`
* **Notes:** `ResourceDependencyRule` now handles dynamic resources strictly.

---

## [BUG-04] - Stats Panel Display "--"
* **Date Solved:** 2026-01-03 16:05
* **Original Issue:** Immediately after a resource storage component is added, the stats panel shows "--" for values instead of updating.
* **Solution Implemented:** Removed early returns in `ui/builder/right_panel.py` (`on_ship_updated`) that were preventing `update_stats_display` from running after `rebuild_stats`.
* **Test Case:** `tests/repro_issues/test_bug_04_display.py`
* **Notes:** Ensure `update_stats_display` is called whenever stats might have changed, even if strict rebuilds occurred.
---

