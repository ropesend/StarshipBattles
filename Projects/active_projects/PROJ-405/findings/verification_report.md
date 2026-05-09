# PROJ-405 Verification Report

**Date:** 2026-05-09
**Branch:** `feat/03c-phase-aware-execution`
**Phase:** 1 — Thread EventBus through Projectile/Seeker construction
**Status:** Code complete; awaiting user smoke verification

## What was wrong

PROJ-382 added an `event_logger` callable kwarg to `Projectile` (with a no-op
default) and called it on `SEEKER_EXPIRE` exits, but no production caller
ever passed a real callable. `rg event_logger` under `game/simulation/` found
only the projectile module itself. Result: missile lifetime/range telemetry
was silently dropped in normal play.

## Production construction chain (post-fix)

| Layer | File:Line | Threading |
|-------|-----------|-----------|
| Session | `game/strategy/engine/game_session.py:88` | Owns `EventBus` (PROJ-252) |
| Turn config | `game/strategy/engine/turn_engine_config.py:184` | `SimulationBattleResolver(event_bus=...)` |
| Strategy adapter | `game/strategy/adapters/simulation_adapter.py:74-90, 307-313` | Stores bus, forwards via `run_battle(event_bus=...)` |
| Runner | `game/simulation/battle_runner.py:149, 267, 332` | `start_engine_from_spec(event_bus=...)` → `BattleEngine(event_bus=...)` |
| Engine | `game/simulation/systems/battle_engine.py:106, 185-211` | Stores `self.event_bus`, calls `set_event_bus` on shared `WeaponFiringSystem` |
| Firing system | `game/simulation/combat/weapon_firing_system.py:43-72, 250-260` | `_event_bus` field; included in every `AttackRequest` |
| Typed contract | `game/simulation/combat/attack_contract.py:81-91` | `AttackRequest.event_bus: EventBus | None` |
| Seeker family | `game/simulation/combat/families/seeker.py:56-79` | `Projectile(event_logger=request.event_bus.log_event, ...)` |
| Projectile family | `game/simulation/combat/families/projectile.py:33-55` | Same shape |
| Restoration | `game/simulation/battle_state.py:545-588` + `game/simulation/battle_controller.py:680-688` | `to_projectile(event_bus=...)` resolves bus from engine |

## Contract decision

`AttackRequest.event_bus` defaults to `None` (Optional). The
prevention seam is `WeaponFiringSystem._create_attack`, which always sets
`event_bus=self._event_bus`. This keeps ~30 existing handler-unit tests
working while making the production wiring impossible to drop without
touching `WeaponFiringSystem` itself. Per CLAUDE.md "no shims", the no-op
default in `Projectile._default_event_logger` is preserved only for
test/replay paths — production now always supplies a real bus.

## Tests

- New regression `tests/unit/simulation/test_projectile_event_bus_wiring.py`
  (4 tests). Initially RED on unmodified production:
  `TypeError: AttackRequest.__init__() got an unexpected keyword argument 'event_bus'`
  and recorder empty. GREEN after implementation.
- `pytest tests/unit/simulation/` — 3733 passed.
- `pytest tests/unit/strategy/ tests/integration/strategy/ tests/unit/simulation/battle_controller/ tests/unit/core/test_serializable_protocol.py` — 4940 passed, 1 skipped.
- Two strategy-adapter tests had stub `_fake_run_battle()` signatures
  missing the new `event_bus=` kwarg; updated mock signatures (no behavior
  change) at `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py:105-110, 147-152`.

## Validators

- `python Projects/scripts/validate_phase.py PROJ-405 1` — PASSED
- `python Projects/scripts/validate_audit_ready.py PROJ-405` — PASSED

## Out-of-scope adjacencies

Logged in `decisions.md`:
1. Non-seeker `Projectile` lifecycle events (`PROJECTILE_HIT`,
   `PROJECTILE_DESTROYED`) — wiring is now in place; emission is a
   one-line addition in `Projectile.update`.
2. Convergence of `BattleEngine.combat_events` (`CombatEventBus`,
   enum-typed combat-pipeline events) with the session `EventBus`
   (string-keyed structured events) — two buses by design today.
3. `BattleSpec.event_bus` field — passed as out-of-band `run_battle` kwarg
   instead, to keep PROJ-405 narrow.

## Files touched

Production:
- `game/simulation/combat/attack_contract.py` — `event_bus` field
- `game/simulation/combat/families/seeker.py` — thread `event_logger`
- `game/simulation/combat/families/projectile.py` — thread `event_logger`
- `game/simulation/combat/weapon_firing_system.py` — `_event_bus` + setter + AttackRequest population
- `game/simulation/systems/battle_engine.py` — `event_bus` ctor param + push to firing system
- `game/simulation/battle_runner.py` — `event_bus` kwarg through `run_battle` and `start_engine_from_spec`
- `game/simulation/services/battle_service.py` — `event_bus` kwarg passed to `BattleEngine`
- `game/simulation/battle_state.py` — `to_projectile(event_bus=...)` keyword
- `game/simulation/battle_controller.py` — resolve `engine.event_bus` for restored projectiles
- `game/strategy/adapters/simulation_adapter.py` — `event_bus` ctor param + forward to `run_battle`
- `game/strategy/engine/turn_engine_config.py` — pass `event_bus` into `SimulationBattleResolver`

Tests:
- `tests/unit/simulation/test_projectile_event_bus_wiring.py` (new) — regression
- `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` — mock signature update
