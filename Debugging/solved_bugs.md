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

---

## [BUG-11] - Confirm Refit Dialog too small
* **Date Solved:** 2026-01-03 19:40
* **Original Issue:** The "Confirm Refit" dialog was too small, causing the multi-line message to be truncated and requiring scrolling.
* **Solution Implemented:** Increased `UIConfirmationDialog` dimensions in `game/ui/screens/builder_screen.py` from `(400, 200)` to `(600, 400)`.
---

## [BUG-12] - Generator produces 0 energy
* **Date Solved:** 2026-01-03 19:45
* **Original Issue:** Generator shows 0 energy generation instead of 25/s.
* **Solution Implemented:** **WORKING AS DESIGNED.** Investigation revealed the Generator was inactive due to unmet `CrewRequired: 1` requirement. The user's ship lacked Crew Quarters/Life Support.
* **Test Case:** `tests/repro_issues/test_bug_12_energy_gen.py`
* **Notes:** System correctly deactivates components when crew requirements are not met. User notification/validation improved in other tickets to clarify this dependency.

---

## [BUG-13] - Weapons Report: Simplify and unify damage/range/accuracy markers
* **Date Solved:** 2026-01-03 19:50
* **Original Issue:** The Weapons Report Panel lacked unified drawing methods and centralized "Points of Interest" for range and accuracy, leading to hardcoded and non-unified breakpoints.
* **Solution Implemented:** Implemented `_draw_unified_weapon_bar` with priority-based collision detection and unified `INTEREST_POINTS_RANGE` and `INTEREST_POINTS_ACCURACY`.
* **Test Case:** 
---

## [BUG-08] - Fuel Storage validation fails despite Fuel Tank presence
* **Date Solved:** 2026-01-03 20:05
* **Original Issue:** The ship builder reported "Needs Fuel Storage" even when a Fuel Tank was present.
* **Solution Implemented:** Fixed attribute mismatch in `ShipStatsCalculator` where it was looking for the wrong attribute name when aggregating resource storage capabilities (`max_amount` vs `amount`).
* **Test Case:** `tests/repro_issues/test_bug_08_fuel_validation.py`
---

## [BUG-07] - Crash in Weapons Panel (AttributeError)
* **Date Solved:** 2026-01-03 17:25
* **Original Issue:** The game crashed with an `AttributeError: 'ToHitAttackModifier' object has no attribute 'value'` when adding a component, specifically in the weapons panel drawing logic.
* **Solution Implemented:** Renamed `amount` to `value` in `ToHitAttackModifier` and `ToHitDefenseModifier` classes in `game/simulation/components/abilities.py` to match the API expectation in `ship.py`.
* **Test Case:** `tests/repro_issues/test_bug_07_crash.py`

---

## [BUG-08b] - Hull Visible in Ship Structure List (ID Collision with Legacy BUG-08)
* **Date Solved:** 2026-01-07
* **Original Issue:** The hull was incorrectly showing up in the ship's structure list in the Ship Builder, whereas it should be hidden from the user.
* **Solution Implemented:** Modified `ui/builder/layer_panel.py` to filter out components with IDs starting with `hull_`.
* **Test Case:** `tests/repro_issues/test_bug_08_hull_visible.py`

---

## [BUG-09b] - Hull Components Visible in Component List (ID Collision with Legacy BUG-09)
* **Date Solved:** 2026-01-07
* **Original Issue:** Hull components were incorrectly appearing in the component palette (selection list), which clutter the UI.
* **Solution Implemented:** Modified `ui/builder/left_panel.py` to filter out components with `type == "Hull"` in the `update_component_list()` method.
* **Test Case:** `tests/repro_issues/test_bug_09_hull_in_palette.py`

---

## [BUG-10b] - Hull Components Missing Required Abilities (ID Collision with Legacy BUG-10)
* **Date Solved:** 2026-01-07
* **Original Issue:** Hull components were missing requirements for Command & Control and Combat Propulsion.
* **Solution Implemented:** Implemented "Requirement Abilities" pattern. Created `RequiresCommandAndControl` and `RequiresCombatMovement` markers in `abilities.py`. Updated `ship_validator.py` and `ship_stats.py` to enforce and tally these markers.
* **Test Case:** `tests/repro_issues/test_bug_10_repro.py`

