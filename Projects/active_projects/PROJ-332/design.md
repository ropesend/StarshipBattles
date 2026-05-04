# PROJ-332: Design

> Architecture context for the characterization tests. No design changes proposed — this document describes the engine *as it is* so test authors can pin behavior accurately.

## TurnEngine in one paragraph

`TurnEngine` is a per-turn orchestrator. It owns 15 injectable engine collaborators (each behind an `I*Engine` Protocol), 4 collaborators it constructs locally inside its methods, a `GameRegistries` reference, an optional `ai_factory`, an optional `IBattleResolver`, an optional `event_bus`, an optional `IRaceRegistry`, and a frozen `TurnEngineConfig`. `process_turn` runs once per turn and drives a 100-tick loop (`_process_tick`) followed by a 6-step end-of-turn block. Each `_process_tick` runs 14 phases. Most phases are wrapped in `_time_phase`, which accumulates timing into `self.phase_times` and converts engine exceptions into `EnginePhaseError`. A few phases bypass the wrapper (D-007). When a `session` is supplied to `process_turn`, snapshots are captured for crash rollback (D-008).

## Collaborator inventory

### 15 injectable engines (constructor kwargs, lazy default factories)

1. `movement_engine: IMovementEngine`
2. `production_engine: IProductionEngine`
3. `order_processor: IOrderProcessor`
4. `conflict_engine: IConflictEngine`
5. `resource_engine: IConsumableEngine` (note: kwarg name is `resource_engine`, type is consumable)
6. `population_engine: IPopulationEngine`
7. `resupply_engine: IResupplyEngine`
8. `harvesting_engine: IHarvestingEngine`
9. `action_engine: IActionExecutionEngine`
10. `environmental_engine: IEnvironmentalHazardEngine`
11. `planet_energy_engine: IPlanetEnergyEngine`
12. `planet_action_engine: IPlanetActionEngine`
13. `component_activation_engine: IComponentActivationEngine`
14. `organics_consumption_engine: IOrganicsConsumptionEngine`
15. `happiness_engine: IHappinessEngine`

Plus the auxiliary `battle_resolver` (positional), `registries`, `config`, `ai_factory`, `race_registry`, `event_bus`.

### 4 locally-constructed (testability blocker — D-004)

- `QualityEngine` — built inside `process_turn` end-of-turn block.
- `AtmosphereEngine` — built inside `process_turn` end-of-turn block.
- `WaterEngine` — built inside `process_turn` end-of-turn block.
- `PlanetModifierEffectEngine` — built inside `_process_tick` Phase 1.8.

These are imported at module scope and instantiated per call. To exercise them in tests, use `unittest.mock.patch('game.strategy.engine.turn_engine.QualityEngine')` (and the analogous patches for the others). They are NOT injectable.

## Lifecycle

```
process_turn(empires, galaxy, save_path=None, *, session=None, progress_callback=None)
  ├─ clear self.last_environmental_events
  ├─ set self._progress_callback
  ├─ set_current_turn on harvest + production engines (if those methods exist) — PROJ-285
  ├─ snapshot = capture(session) if session else None  (capture failure is swallowed — D-008)
  ├─ try:
  │   for tick in range(TICKS_PER_TURN):       # 100 ticks
  │       _process_tick(tick, empires, galaxy, save_path)
  │   # end-of-turn block (NOT wrapped in _time_phase — D-007):
  │   organics_consumption_engine.process(...)
  │   happiness_engine.process(...)
  │   population_engine.process(...)
  │   QualityEngine().process(...)             # locally constructed
  │   AtmosphereEngine().process(...)          # locally constructed
  │   WaterEngine().process(...)               # locally constructed
  ├─ except EnginePhaseError:
  │   snapshot.dump_crash_snapshot(save_path) if (snapshot and save_path)
  │   snapshot.restore(session) if (snapshot and session)
  │   raise
  ├─ finally:
  │   self._progress_callback = None
  │   log perf summary at WARNING
```

### `_process_tick(tick, empires, galaxy, save_path)` — 14 phases per tick

| # | Phase key | Engine / call | `_time_phase`-wrapped? |
|---|-----------|---------------|------------------------|
| 0 | `harvest` | `harvesting_engine` | yes |
| 0b | `resources` | `resource_engine` | yes |
| 0c | `fuel_gen` | `production_engine` (fuel-gen pass) | yes |
| 0c1 | `planet_energy` | `planet_energy_engine` | yes |
| 0d | `resupply` | `resupply_engine` | yes |
| 0e | `production` | `production_engine` | yes |
| 0f | `environmental` | `environmental_engine` | yes |
| 1 | `instant_orders` | `order_processor` | yes |
| 1.5 | `actions` | `action_engine` | yes |
| 1.6 | `planet_actions` | `planet_action_engine` | yes |
| 1.7 | `activation_timers` | `component_activation_engine` | yes |
| 1.8 | (no key) | `PlanetModifierEffectEngine()` (local) | **NO** — D-007 |
| 2 | `movement_calc` | `movement_engine` (calc pass) | yes |
| 3 | `movement_apply` | `movement_engine` (apply pass) | yes |
| 4 | `combat` | `conflict_engine` | yes |

**PROJ-320 detail:** between Phase 1.8 and Phase 2, `_process_tick` builds `pre_movement_locations` (dict of `fleet_id -> location`). After Phase 3, it derives `moved_fleet_ids = {fid for fid, loc in pre_movement_locations.items() if galaxy.find_fleet(fid).location != loc}`. That set is passed to `conflict_engine` in Phase 4. **Currently untested.**

## Error / snapshot boundary

- `_time_phase(key, fn, *args, **kwargs)`:
  - Records `start = time.perf_counter()`.
  - Calls `fn(*args, **kwargs)`.
  - On `EnginePhaseError`: re-raise unchanged (already wrapped).
  - On any other `Exception`: wrap in `EnginePhaseError(phase=key, ...)` and raise.
  - In `finally`: accumulate `time.perf_counter() - start` into `self.phase_times[key]`.
- Snapshot rollback fires only inside the `try` block of `process_turn`. End-of-turn engines and Phase 1.8 escape this — exceptions from them propagate raw and bypass rollback (D-007).

## Mocking strategy

- For the 15 injectable engines: pass `MagicMock(spec=IFooEngine)` via constructor kwargs; reuse `turn_engine` fixture from `conftest.py` for the common case.
- For the 4 locally-constructed engines: `with patch('game.strategy.engine.turn_engine.QualityEngine') as mock_quality_cls:` and assert on `mock_quality_cls.return_value.process` calls.
- For `_process_tick`-direct tests (e.g., movement-diff): the existing pattern in `test_tick_mechanics.py` overrides individual engine attributes on a real `TurnEngine` instance — reuse it for the PROJ-320 tests.
- For snapshot integration: `MagicMock` for the `session` arg + `patch` on the snapshot module's `capture` / `restore` / `dump_crash_snapshot` entry points.

## Cross-references

- [`tests/unit/strategy/turn_engine/conftest.py`](../../../tests/unit/strategy/turn_engine/conftest.py) — fixtures.
- [`tests/unit/strategy/turn_engine/test_tick_mechanics.py`](../../../tests/unit/strategy/turn_engine/test_tick_mechanics.py) — reference for direct-attribute engine override pattern (PROJ-322 Task 3.13).
- [`game/strategy/engine/turn_engine.py`](../../../game/strategy/engine/turn_engine.py) — production surface.
