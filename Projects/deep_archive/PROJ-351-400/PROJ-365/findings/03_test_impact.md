# PROJ-355 Test Impact Analysis

## 1. Tests under tests/unit/strategy/turn_engine/ (13 files)
- **`test_turn_processing.py`** (~104 lines) — phase ordering via `call_order` tracking; validates sequence harvest → resource → fuel_gen → resupply → construct → instant → action → collect → apply → combat.
- **`test_tick_mechanics.py`** — movement calc, JOIN_FLEET, no phase-ordering assertions.
- **`test_turn_engine_phase_timing.py`** — `_time_phase` accumulators, 20 canonical timing keys, exception-wrap.
- **`test_turn_engine_end_of_turn_order.py`** — end-of-turn engine call order (organics → happiness → population), local-construction of QualityEngine/AtmosphereEngine/WaterEngine.
- **`test_turn_engine_phase_320_movement_diff.py`** — `moved_fleet_ids` derivation between phases 3 and 4.
- **`test_dependency_injection.py`** — constructor DI, mixed mock/default engines.
- **`test_turn_engine_init_precedence.py`** — kwarg precedence over config.
- **`test_turn_engine_lazy_properties.py`**, **`test_turn_engine_validation.py`**, **`test_turn_end_of_turn_engine_rollback.py`**, **`test_turn_error_handling.py`**, **`test_turn_snapshot_capture_failure.py`**, **`test_turn_engine_snapshot_integration.py`**.

## 2. Phase-order-pinning tests (will require migration)
- **`test_turn_processing.py::TestTickProcessing::test_tick_calls_phases_in_order`** (lines 69-108) — uses `call_order` list via `side_effect` callbacks. **Refactor:** assert against descriptor list rather than internal `make_tracker` mocks.
- **`test_turn_engine_end_of_turn_order.py`** (lines 43-92) — uses `parent.mock_calls` for cross-mock ordering. End-of-turn block stays imperative (out of scope for PROJ-355), so this test should be unaffected; verify during implementation.

## 3. Timing accumulator tests
- **`test_turn_engine_phase_timing.py`** — pins `_time_phase` accumulator with monkeypatched `time.perf_counter`, asserts exact deltas, double-wrap protection.

**Impact:** descriptor model preserves `_time_phase` semantics via `timing_bucket`; tests should remain green if bucket keys are stable.

## 4. moved_fleet_ids derivation (phase 3→4 boundary)
- **`test_turn_engine_phase_320_movement_diff.py`** — two characterization tests:
  - Fleet moves → `moved_fleet_ids = {100}`
  - Zero empires → empty set still passed to combat (`set()`).

**Impact:** TickContext design must preserve this contract — characterization tests are PROJ-320 invariants and must stay green post-refactor.

## 5. Single-phase boundary coverage
- **Isolated unit tests:** `test_tick_mechanics`, `test_dependency_injection`, `test_turn_engine_init_precedence`.
- **Integration-only phases:** all 14 tick phases tested only via `test_turn_processing.py` end-to-end flow. **No isolated phase unit tests** for individual phases.
- **Gap:** Phase 1.8 (PlanetModifierEffectEngine) is mocked but not tested in isolation.

## 6. Contract-test gap: DEFAULT PHASE LIST EXECUTION
**Does NOT exist.** No test currently asserts: "the default phase list executes in expected order with expected args." Closest proxy is the `call_order` test in `test_turn_processing.py`, but it manually builds mocks and doesn't reference a stable phase list.

## 7. Recommended new tests
1. **TickPhase descriptor unit test:** verify shape, args_resolver behavior, error_policy dispatch, tick_gating.
2. **Default phase list ordering test:** introspect `DEFAULT_TICK_PHASE_LIST` and assert phase_key order matches a frozen golden list (PROJ-320 invariant).
3. **Override-via-kwarg test:** TurnEngine constructed with `tick_phases=[custom_phases]` runs those instead of defaults.
4. **TickContext invariants test:** after phase 3, `pre_movement_locations` is non-None; `moved_fleet_ids` derived correctly.

File: `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py`.

## 8. Reusable fixtures
- **Minimal engine:** `tests/unit/strategy/turn_engine/conftest.py::turn_engine`
- **Mock empire/galaxy:** `tests/unit/strategy/turn_engine/conftest.py::mock_empire/mock_galaxy/mock_fleet`
- **Integration fixtures:** `tests/integration/strategy/turn_engine/conftest.py`
- **Global `fresh_registries`:** `tests/conftest.py`

## Summary
Coverage of the imperative phase code is good for end-to-end and DI; the contract-level "phase list = golden list" test is the explicit deliverable of PROJ-355 Phase 1. Two existing tests (`test_turn_processing.py`, `test_turn_engine_phase_320_movement_diff.py`) are PROJ-355's behavioral invariants and must stay green.
