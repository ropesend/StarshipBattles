# PROJ-351 Dependency Map

## 1. Direct callers of `SimulationBattleResolver(...)` (5 instantiation sites)
- **`game/strategy/engine/turn_engine.py:335`** — `_get_conflict_engine()` lazily creates `SimulationBattleResolver(ai_factory=self._ai_factory)`. Production path.
- **`tests/integration/strategy/test_replay_capture_e2e.py:188, 234, 264, 288`** — Four test instances; no registries passed to `resolve_battle`.
- **`tests/integration/strategy/test_combat_shortcut_paths.py:471`** — Test fixture.
- **`tests/unit/strategy/adapters/test_simulation_adapter.py:72, 89, 111, 136, 150, 164, 179, 200, 207, 253, 273, 292, 308, 323`** — 14 unit test instances; mostly `registries=None`, all mock `run_battle`.

## 2. Primary production caller: ConflictResolutionEngine
**File:** `game/strategy/engine/conflict_resolution_engine.py:450-457`
```python
result = self._battle_resolver.resolve_battle(
    fleets,
    modifiers=modifiers,
    seed=seed,
    registries=self._registries,  # PROJ-50: DI compliance
    environmental_effects=environmental_effects,
    empires=empires_by_team_id,
)
```
TurnEngine threads `self._registries` into ConflictResolutionEngine at `turn_engine.py:346-350`. **ConflictResolutionEngine ALWAYS passes `self._registries`** to `resolve_battle`. The bug is purely on the resolver-internal side.

## 3. Registry test fixtures
- **`tests/conftest.py:189-224`** `fresh_registries` — function-scoped, deep-copied production data (integration).
- **`tests/conftest.py:153-186`** `session_registries` — session-scoped, real data (cached).
- **`tests/conftest.py:227-251`** `minimal_registries` — empty (isolated unit).

Test resolver doubles that ignore registries:
- `tests/integration/gameplay_loop/conftest.py:19-45` `InstantBattleResolver` — accepts but mostly bypasses.
- `tests/integration/colonization/conftest.py:24-50` — same pattern.
- `tests/integration/strategy/test_fleet_registration_lifecycle.py:34-40` `MockResolver`.

## 4. Imports already in simulation_adapter.py
Lines 24-35 import `GameRegistries`, `BattleSpec`, `IBattleResolver`, `IAIControllerFactory`, `run_battle`. Line 245 already imports `get_default_registry_provider` inside `_run_simulated_battle`. **No new imports needed**: GameRegistries IS-A IRegistryProvider (PROJ-211 — see 01_architecture.md).

## 5. Session-scoped registry concept
`GameSession` (`game/strategy/engine/game_session.py:76-80`) does NOT store a session-scoped registry. `TurnEngine._registries` (`turn_engine.py:143`) is the closest thing — per-game-session and threaded into all sub-engines. Not yet a true session-scoped concept; PROJ-351 does not need to invent one.

## 6. Risk: code paths depending on default-provider behavior
**Production: none.** ConflictResolutionEngine always threads the injected registries.

**Tests:** Four `test_replay_capture_e2e.py` tests and ~9 `test_simulation_adapter.py` tests call `resolve_battle` with `registries=None`. They all mock `run_battle`, so the change is invisible. If `resolve_battle` were tightened to require non-None registries, these would break — but PROJ-351 only changes the *forwarding* logic, keeping the existing default-fallback. **No test breakage expected.**
