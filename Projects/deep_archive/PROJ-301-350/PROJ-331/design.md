# PROJ-331 — Design / Architecture Context

## Purpose

Brief production-side surface map for the three in-scope files, plus the mocks/fixtures the new tests will need. This is read-only context — no behavior changes proposed.

## File 1: `game/simulation/battle_state.py` (805 LOC)

### What it does

Pure-data dataclasses + serialization:

| Dataclass | LOC | Role |
|---|---:|---|
| `ComponentState` | ~70 | Per-component HP/active/layer/modifiers |
| `ShipState` | ~220 | Full ship snapshot (position, velocity, components dict, resources, retreat status) |
| `ProjectileState` | ~145 | Projectile snapshot (owner, target, type, hp, distance) |
| `BattleState` | ~155 | Top-level battle snapshot (ships dict, projectiles list, end_condition_data, allow_retreat flags) |
| `BattleResults` | ~65 | Battle-end summary (winner, surviving/destroyed/escaped/captured ship lists) |

Each dataclass has:
- `to_dict()` — pure data → dict
- `from_dict()` — dict → instance, raises `PersistenceException` on validation failure
- (Top two): `to_json()` / `from_json()` — JSON wrappers
- (Bridge methods): `from_ship()` / `to_ship(*, registries)` / `from_component()` / `from_projectile()` / `to_projectile(ship_lookup)` / `capture_from_engine(engine, ...)`
- (Query methods on BattleState): `get_ships_by_team`, `get_alive_ships`, `get_surviving_ships`, `get_escaped_ships`, `get_destroyed_ships`
- (Query methods on BattleResults): `get_team_survivors`, `get_team_losses`

### Key invariants

- `ComponentState.from_dict` requires `current_hp >= 0` and `max_hp > 0`.
- `ShipState.from_dict` requires color (>=3 elements), position (>=2 elements), velocity (>=2 elements). All raise `PersistenceException` on violation.
- `ShipState.from_dict` resilience: corrupt component entries are skipped with warning, not raised.
- `ShipState.to_ship` requires non-None registries (raises `ValidationException`); applies modifiers BEFORE setting damage state (because `add_modifier` triggers `recalculate_stats`).
- `ProjectileState.from_projectile` extracts `proj.type.value` if `proj.type` is an Enum, else uses string.
- `BattleState.capture_from_engine` builds a `ship_id_map` from `engine.ships`; reuses existing map entries if provided.

### Mocks/fixtures the new tests need

- `MagicMock(spec=Ship)` with attributes: `id`, `name`, `ship_class`, `theme_id`, `team_id`, `color`, `movement_policy`, `targeting_policy`, `x`, `y`, `velocity` (with `.x`/`.y`), `angle`, `hp`, `max_hp`, `current_shields`, `max_shields`, `layers` (dict of LayerType → MagicMock with `.components`), `resources` (or None), `current_target`, `is_alive`, `is_derelict`, `retreat_status`.
- `MagicMock(spec=Component)` with attributes: `id`, `current_hp`, `max_hp`, `is_active`, `layer_assigned` (with `.name`), `modifiers` (list).
- `MagicMock(spec=Projectile)` with attributes: `owner`, `target`, `team_id`, `position`, `velocity`, `damage`, `max_range`, `endurance`, `max_endurance`, `type` (Enum), `turn_rate`, `max_speed`, `hp`, `max_hp`, `distance_traveled`, `is_alive`.
- `MagicMock(spec=BattleEngine)` with `ships`, `projectiles`, `tick_counter`, `end_condition` (or None).
- `MagicMock(spec=GameRegistries)` with `components` (dict-like) and `modifiers` (dict-like).

## File 2: `game/simulation/battle_controller.py` (829 LOC)

### What it does

Central orchestrator with three configuration entry paths:
1. **Manual:** `configure(config, spec=None)` → `add_ships(...)` → `start()`
2. **From state:** `configure(...)` → `add_ships_from_state(...)` → `start()`
3. **Spec-in:** `start_from_spec(spec, ai_factory, ...)` (PROJ-270 unified entry)
4. **Load:** `load_state(state)` (sole production caller is internal `save_state` symmetry — production zero per inline comment)

Plus runtime methods:
- `update()` (one tick) / `run_ticks(n)`
- `request_retreat(ship, method)` / `cancel_retreat(ship)` / `add_reinforcements(ships, team_id, entry_point)`
- `save_state()` / `load_state(state)`
- `get_results()` / `get_outcome()`
- Properties: `config`, `service`
- Reset: `reset()`

Internal collaborators:
- `BattleService` (delegated for engine lifecycle)
- `RetreatManager` (boundary-aware retreat state machine)
- `BattleStateManager` (state capture/restore helper)
- `BattleSpec` / `BattleOutcome` (PROJ-270 spec-in DTOs)

### Key invariants

