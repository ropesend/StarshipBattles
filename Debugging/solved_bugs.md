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

---

## [BUG-14] - Multi-Planet Sectors Need Planet Position Offset
* **Date Solved:** 2026-01-19
* **Original Issue:** In the strategy layer, planets in multi-planet sectors were not positioned correctly. The largest planet needed to be offset left by 20% of its diameter, and smaller planets needed to be arranged using polar coordinates centered on the largest planet.
* **Solution Implemented:** Modified `game/ui/screens/strategy_renderer.py` (lines 344-387) to: (1) Offset largest planet left by 20% of diameter; (2) Position smaller planets using polar coordinates centered on largest planet with angles [0°] for 1, [30°,-30°] for 2, [15°,0°,-45°] for 3; (3) Set center-to-center distance to 1.5x largest planet radius.
* **Test Case:** `tests/repro_issues/test_bug_14_multi_planet_offset.py` (9 passed)
* **Notes:** Smaller planets orbit around the largest planet's center, not the hex center.

---

## [BUG-17] - Build Queue Drag and Drop Not Visually Obvious
* **Date Solved:** 2026-01-19
* **Original Issue:** In the build queue, dragging and dropping was not visually obvious - the dragged item seemed to disappear.
* **Solution Implemented:** Modified `game/ui/screens/strategy_scene.py` (lines 152-154) to call `build_queue_screen.draw(screen)` in the render loop. The drag preview code in `build_queue_screen.py` was working but never being rendered because `draw()` wasn't called from the main scene.
* **Test Case:** `tests/ui/test_build_queue_drag_drop.py` (3 passed)
* **Notes:** The root cause was the missing `draw()` call in strategy_scene, not the preview rendering logic itself.
---

## [BUG-24] - Cannot Add Ships to Build Queue With Space Yard
* **Date Solved:** 2026-01-18
* **Original Issue:** Ships could not be added to the build queue because the `has_space_shipyard` property was checking for an `abilities` dictionary, which is absent in saved design JSON (which uses component IDs).
* **Solution Implemented:** Updated `game/strategy/data/planet.py` to check for both component IDs (real saved designs) and `abilities` dictionaries (test fixtures).
* **Test Case:** Production and planetary facilities tests (`tests/strategy/test_planet_facilities.py`)

---

## [BUG-26] - Overlapping planet drawn in System and Sector Report panels
* **Date Solved:** 2026-01-19
* **Original Issue:** Ghost planet icons remained visible in UI panels due to list mutation during iteration when calling `kill()` on items. Position also became stale after hide/show cycles.
* **Solution Implemented:** 
    1. Fixed list mutation by copying lists before iteration in `system_tree_panel.py`, `planet_report_panel.py`, and `build_queue_screen.py`.
    2. Added explicit `layout()` calls in `strategy_screen.py:show_ui()` to refresh tree positioning after returning from the Build Queue.
* **Test Case:** Strategy and build queue tests (`tests/ui/test_build_queue_drag_drop.py`, `tests/strategy/test_strategy_logic.py`)

---

## [BUG-28] - Show strategic move speed in Design Studio
* **Date Solved:** 2026-01-20
* **Original Issue:** The Design Studio ship stats panel lacked a display for strategic movement speed (hexes per turn).
* **Solution Implemented:**
    1. Implemented `get_strategic_speed` in `ui/builder/stats_config.py` to calculate speed using the formula `(total_strategic_movement * 25) / mass`.
    2. Added `strategic_speed` to the `main` systems group in `data/stats_layout.json`.
* **Test Case:** Verified via `tests/integration/test_strategic_abilities.py` mobility logic.

---

## [BUG-15] - Screenshot System Strategy Layer Support
* **Date Solved:** 2026-01-20
* **Original Issue:** The screenshot system did not work in the strategy layer or Build Queue screen. F12 key was unresponsive in the Build Queue modal.
* **Solution Implemented:**
    1. Added `capture_strategy_layer()` method to `ScreenshotManager` for layered strategy scene capture.
    2. Added F12/F11 handlers in `strategy_input_handler.py` for strategy layer screenshots.
    3. Added F12 handler in `build_queue_screen.py` for Build Queue screenshots.
    4. Fixed `_show_screenshot_toast()` crash - incorrect `rect=` parameter changed to `UIMessageWindow` with correct API.
* **Test Case:** `tests/repro_issues/test_bug_15_screenshot_strategy.py`
* **Notes:** Root cause was `TypeError` crash in toast notification due to incorrect pygame_gui API usage (UILabel with `rect=` instead of `relative_rect=`).

---

## [BUG-29] - Build Queue Shows Designs From Other Games
* **Date Solved:** 2026-01-21
* **Original Issue:** In the Build Queue, designs from previous game sessions appeared in new games.
* **Solution Implemented:** Commented out the `_migrate_temp_designs()` call in `save_game_service.py` which was copying designs from the temp folder into new saves.
* **Test Case:** `tests/repro_issues/test_bug_29_design_contamination.py`
* **Notes:** The temp design migration feature was copying stale designs from previous sessions into every new game. New games should start with empty design libraries.

---

## [BUG-30] - Load Game Buttons Non-Functional
* **Date Solved:** 2026-01-20
* **Original Issue:** Load, Show Turns, and Delete buttons in the Load Game dialog did not respond to clicks. Only Cancel worked.
* **Solution Implemented:** Fixed `_handle_selection_change()` in `save_selection_window.py` to use `item["text"]` dictionary access instead of `item.text` dot notation, since `UISelectionList.item_list` returns dictionaries.
* **Test Case:** `tests/unit/ui/test_save_selection.py`
* **Notes:** The `hasattr(item, 'text')` check returned False for dicts, causing `str(item)` to convert the entire dictionary to a string which never matched.

## [BUG-31] - Planet Selection in Zoomed Strategy Layer
* **Date Solved:** 2026-01-24 05:29
* **Original Issue:** In the strategy Layer, when you zoom in on a sector containing multiple planets, you should be able to select the planet on the screen by left clicking on it, they are separated out in their sector.
* **Solution Implemented:**
### 2026-01-23 - Fix Implemented
**Root Cause:** When zoomed in (>= 1.5x), the renderer visually spreads planets within a hex (largest planet left, smaller planets arranged around it using polar coordinates). However, the picking logic only checked which hex was clicked using `pixel_to_hex()` - it didn't account for the visual positions of individual planets.

**Solution:** Added `_hit_test_planets()` method to `strategy_input_handler.py` that:
1. Computes the same expanded planet positions as the renderer (using identical layout algorithm)
2. Performs hit-testing against each planet's screen position and drawn radius
3. Returns the specific planet clicked, which is then prioritized in selection

