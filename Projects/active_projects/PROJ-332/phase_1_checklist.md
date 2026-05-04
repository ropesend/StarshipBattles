# PROJ-332 — Phase 1 Checklist

> 27 characterization tests across 7 new files. One commit per file (D-006). Each entry cites the production region it pins.

## File 1 — `tests/unit/strategy/turn_engine/test_turn_engine_init_precedence.py` (4 tests)

- [ ] **1.1** `__init__` kwarg overrides matching field on `config` when both are supplied. Pins `turn_engine.py` `__init__` precedence logic for at least one engine slot (e.g., `movement_engine` kwarg vs `config.movement_engine`).
- [ ] **1.2** `__init__` initializes `phase_times` to a 14-key dict via `_reset_phase_times`. Pins `_reset_phase_times` keys (lines for `_reset_phase_times`).
- [ ] **1.3** `__init__` threads `race_registry` through to `self.race_registry` and accepts `None`. Pins `race_registry` slot wiring.
- [ ] **1.4** `__init__` initializes `last_environmental_events` as an empty list. Pins the env-events list init.

## File 2 — `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` (10 tests)

> The 5 properties already pinned by `test_dependency_injection.py` are skipped here. The 10 below are the gap.

- [ ] **2.1** `production_engine` property creates default `ProductionEngine` when none injected; second call returns same instance (idempotency).
- [ ] **2.2** `order_processor` property — default class + idempotency.
- [ ] **2.3** `resource_engine` property — default `ConsumableEngine` + idempotency.
- [ ] **2.4** `population_engine` property — default class + idempotency.
- [ ] **2.5** `resupply_engine` property — default class + idempotency.
- [ ] **2.6** `harvesting_engine` property — default class + idempotency.
- [ ] **2.7** `environmental_engine` property — default class + idempotency.
- [ ] **2.8** `planet_energy_engine` property — default class + idempotency.
- [ ] **2.9** `conflict_engine` lazy `battle_resolver` branch: when `ai_factory` is provided and no `battle_resolver`, a `SimulationBattleResolver` is constructed and used.
- [ ] **2.10** `conflict_engine` lazy `battle_resolver` branch: when both `battle_resolver` and `ai_factory` are None, `_NullBattleResolver` is used and a WARNING is logged; `_NullBattleResolver.resolve_battle` raises when invoked.

## File 3 — `tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py` (3 tests)

- [ ] **3.1** `_reset_phase_times()` returns a dict containing all 14 expected keys (`harvest`, `resources`, `fuel_gen`, `planet_energy`, `resupply`, `production`, `environmental`, `instant_orders`, `actions`, `planet_actions`, `activation_timers`, `movement_calc`, `movement_apply`, `combat`).
- [ ] **3.2** `_time_phase` accumulates timing into `phase_times[key]` even when the wrapped callable raises — the `finally` block runs.
- [ ] **3.3** `_time_phase` re-raises a pre-wrapped `EnginePhaseError` unchanged (does NOT double-wrap).

## File 4 — `tests/unit/strategy/turn_engine/test_turn_engine_snapshot_integration.py` (4 tests)

- [ ] **4.1** `process_turn` captures a snapshot iff `session` is provided. With `session=None`, no snapshot module entry point is called.
- [ ] **4.2** On `EnginePhaseError`, `snapshot.restore(session)` is called iff both `snapshot` and `session` are set.
- [ ] **4.3** On `EnginePhaseError`, `snapshot.dump_crash_snapshot(save_path)` is called iff both `snapshot` and `save_path` are set.
- [ ] **4.4** When snapshot capture itself raises, the exception is swallowed (broad `except`), the error is logged, and the turn continues with `snapshot=None` (D-008 observation).

## File 5 — `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py` (3 tests)

- [ ] **5.1** End-of-turn engines are called in the order: organics_consumption → happiness → population (use `MagicMock` `mock_calls` ordering to assert).
- [ ] **5.2** With `patch` on `QualityEngine`, `AtmosphereEngine`, `WaterEngine` import sites: each class is instantiated once per `process_turn` and its `process` (or equivalent entry point) is called after the population step (D-004).
- [ ] **5.3** A raise from any end-of-turn engine (e.g., `happiness_engine.process` raises `RuntimeError`) propagates raw — NOT wrapped in `EnginePhaseError` and NOT timed in `phase_times` (D-007 observation).

## File 6 — `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py` (2 tests)

- [ ] **6.1** When `movement_engine.apply` moves a fleet from location A to location B, the resulting `moved_fleet_ids` set passed to `conflict_engine` contains that fleet's id; fleets that did not move are absent.
- [ ] **6.2** With zero empires (or zero fleets), `moved_fleet_ids` is an empty set and `conflict_engine` is called with that empty set (no exception).

## File 7 — `tests/unit/strategy/turn_engine/test_turn_engine_validation.py` (1 test)

- [ ] **7.1** `validate_colonize_order(galaxy, fleet, target_planet)` constructs/uses a `ColonizeValidator` with the right components (registries, fleet, planet) and returns its `ValidationResult` unchanged. Use `patch` on the `ColonizeValidator` import site.

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