---

## [BUG-11b] - Hull Not Updated When Switching Ship/Class Type (ID Collision with Legacy BUG-11)
* **Date Solved:** 2026-01-08
* **Original Issue:** Switching a ship's type or class did not automatically update the hull component to the new default for that class.
* **Solution Implemented:** Modified `Ship.change_class` to auto-equip the new default hull after layer initialization and exclude the old hull from the component migration list.
* **Test Case:** `tests/repro_issues/test_bug_11_hull_update.py`

---

## [BUG-12] - Ship Builder: Component Addition to Hull Layer
* **Date Solved:** 2026-01-09
* **Original Issue:** The Ship Builder allowed any component to be added to the Hull layer, violating the structural integrity rules where only hull-type components should exist.
* **Solution Implemented:** Modified `game/simulation/ship_validator.py` to enforce the `HullOnly` restriction in `LayerRestrictionDefinitionRule`. It now explicitly blocks any component whose ID does not start with `hull_` when the `HullOnly` restriction is present.
* **Test Case:** `tests/repro_issues/test_bug_12_hull_layer_addition.py`

---

## [BUG-13] - Ship Builder: Clear Design Removes Hull
* **Date Solved:** 2026-01-09
* **Original Issue:** Using the "Clear Design" feature in the Ship Builder removed the mandatory hull component, leaving the ship in an invalid state.
* **Solution Implemented:** Modified `_clear_design` in `game/ui/screens/builder_screen.py` to skip the `LayerType.HULL` layer when clearing components. This ensures the structural hull is preserved while user-added components are removed.
* **Test Case:** `tests/repro_issues/test_bug_13_clear_removes_hull.py`

---

## [BUG-13b] - Colony Flags Replaced by Colored Circles
* **Date Solved:** 2026-01-18
* **Original Issue:** Colony flags in the strategy layer were replaced by colored circles when loading saved games. The saved `theme_path` was an absolute path that became invalid when the project location changed or when loading from a different machine.
* **Solution Implemented:** Modified `_load_assets()` in `game/ui/screens/strategy_scene.py` to recalculate the theme path using `GameConfig.asset_base_path` and the empire's `empire_theme_id` field, instead of trusting the saved absolute `theme_path`.
* **Test Case:** `tests/repro_issues/test_bug_13_colony_flags.py`
* **Notes:** Always derive asset paths relative to current project location rather than storing absolute paths in saves.

---

## [BUG-16] - Atmosphere Raw Data Button Mispositioned
* **Date Solved:** 2026-01-18
* **Original Issue:** The Raw Data button for atmosphere data was positioned at the top-left of the entire planet detail panel instead of the top-right of the graph box.
* **Solution Implemented:** Modified `game/ui/screens/strategy_screen.py` to calculate button position based on `graph_rect` during initialization instead of using `(0, 0)` placeholder.
* **Test Case:** `tests/repro_issues/test_bug_16_raw_data_button.py`
* **Notes:** Button position now correctly calculated as `(graph_rect.right - 22, graph_rect.top + 2)` at construction time.

---

## [BUG-18] - Available Designs Need Miniature Portrait Icons
* **Date Solved:** 2026-01-18
* **Original Issue:** Available Designs list in Build Queue lacked visual icons for each design.
* **Solution Implemented:** Modified `game/ui/screens/build_queue_screen.py` to wrap each design in a UIPanel row with a 36x36 portrait icon. Added `_load_design_portrait()` method that loads portraits from theme assets or falls back to colored placeholders.
* **Test Case:** `tests/ui/test_build_queue_drag_drop.py`
* **Notes:** Portraits loaded from `assets/ShipThemes/{theme}/Portraits/{ShipClass}_Portrait.jpg` with fallback placeholders by type.

---

## [BUG-20] - Build Queue Items Need Miniature Portrait Icons
* **Date Solved:** 2026-01-18
* **Original Issue:** Build Queue items lacked visual portrait icons.
* **Solution Implemented:** Modified `_refresh_queue_display()` in `game/ui/screens/build_queue_screen.py` to add 50x50 portrait icons to each queue item. Added `_load_queue_item_portrait()` method for design lookup and portrait loading.
* **Test Case:** `tests/ui/test_build_queue_drag_drop.py`
* **Notes:** Provides visual consistency with Available Designs list (BUG-18).