**Files Modified:**
- `game/ui/screens/strategy_input_handler.py`:
  - Added `_hit_test_planets()` method (lines 276-367)
  - Modified `_handle_picking()` to call hit-test when zoomed >= 1.5x

**Testing:** All unit tests pass. Manual testing required to confirm planets can be clicked individually when zoomed in.

---

## [BUG-32] - Planet Filter Sliders Should Have Dynamic Min/Max Values
* **Date Solved:** 2026-01-24 05:29
* **Original Issue:** In the planets window - All of the sliders for filtering planets should have minimums and maximums based on the values of the planets, if the hottest planet is 576 kelvin and the coldest it 33 then the slider should go from 33 to 576. All of the sliders should be like that (mass, Gravity, and any new ones that get added).
* **Solution Implemented:**
### 2026-01-23 - Fix Implemented
**Root Cause:** The planet list filter sliders (Gravity, Temperature, Mass) were created with hardcoded min/max limits (e.g., 0-10g, 0-2000K, 0-500 Earth masses) instead of calculating ranges from actual planet data in the galaxy.

**Solution:**
1. Added `_compute_planet_ranges()` method that iterates through all planets and calculates actual min/max values for gravity, temperature, and mass
2. Ranges include 5% padding for better usability
3. Updated `filter_ranges` initialization to use computed values
4. Updated slider creation to use dynamic ranges from `_planet_ranges`

**Files Modified:**
- `game/ui/screens/planet_list_window.py`:
  - Added `_compute_planet_ranges()` method (lines 183-232)
  - Modified `filter_ranges` initialization to use computed ranges (lines 38-44)
  - Updated slider creation to use dynamic ranges (lines 375-381)

**Testing:** All planet list tests pass. Manual testing required to confirm sliders show appropriate ranges based on galaxy data.

---

## [BUG-33] - Planet Graphics Don't Move With Column Reorder
* **Date Solved:** 2026-01-24 05:29
* **Original Issue:** In the Planet List window, When you try to move the column containing the graphic of the planet, the header moves to the right, but the actual planet graphic stays in the left hand column. The graphics need to move with the columns.
* **Solution Implemented:**
### 2026-01-23 - Fix Implemented
**Root Cause:** In `_rebuild_row_pool()`, the icon column widget was created with hardcoded position `(5, 5)` instead of using the calculated `x_off` offset like text columns. When columns are reordered, `_rebuild_row_pool()` recreates widgets in the new order, but the icon always appeared at position (5, 5) regardless of its column position.

**Solution:** Changed the icon widget creation to use `x_off + 5` for the x-coordinate instead of hardcoded `5`, matching how text columns are positioned.

**Files Modified:**
- `game/ui/screens/planet_list_window.py` (line 568):
  - Changed `pygame.Rect(5, 5, 40, 40)` to `pygame.Rect(x_off + 5, 5, 40, 40)`

**Testing:** All planet-related unit tests pass. Manual testing required to confirm planet graphics move correctly with column reordering.

---

## [BUG-34] - Fleet Report Window shows incorrect warp capability
* **Date Solved:** 2026-01-24 05:29
* **Original Issue:** In the Fleet Report Window, a vehicle that has a warp drive but doesn't have the resource capacity to run it, should not be listed as having warp capability.
* **Solution Implemented:**
- 2026-01-23: Ticket created.
- 2026-01-23: Fixed. Modified `has_warp_capability()` in `game/ui/screens/fleet_report_filters.py` to check resource storage capacity in addition to warp drive tonnage. A ship is now only considered warp-capable if:
  1. It has a warp drive with sufficient tonnage for its mass
  2. The warp drive is undamaged
  3. It has enough energy storage capacity (`max_energy >= warp_energy_cost`)
  4. It has enough fuel storage capacity (`max_fuel >= warp_fuel_cost`)

  All existing tests pass.

---

## [BUG-36] - Load Design Screen shows formatting tags
* **Date Solved:** 2026-01-24 05:29
* **Original Issue:** In the Design Workshop, the Load Screen Design shows some of the formatting tags. Filters, and the design names both have formatting tags instead of the formatting.
* **Solution Implemented:**
- 2026-01-23: Ticket created from user report.
- 2026-01-23: Root cause identified - UILabel was using `text=` parameter with HTML tags instead of `html_text=` parameter. Fixed by changing `text="<b>Filters</b>"` to `html_text="<b>Filters</b>"` on line 85, and similarly for design names on line 328 in `game/ui/screens/design_selector_window.py`.

---

## [BUG-39] - Load Design Screen incorrectly calculates mass
* **Date Solved:** 2026-01-24 05:29
* **Original Issue:** In the Design Workshop, the Load Design Screen does not correctly calculate the mass of the design.
* **Solution Implemented:**
- 2026-01-23: Ticket created from user report.
- 2026-01-23: Root cause identified - `DesignMetadata.from_design_file()` was looking for `mass` at the top level of the JSON, but ship designs store mass inside `expected_stats.mass`. Fixed by checking `expected_stats.mass` first, then falling back to top-level `mass`. File modified: `game/strategy/data/design_metadata.py`.

---

## [BUG-40] - Component Modifier Grid should be persistent panel
* **Date Solved:** 2026-01-24 05:29
* **Original Issue:** In the design workshop the Component Modifier Grid should be a persistent panel, and when there is no component selected, it is fine to say: "no modifier effects to display"
* **Solution Implemented:**
- 2026-01-23: Ticket created
- 2026-01-23: Fixed. Changed `ComponentModifierGridPanel` to be persistent:
  - Removed `self.panel.hide()` on init (line 79-80)
  - Modified `update_component()` to not hide panel when no component selected
  - Modified `draw()` to always draw when panel visible (not just when component exists)
  - The `ModifierImpactGrid` already displays "No modifier effects to display" when empty
  - Files modified: `game/ui/panels/component_modifier_grid_panel.py`
  - Tests pass: `tests/unit/ui/test_modifier_impact_grid.py` (9 passed)

---

## [BUG-41] - Ship Structure section needs wider layout
* **Date Solved:** 2026-01-24 05:29
* **Original Issue:** In the design workshop, the Ship Structure section could be 25% wider, so that the cost doesn't overlap with the other information
* **Solution Implemented:**
- 2026-01-23: Ticket created
- 2026-01-23: Fixed. Made Ship Structure panel 25% wider:
  - Updated `PanelWidths.layer_panel` from 400 to 500
  - Updated `calculate_dynamic_layer_width()` to use 0.375 ratio (was 0.3) with bounds 375-625px (was 300-500px)
  - Files modified: `game/ui/screens/builder_utils.py`
  - Tests pass: builder tests (106 items)

---

