# Completed Features Archive

**APPEND ONLY - DO NOT DELETE ENTRIES**

This file serves as the permanent index of all completed features with implementation summaries.

**Entry Format:**
```markdown
## [FEAT-ID] - [Feature Title]
* **Date Completed:** YYYY-MM-DD HH:MM
* **Original Request:** [Summary of what was requested]
* **Implementation Summary:** [Technical details of what was built]
* **Test Case:** [Reference to the test file that covers this]
* **Notes:** [Any future considerations, warnings for refactors]
---
```

---

<!-- New entries should be appended below this line -->

## [FEAT-01] - Pre-populate Save Game Name
* **Date Completed:** 2026-03-14
* **Original Request:** Auto-populate the save name field with "save game" plus a timestamp for new games.
* **Implementation Summary:** Added `generate_default_save_name()` static method to `NewGameSetupScreen` returning `"save game YYYY-MM-DD HHMM"` format. Called `set_text()` on the input after creation.
* **Test Case:** `tests/unit/ui/test_new_game_setup.py::TestNewGameSetupDefaultSaveName`
* **Notes:** Timestamp uses `HHMM` format (no colon) because colons are invalid filesystem characters.
---

## [FEAT-02] - Add "Generate Random" Buttons to Species Setup
* **Date Completed:** 2026-03-14
* **Original Request:** Add "Generate Random" buttons to Identity, Visual, and Ships tabs in Species Setup to randomize all fields with thematically appropriate data.
* **Implementation Summary:** Created `RaceRandomizer` service class with portrait-aware name generation. Added `race_names.json` data file with entries for all 14 portraits. Single button in navigation area dispatches by current tab.
* **Test Case:** `tests/unit/strategy/test_race_randomizer.py` (23 tests)
* **Notes:** Portrait-aware name generation pulls from portrait-specific pools when a portrait is selected.
---

## [FEAT-03] - Randomize All Properties in Identity Setup
* **Date Completed:** 2026-03-14
* **Original Request:** Clicking "Generate random" should fully randomize all identity dropdown fields (physical type, government type, organization, leader title, society type).
* **Implementation Summary:** Fixed dropdown visual update issue — replaced `_set_dropdown_value()` with `_recreate_dropdown()` in `RaceIdentityPanel` using kill-and-recreate pattern (matching `transfer_dialog.py`).
* **Test Case:** `tests/unit/ui/panels/test_race_identity_panel.py::TestSetFromConfig`
* **Notes:** pygame_gui `UIDropDownMenu` has no public API to change displayed selection after creation; must kill and recreate.
---

## [FEAT-04] - Event Log 'Go To Location' Navigation
* **Date Completed:** 2026-03-14
* **Original Request:** Add clickable/double-click navigation to event log entries that moves the camera to the event's location on the map, with a Location column showing where each event occurred.
* **Implementation Summary:** Added `location_hex` and `location_name` to all `log_event()` calls across production, combat, colonization, and superweapon engines. Added Location column to event log via `EVENT_LOG_COLUMNS`. Implemented double-click detection in `EventLogWindow` with navigate callback that closes the log and centers camera via `center_on_hex()`.
* **Test Case:** `tests/unit/ui/screens/test_event_log_data_source.py` (5 tests), `tests/unit/ui/screens/test_event_log_window.py` (5 tests), `tests/unit/ui/screens/test_camera_navigator.py` (3 tests)
* **Notes:** None.
---

## [FEAT-05] - Save/Update Species Workflow Dialog
* **Date Completed:** 2026-03-14
* **Original Request:** When modifying and saving an existing species, prompt a dialog offering to overwrite the old species or save as a new one.
* **Implementation Summary:** Added save/update dialog to `RaceSetupScreen._on_save()` that detects `is_editing` + existing `race_id`. Dialog offers Overwrite (preserves race_id), Save as New (clears race_id), or Cancel.
* **Test Case:** `tests/unit/ui/screens/test_race_setup_screen.py::TestSaveUpdateDialog` (5 tests)
* **Notes:** None.
---

