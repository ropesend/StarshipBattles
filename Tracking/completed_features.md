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

## [FEAT-13] - Generate visual asset captions for race images (LLM description metadata)
* **Date Completed:** 2026-04-28
* **Confirmed in:** QA Session 20260428_190154
* **Original Request:** Generate `.caption.json` sidecars for every existing visual asset (flags, race portraits, ship themes) so the Race Setup Description LLM (PROJ-296/299) receives real visual references instead of placeholder `{"note": "no visual reference available"}`.
* **Implementation Summary:** Generated caption sidecars conforming to schemas in `Tools/captioning/schemas/` for all visual assets — flags (geometry/color_palette/symbolism/cultural_hints/mood/distinctive_traits), race portraits (anatomy/coloration/attire_and_adornment/posture_and_expression/technology_level_hint/distinctive_traits), and ship themes (hull_geometry/materials_and_finish/design_philosophy/color_scheme/technology_level_hint/distinctive_traits). Captioning toolchain at `Tools/captioning/` drives generation via Gemini-vision.
* **Test Case:** Caption files validated by `Tools/captioning/validate_captions.py`. Bio/socio descriptions visibly reference visual traits.
* **Notes:** New asset additions should follow the captioning workflow documented in `Tools/captioning/README.md`.
---

## [FEAT-17] - Build queue pause/unpause toggle button
* **Date Completed:** 2026-04-27
* **Confirmed in:** QA Session 20260428_190154
* **Original Request:** Add a "Pause Build Queue" toggle button at the bottom-left of every per-yard build queue panel that stops resource consumption while preserving accumulated progress on the in-progress item.
* **Implementation Summary:** Added `construction_queue_paused: bool = False` to the three yard-owning entities (`Planet`, `PlanetaryFacility`, `Fleet`). `ProductionEngine.process_construction_tick` gates each iteration site (planet base / facility / fleet yard) on the flag; `_process_queue_tick_dynamic` unchanged so dispatcher/processor split stays clean. Treasury (`EmpireEconomyCalculator`) and Planet-detail (`PlanetEconomyProjector`) skip paused queues so the forecasted next-turn drain matches what `ProductionEngine` will consume. New `SetBuildQueuePausedCommand` + handler follow the PROJ-208 CQRS pattern. New `BaseCommandHandler._resolve_queue_owner` helper. UI: text-only "Pause Build Queue" / "Unpause Build Queue" toggle at the bottom-left of the per-yard build queue panel; Empire Build Queue Window gets a read-only "Status" column showing PAUSED. AI controllers do not touch the flag — player-driven only. Save/load uses `data.get('construction_queue_paused', False)` so legacy saves load with paused=False.
* **Test Case:** 37/37 paused-feature tests pass (`test_paused_queue.py`, `test_construction_queue_paused_persistence.py`, `test_facility_construction_queue.py`, `test_build_queue_source.py`, `test_planet_economy_projector.py`, `test_empire_economy_calculator.py`, `test_set_build_queue_paused_command.py`, `test_empire_build_queue_filter_manager.py`, `test_empire_build_queue_window.py`). Full sharded suite 15802/15802 pass.
* **Notes:** Flag lives on the yard-owning entity (NOT on `BuildQueueSource` which is transient/derived, NOT per queue item). Currently-progressing item retains its `resources_consumed` while paused; unpausing resumes from saved progress on the next tick (no rollback).
---

