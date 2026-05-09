# PROJ-405: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-09 | Project initialized | Starting point for Tier 1 B-06: Wire EventBus through Projectile/Seeker construction |
| 2026-05-09 | Threading seam: `AttackRequest.event_bus` (Optional[EventBus]) | Adding the bus to the typed dispatch contract is exactly one shape change; alternatives (per-ship `set_telemetry_bus`, `WeaponFiringSystem` per-engine, context dicts) all sprawled to 4+ touchpoints. The `AttackRequest` already carries every per-fire input — adding telemetry routing fits cleanly. |
| 2026-05-09 | `event_bus` is Optional in `AttackRequest`, Required-by-convention in production | Per CLAUDE.md "no shims": tests/replay paths build `AttackRequest`s without spinning up a bus; production `WeaponFiringSystem._create_attack` always sets `event_bus=self._event_bus`. Making the field non-Optional would break ~30 existing handler tests for no behavioral gain — the prevention seam lives in `WeaponFiringSystem`, not the dataclass. |
| 2026-05-09 | `WeaponFiringSystem._event_bus` mutable via `set_event_bus()`, not constructor-only | `ShipCombatEngine._weapon_firing_system` is a process-shared class attribute (existing PROJ-44 design). New `BattleEngine.__init__(event_bus=...)` calls `set_event_bus` on the shared instance so the live battle's session bus is the one threaded. Two concurrent `BattleEngine` instances would clobber, but that's a pre-existing constraint of the shared firing system, not introduced here. Out of PROJ-405 scope. |
| 2026-05-09 | Restored projectiles get the engine's `event_bus` via `engine.event_bus` lookup | `ProjectileState.to_projectile(ship_lookup, event_bus=...)` accepts the bus explicitly; `BattleController.set_battle_state` resolves it from the engine and forwards. Save-from-mid-battle replays therefore observe the same telemetry as fresh spawns. |

## Production Construction Chain (mapped 2026-05-09)

```
GameSession._event_bus: EventBus           (game/strategy/engine/game_session.py:88)
    ↓ TurnEngineConfig.create_default(event_bus=...)
SimulationBattleResolver(event_bus=...)    (game/strategy/engine/turn_engine_config.py:184)
    ↓ self._event_bus stored
SimulationBattleResolver._run_simulated_battle()
    ↓ run_battle(spec, event_bus=self._event_bus, ...)
                                            (game/strategy/adapters/simulation_adapter.py:307)
run_battle(event_bus=...)                  (game/simulation/battle_runner.py:267)
    ↓ start_engine_from_spec(event_bus=...)
start_engine_from_spec(event_bus=...)      (game/simulation/battle_runner.py:149)
    ↓ BattleEngine(event_bus=...)
BattleEngine.__init__                       (game/simulation/systems/battle_engine.py:106)
    ↓ self.event_bus = event_bus
    ↓ ShipCombatEngine._weapon_firing_system.set_event_bus(event_bus)
WeaponFiringSystem._event_bus              (game/simulation/combat/weapon_firing_system.py)
    ↓ AttackRequest(event_bus=self._event_bus, ...)   (line ~242)
SeekerHandler.fire(request)                (game/simulation/combat/families/seeker.py:55)
    ↓ Projectile(event_logger=request.event_bus.log_event, ...)
ProjectileHandler.fire(request)            (game/simulation/combat/families/projectile.py:33)
    ↓ Projectile(event_logger=request.event_bus.log_event, ...)
Projectile._event_logger                   (game/simulation/entities/projectile.py:40-42)
    ↓ self._event_logger("SEEKER_EXPIRE", ...) on lifetime/max_range expiry
EventBus.log_event()                       (game/core/event_logging.py:54)
    ↓ handler(event_type, **kwargs)
GameSession event handler / test recorder
```

Restoration path (mid-battle save/load):

```
BattleController.set_battle_state(state)   (game/simulation/battle_controller.py:683)
    ↓ event_bus = getattr(engine, "event_bus", None)
    ↓ proj_state.to_projectile(ship_lookup, event_bus=event_bus)
ProjectileState.to_projectile              (game/simulation/battle_state.py:545)
    ↓ Projectile(event_logger=event_bus.log_event, ...)
```

## Adjacent Telemetry Gaps (NOT in PROJ-405 scope)

- `Projectile.update` only emits `SEEKER_EXPIRE`; non-seeker projectile lifecycle (`PROJECTILE_HIT`, `PROJECTILE_DESTROYED`) is not yet emitted. The wiring is now in place — adding emission is a one-line change in `Projectile.update`. Defer to a future telemetry project.
- `BattleEngine.combat_events` (the per-battle `CombatEventBus`) is a separate object from the session `EventBus` threaded by PROJ-405. Convergence (one bus, one event protocol) is also out of scope; tracked elsewhere if/when prioritized.
- `BattleSpec` does not carry the `event_bus`; we pass it as an out-of-band kwarg to `run_battle`. Adding it to the spec would be cleaner but expands scope to all spec compilers. Deferred.