## [BUG-43] - Colony view flags have white frame and wrong aspect ratio
* **Date Solved:** 2026-01-24 05:29
* **Original Issue:** In the strategy view the flags on the colony view should not have the white frame, and they appear to be vertically compressed, they should be the same aspect ratio as the original image.
* **Solution Implemented:**
- 2026-01-23: Ticket created
- 2026-01-23: Fixed. Updated colony flag rendering:
  - Removed white frame border (`pygame.draw.rect` call)
  - Changed aspect ratio calculation to preserve original image proportions
  - Files modified: `game/ui/screens/strategy_renderer.py`

---

## [BUG-44] - Fleet Report columns need reorder arrows
* **Date Solved:** 2026-01-24 05:29
* **Original Issue:** In the Fleet Report, the columns should be able to be re-ordered with arrows on either side like the planet list.
* **Solution Implemented:**
- 2026-01-23: Ticket created
- 2026-01-23: Fixed. Added column reorder arrows to Fleet Report:
  - Modified `_rebuild_headers()` to create left/right arrow buttons on each column header
  - Added `_swap_columns()` method to swap column positions
  - Updated `update()` method to handle arrow button clicks
  - Pattern matches planet list window implementation
  - Files modified: `game/ui/screens/fleet_report_window.py`

---

## [BUG-45] - Warp navigation logic issues for non-warp-capable fleets
* **Date Solved:** 2026-01-24 05:29
* **Original Issue:** - A fleet with a warp drive but no battery is correctly prevented from jumping through a warp point, but the navigation still try's to use the warp points, If a fleet is not war capable it should not try to warp, it should just try to travel via regular hex path travel.
* **Solution Implemented:**
- 2026-01-23: Ticket created
- 2026-01-23: Deep Investigation initiated - Agent swarm deployed
- 2026-01-23: Root cause identified - 3 bugs found (missing fleet parameter + missing capability check)
- 2026-01-23: Fixes applied:
  - game_session.py:138 - Added `fleet=fleet` to `find_hybrid_path()` call
  - turn_engine.py:298-303 - Added `can_use_warp()` check before warp execution
  - pathfinding.py:289,334 - Added `fleet=chaser_fleet` to intercept calculations
- 2026-01-23: Diagnostic logging added at key decision points

---

## [BUG-35] - Strategy view smaller planets too compacted in multi-planet sectors
* **Date Solved:** 2026-01-24 07:48
* **Original Issue:** In the strategy view, with multiple planets in a sector, we can slightly increase the angle between the smaller planets to spread them out a little. They are too compacted and there is extra space.
* **Solution Implemented:**
- 2026-01-23: Ticket created.
- 2026-01-23: Fixed. Modified `_draw_system_details()` in `game/ui/screens/strategy_renderer.py` to increase angular spread between smaller planets:
  - 2 planets: 35° apart (was 30°)
  - 3 planets: 40° spread (was asymmetric 15°/0°/-45°)
  - 4 planets: new explicit angles [50°, 20°, -20°, -50°]
  - 5 planets: new explicit angles [55°, 27°, 0°, -27°, -55°]
  - 6+ planets: spread from 60° to -70° (130° arc, was 105°)

  This provides better spacing and uses more of the available hex area.

---
### ❌ Fix Rejected [2026-01-24 10:30]
**Reason:** Planets are still too tight together, try to increase the angle between the smaller planets by about 15%
**New Constraints:** Increase angular spread by approximately 15% from current values
---

- 2026-01-24: Rev 5 fix applied. Increased all angular spreads by 15%:
  - 2 planets: 40° (was 35°)
  - 3 planets: 46° (was 40°)
  - 4 planets: [58°, 23°, -23°, -58°] (was [50°, 20°, -20°, -50°])
  - 5 planets: [63°, 31°, 0°, -31°, -63°] (was [55°, 27°, 0°, -27°, -55°])
  - 6+ planets: 150° arc from 70° to -80° (was 130° arc from 60° to -70°)
  File modified: `game/ui/screens/strategy_renderer.py:356-371`

---

## [BUG-37] - Load Design Screen obsolete filter not working correctly
* **Date Solved:** 2026-01-24 07:48
* **Original Issue:** In the Design Workshop, the Load Design Screen does not appear to let you make ships as obsolete, or filter the obsolete ships. When clicking "filter obsolete", the Select button keeps moving further to the left.
* **Solution Implemented:**
- 2026-01-23: Ticket created from user report.
- 2026-01-23: Fixed Select button drift issue. Root cause: `_rebuild_design_list()` was calculating `row_width` from `list_container.get_container().get_rect().width - 20`, then setting `set_scrollable_area_dimensions(row_width, ...)`. Each refresh would read the previously-shrunk width and subtract 20 again, causing cumulative shrinkage. Fixed by using `main_panel.get_container().get_rect().width - 30` as a stable reference.
- 2026-01-23: Note: "Cannot mark ships obsolete" - the Load Design Screen is a read-only selector window. Marking obsolete would be a feature for the Design Workshop editor. Consider creating separate feature ticket if needed.

---
### ❌ Fix Rejected [2026-01-24 10:35]
**Reason:** Either designs are not being correctly identified as obsolete, or they are not getting set as obsolete, I can't really tell.
The load window in the Design Workshop needs to give the option to make a ship obsolete - this can be a button just to the left of the select button. - when pressed the design needs to be updated as obsolete and the file saved. The window should not close.
There needs to be a visible indicator on the line that indicates if the ship is obsolete, right now nothing indicates this.
**New Constraints:**
- Add "Mark Obsolete" button to the left of the Select button in the Load Design window
- When pressed, update the design as obsolete and save the file (window stays open)
- Add visible indicator on each row showing whether the ship is obsolete
---

- 2026-01-24: Implemented obsolete toggle functionality:
  - Added "[OBS]" visual indicator on left side of row when design is obsolete
  - Added "Obsolete"/"Restore" toggle button to the left of Select button
  - Button calls `design_library.mark_obsolete()` to update and save the design file
  - Window stays open and list refreshes after toggling obsolete status
  File modified: `game/ui/screens/design_selector_window.py:295-399`

---

## [BUG-38] - Load Design Screen should show portrait and top-down views
* **Date Solved:** 2026-01-24 07:48
* **Original Issue:** In the Design Workshop, the Load Design Screen should show a portrait and top down view of the designs in the list.
* **Solution Implemented:**
- 2026-01-23: Ticket created from user report.
- 2026-01-23: Implemented portrait thumbnails in design rows. Added `_load_portrait_thumbnail()` method that loads portrait from `assets/ShipThemes/{theme}/Portraits/{class}_Portrait.jpg` and falls back to a gradient placeholder with class initial. Replaced emoji placeholder with `UIImage` widget displaying the portrait. Files modified: `game/ui/screens/design_selector_window.py`.