## [FEAT-23] - Race Setup Summary tab — relocate portrait next to flag, widen environment column to right two-thirds
* **Date Completed:** 2026-04-28
* **Confirmed in:** QA Session 20260428_190154
* **Original Request:** Restructure the Summary tab from three equal-width columns into a left ⅓ / right ⅔ arrangement so the Environment / Aptitudes / Descriptions block has more horizontal room. Portrait moves below the flag in the left column.
* **Implementation Summary:** Single-file restructure in `game/ui/panels/race_summary_panel.py`. `_create_content` switched from `col_width = (panel_width - 40) // 3` to two named widths: `left_col_width = panel_width // 3 - 15` and `right_col_width = panel_width - left_col_width - 30`. Dropped the legacy `y - 55` alignment hack. `_create_column1_content` renamed to `_create_left_column_content` and extended to also place Portrait header + 280×280 panel at the bottom of the left column. `_create_column2_content` deleted; Ship-Theme header+value migrated to a new `_create_ship_theme_strip(x, y, full_width, height)` helper that places a 30-px strip above the ship preview gallery. The `summary_labels['theme_header']` / `summary_labels['theme_value']` keys are preserved so `refresh()` and FEAT-12 randomization continue to work. `_create_column3_content` renamed to `_create_environment_column` with new `(x, y, col_width, col_height)` signature.
* **Test Case:** Existing 20 tests in `tests/unit/ui/test_race_summary_panel.py` unchanged — they assert label text/keys, not pixel coordinates, so the restructure is transparent. All 3668 ui-tests pass.
---

## [FEAT-24] - Default new-game galaxy size to 5 systems
* **Date Completed:** 2026-04-28
* **Confirmed in:** QA Session 20260428_190154
* **Original Request:** Lower the default galaxy size on the New Game Setup screen from 50 systems to 5 systems and the slider's minimum from 25 to 5 so first-time and iteration runs start with a tiny galaxy.
* **Implementation Summary:** 4 edits in `game/ui/screens/new_game_setup_screen.py` — `self.system_count = 50` → `5`; slider `value_range=(25, 150)` → `(5, 150)`; `build_game_config(..., system_count: int = 50)` → `5`; docstring `"default: 50"` → `"default: 5"`. Click increment unchanged at 5.
* **Test Case:** New `TestNewGameSetupSystemCountDefault` class (2 tests, TDD red-green) in `tests/unit/ui/test_new_game_setup.py`. Targeted: 37 passed across `test_new_game_setup.py` and `test_new_game_setup_extended.py`. Direct `pytest tests/`: 15905 passed, 3 skipped.
* **Notes:** Followup feature requested in QA Session 20260428_190154 — extend galaxy generator to support starting with 1–2 systems (which has different invariants: no warp points to place, both empires share a system when systems=1).
---

## [FEAT-20] - Dev "Run 10 turns" button next to End Turn (revised: always-visible, no longer dev-gated)
* **Date Completed:** 2026-04-28
* **Confirmed in:** QA Session 20260428_190154
* **Original Request:** Add a development button next to End Turn that automatically advances the turn 10 times in a row. Revised mid-flight: button should appear unconditionally (not gated behind `--dev`).
* **Implementation Summary:** First pass added a full `--dev` plumbing path (CLI flag → `BootstrapResult.dev_mode` → `ScreenRouter` → `StrategyScreen` → `StrategyUI` → `create_strategy_panels`) gating `btn_run_10_turns` at top-bar slot 10. Click handler calls `StrategyScreen.run_n_turns(10)` → `StrategyGameStateManager.run_n_turns(n)` which loops `process_full_turn()` n times. Esc-cancellation between iterations via `_pump_cancel_events()`; auto-save per turn means cancel can never corrupt saves. Per-turn event-log auto-open suppressed during the loop; a single combined log surfaces at the end. Overlay text parametrised: "PROCESSING TURN k / N… (Esc to cancel)". **Revised scope (per CLAUDE.md System Migration Policy):** sole-consumer audit confirmed FEAT-20 was the only consumer of `--dev` / `dev_mode`, so the entire flag plumbing was eradicated (6 production files + 4 net tests deleted). The button now renders unconditionally; `btn_run_10_turns` field on `StrategyWidgets` retained (default None harmless). `docs/03_CONVENTIONS.md` §10 (Dev-Mode CLI Flag) deleted; §11 Ship Theme renumbered to §10.
* **Test Case:** `test_strategy_panel_manager.py` (button always present), `test_strategy_game_state_manager.py` (7 `run_n_turns` tests including Esc-cancel and event aggregation), `test_strategy_input_handler_core.py` (click routes to `run_n_turns(10)`), `test_strategy_screen.py` (draw-overlay message signature). Full pytest: 16100 passed, 3 skipped.
* **Notes:** Hardcoded `n=10` in the click handler; underlying method takes `n` for future variants. Cancellation is strictly between-iteration (never mid-turn) because each `process_full_turn()` ends with auto-save.
---

