# Test Review Report: Agent 4 -- Strategy Facade/Generation/Save

## Scope
- **Source files reviewed:** 26 files, 5148 LOC
  - `game/strategy/facade/strategy_session_facade.py` (783 LOC)
  - `game/strategy/facade/dto/fleet_dto.py` (234 LOC)
  - `game/strategy/facade/dto/build_queue_dto.py` (41 LOC)
  - `game/strategy/facade/dto/planet_dto.py` (111 LOC)
  - `game/strategy/facade/dto/empire_dto.py` (116 LOC)
  - `game/strategy/facade/dto/system_dto.py` (162 LOC)
  - `game/strategy/generation/loaders/system_blueprints_loader.py` (241 LOC)
  - `game/strategy/generation/loaders/astrophysics_loader.py` (152 LOC)
  - `game/strategy/generation/star_image_registry.py` (111 LOC)
  - `game/strategy/generation/planet_image_registry.py` (129 LOC)
  - `game/strategy/generation/density/density_map.py` (241 LOC)
  - `game/strategy/generation/storm_generator.py` (220 LOC)
  - `game/strategy/generation/density/primitives/geometric.py` (101 LOC)
  - `game/strategy/generation/density/primitives/noise.py` (117 LOC)
  - `game/strategy/generation/loaders/galaxy_layouts_loader.py` (182 LOC)
  - `game/strategy/generation/placement_strategies.py` (210 LOC)
  - `game/strategy/generation/region_classifier.py` (275 LOC)
  - `game/strategy/generation/density/primitives/spiral_arm.py` (103 LOC)
  - `game/strategy/generation/density/primitives/linear.py` (86 LOC)
  - `game/strategy/generation/density/primitives/radial.py` (61 LOC)
  - `game/strategy/generation/density/primitives/ring.py` (63 LOC)
  - `game/strategy/events/event_types.py` (38 LOC)
  - `game/strategy/events/event_log.py` (114 LOC)
  - `game/strategy/systems/design_library.py` (470 LOC)
  - `game/strategy/systems/save_game_service.py` (468 LOC)
  - `game/strategy/quickstart_builder.py` (319 LOC)
- **Test files reviewed:** 62 files, 11556 LOC (unit + integration)
- **Coverage data referenced:** Yes -- line-level missing lines from coverage.json for all 26 source files

## Summary
- Test files reviewed: 62
- Source files reviewed: 26
- Tests flagged for removal: 5 (estimated LOC: 185)
- Tests flagged as happy-path-only: 6
- Source files with inadequate coverage: 5

---

## A. Tests Recommended for Removal

### A1. Duplicate EventQueries in facade tests
- **File:** `tests/unit/strategy/facade/test_strategy_session_facade.py`
- **Test(s):** `TestEventQueries` (lines 614-692) -- all 4 tests
- **Reason:** DUPLICATE_OF:`tests/unit/strategy/facade/test_event_queries.py`
- **Confidence:** HIGH
- **Evidence:** `test_event_queries.py` (157 LOC) tests the same facade methods (`get_turn_events`, `get_all_events`, `get_events_by_category`) using real `EventLog`/`Event` objects instead of mocks. It is strictly more thorough (tests string category, `EventCategory.ALL`, dict output format). The `TestEventQueries` class in `test_strategy_session_facade.py` (lines 614-692) fully mocks the event_log, adding no extra value.
- **Estimated LOC saved:** 78

### A2. Duplicate TestGameStateQueries class
- **File:** `tests/unit/strategy/facade/test_strategy_session_facade.py`
- **Test(s):** First `TestGameStateQueries` class (lines 453-478) -- tests `test_get_turn_number` and `test_get_human_player_ids`
- **Reason:** DUPLICATE_OF: second `TestGameStateQueries` class (lines 695-718)
- **Confidence:** MEDIUM
- **Evidence:** There are two classes with the same name `TestGameStateQueries` in the same file. Python will use the second definition, meaning the first class (lines 453-478 with `test_get_turn_number` and `test_get_human_player_ids`) is silently shadowed and never executed. Either rename the first class or merge the tests.
- **Estimated LOC saved:** 0 (needs fix, not removal -- the tests are shadowed and not running)

### A3. Event type constant assertions
- **File:** `tests/unit/strategy/events/test_event_types.py`
- **Test(s):** `TestEventType.test_ship_built_value`, `test_complex_built_value`, `test_colony_founded_value`, `test_combat_resolved_value`, `test_resource_shortage_value`, `test_fleet_joined_value`, `test_fleet_join_redirected_value`, `test_fleet_join_cancelled_value`; `TestEventCategory.test_production_value`, `test_colonies_value`, `test_combat_value`, `test_all_value`, `test_fleet_operations_value`
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** MEDIUM
- **Evidence:** These 13 tests each assert that a string enum member equals a specific string literal (e.g., `assert EventType.SHIP_BUILT == "ship_built"`). They test no logic, just that constants have the right values. The two count tests (`test_has_seventeen_members`, `test_has_seven_members`) and `test_all_values_are_strings` are the only ones with any regression value -- they catch accidental additions/removals.
- **Estimated LOC saved:** 42 (keep the 3 count/type-check tests, remove the 13 constant-equality tests)