- `_is_configured` set only when `service.create_battle` succeeds.
- `_is_started` set only by `start()` (or `start_from_spec`) on success; second start fails with "already started".
- `add_ships_from_state` requires non-None registries when state contains ships (raises `ValidationException` via `_require_registries_for_state_restore`).
- `_retreat_allowed()` is config-driven only post-PROJ-269.
- `_extract_outcome_on_battle_end` is invoked exactly once per battle (guarded by `_outcome is None`).
- Reset clears: config, initial_state, is_configured, is_started, ship_id_map, retreat_manager.

### Mocks/fixtures the new tests need

- All from `tests/unit/simulation/battle_controller/conftest.py` (`mock_service`, `mock_ship`, `basic_config`, `controller`, `mock_ai_factory`).
- For `start_from_spec` tests: `MagicMock(spec=BattleSpec)` with `seed`, `end_condition`, `absolute_max_ticks`, `boundary`, `modifier_stack`, `post_battle_hook`. Patch `game.simulation.battle_runner.start_engine_from_spec` and `game.simulation.battle_runner.build_context_ship_builder` so the controller's wiring is the unit under test.
- For `_extract_outcome_on_battle_end` replay-id branch: patch `game.simulation.battle_runner.extract_outcome` and `game.simulation.replay.get_default_capture_sink`.

## File 3: `game/strategy/engine/conflict_resolution_engine.py` (556 LOC)

### What it does

Strategy-layer combat dispatcher:

| Method | Visibility | Role |
|---|---|---|
| `__init__` | public | Stores resolver + registries + event_bus |
| `resolve_all_conflicts(empires, galaxy=None, *, tick=None, moved_fleet_ids=None)` | public | Public entry; validates inputs; short-circuits on `tick=None`; delegates to `_resolve_conflicts`; returns `ConflictResult` |
| `_validate_tick_inputs(empires)` | private | Raises `ValidationException` if any fleet has None location |
| `_resolve_conflicts(empires, *, tick, moved_fleet_ids)` | private | Per-fleet movement-opportunity dispatch in deterministic `(empire_id, fleet_id)` order |
| `_should_trigger_combat_for_fleet(fleet, tick, moved_fleet_ids)` | private | Predicate: opportunity tick AND fleet did not leave |
| `_resolve_combat_at_hex(occupants)` | private | Builds N-team battle, calls resolver, reports destroyed fleets |
| `_log_combat_result(...)` | private | Emits `COMBAT_RESOLVED` event with replay_id + storm names |
| `_lookup_environmental_effects(location)` | private | Calls `system_effects_collector.collect_sector_effects` |
| `_collect_team_modifiers(fleets_by_empire, empire_order)` | private | Per-team modifier collection; broad-catches and returns None on collector failure |
| `_generate_battle_seed()` | private | Deterministic monotonic counter |

### Key invariants

- `resolve_all_conflicts` with `tick=None` returns `ConflictResult(combats_resolved=0, fleets_destroyed=[])` without dispatching anything.
- `_validate_tick_inputs` raises before any dispatch when a fleet has `location=None`.
- Iteration order is `sorted(... key=lambda pair: (pair[0].id, pair[1].id))` — deterministic for replay stability.
- `_resolve_combat_at_hex` skips silently if no participating fleet has any ships.
- `_log_combat_result` skips emission when `event_bus is None`.
- `_log_combat_result` extracts unique storm names from sector-effects providers where `source_kind == 'storm'`.
- `_log_combat_result` selects `empire_id = min(owner_ids)` when fleets have differing owners (the event-log filter needs a single owner column).
- `_collect_team_modifiers` returns None on collector exception OR on empty result dict.
- Battle seed counter starts at 1 and monotonically increments per engine instance.

### Mocks/fixtures the new tests need

- `MagicMock(spec=IBattleResolver)` with `resolve_battle(...)` returning a `BattleResult` (has `replay_id` and `replay_unavailable_reason` optional attributes).
- `MagicMock` empires with `id`, `fleets` (list).
- `MagicMock` fleets with `id`, `owner_id`, `location` (HexCoord), `ships` (list of MagicMock), `speed`.
- `MagicMock` galaxy with `get_system_at_location(location)` returning either a system mock or None.
- An `EventBus` constructed with a list-capturing fake handler (per existing `test_conflict_resolution_event_replay.py` pattern).
- For `_collect_team_modifiers` exception test: monkeypatch `game.strategy.services.combat_modifier_collector.collect_combat_modifiers` to raise.

## Cross-cutting test posture

All new tests:
- Are `pytest`-style classes/functions (no unittest.TestCase).
- Use `MagicMock` and `monkeypatch`/`patch` at module boundaries (no live Pygame, no real save files, no real LLM calls).
- Are deterministic — no `time.sleep`, no random unseeded.
- Run in <100ms each (the existing files in this area average that).