## [FEAT-22] - Startup phase profiling — log timings before main menu appears
* **Date Completed:** 2026-04-28
* **Confirmed in:** QA Session 20260428_190154
* **Original Request:** Surface phase-by-phase timing for the bootstrap path so the slow phase(s) before the main menu can be identified.
* **Implementation Summary:** 14-phase instrumentation in `game/app_bootstrap.py`. New private `_timed_phase(name, profiler)` context manager records into `profiler.records` and emits `[startup] <name>: X.XXs` via `logger.info`. `pygame.init` and `ctx.create_production` timed via raw `perf_counter` (profiler doesn't exist yet); records back-filled into the real profiler immediately after `create_production()` returns. 12 sub-phases wrapped: `font.init`, `font.preload`, `display.detect_resolution`, `display.set_mode`, `registry.load_components`, `registry.load_modifiers`, `registry.load_resources`, `registry.initialize_ship_data`, `registry.build_game_registries`, `assets.ensure_component_derivatives`, `assets.load_sprites`, `input.load_keybindings`. Final `[startup] total bootstrap: X.XXs` line. Eager `ctx.profiler.save_history()` before `bootstrap()` returns so launch diagnostics survive in-game crashes.
* **Test Case:** 6 tests in `tests/unit/test_app_bootstrap_profiling.py`. PROJ-309 invariants test (`test_app_bootstrap_invariants.py`) still passes — context-manager wrapping does not reorder calls.
* **Notes:** Docs: `docs/02_PATTERNS.md` Profiler section gained a "Bootstrap Phase Timing" subsection.
---

## [FEAT-25] - Planet Registry — upgrade Effects filter from on/off chips to 3-way tri-state
* **Date Completed:** 2026-04-28
* **Confirmed in:** QA Session 20260428_190154
* **Original Request:** Extend the Effects filter (FEAT-16) from binary on/off chips to YES/NO/IGNORE tri-state filters, using `FilterState` + `TriStateWidget`. Thermal Damage / Shield Modifier / Thrust Modifier called out as priority effects.
* **Implementation Summary:** End-to-end migration across 5 production + 3 test files; the FEAT-16 OR-within-Effects contract is fully replaced (no compatibility layer). `planet_list_filter_manager.py`: `filter_effects` retyped to `Dict[str, FilterState]`; `toggle_effect` deleted; `set_all_effects` takes a `FilterState`. `planet_list_filters.py`: `effects_predicate` rewritten (skip IGNORE, AND across YES/NO). `planet_list_sidebar.py`: chip loop replaced with `TriStateFilterWidget` rows; `All` / `None` buttons retained for Effects (intentional divergence from fleet-report; Effects is dynamically-sized so bulk-clear has real ergonomic value). `planet_list_window.py`: seed flipped to `{k: FilterState.IGNORE}`; event-handler uses `widget.check_pressed(event.ui_element)`. `planet_list_presets.py`: serializes FilterState as `.value` strings (`"yes"`/`"no"`/`"ignore"`); apply reads them back into the enum and silently drops legacy bool / invalid-string entries to `IGNORE`.
* **Test Case:** `TestEffectsPredicate` rewritten (8 tests covering all-IGNORE no-op, YES/NO presence/absence, AND composition, IGNORE-mixed, EnvironmentalDamage subtype distinction). `TestFilterEffects` rewritten for FilterState enum values. New `TestPresetRoundTrip` class (4 tests). Full sharded suite: 16050 tests, 16049 passed, 1 known isolation flake.
* **Notes:** Builds on FEAT-16 (archived).
---

## [FEAT-26] - Wire replay_id through to Event Log and add Replay button on combat entries (closes PROJ-312 UI gap)
* **Date Completed:** 2026-04-29
* **Confirmed in:** QA Session 20260428_190154
* **Original Request:** PROJ-312 captures every battle to disk but the user has no way to open one. Thread `replay_id` from the simulation layer through to the Event Log and add a per-row Replay button on combat entries.
* **Implementation Summary:** Plumbing path: `engine.replay_id` → `BattleOutcome` (`battle_outcome.py`) → `BattleResult` (`battle_resolver.py`) → `COMBAT_RESOLVED.details["replay_id"]` (`conflict_resolution_engine.py`). Empty-string canonicalisation at the `extract_outcome` seam keeps "no replay" a single signal. UI: new generic `replay_action` single-button column type in `VirtualTable` (distinct from build-queue 4-button `actions` column); `EventLogWindow` accepts `replay_resolver` + `launch_replay_callback` kwargs and dispatches per-row clicks via `_handle_replay_click`; `EventLogRegistrar` builds `ReplayResolver.from_registries(...)` from the active save's `ReplayStore` + loaded component registry. New `Game.start_replay(record)` wraps `replay_record_to_spec` + `BattleConfig(replay_mode=True, replay_id=..., captured_telemetry_level=...)` through the widened `screen_router.start_battle(spec, *, headless=False, config=None)`. `BattleScreen.draw_hud` renders a top-center "REPLAY MODE" badge when `controller.config.replay_mode is True`. Graceful degradation on missing/corrupt/version_drift via `UIMessageWindow` toast; registry_drift warns and proceeds. Docs: `docs/systems/strategy_layer.md` §5 Event System gained the Replay Wiring subsection (capture flow diagram, click flow, graceful-degradation states, forwarder + widening notes).
* **Test Case:** 37 new tests across `test_battle_outcome_replay_id.py`, `test_battle_resolver_replay_id.py`, `test_conflict_resolution_event_replay.py`, `test_simulation_adapter.py::TestSimulationAdapterReplayId`, `test_event_log_replay_button.py`, `test_event_log_data_source.py` (column-count 8→9), `test_event_log_graceful_degradation.py`, `test_event_log_replay_e2e.py`. Full regression: 16122 passed, 3 skipped.
* **Notes:** Deferred to follow-ups (per loose-acceptance interpretation): Combat Lab + Battle Setup capture (only strategy battles populate `replay_id` in v1; the field exists on every `BattleResult`); `engine.replay_id` typed-attribute cleanup (currently `# type: ignore[attr-defined]` on `BattleEngine`). Companion fix to BUG-126 — closing FEAT-26 alone makes BUG-126's "no replay to verify" symptom disappear.
---

## [FEAT-27] - Allow new-game galaxy size as low as 1 system (default 2; enforce distinct systems per empire when N≥2)
* **Date Completed:** 2026-04-29
* **Confirmed in:** QA Session 20260428_190154
* **Original Request:** Extend FEAT-24 — slider min 1, default 2. systems=1 produces 0 warp points and all empires start in the same system on different planets. systems≥2 enforces distinct systems per empire.
* **Implementation Summary:** New `DEFAULT_SYSTEM_COUNT = 2` / `MIN_SYSTEM_COUNT = 1` / `MAX_SYSTEM_COUNT = 150` module-level constants in `game_config.py` are the single source of truth. `GameConfig.__post_init__` validates `1 ≤ system_count ≤ 150` and rejects `len(players) > system_count` at N≥2; N=1 explicitly bypasses (intentional shared-system mode). `GameInitializer.initialize()` drives a planet-shortage retry loop (up to 10 attempts, perturbing `galaxy_seed` via `dataclasses.replace`); clears `empire.colonies` between attempts; raises `ValidationException` on exhaustion. Extracted `_empire_home_indices(num_empires, num_systems)` returning a hand-rolled linspace `[round(i * (N-1) / (E-1)) for i in range(E)]` (vs. the old stair-step that clustered at the low end). At N=1, every empire shares `systems[0]` and gets a *different* planet via a per-system `next_planet_in_system` counter — fixes the silent `Planet.owner_id` overwrite. UI: new module-level `system_count_slider_curve(t)` + `system_count_slider_inverse(value)` implement a quadratic curve over an internal `[0, 1000]` slider range mapping to `[1, 150]`. Fine-grained at the low end (each pixel near `t=0` is a 1-system change), coarser at the high end. Docs: `docs/systems/strategy_layer.md` §6 "Galaxy Size Contract".
* **Test Case:** NEW `tests/unit/strategy/engine/test_game_config.py` (default, bounds 0/151/-1/10000 rejected; 1/2/150 accepted; `len(players) > system_count` rejection at N≥2; N=1 multi-empire accepted). Extended `test_game_initializer.py` (N=1/E=1, N=1/E=2 shares system with distinct planets and correct `owner_id`, N=1/E=2 zero warp points, N=2/E=2 distinct systems + one warp link, N=5/E=4 evenly-spread, planet-shortage retries-then-raises, retries-then-succeeds-on-attempt-2). NEW `test_galaxy_warp_generator.py` (N=0/1 zero warps, N=2 one link). Extended `test_new_game_setup.py` (9 slider-curve tests: clamping, monotonicity, fine-low/coarse-high, landing coverage, default-2 reachability). 19 `system_count=0 → 1` sentinel updates in `tests/integration/strategy/test_command_handlers.py` (auto-merged cleanly with BUG-125). Full pytest: 16167 passed, 3 skipped.
* **Notes:** Original deep-dive-parallel investigator stalled after partial implementation; resumed by deep-dive-resume team, which rebased the worktree cleanly onto BUG-125 head and retained the partial work (matched the user-clarified continuous quadratic slider design).
---

## [FEAT-28] - Mutual JOIN orders should make both fleets move toward each other (rendezvous)
* **Date Completed:** 2026-04-29
* **Confirmed in:** QA Session 20260428_190154
* **Original Request:** When two fleets are mutually assigned to join each other (A: JOIN→B, B: JOIN→A) today only one fleet moves; the user wants both fleets to start heading toward each other.
* **Implementation Summary:** Diagnosis confirmed empirically — today's `calculate_intercept_point` is asymmetric for mutual pursuit (the candidate equal to the chaser's own current location wins, so one fleet picks "stay still"). New `FleetNavigationService._is_mutual_pursuit(self_fleet, target_fleet)` predicate (reads target's head order; True iff `MOVE_TO_FLEET`/`JOIN_FLEET` targeting `self_fleet`). `get_destination` MOVE_TO_FLEET branch checks the predicate first; on True, returns `target_fleet.location` directly, bypassing `calculate_intercept_point`. Optional `self_fleet=None` parameter threaded through `compute_next_step` and `_resolve_path_for_order`; `calculate_fleet_next_hex` and `_project_path_inner` pass `self_fleet=fleet`. New `FleetMovementEngine._filter_jump_past_collisions(move_queue)` post-processor: detects mutual-pursuit pairs whose next-hex assignments would swap (`next_a == fleet_b.location` AND `next_b == fleet_a.location`) and drops the larger fleet's entry (more ships wins; tiebreak smaller `fleet.id` — mirrors BUG-122 `_elect_canonical_merges`). Docs: `docs/systems/strategy_layer.md` gained the "Mutual-Pursuit Rendezvous Routing" subsection under FleetPursuerTracker.
* **Test Case:** NEW `tests/unit/strategy/services/test_fleet_navigation_mutual_pursuit.py` (10 cases — predicate truth table, mutual branch returns target location, fall-through when not mutual, `self_fleet=None` fallthrough, signature contract). NEW `tests/integration/strategy/test_mutual_join_rendezvous.py` (7 cases — empirical baseline ≥100 sub-ticks at distance 10 with predicate disabled, rendezvous ≤2/3 of baseline, JOIN_FLEET not prematurely cancelled, one-fleet-cancels-fallback no-crash, swap-parity larger-fleet delays, swap-parity ship-count tiebreak, no-swap no-filter passthrough). Anti-reversion verified for BUG-122 / BUG-125 / PROJ-222 / `_projection_guard` re-entrancy. Full suite: 16184 passed, 3 skipped.
* **Notes:** v1 covers swap-parity only; broader leapfrog cases deferred (fleets at distance 3 land 1 hex apart next tick anyway and merge naturally). Speed-balanced rendezvous (meet hex shifts toward slower fleet), visual indicator on map, and multi-way (3+) rendezvous are explicitly out of scope. Builds on BUG-122's `PursuerTracker` data model.
---
