# PROJ-353 Test Impact Analysis

## 1. CommandHandlerRegistry tests
- **`tests/unit/strategy/test_command_handlers.py`** (~1,890 lines) — 13 handler-specific test classes; covers registry dispatch, handler registration, error paths.
- **`tests/unit/strategy/engine/test_command_handlers_public_api.py`** (~87 lines) — Contract guard for ~21 public symbols.

Key tests:
- `TestCommandHandlerRegistry.test_register_and_dispatch`
- `test_create_default_registry_has_all_handlers`
- `test_create_default_registry_dispatches_all_command_classes`

**Status:** Dispatch mechanism, handler registration, and error handling well-covered.

## 2. ActionTimeResolver tests
**File:** `tests/unit/strategy/services/test_action_time_resolver.py` (~282 lines)
- Explicit action_time, string shorthand, defaults
- Superweapon timings (IMPLODE_PLANET=3, STELLERATE_STAR=5, SELF_DESTRUCT→1)
- Parametrized over TRANSFER, LOAD_POPULATION, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE

**Gap:** No test asserts every OrderType has an action_time entry or defaults safely.

## 3. OrderProcessor dispatch tests
- `test_order_processor_colonize.py`, `test_order_processor_instant.py`, `test_order_processor_transfer.py`
- `test_superweapon_order_processor*.py` (3 files), `test_build_order_processor.py`
- `test_action_execution_engine*.py` (2 files)

**Gap:** No test validates every OrderType has a dispatch path or is intentionally instant.

## 4. Serialization round-trip
**File:** `tests/unit/strategy/data/test_order_serializer.py` (~408 lines)
- `TestRoundTrip` covers all 7 target formats
- `test_every_order_type_deserializes` (parametrized over OrderType)
- Corrupt-data handling

**Gap:** No assertion that every serialized OrderType has a registered handler.

## 5. Integration tests
- `tests/integration/strategy/facade/test_facade_integration.py` (~16K) — command flow through facade
- `tests/integration/strategy/production/test_fleet_save_load.py` (~7.6K) — save/load round trip

**Gap:** No test validates "every OrderType is saveable + loadable + has handler."

## 6. Critical gaps (the contract test PROJ-353 must add)
1. **No CommandSpec contract test:** for every spec, assert (a) registered handler, (b) action-time entry or default, (c) round-trip-safe codec.
2. **No "every OrderType dispatched" test:** new types can ship as silent no-ops.
3. **Sampled, not parametrized:** ActionTimeResolver tests cover named cases, not the full enum.

## 7. Recommended new test files
1. **`tests/unit/strategy/engine/test_command_registry_contract.py`**:
   - `test_every_order_type_has_handler_or_is_instant`
   - `test_every_action_order_type_resolvable_action_time`
   - `test_registry_and_serializer_coverage_match`
   - `test_handler_count_stability` (regression: ≥ current count)
2. **`tests/unit/strategy/data/test_order_types_registry_coverage.py`**:
   - `test_every_order_type_declared_in_enum_has_coverage`
   - `test_no_unregistered_handlers`
3. **Extension** of `test_action_time_resolver.py` with full OrderType parametrization.

## 8. Risk: hand-built registry substitutes
None found. Tests use `create_default_registry()` or mocks — **no migration risk**.

## Summary
~2,667 LOC across core test files. Coverage is good for happy paths; the missing contract tests are the deliverable in PROJ-353 Phase 1 (TDD entry — write failing contract tests first, then implement spec table, watch them go green).