---
### ❌ Fix Rejected [2026-01-24 10:40]
**Reason:** There is a nice portrait view but not top down view - the topdown view should be from the Skins directory of the ship's theme directory. Note that the skins may have a large transparent area, they should be sized based on the visible portion of the image, and this should be the same height as the portrait view.
**New Constraints:**
- Add top-down view in addition to portrait view
- Top-down image source: `assets/ShipThemes/{theme}/Skins/` directory
- Size based on visible (non-transparent) portion of the image
- Top-down view height should match portrait view height
---

- 2026-01-24: Implemented top-down view:
  - Added `_load_topdown_thumbnail()` method that loads from `assets/ShipThemes/{theme}/Skins/{class}.png`
  - Added `_get_visible_bounding_box()` helper to find non-transparent area of PNG
  - Top-down image is scaled so visible portion height matches portrait height (50px)
  - Top-down view displays alongside portrait in each design row
  - Handles multiple class name variations (spaces, underscores, case)
  File modified: `game/ui/screens/design_selector_window.py`

---

## [BUG-42] - Design Workshop remnants visible after exit
* **Date Solved:** 2026-01-24 07:48
* **Original Issue:** When I exit the Design Workshop, and the main strategy layer view is visible, there are portions of the Design Workshop that are still visible.
* **Solution Implemented:**
- 2026-01-23: Ticket created
- 2026-01-23: Fixed. Added cleanup method to clear pygame_gui elements on exit:
  - Added `cleanup()` method to `DesignWorkshopGUI` that calls `ui_manager.clear_and_reset()`
  - Updated `on_builder_return()` in `app.py` to call `builder_scene.cleanup()` before state transition
  - Files modified: `game/ui/screens/workshop_screen.py`, `game/app.py`
  - Tests pass: workshop tests (37 items)

---
### ❌ Fix Rejected [2026-01-24 10:50]
**Reason:** There are still Design Workshop Remnants - A simple solution is Blank the screen and re-draw the whole UI when you go back to the strategy layer, this is also a problem with the fleet report, it leaves a lot of remnants behind as well
**New Constraints:**
- Blank the screen and re-draw the whole UI when returning to strategy layer
- This issue also affects the Fleet Report (leaves remnants behind) - same fix needed
---

- 2026-01-24: Fixed by adding full screen fill at start of `StrategyScene.draw()`:
  - Added `screen.fill((10, 10, 20))` as first line of draw method
  - This clears the entire screen before drawing, preventing remnants from any previous screen
  - Fixes both Design Workshop and Fleet Report remnant issues
  File modified: `game/ui/screens/strategy_scene.py:144-147`

---

## [BUG-47] - Component Modifiers Section and Grid Not Acting Appropriately
* **Date Solved:** 2026-01-24 07:48
* **Original Issue:** The Component modifiers section and the component modifier Grid are not acting appropriately.
* **Solution Implemented:**
| Date | Phase | Notes |
|------|-------|-------|
| 2026-01-24 | Ingested | Ticket created from user report |
| 2026-01-24 | Fixed | Root causes identified and fixed |

### Fix Details (2026-01-24)

**Issue 1: Modifier panel shows different modifiers depending on previous selection**
- **Root Cause:** In `ModifierEditorPanel.layout()`, when selecting a new component, the scroll container was killed but `self.modifier_rows` (containing `ModifierControlRow` objects) was not cleared. The row objects persisted with dead UI element references. Since `build_ui()` was only called when the y-position changed, rows at the same position never got their UI rebuilt.
- **Fix:** Modified `_clear_scroll_container()` in `builder_widgets.py` to also call `_clear_all_rows()`. This ensures all modifier rows are rebuilt with fresh UI elements when a new component is selected.
- **File:** `game/ui/panels/builder_widgets.py:155-166`

**Issue 2: Grid not showing all modifier effects (e.g., Size Mount not shown for Bridge)**
- **Root Cause:** `ModifierImpactGrid.update()` filtered stat columns to only show stats that the component's abilities consume. For example, the Bridge might only consume `crew_req`, but Size Mount affects `mass_mult`. Since `mass_mult` wasn't in the Bridge's consumed stats, the column wasn't displayed, making Size Mount's row appear empty.
- **Fix:** Removed the stat filtering so ALL stats affected by any modifier are shown as columns. Changed `self.stat_columns = self._get_affected_stats(summary, component_stats)` to `self.stat_columns = self._get_affected_stats(summary, None)`.
- **File:** `game/ui/panels/modifier_impact_grid.py:105-111`

---

## [BUG-48] - Core Layer Components Display as Blank and Deletion Issues
* **Date Solved:** 2026-01-24 07:48
* **Original Issue:** When I add a second generator to a design and place it in the core level it shows up as a blank space: C:\Developer\StarshipBattles\screenshots\screenshot_20260124_061019_198733_mouse_focus.png then when I delete the 1st generator that I placed in the outer layer, instead the one that was placed in the core is deleted.
* **Solution Implemented:**
| Date | Phase | Notes |
|------|-------|-------|
| 2026-01-24 | Ingested | Ticket created from user report |
| 2026-01-24 | Fixed | Root causes identified and fixed |

### Fix Details (2026-01-24)

**Issue 1: Components showing as blank in Core layer**
- **Root Cause:** In `LayerPanel.rebuild()`, the UI cache key was `("group", group_key)` which didn't include the layer type. When the same component type (e.g., Generator) existed in both CORE and OUTER layers with identical modifiers, they had the same cache key. The second component's UI overwrote the first in the cache, causing the first to display blank or with wrong data.
- **Fix:** Changed the cache key to `("group", l_type, group_key)` to include the layer type, ensuring unique cache entries for each layer.
- **File:** `ui/builder/layer_panel.py:213`

**Issue 2: Deletion targeting wrong component (wrong layer)**
- **Root Cause:** The `LayerComponentItem` only passed `group_key` to the delete handler. The handler then searched ALL layers for a matching component, finding the first match which could be in the wrong layer (typically the last layer searched in backwards iteration).
- **Fix:**
  1. Added `layer_type` parameter to `LayerComponentItem.__init__` and stored it
  2. Changed the delete action payload from `group_key` to `(group_key, layer_type)` tuple
  3. Updated `_handle_remove_group()` in event router to unpack the layer type and only search the target layer
- **Files:**
  - `ui/builder/structure_list_items.py:258,260,419`
  - `game/ui/screens/workshop_event_router.py:190-235`

---

## [BUG-49] - Component Modifier Grid - Hide Irrelevant Columns
* **Date Solved:** 2026-01-24
* **Original Issue:** Component Modifier Grid showed columns for stats that don't apply to the selected component (e.g., strategic movement for a Bridge).
* **Solution Implemented:** Implemented data-driven column filtering using `_get_component_consumed_stats()` and `UNIVERSAL_STATS` constant. Grid now only shows columns for stats the component actually uses.
* **Test Case:** `tests/unit/ui/test_modifier_impact_grid.py`

