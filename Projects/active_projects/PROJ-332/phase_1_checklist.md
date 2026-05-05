# PROJ-332 — Phase 1 Checklist

> 27 characterization tests across 7 new files. One commit per file (D-006). Each entry cites a concrete test function name + the production region it pins.

## File 1 — `tests/unit/strategy/turn_engine/test_turn_engine_init_precedence.py` (4 tests)

- [ ] **1.1** `test_init_kwarg_takes_precedence_over_config_field_when_both_supplied` — pins `__init__` precedence logic for at least one engine slot (e.g., `movement_engine` kwarg vs `config.movement_engine`).
- [ ] **1.2** `test_init_initializes_phase_times_with_14_canonical_keys` — pins `_reset_phase_times` keys exactly.
- [ ] **1.3** `test_init_threads_race_registry_through_when_supplied` and `test_init_accepts_race_registry_none` — pins `race_registry` slot wiring.
- [ ] **1.4** `test_init_initializes_last_environmental_events_to_empty_list` — pins env-events list init.

## File 2 — `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` (10 tests)

> The 5 properties already pinned by `test_dependency_injection.py` are skipped here. The 10 below are the gap.

- [ ] **2.1** `test_production_engine_property_returns_default_class_when_none_injected` (also asserts `prod_engine is prod_engine` for idempotency).
- [ ] **2.2** `test_order_processor_property_returns_default_class_and_is_idempotent`.
- [ ] **2.3** `test_resource_engine_property_returns_default_consumable_engine_and_is_idempotent`.
- [ ] **2.4** `test_population_engine_property_returns_default_class_and_is_idempotent`.
- [ ] **2.5** `test_resupply_engine_property_returns_default_class_and_is_idempotent`.
- [ ] **2.6** `test_harvesting_engine_property_returns_default_class_and_is_idempotent`.
- [ ] **2.7** `test_environmental_engine_property_returns_default_class_and_is_idempotent`.
- [ ] **2.8** `test_planet_energy_engine_property_returns_default_class_and_is_idempotent`.
- [ ] **2.9** `test_conflict_engine_uses_simulation_battle_resolver_when_ai_factory_provided_no_resolver` — `conflict_engine` lazy `battle_resolver` branch.
- [ ] **2.10** `test_conflict_engine_uses_null_battle_resolver_and_warns_when_both_resolver_and_ai_factory_none` — also asserts `_NullBattleResolver.resolve_battle` raises when invoked.

## File 3 — `tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py` (3 tests)

> **MIN-003 mocking note:** `_time_phase` calls `time.perf_counter()` twice and subtracts. To avoid CI flake under load, monkeypatch `time.perf_counter` to return a deterministic sequence (e.g. `[0.0, 2.5]`) and assert `phase_times[key] == 2.5` exactly. Do NOT assert `> 0` only — that masks regressions where the timing accumulator stops working entirely.

- [ ] **3.1** `test_reset_phase_times_returns_dict_with_14_canonical_keys` — pins exact key set: `harvesting`, `resources`, `fuel_gen`, `planet_energy`, `resupply`, `production`, `environmental`, `instant_orders`, `actions`, `planet_actions`, `activation_timers`, `movement_calc`, `movement_apply`, `combat`.
- [ ] **3.2** `test_time_phase_accumulates_timing_in_finally_block_when_wrapped_callable_raises` — uses monkeypatched `time.perf_counter` returning `[0.0, 2.5]`, asserts `phase_times["combat"] == 2.5` after the wrapped callable raises.
- [ ] **3.3** `test_time_phase_reraises_preexisting_engine_phase_error_without_double_wrapping` — uses `pytest.raises(EnginePhaseError) as exc_info`; asserts `exc_info.value.__cause__` is the original `EnginePhaseError`, not a wrapped chain.

## File 4 — `tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration.py` (4 tests)

- [ ] **4.1** `test_process_turn_captures_snapshot_when_session_provided_and_skips_when_none` — two cases asserting `snapshot.capture` calls.
- [ ] **4.2** `test_engine_phase_error_triggers_snapshot_restore_when_snapshot_and_session_set`.
- [ ] **4.3** `test_engine_phase_error_triggers_dump_crash_snapshot_when_snapshot_and_save_path_set`.
- [ ] **4.4** `test_snapshot_capture_failure_is_swallowed_and_turn_continues_with_snapshot_none` — D-008 observation; pins the broad-except behavior on capture failure.

## File 5 — `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py` (3 tests)

- [ ] **5.1** `test_end_of_turn_engines_called_in_order_organics_then_happiness_then_population` — uses `MagicMock` `mock_calls` ordering across the 3 engines.
- [ ] **5.2** `test_quality_atmosphere_water_engines_instantiated_per_process_turn_after_population_step` — uses `patch` on `QualityEngine`, `AtmosphereEngine`, `WaterEngine` import sites; asserts each is instantiated once and called after population (D-004 observation: locally-constructed not injectable).
- [ ] **5.3** `test_end_of_turn_engine_raise_propagates_unwrapped_and_skips_phase_times_recording` — D-007 observation; uses `happiness_engine.process` raising `RuntimeError`; asserts the exception propagates as-is (NOT `EnginePhaseError`) and `phase_times` does NOT contain a `happiness` key.

## File 6 — `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py` (2 tests)

- [ ] **6.1** `test_moved_fleet_ids_contains_only_fleets_that_moved_in_tick` — fleet at hex A moves to hex B; fleet at hex C does not move; asserts `moved_fleet_ids = {fleet_A.id}` is passed to `conflict_engine.detect_conflicts`.
- [ ] **6.2** `test_moved_fleet_ids_is_empty_set_with_zero_empires` — also covers zero-fleets case; conflict engine still called with `set()`, no exception.

## File 7 — `tests/unit/strategy/turn_engine/test_turn_engine_validation.py` (1 test)

- [ ] **7.1** `test_validate_colonize_order_constructs_validator_with_registries_fleet_planet_and_returns_result_unchanged` — uses `patch` on the `ColonizeValidator` import site.

## Per-file commit checklist

- [ ] Commit File 1 with message `test(PROJ-332): pin TurnEngine __init__ precedence and slot wiring`.
- [ ] Commit File 2 with message `test(PROJ-332): pin 10 TurnEngine lazy-property defaults and battle_resolver branches`.
- [ ] Commit File 3 with message `test(PROJ-332): pin _reset_phase_times keys and _time_phase failure-path timing`.
- [ ] Commit File 4 with message `test(PROJ-332): pin process_turn snapshot integration`.
- [ ] Commit File 5 with message `test(PROJ-332): pin end-of-turn engine order and unwrapped-error observation`.
- [ ] Commit File 6 with message `test(PROJ-332): pin PROJ-320 moved_fleet_ids derivation in _process_tick`.
- [ ] Commit File 7 with message `test(PROJ-332): pin validate_colonize_order delegation`.

## Final verification

- [ ] `pytest tests/unit/strategy/turn_engine/ -x -q` — ~80 tests green (53 existing + 27 new).
- [ ] `pytest tests/unit/strategy/ -x -q` — full strategy slice green.
- [ ] `python Tools/test_sharded/test_sharded.py` — full sharded suite green (modulo pre-existing unrelated failures).
- [ ] `python Tools/lint_test_files.py` — 0 violations.
- [ ] Update `Projects/projects_index.md`: PROJ-332 → Awaiting Verification.
