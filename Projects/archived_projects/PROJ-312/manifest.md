# PROJ-312 File Manifest

> Generated during /claude-proj-start. Used by /claude-proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/ai/behaviors.py` | Production | Phase 1: thread `rng` into `ErraticBehavior` (lines 330-371) |
| `game/ai/controller.py` | Production | Phase 1: pass engine RNG to behavior factory |
| `game/ai/ai_factory.py` | Production | Phase 1: add `rng` parameter to controller creation |
| `game/simulation/systems/battle_engine.py` | Production | Phase 1: ensure `engine.rng` reaches AI controllers (read-only audit + minor wiring) |
| `tests/unit/quality/test_no_unseeded_random.py` | Test | Phase 1: NEW AST guard against unseeded `random.*` in battle/AI layer |
| `tests/unit/ai/test_erratic_behavior_seeded.py` | Test | Phase 1: NEW determinism test for ErraticBehavior |
| `tests/integration/fleet_combat/test_battle_determinism.py` | Test | Phase 1: extend with state-hash regression |
| `docs/02_PATTERNS.md` | Doc | Phase 1: extend Pattern #18 (Per-Battle RNG) coverage list |
| `game/simulation/replay/__init__.py` | Production | Phase 2: NEW package |
| `game/simulation/replay/replay_spec.py` | Production | Phase 2: NEW — `ReplaySpec` + nested DTOs (mirror BattleSpec) |
| `game/simulation/replay/replay_outcome.py` | Production | Phase 2: NEW — `ReplayOutcome` (mirror BattleOutcome) |
| `game/simulation/replay/replay_record.py` | Production | Phase 2: NEW — `ReplayRecord` (spec + outcome + metadata + version) |
| `game/simulation/replay/replay_serialization.py` | Production | Phase 2: NEW — `to_dict`/`from_dict` for Boundary, ModifierStack, ModifierEntry |
| `game/simulation/battle_spec.py` | Production | Phase 2: add `to_dict`/`from_dict` to `BattleSpec` + nested DTOs (`ShipSpec`, `TeamSpec`, `SquadronSpec`, `TaskForceSpec`, `ComponentStateSpec`, `EntryVector`, `CombatPolicies`) |
| `game/simulation/battle_outcome.py` | Production | Phase 2: add `to_dict`/`from_dict` to `BattleOutcome` + nested DTOs (`ShipOutcome`, `TeamOutcome`, `WeaponSummary`, `ShipStats`, `HitRecord`, `ModifierApplication`, `EndReason`, `ShipStatus`) |
| `game/simulation/combat/boundary.py` | Production | Phase 2: add `to_dict`/`from_dict` to `RectBoundary`, `CircleBoundary`, `UnboundedRegion` + dispatch helper |
| `game/simulation/combat/modifier_stack.py` | Production | Phase 2: add `to_dict`/`from_dict` to `ModifierStack`, `ModifierEntry` (delegate to existing `ModifierEffect.to_dict`) |
| `tests/unit/simulation/replay/test_replay_spec_roundtrip.py` | Test | Phase 2: NEW |
| `tests/unit/simulation/replay/test_replay_outcome_roundtrip.py` | Test | Phase 2: NEW |
| `tests/unit/simulation/replay/test_boundary_serialization.py` | Test | Phase 2: NEW |
| `tests/unit/simulation/replay/test_modifier_stack_serialization.py` | Test | Phase 2: NEW |
| `tests/unit/simulation/replay/test_battle_spec_serialization.py` | Test | Phase 2: NEW |
| `tests/unit/simulation/replay/test_battle_outcome_serialization.py` | Test | Phase 2: NEW |
| `game/simulation/replay/replay_capture.py` | Production | Phase 3: NEW — input/outcome snapshot hooks |
| `game/simulation/battle_runner.py` | Production | Phase 3: hook `start_engine_from_spec` (capture input) and `extract_outcome` (capture output) |
| `game/simulation/battle_controller.py` | Production | Phase 3: emit replay-capture event from `start_from_spec` (only if not already covered by `start_engine_from_spec`) |
| `tests/integration/replay/test_capture_pipeline.py` | Test | Phase 3: NEW — `run_battle()` produces a `ReplayRecord`; `BattleController.start_from_spec()` produces an identical record |
| `tests/integration/replay/test_capture_n_team.py` | Test | Phase 3: NEW — 3-, 5-, 8-team battles all capture correctly |
| `game/strategy/services/replay_store.py` | Production | Phase 4: NEW — write / list / load / evict replays |
| `game/strategy/systems/save_game_service.py` | Production | Phase 4: hook `save_game`, `load_game`, `delete_save` to wire `ReplayStore` |
| `output/settings/replay_settings.json` | Data | Phase 4: NEW (lazy-init) — `{"max_replays_per_save": 50}` |
| `tests/integration/replay/test_replay_store.py` | Test | Phase 4: NEW — write/list/load atomicity, ring buffer, settings fallback |
| `tests/integration/replay/test_save_lifecycle.py` | Test | Phase 4: NEW — save delete removes replays/, save load points store at correct dir |
| `game/ui/screens/battle_screen.py` | Production | Phase 5: add `replay_mode: bool` flag, "REPLAY MODE" badge, Exit Replay button, end-of-battle transition override |
| `game/simulation/battle_controller.py` | Production | Phase 5: thread `replay_mode` flag from BattleConfig |
| `game/simulation/battle_config.py` | Production | Phase 5: add `replay_mode: bool` field |
| `tests/unit/ui/screens/test_battle_screen_replay_mode.py` | Test | Phase 5: NEW — replay-mode rendering, badge visibility, Exit transitions to Event Log |
| `tests/integration/replay/test_replay_playback.py` | Test | Phase 5: NEW — end-to-end determinism: capture battle → replay → outcome hash matches |
| `game/ui/screens/event_log_window.py` | Production | Phase 6: add Replay button to each battle event row; click resolves replay_id and launches replay player |
| `game/ui/screens/event_log_data_source.py` | Production | Phase 6: surface `replay_id` per event row (when replay was captured) |
| `tests/unit/ui/screens/test_event_log_replay_button.py` | Test | Phase 6: NEW — Replay button visibility, click handler, graceful handling of missing/corrupt replay |
| `Projects/active_projects/PROJ-312/findings/fleet_battle_replay.md` | Doc | Triage source (no edits) |
