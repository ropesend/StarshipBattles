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