---

## [BUG-21] - Build Queue Drag/Drop Leaves Stale Graphics
* **Date Solved:** 2026-01-18
* **Original Issue:** Dragging items from the build queue and dropping outside the panel left visual artifacts.
* **Solution Implemented:** Added `came_from_queue` flag in `game/ui/screens/build_queue_screen.py` to track item origin. On drop outside queue panel, calls `_refresh_queue_display()` if item originated from queue.
* **Test Case:** `tests/ui/test_build_queue_drag_drop.py`
* **Notes:** Ensures queue visual is always in sync with `planet.construction_queue` after any drag operation.

---

## [BUG-23] - Galactic Planet Registry Missing Owner Column
* **Date Solved:** 2026-01-18
* **Original Issue:** Owner column only showed generic labels ("Unowned", "Player", "Enemy") instead of actual empire names.
* **Solution Implemented:** Enhanced `_get_owner_name()` in `game/ui/screens/planet_list_window.py` to look up actual empire names from `galaxy.empires`. Added star prefix for player colonies, widened column to 140px, and set default sort to owner.
* **Test Case:** `tests/ui/test_planet_list_window.py`
* **Notes:** Flag icons deferred for future enhancement; star (★) indicator provides visual distinction for player colonies.

---

## [BUG-19] - Planet Window Missing Colony Complexes List
* **Date Solved:** 2026-01-18
* **Original Issue:** The planet window in the main Strategy Layer had no list indicating what complexes exist on a colony.
* **Solution Implemented:** Updated `format_planet_info()` in `game/ui/screens/strategy_screen.py` (the main sidebar method) to add colony status and facilities list. Shows "Colony Status: Owned" and lists all complexes by name for colonized planets; uncolonized planets show no change.
* **Test Case:** 195 passed (strategy + planet tests)
* **Notes:** There are TWO `format_planet_info` methods - one in `strategy_detail_fmt.py` (PlanetReportPanel) and one in `strategy_screen.py` (main sidebar). Both were updated.

---

## [BUG-22] - Zoom Level Indicator Visible When Sub-Panels Open
* **Date Solved:** 2026-01-18
* **Original Issue:** The Strategy Layer Zoom level indicator on the bottom left was visible when sub-panels (Build Queue, Design Workshop, Planet List) were open, and mouse wheel zoom still worked.
* **Solution Implemented:** Added `planet_list_window` tracking to `strategy_screen.py`, updated `_has_modal_open()` to check for Planet List Window, and modified `strategy_input_handler.py` to block mouse wheel zoom when any modal is open.
* **Test Case:** 4 passed (strategy button tests)
* **Notes:** Modal check now covers: Build Queue Screen, Fleet Orders Window, Design Workshop, and Planet List Window.

---

## [BUG-25] - Build Queue Category Selection Does Not Clear Stale Options
* **Date Solved:** 2026-01-18
* **Original Issue:** Selecting a category with fewer designs than the previous category left stale option elements visible.
* **Solution Implemented:** Fixed list mutation during iteration in `game/ui/screens/build_queue_screen.py` by copying the elements list before iterating and killing elements.
* **Test Case:** 18 passed (build queue tests)
* **Notes:** When iterating over UI element lists to kill them, always copy the list first to avoid skipping elements.

---

## [BUG-27] - Planet List Missing Owner Filter
* **Date Solved:** 2026-01-18
* **Original Issue:** The Planet List window had no UI filter for Owner (None/Player/Opponents).
* **Solution Implemented:** Added "Owner:" section with All/None buttons and toggle buttons (Player, Enemy, Unowned) to `planet_list_window.py`. Updated `filter_planets()` in `planet_list_filters.py` to accept `filter_owner` and `empire` parameters and filter by owner category.
* **Test Case:** 28 passed (planet-related tests)
* **Notes:** Filter logic: Unowned = `owner_id is None`, Player = `owner_id == empire.id`, Enemy = `owner_id != None and != empire.id`.

