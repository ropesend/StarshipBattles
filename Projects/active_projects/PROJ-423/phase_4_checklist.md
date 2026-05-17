# Phase 4: Collapse `GameSession` to a thin shell

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):** game/strategy/engine/game_session.py, tests/unit/strategy/engine/test_game_session_shape.py
**Objective:** Finish the separation after bootstrap and persistence are external. Route both `__init__` and `from_dict` through a single private `_apply_bootstrap_state(...)` method, convert service properties to forward through `self._services`, and remove the now-unused inline imports.

---

## Tasks

### Task 4.1: Author the red tests first [Medium]
**File:** `tests/unit/strategy/engine/test_game_session_shape.py`

- [ ] `test_game_session_no_longer_constructs_mutator_services_inline` — inspect `game_session.py` source (or its module imports) and assert it does not import `FleetNavigationService`, `FleetWriteService`, `PlanetWriteService`, `EmpireWriteService`, `ShipInstanceWriteService`.
- [ ] `test_game_session_no_longer_constructs_turn_engine_inline` — assert it does not import `TurnEngineConfig`, `TurnEngine`, `create_default_registry`, `EventBus`, or `GameInitializer`.
- [ ] `test_game_session_keeps_lazy_race_registry` — `_race_registry` is `None` on a freshly-constructed session; first `.race_registry` access populates it; second access returns the same instance.
- [ ] `test_game_session_file_loc_budget` — assert `game_session.py` LOC is materially below today's 599 (the source plan calls for a "thin shell"; pick a budget such as ≤ 250 LOC and pin it).
- [ ] Run the file; confirm all four tests fail in the expected ways.

### Task 4.2: Introduce `_apply_bootstrap_state(...)` [Medium]
**File:** `game/strategy/engine/game_session.py`

- [ ] Add a private `_apply_bootstrap_state(self, state: SessionBootstrapState) -> None` method that copies every field from `state` onto `self`: `config`, `_services`, `galaxy`, `empires`, `turn_number`, `save_path`, `human_player_ids`. Also initialize `active_empire` / `enemy_empire` (BUG-125 seeding) and the lazy `_race_registry = None`.
- [ ] Do **not** use `self.__dict__.update(...)`.

### Task 4.3: Refactor `__init__` to the target shape [Medium]
**File:** `game/strategy/engine/game_session.py`

- [ ] Change the signature to `__init__(self, config: GameConfig | None = None, ai_factory: Any | None = None, *, _state: SessionBootstrapState | None = None) -> None`.
- [ ] Body: `state = _state or SessionBootstrap.new_game_state(config or GameConfig(), ai_factory=ai_factory); self._apply_bootstrap_state(state)`.

### Task 4.4: Refactor `from_dict` to the target shape [Simple]
**File:** `game/strategy/engine/game_session.py`

- [ ] Body: `state = SessionPersistenceAdapter.rehydrate_state(data, ai_factory=ai_factory); return cls(_state=state)`.

### Task 4.5: Forward service properties through `self._services` [Medium]
**File:** `game/strategy/engine/game_session.py`

- [ ] Convert the five mutator properties (`fleet_mutator`, `planet_mutator`, `empire_mutator`, `ship_mutator`, and the registries / event_log / event_bus / turn_engine / command_registry surface) to read from `self._services` rather than from now-removed inline attributes.
- [ ] Keep `race_registry` lazy on `GameSession` (its property logic stays, backed by `self._race_registry`).

### Task 4.6: Remove dead imports [Simple]
**File:** `game/strategy/engine/game_session.py`

- [ ] Remove `FleetNavigationService`, `FleetWriteService`, `PlanetWriteService`, `EmpireWriteService`, `ShipInstanceWriteService`, `TurnEngineConfig`, `TurnEngine`, `GameInitializer`, `EventBus`, `create_default_registry` imports.
- [ ] Run the second guardrail `rg` to confirm `game_session.py` is no longer constructing any of these.

### Task 4.7: Validate [Complex]
**Tests:**

- [ ] `pytest tests/unit/strategy/engine/test_game_session_shape.py -x` — all green.
- [ ] `pytest tests/unit/strategy/test_game_session.py tests/unit/strategy/test_game_session_events.py tests/unit/strategy/engine/test_game_session_from_dict.py -x` — no regressions.
- [ ] `pytest tests/integration/gameplay_loop/ tests/integration/quickstart/ tests/integration/test_app_integration.py -x` — no regressions.
- [ ] `python Tools/test_sharded/test_sharded.py` — full sharded run after this phase per the source plan's final gates.

---

## Exit criteria

- [ ] `game_session.py` is a thin shell.
- [ ] Public constructor / `from_dict` behavior is unchanged.
- [ ] Sharded test run after this phase passes.
