# Phase 1: Thread EventBus through Projectile/Seeker construction

**Status:** Complete
**Objective:** Make `SEEKER_EXPIRE` (and other projectile-lifecycle events) actually fire on the EventBus during normal production battle ticks, with a regression test that pins it.

---

## Tasks

### Task 1.1: Map the construction chain [Medium]
**File:** see manifest; also `rg -n "Projectile\(|Seeker\(" game/simulation/`

- [x] Trace every place production code constructs a `Projectile` or `Seeker`. Most likely starting point: `WeaponFiringSystem` (or similar) inside `game/simulation/combat/`.
- [x] Read `BattleState.__init__` and `BattleState.update` (or wherever the per-tick spawning happens) to find the EventBus reference. Confirm where the EventBus is attached on the `BattleState` (PROJ-252 made it session-scoped).
- [x] Document the chain in `decisions.md` with file:line refs.

**Notes:** Three production constructors found: `families/seeker.py:55`, `families/projectile.py:33`, `battle_state.py:564` (deserializer). The `EventBus` is owned by `GameSession` (`game_session.py:88`), threaded into `TurnEngineConfig` (`turn_engine_config.py:101`). Pre-PROJ-405 it was NOT threaded into `BattleEngine` at all — the gap was there, not at the spawn-call sites. `BattleEngine.combat_events: CombatEventBus` is a different bus (combat-pipeline events, enum-typed) — not the session `EventBus` (string-keyed, used by strategy event log).

### Task 1.2: TDD — write failing regression test [Medium]
**File:** `tests/unit/simulation/test_projectile_event_bus_wiring.py` (new)

- [x] Construct a battle through the production-shape entry (use whatever fixture exists — probably `make_battle_state` or similar).
- [x] Subscribe a test recorder to `SEEKER_EXPIRE` (and at least one other projectile event).
- [x] Run a tick chain that causes a seeker to expire (out of fuel / max range).
- [x] Assert the recorder observed at least one event.
- [x] Run against unmodified production — confirm test fails (recorder is empty because the no-op default swallows events).

**Notes:** Test drives `WEAPON_REGISTRY.dispatch(AttackRequest(..., event_bus=bus))` — the actual production seam. Four tests: lifetime-expiry, max-range-expiry, AttackRequest-field-pin, None-fallback. Initial RED was confirmed (`TypeError: AttackRequest.__init__() got an unexpected keyword argument 'event_bus'` and recorder empty).

### Task 1.3: Thread EventBus from `BattleState` through the spawn path [Medium]
**File:** `game/simulation/battle_state.py`, `game/simulation/combat/weapon_firing_system.py` (or equivalent)

- [x] Add an `event_bus` (or `event_logger`) attribute to whichever spawner intermediates between `BattleState` and `Projectile/Seeker`.
- [x] Pass it through every constructor on the chain.
- [x] Update `Projectile.__init__` / `Seeker.__init__` to accept it as a required kwarg (or keep optional with the no-op default but wire production callers to always pass the real bus — choose per CLAUDE.md guidance: prefer required if the no-op default will hide future regressions).
- [x] Run focused tests — they should pass; the new regression should pass.

**Notes:** Bus added to `AttackRequest` (typed contract field, default None for tests/replay). `WeaponFiringSystem.__init__(event_bus=...)` + `set_event_bus()` mutator. `BattleEngine.__init__(event_bus=...)` calls `set_event_bus` on the shared `_weapon_firing_system`. `run_battle`/`start_engine_from_spec` accept and forward the bus. `SimulationBattleResolver(event_bus=...)` threads from `TurnEngineConfig`. `ProjectileState.to_projectile(event_bus=...)` keyword for save/load. `Projectile.event_logger` kwarg shape preserved (PROJ-382 contract). Production handlers always pass `event_bus=request.event_bus.log_event` when bus present; no-op default retained ONLY for non-production paths.

### Task 1.4: Search for any unmigrated production constructors [Simple]
**Tests:** `rg -n "Projectile\(|Seeker\(" game/`

- [x] Confirm every production construction passes the EventBus.
- [x] Test-only constructions (`tests/`, `simulation_tests/`, fixtures) may continue to pass mocks or no-ops — that's fine, but flag any test that's clearly meant to exercise production wiring.

**Notes:** Three production constructors verified migrated: `families/seeker.py:64`, `families/projectile.py:43` (both via `request.event_bus`), `battle_state.py:576` (via `to_projectile(event_bus=...)`). Other matches in `game/` are protocol class definitions or the `Projectile` class itself.

### Task 1.5: Run focused projectile + battle-state suites [Simple]
**Tests:** `pytest tests/unit/simulation/entities/test_projectile.py tests/unit/simulation/test_battle_state.py -v`

- [x] Both pass.

**Notes:** `test_battle_state.py` does not exist; ran the broader battle_state coverage instead: `tests/unit/simulation/test_battle_state_serialization.py`, `test_battle_state_validation.py`, `test_battle_state_live_object_bridges.py`, plus `tests/unit/simulation/systems/`, `tests/unit/simulation/battle_runner/`, `tests/unit/simulation/combat/`. All pass. Two strategy-adapter tests had a stub `_fake_run_battle` missing the new `event_bus=` kwarg; updated their signatures (NOT a behavior change). Final: `pytest tests/unit/simulation/` 3733/3733; `pytest tests/unit/strategy/ tests/integration/strategy/ tests/unit/simulation/battle_controller/ tests/unit/core/test_serializable_protocol.py` 4940/4940 passed, 1 skipped.

### Task 1.6: Closeout
- [x] Update Phase 1 status to `Complete`
- [x] Update plan.md Quick Status + Current State
- [x] Update `Projects/projects_index.md` row for PROJ-405 to `Complete`
- [x] Validators pass
- [x] Commit `PROJ-405 phase 1: thread EventBus through Projectile/Seeker construction`

**Notes:** See verification report at `findings/verification_report.md`.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] Status at top of this file is `Complete`
- [x] plan.md updated
- [x] Focused tests pass
- [x] `python Projects/scripts/validate_phase.py PROJ-405 1` PASSED
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-405` PASSED