---

## [BUG-50] - Load Design Window - Right Edge Clipped
* **Date Solved:** 2026-01-24
* **Original Issue:** The right edge of design rows in the Load Design window was clipped by the scrollbar.
* **Solution Implemented:** Changed row_width calculation to use list_container width minus 25px (for scrollbar + margins) instead of main_panel width.
* **Test Case:** Design selector window tests

---

## [BUG-52] - Design Workshop - Rightmost Panel Should Extend Full Height
* **Date Solved:** 2026-01-24
* **Original Issue:** The rightmost panel in the Design Workshop had unused space at the bottom right; Requirements and Recommendations sections were smaller than needed.
* **Solution Implemented:** Extended right_panel height to `self.height - self.bottom_bar_height` (full height minus bottom bar only).
* **Test Case:** Workshop screen tests

---

## [BUG-53] - Load Design Panel - Overwritten by Component Modifier Grid
* **Date Solved:** 2026-01-24
* **Original Issue:** When the Load Design panel opened, the Component Modifier Grid drew over portions of it.
* **Solution Implemented:** Added check in `draw()` to detect visible UIWindow instances; skips drawing `component_modifier_grid_panel` and `detail_panel` when modal windows are open.
* **Test Case:** Workshop screen tests

---

## [BUG-54] - Planet Selection Hitbox Mismatch After Angle Increase
* **Date Solved:** 2026-01-24
* **Original Issue:** After increasing planet spread angles (BUG-35 Rev 5), clicking on smaller planets in multi-planet sectors used old positions for hit-testing.
* **Solution Implemented:** Synchronized angle values in `strategy_input_handler.py` to match updated `strategy_renderer.py` Rev 5 values for all planet count cases.
* **Test Case:** Strategy input handler tests

---

## [BUG-55] - Build Queue - No Selection Indication
* **Date Solved:** 2026-01-24
* **Original Issue:** No visual indication of which design was selected in the build queue; "Remove Selected" button didn't work.
* **Solution Implemented:** Added `selected_queue_index` state, drag threshold (10px) to distinguish click-select from drag-reorder, blue highlight border for selected items, and "Remove Selected" button handler.
* **Test Case:** `tests/ui/test_build_queue_drag_drop.py`

---

## [BUG-56] - New Game Setup - Star System Count Selector
* **Date Solved:** 2026-02-07
* **Original Issue:** No UI control existed for selecting star system count in new game setup.
* **Solution Implemented:** Added `UIHorizontalSlider` (range 25-150, default 50, click_increment=5) with value label. Slider value flows through `build_game_config()` to `GameConfig.system_count`.
* **Test Case:** New game setup tests (13 passed)

---

## [BUG-57] - Race Setup Window Too Small
* **Date Solved:** 2026-02-07
* **Original Issue:** Race Setup window opened at 1400x900 from New Game Setup, while main menu version used 1800x1200.
* **Solution Implemented:** Changed `setup_width` from 1400 to 1800 and `setup_height` from 900 to 1200 in `new_game_setup_screen.py`.
* **Test Case:** UI sizing change only; no test changes needed

---

## [BUG-58] - Race Setup - Racial Points Not Displayed in Environment Window
* **Date Solved:** 2026-02-07
* **Original Issue:** Racial points budget was only displayed in Aptitudes tab; Environment tab had no points indicator.
* **Solution Implemented:** Added `points_label` UILabel and `_update_points_display()` method to `race_environment_panel.py`. Shows remaining points and environment cost, refreshes on slider changes.
* **Test Case:** `tests/unit/ui/test_race_environment_panel.py` (29 passed)

---

## [BUG-59] - Game Setup + Race Setup Visual Theme Mismatch
* **Date Solved:** 2026-02-07
* **Original Issue:** Menu scene used pygame_gui default styling while strategy layer and design workshop used `builder_theme.json`.
* **Solution Implemented:** Changed `MenuScene` UIManager creation to load `builder_theme.json` from `Paths.DATA_DIR`, matching strategy and workshop screens.
* **Test Case:** All 6519 tests pass

---

## [BUG-60] - Rename All "Race" References to "Species" (UI Text)
* **Date Solved:** 2026-02-07
* **Original Issue:** All user-facing UI text said "Race" instead of "Species".
* **Solution Implemented:** Updated all user-visible UI strings across 6 files: race_setup_screen, race_browser_dialog, race_summary_panel, race_identity_panel, new_game_setup_screen, race_validator. Code-level renames deferred to separate project.
* **Test Case:** All 6519 tests pass

---

## [BUG-61] - Species Setup - Aptitude Range 1-100 with Exponential Cost
* **Date Solved:** 2026-02-07
* **Original Issue:** Aptitudes used 1-10 scale with base 5 and linear cost. Needed 1-100 with base 50 and exponential cost above 50.
* **Solution Implemented:** Expanded scale to 1-100, base 50. Added `_single_aptitude_cost()` with exponential formula above 50: `max(1, int(2^((v-50)/10)))`. Updated race_config, race_point_budget, race_aptitudes_panel, population_engine, and race_validator.
* **Test Case:** `test_race_config.py`, `test_race_point_budget.py`, `test_population_engine.py`, `test_race_aptitudes_panel.py`, `test_race_validator.py`

---

## [BUG-62] - Homeworld Type Should Set Default Environmental Preferences
* **Date Solved:** 2026-02-07
* **Original Issue:** Expected homeworld type selection to auto-populate environmental preferences.
* **Solution Implemented:** **Already implemented.** Dropdown fires `apply_homeworld_preset()` which loads from `homeworld_presets.json` and updates all sliders. No changes needed.
* **Test Case:** Race environment panel tests

---

## [BUG-64] - Design Workshop - Component Disappears in Multi-Layer Placement
* **Date Solved:** 2026-02-07
* **Original Issue:** Placing the same component type in multiple layers caused one to disappear (blank space) because the UI cache key didn't include layer type.
* **Solution Implemented:** Changed cache key from `("group", group_key)` to `("group", l_type, group_key)` in `layer_panel.py` to ensure unique UI entries per layer.
* **Test Case:** `tests/unit/ui/test_structure_visibility.py` - `test_same_component_in_multiple_layers_shows_in_both`

---

## [BUG-65] - Design Workshop - Modifiers Should Auto-Select Applicable Ones
* **Date Solved:** 2026-02-07
* **Original Issue:** Some applicable modifiers (e.g., Hardened Mount) weren't auto-selected for components due to hardcoded incomplete lists in `get_mandatory_modifiers()`.
* **Solution Implemented:** Changed both `ModifierLogic` and `ModifierService` `get_mandatory_modifiers()` to dynamically return ALL allowed modifiers. Toggle buttons disabled; users adjust values only.
* **Test Case:** All 360 modifier-specific tests pass