## [FEAT-08] - Fleet Join Order — Target Selection Dialog and Fleet ID Display
* **Date Completed:** 2026-03-23
* **Original Request:** When pressing 'J' to join a fleet and clicking a hex with multiple fleets, show a selection dialog. Also display target fleet ID in the orders window.
* **Implementation Summary:** Created `FleetSelectionWindow` with UISelectionList for multi-fleet target picking. Modified `handle_join_designation()` to filter valid targets and return choice dict for multiple fleets. Added dialog integration via `strategy_window_manager.py` and `strategy_ui.py`. Orders window already displayed fleet IDs correctly.
* **Test Case:** `tests/integration/ui/test_fleet_ops_facade.py` (including `test_join_returns_choice_for_multiple_valid_targets`)
* **Notes:** Minor display issue with fleet info panel order formatting filed separately as BUG-101.
---

## [FEAT-07] - Add 'W' Hotkey for Explicit Warp Orders
* **Date Completed:** 2026-03-24
* **Original Request:** Add a 'W' hotkey on the strategy map to activate warp order mode, allowing click-to-warp on warp points for the selected fleet.
* **Implementation Summary:** Added `FLEET_WARP` to `InputAction` enum mapped to 'W', added `WARP_TARGET` input mode in `strategy_fleet_command_router.py`, handled click dispatch in `strategy_click_dispatcher.py` to find warp points and issue `IssueWarpCommand`, gated on fleet warp capability.
* **Test Case:** `tests/integration/ui/test_fleet_ops_facade.py`
* **Notes:** Backend infrastructure (OrderType.WARP, IssueWarpCommand, WarpCommandHandler) already existed.
---

## [FEAT-09] - Log Resource Depletion Events When Production Is Paused
* **Date Completed:** 2026-03-24
* **Original Request:** Log structured events when production pauses due to insufficient resources, including which resource was limiting, amounts available/needed, and which build yards were affected.
* **Implementation Summary:** Added new EventType for resource shortage in `event_types.py`. Added `log_event()` call in `ProductionEngine._process_queue_tick_dynamic()` at the affordability check failure point with limiting resource details.
* **Test Case:** `tests/unit/strategy/events/test_event_types.py`
* **Notes:** None.
---

## [FEAT-06] - Populate Treasury Construction Queue Expenses (Split by Ships and Complexes)
* **Date Completed:** 2026-03-24
* **Original Request:** Replace the zero-value "Construction Queues" line in the Treasury view with two separate expense lines for ships and complexes, showing actual next-turn resource expenditures.
* **Implementation Summary:** Implemented queue-walking distribution logic in `EmpireEconomyCalculator` to iterate construction queues, classify items by type, and sum resource expenditures into ship vs complex categories. Depends on the queue distribution logic from BUG-98.
* **Test Case:** `tests/unit/strategy/engine/test_production_refactor.py`
* **Notes:** Depends on BUG-98's `calculate_queue_turn_spend()` for accurate per-item distribution.
---

## [FEAT-10] - Add "Fleet Operations" filter tab to Event Log window
* **Date Completed:** 2026-03-24
* **Confirmed in:** QA Session 20260428_052952
* **Original Request:** Add "Fleet Operations" filter tab to Event Log window so fleet events can be filtered independently.
* **Implementation Summary:** Pure UI change — added "Fleet Ops" filter button in `event_log_window.py:_create_filter_buttons()` and `"fleet_operations": "[FleetOps]"` icon in `event_log_data_source.py:CATEGORY_ICONS`. Backend (EventCategory.FLEET_OPERATIONS) was already complete.
* **Test Case:** Event log tests across `event_log_window` and `event_log_data_source` (5 new test cases; 111/111 pass)
---

## [FEAT-11] - Data-Driven Planet Resource Generation with Mass Scaling
* **Date Completed:** 2026-03-27
* **Confirmed in:** QA Session 20260428_052952
* **Original Request:** Drive planet resource quantity/quality from `astrophysics.json`, scale with mass (Earth-mass baseline ~10M), and support planet-type affinity modifiers.
* **Implementation Summary:** Added `resource_generation` section to `data/astrophysics.json` (mass scaling, quantity/quality params, 11 planet-type affinity entries). Created `ResourceGenerationConfig` (`@lru_cache` singleton mirroring `ClassificationConfig`). Updated `AstrophysicsLoader` schema. Refactored `PlanetGenerator._generate_resources(mass, planet_type)` — all constants externalized, mass-proportional quantity calibrated to 10M Earth-mass baseline, planet-type affinities applied, minimum floors enforced.
* **Test Case:** `test_resource_generation_config.py` (9 new) + `test_planet_gen.py` (12 updated/new tests). Full suite 13,866 passed.
---