### A4. Weak geometric rotation test
- **File:** `tests/unit/strategy/generation/density/test_geometric.py`
- **Test(s):** `TestGeometricPrimitive.test_rotation_affects_shape` (line 76-86)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Line 86: `assert d1 != d2 or True` -- this assertion always passes. The `or True` clause makes it a no-op. The test documents intent ("rotation should change orientation") but asserts nothing.
- **Estimated LOC saved:** 11

### A5. Weak spiral rotation test
- **File:** `tests/unit/strategy/generation/density/test_spiral_arm.py`
- **Test(s):** `TestSpiralArmPrimitive.test_rotation_shifts_pattern` (line 67-78)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** HIGH
- **Evidence:** Line 78: `assert d1 != d2 or True` -- identical issue to A4. Always passes regardless of actual behavior.
- **Estimated LOC saved:** 12

### A6. Weak layout sampling assertion
- **File:** `tests/unit/strategy/generation/density/test_layout_loader.py`
- **Test(s):** `TestAllLayoutsValid.test_layout_can_sample` (lines 130-150)
- **Reason:** TESTS_NOTHING_REAL
- **Confidence:** MEDIUM
- **Evidence:** Line 150: `assert coord is not None or True` -- always passes. The test exercises the sampling code path (useful for crash detection) but the final assertion is vacuous. Should be fixed to assert `coord is not None` or at minimum remove the `or True`.
- **Estimated LOC saved:** 0 (fix assertion, do not remove -- the code path exercise has value)

---

## B. Tests That Are Happy-Path-Only

### B1. StrategySessionFacade command dispatch helpers
- **File:** `tests/unit/strategy/facade/test_strategy_session_facade.py`
- **Test(s):** No tests exist for `dispatch_*` methods (26 dispatch helpers, lines 89-242)
- **What's tested:** Nothing -- zero tests for any dispatch helper
- **What's missing:** All 26 `dispatch_*` methods are untested. These are the entire write path of the facade (lines 89-242). Coverage shows all 76 missing lines in the facade are from these dispatch methods plus `get_empire_build_queues`/`get_hex_build_queues`. Tests should verify at minimum: (1) correct command class instantiation, (2) kwargs forwarded correctly, (3) return value from `handle_command` propagated.
- **Source method(s) affected:** `strategy_session_facade.py:89-242` (dispatch helpers), `strategy_session_facade.py:600-622` (build queue queries)
- **Priority:** HIGH -- these are the primary UI-to-engine mutation path. Zero test coverage means any refactoring of command names or kwargs will break silently.

### B2. BuildQueueSourceDTO.from_domain
- **File:** No test file covers `build_queue_dto.py`
- **Test(s):** None
- **What's tested:** Nothing
- **What's missing:** `BuildQueueSourceDTO.from_domain()` (lines 24-41, coverage shows lines 26-28 missing) converts a domain `BuildQueueSource` to a DTO. No test exercises this conversion. Edge cases: `source.owner_entity` missing `id`/`owner_id` attributes, `source.construction_queue` being empty or containing non-dict items.
- **Source method(s) affected:** `build_queue_dto.py:24-41`
- **Priority:** MEDIUM

### B3. PlanetInfo staging_yard aggregation
- **File:** `tests/unit/strategy/facade/test_population_dtos.py`
- **Test(s):** `TestPlanetInfoPopulation` tests population only
- **What's tested:** Population fields and empty population
- **What's missing:** The `staging_yard_summary` field (planet_dto.py lines 80-91, coverage shows lines 83-87 missing) is never tested. No test creates a Planet with `staging_yard` data. Also, `stockpile` and `max_stockpile` fields (lines 108-109) are not explicitly tested with actual data, though they may get exercised via integration tests.
- **Source method(s) affected:** `planet_dto.py:80-91` (staging_yard aggregation)
- **Priority:** LOW