---

## [BUG-66] - Design Workshop - Hide Vehicle Theme Selector in Strategy Mode
* **Date Solved:** 2026-02-07
* **Original Issue:** Theme dropdown was visible in the Design Workshop when playing the strategy layer, but selecting themes had no effect on ship images.
* **Solution Implemented:** Added `hide_theme_selector` parameter to `BuilderRightPanel`. When workshop is in integrated mode (strategy layer), theme dropdown is not created; theme is locked to the empire's theme.
* **Test Case:** All 241 workshop/builder tests pass

---

## [BUG-67] - Strategy Layer - Add "Build Queues" Button to Top Bar
* **Date Solved:** 2026-02-07
* **Original Issue:** No top bar button existed for viewing all active build queues from the strategy layer.
* **Solution Implemented:** Added `btn_build_queues` button to top bar in `strategy_ui.py`. Created new `BuildQueueListWindow` that lists all active build queues across planets and fleets.
* **Test Case:** All 1113 UI + strategy tests pass

---

## [BUG-71] - Design Workshop - +/- Buttons Affect Wrong Layer for Duplicate Components
* **Date Solved:** 2026-02-08
* **Original Issue:** +/- buttons on components present in multiple layers targeted the wrong layer because no layer context was passed through the event chain.
* **Solution Implemented:** Threaded `layer_type` through `structure_list_items.py`, `layer_panel.py`, `workshop_event_router.py`, and legacy `main.py`. Event handlers now search only the targeted layer.
* **Test Case:** `tests/unit/builder/test_layer_targeted_actions.py` (8 new tests)

---

## [BUG-72] - Leader Needs a Name in Species Setup
* **Date Solved:** 2026-02-08
* **Original Issue:** Species Setup lacked a text input field for the leader's name.
* **Solution Implemented:** Added `leader_name: str` field to `RaceConfig` with serialization support. Added `leader_name_input` (UITextEntryLine) to `race_identity_panel.py` in the Government section.
* **Test Case:** `tests/unit/strategy/data/test_race_config.py`, `tests/unit/ui/panels/test_race_identity_panel.py`

---

## [BUG-74] - Normal New Games Should Have Homeworld Complexes Pre-Built
* **Date Solved:** 2026-02-08
* **Original Issue:** Normal new games created empty homeworlds while quickstart games had 7 pre-built facilities (shipyard, resource harvesters, resupply depot).
* **Solution Implemented:** Added `QuickstartBuilder.copy_quickstart_designs()` and `spawn_initial_complexes()` calls to `_on_new_game_start()` in `app.py`, matching the quickstart code path.
* **Test Case:** Strategy and quickstart tests

---

## [BUG-75] - Planet Details Panel Dimensions Mismatch
* **Date Solved:** 2026-02-08
* **Original Issue:** Planet details panel in the planets list window was 600px wide while the strategy layer version was 580px.
* **Solution Implemented:** Changed `detail_panel_width` from 600 to 580 in `planet_list_window.py` to match strategy layer.
* **Test Case:** Planet list window tests

---

## [BUG-76] - Turn Log Does Not Show at Start of Each Strategy Turn
* **Date Solved:** 2026-02-08
* **Original Issue:** Off-by-one bug: `process_turn()` logs events at turn N then increments to N+1. `get_turn_events()` queried N+1, returning empty results.
* **Solution Implemented:** Captured turn number before calling `process_turn()` and passed it explicitly to `get_turn_events(turn=processed_turn)` in `strategy_screen.py`.
* **Test Case:** Strategy screen tests

---

## [BUG-77] - Ships/Fleets Missing After Save and Load
* **Date Solved:** 2026-02-08
* **Original Issue:** All ships/fleets disappeared after save and load. `Fleet.to_dict()` could not serialize `HexCoord` locations, resulting in `null` in save files.
* **Solution Implemented:** Updated `Fleet.to_dict()` to check `isinstance(HexCoord)` and serialize as `{'q': q, 'r': r}`. Updated `from_dict()` for the new dict format with backward compatibility. Same fix applied to path serialization.
* **Test Case:** `tests/unit/strategy/fleet/test_serialization.py` (9 tests), 46 save/load integration tests

---

## [BUG-78] - Planet Production Values Display as 0; Icons Not Centered
* **Date Solved:** 2026-02-10
* **Original Issue:** Production values showed 0 because `compute_planet_production()` only checked inline abilities, not registry lookups. Icons were left-aligned instead of centered.
* **Solution Implemented:** Added `_get_harvester_info()` with registry lookup fallback in `strategy_detail_formatter.py`. Fixed icon centering to `col_x + (col_w - 24) // 2` in `planet_report_panel.py`.
* **Test Case:** `tests/unit/ui/screens/test_planet_production_display.py` (5 new tests)

---

## [BUG-80] - Build Yards List - Names/Properties Should Be on 1 Line
* **Date Solved:** 2026-02-10
* **Original Issue:** Yard entries in the Build Yards list used `\n` to split name and properties onto two lines, wasting space.
* **Solution Implemented:** Changed format to single-line `"{name} ({count} items, {rate}/turn)"` in `build_queue_selector.py`. Reduced `row_height` from 55 to 30.
* **Test Case:** 169 build queue UI tests pass

---

## [BUG-81] - Build Queue - Item Column Too Narrow, Properties Overflow
* **Date Solved:** 2026-02-10
* **Original Issue:** Build queue Item column was 150px wide with 12-character name truncation. Properties overflowed onto separate lines.
* **Solution Implemented:** Widened Item column from 150px to 450px (3x). Combined design name and type on single line. Shifted Turns and resource columns right. Removed name truncation.
* **Test Case:** 169 build queue tests, 7659 full suite pass

---

## [BUG-79] - Ships with Multiple Fleet Space Yard Components Only Get 1 Build Yard Entry
* **Date Solved:** 2026-02-11
* **Original Issue:** Ships with multiple Fleet Space Yard components only generated 1 Build Yard entry in the sector build queue screen instead of one per yard component.
* **Solution Implemented:** Added `space_shipyard_count` property to `fleet_capability_calculator.py` and `fleet.py` to count all yard components. Updated `build_queue_source.py` to loop `range(yard_count)` instead of boolean check, creating one entry per yard with indexed queue IDs (`fleet_{id}_yard_{n}`).
* **Test Case:** `tests/unit/strategy/fleet/test_space_yard.py::TestFleetSpaceShipyardCount` (5 tests)
* **Notes:** 61/61 yard + build queue tests pass.

---

