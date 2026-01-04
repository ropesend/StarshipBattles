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

## [BUG-09] - Fuel Endurance Infinite Calculation Error
* **Date Solved:** 2026-01-03 17:43
* **Original Issue:** Fuel Endurance was incorrectly calculated as "Infinite" because `ui/builder/stats_config.py` handled any duration > 99,999s as infinite.
* **Solution Implemented:** Removed the arbitrary limit (`val > 99999`) in `ui/builder/stats_config.py`. Now only `float('inf')` triggers the "Infinite" label.
* **Test Case:** `tests/repro_issues/test_bug_09_endurance.py`

---

## [BUG-05] - Stats Panel: Missing detailed Logistics
* **Date Solved:** 2026-01-03 17:45
* **Original Issue:** Stats Panel: Missing detailed Logistics (Max Cap, Gen/Use Rates, Endurance) for all resources.
* **Solution Implemented:** Refactored `ship_stats.py` to calculate `potential_fuel/energy/ammo_consumption` which aggregates the theoretical maximum usage of all components regardless of active status. Updated `stats_config.py` to use these potential values for "Max Load" and "Max Endurance". Fixed legacy double-counting of Shield Regen costs.
* **Test Case:** `tests/repro_issues/repro_bug_05_deep.py`
* **Notes:** `tests/repro_issues/test_bug_05_logistics.py` also exists as an initial repro.

---

## [BUG-06] - Combat Propulsion Validation Error
* **Date Solved:** 2026-01-03 16:55
* **Original Issue:** "Needs Combat Propulsion" error appeared even with an Engine equipped.
* **Solution Implemented:** Fixed two root causes: 1) `ShipStatsCalculator` ignored `CombatPropulsion` abilities (missing `thrust_force` check). 2) `ShipDesignValidator` ignored the candidate component during addition checks, causing circular dependency failures.
* **Test Case:** `tests/repro_issues/test_bug_06_combat_propulsion.py`
* **Notes:** Validation logic must always include the 'candidate' component to accurately predict the state post-addition.


---

## [BUG-10] - Ship Stats not updating for Ammo/Ordinance
* **Date Solved:** 2026-01-03 17:58
* **Original Issue:** `ShipStatsCalculator` failed to see ammo/ordinance consumption because it checked `reload_time` on the Component instead of the WeaponAbility.
* **Solution Implemented:** Updated `_calculate_combat_endurance` in `ship_stats.py` to iterate through abilities and retrieve `reload_time` from `WeaponAbility` instances.
* **Test Case:** `tests/repro_issues/test_bug_10_logistics_update.py`
