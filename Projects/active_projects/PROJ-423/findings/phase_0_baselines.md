# Phase 0 Baselines — captured 2026-05-17

## Guardrail rg #1: GameSession surface across game/tests/docs

Production callers all use `GameSession(...)` / `GameSession.from_dict(...)`:

- `game/strategy/systems/save_game_service.py:437` — `GameSession.from_dict(game_state, ai_factory=ai_factory)`
- `game/screen_router.py:209` — `GameSession(config=config, ai_factory=AIControllerFactory())`
- `game/screen_router.py:266` — `GameSession(config=config)`
- `game/ui/screens/strategy_screen.py:90` — `GameSession(ai_factory=AIControllerFactory())`

Test callers: many, all using public surface. No new factories pre-exist. No
references to `SessionBootstrap`, `SessionPersistenceAdapter`, or
`SessionRuntimeServices` — confirming this is greenfield.

## Guardrail rg #2: composition surface in game_session.py

Hits in `game/strategy/engine/game_session.py` (current `main` shape, pre-refactor):

- `fleet_mutator|planet_mutator|empire_mutator|ship_mutator` — present in
  `__init__` (lines 118-138) and `from_dict` (lines 492-527), plus the four
  public service properties (lines 229-251).
- `TurnEngineConfig.create_default` — `__init__` line 130, `from_dict` line 519.
- `create_default_registry` — `__init__` line 147, `from_dict` line 536. Module
  import on line 67.
- `GameInitializer.initialize` — `__init__` line 160 only (load path doesn't
  re-run initialization, by design).

This is the duplicated composition root described by PROJ-396 CRIT-002.

## Behaviors to preserve

1. **`human_player_ids` load fallback asymmetry.** `__init__` lines 188-190
   derives `[i for i, p in enumerate(config.players) if p.is_human]`.
   `from_dict` line 563 falls back to `[0, 1]` when the key is missing.
   Preserved exactly by `SessionPersistenceAdapter.rehydrate_state(...)`.
2. **`race_registry` laziness.** `_race_registry = None` on construction;
   populated on first `.race_registry` access. Preserved.
3. **`SessionInitializationError` null-object substitution exists only on the
   new-game path.** `__init__` lines 159-184 wrap `GameInitializer.initialize`
   so a failure leaves `galaxy=None`, `empires=[]`, etc. before re-raising as
   `SessionInitializationError`. `from_dict` has no parallel safety net by
   design and continues to surface `PersistenceException` (or other errors)
   without null-object substitution. Preserved.
4. **Two-phase deserialisation order in `from_dict`.** Galaxy first (creates
   all planet ids), then empires (resolve via galaxy registries), then galaxy
   back-references, fleet registration, order reference resolution, pursuer
   tracker rebuild, `active_empire` / `enemy_empire` seeding. Preserved by
   `SessionPersistenceAdapter.rehydrate_state(...)`.
5. **Save schema (byte-for-byte):** `{turn_number, save_path, config, galaxy,
   empires, human_player_ids, event_log}`. Preserved by
   `SessionPersistenceAdapter.serialize(...)`.