## [BUG-46] - Fleet Report Ship Top-Down Image Too Small
* **Date Solved:** 2026-03-14
* **Original Issue:** In the fleet report, the top-down ship image was too small compared to the portrait.
* **Solution Implemented:** Added `max_width` parameter to `scale_image_by_visible_portion()` in `pygame_utils.py`. Scales visible content to fit within both width and height bounds while preserving aspect ratio. `fleet_data_source.py` passes `max_width=56` for topdown images.
* **Test Case:** `tests/unit/ui/test_utils.py` — 6 scale_image_by_visible_portion tests (2 existing + 4 new)

---

## [BUG-63] - Starting Planet Should Match Species Ideal Conditions
* **Date Solved:** 2026-03-14
* **Original Issue:** The starting planet for a player did not have the same conditions as the ideal conditions for that species.
* **Solution Implemented:** `_adjust_homeworld_to_race()` in `game_initializer.py` adjusts planet type, gravity, temperature, water, atmosphere, and pressure to match the race's ideal conditions. Called during empire setup when `race_config` is present.
* **Test Case:** Integration tests covering empire creation and colony setup verify initial conditions.

---

## [BUG-69] - Strategy View Scroll Wheel Zoom Locks Up
* **Date Solved:** 2026-03-14
* **Original Issue:** Scroll wheel zoom stopped working after opening and closing fleet orders or fleet report windows.
* **Solution Implemented:** Fixed `strategy_ui.py` — the `UI_WINDOW_CLOSE` event handler was incorrectly nested inside the `UI_BUTTON_PRESSED` block, so window references were never cleared on close. Moved to a separate top-level handler and added `transfer_dialog` cleanup.
* **Test Case:** 1570 strategy tests pass.

---

## [BUG-82] - Design Workshop - Load Design window is very slow to open
* **Date Solved:** 2026-03-14
* **Original Issue:** The Load Design window in the Design Workshop took a long time to open due to pixel-by-pixel bounding box scans and no thumbnail caching.
* **Solution Implemented:** Replaced `_get_visible_bounding_box` with pygame's native `surface.get_bounding_rect(min_alpha=10)` and added module-level thumbnail caches (`_portrait_cache`, `_topdown_cache`) keyed by `(design_id, size)` in `game/ui/screens/design_image_helper.py`.
* **Test Case:** `tests/unit/ui/screens/test_design_image_helper.py` — 49 design-related tests pass.

---

## [BUG-73] - Species Setup - Homeworld type selection still reports "Custom"
* **Date Solved:** 2026-03-14
* **Original Issue:** Selecting a homeworld type in species setup still showed "Custom" in the summary because display names weren't converted to preset IDs.
* **Solution Implemented:** Convert display name to preset ID via `get_preset_id_from_name()` in dropdown handler; convert back to display name in summary panel.
* **Test Case:** `game/ui/panels/race_environment_panel.py`, `game/ui/panels/race_summary_panel.py`

---

## [BUG-81] - Species Setup - Load Saved Species does nothing
* **Date Solved:** 2026-03-14
* **Original Issue:** Loading a saved species opened the dialog but clicking Load did nothing — sub-panels held stale references to the old RaceConfig object.
* **Solution Implemented:** Added loop in `_populate_ui_from_config` to update `panel.race_config` on all 8 panels before calling `set_from_config()`.
* **Test Case:** `tests/unit/ui/screens/test_race_setup_screen.py::TestRaceSetupLoadSpecies`

---

## [BUG-83] - Fleet Report - Missing special capability columns and filters
* **Date Solved:** 2026-03-14
* **Original Issue:** Fleet Report lacked columns for DestroyPlanet, OpenWarpPoint, CloseWarpPoint, DestroyStar, and CreateSphereWorld capabilities.
* **Solution Implemented:** Added 5 special capability columns with filtering and sorting across column_manager, view model, filters, and window files.
* **Test Case:** 13 new tests across `TestSpecialCapabilityColumns`, `TestSpecialCapabilityFilter`, `TestSpecialCapabilitySort`, `TestViewModelSpecialFilters`.

---

## [BUG-84] - Warp Gate Close and Planet Destroyer orders not registering
* **Date Solved:** 2026-03-14
* **Original Issue:** Superweapon orders (close warp, destroy planet) silently failed when fleet wasn't at target location. Fleet was also destroyed after executing superweapon.
* **Solution Implemented:** Added `skip_location_check` parameter to superweapon validators (matching COLONIZE/TRANSFER pattern). Added `consume_ship` parameter to `_finalize_superweapon()` — only stellerate_star and self_destruct consume. Added sector-level validation at execution time with dict target format.
* **Test Case:** Multiple new tests including `test_skip_location_check_allows_remote_queueing`, `test_ship_not_consumed`, `test_rejects_wrong_sector`. Full suite: 13,178 passed.

---

## [BUG-85] - New game colonies report 0 population instead of max
* **Date Solved:** 2026-03-14
* **Original Issue:** Colonies at game start reported 0 population because `PlayerConfig` was missing `race_config` and initial population was hardcoded to 10,000.
* **Solution Implemented:** Added `race_config=race` to PlayerConfig constructor. Changed initial population from hardcoded 10,000 to `home_planet.max_population`.
* **Test Case:** `tests/unit/ui/test_new_game_setup.py::TestNewGameSetupRaceConfig`, `tests/unit/strategy/engine/test_population_seeding.py`

---

## [BUG-86] - Build Queue planet details missing resource production numbers
* **Date Solved:** 2026-03-14
* **Original Issue:** Build queue and planets list panels showed zero production because `production_rates` parameter wasn't passed to `PlanetReportPanel`.
* **Solution Implemented:** Extracted shared `compute_planet_production()` to `planet_report_panel` module. Updated build queue and planets list to pass production_rates.
* **Test Case:** `test_compute_planet_production.py` (5 tests)

---

## [BUG-87] - Empire Treasury window missing colony resource production totals
* **Date Solved:** 2026-03-14
* **Original Issue:** Economy calculator only checked inline abilities on facility components, missing registry-based components (e.g., `metal_harvester`).
* **Solution Implemented:** Added registry parameter to `EmpireEconomyCalculator` with fallback lookup matching `HarvestingEngine` pattern.
* **Test Case:** `test_registry_fallback_for_colony_production`, `test_registry_fallback_with_no_registries_returns_zero`

---

## [BUG-88] - Empire Population tab blank - missing species information cards
* **Date Solved:** 2026-03-14
* **Original Issue:** Population tab showed "No species data available" because `race_config` was None for empires created without explicit race setup.
* **Solution Implemented:** In `_create_empires()`, create a default `RaceConfig` when `player_cfg.race_config` is None, using player name and theme.
* **Test Case:** `test_empire_always_has_race_config`, `test_empire_preserves_explicit_race_config`

---

