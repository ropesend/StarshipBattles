# PROJ-423 Design — GameSession lifecycle extraction

Source plan: [`TD-02_game_session_lifecycle.md`](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-02_game_session_lifecycle.md). This file distills the verified findings and the target collaborator shapes. The source plan is authoritative — when in doubt, defer to it.

## Verified findings (from the TD-02 plan)

### `__init__` is the composition root

`game/strategy/engine/game_session.py:77-199` — `GameSession.__init__` performs the entire composition-root job:

1. Lines 79-84: config defaulting, `turn_number`, `save_path`.
2. Lines 87-88: `EventLog` + `EventBus` construction with a closure handler.
3. Line 91: `_resolve_registries()` (provider + `ResourceCatalog.from_json()`).
4. Line 98: lazy `_race_registry` slot.
5. Lines 104-123: import + construction of five mutator services (`FleetNavigationService`, `FleetWriteService`, `PlanetWriteService`, `EmpireWriteService`, `ShipInstanceWriteService`).
6. Lines 130-146: `TurnEngineConfig.create_default(...)` + `TurnEngine(...)`.
7. Line 147: `create_default_registry()` (command dispatch).
8. Lines 159-184: `GameInitializer.initialize(config, ...)` wrapped in null-object substitution + `SessionInitializationError` re-raise (PROJ-381 / PROJ-395).
9. Lines 185-190: `systems` list materialisation; `human_player_ids` from `config.players` `is_human` flag.
10. Lines 198-199: `active_empire` / `enemy_empire` seed (BUG-125).

### `from_dict` re-implements the composition root by hand

`game/strategy/engine/game_session.py:432-598` — `from_dict` bypasses `__init__` via `cls.__new__(cls)` (line 456) and manually re-implements steps 1, 2, 3, 5, 6, 7 above plus six rehydration-only operations:

- Line 472: re-calls `_resolve_registries` (the only step extracted to a shared helper).
- Lines 481-482: `EventLog.from_dict(...)` + new `EventBus`.
- Line 488: `_race_registry = None`.
- Lines 498-517: **literally re-imports** the five mutator-service modules and re-constructs the five services in the same order as `__init__` (the comment at lines 490-497 documents that this is mirrored from `__init__` lines 104-123 by hand under PROJ-396 CRIT-002).
- Lines 519-535: `TurnEngineConfig.create_default(...)` + `TurnEngine(...)` again.
- Line 536: `_command_registry`.
- Lines 538-560: two-phase galaxy/empire deserialisation.
- Lines 562-573: galaxy back-references + fleet registration loop (PROJ-219; no equivalent in `__init__`).
- Lines 575-592: `resolve_order_references` (PROJ-207) + pursuer-tracker rebuild (PROJ-222).
- Lines 594-596: `active_empire` / `enemy_empire`.

### PROJ-396 CRIT-002 history — the drift mechanism is confessed

The comment block at `game_session.py:490-497` is self-documenting evidence: *"deserialized sessions MUST construct the same mutator services as `__init__` (lines 104-123). Without these, any command handler that pulls `session.fleet_mutator` ... raises `AttributeError`."* This regression has already happened once and was repaired by hand-mirroring; nothing structurally prevents the next addition from drifting again.

### Concrete drift examples present today

1. **`human_player_ids` semantics differ.** `__init__` (line 188-190) derives `[i for i, p in enumerate(config.players) if p.is_human]`. `from_dict` (line 563) falls back to `[0, 1]`. A two-human / one-AI config that round-trips through save without `human_player_ids` in the dict gets the wrong human set.
2. **`_event_log` handling.** `__init__` constructs a fresh `EventLog()`. `from_dict` does `EventLog.from_dict(data.get('event_log', {'events': []}))`. The fallback shape is a private detail of `EventLog`; if its schema changes the default leaks.
3. **`SessionInitializationError` null-object substitution exists only in `__init__`.** A `from_dict` failure mid-way leaves a partially-constructed object on the caller's stack (e.g. galaxy set but empires missing) — no parallel safety net.
4. **Initialization-only steps.** `GameInitializer.initialize` performs homeworld seeding, colony reset, and population seeding through the mutator surface (lines 160-164). None of this runs on load — by design, but it means the two paths can never share a single bootstrap until those concerns are factored out.
5. **Load-only steps.** Galaxy back-references (lines 566-567), fleet registration (lines 570-573, PROJ-219), order reference resolution (lines 579-581, PROJ-207), pursuer tracker rebuild (lines 586-592, PROJ-222). These have no `__init__` counterpart because fresh games don't need them.

### Public surface

`GameSession` exposes 6 public methods, 7 public properties, 1 static helper, and 3 private helpers (full list in the source plan). They fan out across five separable responsibilities the report calls out:

| Responsibility | Surface |
|---|---|
| Owned domain state | `config`, `turn_number`, `save_path`, `galaxy`, `empires`, `systems`, `human_player_ids`, `active_empire`, `enemy_empire`, `_event_log` |
| Runtime services | 5 mutator properties, `registries`, `race_registry`, `turn_engine`, `_command_registry`, `_event_bus` |
| Command dispatch | `handle_command` |
| Preview helpers | `preview_fleet_path`, `get_fleet_path_projection` |
| Persistence | `to_dict`, `from_dict` (+ all hand-mirrored bootstrap inside it) |

