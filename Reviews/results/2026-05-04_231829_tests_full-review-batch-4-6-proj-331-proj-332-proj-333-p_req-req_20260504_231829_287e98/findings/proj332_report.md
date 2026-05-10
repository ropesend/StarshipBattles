# PROJ-332 Test Characterization Review — Findings Report

**Date:** 2026-05-04
**Reviewer:** OpenCode (test-quality reviewer)
**Files reviewed:** 7 test files + `turn_engine.py` (795 LOC)

---

## 1. Behavior Accuracy — phase_times Keys

### Status: PASS — No issues

Production code at `turn_engine.py:230-236` uses key `'harvesting'` (not `'harvest'`):

```python
self._phase_times: dict[str, float] = {
    'harvesting': 0.0, 'resources': 0.0,
    ...
}
```

Two test files independently pin the full 14-key set including `'harvesting'`:

- `test_turn_engine_init_precedence.py:45-65` — `test_init_initializes_phase_times_with_14_canonical_keys`
- `test_turn_engine_phase_timing.py:33-69` — `test_reset_phase_times_returns_dict_with_14_canonical_keys`

Both assert `set(engine._phase_times.keys()) == {'harvesting', ...}` with all 14 canonical keys. No test uses the incorrect spelling `'harvest'`.

Additionally, `test_turn_engine_end_of_turn_order.py:175` verifies the negative: `'happiness' not in engine._phase_times`, pinning D-007's observation that end-of-turn engines bypass `_time_phase` wrapping.

**All 14 phase_times keys are pinned by assertions. No gap.**

---

## 2. Vacuous Tests

### Status: PASS — No vacuous tests found

All 27 tests across the 7 files create a **real** `TurnEngine` instance via `TurnEngine(registries=fresh_registries, ...)` and exercise real production code paths. No test exclusively uses `MagicMock` for all objects. No test mocks `TurnEngine` itself. No tautological assertions where a mock's return value is asserted equal to itself. No `mock.called == True` assertions without argument verification.

---

## 3. Mocking Discipline

### Status: PASS — No issues

- **TurnEngine itself is never mocked.** All tests import `TurnEngine` directly and instantiate it. No `MagicMock(spec=TurnEngine)` or `patch('...TurnEngine')` anywhere.
- **15 injectable engines mocked at boundary.** Tests use `MagicMock(spec=I*Engine)` matching D-002. Example: `test_turn_engine_phase_320_movement_diff.py:37-72` injects all 12 per-tick engines as spec'd mocks.
- **D-004 locally-constructed engines patched correctly.** The three end-of-turn engines (`QualityEngine`, `AtmosphereEngine`, `WaterEngine`) and Phase 1.8's `PlanetModifierEffectEngine` are patched at their source modules:
  - `patch('game.strategy.engine.quality_engine.QualityEngine')` (etc.) — correct because `process_turn` re-imports them at runtime via `from X import Y`, so patching the source module attribute affects the import.
  - `patch('game.strategy.engine.planet_modifier_effect_engine.PlanetModifierEffectEngine')` — same pattern, correct.

---

## 4. Test Names

### Status: PASS — All names are descriptive

All 27 test names describe the specific behavior being verified. No `test_basic`, `test_default`, `test_simple`, or similarly vague names. Examples:

| File | Representative name |
|------|-------------------|
| init_precedence | `test_init_kwarg_takes_precedence_over_config_field_when_both_supplied` |
| lazy_properties | `test_conflict_engine_uses_null_battle_resolver_and_warns_when_both_resolver_and_ai_factory_none` |
| phase_timing | `test_time_phase_reraises_preexisting_engine_phase_error_without_double_wrapping` |
| snapshot_integration | `test_snapshot_capture_failure_is_swallowed_and_turn_continues_with_snapshot_none` |

---

## 5. Missing Surfaces

### MAJOR: Five lazy-property default-construction paths untested