## [BUG-89] - Workshop Screen Crash on Design Button Click
* **Date Solved:** 2026-03-14
* **Original Issue:** `AttributeError: 'ModifierEditorPanel' object has no attribute 'update'` — missing `update(dt)` method on `ModifierEditorPanel`.
* **Solution Implemented:** Added no-op `update(self, dt)` method to `ModifierEditorPanel` in `builder_widgets.py`.
* **Test Case:** `tests/unit/ui/panels/test_modifier_editor_panel.py` (3 tests)

---

## [BUG-90] - Incorrect atmosphere coloring in planet details box
* **Date Solved:** 2026-03-14
* **Original Issue:** Atmosphere graph showed uniform colors because homeworld atmospheres used full gas names ("Oxygen") but UI mapped by chemical formulas ("O2").
* **Solution Implemented:** Added `GAS_NAME_TO_FORMULA`/`GAS_FORMULA_TO_NAME` mappings. Translated gas names to formulas in `game_initializer.py` and `superweapon_order_processor.py`. Reverse-translated in `habitability.py`.
* **Test Case:** `test_adjust_homeworld_translates_gas_names_to_formulas`, `test_formula_keys_match_display_name_preferences`

---

## [BUG-91] - Missing planet portrait in build yard UI
* **Date Solved:** 2026-03-14
* **Original Issue:** Build queue screen received `portrait_surface` but never forwarded it to `BuildQueuePanelFactory`, resulting in blank portrait.
* **Solution Implemented:** Added `portrait_surface` parameter to factory constructor and forwarded it from `BuildQueueScreen`.
* **Test Case:** `tests/unit/ui/screens/test_build_queue_screen.py::test_portrait_surface_passed_to_panel_factory`

---

## [BUG-92] - New Game Setup fails to populate loaded species data
* **Date Solved:** 2026-03-14
* **Original Issue:** Clicking "Setup Species" after loading a saved species opened a blank form because `race_to_edit` wasn't passed to `RaceSetupScreen`.
* **Solution Implemented:** Added `race_to_edit=self.player_races[player_index]` to `RaceSetupScreen()` constructor call.
* **Test Case:** `tests/unit/ui/test_new_game_setup.py::test_setup_race_passes_loaded_race`

---

## [BUG-93] - Fleet move targeting state cannot be completed or canceled
* **Date Solved:** 2026-03-14
* **Original Issue:** Failed move clicks left the player stuck in MOVE targeting mode because error results didn't reset `input_mode`.
* **Solution Implemented:** Added `else` branch in `_handle_move_mode_click()` that resets `input_mode` to `'SELECT'` on error/None results.
* **Test Case:** `tests/unit/ui/screens/test_strategy_input_handler_core.py` (3 new tests)

---

## [BUG-94] - Star visual radius too small relative to hex grid
* **Date Solved:** 2026-03-14
* **Original Issue:** Star rendering formula used raw `hex_size` instead of accounting for hex geometry. Non-linear scaling needed for different star sizes.
* **Solution Implemented:** Replaced linear formula with non-linear power curve `2 * hex_spacing * (radius_hexes / 2) ^ 1.2`. Extracted `_hex_radius_to_screen()` helper used by both star and Dyson sphere rendering.
* **Test Case:** `tests/unit/ui/screens/test_strategy_renderer.py` — `test_star_radius_accounts_for_hex_geometry`, `test_star_radius_nonlinear_scaling`

---

## [BUG-95] - Load Species dialog — hover/click only registers in row margins
* **Date Solved:** 2026-03-14
* **Original Issue:** Species row overlay elements (portrait, flag, label) were siblings of the button, intercepting mouse events due to z-order.
* **Solution Implemented:** Restructured to single UIButton per row with composite surface as foreground image via `button.normal_images`. Eliminated z-order conflicts.
* **Test Case:** `tests/unit/ui/test_race_browser_dialog.py` (17 tests)

---

## [BUG-70] - Colonize order should load population before moving
* **Date Solved:** 2026-03-14
* **Original Issue:** Colonize command did not insert a TRANSFER (load population) order before the MOVE order, so colony ships arrived at destinations with empty cargo.
* **Solution Implemented:** Reworked LOAD_POPULATION as a generic queued order with no `planet_id`. Colony is resolved dynamically at execution time from the fleet's hex. Command handlers always insert LOAD_POPULATION before MOVE/COLONIZE.
* **Test Case:** `tests/unit/strategy/test_command_handlers.py` — colonize command handler tests
* **Notes:** Colony lookup at command time was wrong approach; execution-time resolution is correct because fleet may not be at a colony when command is issued.

---

## [BUG-97] - Crash when clicking confirmation dialog to clear fleet orders
* **Date Solved:** 2026-03-14
* **Original Issue:** `StrategyWindowManager` crashed with `AttributeError: '_pending_confirmation_dialog'` because the attribute was only set inside `show_confirmation_dialog()` but never initialized in `__init__()`.
* **Solution Implemented:** Added initialization of `_pending_confirmation_dialog` and `_pending_confirmation_callback` to `None` in `StrategyWindowManager.__init__()`.
* **Test Case:** `tests/unit/ui/screens/test_strategy_window_manager.py` — `test_init_confirmation_dialog_attributes`, `test_process_confirmation_event_no_dialog_shown`
* **Notes:** None.

---

## [BUG-96] - Build queue shows total cost instead of per-turn resource usage
* **Date Solved:** 2026-03-14
* **Original Issue:** Build queue resource columns showed total cost divided by turns_remaining, producing inflated values when turns < 1.0. Initial fix corrected turns_remaining pre-calculation but exposed the display formula bug.
* **Solution Implemented:** Superseded by prospective project `build_queue_configurable_columns.md` — the entire build queue will be reworked to use the shared configurable column system with proper per-turn spend and total remaining columns.
* **Test Case:** Will be covered by the project's test suite.
* **Notes:** Deep investigation fix changed display to show remaining cost. Full rework planned as a project.

---

## [BUG-68] - Fleet Report - Ship Selection and Ship Report Panel
* **Date Solved:** 2026-03-22
* **Original Issue:** In the Fleet Report, clicking on a ship row did not select it and the right-hand detail panel did not display ship information. Root cause: `process_event()` used `MOUSEBUTTONDOWN` which was consumed by child `UIPanel` elements before reaching `FleetReportWindow`.
* **Solution Implemented:** Changed event handling from `MOUSEBUTTONDOWN` to `MOUSEBUTTONUP` (matching working patterns in `PlanetListWindow` and `EmpireBuildQueueWindow`). Replaced `DesignReportPanel` with `ShipDetailPanel`, wired callbacks, and forwarded events to the detail panel.
* **Test Case:** `tests/unit/ui/screens/test_fleet_report_window.py` — 56 tests (37 main + 19 multi-select)
* **Notes:** The "Remove from Fleet" button issue was split into a separate ticket (BUG-99). Ship selection and detail panel display are confirmed working.

---
