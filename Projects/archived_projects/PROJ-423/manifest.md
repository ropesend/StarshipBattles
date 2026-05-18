# PROJ-423 File Manifest

Every file in this table appears in at least one phase checklist. Update if implementation discovers additional files. Sourced from [`TD-02_game_session_lifecycle.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-02_game_session_lifecycle.md) "Affected Code" + per-phase touch lists.

## Production files

| File | Type | Action | Phase | Notes |
|------|------|--------|-------|-------|
| `game/strategy/engine/game_session.py` | Production | Edit | 1, 2, 3, 4 | Shrinks across phases. Phase 1: expose `services` property. Phase 2: delegate construction to `SessionBootstrap`. Phase 3: delegate `to_dict`/`from_dict` to `SessionPersistenceAdapter`. Phase 4: route both entry paths through `_apply_bootstrap_state(...)`; remove inline service / turn-engine / `GameInitializer` imports. |
| `game/strategy/engine/session/__init__.py` | Production | Add | 1 | New session package marker. |
| `game/strategy/engine/session/runtime_services.py` | Production | Add | 1 | `SessionRuntimeServices` + `SessionBootstrapState` frozen dataclasses. |
| `game/strategy/engine/session/bootstrap.py` | Production | Add | 2 | `SessionBootstrap._build_services(...)` (canonical wiring) + `SessionBootstrap.new_game_state(...)` (`GameInitializer.initialize` + `SessionInitializationError` wrapping). |
| `game/strategy/engine/session/persistence_adapter.py` | Production | Add | 3 | `SessionPersistenceAdapter.serialize(session)` + `SessionPersistenceAdapter.rehydrate_state(data, ai_factory=...)`. Returns `SessionBootstrapState`, not `GameSession`. |
| `game/strategy/systems/save_game_service.py` | Production | Edit (conditional) | 3 | Only if `from_dict` delegation changes require a docstring or tiny call-site adjustment; do not change API shape. |

## New tests

| File | Type | Action | Phase | Notes |
|------|------|--------|-------|-------|
| `tests/unit/strategy/engine/session/test_runtime_services.py` | Test | Add | 1 | `test_runtime_services_is_frozen_dataclass`, `test_runtime_services_exposes_current_service_members`, `test_bootstrap_state_captures_session_owned_state`, `test_game_session_services_property_returns_runtime_services`. |
| `tests/unit/strategy/engine/session/test_bootstrap.py` | Test | Add | 2 | `test_build_services_returns_fully_wired_runtime_services`, `test_build_services_reuses_injected_event_log`, `test_init_and_from_dict_use_identical_service_classes` (anti-drift), `test_new_game_state_builds_human_player_ids_exactly_as_today`. |
| `tests/unit/strategy/engine/session/test_persistence_adapter.py` | Test | Add | 3 | `test_serialize_preserves_existing_save_schema`, `test_rehydrate_wires_galaxy_back_refs`, `test_rehydrate_registers_loaded_fleets`, `test_rehydrate_resolves_order_references`, `test_rehydrate_rebuilds_pursuer_trackers`. |
| `tests/unit/strategy/engine/test_game_session_shape.py` | Test | Add | 4 | `test_game_session_no_longer_constructs_mutator_services_inline`, `test_game_session_no_longer_constructs_turn_engine_inline`, `test_game_session_keeps_lazy_race_registry`, `test_game_session_file_loc_budget`. |

## Regression coverage that must stay green

These existing tests are high-signal during this refactor. They are not edited by this project — they must stay green at every phase boundary.

| File | Phase boundary |
|------|----------------|
| `tests/unit/strategy/test_game_session.py` | 1, 2, 3, 4 |
| `tests/unit/strategy/test_game_session_events.py` | 1, 2, 3, 4 |
| `tests/unit/strategy/test_game_session_save_load_registries.py` | 1, 2, 3, 4 |
| `tests/unit/strategy/engine/test_game_session_from_dict.py` | 2, 3, 4 |
| `tests/integration/save_load/` | 3, 4 |
| `tests/integration/strategy/test_event_log_integration.py` | 3, 4 |
| `tests/integration/strategy/test_fleet_registration_wiring.py` | 3, 4 |
| `tests/integration/strategy/test_fleet_registration_lifecycle.py` | 3, 4 |
| `tests/integration/strategy/test_game_session_strategy.py` | 3, 4 |
| `tests/integration/gameplay_loop/` | 4 |
| `tests/integration/quickstart/` | 4 |
| `tests/integration/test_app_integration.py` | 4 |

## Docs

| File | Type | Action | Phase | Notes |
|------|------|--------|-------|-------|
| `docs/01_ARCHITECTURE.md` | Docs | Edit | 5 | Document `SessionRuntimeServices`, `SessionBootstrap`, `SessionPersistenceAdapter` as internal collaborators. |
| `docs/02_PATTERNS.md` | Docs | Edit | 5 | Capture the bootstrap-state pattern (single internal payload, single assignment path). |
| `docs/systems/strategy_layer.md` | Docs | Edit | 5 | Update the session lifecycle section. |
| `docs/systems/save_load.md` | Docs | Edit | 5 | Note that save schema is unchanged; `to_dict`/`from_dict` delegate to `SessionPersistenceAdapter`. |