## Target shape

### `SessionRuntimeServices`

```python
@dataclass(frozen=True)
class SessionRuntimeServices:
    registries: GameRegistries
    event_log: EventLog
    event_bus: EventBus
    fleet_mutator: IFleetMutator
    planet_mutator: IPlanetMutator
    empire_mutator: IEmpireMutator
    ship_mutator: IShipInstanceMutator
    turn_engine: TurnEngine
    command_registry: Any
```

`race_registry` intentionally stays **outside** this bag and remains lazy on `GameSession`. It is not part of the drift problem and changing its lifetime here would create unnecessary behavior risk.

**Cross-plan coupling with TD-05 (PROJ-427):** if TD-05 has already landed when TD-02 starts, the `DesignRepository` and per-empire `DesignCatalog` ownership that TD-05 placed directly on `GameSession` should be absorbed into `SessionRuntimeServices` (or into `SessionBootstrapState` for the catalogs, since they are per-empire runtime state) as part of Phase 1. Leaving them on `GameSession` while every other service migrates into the frozen services bag creates a second service-injection convention that future plans would have to bridge. If TD-05 has not yet landed, no action is required here.

### `SessionBootstrapState`

```python
@dataclass(frozen=True)
class SessionBootstrapState:
    config: GameConfig
    services: SessionRuntimeServices
    galaxy: Galaxy | None
    empires: list[Empire]
    turn_number: int
    save_path: str | None
    human_player_ids: list[int]
```

The single internal payload both init and load paths hand to `GameSession`.

### `GameSession` structure

```python
class GameSession:
    def __init__(
        self,
        config: GameConfig | None = None,
        ai_factory: Any | None = None,
        *,
        _state: SessionBootstrapState | None = None,
    ) -> None:
        state = _state or SessionBootstrap.new_game_state(
            config or GameConfig(),
            ai_factory=ai_factory,
        )
        self._apply_bootstrap_state(state)

    @classmethod
    def from_dict(cls, data: dict, ai_factory: Any | None = None) -> "GameSession":
        state = SessionPersistenceAdapter.rehydrate_state(data, ai_factory=ai_factory)
        return cls(_state=state)
```

The private `_apply_bootstrap_state(...)` method is the single assignment path. This avoids both `cls.__new__(cls)` reconstruction in `from_dict` and the risky `self.__dict__.update(...)` shortcut.

### `SessionBootstrap`

- `SessionBootstrap._build_services(...) -> SessionRuntimeServices` is the canonical wiring for all five mutators + turn engine + event bus + command registry. Both new-game and load paths call this.
- `SessionBootstrap.new_game_state(config, *, ai_factory) -> SessionBootstrapState` performs the init-only steps (homeworld seeding, colony reset, population seeding via `GameInitializer.initialize`) and the `SessionInitializationError` null-object substitution.

### `SessionPersistenceAdapter`

- `serialize(session) -> dict` — must return the existing save dict shape byte-for-byte: `{turn_number, save_path, config, galaxy, empires, human_player_ids, event_log}`.
- `rehydrate_state(data, *, ai_factory) -> SessionBootstrapState` — handles the two-phase galaxy/empire deserialisation, galaxy back-references, fleet registration, order reference resolution, and pursuer-tracker rebuild. Preserves the current `human_player_ids` `[0, 1]` fallback. Returns a `SessionBootstrapState`, not a `GameSession`.

## Risks (from the TD-02 plan)

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| A weak executor "helpfully" rewrites all `GameSession(...)` call sites | High | Keep public API stable. Do not add a call-site migration phase. |
| Accidentally changing `race_registry` lifetime while extracting services | Medium | Keep it lazy on `GameSession`; cover with a dedicated shape test. |
| Accidentally changing load semantics while moving logic | Medium | Preserve current `human_player_ids` fallback and existing load exception behavior unless a dedicated failing test approves a change. |
| Replacing duplicated logic with `self.__dict__.update(...)` | Medium | Use `SessionBootstrapState` plus `_apply_bootstrap_state(...)`; never bulk-copy `__dict__`. |
| Save schema drift | Low | Keep `SessionPersistenceAdapter.serialize()` byte-for-byte equivalent to the old `to_dict()` shape and pin with tests. |

## Save compatibility

The on-disk schema does **not** change. Old saves are disposable per project rules, but the round-trip tests should stay green because the serialized shape is identical.

## Executor guardrails

Before each phase, re-run the source plan's two `rg` baselines:

```bash
rg -n "GameSession\(|GameSession\.from_dict\(|SessionBootstrap|SessionPersistenceAdapter|SessionRuntimeServices" game tests docs
rg -n "fleet_mutator|planet_mutator|empire_mutator|ship_mutator|TurnEngineConfig\.create_default|create_default_registry|GameInitializer\.initialize" game/strategy/engine/game_session.py
```

The first command surfaces new external call sites that appeared while parallel work was happening. The second confirms `game_session.py` is actually shrinking.