**Files:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` (gap)

Five of the 15 `@property` getters on `TurnEngine` have no test that verifies their lazy-default-construction behavior (i.e., what class is constructed and that it's idempotent when no mock is injected). The untested properties are:

| Property | Production file:line | Default class |
|----------|---------------------|---------------|
| `action_engine` | `turn_engine.py:384` | `ActionExecutionEngine` |
| `planet_action_engine` | `turn_engine.py:412` | `PlanetActionEngine` |
| `component_activation_engine` | `turn_engine.py:425` | `ComponentActivationEngine` |
| `organics_consumption_engine` | `turn_engine.py:433` | `OrganicsConsumptionEngine` |
| `happiness_engine` | `turn_engine.py:446` | `HappinessEngine` |

**Description:** `test_turn_engine_lazy_properties.py` covers 8 properties (`production_engine`, `order_processor`, `resource_engine`, `population_engine`, `resupply_engine`, `harvesting_engine`, `environmental_engine`, `planet_energy_engine`) plus `conflict_engine` branching. The remaining 5 lazy properties have their injected-mock path exercised in end-of-turn / tick tests, but the **default-construction** path (when no value is injected and None is in the slot) is never characterized.

**Recommendation:** Add 5 tests to `test_turn_engine_lazy_properties.py`, each verifying `isinstance(engine.<prop>, <ExpectedClass>)` and idempotency for the untested properties.

### MAJOR: `create_default_turn_engine` factory function untested

**File:** `game/strategy/engine/turn_engine.py:756-794`

**Description:** `create_default_turn_engine(registries, ai_factory=None, config=None)` is a public factory function with documented usage. No characterization test verifies that it returns a `TurnEngine` instance with the correct registries/config/ai_factory routed through.

**Recommendation:** Add a test verifying `isinstance(result, TurnEngine)` and that `_registries`, `_ai_factory`, `_battle_resolver` are correctly threaded from the factory's arguments.

### Status: Other public methods covered

| Method | Coverage |
|--------|----------|
| `__init__` | `test_turn_engine_init_precedence.py` (4 tests) |
| `process_turn` | `test_turn_engine_snapshot_integration.py` (4 tests), `test_turn_engine_end_of_turn_order.py` (3 tests) |
| `_process_tick` | `test_turn_engine_phase_320_movement_diff.py` (2 tests) |
| `_time_phase` | `test_turn_engine_phase_timing.py` (2 tests) |
| `_reset_phase_times` | `test_turn_engine_init_precedence.py`, `test_turn_engine_phase_timing.py` |
| `validate_colonize_order` | `test_turn_engine_validation.py` (1 test) |
| `_log_empire_state` | Called during `process_turn` but its log output is never explicitly asserted |

---

## 6. Monkeypatch Correctness — Item 7

### Status: PASS — Patch target is correct

**Test:** `test_turn_engine_phase_timing.py:75-115` — `test_time_phase_accumulates_timing_in_finally_block_when_wrapped_callable_raises`

**Production import:** `turn_engine.py:60` — `import time`

**Monkeypatch target:** `test_turn_engine_phase_timing.py:89-92`
```python
import game.strategy.engine.turn_engine as turn_engine_mod
monkeypatch.setattr(
    turn_engine_mod.time, 'perf_counter', lambda: next(perf_values)
)
```

**Verification:** `turn_engine_mod.time` is the `time` module object bound by `import time` at line 60. `monkeypatch.setattr(turn_engine_mod.time, 'perf_counter', ...)` replaces `time.perf_counter` on that module, affecting every `time.perf_counter()` call inside `_time_phase` (lines 259, 267). The 2-value iterator `[0.0, 2.5]` correctly supplies values for the error-path dual call (t0 → fn-raise → catch → delta).

The test also creates a **real** `TurnEngine` instance (line 94) and calls the real `_time_phase` method. Not vacuous.

---

## 7. Additional Observations

### Observation: `_log_empire_state` logging never asserted

**File:** `turn_engine.py:285-294`

**Description:** `_log_empire_state` is called at turn start (line 529) and turn end (line 548) within `process_turn`. It logs at DEBUG level via `logger.debug(...)`. No test captures or asserts on these log messages. The existing snapshot/end-of-turn tests call `process_turn` which exercises the code path, but the output is never verified.

**Severity:** Minor — the function is passive debug logging with no side effects, and the `except (AttributeError, TypeError)` at line 293 silently suppresses failures. Not actionable under characterization discipline.

### Observation: Lazy properties construct real engines — integration depth concern

**File:** `test_turn_engine_lazy_properties.py`

**Description:** Tests like `test_production_engine_property_returns_default_class_when_none_injected` create a real `ProductionEngine` with real registries. This means the tests transitively depend on `ProductionEngine.__init__`, `GameRegistries`, and downstream constructors. This is heavy for unit tests but acceptable under D-001 characterization discipline (documenting observed behavior without refactoring).

---

## Verdict

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| MAJOR | 2 |

**Test coverage is good but has two gaps:**

1. **Five of 15 lazy properties lack default-construction characterization.** These are `action_engine`, `planet_action_engine`, `component_activation_engine`, `organics_consumption_engine`, and `happiness_engine`. Their injected-mock paths are exercised but the "what happens when no mock is provided" path is unpinned.

2. **`create_default_turn_engine` factory function is untested.** A public API function with documented usage has no characterization test.

Both gaps are straightforward to fill (5 lazy-property tests + 1 factory test) and would bring the project to complete surface coverage.