## [FEAT-12] - Race Setup Randomization — Environment, Aptitudes, and Master "Randomize All"
* **Date Completed:** 2026-04-26
* **Confirmed in:** QA Session 20260428_052952 (depends on BUG-118 fix)
* **Original Request:** Add Generate-Random buttons to Environment + Aptitudes tabs and a master "Randomize All" button on the Summary tab; respect 100-point budget.
* **Implementation Summary:** RNG retrofit on existing 4 `RaceRandomizer` methods plus 3 new methods (`randomize_aptitudes`, `randomize_environment`, `randomize_all`) — all accept optional `rng: random.Random` per `docs/02_PATTERNS.md` §18. Master `randomize_all` apportions a random `[0.3, 0.7]` fraction of the residual budget to aptitudes and the remainder to env. Environment randomizer picks a random homeworld preset, applies it via `apply_preset_to_config`, then jitters per-factor. Master button widget added to `RaceSummaryPanel`. New pattern #27 "Budget-Aware Randomization" added to `docs/02_PATTERNS.md`.
* **Test Case:** 28 new tests in `test_race_randomizer.py`, 14 in `test_race_setup_screen.py`, 3 in `test_race_summary_panel.py` (122 total in affected suites).
---

## [FEAT-14] - Race Setup Summary tab — show all environmental factors and aptitudes
* **Date Completed:** 2026-04-27
* **Confirmed in:** QA Session 20260428_052952
* **Original Request:** Summary tab should show every environmental factor in `FACTOR_REGISTRY` and all 7 aptitudes, driven by the registry so adding a new factor surfaces a row automatically.
* **Implementation Summary:** Replaced the static 4-factor block in `RaceSummaryPanel._create_column3_content` with a `UIScrollingContainer` rebuilt from `iter_scalar_factors()` + filtered `iter_gas_factors()` + 7 aptitudes. Setpoint ± tolerance values are formatted via `PreferenceRow.format_value` (the canonical PROJ-293 display contract — no re-implementation). Deleted 5 per-factor formatters and 1 dead `_format_atmosphere_summary` method.
* **Test Case:** `TestFeat14RegistryDrivenSummary` (6 acceptance tests including a monkeypatched synthetic factor proving registry-add-only acceptance). 6657/6657 in scope; 15726/15726 full sharded.
---

## [FEAT-15] - Per-planet probability roll for intrinsic abilities
* **Date Completed:** 2026-04-27
* **Confirmed in:** QA Session 20260428_052952
* **Original Request:** Make planet intrinsic abilities (ShieldModifier, ThrustModifier, etc.) rare — per-planet probability roll instead of deterministic-by-type assignment.
* **Implementation Summary:** Extended the shared `roll_intrinsic_abilities` helper in `intrinsic_roll.py` with a per-ability `chance` field. When `chance < 1.0`, draws `rng.random()` once and `continue`s on failure; the `chance` key is stripped from the output dict. Templates without `chance` consume zero extra RNG draws (byte-identical determinism for stars/warps/archetypes). Tuned `data/planet_types.json` v1.1 with chances 0.10–0.25 across 5 planet types; DYSON_SPHERE stays at 1.0.
* **Test Case:** `TestRollIntrinsicAbilitiesChanceGate` (6 unit tests) + `test_planet_types_chance_fields_in_valid_range` schema test. 114/114 targeted; 15731/15731 full sharded (around 14% of 100 planets get abilities, down from ~50%).
---