### B4. FleetInfo order conversion -- only MOVE and BUILD tested
- **File:** `tests/unit/strategy/facade/test_fleet_dto_build.py`
- **Test(s):** Tests only BUILD and MOVE order types
- **What's tested:** `is_building` true/false, `has_space_shipyard`, `construction_queue_size`
- **What's missing:** FleetInfo.from_fleet order conversion (fleet_dto.py lines 130-178) covers MOVE, COLONIZE, MOVE_TO_FLEET, JOIN_FLEET, BUILD, and TRANSFER order types. Only MOVE and BUILD are tested. Coverage data shows lines 141-170 (COLONIZE dict/Planet target, MOVE_TO_FLEET/JOIN_FLEET Fleet target, TRANSFER dict target) are all missing coverage. Also, `cargo_resources`, `cargo_capacities`, `carried_items_summary`, `pod_storage_capacity`, `pod_storage_used` (lines 205-218, 220-234) are untested.
- **Source method(s) affected:** `fleet_dto.py:130-178` (order conversion), `fleet_dto.py:205-234` (cargo/carried items)
- **Priority:** HIGH -- these are the primary DTO fields consumed by UI panels.

### B5. DesignLibrary.save_design error paths
- **File:** `tests/unit/strategy/design_library/test_basics.py`
- **Test(s):** `test_save_design_new`, `test_save_design_prevents_overwrite_built`, `test_save_design_can_update_unbuilt`
- **What's tested:** Happy path save, built-design protection, update unbuilt
- **What's missing:** Error paths in `save_design` (design_library.py lines 251-262): PermissionError, OSError, ValidationException, and AttributeError/KeyError during `ship.to_dict()` or metadata creation. Coverage shows lines 251-262 are all uncovered. Also `scan_designs` error paths (lines 167-179): JSONDecodeError, KeyError, PermissionError/OSError, ValidationException during file scan are untested.
- **Source method(s) affected:** `design_library.py:251-262` (save error handlers), `design_library.py:167-179` (scan error handlers)
- **Priority:** MEDIUM

### B6. SaveGameService.get_save_info exception paths
- **File:** `tests/unit/strategy/save_game_service/test_error_handling.py`
- **Test(s):** `test_get_save_info_returns_none_on_error` -- only tests when `load_json` returns None
- **What's tested:** `load_json` returning None
- **What's missing:** The `get_save_info` method (save_game_service.py lines 439-468) has exception handlers for `PermissionError`, `OSError`, `json.JSONDecodeError` (line 463), and `KeyError`/`TypeError`/`ValueError` (line 466). Coverage shows lines 463-468 are all uncovered. Note: line 463 references `json.JSONDecodeError` but the module imports are `from json import JSONDecodeError` -- this may be a latent bug where the except clause references `json.JSONDecodeError` without `import json`.
- **Source method(s) affected:** `save_game_service.py:463-468`
- **Priority:** HIGH -- potential latent bug at line 463 (`json.JSONDecodeError` used but `json` not imported as a module; the `from json import JSONDecodeError` at line 13 does not make `json.JSONDecodeError` available).

---

## C. Source Code with Inadequate Coverage

### C1. strategy_session_facade.py
- **Source file:** `game/strategy/facade/strategy_session_facade.py` (783 LOC)
- **Coverage:** 74.7% -- 75 lines missing
- **Untested areas:**
  - All 26 `dispatch_*` command helpers (lines 91-242) -- zero coverage on every one
  - `get_empire_build_queues` (lines 600-605) -- untested
  - `get_hex_build_queues` (lines 617-622) -- untested
- **Risk:** Any rename/refactoring of command classes or kwargs will break silently. Build queue query delegation is completely untested.
- **Priority:** HIGH

### C2. fleet_dto.py
- **Source file:** `game/strategy/facade/dto/fleet_dto.py` (234 LOC)
- **Coverage:** 75.5% -- 24 lines missing
- **Untested areas:**
  - Order conversion for COLONIZE with dict target containing 'planet' key (lines 141-148)
  - Order conversion for COLONIZE with Planet target (lines 149-152)
  - Order conversion for MOVE_TO_FLEET/JOIN_FLEET (lines 153-157, partial)
  - Order conversion for BUILD order (lines 158-160)
  - Order conversion for TRANSFER order (lines 161-170)
  - `_aggregate_carried_items` static method (lines 220-234) -- completely untested
  - `capabilities` error handling (line 184) -- ValueError/AttributeError path untested
- **Risk:** UI order display panels rely on these conversions. A regression in order-to-DTO mapping would show wrong info in fleet panels.
- **Priority:** HIGH

### C3. system_blueprints_loader.py
- **Source file:** `game/strategy/generation/loaders/system_blueprints_loader.py` (241 LOC)
- **Coverage:** 78.5% -- 17 lines missing
- **Untested areas:**
  - `_validate_blueprint` error paths: missing `star_count` (line 166), missing `planet_count` (line 172), missing `weight` (line 178), star_count range violations (lines 188, 196, 201-202, 208), planet_count not-a-dict (line 217), planet_count missing min/max (line 223), planet_count invalid range (line 229), weight <= 0 (line 237)
  - `_validate_schema` error paths: data not dict (line 129), missing 'blueprints' key (line 136), blueprints not dict (line 144)
  - `select_random_blueprint` no-positive-weights path (line 101)
  - `select_random_blueprint` fallback return (line 116)
