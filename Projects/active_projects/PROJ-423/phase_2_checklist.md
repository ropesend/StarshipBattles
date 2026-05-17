# Phase 2: Extract canonical service construction into `SessionBootstrap`

**Status:** Complete
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):** game/strategy/engine/session/bootstrap.py, game/strategy/engine/game_session.py, tests/unit/strategy/engine/session/test_bootstrap.py
**Objective:** Eliminate the duplicated mutator-service / turn-engine / event-bus construction currently mirrored by hand between `__init__` and `from_dict`. After this phase, both fresh and loaded sessions use the same internal `SessionBootstrap._build_services(...)` function.

---

## Tasks

### Task 2.1: Author the red tests first [Medium]
**File:** `tests/unit/strategy/engine/session/test_bootstrap.py`

- [x] `test_build_services_returns_fully_wired_runtime_services` — every field on the returned `SessionRuntimeServices` is non-`None` and of the expected type.
- [x] `test_build_services_reuses_injected_event_log` — when a caller passes an existing `EventLog` (the load path), `SessionBootstrap._build_services(...)` uses it rather than constructing a new one.
- [x] `test_init_and_from_dict_use_identical_service_classes` — the **anti-drift** test. Construct one session via `GameSession(config=...)` and one via `GameSession.from_dict(round_tripped_data)`. Assert `type(a.fleet_mutator) is type(b.fleet_mutator)` for all five mutators, plus `turn_engine`, plus `command_registry`.
- [x] `test_new_game_state_builds_human_player_ids_exactly_as_today` — given a `GameConfig` with mixed `is_human` flags, `SessionBootstrap.new_game_state(...).human_player_ids` matches the current `__init__` semantics.
- [x] Run the file; confirm all four tests fail in the expected ways.

### Task 2.2: Implement `SessionBootstrap._build_services(...)` [Complex]
**File:** `game/strategy/engine/session/bootstrap.py`

- [x] Define `SessionBootstrap` class (or module-level functions; the source plan uses the class form).
- [x] Implement `_build_services(registries, *, event_log=None, ai_factory=None, ...) -> SessionRuntimeServices`. This function is the canonical wiring for the five mutators, `EventBus`, `TurnEngineConfig.create_default(...)`, `TurnEngine(...)`, and `create_default_registry()`.
- [x] If `event_log` is `None`, construct a fresh `EventLog()`. Otherwise reuse the injected one (load path).
- [x] Construct `EventBus` with the same closure handler shape currently in `__init__` lines 87-88.

### Task 2.3: Implement `SessionBootstrap.new_game_state(...)` [Complex]
**File:** `game/strategy/engine/session/bootstrap.py`

- [x] Implement `new_game_state(config, *, ai_factory=None) -> SessionBootstrapState`.
- [x] This function performs the **new-game-only** steps: `_resolve_registries`, `_build_services`, then `GameInitializer.initialize(config, ...)` wrapped in the same `SessionInitializationError` null-object substitution `__init__` currently has.
- [x] Returns a `SessionBootstrapState` with `turn_number=0`, `save_path=None`, `human_player_ids` derived from `config.players[i].is_human`, and the freshly-initialized `galaxy` / `empires`.

### Task 2.4: Route `GameSession.__init__` through `SessionBootstrap.new_game_state(...)` [Medium]
**File:** `game/strategy/engine/game_session.py`

- [x] Replace the inline service construction + `GameInitializer.initialize` block in `__init__` with a call to `SessionBootstrap.new_game_state(config, ai_factory=ai_factory)`.
- [x] Apply the returned `SessionBootstrapState` to `self` (provisional — Phase 4 introduces the canonical `_apply_bootstrap_state(...)` method; for this phase a direct assignment block is acceptable).
- [x] Route `from_dict`'s hand-mirrored service-construction block through `SessionBootstrap._build_services(...)`. The `EventLog.from_dict(...)`-reuse path comes through the `event_log=` kwarg.

### Task 2.5: Preserve current behavior [Simple]

- [x] Confirm `SessionInitializationError` null-object substitution remains on the new-game path only; load-path exception behavior is unchanged in this phase.
- [x] Confirm the current `human_player_ids` load fallback (`[0, 1]` when missing from the dict) is **not** changed in this phase — that lives in the load-path branch of `from_dict` and gets moved into `SessionPersistenceAdapter` in Phase 3.

### Task 2.6: Validate [Medium]
**Tests:**

- [x] `pytest tests/unit/strategy/engine/session/test_bootstrap.py -x` — all green, including the anti-drift test.
- [x] `pytest tests/unit/strategy/engine/test_game_session_from_dict.py -x` — no regressions.
- [x] `pytest tests/unit/strategy/ tests/integration/strategy/ -k "game_session or from_dict" -x` — no regressions.

---

## Exit criteria

- [x] Both fresh and loaded sessions use the same service-construction function (`SessionBootstrap._build_services(...)`).
- [x] The anti-drift test comparing service classes passes.
- [x] All cited regression tests remain green.