## [FEAT-16] - Planet List — filter and column support for planet effects/abilities
* **Date Completed:** 2026-04-27
* **Confirmed in:** QA Session 20260428_052952
* **Original Request:** Add Effects filter group and toggleable Effects columns to the Galactic Planet Registry, dynamically derived from abilities present in the loaded save.
* **Implementation Summary:** Promoted `make_group_key` / `make_display_name` to public helpers and added shared `format_intrinsic_ability_magnitude` in `system_effects_collector.py`. Refactored `filter_planets` to a predicate-list pipeline (six builders + new `effects_predicate`). Added `compute_planet_effect_keys(all_planets)` for dynamic discovery. `PlanetListFilterManager.filter_effects` state, `build_sidebar(..., effect_keys=None)` conditional rendering, `PlanetListWindow` per-effect columns via `build_effect_columns`, preset round-trip via `capture_planet_list_state` / `apply_planet_list_state`. Filter semantics: OR within Effects, AND across categories, zero-selected = no-op.
* **Test Case:** 124/124 FEAT-16 scope tests across 5 test modules (`test_planet_list_filters.py`, `_filter_manager.py`, `_window.py`, `_components.py`, `test_system_effects_collector.py`).
---

## [FEAT-18] - Build queue — add reorder-down arrow button
* **Date Completed:** 2026-04-27
* **Confirmed in:** QA Session 20260428_052952
* **Original Request:** Add a `v` (down-arrow) button to each build queue row symmetric to the existing `^` up-arrow.
* **Implementation Summary:** Bumped actions column width from 100 to 150 px (4 buttons * 30 + 3 spacers * 5 + padding = 145 min) so the down button is not overpainted by the adjacent portrait column. Replaced the no-op `update_visible_rows` actions branch with enable/disable logic for up button on row 0 and down button on the last row.
* **Test Case:** `test_update_visible_rows_disables_edge_action_buttons` (parametrised) + `test_actions_column_wide_enough_for_four_buttons` regression guard. 5 new tests; 621 build-queue + table tests pass.
---

## [FEAT-19] - Surplus-food happiness bonus (allocation > 1.0× rewards happiness)
* **Date Completed:** 2026-04-27
* **Confirmed in:** QA Session 20260428_052952
* **Original Request:** Increasing food allocation above 1.0× should reward happiness, not be a no-op.
* **Implementation Summary:** Added `ColonySpeciesConfig.last_food_surplus` `@property` (= `food_allocation × MIN(last_consumption_ratios)`, 1.0 fallback). Extended `EconomyConfig` with data-driven `surplus_food_bonus_per_x` (0.20) + `surplus_food_bonus_cap` (0.20). `HappinessEngine` takes `economy_config` kwarg and adds `min(cap, per_x × (surplus - 1.0))` before the existing [0, 3] clamp when `surplus > 1.0`. Facade `EconomySlice` pre-computes `food_surplus` + `food_surplus_bonus` on `SpeciesDemographicView`; UI conditionally renders surplus row when surplus > 1.0. `OrganicsConsumptionEngine` and `PopulationEngine` deliberately untouched (avoid double-counting via pop.happiness pathway).
* **Test Case:** 20 new tests across `test_colony_species_config.py`, `test_happiness_engine.py`, `test_demographics_loop.py`, `test_colony_demographic_view.py`, `test_strategy_detail_fmt.py`. QA repro verified: allocation 1.35× → happiness 0.24 → 0.31.
---

## [FEAT-21] - Strategy screen — numpad +/- keyboard zoom controls
* **Date Completed:** 2026-04-27
* **Confirmed in:** QA Session 20260428_052952
* **Original Request:** Numpad + / − keys should zoom the strategy camera in/out as a permanent secondary control (workaround for BUG-121 scroll-wheel regression).
* **Implementation Summary:** Plugged into the PROJ-71 data-driven keybinding system rather than raw KEYDOWN checks. Added `STRATEGY_ZOOM_IN` / `STRATEGY_ZOOM_OUT` `InputAction` values bound to `K_KP_PLUS` / `K_KP_MINUS` in `default_keybindings.json`. Routed via `UIActionRouter.handle_ui_action` to two new `CameraNavigator` methods (`zoom_in_step` / `zoom_out_step`) that mutate `camera.target_zoom` geometrically by `ZOOM_KEYBOARD_STEP = 1.5` (around 3 wheel ticks per press), clamped to `[min_zoom, max_zoom]`. Existing `Camera.update()` exponential interpolation handles smoothing.
* **Test Case:** 7 new tests across `test_camera_navigator.py` and `test_strategy_input_handler_hotkeys.py`. 233/233 targeted; 15824/15824 full sharded.
---