- **Risk:** Invalid blueprint data files would load silently without validation errors. The schema validator exists but many of its branches are untested.
- **Priority:** LOW -- the data files are fixed assets, not user-supplied. But if someone adds a new blueprint with a typo, validation won't catch it in tests.

### C4. design_library.py
- **Source file:** `game/strategy/systems/design_library.py` (470 LOC)
- **Coverage:** 81.0% -- 43 lines missing
- **Untested areas:**
  - `__init__` OSError fallback path (lines 132-138): when primary makedirs fails with OSError (not PermissionError), falls back to temp dir
  - `scan_designs` None designs_folder guard (lines 149-151)
  - `scan_designs` individual file error handlers: JSONDecodeError (167-169), KeyError (170-172), PermissionError/OSError (173-175), ValidationException (176-179)
  - `save_design` error handlers: PermissionError (251-253), OSError (254-256), ValidationException (257-259), AttributeError/KeyError (260-262)
  - `mark_obsolete` error handler for JSONDecodeError (329-330), PermissionError/OSError (331-332), catch-all (333-335)
  - `increment_built_count` error handlers: JSONDecodeError (369-370), PermissionError/OSError (371-373), catch-all (374-376)
- **Risk:** File system errors during design operations would be unhandled in production. However, all error handlers simply log and return False/error tuples, so the risk is limited to logging correctness.
- **Priority:** MEDIUM

### C5. save_game_service.py
- **Source file:** `game/strategy/systems/save_game_service.py` (468 LOC)
- **Coverage:** 89.8% -- 24 lines missing
- **Untested areas:**
  - `save_game` PermissionError path (line 96, save_json returns False for metadata)
  - `list_turns` PermissionError (lines 183-184), OSError (lines 188-189)
  - `list_saves` PermissionError (lines 226-227)
  - `get_save_info` exception handlers (lines 463-468) -- potential bug: `json.JSONDecodeError` referenced but `json` module not imported (only `from json import JSONDecodeError` at line 13)
  - `delete_save` `shutil.Error` path (lines 263-265)
  - `_reconstruct_game_session` `AttributeError/ImportError/RuntimeError/StateException` path (line 400-402)
  - `_load_save_metadata` missing metadata keys path (line 329) -- partially tested
- **Risk:** The `get_save_info` method (lines 463-468) has a likely NameError bug: `json.JSONDecodeError` is used but `json` is not imported as a module. If `load_json` returns a result that triggers the except clause, it would raise `NameError: name 'json' is not defined` instead of handling the error gracefully.
- **Priority:** HIGH for the `json.JSONDecodeError` bug; LOW for the other missing error paths (they are standard error-logging patterns).

---

## D. Cross-Domain Observations

### D1. Shadowed test class -- silently lost tests
In `tests/unit/strategy/facade/test_strategy_session_facade.py`, there are two classes both named `TestGameStateQueries` (lines 453 and 695). Python uses the second definition, meaning `test_get_turn_number` and `test_get_human_player_ids` (lines 456-478) are silently never executed. This is a bug in the test file, not a domain issue, but affects test coverage counts across the board.

### D2. Potential production bug in save_game_service.py:463
`get_save_info` (line 463) catches `json.JSONDecodeError` but the file only has `from json import JSONDecodeError` (line 13), not `import json`. This means if `load_json` somehow lets a JSONDecodeError through (unlikely since `load_json` catches it internally), the except clause would fail with `NameError`. This should be verified and fixed by either changing to `JSONDecodeError` or adding `import json`.

### D3. MockGameSession duplicated across files
`MockGameSession` is copy-pasted identically in `tests/unit/strategy/save_game_service/conftest.py`, `test_save_load_ops.py`, and `test_error_handling.py`. This creates maintenance burden -- if the mock needs updating (e.g., new required fields), three files must change. Should be consolidated into `conftest.py` only.

### D4. Integration save/load tests are comprehensive
The 20 integration test files under `tests/integration/save_load/` provide excellent roundtrip coverage for all entity types (planets, fleets, empires, galaxies, stars, storms, events, orders, configs, research, ships, designs). They test corrupt data, version mismatches, missing fields, and multi-cycle save/load. These integration tests compensate for gaps in the unit-level SaveGameService tests, particularly for the reconstruction path.

### D5. `assert ... or True` anti-pattern
Three tests use `assert X or True` which always passes (A4, A5, A6 above). This pattern appears to be intentional ("may be equal by coincidence") but renders the test assertions meaningless. These should either have the `or True` removed (accepting occasional false failures) or be rewritten with deterministic test inputs that guarantee inequality.
